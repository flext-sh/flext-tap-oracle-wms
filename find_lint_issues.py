#!/usr/bin/env python3
"""Find all lint and mypy issues in tap-oracle-wms."""

import ast
from pathlib import Path
import sys


def check_python_syntax(file_path: Path) -> list[str]:
    """Check Python file for syntax errors."""
    issues = []
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check for basic syntax
        ast.parse(content)

        # Check common lint issues
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Line too long (>88 chars for black compatibility)
            if len(line) > 88:
                issues.append(
                    f"{file_path}:{i}: E501 line too long ({len(line)} > 88 characters)",
                )

            # Trailing whitespace
            if line.rstrip() != line:
                issues.append(f"{file_path}:{i}: W291 trailing whitespace")

            # Multiple imports on one line
            if line.strip().startswith("import ") and "," in line:
                issues.append(f"{file_path}:{i}: E401 multiple imports on one line")

            # Missing newline at end of file
            if i == len(lines) and line and not content.endswith("\n"):
                issues.append(f"{file_path}:{i}: W292 no newline at end of file")

    except SyntaxError as e:
        issues.append(f"{file_path}:{e.lineno}: E999 SyntaxError: {e.msg}")
    except Exception as e:
        issues.append(f"{file_path}: ERROR reading file: {e}")

    return issues


def main() -> int:
    """Find all lint issues."""
    src_dir = Path("src")
    examples_dir = Path("examples")

    all_issues = []

    # Check source files
    for py_file in src_dir.rglob("*.py"):
        issues = check_python_syntax(py_file)
        all_issues.extend(issues)

    # Check example files
    if examples_dir.exists():
        for py_file in examples_dir.rglob("*.py"):
            issues = check_python_syntax(py_file)
            all_issues.extend(issues)

    # Check root level Python files
    for py_file in Path().glob("*.py"):
        issues = check_python_syntax(py_file)
        all_issues.extend(issues)

    if all_issues:
        for _issue in all_issues:
            pass
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
