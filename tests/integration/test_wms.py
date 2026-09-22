"""Simple integration test for Oracle WMS connection.

Tests basic connectivity without complex dependencies.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from itertools import islice

import pytest
from flext_tests import tm

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.tap import FlextTapOracleWms

_RECORD_SAMPLE_LIMIT = 2


@pytest.mark.integration
class TestsFlextTapOracleWmsWms:
    """Test real Oracle WMS integration."""

    def test_tap_creation_with_real_config(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Test tap can be created with real settings."""
        tap = FlextTapOracleWms.from_settings(real_config)
        tm.that(tap, none=False)
        tm.that(tap.name, eq=FlextTapOracleWms.name)

    def test_configuration_validation(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Validation exposes exactly the non-secret configured fields."""
        tap = FlextTapOracleWms.from_settings(real_config)
        result = tap.validate_configuration()
        tm.ok(result)
        value = result.value
        assert isinstance(value, Mapping)
        tm.that(set(value), eq={"base_url", "api_version", "page_size"})

    def test_tap_initialization(self, real_config: FlextTapOracleWmsSettings) -> None:
        """Test tap initialization."""
        tap = FlextTapOracleWms.from_settings(real_config)
        result = tap.initialize()
        tm.ok(result)

    def test_stream_discovery(self, real_config: FlextTapOracleWmsSettings) -> None:
        """Test stream discovery."""
        tap = FlextTapOracleWms.from_settings(real_config)
        init_result = tap.initialize()
        tm.ok(init_result)
        streams = tap.discover_streams()
        tm.that(bool(streams), eq=True)
        for stream in streams:
            tm.that(stream.name, none=False)

    def test_stream_extraction(self, real_config: FlextTapOracleWmsSettings) -> None:
        """Exercise every discovered stream without suppressing extraction failures."""
        tap = FlextTapOracleWms.from_settings(real_config)
        init_result = tap.initialize()
        tm.ok(init_result)
        streams = tap.discover_streams()
        tm.that(bool(streams), eq=True)
        for stream in streams:
            records = list(
                islice(stream.get_records(context=None), _RECORD_SAMPLE_LIMIT)
            )
            for record in records:
                tm.that(record, is_=Mapping)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
