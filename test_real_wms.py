#!/usr/bin/env python3
"""Test Oracle WMS Tap with REAL WMS instance."""

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from tap_oracle_wms.discovery import EntityDiscovery
from tap_oracle_wms.tap import TapOracleWMS

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print("❌ No .env file found!")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
)

def validate_env_config():
    """Validate that required environment variables are set."""
    required_vars = [
        "TAP_ORACLE_WMS_BASE_URL",
        "TAP_ORACLE_WMS_USERNAME",
        "TAP_ORACLE_WMS_PASSWORD",
    ]

    missing = []
    placeholder_values = ["your_username", "your_password", "https://your-wms-instance.com"]

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        elif value in placeholder_values:
            missing.append(f"{var} (still has placeholder value)")

    if missing:
        print("❌ Missing or placeholder environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\n💡 Update your .env file with real values:")
        print("   TAP_ORACLE_WMS_BASE_URL=https://your-real-wms.company.com")
        print("   TAP_ORACLE_WMS_USERNAME=your_real_username")
        print("   TAP_ORACLE_WMS_PASSWORD=your_real_password")
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

async def test_discovery_real():
    """Test entity discovery with real WMS."""
    print("\n" + "="*60)
    print("🔍 TESTING ENTITY DISCOVERY WITH REAL WMS")
    print("="*60)

    config = get_wms_config()
    print(f"🌐 Base URL: {config['base_url']}")
    print(f"👤 Username: {config['username']}")
    print(f"🏢 Company: {config['company_code']}")
    print(f"🏭 Facility: {config['facility_code']}")

    discovery = EntityDiscovery(config)

    try:
        # Test 1: Discover entities
        print(f"\n1️⃣ Discovering entities from {discovery.entity_endpoint}")
        entities = await discovery.discover_entities()

        print(f"✅ SUCCESS: Found {len(entities)} entities")
        for i, (name, url) in enumerate(entities.items(), 1):
            print(f"   {i:2d}. {name}")

        if not entities:
            print("⚠️  No entities found. Check your WMS permissions.")
            return False

        # Test 2: Describe first entity
        first_entity = next(iter(entities.keys()))
        print(f"\n2️⃣ Describing entity '{first_entity}'")

        metadata = await discovery.describe_entity(first_entity)
        if metadata:
            print(f"✅ SUCCESS: Got metadata for {first_entity}")
            fields = metadata.get("fields", {})
            print(f"   Fields ({len(fields)}): {', '.join(fields.keys())}")
        else:
            print(f"⚠️  No metadata available for {first_entity}")

        # Test 3: Get sample data
        print(f"\n3️⃣ Getting sample data from '{first_entity}'")
        samples = await discovery.get_entity_sample(first_entity, limit=3)

        if samples:
            print(f"✅ SUCCESS: Got {len(samples)} sample records")
            print(f"   Sample record fields: {', '.join(samples[0].keys())}")
            print(f"   First record: {samples[0]}")
        else:
            print(f"⚠️  No sample data available for {first_entity}")

        # Test 4: Check access to multiple entities
        print("\n4️⃣ Testing access to entities")
        accessible_entities = []

        for entity_name in list(entities.keys())[:5]:  # Test first 5
            access = await discovery.check_entity_access(entity_name)
            if access:
                accessible_entities.append(entity_name)
                print(f"   ✅ {entity_name}: Accessible")
            else:
                print(f"   ❌ {entity_name}: No access")

        print(f"\n📊 Summary: {len(accessible_entities)}/{len(entities)} entities accessible")

        return True

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")

        # Provide helpful debugging info
        if "404" in str(e):
            print("\n💡 Debug: 404 Not Found")
            print("   - Check if the base URL is correct")
            print("   - Verify the WMS API endpoint path")
            print(f"   - Tried: {discovery.entity_endpoint}")

        elif "401" in str(e) or "403" in str(e):
            print("\n💡 Debug: Authentication/Authorization Error")
            print("   - Check username and password")
            print("   - Verify WMS permissions")
            print("   - Check company/facility codes")

        elif "timeout" in str(e).lower():
            print("\n💡 Debug: Connection Timeout")
            print("   - Check network connectivity")
            print("   - Increase request_timeout in .env")
            print("   - Check if WMS server is running")

        elif "ssl" in str(e).lower():
            print("\n💡 Debug: SSL Error")
            print("   - Try setting TAP_ORACLE_WMS_VERIFY_SSL=false")
            print("   - Check SSL certificate configuration")

        return False

def test_tap_integration():
    """Test full TAP integration."""
    print("\n" + "="*60)
    print("🎯 TESTING FULL TAP INTEGRATION")
    print("="*60)

    config = get_wms_config()

    try:
        # Test TAP initialization
        print("1️⃣ Initializing TAP...")
        tap = TapOracleWMS(config=config)
        print(f"✅ TAP initialized: {tap.name}")

        # Test stream discovery (this will call our async discovery)
        print("\n2️⃣ Discovering streams...")
        streams = tap.discover_streams()
        print(f"✅ SUCCESS: Discovered {len(streams)} streams")

        for i, stream in enumerate(streams[:5], 1):  # Show first 5
            print(f"   {i}. {stream.name} (replication: {stream.replication_method})")

        if len(streams) > 5:
            print(f"   ... and {len(streams) - 5} more streams")

        # Test catalog generation
        print("\n3️⃣ Generating catalog...")
        catalog_dict = tap.catalog_dict
        print(f"✅ SUCCESS: Catalog has {len(catalog_dict.get('streams', []))} stream definitions")

        return True

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 ORACLE WMS TAP - REAL ENVIRONMENT TESTING")
    print("=" * 60)

    # Validate configuration
    if not validate_env_config():
        print("\n❌ Configuration validation failed!")
        print("Please update your .env file with real WMS credentials.")
        return False

    print("✅ Environment configuration validated")

    # Run discovery tests
    discovery_success = await test_discovery_real()

    # Run integration tests
    integration_success = test_tap_integration()

    # Final results
    print("\n" + "="*60)
    print("📋 FINAL RESULTS")
    print("="*60)
    print(f"🔍 Discovery Tests: {'✅ PASSED' if discovery_success else '❌ FAILED'}")
    print(f"🎯 Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")

    overall_success = discovery_success and integration_success
    print(f"\n🏆 OVERALL: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")

    if overall_success:
        print("\n🎉 Congratulations! Your Oracle WMS Tap is working correctly!")
        print("You can now use it for data extraction:")
        print("   python -m tap_oracle_wms --config config.json --discover")
        print("   python -m tap_oracle_wms --config config.json --catalog catalog.json")
    else:
        print("\n🔧 Please fix the issues above and try again.")

    return overall_success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
