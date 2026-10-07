# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_oracle_wms import e
    from flext_tests import api, d, h, r, td, tf, tk, tm, x

    from tests import e2e, integration, performance, unit
    from tests.base import TestsFlextTapOracleWmsServiceBase, s
    from tests.constants import TestsFlextTapOracleWmsConstants, c
    from tests.models import TestsFlextTapOracleWmsModels, m
    from tests.protocols import TestsFlextTapOracleWmsProtocols, p
    from tests.settings import TestsFlextTapOracleWmsSettings
    from tests.typings import TestsFlextTapOracleWmsTypes, t
    from tests.utilities import TestsFlextTapOracleWmsUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsServiceBase",
    "TestsFlextTapOracleWmsSettings",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "api",
    "c",
    "d",
    "e",
    "e2e",
    "h",
    "integration",
    "m",
    "p",
    "performance",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "unit",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextTapOracleWmsConstants": ".constants",
        "TestsFlextTapOracleWmsModels": ".models",
        "TestsFlextTapOracleWmsProtocols": ".protocols",
        "TestsFlextTapOracleWmsServiceBase": ".base",
        "TestsFlextTapOracleWmsSettings": ".settings",
        "TestsFlextTapOracleWmsTypes": ".typings",
        "TestsFlextTapOracleWmsUtilities": ".utilities",
        "api": "flext_tests",
        "c": ".constants",
        "d": "flext_tests",
        "e": "flext_oracle_wms",
        "e2e": ".e2e",
        "h": "flext_tests",
        "integration": ".integration",
        "m": ".models",
        "p": ".protocols",
        "performance": ".performance",
        "r": "flext_tests",
        "s": ".base",
        "t": ".typings",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "unit": ".unit",
        "x": "flext_tests",
    }),
    public_exports=__all__,
)
