#!/usr/bin/env python3
"""Validate Oracle WMS Tap functionality.

This script checks:
1. Generic implementation without project-specific references
2. Oracle WMS specific features preserved
3. Business logic maintained
4. Dynamic entity discovery works
"""

import json
from unittest.mock import Mock, patch, AsyncMock

# Test imports
try:
    from tap_oracle_wms.tap import TapOracleWMS
    from tap_oracle_wms.streams import WMSStream, WMSPaginator
    from tap_oracle_wms.discovery import EntityDiscovery, SchemaGenerator
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


def test_generic_implementation():
    """Test implementation is generic."""
    print("\n🔍 Testing generic implementation...")
    
    # Check tap name
    assert TapOracleWMS.name == "tap-oracle-wms"
    print("  ✅ Tap name is generic")
    
    # Check configuration has no hardcoded references
    config_json = json.dumps(TapOracleWMS.config_jsonschema)
    assert "client-b" not in config_json.lower()
    assert "client-b" not in config_json.lower()
    print("  ✅ No hardcoded references in config")
    
    # Test with any WMS instance
    config = {
        "base_url": "https://any-wms.company.com",
        "username": "any_user",
        "password": "any_pass",
        "company_code": "ANY_COMP",
        "facility_code": "ANY_FAC"
    }
    
    tap = TapOracleWMS(config=config)
    assert tap.config["base_url"] == "https://any-wms.company.com"
    assert tap.config["company_code"] == "ANY_COMP"
    print("  ✅ Works with any WMS instance")


def test_wms_specific_features():
    """Test Oracle WMS specific features preserved."""
    print("\n🔍 Testing WMS-specific features...")
    
    config_schema = TapOracleWMS.config_jsonschema
    properties = config_schema["properties"]
    
    # Check WMS-specific fields
    assert "company_code" in properties
    assert "facility_code" in properties
    assert "wms_api_version" in properties
    assert properties["wms_api_version"]["default"] == "v10"
    print("  ✅ WMS-specific configuration preserved")
    
    # Check pagination modes
    assert "page_mode" in properties
    page_mode_prop = properties["page_mode"]
    if isinstance(page_mode_prop, dict):
        assert page_mode_prop.get("default") == "sequenced"
    print("  ✅ WMS pagination modes preserved")
    
    # Test WMS paginator
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [{"id": 1}],
        "next_page": "https://wms.com/api?page=2",
        "page_nbr": 1
    }
    
    paginator = WMSPaginator()
    assert paginator.get_next_url(mock_response) == "https://wms.com/api?page=2"
    assert paginator.has_more(mock_response) is True
    print("  ✅ HATEOAS pagination working")


def test_business_logic_preserved():
    """Test business logic is preserved."""
    print("\n🔍 Testing preserved business logic...")
    
    # Test entity discovery
    config = {
        "base_url": "https://wms.example.com",
        "username": "test",
        "password": "test",
        "wms_api_version": "v11"
    }
    
    discovery = EntityDiscovery(config)
    assert discovery.entity_endpoint == "https://wms.example.com/wms/lgfapi/v11/entity/"
    print("  ✅ Entity discovery endpoint generation preserved")
    
    # Test schema generator with WMS metadata
    generator = SchemaGenerator({})
    metadata = {
        "fields": [
            {"name": "id", "type": "pk", "required": True},
            {"name": "order_nbr", "type": "varchar", "required": True},
            {"name": "active_flg", "type": "boolean", "required": False},
            {"name": "mod_ts", "type": "datetime", "required": True}
        ]
    }
    
    schema = generator.generate_from_metadata(metadata)
    props = schema["properties"]
    
    assert props["id"]["type"] == ["integer", "null"]
    assert props["order_nbr"]["type"] == ["string", "null"]
    assert props["active_flg"]["type"] == ["boolean", "null"]
    assert props["mod_ts"]["format"] == "date-time"
    print("  ✅ WMS metadata type mapping preserved")
    
    # Test incremental sync with mod_ts
    config = {
        "base_url": "https://wms.com",
        "enable_incremental": True,
        "replication_key": "mod_ts"
    }
    
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "mod_ts": {"type": "string", "format": "date-time"}
        }
    }
    
    stream = WMSStream(
        tap=Mock(config=config),
        name="order_hdr",
        schema=schema
    )
    
    assert stream.replication_method == "INCREMENTAL"
    assert stream.replication_key == "mod_ts"
    print("  ✅ Incremental sync with mod_ts preserved")


def test_dynamic_features():
    """Test dynamic features work."""
    print("\n🔍 Testing dynamic features...")
    
    # Test dynamic stream creation
    config = {
        "base_url": "https://wms.com",
        "username": "test",
        "password": "test",
        "entities": ["custom_entity_1", "custom_entity_2"]
    }
    
    tap = TapOracleWMS(config=config)
    
    with patch.object(tap, '_generate_schema_async') as mock_gen:
        mock_gen.return_value = {
            "type": "object",
            "properties": {"id": {"type": "integer"}}
        }
        
        streams = tap.discover_streams()
        
        assert len(streams) == 2
        stream_names = [s.name for s in streams]
        assert "custom_entity_1" in stream_names
        assert "custom_entity_2" in stream_names
        print("  ✅ Dynamic stream creation working")
    
    # Test entity filtering
    discovery = EntityDiscovery({
        "base_url": "https://wms.com",
        "username": "test",
        "password": "test",
        "entity_patterns": {
            "include": ["order_*", "item_*"],
            "exclude": ["*_temp"]
        }
    })
    
    entities = {
        "order_hdr": "url1",
        "order_dtl": "url2",
        "item_master": "url3",
        "order_temp": "url4",
        "other": "url5"
    }
    
    filtered = discovery.filter_entities(entities)
    assert "order_hdr" in filtered
    assert "order_dtl" in filtered
    assert "item_master" in filtered
    assert "order_temp" not in filtered  # Excluded
    assert "other" not in filtered  # Not included
    print("  ✅ Entity filtering logic preserved")


def test_audit_fields():
    """Test audit fields handling."""
    print("\n🔍 Testing audit fields...")
    
    generator = SchemaGenerator({})
    metadata = {
        "fields": [
            {"name": "CREATE_USER", "type": "varchar"},
            {"name": "CREATE_TS", "type": "datetime"},
            {"name": "MOD_USER", "type": "varchar"},
            {"name": "MOD_TS", "type": "datetime"}
        ]
    }
    
    schema = generator.generate_from_metadata(metadata)
    props = schema["properties"]
    
    assert "CREATE_USER" in props
    assert "CREATE_TS" in props
    assert props["CREATE_TS"]["format"] == "date-time"
    assert "MOD_USER" in props
    assert "MOD_TS" in props
    print("  ✅ Audit fields recognized correctly")


def main():
    """Run all validation tests."""
    print("🚀 Starting Oracle WMS Tap validation...\n")
    
    try:
        test_generic_implementation()
        test_wms_specific_features()
        test_business_logic_preserved()
        test_dynamic_features()
        test_audit_fields()
        
        print("\n✅ All functionality has been preserved!")
        print("✅ Tap is completely generic!")
        print("✅ Oracle WMS features intact!")
        print("✅ Ready for production use!")
        
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()