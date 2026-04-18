# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_cli": ("TestCLI",),
        ".test_config": ("TestFlextTapOracleWmsSettings",),
        ".test_config_validation": ("TestConfigValidation",),
        ".test_tap": ("TestFlextTapOracleWms",),
        ".test_tap_initialization": ("TestTapInitialization",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
