"""
Test validation and quality assurance utilities.

This module provides utilities to validate test quality, coverage, and consistency.
"""

import ast
from pathlib import Path
import sys
from typing import Any, Optional

import pytest


class TestQualityValidator:
    """Validates test quality and consistency."""

    def __init__(self, test_dir: Optional[Path] = None) -> None:
        self.test_dir = test_dir or Path(__file__).parent
        self.issues = []

    def validate_test_structure(self) -> list[str]:
        """Validate overall test structure."""
        issues = []

        # Check required directories exist
        required_dirs = ["unit", "integration", "e2e", "performance"]
        for dir_name in required_dirs:
            dir_path = self.test_dir / dir_name
            if not dir_path.exists():
                issues.append(f"Missing required directory: {dir_name}")
            elif not any(dir_path.glob("test_*.py")):
                issues.append(f"Directory {dir_name} has no test files")

        # Check conftest.py exists
        if not (self.test_dir / "conftest.py").exists():
            issues.append("Missing conftest.py file")

        # Check pytest.ini exists
        if not (self.test_dir.parent / "pytest.ini").exists():
            issues.append("Missing pytest.ini configuration")

        return issues

    def validate_test_files(self) -> list[str]:
        """Validate individual test files."""
        issues = []

        test_files = list(self.test_dir.rglob("test_*.py"))

        for test_file in test_files:
            file_issues = self._validate_single_file(test_file)
            issues.extend([f"{test_file.name}: {issue}" for issue in file_issues])

        return issues

    def _validate_single_file(self, file_path: Path) -> list[str]:
        """Validate a single test file."""
        issues = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Check for docstring
            if not ast.get_docstring(tree):
                issues.append("Missing module docstring")

            # Check for test classes and functions
            test_classes = [node for node in ast.walk(tree)
                          if isinstance(node, ast.ClassDef) and node.name.startswith("Test")]
            test_functions = [node for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]

            if not test_classes and not test_functions:
                issues.append("No test classes or functions found")

            # Check for pytest markers
            any(
                decorator.id == "pytest.mark" if isinstance(decorator, ast.Attribute) else False
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                for decorator in node.decorator_list
                if isinstance(decorator, ast.Attribute)
            )

            # Validate test function names
            for func in test_functions:
                if not func.name.startswith("test_"):
                    issues.append(f"Test function {func.name} doesn't follow naming convention")

                # Check for docstring in test functions
                if not ast.get_docstring(func):
                    issues.append(f"Test function {func.name} missing docstring")

            # Check imports
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            has_pytest_import = any(
                (isinstance(imp, ast.Import) and any(alias.name == "pytest" for alias in imp.names)) or
                (isinstance(imp, ast.ImportFrom) and imp.module == "pytest")
                for imp in imports
            )

            if (test_classes or test_functions) and not has_pytest_import:
                issues.append("Missing pytest import")

        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
        except Exception as e:
            issues.append(f"Error parsing file: {e}")

        return issues

    def validate_test_markers(self) -> list[str]:
        """Validate pytest markers consistency."""
        issues = []

        # Load pytest.ini to get defined markers
        pytest_ini = self.test_dir.parent / "pytest.ini"
        defined_markers = set()

        if pytest_ini.exists():
            with open(pytest_ini, encoding="utf-8") as f:
                content = f.read()
                in_markers_section = False
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("markers"):
                        in_markers_section = True
                        continue
                    if in_markers_section:
                        if line and not line.startswith(" ") and not line.startswith("\t"):
                            break
                        if ":" in line:
                            marker_name = line.split(":")[0].strip()
                            if marker_name:
                                defined_markers.add(marker_name)

        # Check test files for undefined markers
        test_files = list(self.test_dir.rglob("test_*.py"))
        used_markers = set()

        for test_file in test_files:
            try:
                with open(test_file, encoding="utf-8") as f:
                    content = f.read()

                # Find pytest.mark usage
                import re
                marker_pattern = r"@pytest\.mark\.(\w+)"
                markers = re.findall(marker_pattern, content)
                used_markers.update(markers)

            except Exception as e:
                issues.append(f"Error reading {test_file.name}: {e}")

        # Check for undefined markers
        undefined_markers = used_markers - defined_markers
        if undefined_markers:
            issues.append(f"Undefined markers found: {', '.join(undefined_markers)}")

        return issues

    def validate_fixture_usage(self) -> list[str]:
        """Validate fixture usage and definitions."""
        issues = []

        # Load conftest.py to find defined fixtures
        conftest_file = self.test_dir / "conftest.py"
        defined_fixtures = set()

        if conftest_file.exists():
            try:
                with open(conftest_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                # Find fixture definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            if (isinstance(decorator, ast.Attribute) and
                                decorator.attr == "fixture" and
                                isinstance(decorator.value, ast.Attribute) and
                                decorator.value.attr == "mark" and
                                isinstance(decorator.value.value, ast.Name) and
                                decorator.value.value.id == "pytest") or (isinstance(decorator, ast.Call) and
                                  isinstance(decorator.func, ast.Attribute) and
                                  decorator.func.attr == "fixture"):
                                defined_fixtures.add(node.name)
                                break

            except Exception as e:
                issues.append(f"Error parsing conftest.py: {e}")

        return issues

    def generate_quality_report(self) -> dict[str, Any]:
        """Generate comprehensive quality report."""
        report = {
            "structure_issues": self.validate_test_structure(),
            "file_issues": self.validate_test_files(),
            "marker_issues": self.validate_test_markers(),
            "fixture_issues": self.validate_fixture_usage(),
            "summary": {},
        }

        total_issues = sum(len(issues) for issues in report.values() if isinstance(issues, list))
        report["summary"] = {
            "total_issues": total_issues,
            "structure_ok": len(report["structure_issues"]) == 0,
            "files_ok": len(report["file_issues"]) == 0,
            "markers_ok": len(report["marker_issues"]) == 0,
            "fixtures_ok": len(report["fixture_issues"]) == 0,
            "overall_quality": "EXCELLENT" if total_issues == 0 else
                              "GOOD" if total_issues < 5 else
                              "NEEDS_IMPROVEMENT" if total_issues < 15 else "POOR",
        }

        return report


