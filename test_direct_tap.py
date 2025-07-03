#!/usr/bin/env python3
"""Test direto do tap para verificar o problema."""

import json
import sys

# Add path for imports
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

def test_tap_directly():
    """Test tap discovery and extraction directly."""
    print("🧪 Testing tap-oracle-wms directly...")

    # Configuração básica
    config = {
        "base_url": "https://algar.gruponos.io:9043",  # WMS API URL
        "client_id": "gruponos_external",
        "client_secret": "GrupoNOS@2024!Secure",
        "username": "GRUPONOS_EXTERNAL",
        "password": "GrupoNOS@2024!External",
        "company_code": "*",
        "facility_code": "*",
        "entities": ["allocation", "order_hdr", "order_dtl"],
        "page_size": 10,
        "start_date": "2025-01-01T00:00:00Z",
    }

    print(f"📋 Config: {json.dumps(config, indent=2)}")

    try:
        # Import tap
        from tap_oracle_wms.tap import TapOracleWMS

        # Create tap instance
        tap = TapOracleWMS(config=config)

        print("✅ Tap instance created successfully")

        # Test discovery
        print("🔍 Testing discovery...")
        catalog = tap.discover_streams()

        if catalog:
            print(f"✅ Discovery successful - found {len(catalog)} streams:")
            for stream in catalog:
                print(f"  - {stream.name}: {len(stream.schema.get('properties', {}))} properties")
        else:
            print("❌ Discovery returned empty catalog")
            return

        # Test extraction for allocation
        print("\n📤 Testing extraction for allocation...")
        allocation_stream = None
        for stream in catalog:
            if stream.name == "allocation":
                allocation_stream = stream
                break

        if not allocation_stream:
            print("❌ Allocation stream not found in catalog")
            return

        print("🔄 Extracting records...")
        records = list(allocation_stream.get_records(None))

        print(f"✅ Extracted {len(records)} records")
        if records:
            print("📋 First record sample:")
            print(json.dumps(records[0], indent=2, default=str))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tap_directly()
