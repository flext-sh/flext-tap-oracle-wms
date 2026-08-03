# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map({
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
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
