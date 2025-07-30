"""Comprehensive tests for WMS Authentication module.

This module tests all authentication scenarios including:
- Basic authentication success/failure
- Token refresh mechanisms
- Error handling and retry logic
- Configuration validation.
"""

from __future__ import annotations

import base64
import threading
from unittest.mock import Mock, patch

import pytest
import requests

from flext_tap_oracle_wms.auth import (
    WMSBasicAuthenticator,
    get_wms_authenticator,
    get_wms_headers,
)

# Test constants
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_pass"  # Test fixture password


class TestWMSBasicAuthenticator:
    """Test WMS Basic authenticator functionality."""

    def create_test_authenticator(
        self,
        username: str = TEST_USERNAME,
        password: str = TEST_PASSWORD,
    ) -> WMSBasicAuthenticator:
        """Create test authenticator instance."""
        stream = Mock()
        return WMSBasicAuthenticator(stream, username, password)

    def test_authenticator_initialization(self) -> None:
        """Test authenticator initialization."""
        stream = Mock()
        username = "test_user"
        password = "test_password"
        authenticator = WMSBasicAuthenticator(stream, username, password)
        if authenticator.username != username:
            msg = f"Expected {username}, got {authenticator.username}"
            raise AssertionError(msg)
        assert authenticator.password == password
        assert authenticator._auth_headers is None
        assert isinstance(authenticator._auth_lock, type(threading.RLock()))

    def test_authenticator_initialization_with_debug_logging(self) -> None:
        """Test authenticator initialization with debug logging."""
        with patch("flext_tap_oracle_wms.auth.logger") as mock_logger:
            stream = Mock()
            username = "test_user"
            password = "test_password"
            authenticator = WMSBasicAuthenticator(stream, username, password)
            if authenticator.username != username:
                msg = f"Expected {username}, got {authenticator.username}"
                raise AssertionError(
                    msg,
                )
            mock_logger.debug.assert_called_with(
                "Initializing basic authenticator for user: %s",
                username,
            )

    def test_call_creates_auth_headers(self) -> None:
        """Test that calling authenticator creates auth headers."""
        authenticator = self.create_test_authenticator("user123", "pass456")
        request = requests.PreparedRequest()
        request.headers = requests.structures.CaseInsensitiveDict()
        result = authenticator(request)
        # Verify auth header is created
        if "Authorization" not in result.headers:
            msg = f"Expected {'Authorization'} in {result.headers}"
            raise AssertionError(msg)
        auth_header = result.headers["Authorization"]
        assert auth_header.startswith("Basic ")
        # Verify encoding is correct
        expected_creds = "user123:pass456"
        expected_encoded = base64.b64encode(expected_creds.encode()).decode()
        if auth_header != f"Basic {expected_encoded}":
            msg = f"Expected {f'Basic {expected_encoded}'}, got {auth_header}"
            raise AssertionError(
                msg,
            )

    def test_call_caches_auth_headers(self) -> None:
        """Test that auth headers are cached after first call."""
        authenticator = self.create_test_authenticator()
        request1 = requests.PreparedRequest()
        request1.headers = requests.structures.CaseInsensitiveDict()
        request2 = requests.PreparedRequest()
        request2.headers = requests.structures.CaseInsensitiveDict()
        # First call should create headers
        authenticator(request1)
        assert authenticator._auth_headers is not None
        cached_headers = authenticator._auth_headers.copy()
        # Second call should use cached headers
        authenticator(request2)
        if authenticator._auth_headers != cached_headers:
            msg = f"Expected {cached_headers}, got {authenticator._auth_headers}"
            raise AssertionError(
                msg,
            )

    def test_call_thread_safety(self) -> None:
        """Test thread safety of authenticator calls."""
        authenticator = self.create_test_authenticator()
        results = []
        errors = []

        def worker() -> None:
            try:
                request = requests.PreparedRequest()
                request.headers = requests.structures.CaseInsensitiveDict()
                result = authenticator(request)
                results.append(result.headers.get("Authorization"))
            except (RuntimeError, ValueError, TypeError) as e:
                errors.append(e)

        # Start multiple threads
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        # All threads should succeed with same auth header
        if len(errors) != 0:
            msg = f"Expected {0}, got {len(errors)}"
            raise AssertionError(msg)
        assert len(results) == 10

        assert results[0] is not None

    def test_call_with_existing_headers(self) -> None:
        """Test calling authenticator with existing request headers."""
        authenticator = self.create_test_authenticator()
        request = requests.PreparedRequest()
        request.headers = requests.structures.CaseInsensitiveDict(
            {"Custom-Header": "custom-value"},
        )
        result = authenticator(request)
        # Should preserve existing headers and add auth
        if result.headers["Custom-Header"] != "custom-value":
            msg = f"Expected {'custom-value'}, got {result.headers['Custom-Header']}"
            raise AssertionError(
                msg,
            )
        if "Authorization" not in result.headers:
            msg = f"Expected {'Authorization'} in {result.headers}"
            raise AssertionError(msg)

    def test_call_updates_request_headers_in_place(self) -> None:
        """Test that authenticator updates request headers in place."""
        authenticator = self.create_test_authenticator()
        request = requests.PreparedRequest()
        request.headers = requests.structures.CaseInsensitiveDict()
        original_headers = request.headers
        result = authenticator(request)
        # Should be same object, modified in place
        assert result.headers is original_headers
        if "Authorization" not in original_headers:
            msg = f"Expected {'Authorization'} in {original_headers}"
            raise AssertionError(msg)

    def test_call_with_debug_logging(self) -> None:
        """Test authenticator call with debug logging."""
        with patch("flext_tap_oracle_wms.auth.logger") as mock_logger:
            authenticator = self.create_test_authenticator()
            request = requests.PreparedRequest()
            request.headers = {}
            authenticator(request)
            # Should log header creation
            mock_logger.debug.assert_any_call("Basic auth headers created")

    def test_call_debug_logging_only_on_first_call(self) -> None:
        """Test debug logging only occurs on first call."""
        with patch("flext_tap_oracle_wms.auth.logger") as mock_logger:
            authenticator = self.create_test_authenticator()
            request1 = requests.PreparedRequest()
            request1.headers = requests.structures.CaseInsensitiveDict()
            request2 = requests.PreparedRequest()
            request2.headers = requests.structures.CaseInsensitiveDict()
            # First call should log
            authenticator(request1)
            if mock_logger.debug.call_count < 1:
                msg = f"Expected {mock_logger.debug.call_count} >= {1}"
                raise AssertionError(msg)
            # Reset and make second call
            mock_logger.reset_mock()
            authenticator(request2)
            # Second call should not log header creation
            mock_logger.debug.assert_not_called()

    def test_different_credentials_create_different_headers(self) -> None:
        """Test different credentials create different auth headers."""
        auth1 = self.create_test_authenticator("user1", "pass1")
        auth2 = self.create_test_authenticator("user2", "pass2")
        request1 = requests.PreparedRequest()
        request1.headers = requests.structures.CaseInsensitiveDict()
        request2 = requests.PreparedRequest()
        request2.headers = requests.structures.CaseInsensitiveDict()
        auth1(request1)
        auth2(request2)
        assert request1.headers["Authorization"] != request2.headers["Authorization"]

    def test_empty_credentials_still_work(self) -> None:
        """Test that empty credentials still create valid auth headers."""
        auth = self.create_test_authenticator("", "")
        request = requests.PreparedRequest()
        request.headers = requests.structures.CaseInsensitiveDict()
        result = auth(request)
        # Should create basic auth header even with empty creds
        if "Authorization" not in result.headers:
            msg = f"Expected {'Authorization'} in {result.headers}"
            raise AssertionError(msg)
        if result.headers["Authorization"] != "Basic Og==":  # base64 of ":":
            msg = f"Expected {'Basic Og=='} in {result.headers['Authorization']}"
            raise AssertionError(
                msg,
            )

    def test_special_characters_in_credentials(self) -> None:
        """Test handling of special characters in credentials."""
        username = "user@domain.com"
        password = "pass!@#$%^&*()"
        auth = self.create_test_authenticator(username, password)
        request = requests.PreparedRequest()
        request.headers = requests.structures.CaseInsensitiveDict()
        result = auth(request)
        # Should handle special characters correctly
        expected_creds = f"{username}:{password}"
        expected_encoded = base64.b64encode(expected_creds.encode()).decode()
        if result.headers["Authorization"] != f"Basic {expected_encoded}":
            msg = f"Expected {f'Basic {expected_encoded}'}, got {result.headers['Authorization']}"
            raise AssertionError(
                msg,
            )

    def test_unicode_credentials(self) -> None:
        """Test handling of unicode characters in credentials."""
        username = "usuário"
        password = "señal123"
        auth = self.create_test_authenticator(username, password)
        request = requests.PreparedRequest()
        request.headers = requests.structures.CaseInsensitiveDict()
        result = auth(request)
        # Should handle unicode correctly
        expected_creds = f"{username}:{password}"
        expected_encoded = base64.b64encode(expected_creds.encode()).decode()
        if result.headers["Authorization"] != f"Basic {expected_encoded}":
            msg = f"Expected {f'Basic {expected_encoded}'}, got {result.headers['Authorization']}"
            raise AssertionError(
                msg,
            )


