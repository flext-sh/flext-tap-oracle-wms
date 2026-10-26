# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_oracle_wms import e
    from flext_tests import (
        api,
        config,
        d,
        h,
        install_local_packages,
        r,
        settings,
        td,
        tf,
        tk,
        tm,
        x,
    )

    from flext_tap_oracle_wms import cli, main, meltano, oracle_wms, tap_oracle_wms, web
    from tests.base import TestsFlextTapOracleWmsServiceBase, s
    from tests.constants import TestsFlextTapOracleWmsConstants, c
    from tests.helpers import TestsFlextTapOracleWmsHelpersMixin
    from tests.models import TestsFlextTapOracleWmsModels, m
    from tests.protocols import TestsFlextTapOracleWmsProtocols, p
    from tests.settings import TestsFlextTapOracleWmsSettings
    from tests.typings import TestsFlextTapOracleWmsTypes, t
    from tests.utilities import TestsFlextTapOracleWmsUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsHelpersMixin",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsServiceBase",
    "TestsFlextTapOracleWmsSettings",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "api",
    "c",
    "cli",
    "config",
    "d",
    "e",
    "h",
    "install_local_packages",
    "m",
    "main",
    "meltano",
    "oracle_wms",
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
    "web",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextTapOracleWmsConstants": ".constants",
        "TestsFlextTapOracleWmsHelpersMixin": ".helpers",
        "TestsFlextTapOracleWmsModels": ".models",
        "TestsFlextTapOracleWmsProtocols": ".protocols",
        "TestsFlextTapOracleWmsServiceBase": ".base",
        "TestsFlextTapOracleWmsSettings": ".settings",
        "TestsFlextTapOracleWmsTypes": ".typings",
        "TestsFlextTapOracleWmsUtilities": ".utilities",
        "api": "flext_tests",
        "c": ".constants",
        "cli": "flext_tap_oracle_wms",
        "config": "flext_tests",
        "d": "flext_tests",
        "e": "flext_oracle_wms",
        "h": "flext_tests",
        "install_local_packages": "flext_tests",
        "m": ".models",
        "main": "flext_tap_oracle_wms",
        "meltano": "flext_tap_oracle_wms",
        "oracle_wms": "flext_tap_oracle_wms",
        "p": ".protocols",
        "r": "flext_tests",
        "s": ".base",
        "settings": "flext_tests",
        "t": ".typings",
        "tap_oracle_wms": "flext_tap_oracle_wms",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "web": "flext_tap_oracle_wms",
        "x": "flext_tests",
    }),
    public_exports=__all__,
)
