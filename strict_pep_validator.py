#!/usr/bin/env python3
"""Strict PEP compliance validator for tap-oracle-wms."""

import ast
from pathlib import Path
import re
import sys


class StrictPEPValidator:
    """Comprehensive PEP compliance validator."""

    def __init__(self) -> None:
        """Initialize the validator."""
        self.violations: list[str] = []
        self.files_checked = 0

    def validate_pep8_naming(self, content: str, file_path: str) -> None:
        """Validate PEP 8 naming conventions."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for camelCase function names (should be snake_case)
            if re.search(r"def [a-z]+[A-Z]", line):
                self.violations.append(
                    f"{file_path}:{i}: PEP8-N802 function name should be lowercase"
                )

            # Check for camelCase variable names
            if re.search(r"[a-z]+[A-Z][a-zA-Z]* =", line):
                self.violations.append(
                    f"{file_path}:{i}: PEP8-N806 variable should be lowercase"
                )

            # Check class names (should be PascalCase)
            if re.search(r"class [a-z]", line):
                self.violations.append(
                    f"{file_path}:{i}: PEP8-N801 class name should use CapWords"
                )

    def validate_pep257_docstrings(self, content: str, file_path: str) -> None:
        """Validate PEP 257 docstring conventions."""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    # Check if public function/class has docstring
                    if not node.name.startswith("_"):
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            self.violations.append(
                                f"{file_path}:{node.lineno}: PEP257-D100 missing docstring"
                            )
                        elif len(docstring.strip()) < 10:
                            self.violations.append(
                                f"{file_path}:{node.lineno}: PEP257-D101 docstring too short"
                            )
        except SyntaxError:
            pass  # Skip files with syntax errors

    def validate_pep484_annotations(self, content: str, file_path: str) -> None:
        """Validate PEP 484/526 type annotations."""
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check function parameter annotations
                    for arg in node.args.args:
                        if not arg.annotation and arg.arg != "self":
                            self.violations.append(
                                f"{file_path}:{node.lineno}: PEP484-ANN001 missing type annotation for {arg.arg}"
                            )

                    # Check return annotation
                    if not node.returns and not node.name.startswith("_"):
                        self.violations.append(
                            f"{file_path}:{node.lineno}: PEP484-ANN201 missing return type annotation"
                        )
        except SyntaxError:
            pass

    def validate_pep8_imports(self, content: str, file_path: str) -> None:
        """Validate PEP 8 import organization."""
        lines = content.split("\n")

        import_started = False
        last_import_type = 0  # 0=standard, 1=third-party, 2=local

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            if stripped.startswith(("import ", "from ")):
                import_started = True

                # Determine import type
                if any(mod in stripped for mod in ["os", "sys", "json", "re", "datetime", "pathlib", "typing"]):
                    current_type = 0  # standard library
                elif "tap_oracle_wms" in stripped:
                    current_type = 2  # local
                else:
                    current_type = 1  # third-party

                # Check import order
                if current_type < last_import_type:
                    self.violations.append(
                        f"{file_path}:{i}: PEP8-I001 import order violation"
                    )

                last_import_type = current_type

            elif import_started and stripped and not stripped.startswith("#"):
                # Check for proper spacing after imports
                if lines[i - 2:i - 1] and not any(l.strip() == "" for l in lines[i - 2:i - 1]):
                    self.violations.append(
                        f"{file_path}:{i}: PEP8-E302 expected 2 blank lines after imports"
                    )
                break

    def validate_pep8_formatting(self, content: str, file_path: str) -> None:
        """Validate PEP 8 formatting standards."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check line length (should be <= 88)
            if len(line) > 88:
                self.violations.append(
                    f"{file_path}:{i}: PEP8-E501 line too long ({len(line)} > 88)"
                )

            # Check trailing whitespace
            if line.rstrip() != line:
                self.violations.append(
                    f"{file_path}:{i}: PEP8-W291 trailing whitespace"
                )

            # Check for proper spacing around operators
            if re.search(r"[a-zA-Z0-9)]\+[a-zA-Z0-9(]", line):
                self.violations.append(
                    f"{file_path}:{i}: PEP8-E226 missing whitespace around arithmetic operator"
                )

    def validate_file(self, file_path: Path) -> None:
        """Validate a single Python file for PEP compliance."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            file_str = str(file_path)

            # Apply all PEP validations
            self.validate_pep8_naming(content, file_str)
            self.validate_pep257_docstrings(content, file_str)
            self.validate_pep484_annotations(content, file_str)
            self.validate_pep8_imports(content, file_str)
            self.validate_pep8_formatting(content, file_str)

            self.files_checked += 1

        except Exception as e:
            self.violations.append(f"{file_path}: Error reading file: {e}")

    def validate_project(self) -> tuple[bool, int, list[str]]:
        """Validate entire project for strict PEP compliance."""
        # Check source files
        for py_file in Path("src").rglob("*.py"):
            self.validate_file(py_file)

        # Check examples
        for py_file in Path("examples").glob("*.py"):
            self.validate_file(py_file)

        # Check root Python files (excluding validation scripts)
        for py_file in Path().glob("*.py"):
            if not py_file.name.startswith(("validate", "strict_pep", "quick_")):
                self.validate_file(py_file)

        return len(self.violations) == 0, self.files_checked, self.violations

    def generate_report(self) -> str:
        """Generate comprehensive PEP compliance report."""
        success, files_checked, violations = self.validate_project()

        report = f"""# Strict PEP Compliance Report

