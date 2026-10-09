"""Runtime settings for flext-tap-oracle-wms tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
tests/settings
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsSettings

from flext_tap_oracle_wms._settings import FlextTapOracleWmsSettings


class TestsFlextTapOracleWmsSettings(FlextTapOracleWmsSettings, FlextTestsSettings):
    """Tap Oracle WMS settings extended with the shared test namespace."""


__all__: list[str] = ["TestsFlextTapOracleWmsSettings"]
