"""Tap initialization behavior tests aligned with current tap contract."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from flext_tap_oracle_wms import FlextTapOracleWms, FlextTapOracleWmsConfigurationError
from tests import r


class TestTapInitialization:
    """Verify initialization and stream loading without external I/O."""

    def test_tap_initialization_uses_normalized_config(self) -> None:
        """Tap stores normalized settings values from settings serialization."""
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(
                settings={
                    "base_url": "https://test.example.com",
                    "username": "test",
                    "password": "test",
                },
            )
        assert "test.example.com" in str(tap.settings["base_url"])
        assert tap.settings["username"] == "test"

    def test_discover_streams_returns_empty_on_discovery_failure(self) -> None:
        """discover_streams returns no streams if catalog discovery fails."""
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(
                settings={
                    "base_url": "https://test.example.com",
                    "username": "test",
                    "password": "test",
                },
            )

        with patch.object(
            tap,
            "discovercatalog_typed",
            return_value=r.fail("discovery unavailable"),
        ):
            with pytest.raises(FlextTapOracleWmsConfigurationError):
                tap.discover_streams()

    def test_discover_streams_uses_client_entities(self) -> None:
        """discover_streams builds streams for each discovered entity."""
        mock_client = MagicMock()
        mock_client.start.return_value = r[bool].ok(True)
        mock_client.discover_entities.return_value = r[list[str]].ok([
            "allocation",
            "order_hdr",
        ])
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(
                settings={
                    "base_url": "https://test.example.com",
                    "username": "test",
                    "password": "test",
                },
            )
        tap._wms_client = mock_client
        stream_names = [stream.name for stream in tap.discover_streams()]
        assert "allocation" in stream_names
        assert "order_hdr" in stream_names

    def test_execute_reuses_sync_all_entrypoint(self) -> None:
        """execute() delegates to sync_all when no message is passed."""
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(
                settings={
                    "base_url": "https://test.example.com",
                    "username": "test",
                    "password": "test",
                },
            )
        with patch.object(tap, "sync_all") as mock_sync:
            result = tap.execute()
        assert result.success
        mock_sync.assert_called_once()
