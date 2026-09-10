# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_oracle_wms import FlextTapOracleWmsConstants
    from flext_tests import FlextTestsConstants, d, e, h, r, td, tf, tk, tm, tv, x

    from . import e2e, integration, performance, unit
    from .base import (
        TestsFlextTapOracleWmsServiceBase,
        TestsFlextTapOracleWmsServiceBase as s,
    )
    from .constants import (
        TestsFlextTapOracleWmsConstants,
        TestsFlextTapOracleWmsConstants as c,
    )
    from .models import TestsFlextTapOracleWmsModels, TestsFlextTapOracleWmsModels as m
    from .protocols import (
        TestsFlextTapOracleWmsProtocols,
        TestsFlextTapOracleWmsProtocols as p,
    )
    from .settings import TestsFlextTapOracleWmsSettings
    from .typings import TestsFlextTapOracleWmsTypes, TestsFlextTapOracleWmsTypes as t
    from .utilities import (
        TestsFlextTapOracleWmsUtilities,
        TestsFlextTapOracleWmsUtilities as u,
    )
__all__: tuple[str, ...] = (
    "FlextTapOracleWmsConstants",
    "FlextTestsConstants",
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsServiceBase",
    "TestsFlextTapOracleWmsSettings",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
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
    "tv",
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
            "flext_tap_oracle_wms": ("FlextTapOracleWmsConstants",),
            "flext_tests": (
                "FlextTestsConstants",
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
