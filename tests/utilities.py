"""Utilities for flext-tap-oracle-wms tests - uses composition with TestsFlextUtilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import FlextTestsUtilities

from flext_tap_oracle_wms import FlextTapOracleWmsUtilities


class TestsFlextTapOracleWmsUtilities(FlextTestsUtilities, FlextTapOracleWmsUtilities):
    """Utilities for flext-tap-oracle-wms tests - uses composition with TestsFlextUtilities.

    Architecture: Uses composition (not inheritance) with TestsFlextUtilities and FlextTapOracleWmsUtilities
    for flext-tap-oracle-wms-specific utility definitions.

    Access patterns:
    - TestsFlextTapOracleWmsUtilities.Tests.* = flext_tests test utilities (via composition)
    - TestsFlextTapOracleWmsUtilities.TapOracleWms.* = flext-tap-oracle-wms-specific test utilities
    - TestsFlextTapOracleWmsUtilities.* = TestsFlextUtilities methods (via composition)

    Rules:
    - Use composition, not inheritance (TestsFlextUtilities deprecates subclassing)
    - flext-tap-oracle-wms-specific utilities go in TapOracleWms namespace
    - Generic utilities accessed via Tests namespace
    """


u = TestsFlextTapOracleWmsUtilities
__all__: list[str] = ["TestsFlextTapOracleWmsUtilities", "u"]
