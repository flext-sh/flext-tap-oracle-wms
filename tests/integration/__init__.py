# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Integration tests for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from tests.integration.test_functional import TestOracleWMSFunctionalComplete
    from tests.integration.test_streams_functional import (
        TestStreamsFunctional,
        TestWMSPaginatorUnit,
        logger,
    )
    from tests.integration.test_wms import TestRealWmsIntegration
    from tests.integration.test_wms_connection import (
        TestFilteringAndSelection,
        TestIntegration,
        TestRealConnection,
        TestRealDataExtraction,
        env_path,
        real_config,
        tap,
    )

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestFilteringAndSelection": (
        "tests.integration.test_wms_connection",
        "TestFilteringAndSelection",
    ),
    "TestIntegration": ("tests.integration.test_wms_connection", "TestIntegration"),
    "TestOracleWMSFunctionalComplete": (
        "tests.integration.test_functional",
        "TestOracleWMSFunctionalComplete",
    ),
    "TestRealConnection": (
        "tests.integration.test_wms_connection",
        "TestRealConnection",
    ),
    "TestRealDataExtraction": (
        "tests.integration.test_wms_connection",
        "TestRealDataExtraction",
    ),
    "TestRealWmsIntegration": ("tests.integration.test_wms", "TestRealWmsIntegration"),
    "TestStreamsFunctional": (
        "tests.integration.test_streams_functional",
        "TestStreamsFunctional",
    ),
    "TestWMSPaginatorUnit": (
        "tests.integration.test_streams_functional",
        "TestWMSPaginatorUnit",
    ),
    "env_path": ("tests.integration.test_wms_connection", "env_path"),
    "logger": ("tests.integration.test_streams_functional", "logger"),
    "real_config": ("tests.integration.test_wms_connection", "real_config"),
    "tap": ("tests.integration.test_wms_connection", "tap"),
}

__all__ = [
    "TestFilteringAndSelection",
    "TestIntegration",
    "TestOracleWMSFunctionalComplete",
    "TestRealConnection",
    "TestRealDataExtraction",
    "TestRealWmsIntegration",
    "TestStreamsFunctional",
    "TestWMSPaginatorUnit",
    "env_path",
    "logger",
    "real_config",
    "tap",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
