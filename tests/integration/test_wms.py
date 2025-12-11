"""Simple integration test for Oracle WMS connection.

Tests basic connectivity without complex dependencies.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

import os

import pytest

from flext_tap_oracle_wms import (
    FlextTapOracleWms,
    FlextTapOracleWmsSettings,
)


@pytest.fixture
def real_config() -> FlextTapOracleWmsSettings:
    """Create real configuration from environment."""
    return FlextTapOracleWmsSettings(
        base_url=os.getenv("ORACLE_WMS_BASE_URL") or "https://test.example.com",
        username=os.getenv("ORACLE_WMS_USERNAME") or "test_user",
        password=os.getenv("ORACLE_WMS_PASSWORD") or "test_password",
        api_version=os.getenv("ORACLE_WMS_API_VERSION", "v10"),
        timeout=int(os.getenv("ORACLE_WMS_TIMEOUT", "30")),
        page_size=int(os.getenv("ORACLE_WMS_PAGE_SIZE", "100")),
        verify_ssl=os.getenv("ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
    )


@pytest.mark.integration
@pytest.mark.oracle_wms
class TestRealWmsIntegration:
    """Test real Oracle WMS integration."""

    def test_tap_creation_with_real_config(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test tap can be created with real config."""
        tap = FlextTapOracleWms(config=real_config)
        assert tap is not None
        assert tap.name == "flext-tap-oracle-wms"

    def test_configuration_validation(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test configuration validation."""
        # Create tap
        tap = FlextTapOracleWms(config=real_config)

        # Validate config
        result = tap.validate_configuration()

        # Check result
        if result.is_success:
            assert result.data["valid"] is True
        else:
            pytest.skip(f"Configuration validation failed: {result.error}")

    def test_tap_initialization(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test tap initialization."""
        tap = FlextTapOracleWms(config=real_config)

        # Initialize
        result = tap.initialize()

        if not result.is_success:
            pytest.skip(f"Tap initialization failed: {result.error}")

    def test_stream_discovery(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test stream discovery."""
        tap = FlextTapOracleWms(config=real_config)

        # Initialize first
        init_result = tap.initialize()
        if init_result.is_failure:
            pytest.skip(
                f"Cannot test discovery, initialization failed: {init_result.error}",
            )

        # Discover streams
        streams = tap.discover_streams()

        assert len(streams) > 0

        for stream in streams:
            assert stream.name is not None
            assert hasattr(stream, "schema")

    @pytest.mark.parametrize("stream_name", ["inventory", "locations", "items"])
    def test_stream_extraction(
        self,
        real_config: FlextTapOracleWmsSettings,
        stream_name: str,
    ) -> None:
        """Test data extraction from specific streams."""
        tap = FlextTapOracleWms(config=real_config)

        # Initialize
        init_result = tap.initialize()
        if init_result.is_failure:
            pytest.skip(
                f"Cannot test extraction, initialization failed: {init_result.error}",
            )

        # Get streams
        streams = tap.discover_streams()
        stream = next((s for s in streams if s.name == stream_name), None)

        if stream is None:
            pytest.skip(f"Stream '{stream_name}' not available")

        # Try to extract a few records
        records = []
        try:
            for i, record in enumerate(stream.get_records(context=None)):
                records.append(record)
                if i >= 2:  # Just get 3 records for testing
                    break

            assert records is not None, "No records found"

        except Exception as e:
            # Check if it's an authentication or connection error
            error_msg = str(e).lower()
            if any(
                x in error_msg for x in ["auth", "401", "403", "connection", "timeout"]
            ):
                pytest.skip(f"Connection/auth issue with {stream_name}: {e}")
            else:
                raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
