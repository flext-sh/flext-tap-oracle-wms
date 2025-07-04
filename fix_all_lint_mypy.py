#!/usr/bin/env python3
"""Fix all lint and mypy issues for strict compliance."""

import os
import re
import subprocess


def fix_error_logging() -> None:
    """Fix error_logging.py - add from __future__ import annotations."""
    file_path = "src/tap_oracle_wms/error_logging.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Add from __future__ import annotations at the top
    if "from __future__ import annotations" not in content:
        lines = content.split("\n")
        # Insert after docstring but before first import
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') and '"""' in line[3:]:
                # Single line docstring
                insert_idx = i + 1
                break
            if line.strip().startswith('"""'):
                # Multi-line docstring
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j]:
                        insert_idx = j + 1
                        break
                break
            if not line.strip() or line.strip().startswith("#"):
                continue
            insert_idx = i
            break

        lines.insert(insert_idx, "\nfrom __future__ import annotations")
        content = "\n".join(lines)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_streams_py() -> None:
    """Fix streams.py - remove f-strings from exceptions and fix error messages."""
    file_path = "src/tap_oracle_wms/streams.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix f-string in exception
    content = re.sub(
        r'raise ValueError\(f"Invalid pagination token query: \{e\}"\)',
        'msg = f"Invalid pagination token query: {e}"\n                raise ValueError(msg)',
        content,
    )

    # Fix string literals in exceptions
    content = re.sub(
        r'raise ValueError\("Bookmark ID cannot be negative"\)',
        'msg = "Bookmark ID cannot be negative"\n                    raise ValueError(msg)',
        content,
    )

    content = re.sub(
        r'raise ValueError\("Bookmark ID suspiciously large"\)',
        'msg = "Bookmark ID suspiciously large"\n                    raise ValueError(msg)',
        content,
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_cli_enhanced() -> None:
    """Fix cli_enhanced.py - change logger.error to logger.exception for exceptions."""
    file_path = "src/tap_oracle_wms/cli_enhanced.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Replace logger.error with logger.exception in exception handlers
    content = re.sub(
        r'logger\.error\("❌ CONFIGURATION ERROR - Invalid tap configuration: %s", e\)',
        'logger.exception("❌ CONFIGURATION ERROR - Invalid tap configuration: %s", e)',
        content,
    )

    content = re.sub(
        r'logger\.error\("❌ CONNECTION FAILED - Cannot connect to Oracle WMS: %s", e\)',
        'logger.exception("❌ CONNECTION FAILED - Cannot connect to Oracle WMS: %s", e)',
        content,
    )

    content = re.sub(
        r'logger\.error\("❌ ENTITY LISTING FAILED - Cannot list entities: %s", e\)',
        'logger.exception("❌ ENTITY LISTING FAILED - Cannot list entities: %s", e)',
        content,
    )

    content = re.sub(
        r'logger\.error\("❌ ENTITY DESCRIPTION FAILED - Cannot describe entity: %s", e\)',
        'logger.exception("❌ ENTITY DESCRIPTION FAILED - Cannot describe entity: %s", e)',
        content,
    )

    content = re.sub(
        r'logger\.error\("❌ EXTRACTION TEST FAILED - Data extraction test failed: %s", e\)',
        'logger.exception("❌ EXTRACTION TEST FAILED - Data extraction test failed: %s", e)',
        content,
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_discovery_py() -> None:
    """Fix discovery.py - remove duplicate exception handlers and fix logger patterns."""
    file_path = "src/tap_oracle_wms/discovery.py"

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Fix logger.error to logger.exception
    content = re.sub(
        r'logger\.error\("Entity %s does not exist \(404\) - check entity name or permissions", entity_name\)',
        'logger.exception("Entity %s does not exist (404) - check entity name or permissions", entity_name)',
        content,
    )

    # Remove the malformed/duplicate exception handlers at the end of describe_entity method
    # Find the describe_entity method and clean it up
    content = re.sub(
        r"(except \(ValueError, KeyError, TypeError\) as e:\s+# Data parsing errors during optional size estimation\s+logger\.warning\([^)]+\)\s+return None)\s+# All other HTTP errors in size estimation.*?return None",
        r"\1",
        content,
        flags=re.DOTALL,
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def fix_config_constants() -> None:
    """Make sure config.py has necessary constants."""
    file_path = "src/tap_oracle_wms/config.py"

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                '''"""Configuration constants for Oracle WMS tap."""

# HTTP status codes
HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_FORBIDDEN = 403
HTTP_UNAUTHORIZED = 401
HTTP_TOO_MANY_REQUESTS = 429
HTTP_SERVER_ERROR = 500

# Default values
DEFAULT_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
'''
            )
    else:
        pass


def main() -> None:
    """Fix all lint and mypy issues."""
    try:
        os.chdir("/home/marlonsc/flext/flext-tap-oracle-wms")

        fix_error_logging()
        fix_streams_py()
        fix_cli_enhanced()
        fix_discovery_py()
        fix_config_constants()

        # Run quick test
        result = subprocess.run(
            ["python", "-m", "mypy", "src/tap_oracle_wms/", "--strict"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            pass
        else:
            pass

    except Exception:
        raise


if __name__ == "__main__":
    main()
