# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Performance tests for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from tests.performance.test_extraction_performance import (
        TestExtractionPerformance,
        TestRateLimitingPerformance,
        env_path,
        performance_config,
        tap,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestExtractionPerformance": ("tests.performance.test_extraction_performance", "TestExtractionPerformance"),
    "TestRateLimitingPerformance": ("tests.performance.test_extraction_performance", "TestRateLimitingPerformance"),
    "env_path": ("tests.performance.test_extraction_performance", "env_path"),
    "performance_config": ("tests.performance.test_extraction_performance", "performance_config"),
    "tap": ("tests.performance.test_extraction_performance", "tap"),
}

__all__ = [
    "TestExtractionPerformance",
    "TestRateLimitingPerformance",
    "env_path",
    "performance_config",
    "tap",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
