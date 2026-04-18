"""Types for flext-tap-oracle-wms tests - uses composition with TestsFlextTypes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from flext_tests import FlextTestsTypes

from flext_tap_oracle_wms import FlextTapOracleWmsTypes


class TestsFlextTapOracleWmsTypes(FlextTestsTypes, FlextTapOracleWmsTypes):
    """Types for flext-tap-oracle-wms tests - uses composition with TestsFlextTypes.

    Architecture: Uses composition (not inheritance) with TestsFlextTypes and FlextTapOracleWmsTypes
    for flext-tap-oracle-wms-specific type definitions.

    Access patterns:
    - TestsFlextTapOracleWmsTypes.Tests.* = flext_tests test types (via composition)
    - TestsFlextTapOracleWmsTypes.TapOracleWms.* = flext-tap-oracle-wms-specific test types
    - TestsFlextTapOracleWmsTypes.* = TestsFlextTypes types (via composition)

    Rules:
    - Use composition, not inheritance (TestsFlextTypes deprecates subclassing)
    - flext-tap-oracle-wms-specific types go in TapOracleWms namespace
    - Generic types accessed via Tests namespace
    """

    class TapOracleWms:
        """Tap Oracle WMS test types - domain-specific for Oracle WMS tap testing.

        Contains test types specific to Oracle WMS tap functionality including:
        - Test configuration types
        - Mock Oracle WMS data types
        - Test scenario types
        """

        type MockOracleWmsRecord = Mapping[str, FlextTapOracleWmsTypes.Scalar]
        type MockOracleWmsResponse = Mapping[
            str,
            Sequence[MockOracleWmsRecord] | bool | str | None,
        ]
        type TestOracleWmsScenario = FlextTestsTypes.RecursiveContainerMapping
        type TestOracleWmsValidationResult = Mapping[
            str, bool | str | FlextTestsTypes.StrSequence
        ]
        type TestOracleWmsApiResult = FlextTestsTypes.RecursiveContainerMapping


t = TestsFlextTapOracleWmsTypes
__all__: list[str] = ["TestsFlextTapOracleWmsTypes", "t"]
