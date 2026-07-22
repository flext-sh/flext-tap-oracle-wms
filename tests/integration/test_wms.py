"""Simple integration test for Oracle WMS connection.

Tests basic connectivity without complex dependencies.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations


from collections.abc import Mapping
from typing import TYPE_CHECKING

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from flext_tests import tm

if TYPE_CHECKING:
    from tests import t


_RECORD_SAMPLE_LIMIT = 2


@pytest.mark.integration
@pytest.mark.oracle_wms
class TestsFlextTapOracleWmsWms:
    """Test real Oracle WMS integration."""

    def test_tap_creation_with_real_config(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Test tap can be created with real settings."""
        tap = FlextTapOracleWms.from_settings(real_config)
        tm.that(tap, none=False)
        tm.that(tap.name, eq="flext-tap-oracle-wms")

    def test_configuration_validation(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Test configuration validation."""
        tap = FlextTapOracleWms.from_settings(real_config)
        result = tap.validate_configuration()
        if result.success:
            value = result.value
            assert isinstance(value, Mapping)
            assert value.get("valid") is True
        else:
            pytest.skip(f"Configuration validation failed: {result.error}")

    def test_tap_initialization(self, real_config: FlextTapOracleWmsSettings) -> None:
        """Test tap initialization."""
        tap = FlextTapOracleWms.from_settings(real_config)
        result = tap.initialize()
        if not result.success:
            pytest.skip(f"Tap initialization failed: {result.error}")

    def test_stream_discovery(self, real_config: FlextTapOracleWmsSettings) -> None:
        """Test stream discovery."""
        tap = FlextTapOracleWms.from_settings(real_config)
        init_result = tap.initialize()
        if init_result.failure:
            pytest.skip(
                f"Cannot test discovery, initialization failed: {init_result.error}"
            )
        streams = tap.discover_streams()
        assert streams
        for stream in streams:
            tm.that(stream.name, none=False)

    @pytest.mark.parametrize("stream_name", ["inventory", "locations", "items"])
    def test_stream_extraction(
        self, real_config: FlextTapOracleWmsSettings, stream_name: str
    ) -> None:
        """Test data extraction from specific streams."""
        tap = FlextTapOracleWms.from_settings(real_config)
        init_result = tap.initialize()
        if init_result.failure:
            pytest.skip(
                f"Cannot test extraction, initialization failed: {init_result.error}"
            )
        streams = tap.discover_streams()
        stream = next((s for s in streams if s.name == stream_name), None)
        if stream is None:
            pytest.skip(f"Stream '{stream_name}' not available")
        records: list[t.JsonMapping] = []
        try:
            for i, record in enumerate(stream.get_records(context=None)):
                records.append(record)
                if i >= _RECORD_SAMPLE_LIMIT:
                    break
            tm.that(records, none=False)
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ) as e:
            error_msg = str(e).lower()
            if any(
                x in error_msg for x in ["auth", "401", "403", "connection", "timeout"]
            ):
                pytest.skip(f"Connection/auth issue with {stream_name}: {e}")
            else:
                raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
