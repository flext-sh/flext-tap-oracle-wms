"""Service base for flext-tap-oracle-wms tests."""

from __future__ import annotations

from typing import override

from flext_tap_oracle_wms import m
from flext_tests import s as tests_s
from tests.settings import TestsFlextTapOracleWmsSettings


class TestsFlextTapOracleWmsServiceBase(tests_s):
    """Tap Oracle WMS test service base with source and test settings namespaces."""

    # NOTE (multi-agent): flext-tests owns fetch_settings; this project
    # declares only its more-specific bootstrap settings type.
    @classmethod
    @override
    def _runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextTapOracleWmsSettings)


s = TestsFlextTapOracleWmsServiceBase

__all__: list[str] = ["TestsFlextTapOracleWmsServiceBase", "s"]
