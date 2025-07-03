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
    print("Oracle WMS Tap - E2E Test Configuration Validator")
    print("=" * 50)

    # Check for .env file
    env_file = Path(__file__).parent.parent.parent / ".env"
    if not env_file.exists():
        print("\n❌ ERROR: .env file not found!")
        print(f"   Expected location: {env_file}")
        print("\n   To fix:")
        print("   1. Copy .env.example to .env")
        print("   2. Fill in your WMS credentials")
        print(f"\n   cd {env_file.parent}")
        print("   cp .env.example .env")
        print("   # Edit .env with your WMS details")
        return False

    print(f"\n✓ Found .env file at: {env_file}")

    # Load environment variables
    load_dotenv(env_file)

    # Check required variables
    print("\nChecking required environment variables:")
    required_vars = {
        "TAP_ORACLE_WMS_BASE_URL": "Base URL for WMS instance",
        "TAP_ORACLE_WMS_USERNAME": "Username for authentication",
        "TAP_ORACLE_WMS_PASSWORD": "Password for authentication",
    }

    all_valid = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"\n❌ {var}: NOT SET")
            print(f"   Description: {description}")
            all_valid = False
        else:
            # Mask sensitive values
            if "PASSWORD" in var:
                display_value = "*" * 8
            elif "USERNAME" in var:
                display_value = value[:2] + "*" * (len(value) - 2) if len(value) > 2 else "*" * len(value)
            else:
                display_value = value

            print(f"\n✓ {var}: {display_value}")

            # Validate URL format
            if var == "TAP_ORACLE_WMS_BASE_URL":
                try:
                    result = urlparse(value)
                    if not all([result.scheme, result.netloc]):
                        print("   ⚠️  WARNING: URL format seems invalid")
                        print("   Expected format: https://your-wms-instance.com")
                        all_valid = False
                    elif result.scheme not in ["http", "https"]:
                        print("   ⚠️  WARNING: URL scheme should be http or https")
                        all_valid = False
                except Exception as e:
                    print(f"   ❌ ERROR: Invalid URL format: {e}")
                    all_valid = False

    # Check optional variables
    print("\n\nChecking optional environment variables:")
    optional_vars = {
        "TAP_ORACLE_WMS_COMPANY_CODE": ("*", "Company code filter"),
        "TAP_ORACLE_WMS_FACILITY_CODE": ("*", "Facility code filter"),
        "TAP_ORACLE_WMS_PAGE_SIZE": ("100", "Records per page"),
        "TAP_ORACLE_WMS_REQUEST_TIMEOUT": ("120", "Request timeout in seconds"),
        "TAP_ORACLE_WMS_VERIFY_SSL": ("true", "SSL verification"),
        "TAP_ORACLE_WMS_RECORD_LIMIT": ("10", "Max records for tests"),
    }

    for var, (default, description) in optional_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"\n- {var}: NOT SET (will use default: {default})")
            print(f"  Description: {description}")
        else:
            print(f"\n✓ {var}: {value}")

            # Validate numeric values
            if var in ["TAP_ORACLE_WMS_PAGE_SIZE", "TAP_ORACLE_WMS_REQUEST_TIMEOUT", "TAP_ORACLE_WMS_RECORD_LIMIT"]:
                try:
                    int_value = int(value)
                    if var == "TAP_ORACLE_WMS_PAGE_SIZE" and not (1 <= int_value <= 1250):
                        print("  ⚠️  WARNING: Page size should be between 1 and 1250")
                except ValueError:
                    print(f"  ❌ ERROR: {var} must be a number")
                    all_valid = False

    # Summary
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ Configuration is valid! E2E tests can run.")
        print("\nTo run E2E tests:")
        print("  pytest tests/e2e --run-e2e")
        print("\nTo run specific test:")
        print("  pytest tests/e2e/test_wms_e2e.py::test_tap_initialization --run-e2e -v")
    else:
        print("❌ Configuration has errors. Please fix them before running E2E tests.")
        print("\nExample .env configuration:")
        print("  TAP_ORACLE_WMS_BASE_URL=https://wms.example.com")
        print("  TAP_ORACLE_WMS_USERNAME=your_username")
        print("  TAP_ORACLE_WMS_PASSWORD=your_password")

    return all_valid


if __name__ == "__main__":
    valid = validate_e2e_config()
    sys.exit(0 if valid else 1)
