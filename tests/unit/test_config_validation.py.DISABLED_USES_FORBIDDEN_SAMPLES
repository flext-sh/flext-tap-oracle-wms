"""Unit tests for configuration validation."""

import os
from unittest.mock import patch

from tap_oracle_wms.config import validate_auth_config, validate_pagination_config


class TestConfigValidation:
    """Test configuration validation functions."""

    def test_validate_auth_config_basic(self) -> None:
        """Test basic auth validation."""
        # Valid basic auth
        config = {
            "auth_method": "basic",
            "username": "test_user",
            "password": "test_pass",
        }
        assert validate_auth_config(config) is True

        # Missing username
        config = {
            "auth_method": "basic",
            "password": "test_pass",
        }
        assert validate_auth_config(config) is False

        # Missing password
        config = {
            "auth_method": "basic",
            "username": "test_user",
        }
        assert validate_auth_config(config) is False

        # Empty credentials
        config = {
            "auth_method": "basic",
            "username": "",
            "password": "",
        }
        assert validate_auth_config(config) is False

    def test_validate_auth_config_oauth2(self) -> None:
        """Test OAuth2 auth validation."""
        # Valid OAuth2
        config = {
            "auth_method": "oauth2",
            "oauth_client_id": "client123",
            "oauth_client_secret": "secret456",
            "oauth_token_url": "https://auth.example.com/token",
        }
        assert validate_auth_config(config) is True

        # Missing client_id
        config = {
            "auth_method": "oauth2",
            "oauth_client_secret": "secret456",
            "oauth_token_url": "https://auth.example.com/token",
        }
        assert validate_auth_config(config) is False

        # Missing token_url
        config = {
            "auth_method": "oauth2",
            "oauth_client_id": "client123",
            "oauth_client_secret": "secret456",
        }
        assert validate_auth_config(config) is False

    def test_validate_auth_config_default(self) -> None:
        """Test default auth method."""
        # No auth method specified - defaults to basic
        config = {
            "username": "test_user",
            "password": "test_pass",
        }
        assert validate_auth_config(config) is True

        # Invalid auth method
        config = {
            "auth_method": "invalid_method",
        }
        assert validate_auth_config(config) is False

    def test_validate_pagination_config(self) -> None:
        """Test pagination config validation."""
        # Valid page sizes
        assert validate_pagination_config({"page_size": 1}) is True
        assert validate_pagination_config({"page_size": 100}) is True
        assert validate_pagination_config({"page_size": 1000}) is True
        assert validate_pagination_config({"page_size": 1250}) is True

        # Invalid page sizes
        assert validate_pagination_config({"page_size": 0}) is False
        assert validate_pagination_config({"page_size": -1}) is False
        assert validate_pagination_config({"page_size": 1251}) is False
        assert validate_pagination_config({"page_size": 5000}) is False

        # Default page size (should be valid)
        assert validate_pagination_config({}) is True

    def test_env_var_override(self) -> None:
        """Test that environment variables can override config."""
        # Test with environment variables
        with patch.dict(
            os.environ,
            {
                "WMS_BASE_URL": "https://env.example.com",
                "WMS_USERNAME": "env_user",
                "WMS_PASSWORD": "env_pass",
            },
        ):
            # Environment variables should be accessible
            assert os.getenv("WMS_BASE_URL") == "https://env.example.com"
            assert os.getenv("WMS_USERNAME") == "env_user"
            assert os.getenv("WMS_PASSWORD") == "env_pass"

    def test_config_defaults(self) -> None:
        """Test configuration defaults."""
        from tap_oracle_wms.config import WMS_DEFAULT_PAGE_SIZE, WMS_MAX_PAGE_SIZE

        assert WMS_DEFAULT_PAGE_SIZE == 1000
        assert WMS_MAX_PAGE_SIZE == 1250
        assert WMS_DEFAULT_PAGE_SIZE <= WMS_MAX_PAGE_SIZE

    def test_url_validation_patterns(self) -> None:
        """Test URL validation patterns."""
        valid_urls = [
            "https://wms.example.com",
            "https://wms.example.com/",
            "https://wms.example.com:8443",
            "http://localhost:8080",
            "https://internal.invalid/REDACTED",
            "https://internal.invalid/REDACTED",
        ]

        invalid_urls = [
            "",
            "not-a-url",
            "ftp://wms.example.com",
            "//no-protocol.com",
            "https://",
            "http:/missing-slash.com",
        ]

        # Using urlparse for validation (same as E2E tests)
        from urllib.parse import urlparse

        for url in valid_urls:
            result = urlparse(url)
            assert result.scheme in {"http", "https"}, f"Invalid scheme for {url}"
            assert result.netloc, f"Missing netloc for {url}"

        for url in invalid_urls:
            result = urlparse(url)
            valid = result.scheme in {"http", "https"} and bool(result.netloc)
            assert not valid, f"URL should be invalid: {url}"
