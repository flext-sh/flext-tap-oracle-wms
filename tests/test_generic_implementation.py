"""Test generic implementation of Oracle WMS Tap.

This module tests that the tap is completely generic and has no
hardcoded references to specific projects while preserving all
Oracle WMS specific functionality.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest
from flext_tap_oracle_wms.discovery import EntityDiscovery, SchemaGenerator
from flext_tap_oracle_wms.streams import WMSStream
from flext_tap_oracle_wms.tap import TapOracleWMS


class TestGenericImplementation:
    """Test that implementation is generic without project-specific references."""

    def test_no_client-b_references(self) -> None:
        # Check tap configuration
        config = TapOracleWMS.config_jsonschema
        config_str = json.dumps(config)
        assert "client-b" not in config_str.lower()
        assert "client-b" not in config_str.lower()

        # Check tap name
        assert TapOracleWMS.name == "tap-oracle-wms"

    def test_generic_configuration(self) -> None:
        config = {
            "base_url": "https://any-wms.company.com",
            "username": "any_user",
            "password": "any_pass",
            "company_code": "COMP1",
            "facility_code": "FAC1",
        }

        tap = TapOracleWMS(config=config)
        assert tap.config["base_url"] == "https://any-wms.company.com"
        assert tap.config["company_code"] == "COMP1"

    def test_wms_specific_features_preserved(self) -> None:
        config_schema = TapOracleWMS.config_jsonschema

        # Check WMS-specific configuration options
        properties = config_schema["properties"]
        assert "company_code" in properties
        assert "facility_code" in properties
        assert "wms_api_version" in properties
        assert properties["wms_api_version"]["default"] == "v10"

        # Check WMS pagination modes
        assert "page_mode" in properties
        assert properties["page_mode"]["enum"] == ["sequenced", "paged"]
        assert properties["page_mode"]["default"] == "sequenced"

    def test_entity_discovery_is_generic(self) -> None:
        config = {
            "base_url": "https://wms.example.com",
            "username": "test",
            "password": "test",
        }

        discovery = EntityDiscovery(config)

        # Check base configuration
        assert discovery.base_url == "https://wms.example.com"
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
        }

        tap = TapOracleWMS(config=config)

        # Mock schema generation
        with patch.object(tap, "_generate_schema_async") as mock_gen:
            mock_gen.return_value = {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
            }

            streams = tap.discover_streams()

            # Verify streams are created for configured entities
            assert len(streams) == 2
            stream_names = [s.name for s in streams]
            assert "custom_entity" in stream_names
            assert "another_entity" in stream_names


class TestWMSStreamGeneric:
    """Test WMS Stream is generic but preserves WMS functionality."""

    def test_wms_url_generation(self) -> None:
        config = {
            "base_url": "https://wms.company.com",
            "api_endpoint_prefix": "/wms/lgfapi/v10/entity",
        }

        stream = WMSStream(
            tap=Mock(config=config),
            name="allocation",
            schema={"type": "object", "properties": {}},
        )

        # Default path pattern
        assert stream.path == "/wms/lgfapi/v10/entity/allocation"

    def test_wms_pagination_preserved(self) -> None:
        from flext_tap_oracle_wms.streams import (  # TODO: Move import to module level
            WMSPaginator,
        )

        # Mock response with WMS pagination
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "next_page": "https://wms.com/api?page=2",
            "page_nbr": 1,
        }

        paginator = WMSPaginator()

        # Test next URL extraction
        assert paginator.get_next_url(mock_response) == "https://wms.com/api?page=2"
        assert paginator.has_more(mock_response) is True

        # Test no more pages
        mock_response.json.return_value = {"results": [], "page_nbr": 2}
        assert paginator.get_next_url(mock_response) is None
        assert paginator.has_more(mock_response) is False

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
        assert stream.replication_method == "INCREMENTAL"
        assert stream.replication_key == "mod_ts"

    def test_wms_field_flattening(self) -> None:
        config = {"base_url": "https://wms.com", "flattening_enabled": True}

        stream = WMSStream(
            tap=Mock(config=config),
            name="test_entity",
            schema={"type": "object", "properties": {}},
        )

        # Test flattening of complex WMS objects
        record = {
            "id": 123,
            "order": {"key": "ORD001", "status": "ACTIVE"},
            "mod_ts": "2024-01-01T00:00:00Z",
        }

        with patch("flext_tap_oracle_wms.streams.SchemaGenerator") as mock_gen:
            mock_instance = Mock()
            mock_gen.return_value = mock_instance
            mock_instance.flatten_complex_objects.return_value = {
                "id": 123,
                "order_key": "ORD001",
                "order_status": "ACTIVE",
                "mod_ts": "2024-01-01T00:00:00Z",
            }

            processed = stream.post_process(record)

            # Verify flattening was applied
            mock_instance.flatten_complex_objects.assert_called_once()
            assert "order_key" in processed
            assert processed["order_key"] == "ORD001"


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
        assert props["id"]["type"] == ["integer", "null"]
        assert props["code"]["type"] == ["string", "null"]
        assert props["active_flg"]["type"] == ["boolean", "null"]
        assert props["mod_ts"]["format"] == "date-time"

    def test_audit_fields_recognized(self) -> None:
        config: dict[str, Any] = {}
        generator = SchemaGenerator(config)

        metadata = {
            "fields": [
                {"name": "CREATE_USER", "type": "varchar"},
                {"name": "CREATE_TS", "type": "datetime"},
                {"name": "MOD_USER", "type": "varchar"},
                {"name": "MOD_TS", "type": "datetime"},
            ],
        }

        schema = generator.generate_from_metadata(metadata)
        props = schema["properties"]

        # Verify audit fields are recognized
        assert "CREATE_USER" in props
        assert "CREATE_TS" in props
        assert props["CREATE_TS"]["format"] == "date-time"
        assert "MOD_USER" in props
        assert "MOD_TS" in props
        assert props["MOD_TS"]["format"] == "date-time"


class TestBusinessLogicPreserved:
    """Test that all business logic is preserved in generic implementation."""

    @pytest.mark.asyncio
    async def test_entity_filtering_logic(self) -> None:
        config = {
            "base_url": "https://wms.com",
            "username": "test",
            "password": "test",
            "entity_patterns": {
                "include": ["order_*", "allocation*"],
                "exclude": ["*_temp", "*_backup"],
            },
        }

        discovery = EntityDiscovery(config)

        # Test filtering
        entities = {
            "order_hdr": "url1",
            "order_dtl": "url2",
            "allocation": "url3",
            "order_temp": "url4",
            "test_backup": "url5",
            "other_entity": "url6",
        }

        filtered = discovery.filter_entities(entities)

        # Verify filtering logic
        assert "order_hdr" in filtered
        assert "order_dtl" in filtered
        assert "allocation" in filtered
        assert "order_temp" not in filtered  # Excluded
        assert "test_backup" not in filtered  # Excluded
        assert "other_entity" not in filtered  # Not included

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
            assert params["mod_ts__gte"] == expected.isoformat()

    def test_full_sync_recovery_logic(self) -> None:
        config = {
            "base_url": "https://wms.com",
            "enable_incremental": False,  # Force full sync
        }

        schema = {"type": "object", "properties": {"id": {"type": "integer"}}}

        stream = WMSStream(tap=Mock(config=config), name="test", schema=schema)

        # Verify full sync configuration
        assert stream.replication_method == "FULL_TABLE"
        assert stream.replication_key == "id"

        # Test ordering for full sync
        params: dict[str, Any] = {}
        stream._add_full_table_ordering(params)
        assert params["ordering"] == "-id"  # Descending for recovery


if __name__ == "__main__":
            pytest.main([__file__, "-v"])
