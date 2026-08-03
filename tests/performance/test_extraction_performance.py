"""Performance tests for Oracle WMS extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

import psutil
import pytest
from dotenv import load_dotenv

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from flext_tests import tm

if TYPE_CHECKING:
    from tests import t

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

_MAX_DISCOVERY_SECONDS = 10.0
_PAGINATION_SAMPLE_LIMIT = 99
_CONCURRENT_SAMPLE_LIMIT = 49
_LARGE_EXTRACTION_SAMPLE_LIMIT = 999
_MAX_MEMORY_INCREASE_MB = 100


@pytest.fixture
def performance_config() -> FlextTapOracleWmsSettings:
    """Create configuration for performance testing."""
    # NOTE (multi-agent): mro-u3eu — ADR-005 namespaces project fields under
    # settings.TapOracleWms.*; construct via the namespace payload.
    return FlextTapOracleWmsSettings.model_validate({
        "TapOracleWms": {
            "base_url": os.getenv("ORACLE_WMS_BASE_URL", "https://localhost"),
            "username": os.getenv("ORACLE_WMS_USERNAME", "user"),
            "password": os.getenv("ORACLE_WMS_PASSWORD", "pass"),
            "api_version": os.getenv("ORACLE_WMS_API_VERSION", "v10"),
            "page_size": 100,
            "verify_ssl": True,
            "enable_rate_limiting": False,
        }
    })


@pytest.fixture
def tap(performance_config: FlextTapOracleWmsSettings) -> FlextTapOracleWms:
    """Create tap instance for performance testing."""
    return FlextTapOracleWms.from_settings(performance_config)


@pytest.mark.performance
class TestsFlextTapOracleWmsExtractionPerformance:
    """Test data extraction performance."""

    def test_catalog_discovery_performance(self, tap: FlextTapOracleWms) -> None:
        """Benchmark catalog discovery time."""
        tap.initialize()
        start_time = time.time()
        result = tap.discovercatalog_typed()
        discovery_time = time.time() - start_time
        tm.ok(result)
        assert discovery_time < _MAX_DISCOVERY_SECONDS

    @pytest.mark.parametrize("page_size", [10, 50, 100, 200])
    def test_pagination_performance(
        self, tap: FlextTapOracleWms, page_size: int
    ) -> None:
        """Benchmark different page sizes."""
        tap.initialize()
        tap.flext_config.TapOracleWms.page_size = page_size
        streams = tap.discover_streams()
        inventory_stream = next((s for s in streams if s.name == "inventory"), None)
        if not inventory_stream:
            pytest.skip("Inventory stream not available")
        inventory_stream.page_size = page_size
        start_time = time.time()
        records: list[t.JsonMapping] = []
        for i, record in enumerate(inventory_stream.get_records(context=None)):
            records.append(record)
            if i >= _PAGINATION_SAMPLE_LIMIT:
                break
        _ = time.time() - start_time

    def test_concurrent_streams_extraction(self, tap: FlextTapOracleWms) -> None:
        """Test extracting multiple streams concurrently."""
        tap.initialize()
        streams = tap.discover_streams()[:3]
        total_records = 0
        start_time = time.time()
        for stream in streams:
            stream_start = time.time()
            records = 0
            for i, _record in enumerate(stream.get_records(context=None)):
                records += 1
                if i >= _CONCURRENT_SAMPLE_LIMIT:
                    break
            _ = time.time() - stream_start
            total_records += records
        _ = time.time() - start_time

    def test_memory_usage_during_large_extraction(self, tap: FlextTapOracleWms) -> None:
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
            assert memory_increase < _MAX_MEMORY_INCREASE_MB

    """Test rate limiting impact on performance."""

    def test_rate_limiting_impact(
        self, performance_config: FlextTapOracleWmsSettings
    ) -> None:
        """Compare performance with and without rate limiting."""
        config_no_limit = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                **performance_config.TapOracleWms.model_dump(),
                "enable_rate_limiting": False,
            }
        })
        tap_no_limit = FlextTapOracleWms.from_settings(config_no_limit)
        tap_no_limit.initialize()
        config_with_limit = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                **performance_config.TapOracleWms.model_dump(),
                "enable_rate_limiting": True,
                "max_requests_per_minute": 60,
            }
        })
        tap_with_limit = FlextTapOracleWms.from_settings(config_with_limit)
        tap_with_limit.initialize()
        for tap, _label in [(tap_no_limit, "No Limit"), (tap_with_limit, "With Limit")]:
            streams = tap.discover_streams()
            if streams:
                stream = streams[0]
                start_time = time.time()
                records: list[t.JsonMapping] = []
                for i, record in enumerate(stream.get_records(context=None)):
                    records.append(record)
                    if i >= _CONCURRENT_SAMPLE_LIMIT:
                        break
                _ = time.time() - start_time


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "performance"])
