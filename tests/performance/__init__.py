# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.performance package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import c, d, e, h, m, p, r, s, t, td, tf, tk, tm, tv, u, x

    from .test_extraction_performance import (
        TestsFlextTapOracleWmsExtractionPerformance,
        env_path,
        performance_config,
        tap,
    )
__all__: tuple[str, ...] = (
    "TestsFlextTapOracleWmsExtractionPerformance",
    "c",
    "d",
    "e",
    "env_path",
    "h",
    "m",
    "p",
    "performance_config",
    "r",
    "s",
    "t",
    "tap",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".test_extraction_performance": (
                "TestsFlextTapOracleWmsExtractionPerformance",
                "env_path",
                "performance_config",
                "tap",
            ),
            "flext_tests": (
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
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
