# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_oracle_wms import e
    from flext_tests import api, d, h, r, td, tf, tk, tm, x

    from flext_tap_oracle_wms import config, main, settings, tap_oracle_wms
    from tests.base import TestsFlextTapOracleWmsServiceBase, s
    from tests.constants import TestsFlextTapOracleWmsConstants, c
    from tests.helpers import TestsFlextTapOracleWmsHelpers
    from tests.models import TestsFlextTapOracleWmsModels, m
    from tests.protocols import TestsFlextTapOracleWmsProtocols, p
    from tests.settings import TestsFlextTapOracleWmsSettings
    from tests.typings import TestsFlextTapOracleWmsTypes, t
    from tests.utilities import TestsFlextTapOracleWmsUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsHelpers",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsServiceBase",
    "TestsFlextTapOracleWmsSettings",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "api",
    "c",
    "config",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "tap_oracle_wms",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "TestsFlextTapOracleWmsConstants": ".constants",
        "TestsFlextTapOracleWmsHelpers": ".helpers",
        "TestsFlextTapOracleWmsModels": ".models",
        "TestsFlextTapOracleWmsProtocols": ".protocols",
        "TestsFlextTapOracleWmsServiceBase": ".base",
        "TestsFlextTapOracleWmsSettings": ".settings",
        "TestsFlextTapOracleWmsTypes": ".typings",
        "TestsFlextTapOracleWmsUtilities": ".utilities",
        "api": "flext_tests",
        "c": ".constants",
        "config": "flext_tap_oracle_wms",
        "d": "flext_tests",
        "e": "flext_oracle_wms",
        "h": "flext_tests",
        "m": ".models",
        "main": "flext_tap_oracle_wms",
        "p": ".protocols",
        "r": "flext_tests",
        "s": ".base",
        "settings": "flext_tap_oracle_wms",
        "t": ".typings",
        "tap_oracle_wms": "flext_tap_oracle_wms",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "x": "flext_tests",
    },
    public_exports=__all__,
)
