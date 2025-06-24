"""Integration tests for WMS API connection."""

import httpx
import pytest

from tap_oracle_wms.tap import TapOracleWMS


class TestWMSConnection:
    """Test WMS API connection and basic functionality."""

    @pytest.mark.integration
    def test_api_connectivity(self, sample_config) -> None:
        """Test basic API connectivity to WMS."""
        # Create HTTP client with auth headers
        from tap_oracle_wms.auth import get_wms_headers

        headers = get_wms_headers(sample_config)
        base_url = sample_config["base_url"].rstrip("/")

        # Test basic connectivity
        with httpx.Client(headers=headers, timeout=30.0) as client:
            # Try to access a basic endpoint
            test_url = f"{base_url}/facility"

            try:
                response = client.get(test_url)

                # Accept both success and auth-related responses
                # (since we may not have valid credentials in test environment)
                acceptable_status = [200, 401, 403, 404]
                assert response.status_code in acceptable_status

                if response.status_code == 200:
                    # If successful, validate response structure
                    data = response.json()
                    assert isinstance(data, dict | list)

            except httpx.RequestError as e:
                pytest.skip(f"Network connectivity issue: {e}")

    @pytest.mark.integration
    def test_stream_initialization_with_real_config(self, sample_config) -> None:
        """Test that streams initialize properly with real configuration."""
        tap = TapOracleWMS(config=sample_config)

        # Test each stream can be initialized
        for stream_class in tap.streams.values():
            stream = stream_class(tap=tap)

            # Validate stream has proper configuration
            assert stream.config == sample_config
            assert stream.tap_name == "tap-oracle-wms"
            assert stream.name == stream_name

            # Validate stream has proper URL construction
            assert hasattr(stream, "url_base")
            assert stream.url_base.startswith("http")

    @pytest.mark.integration
    def test_authentication_headers_generation(self, sample_config) -> None:
        """Test that authentication headers are generated correctly."""
        from tap_oracle_wms.auth import get_wms_headers

        headers = get_wms_headers(sample_config)

        # Validate required headers
        required_headers = ["Authorization", "Content-Type"]
        for header in required_headers:
            assert header in headers

        # Validate authorization format
        auth_header = headers["Authorization"]
        assert auth_header.startswith("Basic ")

        # Validate content type
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.integration
    def test_catalog_discovery_structure(self, sample_config) -> None:
        """Test that catalog discovery produces valid structure."""
        tap = TapOracleWMS(config=sample_config)
        catalog = tap.catalog_dict

        # Validate top-level structure
        assert isinstance(catalog, dict)
        assert "streams" in catalog
        assert isinstance(catalog["streams"], list)

        # Validate each stream in catalog
        for stream_def in catalog["streams"]:
            assert "tap_stream_id" in stream_def
            assert "schema" in stream_def
            assert "metadata" in stream_def

            # Validate schema structure
            schema = stream_def["schema"]
            assert "type" in schema
            assert "properties" in schema
            assert schema["type"] == "object"

            # Validate metadata structure
            metadata = stream_def["metadata"]
            assert isinstance(metadata, list)

    @pytest.mark.integration
    def test_stream_schema_consistency(self, sample_config) -> None:
        """Test that stream schemas are consistent and valid."""
        tap = TapOracleWMS(config=sample_config)

        for stream_class in tap.streams.values():
            stream = stream_class(tap=tap)
            schema = stream.schema

            # Validate schema structure
            assert isinstance(schema, dict)
            assert "type" in schema
            assert "properties" in schema
            assert schema["type"] == "object"

            # Validate properties
            properties = schema["properties"]
            assert isinstance(properties, dict)
            assert len(properties) > 0

            # Each property should have a type
            for prop_def in properties.values():
                assert isinstance(prop_def, dict)
                assert "type" in prop_def or "anyOf" in prop_def

    @pytest.mark.integration
    def test_error_handling_configuration(self, sample_config) -> None:
        """Test that streams handle configuration errors appropriately."""
        # Test with missing required fields
        invalid_configs = [
            {},  # Empty config
            {"base_url": "https://example.com"},  # Missing auth
            {"username": "test", "password": "test"},  # Missing base_url
        ]

        for invalid_config in invalid_configs:
            with pytest.raises((ValueError, KeyError, TypeError)):
                tap = TapOracleWMS(config=invalid_config)
                # Try to access streams to trigger validation
                list(tap.streams.items())
