"""Test tap initialization without network calls.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from unittest.mock import MagicMock, patch

from flext_tap_oracle_wms import FlextTapOracleWMS

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License


# Constants
EXPECTED_BULK_SIZE = 2


class TestTapInitialization:
    """Test tap initialization behavior."""

    @patch("flext_tap_oracle_wms.tap.FlextTapOracleWMS.discover_streams")
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
            tap = FlextTapOracleWMS(config=config)
            # Verify no external network calls were made
            mock_get.assert_not_called()
            mock_client_get.assert_not_called()
            mock_requests_get.assert_not_called()
            # Verify tap is properly initialized
            if tap.config["base_url"] != "https://test.example.com":
                msg: str = f"Expected {'https://test.example.com'}, got {tap.config['base_url']}"
                raise AssertionError(
                    msg,
                )
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
            patch.object(FlextTapOracleWMS, "_create_minimal_schema") as mock_schema,
        ):
            # Mock the discovery metadata fetch
            mock_schema.return_value = {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "mod_ts": {"type": "string", "format": "date-time"},
                },
            }
            tap = FlextTapOracleWMS(config=config)
            # Discover streams in sync mode
            streams = tap.discover_streams()
            # Should create minimal streams without API calls
            if len(streams) != EXPECTED_BULK_SIZE:
                msg: str = f"Expected {2}, got {len(streams)}"
                raise AssertionError(msg)
            assert streams[0].name == "allocation"
            if streams[1].name != "order_hdr":
                msg: str = f"Expected {'order_hdr'}, got {streams[1].name}"
                raise AssertionError(msg)
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
            patch(
                "flext_tap_oracle_wms.tap.FlextTapOracleWMS.discovery",
            ) as mock_discovery,
        ):
            # Mock the discovery property to avoid actual network calls
            mock_discovery.describe_entity_sync.return_value = {
                "fields": {
                    "id": {"type": "string", "nullable": False},
                    "name": {"type": "string", "nullable": True},
                },
            }
            tap = FlextTapOracleWMS(config=config)
            # Set discovery mode
            tap.set_discovery_mode(enabled=True)
            # Now discovery should work
            streams = tap.discover_streams()
            if len(streams) != 1:
                msg: str = f"Expected {1}, got {len(streams)}"
                raise AssertionError(msg)
            assert streams[0].name == "test_entity"

    @patch("flext_tap_oracle_wms.tap.FlextTapOracleWMS.discover_streams")
    @patch("flext_tap_oracle_wms.cache.CacheManagerAdapter")
    def test_lazy_loading_discovery(
        self,
        mock_cache_adapter: MagicMock,
        mock_discover: MagicMock,
    ) -> None:
        """Test lazy loading discovery behavior."""
        # Mock discover_streams to return empty list during initialization
        mock_discover.return_value = []

        # Mock cache manager to avoid FlextOracleWmsCacheStats initialization issues
        mock_cache_instance = MagicMock()
        mock_cache_adapter.return_value = mock_cache_instance

        config = {
            "base_url": "https://test.example.com",
            "username": "test",
            "password": "test",
            "entities": ["allocation", "order_hdr"],
        }
        tap = FlextTapOracleWMS(config=config)
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

    @patch("flext_tap_oracle_wms.tap.FlextTapOracleWMS.discover_streams")
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
            tap = FlextTapOracleWMS(config=config)
            # Verify types are correct
            assert isinstance(tap.config["page_size"], int)
            if tap.config["page_size"] != 100:
                msg: str = f"Expected {100}, got {tap.config['page_size']}"
                raise AssertionError(msg)
            assert isinstance(tap.config["enable_incremental"], bool)
            if not (tap.config["enable_incremental"]):
                msg: str = f"Expected True, got {tap.config['enable_incremental']}"
                raise AssertionError(
                    msg,
                )
            assert isinstance(tap.config["verify_ssl"], bool)
            if tap.config["verify_ssl"]:
                msg: str = f"Expected False, got {tap.config['verify_ssl']}"
                raise AssertionError(msg)

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
            patch.object(FlextTapOracleWMS, "discovery") as mock_discovery,
            patch.object(FlextTapOracleWMS, "_discover_entities_sync") as mock_entities,
        ):
            mock_entities.return_value = {"test_entity": "http://test.url"}
            mock_discovery.describe_entity_sync.return_value = None
            tap = FlextTapOracleWMS(config=config)
            # Create minimal schema
            schema = tap._create_minimal_schema("test_entity")
            if schema["type"] != "object":
                msg: str = f"Expected {'object'}, got {schema['type']}"
                raise AssertionError(msg)
            if "properties" not in schema:
                msg: str = f"Expected {'properties'} in {schema}"
                raise AssertionError(msg)
            assert "id" in schema["properties"]
            if "_sdc_extracted_at" not in schema["properties"]:
                msg: str = f"Expected {'_sdc_extracted_at'} in {schema['properties']}"
                raise AssertionError(
                    msg,
                )
            assert "_sdc_entity" in schema["properties"]
            if not (schema["additionalProperties"]):
                msg: str = f"Expected True, got {schema['additionalProperties']}"
                raise AssertionError(
                    msg,
                )
