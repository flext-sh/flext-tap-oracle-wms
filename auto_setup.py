#!/usr/bin/env python3
"""Auto-setup Oracle WMS Tap with real credentials detection."""

import os
import sys
from pathlib import Path

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

    if not base_url or any(pattern in base_url.lower() for pattern in placeholder_patterns):
        return False, f"Base URL not configured: {base_url}"

    if not username or any(pattern in username.lower() for pattern in placeholder_patterns):
        return False, f"Username not configured: {username}"

    if not password or any(pattern in password.lower() for pattern in placeholder_patterns):
        return False, f"Password not configured: {password}"

    return True, {
        "base_url": base_url,
        "username": username,
        "password": password,
        "company_code": os.getenv("TAP_ORACLE_WMS_COMPANY_CODE", "*"),
        "facility_code": os.getenv("TAP_ORACLE_WMS_FACILITY_CODE", "*"),
        "verify_ssl": os.getenv("TAP_ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
    }


def test_connection(config):
    """Test connection to Oracle WMS with provided config."""
    try:
        import asyncio

        from tap_oracle_wms.discovery import EntityDiscovery

        print(f"Testing connection to: {config['base_url']}")
        print(f"Username: {config['username']}")
        print(f"Company: {config['company_code']}")
        print(f"Facility: {config['facility_code']}")

        discovery = EntityDiscovery(config)
        entities = asyncio.run(discovery.discover_entities())

        if entities:
            print(f"✅ SUCCESS: Connected and found {len(entities)} entities")
            for i, entity in enumerate(list(entities.keys())[:5], 1):
                print(f"  {i}. {entity}")
            if len(entities) > 5:
                print(f"  ... and {len(entities) - 5} more entities")
            return True
        print("⚠️  Connected but no entities found")
        return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def create_working_config():
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
    with open("working_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("✅ Created working_config.json")
    return "working_config.json"


def main():
    """Main auto-setup function."""
    print("🔍 Oracle WMS Tap Auto-Setup")
    print("=" * 40)

    # Step 1: Check for valid credentials
    print("1. Checking credentials...")
    is_valid, result = detect_valid_credentials()

    if not is_valid:
        print(f"❌ {result}")
        print("\n💡 To fix this:")
        print("   1. Edit .env file with real Oracle WMS credentials")
        print("   2. Update TAP_ORACLE_WMS_BASE_URL with your WMS URL")
        print("   3. Update TAP_ORACLE_WMS_USERNAME with your username")
        print("   4. Update TAP_ORACLE_WMS_PASSWORD with your password")
        print("   5. Run this script again")
        return False

    config = result
    print("✅ Valid credentials detected")

    # Step 2: Test connection
    print("\n2. Testing Oracle WMS connection...")
    connection_ok = test_connection(config)

    if not connection_ok:
        print("\n❌ Connection test failed")
        print("💡 Check your credentials and WMS server accessibility")
        return False

    # Step 3: Create working configuration
    print("\n3. Creating working configuration...")
    config_file = create_working_config()

    # Step 4: Success summary
    print("\n🎉 AUTO-SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 40)
    print("✅ Credentials validated")
    print("✅ WMS connection tested")
    print("✅ Working configuration created")
    print(f"✅ Config file: {config_file}")

    print("\n🚀 Ready to use! Try these commands:")
    print("   make check-connection  # Test connection")
    print("   make test-entity      # Test entity extraction")
    print("   make discover         # Discover all entities")
    print("   make e2e-test         # Complete end-to-end test")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
