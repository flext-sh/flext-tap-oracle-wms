#!/usr/bin/env python3
"""Fix G004 ruff violations (f-strings in logging) systematically."""

import contextlib
from pathlib import Path
import re
import sys


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

    return re.sub(pattern, replace_fstring, content, flags=re.MULTILINE | re.DOTALL)


def process_file(file_path: Path) -> None:
    """Process a single file to fix G004 violations."""
    content = file_path.read_text(encoding="utf-8")
    original_content = content

    content = fix_logging_fstrings(content)

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")


def main() -> None:
    """Main function to fix all G004 violations."""
    src_dir = Path("src/tap_oracle_wms")

    if not src_dir.exists():
        sys.exit(1)

    python_files = list(src_dir.glob("*.py"))

    for file_path in python_files:
        with contextlib.suppress(Exception):
            process_file(file_path)


if __name__ == "__main__":
    main()
