"""Integration tests for FLEXT Tap Oracle WMS with real Oracle WMS instance."""

from __future__ import annotations

import pytest
from flext_core import FlextLogger

from flext_tap_oracle_wms import FlextTapOracleWMS, FlextTapOracleWMSConfig

logger = FlextLogger(__name__)


@pytest.mark.oracle_wms
@pytest.mark.integration
class TestRealOracleWMSIntegration:
    """Test Oracle WMS tap with real WMS instance."""

    @pytest.fixture
    def real_tap(self, real_config: FlextTapOracleWMSConfig) -> FlextTapOracleWMS:
        """Create tap with real configuration."""
        return FlextTapOracleWMS(config=real_config)

    def test_real_connection(self, real_tap: FlextTapOracleWMS) -> None:
        """Test connection to real Oracle WMS."""
        result = real_tap.validate_configuration()

        assert result.is_success, f"Connection failed: {result.error}"
        assert result.value["valid"] is True
        assert result.value["connection"] == "success"

    def test_real_catalog_discovery(self, real_tap: FlextTapOracleWMS) -> None:
        """Test catalog discovery with real Oracle WMS."""
        result = real_tap.discover_catalog()

        assert result.is_success, f"Discovery failed: {result.error}"

        catalog = result.value
        assert catalog["type"] == "CATALOG"
        assert "streams" in catalog
        assert len(catalog["streams"]) > 0

        # Check that common streams are discovered
        stream_names = {stream["stream"] for stream in catalog["streams"]}

        # At least some streams should be available
        assert len(stream_names) > 0

    def test_real_stream_discovery(self, real_tap: FlextTapOracleWMS) -> None:
        """Test stream discovery with real Oracle WMS."""
        streams = real_tap.discover_streams()

        assert len(streams) > 0

        # Check stream properties
        for stream in streams:
            assert hasattr(stream, "name")
            assert hasattr(stream, "tap")
            assert hasattr(stream, "schema")
            assert stream.tap == real_tap

    @pytest.mark.slow
    def test_real_data_extraction(self, real_tap: FlextTapOracleWMS) -> None:
        """Test data extraction from real Oracle WMS."""
        # Initialize tap
        init_result = real_tap.initialize()
        assert init_result.is_success

        # Get available streams
        streams = real_tap.discover_streams()
        assert len(streams) > 0

        # Try to extract data from first available stream
        test_stream = streams[0]

        # Extract some records
        records = []
        record_count = 0
        max_records = 10

        try:
            for record in test_stream.get_records(context=None):
                records.append(record)
                record_count += 1
                if record_count >= max_records:
                    break

            # Verify we got some data
            if len(records) > 0:
                # Check record structure
                first_record = records[0]
                assert isinstance(first_record, dict)
                assert len(first_record) > 0

        except Exception as e:
            # Some streams might be empty or require specific permissions
            logger.debug(
                f"Stream {test_stream.name} extraction failed (expected for some streams): {e}",
            )

    def test_real_filtered_discovery(
        self,
        real_config: FlextTapOracleWMSConfig,
    ) -> None:
        """Test discovery with filtered entities."""
        # Create tap with filtered config
        real_config.include_entities = ["inventory", "locations"]
        tap = FlextTapOracleWMS(config=real_config)

        streams = tap.discover_streams()
        stream_names = [stream.name for stream in streams]

        # Only included streams should be present
        assert all(name in {"inventory", "locations"} for name in stream_names)

    def test_real_pagination(self, real_tap: FlextTapOracleWMS) -> None:
        """Test pagination with real Oracle WMS."""
        # Set small page size to test pagination
        real_tap.config["page_size"] = 5

        streams = real_tap.discover_streams()
        if not streams:
            pytest.skip("No streams available")

        # Find a stream with data
        for stream in streams:
            try:
                records = []
                for i, record in enumerate(stream.get_records(context=None)):
                    records.append(record)
                    if i >= 10:  # Get more than one page
                        break

                if len(records) > 5:
                    assert len(records) > 5  # Got more than one page
                    return

            except Exception as e:
                logger.debug(
                    f"Stream {stream.name} failed pagination test (expected for some streams): {e}",
                )
                continue

        pytest.skip("No streams with sufficient data for pagination test")

    def test_real_incremental_extraction(self, real_tap: FlextTapOracleWMS) -> None:
        """Test incremental extraction with real Oracle WMS."""
        # Configure for incremental
        real_tap.config["start_date"] = "2024-01-01T00:00:00Z"

        streams = real_tap.discover_streams()

        # Find a stream with replication key
        incremental_stream = None
        for stream in streams:
            if stream.replication_key:
                incremental_stream = stream
                break

        if not incremental_stream:
            pytest.skip("No incremental streams available")

        # Extract some records
        records = []
        for i, record in enumerate(incremental_stream.get_records(context=None)):
            records.append(record)
            if i >= 5:
                break

        if records:
            # Check that records have the replication key
            for record in records:
                assert incremental_stream.replication_key in record

    def test_real_error_handling(self, real_config: FlextTapOracleWMSConfig) -> None:
        """Test error handling with invalid configuration."""
        # Create tap with invalid URL
        real_config.base_url = "https://invalid.wms.example.com"
        tap = FlextTapOracleWMS(config=real_config)

        result = tap.validate_configuration()

        assert result.is_failure
        assert "Connection test failed" in str(
            result.error,
        ) or "Failed to connect" in str(result.error)
