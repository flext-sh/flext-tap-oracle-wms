#!/usr/bin/env python3
"""Fix common lint issues across all files."""

from __future__ import annotations

from pathlib import Path
import re


def fix_line_length_issues(content: str) -> str:
    """Fix E501 line length issues."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if len(line) > 88:
            # Check if it's a string that can be split
            if '"' in line or "'" in line:
                # Try to split at a natural break point
                if " and " in line:
                    parts = line.split(" and ", 1)
                    if len(parts) == 2:
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.append(parts[0] + " and")
                        fixed_lines.append(" " * (indent + 4) + parts[1])
                        continue
                elif " or " in line:
                    parts = line.split(" or ", 1)
                    if len(parts) == 2:
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.append(parts[0] + " or")
                        fixed_lines.append(" " * (indent + 4) + parts[1])
                        continue
        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_logging_fstrings(content: str) -> str:
    """Fix G004 logging f-string issues."""
    # Replace logger.warning(f"...") with logger.warning("...", vars)
    pattern = r'logger\.(debug|info|warning|error)\(f"([^"]+)"\)'

    def replacer(match):
        level = match.group(1)
        msg = match.group(2)
        # Extract variables from f-string
        vars_in_msg = re.findall(r"\{(\w+)\}", msg)
        if vars_in_msg:
            clean_msg = re.sub(r"\{(\w+)\}", r"%s", msg)
            return f'logger.{level}("{clean_msg}", {", ".join(vars_in_msg)})'
        return match.group(0)

    return re.sub(pattern, replacer, content)


def fix_magic_values(content: str) -> str:
    """Fix PLR2004 magic value issues."""
    # Common magic values that should be constants
    replacements = {
        "200": "HTTP_OK",
        "404": "HTTP_NOT_FOUND",
        "401": "HTTP_UNAUTHORIZED",
        "403": "HTTP_FORBIDDEN",
        "429": "HTTP_TOO_MANY_REQUESTS",
        "500": "HTTP_SERVER_ERROR",
    }

    for value, constant in replacements.items():
        # Only replace in comparisons
        content = re.sub(
            rf"(\s==\s|!=\s|>\s|<\s|>=\s|<=\s){value}(\s|\))",
            rf"\1{constant}\2",
            content,
        )

    return content


def fix_file(file_path: Path) -> None:
    """Fix common issues in a single file."""
    print(f"Fixing {file_path}")

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Apply fixes
    content = fix_line_length_issues(content)
    content = fix_logging_fstrings(content)
    content = fix_magic_values(content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Fix all Python files in src/tap_oracle_wms/."""
    src_dir = Path("src/tap_oracle_wms")

    for py_file in src_dir.glob("*.py"):
        if py_file.name != "__pycache__":
            fix_file(py_file)

    print("Done fixing common lint issues")


if __name__ == "__main__":
    main()
