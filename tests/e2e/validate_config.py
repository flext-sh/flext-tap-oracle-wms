#!/usr/bin/env python3
"""Validate E2E test configuration without running tests.

This script checks if the environment is properly configured for E2E tests.
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


def validate_e2e_config():
    """Validate E2E test configuration and provide feedback."""
    # Check for .env file
    env_file = Path(__file__).parent.parent.parent / ".env"
    if not env_file.exists():
        return False

    # Load environment variables
    load_dotenv(env_file)

    # Check required variables
    required_vars = {
        "TAP_ORACLE_WMS_BASE_URL": "Base URL for WMS instance",
        "TAP_ORACLE_WMS_USERNAME": "Username for authentication",
        "TAP_ORACLE_WMS_PASSWORD": "Password for authentication",
    }

    all_valid = True
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            all_valid = False
        else:
            # Mask sensitive values
            if "PASSWORD" in var:
                pass
            elif "USERNAME" in var:
                (
                    value[:2] + "*" * (len(value) - 2)
                    if len(value) > 2
                    else "*" * len(value)
                )
            else:
                pass

            # Validate URL format
            if var == "TAP_ORACLE_WMS_BASE_URL":
                try:
                    result = urlparse(value)
                    if not all([result.scheme, result.netloc]) or result.scheme not in [
                        "http",
                        "https",
                    ]:
                        all_valid = False
                except Exception:
                    all_valid = False

    # Check optional variables
    optional_vars = {
        "TAP_ORACLE_WMS_COMPANY_CODE": ("*", "Company code filter"),
        "TAP_ORACLE_WMS_FACILITY_CODE": ("*", "Facility code filter"),
        "TAP_ORACLE_WMS_PAGE_SIZE": ("100", "Records per page"),
        "TAP_ORACLE_WMS_REQUEST_TIMEOUT": ("120", "Request timeout in seconds"),
        "TAP_ORACLE_WMS_VERIFY_SSL": ("true", "SSL verification"),
        "TAP_ORACLE_WMS_RECORD_LIMIT": ("10", "Max records for tests"),
    }

    for var in optional_vars:
        value = os.getenv(var)
        if not value:
            pass

        # Validate numeric values
        elif var in [
            "TAP_ORACLE_WMS_PAGE_SIZE",
            "TAP_ORACLE_WMS_REQUEST_TIMEOUT",
            "TAP_ORACLE_WMS_RECORD_LIMIT",
        ]:
            try:
                int_value = int(value)
                if var == "TAP_ORACLE_WMS_PAGE_SIZE" and not (1 <= int_value <= 1250):
                    pass
            except ValueError:
                all_valid = False

    # Summary
    if all_valid:
        pass
    else:
        pass

    return all_valid


if __name__ == "__main__":
    valid = validate_e2e_config()
    sys.exit(0 if valid else 1)
