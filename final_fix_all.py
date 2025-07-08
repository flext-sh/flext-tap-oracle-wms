#!/usr/bin/env python3
"""Final comprehensive fix for all lint issues."""

from __future__ import annotations

from pathlib import Path
import re

# Define constants for magic numbers
CONSTANTS = """
# API and Performance Constants
MAX_PAGE_SIZE = 1250
MAX_REQUEST_TIMEOUT = 600
MAX_RETRIES = 10
DEFAULT_FIELD_DISPLAY_LIMIT = 10
HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_TOO_MANY_REQUESTS = 429
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500
HTTP_STATUS_SERVER_ERROR_END = 600
DEFAULT_RETRY_AFTER = 60
"""


def fix_undefined_names(content: str) -> str:
    """Fix undefined name errors like 'from e' without exception."""
    # Fix patterns where 'from e' is used without an exception variable
    lines = content.split("\n")
    fixed_lines = []
    in_except_block = False
    has_exception_var = False

    for i, line in enumerate(lines):
        if "except" in line and ":" in line:
            in_except_block = True
            has_exception_var = " as " in line
            fixed_lines.append(line)
        elif (
            in_except_block
            and "raise" in line
            and "from e" in line
            and not has_exception_var
        ):
            # Remove 'from e' if there's no exception variable
            fixed_lines.append(line.replace(" from e", ""))
        else:
            if line.strip() and not line.strip().startswith(("except", "finally")):
                in_except_block = False
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def add_constants_to_file(file_path: Path) -> None:
    """Add constants to the top of the file if they don't exist."""
    content = file_path.read_text()

    # Check if constants are already defined
    if "MAX_PAGE_SIZE" not in content:
        # Find the right place to insert constants (after imports)
        lines = content.split("\n")
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(("import ", "from ", "#", '"""')):
                import_end = i
                break

        # Insert constants
        lines.insert(import_end, CONSTANTS)
        content = "\n".join(lines)
        file_path.write_text(content)


def fix_magic_numbers(content: str) -> str:
    """Replace magic numbers with constants."""
    replacements = [
        (r"\b1250\b", "MAX_PAGE_SIZE"),
        (r"\b600\b", "MAX_REQUEST_TIMEOUT"),
        (r"> 10\b", "> MAX_RETRIES"),
        (r"\b200\b", "HTTP_STATUS_OK"),
        (r"\b400\b", "HTTP_STATUS_BAD_REQUEST"),
        (r"\b401\b", "HTTP_STATUS_UNAUTHORIZED"),
        (r"\b403\b", "HTTP_STATUS_FORBIDDEN"),
        (r"\b404\b", "HTTP_STATUS_NOT_FOUND"),
        (r"\b429\b", "HTTP_STATUS_TOO_MANY_REQUESTS"),
        (r"\b500\b", "HTTP_STATUS_INTERNAL_SERVER_ERROR"),
        (r"< 600\b", "< HTTP_STATUS_SERVER_ERROR_END"),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    return content


def fix_long_lines(content: str) -> str:
    """Fix long lines by breaking them appropriately."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if len(line) > 88:
            # Handle string literals in error messages
            if "self.errors.append(" in line or "self.warnings.append(" in line:
                # Break at the string
                match = re.search(r"(.*append\()(.*)\)(.*)$", line)
                if match:
                    indent = len(match.group(1)) - len(match.group(1).lstrip())
                    fixed_lines.append(match.group(1))
                    fixed_lines.append(" " * (indent + 4) + match.group(2))
                    fixed_lines.append(" " * indent + ")" + match.group(3))
                else:
                    fixed_lines.append(line)
            elif "description=" in line and '"' in line:
                # Break long descriptions
                parts = line.split('description="', 1)
                if len(parts) == 2:
                    desc_and_rest = parts[1]
                    desc_parts = desc_and_rest.split('"', 1)
                    if len(desc_parts) == 2:
                        desc = desc_parts[0]
                        rest = desc_parts[1]
                        if len(desc) > 60:
                            # Split description
                            mid = len(desc) // 2
                            split_point = desc.rfind(" ", 0, mid)
                            if split_point == -1:
                                split_point = mid

                            indent = len(parts[0]) - len(parts[0].lstrip())
                            fixed_lines.append(
                                parts[0] + 'description="' + desc[:split_point] + '"'
                            )
                            fixed_lines.append(
                                " " * (indent + 4)
                                + '"'
                                + desc[split_point:].strip()
                                + '"'
                                + rest
                            )
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_file(file_path: Path) -> bool:
    """Fix a single file."""
    print(f"Fixing {file_path.name}...")

    try:
        content = file_path.read_text()
        original_content = content

        # Apply fixes
        content = fix_undefined_names(content)
        content = fix_magic_numbers(content)
        content = fix_long_lines(content)

        # Fix specific patterns
        if file_path.name == "type_mapping.py":
            # Remove unused parameters
            content = re.sub(
                r"def _create_schema_from_metadata\(\s*metadata_type: str,\s*max_length: int \| None,\s*\)",
                "def _create_schema_from_metadata(\n    metadata_type: str,\n)",
                content,
            )
            content = re.sub(
                r"def _create_pattern_schema\(pattern_key: str, max_length: int \| None\)",
                "def _create_pattern_schema(pattern_key: str)",
                content,
            )

        if content != original_content:
            # Add constants if needed
            if any(
                const in content
                for const in ["MAX_PAGE_SIZE", "HTTP_STATUS_OK", "MAX_RETRIES"]
            ):
                add_constants_to_file(file_path)
                # Re-read and apply fixes again
                content = file_path.read_text()
                content = fix_undefined_names(content)
                content = fix_magic_numbers(content)
                content = fix_long_lines(content)

            file_path.write_text(content)
            print(f"✅ Fixed {file_path.name}")
            return True
        print(f"ℹ️  No changes needed for {file_path.name}")
        return False

    except Exception as e:
        print(f"❌ Error fixing {file_path.name}: {e}")
        return False


def main():
    """Main function."""
    src_dir = Path("src/tap_oracle_wms")

    # Files with issues
    files_to_fix = [
        "config_validator.py",
        "config_profiles.py",
        "config_mapper.py",
        "tap.py",
        "entity_discovery.py",
        "critical_validation.py",
        "schema_generator.py",
        "type_mapping.py",
        "discovery.py",
        "cache_manager.py",
        "auth.py",
        "streams.py",
    ]

    fixed_count = 0
    for filename in files_to_fix:
        file_path = src_dir / filename
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1

    print(f"\n✅ Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
