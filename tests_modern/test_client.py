"""Modern unit tests for WMS client."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from unittest.mock import Mock, patch

import httpx

import pytest
from flext_tap_oracle_wms.client import (
    AuthenticationError,
    WMSClient,
    WMSConnectionError,
)
from flext_tap_oracle_wms.models import TapMetrics, WMSConfig


class TestWMSClient:
    """Test WMS HTTP client."""

    @pytest.fixture
    def config(self) -> WMSConfig:
        return WMSConfig(
            base_url="https://wms.example.com",
            username="test_user",
            password="test_pass",
        )

    @pytest.fixture
    def metrics(self) -> TapMetrics:
        return TapMetrics()

    def test_client_initialization(
        self,
        config: WMSConfig,
        metrics: TapMetrics,
    ) -> None:
        with WMSClient(config, metrics) as client:
            assert client.config == config
            assert client.metrics == metrics
            assert client.client.base_url == "https://wms.example.com"

    @patch("flext_tap_oracle_wms.client.httpx.Client")
    def test_successful_get_request(
        self,
        mock_client_class: Mock,
        config: WMSConfig,
        metrics: TapMetrics,
    ) -> None:
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with WMSClient(config, metrics) as client:
            result = client.get("/test", {"param": "value"})

        assert result == {"data": "test"}
        assert metrics.api_calls_made == 1

    @patch("flext_tap_oracle_wms.client.httpx.Client")
    def test_authentication_error(
        self,
        mock_client_class: Mock,
        config: WMSConfig,
        metrics: TapMetrics,
    ) -> None:
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            with WMSClient(config, metrics) as client:
                client.get("/test")

    @patch("flext_tap_oracle_wms.client.httpx.Client")
    def test_connection_error(
        self,
        mock_client_class: Mock,
        config: WMSConfig,
        metrics: TapMetrics,
    ) -> None:
        # Setup mock
        mock_client = Mock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        mock_client_class.return_value = mock_client

        with pytest.raises(WMSConnectionError, match="Failed to connect to WMS"):
            with WMSClient(config, metrics) as client:
                client.get("/test")

    @patch("flext_tap_oracle_wms.client.httpx.Client")
    def test_discover_entities_success(
        self,
        mock_client_class: Mock,
        config: WMSConfig,
        metrics: TapMetrics,
    ) -> None:
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "item_master", "endpoint": "/api/item_master"},
            {"name": "location", "endpoint": "/api/location"},
        ]
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with WMSClient(config, metrics) as client:
            entities = client.discover_entities()

        assert len(entities) == 2
        assert entities[0]["name"] == "item_master"

    @patch("flext_tap_oracle_wms.client.httpx.Client")
    def test_get_entity_data(
        self,
        mock_client_class: Mock,
        config: WMSConfig,
        metrics: TapMetrics,
    ) -> None:
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"records": [{"id": 1, "name": "test"}]}
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with WMSClient(config, metrics) as client:
            client.get_entity_data("item_master", {"limit": 10})

        # Verify correct endpoint called with scoping parameters
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "/api/item_master"

        # Verify scoping parameters added
        params = call_args[1]["params"]
        assert params["company_code"] == "*"
        assert params["facility_code"] == "*"
        assert params["page_size"] == 100
        assert params["limit"] == 10
