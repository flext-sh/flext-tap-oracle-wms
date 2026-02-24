"""Test protocol definitions for flext-tap-oracle-wms.

Provides TestsFlextTapOracleWmsProtocols, combining FlextTestsProtocols with
FlextTapOracleWmsProtocols for test-specific protocol definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols
from flext_tests.protocols import FlextTestsProtocols


class TestsFlextTapOracleWmsProtocols(FlextTestsProtocols, FlextTapOracleWmsProtocols):
    """Test protocols combining FlextTestsProtocols and FlextTapOracleWmsProtocols.

    Provides access to:
    - p.Tests.Docker.* (from FlextTestsProtocols)
    - p.Tests.Factory.* (from FlextTestsProtocols)
    - p.TapOracleWms.* (from FlextTapOracleWmsProtocols)
    """

    class TapOracleWms(FlextTapOracleWmsProtocols.TapOracleWms):
        """TapOracleWms-specific protocols."""

        class Tests:
            """Project-specific test protocols.

            Extends FlextTestsProtocols.Tests with TapOracleWms-specific protocols.
            """


# Runtime aliases
p = TestsFlextTapOracleWmsProtocols
p = TestsFlextTapOracleWmsProtocols

__all__ = ["TestsFlextTapOracleWmsProtocols", "p", "p"]
