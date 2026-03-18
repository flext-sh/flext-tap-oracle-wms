"""Test protocol definitions for flext-tap-oracle-wms.

Provides TestsFlextTapOracleWmsProtocols, combining p with
FlextTapOracleWmsProtocols for test-specific protocol definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import p

from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols


class TestsFlextTapOracleWmsProtocols(p, FlextTapOracleWmsProtocols):
    """Test protocols combining p and FlextTapOracleWmsProtocols.

    Provides access to:
    - p.Tests.Docker.* (from p)
    - p.Tests.Factory.* (from p)
    - p.TapOracleWms.* (from FlextTapOracleWmsProtocols)
    """

    class TapOracleWms(FlextTapOracleWmsProtocols.TapOracleWms):
        """TapOracleWms-specific protocols."""

        class Tests:
            """Project-specific test protocols.

            Extends p.Tests with TapOracleWms-specific protocols.
            """


__all__ = ["TestsFlextTapOracleWmsProtocols", "p"]

p = TestsFlextTapOracleWmsProtocols
