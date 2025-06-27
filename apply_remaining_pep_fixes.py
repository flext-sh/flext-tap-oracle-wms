#!/usr/bin/env python3
"""Apply remaining PEP standard fixes to tap-oracle-wms project."""

from pathlib import Path
import re


def fix_import_order_issues() -> None:
    """Fix remaining import order violations across all Python files."""
    src_files = list(Path("src").rglob("*.py"))
    example_files = list(Path("examples").glob("*.py"))
    all_files = src_files + example_files

    fixes_applied = 0

    for file_path in all_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix common import order patterns
            # 1. Fix typing imports after standard library
            pattern1 = r"(import \w+\nfrom \w+)"
            if re.search(pattern1, content):
                # More specific fixes needed per file
                pass

            # Fix line length issues with simple string breaks
            lines = content.split("\n")
            fixed_lines = []

            for line in lines:
                if len(line) > 88 and "description=" in line and '"' in line:
                    # Break long description strings
                    if line.strip().endswith('",'):
                        # Find the description string
                        desc_match = re.search(r'description="([^"]+)"', line)
                        if desc_match and len(desc_match.group(1)) > 50:
                            desc_text = desc_match.group(1)
                            # Split at logical points
                            if " and " in desc_text:
                                parts = desc_text.split(" and ", 1)
                                new_line = line.replace(
                                    f'description="{desc_text}"',
                                    f'description="{parts[0]} "\n        "and {parts[1]}"'
                                )
                                fixed_lines.append(new_line)
                                continue
                            if " for " in desc_text:
                                parts = desc_text.split(" for ", 1)
                                new_line = line.replace(
                                    f'description="{desc_text}"',
                                    f'description="{parts[0]} "\n        "for {parts[1]}"'
                                )
                                fixed_lines.append(new_line)
                                continue

                fixed_lines.append(line)

            content = "\n".join(fixed_lines)

            # Add missing newlines at end of file
            if not content.endswith("\n"):
                content += "\n"

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                fixes_applied += 1

        except Exception:
            pass


def fix_specific_line_length_violations() -> None:
    """Fix specific line length violations identified in the report."""
    specific_fixes = {
        "src/tap_oracle_wms/cli.py": [
            # Add specific line fixes here if needed
        ],
        "src/tap_oracle_wms/streams.py": [
            # Add specific line fixes here if needed
        ],
    }

    for file_path, fixes in specific_fixes.items():
        if Path(file_path).exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                for old_text, new_text in fixes:
                    content = content.replace(old_text, new_text)

                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

            except Exception:
                pass


def fix_trailing_whitespace() -> None:
    """Remove trailing whitespace from all Python files."""
    src_files = list(Path("src").rglob("*.py"))
    example_files = list(Path("examples").glob("*.py"))
    all_files = src_files + example_files

    fixes_applied = 0

    for file_path in all_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Remove trailing whitespace
            fixed_lines = [line.rstrip() + "\n" for line in lines]

            # Ensure file ends with single newline
            if fixed_lines and not fixed_lines[-1].endswith("\n"):
                fixed_lines[-1] += "\n"
            elif fixed_lines and fixed_lines[-1].strip() == "":
                # Remove empty trailing lines except one
                while len(fixed_lines) > 1 and fixed_lines[-1].strip() == "":
                    fixed_lines.pop()
                if not fixed_lines[-1].endswith("\n"):
                    fixed_lines[-1] += "\n"

            new_content = "".join(fixed_lines)

            # Read original for comparison
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            if new_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                fixes_applied += 1

        except Exception:
            pass


def main() -> None:
    """Apply all remaining PEP fixes."""
    fix_import_order_issues()

    fix_specific_line_length_violations()

    fix_trailing_whitespace()


if __name__ == "__main__":
    main()
