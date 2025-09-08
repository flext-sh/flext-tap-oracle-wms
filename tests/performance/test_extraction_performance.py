"""Performance tests for FLEXT Tap Oracle WMS.

Tests extraction performance against real Oracle WMS environment.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import os
import time
from pathlib import Path

import psutil
import pytest
from dotenv import load_dotenv

from flext_tap_oracle_wms import FlextTapOracleWMS, FlextTapOracleWMSConfig

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


@pytest.fixture
def performance_config() -> FlextTapOracleWMSConfig:
    """Create configuration for performance testing."""
    return FlextTapOracleWMSConfig(
        base_url=os.getenv("ORACLE_WMS_BASE_URL"),
        username=os.getenv("ORACLE_WMS_USERNAME"),
        password=os.getenv("ORACLE_WMS_PASSWORD"),
        api_version=os.getenv("ORACLE_WMS_API_VERSION", "v10"),
        page_size=100,  # Standard page size for benchmarking
        verify_ssl=True,
        enable_rate_limiting=False,  # Disable for performance testing
    )


@pytest.fixture
def tap(performance_config: FlextTapOracleWMSConfig) -> FlextTapOracleWMS:
    """Create tap instance for performance testing."""
    return FlextTapOracleWMS(config=performance_config)


@pytest.mark.performance
class TestExtractionPerformance:
    """Test data extraction performance."""

    def test_discovery_performance(self, tap: FlextTapOracleWMS) -> None:
        """Benchmark catalog discovery time."""
        # Initialize tap
        tap.initialize()

        # Measure discovery time
        start_time = time.time()
        result = tap.discover_catalog()
        discovery_time = time.time() - start_time

        assert result.is_success

        # Performance assertion
        assert discovery_time < 10.0  # Should complete within 10 seconds

    @pytest.mark.parametrize("page_size", [10, 50, 100, 200])
    def test_pagination_performance(
        self,
        tap: FlextTapOracleWMS,
        page_size: int,
    ) -> None:
        """Benchmark different page sizes."""
        tap.initialize()

        # Configure page size
        tap.flext_config.page_size = page_size

        # Get inventory stream
        streams = tap.discover_streams()
        inventory_stream = next((s for s in streams if s.name == "inventory"), None)

        if not inventory_stream:
            pytest.skip("Inventory stream not available")

        inventory_stream._page_size = page_size

        # Extract records
        start_time = time.time()
        records = []

        for i, record in enumerate(inventory_stream.get_records(context=None)):
            records.append(record)
            if i >= 99:  # Extract 100 records
                break

        time.time() - start_time

    def test_concurrent_stream_extraction(self, tap: FlextTapOracleWMS) -> None:
        """Test extracting multiple streams concurrently."""
        tap.initialize()
        streams = tap.discover_streams()[:3]  # Test first 3 streams

        total_records = 0
        start_time = time.time()

        for stream in streams:
            stream_start = time.time()
            records = 0

            for i, _record in enumerate(stream.get_records(context=None)):
                records += 1
                if i >= 49:  # Extract 50 records per stream
                    break

            time.time() - stream_start
            total_records += records

        time.time() - start_time

    def test_memory_usage(self, tap: FlextTapOracleWMS) -> None:
        """Test memory usage during large extractions."""
        process = psutil.Process()

        # Initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Initialize and extract
        tap.initialize()
        streams = tap.discover_streams()

        if streams:
            stream = streams[0]
            records = []

            for i, record in enumerate(stream.get_records(context=None)):
                records.append(record)
                if i >= 999:  # Extract 1000 records
                    break

            # Final memory
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory should not increase too much
            assert memory_increase < 100  # Less than 100MB increase


@pytest.mark.performance
class TestRateLimitingPerformance:
    """Test rate limiting impact on performance."""

    def test_rate_limiting_impact(
        self,
        performance_config: FlextTapOracleWMSConfig,
    ) -> None:
        """Compare performance with and without rate limiting."""
        # Without rate limiting
        config_no_limit = FlextTapOracleWMSConfig(
            **performance_config.model_dump(),
            enable_rate_limiting=False,
        )
        tap_no_limit = FlextTapOracleWMS(config=config_no_limit)
        tap_no_limit.initialize()

        # With rate limiting
        config_with_limit = FlextTapOracleWMSConfig(
            **performance_config.model_dump(),
            enable_rate_limiting=True,
            max_requests_per_minute=60,
        )
        tap_with_limit = FlextTapOracleWMS(config=config_with_limit)
        tap_with_limit.initialize()

        # Test both
        for tap, _label in [(tap_no_limit, "No Limit"), (tap_with_limit, "With Limit")]:
            streams = tap.discover_streams()
            if streams:
                stream = streams[0]

                start_time = time.time()
                records = []

                for i, record in enumerate(stream.get_records(context=None)):
                    records.append(record)
                    if i >= 49:  # Extract 50 records
                        break

                time.time() - start_time


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "performance"])
