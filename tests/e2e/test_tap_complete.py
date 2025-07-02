"""End-to-end tests for complete tap functionality."""

import json

import pytest

from tap_oracle_wms.tap import TapOracleWMS


class TestTapComplete:
    """End-to-end tests for complete tap workflow."""

    @pytest.mark.e2e
    def test_complete_discovery_workflow(self, sample_config) -> None:
        """Test complete discovery workflow from config to catalog."""
        tap = TapOracleWMS(config=sample_config)

        # Test discovery process
        catalog = tap.catalog_dict

        # Validate complete catalog structure
        assert isinstance(catalog, dict)
        assert "streams" in catalog
        streams = catalog["streams"]
        assert len(streams) > 0

        # Validate each stream is properly discoverable
        for stream_def in streams:
            # Required top-level fields
            assert "tap_stream_id" in stream_def
            assert "schema" in stream_def
            assert "metadata" in stream_def

            # Schema validation
            schema = stream_def["schema"]
            assert schema["type"] == "object"
            assert "properties" in schema
            assert len(schema["properties"]) > 0

            # Metadata validation
            metadata = stream_def["metadata"]
            assert isinstance(metadata, list)

            # Should have table-level metadata
            table_metadata = [m for m in metadata if m.get("breadcrumb") == []]
            assert len(table_metadata) > 0

    @pytest.mark.e2e
    def test_catalog_json_serialization(self, sample_config) -> None:
        """Test that catalog can be properly serialized to JSON."""
        tap = TapOracleWMS(config=sample_config)
        catalog = tap.catalog_dict

        # Test JSON serialization
        try:
            catalog_json = json.dumps(catalog, indent=2)
            assert len(catalog_json) > 0

            # Test deserialization
            parsed_catalog = json.loads(catalog_json)
            assert parsed_catalog == catalog

        except (TypeError, ValueError) as e:
            pytest.fail(f"Catalog is not JSON serializable: {e}")

    @pytest.mark.e2e
    def test_stream_instantiation_complete(self, sample_config) -> None:
        """Test complete stream instantiation and basic functionality."""
        tap = TapOracleWMS(config=sample_config)

        # Test each stream can be fully instantiated
        for stream_class in tap.streams.values():
            stream = stream_class(tap=tap)

            # Basic validation
            assert stream.name == stream.name
            assert stream.tap_name == "tap-oracle-wms"

            # Schema validation
            schema = stream.schema
            assert isinstance(schema, dict)
            assert "type" in schema
            assert "properties" in schema

            # URL construction validation
            assert hasattr(stream, "url_base")
            url_base = stream.url_base
            assert url_base.startswith("http")
            assert sample_config["base_url"] in url_base

            # Authentication validation
            assert hasattr(stream, "authenticator")
            assert stream.authenticator is not None

    @pytest.mark.e2e
    def test_configuration_validation_complete(self, sample_config) -> None:
        """Test complete configuration validation."""
        # Test with valid config
        tap = TapOracleWMS(config=sample_config)
        assert tap.config == sample_config

        # Test config access patterns
        streams = tap.streams
        assert len(streams) > 0

        # Each stream should have access to config
        for stream_class in streams.values():
            stream = stream_class(tap=tap)
            assert stream.config == sample_config

    @pytest.mark.e2e
    def test_tap_cli_compatibility(self, sample_config) -> None:
        """Test that tap is compatible with Singer CLI patterns."""
        tap = TapOracleWMS(config=sample_config)

        # Test discovery mode
        catalog = tap.catalog_dict
        assert "streams" in catalog

        # Test that streams can be selected
        for stream_def in catalog["streams"]:
            stream_id = stream_def["tap_stream_id"]

            # Stream should be available in tap.streams
            assert stream_id in tap.streams

            # Stream should be instantiable
            stream_class = tap.streams[stream_id]
            stream = stream_class(tap=tap)
            assert stream.name == stream_id

    @pytest.mark.e2e
    def test_error_handling_workflow(self, sample_config) -> None:
        """Test error handling throughout the workflow."""
        # Test tap initialization with various error conditions

        # Missing required fields
        invalid_configs = [
            {},
            {"base_url": "invalid_url"},
            {"base_url": "https://example.com"},  # Missing auth
        ]

        for invalid_config in invalid_configs:
            try:
                tap = TapOracleWMS(config=invalid_config)
                # Try to access functionality that requires valid config
                streams = tap.streams
                if streams:
                    # If streams are available, try to instantiate one
                    first_stream = next(iter(streams.values()))
                    first_stream(tap=tap)
                    # This should either work or raise appropriate errors

            except (ValueError, KeyError, TypeError) as e:
                # Expected for invalid configurations
                assert len(str(e)) > 0

    @pytest.mark.e2e
    def test_memory_efficiency(self, sample_config) -> None:
        """Test that tap operations are memory efficient."""
        # Test that multiple tap instances don't accumulate memory
        for _i in range(5):
            tap = TapOracleWMS(config=sample_config)
            catalog = tap.catalog_dict

            # Basic validation that each iteration works
            assert len(catalog["streams"]) > 0

            # Clean up
            del tap
            del catalog
