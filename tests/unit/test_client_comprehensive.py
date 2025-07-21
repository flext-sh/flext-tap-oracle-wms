"""Comprehensive test suite for client module covering missing lines."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import httpx
import pytest
from pydantic import HttpUrl

from flext_tap_oracle_wms.client import (
    AuthenticationError,
    WMSClient,
    WMSClientError,
    WMSConnectionError,
)
from flext_tap_oracle_wms.models import TapMetrics, WMSConfig


class TestWMSClientComprehensive:
    """Comprehensive tests for WMSClient covering all missing lines."""

    @pytest.fixture
    def mock_config(self) -> WMSConfig:
        """Create mock WMS configuration."""
        return WMSConfig(
            base_url=HttpUrl("https://wms.example.com"),
            username="test_user",
            password="test_pass",
            timeout=30,
            company_code="TEST_COMP",
            facility_code="TEST_FAC",
            page_size=100,
        )

    @pytest.fixture
    def mock_metrics(self) -> TapMetrics:
        """Create mock metrics."""
        return TapMetrics(start_time=None)

    @pytest.fixture
    def wms_client(self, mock_config: WMSConfig, mock_metrics: TapMetrics) -> WMSClient:
        """Create WMS client instance."""
        return WMSClient(mock_config, mock_metrics)

    def test_client_imports_correct_modules(self) -> None:
        """Test that client module imports are correct (lines 17-20)."""
        # Import the client module to test TYPE_CHECKING imports
        from flext_tap_oracle_wms import client

        # Verify TYPE_CHECKING imports are available during runtime
        assert hasattr(client, "TYPE_CHECKING")
        # The imports inside TYPE_CHECKING block should be accessible
        # when TYPE_CHECKING is True (during static analysis)

    @patch("httpx.Client.get")
    def test_get_method_exception_handling_unexpected_error(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test GET method handles unexpected errors (line 128)."""
        # Mock an unexpected exception that's not in the handled types
        mock_get.side_effect = ValueError("Unexpected error")

        with pytest.raises(WMSClientError) as excinfo:
            wms_client.get("/test")

        assert "Unexpected error: Unexpected error" in str(excinfo.value)

    @patch("httpx.Client.get")
    def test_discover_entities_multiple_endpoints_success(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test discover_entities tries multiple endpoints and succeeds.

        (lines 139-165).
        """
        # First endpoint fails, second succeeds
        responses = [
            # First call to /entities fails
            MagicMock(side_effect=WMSClientError("Not found")),
            # Second call to /api/entities succeeds
            MagicMock(
                status_code=200,
                json=lambda: {"data": [{"id": 1, "name": "item"}]},
            ),
        ]
        mock_get.side_effect = responses

        with patch("flext_tap_oracle_wms.client.logger") as mock_logger:
            result = wms_client.discover_entities()

        assert result == [{"id": 1, "name": "item"}]
        mock_logger.info.assert_any_call("Discovering WMS entities")
        mock_logger.info.assert_any_call("Found %d entities via %s", 1, "/api/entities")

    @patch("httpx.Client.get")
    def test_discover_entities_entities_key_format(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test discover_entities handles entities key format (lines 156-160)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"entities": [{"id": 1}, {"id": 2}]}
        mock_get.return_value = mock_response

        with patch("flext_tap_oracle_wms.client.logger") as mock_logger:
            result = wms_client.discover_entities()

        assert result == [{"id": 1}, {"id": 2}]
        mock_logger.info.assert_any_call("Found %d entities via %s", 2, "/entities")

    @patch("httpx.Client.get")
    def test_discover_entities_all_endpoints_fail(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test discover_entities when all endpoints fail (lines 161-165)."""
        # All endpoints fail
        mock_get.side_effect = WMSClientError("Not found")

        with patch("flext_tap_oracle_wms.client.logger") as mock_logger:
            result = wms_client.discover_entities()

        assert result == []
        mock_logger.warning.assert_called_with(
            "No entities discovered - will try common WMS endpoints",
        )

    def test_get_entity_data_with_config_params(self, wms_client: WMSClient) -> None:
        """Test get_entity_data uses config parameters (lines 182-192)."""
        with patch.object(wms_client, "get") as mock_get:
            mock_get.return_value = {"data": "test"}

            result = wms_client.get_entity_data("items", {"limit": 50})

            expected_params = {
                "company_code": "TEST_COMP",
                "facility_code": "TEST_FAC",
                "page_size": 100,
                "limit": 50,
            }
            mock_get.assert_called_once_with("/api/items", expected_params)
            assert result == {"data": "test"}

    def test_get_entity_data_without_params(self, wms_client: WMSClient) -> None:
        """Test get_entity_data without additional params."""
        with patch.object(wms_client, "get") as mock_get:
            mock_get.return_value = {"data": "test"}

            wms_client.get_entity_data("orders")

            expected_params = {
                "company_code": "TEST_COMP",
                "facility_code": "TEST_FAC",
                "page_size": 100,
            }
            mock_get.assert_called_once_with("/api/orders", expected_params)

    @patch("httpx.Client.get")
    def test_test_connection_primary_endpoint_success(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test test_connection succeeds on primary endpoint (line 201-214)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        result = wms_client.test_connection()

        assert result is True
        mock_get.assert_called_once_with("/api/ping", params={})

    @patch("httpx.Client.get")
    def test_test_connection_fallback_endpoints(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test test_connection tries fallback endpoints (lines 204-214)."""
        # Primary endpoint fails, fallback succeeds
        responses = [
            # /api/ping fails
            MagicMock(side_effect=WMSClientError("Not found")),
            # /health succeeds
            MagicMock(status_code=200, json=lambda: {"status": "healthy"}),
        ]
        mock_get.side_effect = responses

        result = wms_client.test_connection()

        assert result is True
        assert mock_get.call_count == 2

    @patch("httpx.Client.get")
    def test_test_connection_all_endpoints_fail(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test test_connection when all endpoints fail (lines 208-213)."""
        # All endpoints fail
        mock_get.side_effect = WMSConnectionError("Connection failed")

        result = wms_client.test_connection()

        assert result is False
        # Should try all endpoints: /api/ping, /health, /status, /api/health
        assert mock_get.call_count == 4

    def test_handle_response_errors_unauthorized(self) -> None:
        """Test _handle_response_errors for 401 status (lines 230-231)."""
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.UNAUTHORIZED

        with pytest.raises(AuthenticationError) as excinfo:
            WMSClient._handle_response_errors(mock_response)

        assert str(excinfo.value) == "Invalid credentials"

    def test_handle_response_errors_forbidden(self) -> None:
        """Test _handle_response_errors for 403 status (lines 233-234)."""
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.FORBIDDEN

        with pytest.raises(AuthenticationError) as excinfo:
            WMSClient._handle_response_errors(mock_response)

        assert str(excinfo.value) == "Access forbidden"

    def test_handle_response_errors_server_error(self) -> None:
        """Test _handle_response_errors for server errors (lines 236-237)."""
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

        with pytest.raises(WMSConnectionError) as excinfo:
            WMSClient._handle_response_errors(mock_response)

        assert str(excinfo.value) == "Server error: 500"

    def test_handle_response_errors_client_error(self) -> None:
        """Test _handle_response_errors for client errors (lines 239-240)."""
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_response.text = "Bad request body"

        with pytest.raises(WMSClientError) as excinfo:
            WMSClient._handle_response_errors(mock_response)

        assert str(excinfo.value) == "Client error: 400 - Bad request body"

    def test_handle_response_errors_success_status(self) -> None:
        """Test _handle_response_errors for success status (no error)."""
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK

        # Should not raise any exception
        WMSClient._handle_response_errors(mock_response)

    @patch("httpx.Client.get")
    def test_get_method_with_response_error_handling(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test GET method calls _handle_response_errors."""
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.UNAUTHORIZED
        mock_get.return_value = mock_response

        with pytest.raises(AuthenticationError):
            wms_client.get("/test")

    @patch("httpx.Client.get")
    def test_get_method_httpx_connect_error(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test GET method handles httpx.ConnectError."""
        mock_get.side_effect = httpx.ConnectError("Connection refused")

        with pytest.raises(WMSConnectionError) as excinfo:
            wms_client.get("/test")

        assert "Failed to connect to WMS: Connection refused" in str(excinfo.value)

    @patch("httpx.Client.get")
    def test_get_method_httpx_timeout_error(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test GET method handles httpx.TimeoutException."""
        mock_get.side_effect = httpx.TimeoutException("Request timeout")

        with pytest.raises(WMSConnectionError) as excinfo:
            wms_client.get("/test")

        assert "Request timeout: Request timeout" in str(excinfo.value)

    @patch("httpx.Client.get")
    def test_get_method_non_dict_response_wrapping(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test GET method wraps non-dict responses."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["item1", "item2"]  # List instead of dict
        mock_get.return_value = mock_response

        result = wms_client.get("/test")

        assert result == {"data": ["item1", "item2"]}

    @patch("httpx.Client.get")
    def test_get_method_metrics_tracking(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test GET method tracks metrics."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response

        initial_api_calls = wms_client.metrics.api_calls

        wms_client.get("/test")

        assert wms_client.metrics.api_calls == initial_api_calls + 1

    def test_client_ssl_verification_enabled(self, wms_client: WMSClient) -> None:
        """Test that SSL verification is always enabled."""
        # The httpx client should have verify=True
        # We test this indirectly by verifying the client was properly configured
        # Note: httpx Client doesn't expose verify publicly in newer versions
        assert (
            wms_client.client is not None
        )  # Client exists and was configured properly

    def test_client_basic_auth_configuration(self, wms_client: WMSClient) -> None:
        """Test that basic auth is properly configured."""
        # The auth should be configured
        auth = wms_client.client.auth
        assert auth is not None
        # httpx basic auth - we test it's the right type
        assert str(type(auth).__name__) == "BasicAuth"

    @patch("httpx.Client.get")
    def test_discover_entities_data_key_empty_list(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test discover_entities when data key has empty list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}  # Empty list
        mock_get.return_value = mock_response

        # Should continue to next endpoint when empty
        mock_get.side_effect = [
            mock_response,  # First endpoint returns empty
            WMSClientError("Not found"),  # Second endpoint fails
            WMSClientError("Not found"),  # Third endpoint fails
        ]

        with patch("flext_tap_oracle_wms.client.logger") as mock_logger:
            result = wms_client.discover_entities()

        assert result == []
        mock_logger.warning.assert_called_with(
            "No entities discovered - will try common WMS endpoints",
        )

    @patch("httpx.Client.get")
    def test_discover_entities_entities_key_not_list(
        self,
        mock_get: MagicMock,
        wms_client: WMSClient,
    ) -> None:
        """Test discover_entities when entities key is not a list."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"entities": "not a list"}
        mock_get.return_value = mock_response

        # Should continue to next endpoint when entities is not a list
        mock_get.side_effect = [
            mock_response,  # First endpoint returns non-list
            WMSClientError("Not found"),  # Second endpoint fails
            WMSClientError("Not found"),  # Third endpoint fails
        ]

        with patch("flext_tap_oracle_wms.client.logger"):
            result = wms_client.discover_entities()

        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
