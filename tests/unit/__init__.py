# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import c, d, e, h, m, p, r, s, t, td, tf, tk, tm, tv, u, x

    from .test_cli import TestsFlextTapOracleWmsCli
    from .test_config import TestsFlextTapOracleWmsConfig
    from .test_config_validation import TestsFlextTapOracleWmsConfigValidation
    from .test_tap import TestsFlextTapOracleWmsTap
    from .test_tap_initialization import TestsFlextTapOracleWmsTapInitialization
__all__: tuple[str, ...] = (
    "TestsFlextTapOracleWmsCli",
    "TestsFlextTapOracleWmsConfig",
    "TestsFlextTapOracleWmsConfigValidation",
    "TestsFlextTapOracleWmsTap",
    "TestsFlextTapOracleWmsTapInitialization",
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
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".test_cli": ("TestsFlextTapOracleWmsCli",),
            ".test_config": ("TestsFlextTapOracleWmsConfig",),
            ".test_config_validation": ("TestsFlextTapOracleWmsConfigValidation",),
            ".test_tap": ("TestsFlextTapOracleWmsTap",),
            ".test_tap_initialization": ("TestsFlextTapOracleWmsTapInitialization",),
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