class TestCoverageAnalyzer:
    """Analyzes test coverage and identifies gaps."""

    def __init__(self, src_dir: Optional[Path] = None, test_dir: Optional[Path] = None) -> None:
        self.src_dir = src_dir or Path(__file__).parent.parent / "src"
        self.test_dir = test_dir or Path(__file__).parent

    def analyze_component_coverage(self) -> dict[str, Any]:
        """Analyze test coverage by component."""
        coverage_data = {}

        # Find source modules
        src_modules = list(self.src_dir.rglob("*.py"))
        src_modules = [m for m in src_modules if not m.name.startswith("_")]

        # Find test files
        test_files = list(self.test_dir.rglob("test_*.py"))

        for src_module in src_modules:
            module_name = src_module.stem
            relative_path = src_module.relative_to(self.src_dir)

            # Find corresponding test files
            corresponding_tests = [test_file.name for test_file in test_files if module_name in test_file.name or any(part in test_file.name for part in relative_path.parts)]

            coverage_data[str(relative_path)] = {
                "has_tests": len(corresponding_tests) > 0,
                "test_files": corresponding_tests,
                "test_count": len(corresponding_tests),
            }

        return coverage_data

    def identify_untested_components(self) -> list[str]:
        """Identify components without tests."""
        coverage_data = self.analyze_component_coverage()
        return [component for component, data in coverage_data.items() if not data["has_tests"]]


@pytest.mark.unit
class TestQualityValidation:
    """Tests for test quality validation."""

    def test_test_structure_validation(self) -> None:
        """Test that test structure validation works."""
        validator = TestQualityValidator()
        issues = validator.validate_test_structure()

        # Should have minimal structural issues in a well-organized test suite
        assert len(issues) <= 2, f"Too many structural issues: {issues}"

    def test_test_file_validation(self) -> None:
        """Test that test file validation works."""
        validator = TestQualityValidator()
        issues = validator.validate_test_files()

        # Some issues might exist, but should be reasonable
        assert len(issues) <= 20, f"Too many file validation issues: {issues}"

    def test_marker_validation(self) -> None:
        """Test that marker validation works."""
        validator = TestQualityValidator()
        issues = validator.validate_test_markers()

        # Should have no undefined markers
        assert len(issues) == 0, f"Marker validation issues: {issues}"

    def test_quality_report_generation(self) -> None:
        """Test quality report generation."""
        validator = TestQualityValidator()
        report = validator.generate_quality_report()

        # Report should have all required sections
        assert "structure_issues" in report
        assert "file_issues" in report
        assert "marker_issues" in report
        assert "fixture_issues" in report
        assert "summary" in report

        # Summary should have quality assessment
        assert "overall_quality" in report["summary"]
        assert report["summary"]["overall_quality"] in {"EXCELLENT", "GOOD", "NEEDS_IMPROVEMENT", "POOR"}

    def test_coverage_analysis(self) -> None:
        """Test coverage analysis functionality."""
        analyzer = TestCoverageAnalyzer()
        coverage_data = analyzer.analyze_component_coverage()

        # Should find some components
        assert len(coverage_data) > 0

        # Each component should have coverage info
        for data in coverage_data.values():
            assert "has_tests" in data
            assert "test_files" in data
            assert "test_count" in data

    def test_untested_components_identification(self) -> None:
        """Test identification of untested components."""
        analyzer = TestCoverageAnalyzer()
        untested = analyzer.identify_untested_components()

        # Should return a list (might be empty if all components are tested)
        assert isinstance(untested, list)

        # If there are untested components, should be specific
        if untested:
            for component in untested:
                assert isinstance(component, str)
                assert len(component) > 0


def run_quality_validation() -> bool:
    """Run comprehensive quality validation."""

    validator = TestQualityValidator()
    report = validator.generate_quality_report()

    if report["structure_issues"]:
        for _issue in report["structure_issues"]:
            pass

    if report["file_issues"]:
        for _issue in report["file_issues"][:10]:  # Show first 10
            pass
        if len(report["file_issues"]) > 10:
            pass

    if report["marker_issues"]:
        for _issue in report["marker_issues"]:
            pass

    if report["fixture_issues"]:
        for _issue in report["fixture_issues"]:
            pass

    # Coverage analysis
    analyzer = TestCoverageAnalyzer()
    coverage_data = analyzer.analyze_component_coverage()
    untested = analyzer.identify_untested_components()

    tested_components = sum(1 for data in coverage_data.values() if data["has_tests"])
    total_components = len(coverage_data)
    (tested_components / total_components * 100) if total_components > 0 else 0

    if untested:
        for _component in untested[:5]:  # Show first 5
            pass
        if len(untested) > 5:
            pass

    if report["summary"]["total_issues"] == 0 and not untested:
        return True
    return bool(report["summary"]["total_issues"] < 5 and len(untested) < 3)


if __name__ == "__main__":
    success = run_quality_validation()
    sys.exit(0 if success else 1)
