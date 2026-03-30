# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Performance tests for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.performance import (
        test_extraction_performance as test_extraction_performance,
    )
    from tests.performance.test_extraction_performance import (
        TestExtractionPerformance as TestExtractionPerformance,
        TestRateLimitingPerformance as TestRateLimitingPerformance,
        env_path as env_path,
        performance_config as performance_config,
        tap as tap,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestExtractionPerformance": [
        "tests.performance.test_extraction_performance",
        "TestExtractionPerformance",
    ],
    "TestRateLimitingPerformance": [
        "tests.performance.test_extraction_performance",
        "TestRateLimitingPerformance",
    ],
    "env_path": ["tests.performance.test_extraction_performance", "env_path"],
    "performance_config": [
        "tests.performance.test_extraction_performance",
        "performance_config",
    ],
    "tap": ["tests.performance.test_extraction_performance", "tap"],
    "test_extraction_performance": [
        "tests.performance.test_extraction_performance",
        "",
    ],
}

_EXPORTS: Sequence[str] = [
    "TestExtractionPerformance",
    "TestRateLimitingPerformance",
    "env_path",
    "performance_config",
    "tap",
    "test_extraction_performance",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
