"""Unit tests for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flext_core import FlextResult



    FlextTapOracleWms,
    FlextTapOracleWmsSettings,
    FlextTapOracleWmsSettingsurationError,
)


class TestFlextTapOracleWms:
    """Test FlextTapOracleWms class."""

    def test_tap_initialization_with_config(
        self,
        sample_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test tap initialization with config."""
        tap = FlextTapOracleWms(config=sample_config)

        assert tap.name == "flext-tap-oracle-wms"
        assert tap.flext_config == sample_config
        # Client is initialized on first access, discovery uses wms_client directly
        assert tap._wms_client is not None  # Created when accessing streams
        assert tap.discovery is not None  # Discovery property returns wms_client

    def test_tap_initialization_with_dict(self) -> None:
        """Test tap initialization with dict[str, object] config."""
        config_dict: dict[str, object] = {
            "base_url": "https://test.wms.example.com",
            "username": "test_user",
            "password": "test_password",
        }

        tap = FlextTapOracleWms(config=config_dict)

        assert tap.flext_config.base_url == "https://test.wms.example.com"
        assert tap.flext_config.username == "test_user"

    def test_tap_initialization_invalid_config(self) -> None:
        """Test tap initialization with invalid config."""
        config_dict: dict[str, object] = {
            "base_url": "invalid-url",  # Missing protocol
            "username": "test_user",
            "password": "test_password",
        }

        with pytest.raises(FlextTapOracleWmsSettingsurationError):
            FlextTapOracleWms(config=config_dict)

    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsClient")
    def test_wms_client_property(
        self,
        mock_client_class: MagicMock,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test WMS client property lazy initialization."""
        # Mock client instance
        mock_client = MagicMock()
        mock_client.connect.return_value = FlextResult[None].ok(data=None)
        mock_client_class.return_value = mock_client

        # First access creates client
        client1 = tap_instance.wms_client
        assert client1 == mock_client
        mock_client_class.assert_called_once()
        mock_client.connect.assert_called_once()

        # Second access returns same client
        client2 = tap_instance.wms_client
        assert client2 == client1
        assert mock_client_class.call_count == 1

    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsClient")
    def test_wms_client_connection_failure(
        self,
        mock_client_class: MagicMock,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test WMS client connection failure."""
        # Mock failed connection
        mock_client = MagicMock()
        mock_client.connect.return_value = FlextResult[None].fail("Connection refused")
        mock_client_class.return_value = mock_client

        with pytest.raises(FlextTapOracleWmsSettingsurationError) as exc_info:
            _ = tap_instance.wms_client

        assert "Failed to connect to Oracle WMS" in str(exc_info.value)

    @patch("flext_tap_oracle_wms.tap.FlextWmsDiscovery")
    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsClient")
    def test_initialize(
        self,
        mock_client_class: MagicMock,
        mock_discovery_class: MagicMock,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test tap initialization."""
        # Mock client
        mock_client = MagicMock()
        mock_client.connect.return_value = FlextResult[None].ok(data=None)
        mock_client_class.return_value = mock_client

        # Mock discovery
        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery

        result = tap_instance.initialize()

        assert result.is_success
        assert tap_instance._discovery == mock_discovery
        mock_discovery_class.assert_called_once_with(mock_client)

    @patch("flext_tap_oracle_wms.tap.FlextWmsDiscovery")
    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsClient")
    def test_discover_catalog(
        self,
        mock_client_class: MagicMock,
        mock_discovery_class: MagicMock,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test catalog discovery."""
        # Mock client
        mock_client = MagicMock()
        mock_client.connect.return_value = FlextResult[None].ok(data=None)
        mock_client_class.return_value = mock_client

        # Mock discovery
        mock_discovery = MagicMock()
        mock_discovery.discover_entities.return_value = FlextResult[
            dict[str, object]
        ].ok(
            data={
                "inventory": {"type": "object", "properties": {}},
                "locations": {"type": "object", "properties": {}},
            },
        )
        mock_discovery.build_catalog.return_value = {
            "type": "CATALOG",
            "streams": [],
        }
        mock_discovery_class.return_value = mock_discovery

        result = tap_instance.discover_catalog()

        assert result.is_success
        assert result.value["type"] == "CATALOG"
        mock_discovery.discover_entities.assert_called_once()
        mock_discovery.build_catalog.assert_called_once()

    def test_stream_discovery(self, tap_instance: FlextTapOracleWms) -> None:
        """Test stream discovery."""
        streams = tap_instance.discover_streams()

        assert len(streams) > 0
        assert all(hasattr(stream, "name") for stream in streams)
        assert all(hasattr(stream, "tap") for stream in streams)
        assert all(stream.tap == tap_instance for stream in streams)

    def test_discover_streams_with_include(
        self,
        sample_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test stream discovery with include filter."""
        sample_config.include_entities = ["inventory", "locations"]
        tap = FlextTapOracleWms(config=sample_config)

        streams = tap.discover_streams()
        stream_names = [stream.name for stream in streams]

        assert "inventory" in stream_names
        assert "locations" in stream_names
        assert "shipments" not in stream_names

    def test_discover_streams_with_exclude(
        self,
        sample_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test stream discovery with exclude filter."""
        sample_config.exclude_entities = ["shipments", "receipts"]
        tap = FlextTapOracleWms(config=sample_config)

        streams = tap.discover_streams()
        stream_names = [stream.name for stream in streams]

        assert "inventory" in stream_names
        assert "locations" in stream_names
        assert "shipments" not in stream_names
        assert "receipts" not in stream_names

    def test_execute_normal_mode(self, tap_instance: FlextTapOracleWms) -> None:
        """Test execute without message (normal tap mode)."""
        with patch.object(tap_instance, "run") as mock_run:
            result = tap_instance.execute()

            assert result.is_success
            mock_run.assert_called_once()

    def test_execute_with_message_unsupported(
        self,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test execute with message (not supported for tap)."""
        result = tap_instance.execute("some message")

        assert result.is_failure
        assert "Tap does not support message processing" in str(result.error)

    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsClient")
    def test_validate_configuration(
        self,
        mock_client_class: MagicMock,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test configuration validation."""
        # Mock client
        mock_client = MagicMock()
        mock_client.connect.return_value = FlextResult[None].ok(data=None)
        mock_client.list_entities.return_value = FlextResult[list[str]].ok([
            "inventory",
        ])
        mock_client_class.return_value = mock_client

        result = tap_instance.validate_configuration()

        assert result.is_success
        assert result.value["valid"] is True
        assert result.value["connection"] == "success"
        mock_client.list_entities.assert_called_once_with(limit=1)

    def test_get_implementation_name(
        self,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test get implementation name."""
        assert tap_instance.get_implementation_name() == "FLEXT Oracle WMS Tap"

    def test_get_implementation_version(
        self,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test get implementation version."""
        version = tap_instance.get_implementation_version()
        assert isinstance(version, str)
        assert "." in version  # Should be semantic version

    def test_get_implementation_metrics(
        self,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test get implementation metrics."""
        result = tap_instance.get_implementation_metrics()

        assert result.is_success
        metrics = result.value
        assert "tap_name" in metrics
        assert "version" in metrics
        assert "streams_available" in metrics
        assert "configuration" in metrics
