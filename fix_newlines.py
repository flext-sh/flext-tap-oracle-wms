#!/usr/bin/env python3
"""Fix missing newlines at end of files."""

from pathlib import Path


def fix_missing_newlines() -> None:
    """Fix files that don't end with newline."""
    files_fixed = []

    # Check Python files
    for pattern in ["src/**/*.py", "examples/**/*.py", "*.py"]:
        for file_path in Path().glob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    if content and not content.endswith("\n"):
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content + "\n")
                        files_fixed.append(str(file_path))

                except Exception:
                    pass

    if files_fixed:
        pass
    else:
        pass

    return files_fixed


if __name__ == "__main__":
    fix_missing_newlines()
