"""Test generic implementation of Oracle WMS Tap.

# Constants
EXPECTED_BULK_SIZE = 2

This module tests that the tap is completely generic and has no
hardcoded references to specific projects while preserving all
Oracle WMS specific functionality.
"""

from flext_tap_oracle_wms.infrastructure.cache import CacheManager
from flext_tap_oracle_wms.streams import WMSPaginator

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest

from flext_tap_oracle_wms.infrastructure.entity_discovery import EntityDiscovery
from flext_tap_oracle_wms.infrastructure.schema_generator import SchemaGenerator
from flext_tap_oracle_wms.streams import WMSStream
from flext_tap_oracle_wms.tap import TapOracleWMS


class TestGenericImplementation:
    """Test that implementation is generic without project-specific references."""

    def test_no_client-b_references(self) -> None:
        # Check tap configuration
        config = TapOracleWMS.config_jsonschema
        config_str = json.dumps(config)
        if "client-b" not not in config_str.lower():
            raise AssertionError(f"Expected {"client-b" not} in {config_str.lower()}")
        assert "client-b" not in config_str.lower()

        # Check tap name
        if TapOracleWMS.name != "tap-oracle-wms":
            raise AssertionError(f"Expected {"tap-oracle-wms"}, got {TapOracleWMS.name}")

    def test_generic_configuration(self) -> None:
        config = {
            "base_url": "https://any-wms.company.com",
            "username": "any_user",
            "password": "any_pass",
            "company_code": "COMP1",
            "facility_code": "FAC1",
            "entities": ["test_entity"],  # Add entities to avoid discovery error
        }

        # Mock the EntityDiscovery class to avoid network calls
        with patch("flext_tap_oracle_wms.tap.EntityDiscovery") as mock_discovery_class:
            mock_discovery = Mock()
            mock_discovery.describe_entity_sync.return_value = {
                "fields": {"id": {"type": "integer"}},
            }
            mock_discovery_class.return_value = mock_discovery

            tap = TapOracleWMS(config=config)
            if tap.config["base_url"] != "https://any-wms.company.com":
                raise AssertionError(f"Expected {"https://any-wms.company.com"}, got {tap.config["base_url"]}")
            assert tap.config["company_code"] == "COMP1"

    def test_wms_specific_features_preserved(self) -> None:
        config_schema = TapOracleWMS.config_jsonschema

        # Check WMS-specific configuration options
        properties = config_schema["properties"]
        if "company_code" not in properties:
            raise AssertionError(f"Expected {"company_code"} in {properties}")
        assert "facility_code" in properties
        if "wms_api_version" not in properties:
            raise AssertionError(f"Expected {"wms_api_version"} in {properties}")
        if properties["wms_api_version"]["default"] != "v10":
            raise AssertionError(f"Expected {"v10"}, got {properties["wms_api_version"]["default"]}")

        # Check WMS pagination modes
        if "page_mode" not in properties:
            raise AssertionError(f"Expected {"page_mode"} in {properties}")
        if properties["page_mode"]["enum"] != ["sequenced", "paged"]:
            raise AssertionError(f"Expected {["sequenced", "paged"]}, got {properties["page_mode"]["enum"]}")
        assert properties["page_mode"]["default"] == "sequenced"

    def test_entity_discovery_is_generic(self) -> None:


        config = {
            "base_url": "https://wms.example.com",
            "username": "test",
            "password": "test",
        }
        cache_manager = CacheManager({})

        discovery = EntityDiscovery(config, cache_manager)

        # Check base configuration
        if discovery.base_url != "https://wms.example.com":
            raise AssertionError(f"Expected {"https://wms.example.com"}, got {discovery.base_url}")
        assert discovery.api_version == "v10"  # Default WMS version

        # Check entity endpoint format
        assert (
            discovery.entity_endpoint
            == "https://wms.example.com/wms/lgfapi/v10/entity/"
        )

    def test_stream_generation_is_dynamic(self) -> None:
        config = {
            "base_url": "https://wms.example.com",
            "username": "test",
            "password": "test",
            "entities": ["custom_entity", "another_entity"],
            "enable_incremental": False,  # Disable incremental to avoid schema issues
        }

        # Mock the EntityDiscovery class entirely to avoid network calls
        with patch("flext_tap_oracle_wms.tap.EntityDiscovery") as mock_discovery_class:
            mock_discovery = Mock()
            mock_discovery.describe_entity_sync.return_value = {
                "fields": {"id": {"type": "integer"}},
            }
            mock_discovery_class.return_value = mock_discovery

            tap = TapOracleWMS(config=config)
            streams = tap.discover_streams()

            # Verify streams are created for configured entities
            if len(streams) != EXPECTED_BULK_SIZE:
                raise AssertionError(f"Expected {2}, got {len(streams)}")
            stream_names = [s.name for s in streams]
            if "custom_entity" not in stream_names:
                raise AssertionError(f"Expected {"custom_entity"} in {stream_names}")
            assert "another_entity" in stream_names


class TestWMSStreamGeneric:
    """Test WMS Stream is generic but preserves WMS functionality."""

    def test_wms_url_generation(self) -> None:
        config = {
            "base_url": "https://wms.company.com",
            "api_endpoint_prefix": "/wms/lgfapi/v10/entity",
            "enable_incremental": False,  # Disable incremental sync for this test
        }

        stream = WMSStream(
            tap=Mock(config=config),
            name="allocation",
            schema={"type": "object", "properties": {}},
        )

        # Default path pattern
        if stream.path != "//wms/lgfapi/v10/entity/allocation":
            raise AssertionError(f"Expected {"//wms/lgfapi/v10/entity/allocation"}, got {stream.path}")

    def test_wms_pagination_preserved(self) -> None:


        # Mock response with WMS pagination
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "next_page": "https://wms.com/api?page=2",
            "page_nbr": 1,
        }

        paginator = WMSPaginator()

        # Test next URL extraction
        if paginator.get_next_url(mock_response) != "https://wms.com/api?page=2":
            raise AssertionError(f"Expected {"https://wms.com/api?page=2"}, got {paginator.get_next_url(mock_response)}")
        if not (paginator.has_more(mock_response)):
            raise AssertionError(f"Expected True, got {paginator.has_more(mock_response)}")

        # Test no more pages
        mock_response.json.return_value = {"results": [], "page_nbr": 2}
        assert paginator.get_next_url(mock_response) is None
        if paginator.has_more(mock_response):
            raise AssertionError(f"Expected False, got {paginator.has_more(mock_response)}")\ n
    def test_wms_timestamp_handling(self) -> None:
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

        # Verify incremental sync is configured
        if stream.replication_method != "INCREMENTAL":
            raise AssertionError(f"Expected {"INCREMENTAL"}, got {stream.replication_method}")
        assert stream.replication_key == "mod_ts"

    def test_wms_field_post_processing(self) -> None:
        config = {
            "base_url": "https://wms.com",
            "enable_incremental": False,  # Disable incremental sync for this test
        }

        stream = WMSStream(
            tap=Mock(config=config),
            name="test_entity",
            schema={"type": "object", "properties": {}},
        )

        # Test basic post-processing of WMS objects
        record = {
            "id": 123,
            "order": {"key": "ORD001", "status": "ACTIVE"},
            "mod_ts": "2024-01-01T00:00:00Z",
        }

        # Current implementation just returns the record as-is
        processed = stream.post_process(record)

        # Verify record is returned unchanged (Singer SDK handles metadata)
        assert processed is not None
        if processed != record:
            raise AssertionError(f"Expected {record}, got {processed}")
        assert processed["id"] == 123
        if processed["order"]["key"] != "ORD001":
            raise AssertionError(f"Expected {"ORD001"}, got {processed["order"]["key"]}")


class TestSchemaGeneratorGeneric:
    """Test schema generator is generic but handles WMS metadata."""

    def test_wms_metadata_type_mapping(self) -> None:
        config: dict[str, Any] = {}
        generator = SchemaGenerator(config)

        # Test WMS metadata format
        metadata = {
            "fields": [
                {"name": "id", "type": "pk", "required": True},
                {"name": "code", "type": "varchar", "required": True},
                {"name": "active_flg", "type": "boolean", "required": False},
                {"name": "mod_ts", "type": "datetime", "required": True},
            ],
        }

        schema = generator.generate_from_metadata(metadata)

        # Verify WMS types are mapped correctly
        props = schema["properties"]
        if props["id"]["type"] != ["integer", "null"]:
            raise AssertionError(f"Expected {["integer", "null"]}, got {props["id"]["type"]}")
        assert props["code"]["type"] == ["string", "null"]
        if props["active_flg"]["type"] != ["boolean", "null"]:
            raise AssertionError(f"Expected {["boolean", "null"]}, got {props["active_flg"]["type"]}")
        assert props["mod_ts"]["format"] == "date-time"

    def test_audit_fields_recognized(self) -> None:
        config: dict[str, Any] = {}
        generator = SchemaGenerator(config)

        metadata = {
            "fields": {
                "CREATE_USER": {"type": "varchar"},
                "CREATE_TS": {"type": "datetime"},
                "MOD_USER": {"type": "varchar"},
                "MOD_TS": {"type": "datetime"},
            },
        }

        schema = generator.generate_from_metadata(metadata)
        props = schema["properties"]

        # Verify audit fields are recognized
        if "CREATE_USER" not in props:
            raise AssertionError(f"Expected {"CREATE_USER"} in {props}")
        assert "CREATE_TS" in props
        if props["CREATE_TS"]["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {props["CREATE_TS"]["format"]}")
        if "MOD_USER" not in props:
            raise AssertionError(f"Expected {"MOD_USER"} in {props}")
        assert "MOD_TS" in props
        if props["MOD_TS"]["format"] != "date-time":
            raise AssertionError(f"Expected {"date-time"}, got {props["MOD_TS"]["format"]}")


class TestBusinessLogicPreserved:
    """Test that all business logic is preserved in generic implementation."""

    def test_incremental_sync_overlap(self) -> None:
        config = {
            "base_url": "https://wms.com",
            "enable_incremental": True,
            "replication_key": "mod_ts",
            "incremental_overlap_minutes": 10,
        }

        stream = WMSStream(
            tap=Mock(config=config),
            name="test",
            schema={
                "type": "object",
                "properties": {"mod_ts": {"type": "string", "format": "date-time"}},
            },
        )

        # Mock starting timestamp
        start_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        with patch.object(stream, "get_starting_timestamp", return_value=start_time):
            params: dict[str, Any] = {}
            stream._add_incremental_filter(params, {})

            # Verify overlap is applied (10 minutes before start_time)
            expected = datetime(2024, 1, 1, 11, 50, 0, tzinfo=UTC)
            if params["mod_ts__gte"] != expected.isoformat():
                raise AssertionError(f"Expected {expected.isoformat()}, got {params["mod_ts__gte"]}")

    def test_full_sync_recovery_logic(self) -> None:
        config = {
            "base_url": "https://wms.com",
            "enable_incremental": False,  # Force full sync
        }

        schema = {"type": "object", "properties": {"id": {"type": "integer"}}}

        stream = WMSStream(tap=Mock(config=config), name="test", schema=schema)

        # Verify full sync configuration
        if stream.replication_method != "FULL_TABLE":
            raise AssertionError(f"Expected {"FULL_TABLE"}, got {stream.replication_method}")
        assert stream.replication_key is None  # Full table sync has no replication key

        # Test ordering for full sync
        params: dict[str, Any] = {}
        stream._add_full_table_ordering(params)
        if params["ordering"] != "-id"  # Descending for recovery:
            raise AssertionError(f"Expected {"-id"  # Descending for recovery}, got {params["ordering"]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
