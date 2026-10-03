# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

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

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextTapOracleWmsServiceBase", "s"),
            ".constants": ("TestsFlextTapOracleWmsConstants", "c"),
            ".e2e": ("e2e",),
            ".integration": ("integration",),
            ".models": ("TestsFlextTapOracleWmsModels", "m"),
            ".performance": ("performance",),
            ".protocols": ("TestsFlextTapOracleWmsProtocols", "p"),
            ".settings": ("TestsFlextTapOracleWmsSettings",),
            ".typings": ("TestsFlextTapOracleWmsTypes", "t"),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextTapOracleWmsUtilities", "u"),
            "flext_oracle_wms": ("e",),
            "flext_tests": ("api", "d", "h", "r", "td", "tf", "tk", "tm", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
