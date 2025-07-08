#!/usr/bin/env python3
"""Validate Oracle WMS Tap functionality.

This script checks:
1. Generic implementation without project-specific references
2. Oracle WMS specific features preserved
3. Business logic maintained
4. Dynamic entity discovery works
"""

from __future__ import annotations

import json
import sys
from unittest.mock import Mock, patch

# Test imports
try:
    from tap_oracle_wms.discovery import EntityDiscovery, SchemaGenerator
    from tap_oracle_wms.streams import WMSPaginator, WMSStream
    from tap_oracle_wms.tap import TapOracleWMS

except ImportError:
    sys.exit(1)


def test_generic_implementation() -> None:
    """Test implementation is generic."""
    # Check tap name
    assert TapOracleWMS.name == "tap-oracle-wms"

    # Check configuration has no hardcoded references
    config_json = json.dumps(TapOracleWMS.config_jsonschema)
    assert "client-b" not in config_json.lower()
    assert "client-b" not in config_json.lower()

    # Test with any WMS instance
    config = {
        "base_url": "https://any-wms.company.com",
        "username": "any_user",
        "password": "any_pass",
        "company_code": "ANY_COMP",
        "facility_code": "ANY_FAC",
    }

    tap = TapOracleWMS(config=config)
    assert tap.config["base_url"] == "https://any-wms.company.com"
    assert tap.config["company_code"] == "ANY_COMP"


def test_wms_specific_features() -> None:
    """Test Oracle WMS specific features preserved."""
    config_schema = TapOracleWMS.config_jsonschema
    properties = config_schema["properties"]

    # Check WMS-specific fields
    assert "company_code" in properties
    assert "facility_code" in properties
    assert "wms_api_version" in properties
    assert properties["wms_api_version"]["default"] == "v10"

    # Check pagination modes
    assert "page_mode" in properties
    page_mode_prop = properties["page_mode"]
    if isinstance(page_mode_prop, dict):
        assert page_mode_prop.get("default") == "sequenced"

    # Test WMS paginator
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [{"id": 1}],
        "next_page": "https://wms.com/api?page=2",
        "page_nbr": 1,
    }

    paginator = WMSPaginator()
    assert paginator.get_next_url(mock_response) == "https://wms.com/api?page=2"
    assert paginator.has_more(mock_response) is True


def test_business_logic_preserved() -> None:
    """Test business logic is preserved."""
    # Test entity discovery
    config = {
        "base_url": "https://wms.example.com",
        "username": "test",
        "password": "test",
        "wms_api_version": "v11",
    }

    discovery = EntityDiscovery(config)
    assert discovery.entity_endpoint == "https://wms.example.com/wms/lgfapi/v11/entity/"

    # Test schema generator with WMS metadata
    generator = SchemaGenerator({})
    metadata = {
        "fields": {
            "id": {"type": "pk", "required": True},
            "order_nbr": {"type": "varchar", "required": True},
            "active_flg": {"type": "boolean", "required": False},
            "mod_ts": {"type": "datetime", "required": True},
        }
    }

    schema = generator.generate_from_metadata(metadata)
    props = schema["properties"]

    assert props["id"]["type"] == ["integer", "null"]
    assert props["order_nbr"]["type"] == ["string", "null"]
    assert props["active_flg"]["type"] == ["boolean", "null"]
    assert props["mod_ts"]["format"] == "date-time"

    # Test incremental sync with mod_ts
    config = {
        "base_url": "https://wms.com",
        "enable_incremental": True,
        "replication_key": "mod_ts",
    }

    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "mod_ts": {"type": "string", "format": "date-time"},
        },
    }

    stream = WMSStream(tap=Mock(config=config), name="order_hdr", schema=schema)

    assert stream.replication_method == "INCREMENTAL"
    assert stream.replication_key == "mod_ts"


def test_dynamic_features() -> None:
    """Test dynamic features work."""
    # Test dynamic stream creation
    config = {
        "base_url": "https://wms.com",
        "username": "test",
        "password": "test",
        "entities": ["custom_entity_1", "custom_entity_2"],
    }

    tap = TapOracleWMS(config=config)

    with patch.object(tap, "_generate_schema_async") as mock_gen:
        mock_gen.return_value = {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
        }

        streams = tap.discover_streams()

        assert len(streams) == 2
        stream_names = [s.name for s in streams]
        assert "custom_entity_1" in stream_names
        assert "custom_entity_2" in stream_names

    # Test entity filtering
    discovery = EntityDiscovery(
        {
            "base_url": "https://wms.com",
            "username": "test",
            "password": "test",
            "entity_patterns": {
                "include": ["order_*", "item_*"],
                "exclude": ["*_temp"],
            },
        }
    )

    entities = {
        "order_hdr": "url1",
        "order_dtl": "url2",
        "item_master": "url3",
        "order_temp": "url4",
        "other": "url5",
    }

    filtered = discovery.filter_entities(entities)
    assert "order_hdr" in filtered
    assert "order_dtl" in filtered
    assert "item_master" in filtered
    assert "order_temp" not in filtered  # Excluded
    assert "other" not in filtered  # Not included


def test_audit_fields() -> None:
    """Test audit fields handling."""
    generator = SchemaGenerator({})
    metadata = {
        "fields": {
            "CREATE_USER": {"type": "varchar"},
            "CREATE_TS": {"type": "datetime"},
            "MOD_USER": {"type": "varchar"},
            "MOD_TS": {"type": "datetime"},
        }
    }

    schema = generator.generate_from_metadata(metadata)
    props = schema["properties"]

    assert "CREATE_USER" in props
    assert "CREATE_TS" in props
    assert props["CREATE_TS"]["format"] == "date-time"
    assert "MOD_USER" in props
    assert "MOD_TS" in props


def main() -> None:
    """Run all validation tests."""
    try:
        test_generic_implementation()
        test_wms_specific_features()
        test_business_logic_preserved()
        test_dynamic_features()
        test_audit_fields()

    except AssertionError:
        sys.exit(1)
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
