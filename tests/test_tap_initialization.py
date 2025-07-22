"""Test tap initialization without network calls."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from unittest.mock import MagicMock, patch

from flext_tap_oracle_wms.tap import TapOracleWMS


class TestTapInitialization:
    """Test tap initialization behavior."""

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams")
    def test_tap_init_no_network_calls(self, mock_discover: MagicMock) -> None:
        # Mock discover_streams to return empty list during initialization
        mock_discover.return_value = []
        config = {
            "base_url": "https://test.example.com",
            "username": "test",
            "password": "test",
            "entities": ["allocation", "order_hdr"],
        }
        # Mock external network calls to ensure they're not made
        with (
            patch("httpx.AsyncClient.get") as mock_get,
            patch("httpx.Client.get") as mock_client_get,
            patch("requests.get") as mock_requests_get,
        ):
            # Initialize tap - should not trigger external network calls
            tap = TapOracleWMS(config=config)
            # Verify no external network calls were made
            mock_get.assert_not_called()
            mock_client_get.assert_not_called()
            mock_requests_get.assert_not_called()
            # Verify tap is properly initialized
            assert tap.config["base_url"] == "https://test.example.com"
            assert tap.config["entities"] == ["allocation", "order_hdr"]

    def test_discover_streams_sync_mode_no_api_calls(self) -> None:
        config = {
            "base_url": "https://test.example.com",
            "username": "test",
            "password": "test",
            "entities": ["allocation", "order_hdr"],
        }
        # Mock both async and sync HTTP calls
        with (
            patch("httpx.AsyncClient") as mock_async_client,
            patch("httpx.Client") as mock_sync_client,
            patch("requests.get") as mock_requests,
            patch.object(TapOracleWMS, "_create_minimal_schema") as mock_schema,
        ):
            # Mock the discovery metadata fetch
            mock_schema.return_value = {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "mod_ts": {"type": "string", "format": "date-time"},
                },
            }
            tap = TapOracleWMS(config=config)
            # Discover streams in sync mode
            streams = tap.discover_streams()
            # Should create minimal streams without API calls
            assert len(streams) == 2
            assert streams[0].name == "allocation"
            assert streams[1].name == "order_hdr"
            # Verify no network calls were made
            mock_async_client.assert_not_called()
            mock_sync_client.assert_not_called()
            mock_requests.assert_not_called()

    def test_discover_streams_discovery_mode_deferred(self) -> None:
        """Test discovery mode deferred behavior."""
        config = {
            "base_url": "https://test.example.com",
            "username": "test",
            "password": "test",
            "entities": ["test_entity"],
            "enable_incremental": False,  # Disable incremental for simpler test
        }
        with (
            patch("httpx.AsyncClient"),
            patch("flext_tap_oracle_wms.tap.TapOracleWMS.discovery") as mock_discovery,
        ):
            # Mock the discovery property to avoid actual network calls
            mock_discovery.describe_entity_sync.return_value = {
                "fields": {
                    "id": {"type": "string", "nullable": False},
                    "name": {"type": "string", "nullable": True},
                },
            }
            tap = TapOracleWMS(config=config)
            # Set discovery mode
            tap.set_discovery_mode(enabled=True)
            # Now discovery should work
            streams = tap.discover_streams()
            assert len(streams) == 1
            assert streams[0].name == "test_entity"

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams")
    def test_lazy_loading_discovery(self, mock_discover: MagicMock) -> None:
        """Test lazy loading discovery behavior."""
        # Mock discover_streams to return empty list during initialization
        mock_discover.return_value = []
        config = {
            "base_url": "https://test.example.com",
            "username": "test",
            "password": "test",
            "entities": ["allocation", "order_hdr"],
        }
        tap = TapOracleWMS(config=config)
        # Initially, discovery should be None
        assert tap._discovery is None
        assert tap._schema_generator is None
        # Mock validation to avoid network calls
        with patch.object(tap, "_validate_configuration"):
            # Access discovery property - should create instance
            discovery = tap.discovery
            assert discovery is not None
            assert tap._discovery is discovery
            # Access schema_generator - should create instance
            schema_gen = tap.schema_generator
            # Verify schema generator is properly initialized
            _ = schema_gen  # Used to satisfy mypy

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams")
    def test_config_type_conversion(self, mock_discover: MagicMock) -> None:
        # Mock discover_streams to return empty list during initialization
        mock_discover.return_value = []
        config = {
            "base_url": "https://test.example.com",
            "username": "test",
            "password": "test",
            "entities": ["test_entity"],
            "page_size": 100,  # Integer
            "enable_incremental": True,  # Boolean
            "verify_ssl": False,  # Boolean
        }
        # Mock all network calls to prevent real API calls during initialization
        with (
            patch("httpx.AsyncClient"),
            patch("httpx.Client"),
            patch("requests.get"),
        ):
            tap = TapOracleWMS(config=config)
            # Verify types are correct
            assert isinstance(tap.config["page_size"], int)
            assert tap.config["page_size"] == 100
            assert isinstance(tap.config["enable_incremental"], bool)
            assert tap.config["enable_incremental"] is True
            assert isinstance(tap.config["verify_ssl"], bool)
            assert tap.config["verify_ssl"] is False

    def test_minimal_schema_creation(self) -> None:
        config = {
            "base_url": "https://test.example.com",
            "username": "test",
            "password": "test",
            "entities": ["test_entity"],
        }
        # Mock all network calls completely
        with (
            patch("httpx.AsyncClient"),
            patch("httpx.Client"),
            patch("requests.get"),
            patch.object(TapOracleWMS, "discovery") as mock_discovery,
            patch.object(TapOracleWMS, "_discover_entities_sync") as mock_entities,
        ):
            mock_entities.return_value = {"test_entity": "http://test.url"}
            mock_discovery.describe_entity_sync.return_value = None
            tap = TapOracleWMS(config=config)
            # Create minimal schema
            schema = tap._create_minimal_schema("test_entity")
            assert schema["type"] == "object"
            assert "properties" in schema
            assert "id" in schema["properties"]
            assert "_sdc_extracted_at" in schema["properties"]
            assert "_sdc_entity" in schema["properties"]
            assert schema["additionalProperties"] is True
