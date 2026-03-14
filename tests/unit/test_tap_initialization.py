"""Tap initialization behavior tests aligned with current tap contract."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from flext_core import r

from flext_tap_oracle_wms import FlextTapOracleWms


class TestTapInitialization:
    """Verify initialization and stream loading without external I/O."""

    def test_tap_initialization_uses_normalized_config(self) -> None:
        """Tap stores normalized config values from settings serialization."""
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(
                config={
                    "base_url": "https://test.example.com",
                    "username": "test",
                    "password": "test",
                }
            )
        assert tap.config["base_url"] == "https://test.example.com/"
        assert tap.config["username"] == "test"
        assert tap.config["password"] == "**********"

    def test_discover_streams_returns_empty_on_discovery_failure(self) -> None:
        """discover_streams returns no streams if catalog discovery fails."""
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(
                config={
                    "base_url": "https://test.example.com",
                    "username": "test",
                    "password": "test",
                }
            )
        with patch.object(
            tap,
            "discover_catalog",
            return_value=r.fail("discovery unavailable"),
        ):
            streams = tap.discover_streams()
        assert streams == []

    @patch("flext_tap_oracle_wms.tap.FlextOracleWmsClient")
    def test_discover_streams_uses_client_entities(
        self, mock_client_class: MagicMock
    ) -> None:
        """discover_streams builds streams for each discovered entity."""
        mock_client = MagicMock()
        mock_client.start.return_value = r.ok(True)
        mock_client.discover_entities.return_value = r.ok([
            "allocation",
            "order_hdr",
        ])
        mock_client_class.return_value = mock_client
        tap = FlextTapOracleWms(
            config={
                "base_url": "https://test.example.com",
                "username": "test",
                "password": "test",
            }
        )
        stream_names = [stream.name for stream in tap.discover_streams()]
        assert "allocation" in stream_names
        assert "order_hdr" in stream_names

    def test_execute_reuses_sync_all_entrypoint(self) -> None:
        """execute() delegates to sync_all when no message is passed."""
        with patch.object(FlextTapOracleWms, "discover_streams", return_value=[]):
            tap = FlextTapOracleWms(
                config={
                    "base_url": "https://test.example.com",
                    "username": "test",
                    "password": "test",
                }
            )
        with patch.object(tap, "sync_all") as mock_sync:
            result = tap.execute()
        assert result.is_success
        mock_sync.assert_called_once()
