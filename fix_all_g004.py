#!/usr/bin/env python3
"""Fix all G004 ruff violations (f-strings in logging) project-wide."""

import contextlib
from pathlib import Path
import re


def fix_logging_fstrings(content: str) -> str:
    """Fix f-string logging violations."""
    # Pattern to match logger.method(f"...{var}...")
    pattern = r'(logger\.(?:trace|debug|info|warning|error|critical|exception)\s*\(\s*)f"([^"]*?)"\s*\)'

    def replace_fstring(match) -> str:
        prefix = match.group(1)
        fstring_content = match.group(2)

        # Find all {var} patterns and replace with %s
        var_pattern = r"\{([^}]+)\}"
        vars_found = re.findall(var_pattern, fstring_content)

        if not vars_found:
            # No variables, just remove f
            return f'{prefix}"{fstring_content}")'

        # Replace {var} with %s
        new_content = re.sub(var_pattern, "%s", fstring_content)

        # Add variables as separate arguments
        var_args = ", ".join(vars_found)
        return f'{prefix}"{new_content}", {var_args})'

    # Also fix multi-line f-strings
    multiline_pattern = r'(logger\.(?:trace|debug|info|warning|error|critical|exception)\s*\(\s*)f"([^"]*?\\[^"]*?)"'
    content = re.sub(multiline_pattern, replace_fstring, content, flags=re.MULTILINE | re.DOTALL)

    return re.sub(pattern, replace_fstring, content, flags=re.MULTILINE | re.DOTALL)


def process_file(file_path: Path) -> None:
    """Process a single file to fix G004 violations."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        content = fix_logging_fstrings(content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
    except Exception:
        pass


def main() -> None:
    """Main function to fix all G004 violations project-wide."""
    # Find all Python files in project
    python_files = []

    # Source files
    src_dir = Path("src")
    if src_dir.exists():
        python_files.extend(src_dir.rglob("*.py"))

    # Test files
    test_dirs = ["tests", "test"]
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if test_path.exists():
            python_files.extend(test_path.rglob("*.py"))

    # Examples
    examples_dir = Path("examples")
    if examples_dir.exists():
        python_files.extend(examples_dir.rglob("*.py"))

    # Root level scripts
    for py_file in Path().glob("*.py"):
        python_files.append(py_file)

    # Webhook config
    webhook_dir = Path("webhook-config")
    if webhook_dir.exists():
        python_files.extend(webhook_dir.rglob("*.py"))

    for file_path in python_files:
        with contextlib.suppress(Exception):
            process_file(file_path)


if __name__ == "__main__":
    main()
