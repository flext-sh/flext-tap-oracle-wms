# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_tests import td, tf, tk, tm, tv

    from flext_tap_oracle_wms import d, e, h, r, s, x
    from tests.constants import TestsFlextTapOracleWmsConstants, c
    from tests.models import TestsFlextTapOracleWmsModels, m
    from tests.protocols import TestsFlextTapOracleWmsProtocols, p
    from tests.typings import TestsFlextTapOracleWmsTypes, t
    from tests.utilities import TestsFlextTapOracleWmsUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".integration",
        ".performance",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".constants": (
                "TestsFlextTapOracleWmsConstants",
                "c",
            ),
            ".models": (
                "TestsFlextTapOracleWmsModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextTapOracleWmsProtocols",
                "p",
            ),
            ".typings": (
                "TestsFlextTapOracleWmsTypes",
                "t",
            ),
            ".utilities": (
                "TestsFlextTapOracleWmsUtilities",
                "u",
            ),
            "flext_tap_oracle_wms": (
                "d",
                "e",
                "h",
                "r",
                "s",
                "x",
            ),
            "flext_tests": (
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
            ),
        },
    ),
    exclude_names=(
        "FlextDispatcher",
        "FlextLogger",
        "FlextRegistry",
        "FlextRuntime",
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
]
