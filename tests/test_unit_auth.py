"""Unit tests for authentication functionality."""

import pytest
from singer_sdk.authenticators import BasicAuthenticator

from tap_oracle_wms.auth import get_wms_authenticator, get_wms_headers
from tap_oracle_wms.config import BASIC_AUTH_PREFIX_LENGTH


class TestWMSAuthentication:
    """Test WMS authentication methods."""

    def test_get_wms_headers_basic_auth(self, sample_config) -> None:
        """Test WMS headers generation for basic auth."""
        headers = get_wms_headers(sample_config)

        # Validate required headers are present
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"

        # Validate authorization format
        auth_header = headers["Authorization"]
        assert auth_header.startswith("Basic ")
        assert (
            len(auth_header) > BASIC_AUTH_PREFIX_LENGTH
        )  # "Basic " + encoded credentials

    def test_get_wms_authenticator_returns_basic_auth(self, sample_config) -> None:
        """Test that WMS authenticator returns BasicAuthenticator instance."""

        # Create a simple stream instance for testing
        class TestStream:
            def __init__(self, config) -> None:
                self.config = config
                self.logger = None

        stream = TestStream(sample_config)
        authenticator = get_wms_authenticator(stream, sample_config)

        # Validate authenticator type and configuration
        assert isinstance(authenticator, BasicAuthenticator)

    def test_wms_headers_include_required_fields(self, sample_config) -> None:
        """Test that WMS headers include all required fields."""
        headers = get_wms_headers(sample_config)

        required_headers = ["Authorization", "Content-Type", "Accept"]
        for header in required_headers:
            assert header in headers, f"Required header '{header}' missing"

    def test_wms_authenticator_configuration_validation(self, sample_config) -> None:
        """Test that authenticator properly validates configuration."""

        # Test with valid config
        class TestStream:
            def __init__(self, config) -> None:
                self.config = config
                self.logger = None

        stream = TestStream(sample_config)
        authenticator = get_wms_authenticator(stream, sample_config)

        # Authenticator should be properly configured
        assert authenticator is not None
        assert hasattr(authenticator, "username")
        assert hasattr(authenticator, "password")

    def test_wms_headers_encoding(self, sample_config) -> None:
        """Test that WMS headers properly encode credentials."""
        headers = get_wms_headers(sample_config)
        auth_header = headers["Authorization"]

        # Should be properly formatted Basic auth
        assert auth_header.startswith("Basic ")

        # Should contain base64 encoded credentials
        import base64

        encoded_part = auth_header[6:]  # Remove "Basic "
        try:
            decoded = base64.b64decode(encoded_part).decode("utf-8")
            assert ":" in decoded  # Should be username:password format
        except Exception as e:
            pytest.fail(f"Authorization header not properly base64 encoded: {e}")
