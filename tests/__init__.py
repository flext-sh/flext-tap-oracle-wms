# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli import cli
    from flext_meltano import meltano
    from flext_oracle_wms import e, oracle_wms
    from flext_tests import (
        active_rules,
        api,
        config,
        discover_repository_root,
        install_local_packages,
        load_infra_report,
        settings,
        split_csv,
        td,
        tf,
        tk,
        tm,
        tv,
    )
    from flext_web import web

    from flext_core import core, d, h, lazy_attribute, r, x
    from flext_tap_oracle_wms import main, tap_oracle_wms

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
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsServiceBase",
    "TestsFlextTapOracleWmsSettings",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "active_rules",
    "api",
    "c",
    "cli",
    "config",
    "core",
    "d",
    "discover_repository_root",
    "e",
    "e2e",
    "h",
    "install_local_packages",
    "integration",
    "lazy_attribute",
    "load_infra_report",
    "m",
    "main",
    "meltano",
    "oracle_wms",
    "p",
    "performance",
    "r",
    "s",
    "settings",
    "split_csv",
    "t",
    "tap_oracle_wms",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "unit",
    "web",
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
            "flext_cli": ("cli",),
            "flext_core": ("core", "d", "h", "lazy_attribute", "r", "x"),
            "flext_meltano": ("meltano",),
            "flext_oracle_wms": ("e", "oracle_wms"),
            "flext_tap_oracle_wms": ("main", "tap_oracle_wms"),
            "flext_tests": (
                "active_rules",
                "api",
                "config",
                "discover_repository_root",
                "install_local_packages",
                "load_infra_report",
                "settings",
                "split_csv",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
            ),
            "flext_web": ("web",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
