# AUTO-GENERATED FILE — Regenerate with: make gen
"""Integration package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_functional": ("test_functional",),
        ".test_streams_functional": ("test_streams_functional",),
        ".test_wms": ("test_wms",),
        ".test_wms_connection": ("test_wms_connection",),
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