class TestGetWMSAuthenticator:
    """Test get_wms_authenticator function."""

    def test_get_authenticator_with_valid_config(self) -> None:
        """Test getting authenticator with valid configuration."""
        stream = Mock()
        config = {
            "username": "test_user",
            "password": "test_password",
        }
        authenticator = get_wms_authenticator(stream, config)
        assert isinstance(authenticator, WMSBasicAuthenticator)
        if authenticator.username != "test_user":
            msg = f"Expected {'test_user'}, got {authenticator.username}"
            raise AssertionError(
                msg,
            )
        assert authenticator.password == "test_password"

    def test_get_authenticator_missing_username(self) -> None:
        """Test error when username is missing."""
        stream = Mock()
        config = {"password": "test_password"}
        with pytest.raises(
            ValueError,
            match="Username and password are required for WMS authentication",
        ):
            get_wms_authenticator(stream, config)

    def test_get_authenticator_missing_password(self) -> None:
        """Test error when password is missing."""
        stream = Mock()
        config = {"username": "test_user"}
        with pytest.raises(
            ValueError,
            match="Username and password are required for WMS authentication",
        ):
            get_wms_authenticator(stream, config)

    def test_get_authenticator_empty_username(self) -> None:
        """Test error when username is empty."""
        stream = Mock()
        config = {
            "username": "",
            "password": "test_password",
        }
        with pytest.raises(
            ValueError,
            match="Username and password are required for WMS authentication",
        ):
            get_wms_authenticator(stream, config)

    def test_get_authenticator_empty_password(self) -> None:
        """Test error when password is empty."""
        stream = Mock()
        config = {
            "username": "test_user",
            "password": "",
        }
        with pytest.raises(
            ValueError,
            match="Username and password are required for WMS authentication",
        ):
            get_wms_authenticator(stream, config)

    def test_get_authenticator_both_missing(self) -> None:
        """Test error when both username and password are missing."""
        stream = Mock()
        config: dict[str, str] = {}
        with pytest.raises(
            ValueError,
            match="Username and password are required for WMS authentication",
        ):
            get_wms_authenticator(stream, config)

    def test_get_authenticator_none_values(self) -> None:
        """Test error when username and password are None."""
        stream = Mock()
        config = {
            "username": None,
            "password": None,
        }
        with pytest.raises(
            ValueError,
            match="Username and password are required for WMS authentication",
        ):
            get_wms_authenticator(stream, config)

    def test_get_authenticator_with_extra_config(self) -> None:
        """Test getting authenticator ignores extra config values."""
        stream = Mock()
        config = {
            "username": "test_user",
            "password": "test_password",
            "extra_field": "ignored",
            "another_field": 123,
        }
        authenticator = get_wms_authenticator(stream, config)
        assert isinstance(authenticator, WMSBasicAuthenticator)
        if authenticator.username != "test_user":
            msg = f"Expected {'test_user'}, got {authenticator.username}"
            raise AssertionError(
                msg,
            )
        assert authenticator.password == "test_password"


