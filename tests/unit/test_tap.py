"""Unit tests for the Oracle WMS tap implementation."""

from __future__ import annotations

from collections.abc import (
    Mapping,
)
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from flext_tests import r, tm

from flext_tap_oracle_wms import m
from flext_tap_oracle_wms.errors import FlextTapOracleWmsConfigurationError
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from tests import t

if TYPE_CHECKING:
    from flext_tap_oracle_wms._settings import FlextTapOracleWmsSettings


class TestsFlextTapOracleWmsTap:
    """Validate tap behavior against current implementation contract."""

    def test_tap_initialization_with_config(
        self,
        sample_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Tap stores validated settings and starts with lazy client."""
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(
                config=sample_config.TapOracleWms.model_dump(mode="json"),
            )
        tm.that(tap.name, eq="flext-tap-oracle-wms")

    def test_tap_initialization_with_dict(self) -> None:
        """Tap accepts plain settings mappings and normalizes settings values."""
        config_dict = {
            "base_url": "https://test.wms.example.com",
            "username": "test_user",
            "password": "test_password",
        }
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(config=config_dict)
        tm.that(tap.flext_config.TapOracleWms.base_url, has="test.wms.example.com")
        tm.that(tap.flext_config.TapOracleWms.username, eq="test_user")

    def test_tap_initialization_invalid_config(self) -> None:
        """Invalid settings payload raises configuration error."""
        config_dict = {
            "base_url": "invalid-url",
            "username": "test_user",
            "password": "test_password",
        }
        with pytest.raises(FlextTapOracleWmsConfigurationError):
            FlextTapOracleWms(config=config_dict)

    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsUtilities.OracleWms.Client")
    def test_wms_client_property_lazy_initialization(
        self,
        mock_client_class: MagicMock,
    ) -> None:
        """Client is created only once and reused after first access."""
        mock_client = MagicMock()
        mock_client.start.return_value = r[bool].ok(True)
        mock_client.discover_entities.return_value = r[t.StrSequence].ok(())
        mock_client_class.return_value = mock_client
        tap = FlextTapOracleWms(
            config={
                "base_url": "https://test.wms.example.com",
                "username": "test_user",
                "password": "test_password",
            },
        )
        client_1 = tap.wms_client
        client_2 = tap.wms_client
        tm.that(client_1, eq=mock_client)
        tm.that(client_2, eq=mock_client)
        mock_client_class.assert_called_once()
        mock_client.start.assert_called_once()

    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsUtilities.OracleWms.Client")
    def test_wms_client_connection_failure(self, mock_client_class: MagicMock) -> None:
        """Failed WMS client start is surfaced as tap settings error."""
        mock_client = MagicMock()
        mock_client.start.return_value = r[bool].fail("Connection refused")
        mock_client_class.return_value = mock_client
        with pytest.raises(FlextTapOracleWmsConfigurationError):
            _ = FlextTapOracleWms(
                config={
                    "base_url": "https://test.wms.example.com",
                    "username": "test_user",
                    "password": "test_password",
                },
            )

    def test_discover_catalog_success(self, tap_instance: FlextTapOracleWms) -> None:
        """Catalog discovery maps discovered entities to Singer streams."""
        mock_client = MagicMock()
        mock_client.discover_entities.return_value = r[t.StrSequence].ok([
            "inventory",
            "locations",
        ])
        with patch.object(
            FlextTapOracleWms,
            "wms_client",
            new_callable=PropertyMock,
            return_value=mock_client,
        ):
            result = tap_instance.discovercatalog_typed()
        tm.ok(result)
        tm.that(result.value.streams[0].stream, eq="inventory")
        tm.that(result.value.streams[1].stream, eq="locations")

    def test_discover_catalog_failure(self, tap_instance: FlextTapOracleWms) -> None:
        """Catalog discovery propagates client discovery failures."""
        mock_client = MagicMock()
        mock_client.discover_entities.return_value = r[t.StrSequence].fail("boom")
        with patch.object(
            FlextTapOracleWms,
            "wms_client",
            new_callable=PropertyMock,
            return_value=mock_client,
        ):
            result = tap_instance.discovercatalog_typed()
        tm.fail(result)
        tm.that(result.error, eq="boom")

    def test_discover_streams_empty_when_catalog_fails(
        self,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Stream discovery raises ConfigurationError when catalog discovery fails."""
        with patch.object(
            tap_instance,
            "discovercatalog_typed",
            return_value=r[m.Meltano.SingerCatalog].fail("no catalog"),
        ):
            with pytest.raises(FlextTapOracleWmsConfigurationError):
                tap_instance.discover_streams()

    def test_discover_streams_success(self, tap_instance: FlextTapOracleWms) -> None:
        """Stream discovery builds stream objects from discovered catalog."""
        catalog = m.Meltano.SingerCatalog(
            streams=[
                m.Meltano.SingerCatalogEntry.model_validate({
                    "tap_stream_id": "inventory",
                    "stream": "inventory",
                    "schema": {"type": "object"},
                    "metadata": [],
                    "key_properties": ["id"],
                    "replication_key": None,
                    "replication_method": "FULL_TABLE",
                    "is_view": None,
                    "table_name": None,
                    "database_name": None,
                    "row_count": None,
                }),
            ],
        )
        with patch.object(
            tap_instance,
            "discovercatalog_typed",
            return_value=r[m.Meltano.SingerCatalog].ok(catalog),
        ):
            streams = tap_instance.discover_streams()
        tm.that(len(streams), eq=1)
        tm.that(streams[0].name, eq="inventory")

    def test_execute_normal_mode(self, tap_instance: FlextTapOracleWms) -> None:
        """Execute without message triggers sync flow and returns success."""
        with patch.object(tap_instance, "sync_all") as mock_sync:
            result = tap_instance.execute()
        tm.ok(result)
        mock_sync.assert_called_once()

    def test_execute_with_message_unsupported(
        self,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Custom message execution is not supported by the tap."""
        result = tap_instance.execute("some message")
        tm.fail(result)
        tm.that(str(result.error), has="Tap does not support message execution")

    def test_validate_configuration(self, tap_instance: FlextTapOracleWms) -> None:
        """Validation method exposes non-secret effective settings values."""
        result = tap_instance.validate_configuration()
        tm.ok(result)
        value = result.value
        tm.that(value, is_=Mapping)
        tm.that(value["base_url"], eq=tap_instance.flext_config.TapOracleWms.base_url)
        tm.that(value, lacks="password")

    def test_get_implementation_name_and_version(
        self,
        tap_instance: FlextTapOracleWms,
    ) -> None:
        """Implementation metadata methods return stable, non-empty values."""
        tm.that(tap_instance.get_implementation_name(), eq="FLEXT Oracle WMS Tap")
        tm.that(tap_instance.get_implementation_version(), ne="")

    def test_get_implementation_metrics(self, tap_instance: FlextTapOracleWms) -> None:
        """Metrics payload contains baseline tap observability fields."""
        with patch.object(tap_instance, "discover_streams", return_value=[]):
            result = tap_instance.get_implementation_metrics()
        tm.ok(result)
        metrics = result.value
        tm.that(metrics, is_=Mapping)
        tm.that(metrics["tap_name"], eq="flext-tap-oracle-wms")
        tm.that(metrics, has="version")
        tm.that(metrics, has="streams_available")
