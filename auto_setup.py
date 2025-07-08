#!/usr/bin/env python3
"""Auto-setup Oracle WMS Tap with real credentials detection."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from dotenv import load_dotenv


def detect_valid_credentials():
    """Detect if .env has valid credentials (not placeholders)."""
    env_file = Path(".env")
    if not env_file.exists():
        return False, "No .env file found"

    load_dotenv(env_file)

    # Check for placeholder values
    base_url = os.getenv("TAP_ORACLE_WMS_BASE_URL", "")
    username = os.getenv("TAP_ORACLE_WMS_USERNAME", "")
    password = os.getenv("TAP_ORACLE_WMS_PASSWORD", "")

    # Check if values are set and not placeholders
    placeholder_patterns = ["your-", "your_", "example", "placeholder"]

    if not base_url or any(
        pattern in base_url.lower() for pattern in placeholder_patterns
    ):
        return False, f"Base URL not configured: {base_url}"

    if not username or any(
        pattern in username.lower() for pattern in placeholder_patterns
    ):
        return False, f"Username not configured: {username}"

    if not password or any(
        pattern in password.lower() for pattern in placeholder_patterns
    ):
        return False, f"Password not configured: {password}"

    return True, {
        "base_url": base_url,
        "username": username,
        "password": password,
        "company_code": os.getenv("TAP_ORACLE_WMS_COMPANY_CODE", "*"),
        "facility_code": os.getenv("TAP_ORACLE_WMS_FACILITY_CODE", "*"),
        "verify_ssl": os.getenv("TAP_ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
    }


def test_connection(config) -> bool | None:
    """Test connection to Oracle WMS with provided config."""
    try:
        import asyncio

        from tap_oracle_wms.discovery import EntityDiscovery

        discovery = EntityDiscovery(config)
        entities = asyncio.run(discovery.discover_entities())

        if entities:
            for _i, _entity in enumerate(list(entities.keys())[:5], 1):
                pass
            if len(entities) > 5:
                pass
            return True
        return False

    except Exception:
        return False


def create_working_config() -> str:
    """Create a working test configuration file."""
    config = {
        "base_url": os.getenv("TAP_ORACLE_WMS_BASE_URL"),
        "username": os.getenv("TAP_ORACLE_WMS_USERNAME"),
        "password": os.getenv("TAP_ORACLE_WMS_PASSWORD"),
        "company_code": os.getenv("TAP_ORACLE_WMS_COMPANY_CODE", "*"),
        "facility_code": os.getenv("TAP_ORACLE_WMS_FACILITY_CODE", "*"),
        "verify_ssl": os.getenv("TAP_ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
        "page_size": int(os.getenv("TAP_ORACLE_WMS_PAGE_SIZE", "100")),
        "request_timeout": int(os.getenv("TAP_ORACLE_WMS_REQUEST_TIMEOUT", "120")),
        "record_limit": int(os.getenv("TAP_ORACLE_WMS_RECORD_LIMIT", "10")),
    }

    import json

    with open("working_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    return "working_config.json"


def main() -> bool:
    """Main auto-setup function."""
    # Step 1: Check for valid credentials
    is_valid, result = detect_valid_credentials()

    if not is_valid:
        return False

    config = result

    # Step 2: Test connection
    connection_ok = test_connection(config)

    if not connection_ok:
        return False

    # Step 3: Create working configuration
    create_working_config()

    # Step 4: Success summary

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
