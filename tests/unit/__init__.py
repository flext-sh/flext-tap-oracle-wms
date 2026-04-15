# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_cli": ("test_cli",),
        ".test_config": ("test_config",),
        ".test_config_validation": ("test_config_validation",),
        ".test_tap": ("test_tap",),
        ".test_tap_initialization": ("test_tap_initialization",),
        "flext_tap_oracle_wms": (
            "c",
            "d",
            "e",
            "h",
            "m",
            "p",
            "r",
            "s",
            "t",
            "u",
            "x",
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
