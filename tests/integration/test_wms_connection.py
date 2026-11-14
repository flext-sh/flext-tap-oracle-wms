"""Test real Oracle WMS connection and basic operations.

Tests against the actual Oracle WMS environment using real credentials.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_oracle_wms import FlextTapOracleWms, FlextTapOracleWmsSettings
from tests import TestsFlextTapOracleWmsHelpers, c, tm, u

_PAGE_SAMPLE_LIMIT = 5
_MIN_SAMPLE_RECORDS = 2


class TestsFlextTapOracleWmsWmsConnection(TestsFlextTapOracleWmsHelpers):
    """Test real Oracle WMS connection."""

    @staticmethod
    def test_configuration_validation(
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Validation exposes exactly the non-secret configured fields."""
        result = real_tap_instance.validate_configuration()
        tm.ok(result)
        value = tm.instance(result.value, dict)
        tm.that(set(value), eq={"base_url", "api_version", "page_size"})
        tm.that(value["base_url"], is_=str)
        tm.that(value["api_version"], is_=str)
        tm.that(value["page_size"], is_=int)
        tm.ok("password" not in value and "username" not in value)

    @staticmethod
    def test_catalog_discovery(real_tap_instance: FlextTapOracleWms) -> None:
        """Discovered catalog entries are named Singer streams."""
        result = real_tap_instance.discovercatalog_typed()
        tm.ok(result)
        catalog = result.value
        tm.that(getattr(catalog, "type", None), eq="CATALOG")
        catalog_streams = getattr(catalog, "streams", [])
        tm.that(catalog_streams, truth=True)
        for stream in catalog_streams:
            tm.that(stream.tap_stream_id, is_=str)
            tm.that(stream.tap_stream_id, truth=True)

    @staticmethod
    def test_stream_discovery(real_tap_instance: FlextTapOracleWms) -> None:
        """Discovered streams expose non-empty names."""
        streams = real_tap_instance.discover_streams()
        tm.that(streams, truth=True)
        for stream in streams:
            tm.that(stream.name, is_=str)
            tm.that(stream.name, truth=True)

    @staticmethod
    def test_stream_schemas_validation(
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test stream schemas."""
        streams = real_tap_instance.discover_streams()
        for stream in streams:
            tm.that(stream.name, truth=True)
            stream_schema = stream.schema
            if "properties" in stream_schema:
                properties = stream_schema["properties"]
                tm.that(properties, truth=True)

    """Test real data extraction from Oracle WMS."""

    @c.Tests.MARK.parametrize("stream_name", ["inventory", "locations", "items"])
    def test_extract_stream_data(
        self,
        real_tap_instance: FlextTapOracleWms,
        stream_name: str,
    ) -> None:
        """Test extracting data from specific streams."""
        tm.ok(real_tap_instance.initialize())
        stream = self._named_stream(real_tap_instance, stream_name)
        self._sample_records(stream, _PAGE_SAMPLE_LIMIT + 1)

    def test_pagination_functionality(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test pagination functionality."""
        inventory_stream = self._named_stream(real_tap_instance, "inventory")
        inventory_stream.page_size = 2
        records = self._sample_records(inventory_stream, _PAGE_SAMPLE_LIMIT + 1)
        tm.that(len(records), gt=_MIN_SAMPLE_RECORDS)

    """Test entity filtering and selection."""

    @staticmethod
    def test_entity_inclusion_filter(
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test including specific entities."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                **real_config.TapOracleWms.model_dump(),
                "include_entities": ["inventory", "locations"],
            },
        })
        real_tap_instance = FlextTapOracleWms.from_settings(settings)
        streams = real_tap_instance.discover_streams()
        stream_names = {s.name for s in streams}
        tm.that(stream_names, has="inventory")
        tm.that(stream_names, has="locations")
        tm.that(stream_names, lacks="orders")

    @staticmethod
    def test_entity_exclusion_filter(
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test excluding specific entities."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                **real_config.TapOracleWms.model_dump(),
                "exclude_entities": ["orders", "shipments"],
            },
        })
        real_tap_instance = FlextTapOracleWms.from_settings(settings)
        streams = real_tap_instance.discover_streams()
        stream_names = {s.name for s in streams}
        tm.that(stream_names, lacks="orders")
        tm.that(stream_names, lacks="shipments")
        tm.that(stream_names, truth=True)

    """Test /sync integration with flext-oracle-wms."""

    @staticmethod
    def test_client_lifecycle_management(
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test proper client lifecycle management."""
        tm.ok(real_tap_instance.initialize())
        first_client = real_tap_instance.wms_client
        tm.that(first_client, none=False)
        tm.that(real_tap_instance.wms_client is first_client)
        result = real_tap_instance.discovercatalog_typed()
        tm.ok(result)


if __name__ == "__main__":
    u.Tests.main([__file__, "-v", "-s"])
