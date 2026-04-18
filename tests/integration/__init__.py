# AUTO-GENERATED FILE — Regenerate with: make gen
"""Integration package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_functional": ("TestOracleWMSFunctionalComplete",),
        ".test_streams_functional": ("TestStreamsFunctional",),
        ".test_wms": ("TestRealWmsIntegration",),
        ".test_wms_connection": (
            "TestFilteringAndSelection",
            "TestIntegration",
            "TestRealConnection",
            "TestRealDataExtraction",
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
