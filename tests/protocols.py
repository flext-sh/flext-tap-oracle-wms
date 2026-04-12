"""Test protocol definitions for flext-tap-oracle-wms.

Provides TestsFlextTapOracleWmsProtocols, combining TestsFlextProtocols with
FlextTapOracleWmsProtocols for test-specific protocol definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_tap_oracle_wms import FlextTapOracleWmsProtocols


class TestsFlextTapOracleWmsProtocols(FlextTestsProtocols, FlextTapOracleWmsProtocols):
    """Test protocols combining TestsFlextProtocols and FlextTapOracleWmsProtocols.

    Provides access to:
    - TestsFlextProtocols.Tests.Docker.* (from TestsFlextProtocols)
    - TestsFlextProtocols.Tests.Factory.* (from TestsFlextProtocols)
    - FlextTapOracleWmsProtocols.TapOracleWms.* (from FlextTapOracleWmsProtocols)
    """

    class TapOracleWms(FlextTapOracleWmsProtocols.TapOracleWms):
        """TapOracleWms-specific protocols."""

        class Tests:
            """Project-specific test protocols.

            Extends TestsFlextProtocols.Tests with TapOracleWms-specific protocols.
            """


p = TestsFlextTapOracleWmsProtocols
__all__: list[str] = ["TestsFlextTapOracleWmsProtocols", "p"]
