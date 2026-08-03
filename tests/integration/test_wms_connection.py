"""Test real Oracle WMS connection and basic operations.

Tests against the actual Oracle WMS environment using real credentials.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from flext_tests import tm

if TYPE_CHECKING:
    from tests import t


_PAGE_SAMPLE_LIMIT = 5
_MIN_SAMPLE_RECORDS = 2


class TestsFlextTapOracleWmsWmsConnection:
    """Test real Oracle WMS connection."""

    def test_configuration_validation(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test configuration validation."""
        result = real_tap_instance.validate_configuration()
        tm.ok(result)
        value = result.value
        assert isinstance(value, dict)
        tm.that(value.get("valid"), eq=True)
        tm.that(value, has="health")

    def test_tap_initialization(self, real_tap_instance: FlextTapOracleWms) -> None:
        """Test tap initialization."""
        # assert result.is_success

    def test_catalog_discovery(self, real_tap_instance: FlextTapOracleWms) -> None:
        """Test catalog discovery."""
        # assert init_result.is_success
        result = real_tap_instance.discovercatalog_typed()
        tm.ok(result)
        catalog = result.value
        tm.that(getattr(catalog, "type", None), eq="CATALOG")
        catalog_streams = getattr(catalog, "streams", [])
        assert catalog_streams
        for _stream in catalog_streams:
            pass

    def test_stream_discovery(self, real_tap_instance: FlextTapOracleWms) -> None:
        """Test stream discovery."""
        streams = real_tap_instance.discover_streams()
        assert streams
        for _stream in streams:
            pass

    def test_stream_schemas_validation(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test stream schemas."""
        streams = real_tap_instance.discover_streams()
        for stream in streams:
            assert stream.name
            stream_schema = stream.schema
            if "properties" in stream_schema:
                properties = stream_schema["properties"]
                assert properties

    """Test real data extraction from Oracle WMS."""

    @pytest.mark.parametrize("stream_name", ["inventory", "locations", "items"])
    def test_extract_stream_data(
        self, real_tap_instance: FlextTapOracleWms, stream_name: str
    ) -> None:
        """Test extracting data from specific streams."""
        tm.ok(real_tap_instance.initialize())
        streams = real_tap_instance.discover_streams()
        stream = next((s for s in streams if s.name == stream_name), None)
        if stream is None:
            pytest.skip(f"Stream {stream_name} not available")
        records: list[t.JsonMapping] = []
        record_count = 0
        max_records = 5
        try:
            for record in stream.get_records(context=None):
                records.append(record)
                record_count += 1
                if record_count >= max_records:
                    break
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ) as e:
            pytest.fail(f"Failed to extract records from {stream_name}: {e}")

    def test_pagination_functionality(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test pagination functionality."""
        streams = real_tap_instance.discover_streams()
        inventory_stream = next((s for s in streams if s.name == "inventory"), None)
        if not inventory_stream:
            pytest.skip("Inventory stream not available")
        inventory_stream.page_size = 2
        records: list[t.JsonMapping] = []
        pages = 0
        for i, record in enumerate(inventory_stream.get_records(context=None)):
            records.append(record)
            if i > 0 and i % 2 == 0:
                pages += 1
            if i >= _PAGE_SAMPLE_LIMIT:
                break
        assert len(records) > _MIN_SAMPLE_RECORDS

    """Test entity filtering and selection."""

    def test_entity_inclusion_filter(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Test including specific entities."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                **real_config.TapOracleWms.model_dump(),
                "include_entities": ["inventory", "locations"],
            }
        })
        real_tap_instance = FlextTapOracleWms.from_settings(settings)
        streams = real_tap_instance.discover_streams()
        stream_names = {s.name for s in streams}
        tm.that(stream_names, has="inventory")
        tm.that(stream_names, has="locations")
        tm.that(stream_names, lacks="orders")

    def test_entity_exclusion_filter(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Test excluding specific entities."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                **real_config.TapOracleWms.model_dump(),
                "exclude_entities": ["orders", "shipments"],
            }
        })
        real_tap_instance = FlextTapOracleWms.from_settings(settings)
        streams = real_tap_instance.discover_streams()
        stream_names = {s.name for s in streams}
        tm.that(stream_names, lacks="orders")
        tm.that(stream_names, lacks="shipments")
        assert stream_names

    """Test /sync integration with flext-oracle-wms."""

    def test_client_lifecycle_management(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test proper client lifecycle management."""
        tm.ok(real_tap_instance.initialize())
        first_client = real_tap_instance.wms_client
        tm.that(first_client, none=False)
        assert real_tap_instance.wms_client is first_client
        result = real_tap_instance.discovercatalog_typed()
        tm.ok(result)

    def test_error_handling(self) -> None:
        """Test error handling with invalid configuration."""
        bad_settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://invalid.example.com",
                "username": "invalid",
                "password": "invalid",
            }
        })
        tap = FlextTapOracleWms.from_settings(bad_settings)
        result = tap.validate_configuration()
        tm.fail(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
