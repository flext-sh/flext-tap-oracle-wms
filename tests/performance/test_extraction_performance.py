"""Performance tests for Oracle WMS extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

import psutil

from flext_tap_oracle_wms import FlextTapOracleWms, FlextTapOracleWmsSettings
from tests import TestsFlextTapOracleWmsHelpers, c, t, tm, u

_MAX_DISCOVERY_SECONDS = 10.0
_LARGE_EXTRACTION_SAMPLE_LIMIT = 999
_MAX_MEMORY_INCREASE_MB = 100


@u.Tests.fixture
def performance_config(
    real_config: FlextTapOracleWmsSettings,
) -> FlextTapOracleWmsSettings:
    """Create configuration for performance testing based on real config.

    Returns:
        The resulting ``FlextTapOracleWmsSettings``.

    """
    base = real_config.TapOracleWms.model_dump()
    base.update({
        "page_size": 100,
        "verify_ssl": True,
        "enable_rate_limiting": False,
    })
    return FlextTapOracleWmsSettings.model_validate({"TapOracleWms": base})


@u.Tests.fixture
def tap(performance_config: FlextTapOracleWmsSettings) -> FlextTapOracleWms:
    """Create tap instance for performance testing.

    Returns:
        The resulting ``FlextTapOracleWms``.

    """
    return FlextTapOracleWms.from_settings(performance_config)


@c.Tests.MARK.performance
class TestsFlextTapOracleWmsExtractionPerformance(TestsFlextTapOracleWmsHelpers):
    """Test data extraction performance."""

    @staticmethod
    def test_catalog_discovery_performance(tap: FlextTapOracleWms) -> None:
        """Benchmark catalog discovery time."""
        tap.initialize()
        start_time = time.time()
        result = tap.discovercatalog_typed()
        discovery_time = time.time() - start_time
        tm.ok(result)
        tm.that(discovery_time, lt=_MAX_DISCOVERY_SECONDS)

    @staticmethod
    def test_memory_usage_during_large_extraction(tap: FlextTapOracleWms) -> None:
        """Test memory usage during large extractions."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        tap.initialize()
        streams = tap.discover_streams()
        if streams:
            stream = streams[0]
            records: list[t.JsonMapping] = []
            for i, record in enumerate(stream.get_records(context=None)):
                records.append(record)
                if i >= _LARGE_EXTRACTION_SAMPLE_LIMIT:
                    break
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory
            tm.that(memory_increase, lt=_MAX_MEMORY_INCREASE_MB)


if __name__ == "__main__":
    u.Tests.main([__file__, "-v", "-s", "-m", "performance"])
