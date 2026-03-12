"""Unit tests for the Oracle WMS tap implementation."""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from flext_core import r

from flext_tap_oracle_wms import (
    FlextTapOracleWms,
    FlextTapOracleWmsConfigurationError,
    FlextTapOracleWmsSettings,
)
from flext_tap_oracle_wms.models import m


class TestFlextTapOracleWms:
    """Validate tap behavior against current implementation contract."""

    def test_tap_initialization_with_config(
        self, sample_config: FlextTapOracleWmsSettings
    ) -> None:
        """Tap stores validated settings and starts with lazy client."""
        tap = FlextTapOracleWms(config=sample_config)
        assert tap.name == "flext-tap-oracle-wms"
        assert tap.flext_config == sample_config

    def test_tap_initialization_with_dict(self) -> None:
        """Tap accepts plain config mappings and normalizes settings values."""
        config_dict: dict[str, object] = {
            "base_url": "https://test.wms.example.com",
            "username": "test_user",
            "password": "test_password",
        }
        tap = FlextTapOracleWms(config=config_dict)
        assert str(tap.flext_config.base_url) == "https://test.wms.example.com/"
        assert tap.flext_config.username == "test_user"

    def test_tap_initialization_invalid_config(self) -> None:
        """Invalid config payload raises configuration error."""
        config_dict: dict[str, object] = {
            "base_url": "invalid-url",
            "username": "test_user",
            "password": "test_password",
        }
        with pytest.raises(FlextTapOracleWmsConfigurationError):
            FlextTapOracleWms(config=config_dict)

    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsClient")
    def test_wms_client_property_lazy_initialization(
        self, mock_client_class: MagicMock
    ) -> None:
        """Client is created only once and reused after first access."""
        mock_client = MagicMock()
        mock_client.start.return_value = r[bool].ok(True)
        mock_client_class.return_value = mock_client
        tap = FlextTapOracleWms(
            config={
                "base_url": "https://test.wms.example.com",
                "username": "test_user",
                "password": "test_password",
            }
        )
        client_1 = tap.wms_client
        client_2 = tap.wms_client
        assert client_1 == mock_client
        assert client_2 == mock_client
        mock_client_class.assert_called_once()
        mock_client.start.assert_called_once()

    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsClient")
    def test_wms_client_connection_failure(self, mock_client_class: MagicMock) -> None:
        """Failed WMS client start is surfaced as tap config error."""
        mock_client = MagicMock()
        mock_client.start.return_value = r[bool].fail("Connection refused")
        mock_client_class.return_value = mock_client
        with pytest.raises(FlextTapOracleWmsConfigurationError):
            _ = FlextTapOracleWms(
                config={
                    "base_url": "https://test.wms.example.com",
                    "username": "test_user",
                    "password": "test_password",
                }
            )

    def test_discover_catalog_success(self, tap_instance: FlextTapOracleWms) -> None:
        """Catalog discovery maps discovered entities to Singer streams."""
        mock_client = MagicMock()
        mock_client.discover_entities.return_value = r[list[str]].ok([
            "inventory",
            "locations",
        ])
        with patch.object(
            FlextTapOracleWms,
            "wms_client",
            new_callable=PropertyMock,
            return_value=mock_client,
        ):
            result = tap_instance.discover_catalog()
        assert result.is_success
        assert result.value.streams[0].stream == "inventory"
        assert result.value.streams[1].stream == "locations"

    def test_discover_catalog_failure(self, tap_instance: FlextTapOracleWms) -> None:
        """Catalog discovery propagates client discovery failures."""
        mock_client = MagicMock()
        mock_client.discover_entities.return_value = r[list[str]].fail("boom")
        with patch.object(
            FlextTapOracleWms,
            "wms_client",
            new_callable=PropertyMock,
            return_value=mock_client,
        ):
            result = tap_instance.discover_catalog()
        assert result.is_failure
        assert result.error == "boom"

    def test_discover_streams_empty_when_catalog_fails(
        self, tap_instance: FlextTapOracleWms
    ) -> None:
        """Stream discovery returns empty list when catalog discovery fails."""
        with patch.object(
            tap_instance,
            "discover_catalog",
            return_value=r[m.Meltano.SingerCatalog].fail("no catalog"),
        ):
            streams = tap_instance.discover_streams()
        assert streams == []

    def test_discover_streams_success(self, tap_instance: FlextTapOracleWms) -> None:
        """Stream discovery builds stream objects from discovered catalog."""
        catalog = m.Meltano.SingerCatalog(
            streams=[
                m.Meltano.SingerCatalogEntry(
                    tap_stream_id="inventory",
                    stream="inventory",
                    schema={"type": "object", "properties": {}},
                    metadata=[],
                )
            ]
        )
        with patch.object(
            tap_instance,
            "discover_catalog",
            return_value=r[m.Meltano.SingerCatalog].ok(catalog),
        ):
            streams = tap_instance.discover_streams()
        assert len(streams) == 1
        assert streams[0].name == "inventory"

    def test_execute_normal_mode(self, tap_instance: FlextTapOracleWms) -> None:
        """Execute without message triggers sync flow and returns success."""
        with patch.object(tap_instance, "sync_all") as mock_sync:
            result = tap_instance.execute()
        assert result.is_success
        mock_sync.assert_called_once()

    def test_execute_with_message_unsupported(
        self, tap_instance: FlextTapOracleWms
    ) -> None:
        """Custom message execution is not supported by the tap."""
        result = tap_instance.execute("some message")
        assert result.is_failure
        assert "Tap does not support message execution" in str(result.error)

    def test_validate_configuration(self, tap_instance: FlextTapOracleWms) -> None:
        """Validation method exposes non-secret effective config values."""
        result = tap_instance.validate_configuration()
        assert result.is_success
        assert result.value["base_url"] == str(tap_instance.flext_config.base_url)
        assert "password" not in result.value

    def test_get_implementation_name_and_version(
        self, tap_instance: FlextTapOracleWms
    ) -> None:
        """Implementation metadata methods return stable, non-empty values."""
        assert tap_instance.get_implementation_name() == "FLEXT Oracle WMS Tap"
        assert tap_instance.get_implementation_version() != ""

    def test_get_implementation_metrics(self, tap_instance: FlextTapOracleWms) -> None:
        """Metrics payload contains baseline tap observability fields."""
        with patch.object(tap_instance, "discover_streams", return_value=[]):
            result = tap_instance.get_implementation_metrics()
        assert result.is_success
        metrics = result.value
        assert metrics["tap_name"] == "flext-tap-oracle-wms"
        assert "version" in metrics
        assert "streams_available" in metrics
