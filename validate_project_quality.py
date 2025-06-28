#!/usr/bin/env python3
"""Comprehensive project quality validation script."""

import ast
from pathlib import Path
import subprocess
import sys
from typing import Any


def run_command(command: list[str]) -> tuple[bool, str, str]:
    """Run a command and return success status with output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def validate_python_syntax() -> tuple[bool, list[str]]:
    """Validate Python syntax for all files."""
    errors = []
    files_checked = 0

    # Check source files
    for py_file in Path("src").rglob("*.py"):
        if validate_file_syntax(py_file):
            files_checked += 1
        else:
            errors.append(f"Syntax error in {py_file}")

    # Check examples
    for py_file in Path("examples").glob("*.py"):
        if validate_file_syntax(py_file):
            files_checked += 1
        else:
            errors.append(f"Syntax error in {py_file}")

    # Check root level Python files
    for py_file in Path().glob("*.py"):
        if validate_file_syntax(py_file):
            files_checked += 1
        else:
            errors.append(f"Syntax error in {py_file}")

    return len(errors) == 0, errors


def validate_file_syntax(file_path: Path) -> bool:
    """Validate syntax of a single Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
        return True
    except (SyntaxError, UnicodeDecodeError):
        return False


def validate_imports() -> tuple[bool, list[str]]:
    """Validate that core imports work."""
    import_tests = [
        "import tap_oracle_wms",
        "from tap_oracle_wms import TapOracleWMS",
        "from tap_oracle_wms.auth import get_wms_authenticator",
        "from tap_oracle_wms.discovery import EntityDiscovery, SchemaGenerator",
        "from tap_oracle_wms.config import TapOracleWMSConfig",
    ]

    errors = []
    sys.path.insert(0, "src")

    for import_statement in import_tests:
        try:
            exec(import_statement)  # noqa: S102
        except Exception as e:
            errors.append(f"Import failed: {import_statement} -> {e}")

    return len(errors) == 0, errors


def validate_ruff() -> tuple[bool, str]:
    """Run ruff lint checks."""
    success, stdout, stderr = run_command(
        ["python", "-m", "ruff", "check", ".", "--select", "ALL"],
    )

    if success:
        return True, "No violations found"
    return False, f"Ruff violations found:\n{stdout}\n{stderr}"


def validate_mypy() -> tuple[bool, str]:
    """Run mypy type checking."""
    success, stdout, stderr = run_command(["python", "-m", "mypy", "src/", "--strict"])

    if success:
        return True, "No type errors found"
    return False, f"MyPy errors found:\n{stdout}\n{stderr}"


def generate_quality_report(results: dict[str, Any]) -> None:
    """Generate comprehensive quality report."""
    report = f"""# Project Quality Validation Report

**Date**: {Path(__file__).stat().st_mtime}
**Validation Script**: validate_project_quality.py

## Summary

| Check | Status | Details |
|-------|--------|---------|
| Python Syntax | {"✅ PASS" if results["syntax"][0] else "❌ FAIL"} | {len(results["syntax"][1])} errors |
| Import Validation | {"✅ PASS" if results["imports"][0] else "❌ FAIL"} | {len(results["imports"][1])} failures |
| Ruff Lint | {"✅ PASS" if results["ruff"][0] else "❌ FAIL"} | Comprehensive rule set |
| MyPy Type Check | {"✅ PASS" if results["mypy"][0] else "❌ FAIL"} | Strict mode |

## Overall Status

**{"🎯 ALL CHECKS PASSED - ZERO VIOLATIONS" if all(r[0] for r in results.values()) else "❌ QUALITY ISSUES DETECTED"}**

## Detailed Results

### Syntax Validation
{"✅ All Python files have valid syntax" if results["syntax"][0] else "❌ Syntax errors found:"}
{chr(10).join(f"- {error}" for error in results["syntax"][1]) if results["syntax"][1] else ""}

### Import Validation
{"✅ All core imports successful" if results["imports"][0] else "❌ Import errors found:"}
{chr(10).join(f"- {error}" for error in results["imports"][1]) if results["imports"][1] else ""}

### Ruff Lint Analysis
{results["ruff"][1]}

### MyPy Type Checking
{results["mypy"][1]}

## Maintenance Notes

- Run this script regularly to maintain quality standards
- Address any failures immediately to prevent quality degradation
- Update validation criteria as project evolves

**Quality Commitment**: Zero tolerance for violations in production code.
"""

    with open("QUALITY_VALIDATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)


def main() -> int:
    """Run comprehensive quality validation."""
    # Run all validation checks
    results = {
        "syntax": validate_python_syntax(),
        "imports": validate_imports(),
        "ruff": validate_ruff(),
        "mypy": validate_mypy(),
    }

    # Summary
    passed_checks = sum(1 for success, _ in results.values() if success)
    total_checks = len(results)

    if passed_checks == total_checks:
        generate_quality_report(results)
        return 0
    generate_quality_report(results)

    # Print specific failures
    for (success, details) in results.values():
        if not success and isinstance(details, list):
            for _detail in details:
                pass

    return 1


if __name__ == "__main__":
    sys.exit(main())