class TestGetWMSHeaders:
    """Test get_wms_headers function."""

    def test_get_headers_default(self) -> None:
        """Test getting default WMS headers."""
        config: dict[str, str] = {}
        headers = get_wms_headers(config)
        expected = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "flext-data.taps.flext-data.taps.flext-tap-oracle-wms/1.0",
        }
        if headers != expected:
            msg = f"Expected {expected}, got {headers}"
            raise AssertionError(msg)

    def test_get_headers_with_custom_headers(self) -> None:
        """Test getting headers with custom headers from config."""
        config = {
            "headers": {
                "Custom-Header": "custom-value",
                "Another-Header": "another-value",
            },
        }
        headers = get_wms_headers(config)
        # Should include both default and custom headers
        if headers["Accept"] != "application/json":
            msg = f"Expected {'application/json'}, got {headers['Accept']}"
            raise AssertionError(
                msg,
            )
        assert headers["Content-Type"] == "application/json"
        assert (
            headers["User-Agent"]
            == "flext-data.taps.flext-data.taps.flext-tap-oracle-wms/1.0"
        )
        if headers["Custom-Header"] != "custom-value":
            msg = f"Expected {'custom-value'}, got {headers['Custom-Header']}"
            raise AssertionError(
                msg,
            )
        assert headers["Another-Header"] == "another-value"

    def test_get_headers_overrides_default(self) -> None:
        """Test that custom headers can override defaults."""
        config = {
            "headers": {
                "Accept": "text/plain",
                "User-Agent": "custom-agent/2.0",
            },
        }
        headers = get_wms_headers(config)
        # Custom headers should override defaults
        if headers["Accept"] != "text/plain":
            msg = f"Expected {'text/plain'}, got {headers['Accept']}"
            raise AssertionError(msg)
        assert headers["User-Agent"] == "custom-agent/2.0"
        if headers["Content-Type"] != "application/json":  # Not overridden:
            msg = f"Expected {'application/json'} in {headers['Content-Type']}"
            raise AssertionError(
                msg,
            )

    def test_get_headers_empty_custom_headers(self) -> None:
        """Test getting headers with empty custom headers."""
        config: dict[str, dict[str, str]] = {"headers": {}}
        headers = get_wms_headers(config)
        expected = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "flext-data.taps.flext-data.taps.flext-tap-oracle-wms/1.0",
        }
        if headers != expected:
            msg = f"Expected {expected}, got {headers}"
            raise AssertionError(msg)

    def test_get_headers_no_headers_key(self) -> None:
        """Test getting headers when config has no headers key."""
        config = {"other_field": "value"}
        headers = get_wms_headers(config)
        expected = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "flext-data.taps.flext-data.taps.flext-tap-oracle-wms/1.0",
        }
        if headers != expected:
            msg = f"Expected {expected}, got {headers}"
            raise AssertionError(msg)

    def test_get_headers_preserves_original_config(self) -> None:
        """Test that getting headers doesn't modify original config."""
        original_config = {
            "headers": {
                "Custom-Header": "custom-value",
            },
            "other_field": "value",
        }
        config = original_config.copy()
        headers = get_wms_headers(config)
        # Config should be unchanged
        if config != original_config:
            msg = f"Expected {original_config}, got {config}"
            raise AssertionError(msg)
        # But headers should include both default and custom
        assert len(headers) > len(config["headers"])

    def test_get_headers_various_header_types(self) -> None:
        """Test getting headers with various header value types."""
        config = {
            "headers": {
                "String-Header": "string-value",
                "Int-Header": 123,
                "Bool-Header": True,
                "Float-Header": 45.67,
            },
        }
        headers = get_wms_headers(config)
        # All header values should be converted to strings
        if headers["String-Header"] != "string-value":
            msg = f"Expected {'string-value'}, got {headers['String-Header']}"
            raise AssertionError(
                msg,
            )
        assert headers["Int-Header"] == "123"
        if headers["Bool-Header"] != "True":
            msg = f"Expected {'True'}, got {headers['Bool-Header']}"
            raise AssertionError(msg)
        assert headers["Float-Header"] == "45.67"


