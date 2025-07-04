#!/usr/bin/env python3
"""Test Oracle WMS Tap with REAL WMS instance."""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from tap_oracle_wms.discovery import EntityDiscovery
from tap_oracle_wms.tap import TapOracleWMS

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
)


def validate_env_config() -> bool:
    """Validate that required environment variables are set."""
    required_vars = [
        "TAP_ORACLE_WMS_BASE_URL",
        "TAP_ORACLE_WMS_USERNAME",
        "TAP_ORACLE_WMS_PASSWORD",
    ]

    missing = []
    placeholder_values = [
        "your_username",
        "your_password",
        "https://your-wms-instance.com",
    ]

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        elif value in placeholder_values:
            missing.append(f"{var} (still has placeholder value)")

    if missing:
        for var in missing:
            pass
        return False

    return True


def get_wms_config():
    """Get WMS configuration from environment."""
    return {
        "base_url": os.getenv("TAP_ORACLE_WMS_BASE_URL"),
        "username": os.getenv("TAP_ORACLE_WMS_USERNAME"),
        "password": os.getenv("TAP_ORACLE_WMS_PASSWORD"),
        "company_code": os.getenv("TAP_ORACLE_WMS_COMPANY_CODE", "*"),
        "facility_code": os.getenv("TAP_ORACLE_WMS_FACILITY_CODE", "*"),
        "page_size": int(os.getenv("TAP_ORACLE_WMS_PAGE_SIZE", "100")),
        "request_timeout": int(os.getenv("TAP_ORACLE_WMS_REQUEST_TIMEOUT", "120")),
        "verify_ssl": os.getenv("TAP_ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
        "record_limit": int(os.getenv("TAP_ORACLE_WMS_RECORD_LIMIT", "10")),
    }


async def test_discovery_real() -> Optional[bool]:
    """Test entity discovery with real WMS."""
    config = get_wms_config()

    discovery = EntityDiscovery(config)

    try:
        # Test 1: Discover entities
        entities = await discovery.discover_entities()

        for _i, (_name, _url) in enumerate(entities.items(), 1):
            pass

        if not entities:
            return False

        # Test 2: Describe first entity
        first_entity = next(iter(entities.keys()))

        metadata = await discovery.describe_entity(first_entity)
        if metadata:
            metadata.get("fields", {})
        else:
            pass

        # Test 3: Get sample data
        samples = await discovery.get_entity_sample(first_entity, limit=3)

        if samples:
            pass
        else:
            pass

        # Test 4: Check access to multiple entities
        accessible_entities = []

        for entity_name in list(entities.keys())[:5]:  # Test first 5
            access = await discovery.check_entity_access(entity_name)
            if access:
                accessible_entities.append(entity_name)
            else:
                pass

        return True

    except Exception as e:
        # Provide helpful debugging info
        if (
            "404" in str(e)
            or "401" in str(e)
            or "403" in str(e)
            or "timeout" in str(e).lower()
            or "ssl" in str(e).lower()
        ):
            pass

        return False


def test_tap_integration() -> Optional[bool]:
    """Test full TAP integration."""
    config = get_wms_config()

    try:
        # Test TAP initialization
        tap = TapOracleWMS(config=config)

        # Test stream discovery (this will call our async discovery)
        streams = tap.discover_streams()

        for _i, _stream in enumerate(streams[:5], 1):  # Show first 5
            pass

        if len(streams) > 5:
            pass

        # Test catalog generation

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    # Validate configuration
    if not validate_env_config():
        return False

    # Run discovery tests
    discovery_success = await test_discovery_real()

    # Run integration tests
    integration_success = test_tap_integration()

    # Final results

    overall_success = discovery_success and integration_success

    if overall_success:
        pass
    else:
        pass

    return overall_success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
