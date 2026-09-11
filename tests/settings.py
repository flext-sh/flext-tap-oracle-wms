"""Runtime settings for flext-tap-oracle-wms tests."""

from __future__ import annotations

from flext_tests import FlextTestsSettings

from flext_tap_oracle_wms import FlextTapOracleWmsSettings


class TestsFlextTapOracleWmsSettings(FlextTapOracleWmsSettings, FlextTestsSettings):
    """Tap Oracle WMS settings extended with the shared test namespace."""


__all__: list[str] = ["TestsFlextTapOracleWmsSettings"]
