"""Service base for flext-tap-oracle-wms tests."""

from __future__ import annotations

from typing import override

from flext_tests import s as tests_s

from flext_tap_oracle_wms import m
from tests.settings import TestsFlextTapOracleWmsSettings


class TestsFlextTapOracleWmsServiceBase(tests_s):
    """Tap Oracle WMS test service base with source and test settings namespaces."""

    @classmethod
    @override
    def fetch_settings(cls) -> TestsFlextTapOracleWmsSettings:
        """Return the typed Tap Oracle WMS+Tests settings singleton."""
        return TestsFlextTapOracleWmsSettings.fetch_global()

    @classmethod
    @override
    def _runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextTapOracleWmsSettings)


s = TestsFlextTapOracleWmsServiceBase

__all__: list[str] = ["TestsFlextTapOracleWmsServiceBase", "s"]
