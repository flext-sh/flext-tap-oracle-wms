"""Test real Oracle WMS connection and basic operations.

Tests against the actual Oracle WMS environment using real credentials.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from flext_tap_oracle_wms import (
    FlextTapOracleWms,
    FlextTapOracleWmsConfig,
)

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


@pytest.fixture
def real_config() -> FlextTapOracleWmsConfig:
    """Create real configuration from environment."""
    return FlextTapOracleWmsConfig(
        base_url=os.getenv("ORACLE_WMS_BASE_URL"),
        username=os.getenv("ORACLE_WMS_USERNAME"),
        password=os.getenv("ORACLE_WMS_PASSWORD"),
        api_version=os.getenv("ORACLE_WMS_API_VERSION", "v10"),
        timeout=int(os.getenv("ORACLE_WMS_TIMEOUT", "30")),
        page_size=int(os.getenv("ORACLE_WMS_PAGE_SIZE", "100")),
        verify_ssl=os.getenv("ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
        enable_rate_limiting=True,
        max_requests_per_minute=60,
    )


@pytest.fixture
def tap(real_config: FlextTapOracleWmsConfig) -> FlextTapOracleWms:
    """Create tap instance with real configuration."""
    return FlextTapOracleWms(config=real_config)


class TestRealConnection:
    """Test real Oracle WMS connection."""

    def test_configuration_validation(self, tap: FlextTapOracleWms) -> None:
        """Test configuration validation."""
        result = tap.validate_configuration()
        assert result.is_success
        assert result.value["valid"] is True
        assert "health" in result.value

    def test_tap_initialization(self, tap: FlextTapOracleWms) -> None:
        """Test tap initialization."""
        result = tap.initialize()
        assert result.is_success

    def test_catalog_discovery(self, tap: FlextTapOracleWms) -> None:
        """Test catalog discovery."""
        # Initialize first
        init_result = tap.initialize()
        assert init_result.is_success

        # Discover catalog
        result = tap.discover_catalog()
        assert result.is_success

        catalog = result.value
        assert catalog["type"] == "CATALOG"
        assert "streams" in catalog
        assert len(catalog["streams"]) > 0

        for stream in catalog["streams"]:
            stream.get("schema", {}).get("properties", {})

    def test_stream_discovery(self, tap: FlextTapOracleWms) -> None:
        """Test stream discovery."""
        streams = tap.discover_streams()
        assert len(streams) > 0

        for _stream in streams:
            pass

    def test_stream_schemas_validation(self, tap: FlextTapOracleWms) -> None:
        """Test stream schemas."""
        streams = tap.discover_streams()

        for stream in streams:
            assert stream.name
            assert stream.schema is not None

            # Check schema structure
            if "properties" in stream.schema:
                properties = stream.schema["properties"]
                assert len(properties) > 0


class TestRealDataExtraction:
    """Test real data extraction from Oracle WMS."""

    @pytest.mark.parametrize("stream_name", ["inventory", "locations", "items"])
    def test_extract_stream_data(
        self,
        tap: FlextTapOracleWms,
        stream_name: str,
    ) -> None:
        """Test extracting data from specific streams."""
        # Initialize tap
        init_result = tap.initialize()
        assert init_result.is_success

        # Get specific stream
        streams = tap.discover_streams()
        stream = next((s for s in streams if s.name == stream_name), None)

        if stream is None:
            pytest.skip(f"Stream {stream_name} not available")

        # Extract some records
        records = []
        record_count = 0
        max_records = 5  # Limit for testing

        try:
            for record in stream.get_records(context=None):
                records.append(record)
                record_count += 1
                if record_count >= max_records:
                    break

            if records:
                pass
        except Exception as e:
            pytest.fail(f"Failed to extract records from {stream_name}: {e}")

    def test_pagination_functionality(self, tap: FlextTapOracleWms) -> None:
        """Test pagination functionality."""
        # Use a stream with many records
        tap.initialize()
        streams = tap.discover_streams()

        # Try inventory stream
        inventory_stream = next((s for s in streams if s.name == "inventory"), None)
        if not inventory_stream:
            pytest.skip("Inventory stream not available")

        # Set small page size
        inventory_stream._page_size = 2

        # Extract records
        records = []
        pages = 0

        for i, record in enumerate(inventory_stream.get_records(context=None)):
            records.append(record)
            if i > 0 and i % 2 == 0:
                pages += 1
            if i >= 5:  # Limit for testing
                break

        assert len(records) > 2  # Should have multiple pages


class TestFilteringAndSelection:
    """Test entity filtering and selection."""

    def test_entity_inclusion_filter(
        self,
        real_config: FlextTapOracleWmsConfig,
    ) -> None:
        """Test including specific entities."""
        config = FlextTapOracleWmsConfig(
            **real_config.model_dump(),
            include_entities=["inventory", "locations"],
        )
        tap = FlextTapOracleWms(config=config)

        streams = tap.discover_streams()
        stream_names = {s.name for s in streams}

        assert "inventory" in stream_names
        assert "locations" in stream_names
        assert "orders" not in stream_names  # Should be excluded

    def test_entity_exclusion_filter(
        self,
        real_config: FlextTapOracleWmsConfig,
    ) -> None:
        """Test excluding specific entities."""
        config = FlextTapOracleWmsConfig(
            **real_config.model_dump(),
            exclude_entities=["orders", "shipments"],
        )
        tap = FlextTapOracleWms(config=config)

        streams = tap.discover_streams()
        stream_names = {s.name for s in streams}

        assert "orders" not in stream_names
        assert "shipments" not in stream_names
        assert len(stream_names) > 0  # Should have other streams


class TestIntegration:
    """Test /sync integration with flext-oracle-wms."""

    def test_client_lifecycle_management(self, tap: FlextTapOracleWms) -> None:
        """Test proper client lifecycle management."""
        # Initialize should start the client
        init_result = tap.initialize()
        assert init_result.is_success

        # Client should be created
        assert tap._wms_client is not None
        assert tap._is_started is True

        # Discovery should work
        result = tap.discover_catalog()
        assert result.is_success

    def test_error_handling(self) -> None:
        """Test error handling with invalid configuration."""
        bad_config = FlextTapOracleWmsConfig(
            base_url="https://invalid.example.com",
            username="invalid",
            password="invalid",
        )
        tap = FlextTapOracleWms(config=bad_config)

        # Should handle connection errors gracefully
        result = tap.validate_configuration()
        assert result.is_failure


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