**Date**: {Path(__file__).stat().st_mtime}
**Files Checked**: {files_checked}
**Violations Found**: {len(violations)}
**Status**: {"✅ COMPLIANT" if success else "❌ VIOLATIONS DETECTED"}

## Summary

| PEP Standard | Category | Status |
|-------------|----------|--------|
| **PEP 8** | Style Guide | {"✅ PASS" if not any("PEP8" in v for v in violations) else "❌ FAIL"} |
| **PEP 257** | Docstring Conventions | {"✅ PASS" if not any("PEP257" in v for v in violations) else "❌ FAIL"} |
| **PEP 484** | Type Annotations | {"✅ PASS" if not any("PEP484" in v for v in violations) else "❌ FAIL"} |

## Detailed Violations

"""

        if violations:
            # Group violations by type
            pep8_violations = [v for v in violations if "PEP8" in v]
            pep257_violations = [v for v in violations if "PEP257" in v]
            pep484_violations = [v for v in violations if "PEP484" in v]

            if pep8_violations:
                report += "### PEP 8 Style Guide Violations\n\n"
                for violation in pep8_violations[:10]:  # Show first 10
                    report += f"- {violation}\n"
                if len(pep8_violations) > 10:
                    report += f"- ... and {len(pep8_violations) - 10} more\n"
                report += "\n"

            if pep257_violations:
                report += "### PEP 257 Docstring Violations\n\n"
                for violation in pep257_violations[:10]:
                    report += f"- {violation}\n"
                if len(pep257_violations) > 10:
                    report += f"- ... and {len(pep257_violations) - 10} more\n"
                report += "\n"

            if pep484_violations:
                report += "### PEP 484 Type Annotation Violations\n\n"
                for violation in pep484_violations[:10]:
                    report += f"- {violation}\n"
                if len(pep484_violations) > 10:
                    report += f"- ... and {len(pep484_violations) - 10} more\n"
                report += "\n"
        else:
            report += "### ✅ No Violations Found\n\nAll files comply with strict PEP standards.\n\n"

        report += """## Compliance Recommendations

### For PEP 8 Compliance:
- Use snake_case for function and variable names
- Use PascalCase for class names
- Maintain line length ≤ 88 characters
- Organize imports: standard library → third-party → local
- Use proper spacing around operators

### For PEP 257 Compliance:
- Add docstrings to all public functions and classes
- Use Google-style docstring format
- Ensure docstrings are descriptive (≥10 characters)

### For PEP 484 Compliance:
- Add type annotations to all function parameters
- Add return type annotations to all functions
- Use modern type syntax (dict[str, Any] vs Dict[str, Any])

**Quality Commitment**: Maintain strict PEP compliance for enterprise-grade code quality.
"""

        return report


def main() -> int:
    """Run strict PEP compliance validation."""
    validator = StrictPEPValidator()
    success, _files_checked, violations = validator.validate_project()

    if success:
        result = 0
    else:

        # Show summary by type
        len([v for v in violations if "PEP8" in v])
        len([v for v in violations if "PEP257" in v])
        len([v for v in violations if "PEP484" in v])

        result = 1

    # Generate detailed report
    report = validator.generate_report()
    with open("STRICT_PEP_COMPLIANCE_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)

    return result


if __name__ == "__main__":
    sys.exit(main())