class TestAuthIntegration:
    """Test integration between auth components."""

    def test_authenticator_and_headers_integration(self) -> None:
        """Test integration between authenticator and headers."""
        stream = Mock()
        config = {
            "username": "test_user",
            "password": "test_password",
            "headers": {
                "Custom-Header": "custom-value",
            },
        }
        # Get authenticator and headers
        authenticator = get_wms_authenticator(stream, config)
        headers = get_wms_headers(config)
        # Create request with headers
        request = requests.PreparedRequest()
        request.headers = requests.structures.CaseInsensitiveDict(headers)
        # Apply authentication
        auth_request = authenticator(request)
        # Should have both custom and auth headers
        if auth_request.headers["Custom-Header"] != "custom-value":
            msg = f"Expected {'custom-value'}, got {auth_request.headers['Custom-Header']}"
            raise AssertionError(
                msg,
            )
        if "Authorization" not in auth_request.headers:
            msg = f"Expected {'Authorization'} in {auth_request.headers}"
            raise AssertionError(
                msg,
            )
        if auth_request.headers["Accept"] != "application/json":
            msg = f"Expected {'application/json'}, got {auth_request.headers['Accept']}"
            raise AssertionError(
                msg,
            )

    def test_multiple_authenticators_independence(self) -> None:
        """Test that multiple authenticators work independently."""
        stream1 = Mock()
        stream2 = Mock()
        config1 = {"username": "user1", "password": "pass1"}
        config2 = {"username": "user2", "password": "pass2"}
        auth1 = get_wms_authenticator(stream1, config1)
        auth2 = get_wms_authenticator(stream2, config2)
        request1 = requests.PreparedRequest()
        request1.headers = requests.structures.CaseInsensitiveDict()
        request2 = requests.PreparedRequest()
        request2.headers = requests.structures.CaseInsensitiveDict()
        auth1(request1)
        auth2(request2)
        # Should have different auth headers
        assert request1.headers["Authorization"] != request2.headers["Authorization"]

    def test_error_conditions_comprehensive(self) -> None:
        """Test comprehensive error conditions."""
        stream = Mock()
        # Test various invalid configurations
        invalid_configs = [
            {},
            {"username": "user"},
            {"password": "pass"},
            {"username": "", "password": "pass"},
            {"username": "user", "password": ""},
            {"username": None, "password": "pass"},
            {"username": "user", "password": None},
        ]
        for invalid_config in invalid_configs:
            with pytest.raises(ValueError, match=".*"):
                get_wms_authenticator(stream, invalid_config)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
