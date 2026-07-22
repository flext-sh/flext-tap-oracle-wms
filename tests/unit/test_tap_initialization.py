"""Tap initialization behavior tests aligned with current tap contract.

Stream/catalog discovery and sync reach the external Oracle WMS Cloud (the
Singer SDK calls ``discover_streams`` at construction). With no local WMS
container those paths are covered by real end-to-end runs, not by mocking the
WMS client; the initialization contract is exercised by building the tap from
a real ``catalog`` input.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from flext_tests import tm

if TYPE_CHECKING:
    from flext_tap_oracle_wms import m


class TestsFlextTapOracleWmsTapInitialization:
    """Verify initialization and normalized settings without external I/O."""

    def test_tap_initialization_uses_normalized_config(
        self, sample_catalog: m.Meltano.SingerCatalog
    ) -> None:
        """Tap stores normalized settings values from settings serialization."""
        settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                "base_url": "https://test.example.com",
                "username": "test",
                "password": "test",
            }
        })
        tap = FlextTapOracleWms.from_settings(settings, catalog=sample_catalog)
        tm.that(str(tap.settings["base_url"]), has="test.example.com")
        tm.that(tap.settings["username"], eq="test")
