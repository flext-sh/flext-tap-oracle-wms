"""Test protocol definitions for flext-tap-oracle-wms.

Provides FlextTapOracleWmsTestProtocols, combining FlextTestsProtocols with
FlextTapOracleWmsProtocols for test-specific protocol definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_tap_oracle_wms import FlextTapOracleWmsProtocols


class FlextTapOracleWmsTestProtocols(FlextTestsProtocols, FlextTapOracleWmsProtocols):
    """Test protocols combining FlextTestsProtocols and FlextTapOracleWmsProtocols.

    Provides access to:
    - FlextTestsProtocols.Tests.Docker.* (from FlextTestsProtocols)
    - FlextTestsProtocols.Tests.Factory.* (from FlextTestsProtocols)
    - FlextTapOracleWmsProtocols.TapOracleWms.* (from FlextTapOracleWmsProtocols)
    """

    class TapOracleWms(FlextTapOracleWmsProtocols.TapOracleWms):
        """TapOracleWms-specific protocols."""

        class Tests:
            """Project-specific test protocols.

            Extends FlextTestsProtocols.Tests with TapOracleWms-specific protocols.
            """


p = FlextTapOracleWmsTestProtocols
__all__ = ["FlextTapOracleWmsTestProtocols", "p"]
