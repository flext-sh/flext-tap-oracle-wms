"""Runtime settings for flext-tap-oracle-wms tests."""

from __future__ import annotations

from typing import ClassVar

from flext_tests import FlextTestsSettings

from flext_tap_oracle_wms import FlextTapOracleWmsSettings, m


class TestsFlextTapOracleWmsSettings(FlextTapOracleWmsSettings, FlextTestsSettings):
    """Tap Oracle WMS settings extended with the shared test namespace."""

    model_config: ClassVar[m.SettingsConfigDict]


__all__: list[str] = ["TestsFlextTapOracleWmsSettings"]
