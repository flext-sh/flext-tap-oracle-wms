"""Types for flext-tap-oracle-wms tests - uses composition with FlextTestsTypes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from flext_tests import FlextTestsTypes

from flext_tap_oracle_wms import (
    FlextTapOracleWmsConstants as _c,
    FlextTapOracleWmsTypes,
)


class FlextTapOracleWmsTestTypes(FlextTestsTypes, FlextTapOracleWmsTypes):
    """Types for flext-tap-oracle-wms tests - uses composition with FlextTestsTypes.

    Architecture: Uses composition (not inheritance) with FlextTestsTypes and FlextTapOracleWmsTypes
    for flext-tap-oracle-wms-specific type definitions.

    Access patterns:
    - FlextTapOracleWmsTestTypes.Tests.* = flext_tests test types (via composition)
    - FlextTapOracleWmsTestTypes.TapOracleWms.* = flext-tap-oracle-wms-specific test types
    - FlextTapOracleWmsTestTypes.* = FlextTestsTypes types (via composition)

    Rules:
    - Use composition, not inheritance (FlextTestsTypes deprecates subclassing)
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

        type TestOracleWmsBaseUrl = _c.TestOracleWmsBaseUrl
        type TestOracleWmsUsername = _c.TestOracleWmsUsername
        type TestOracleWmsMethod = _c.TestOracleWmsMethod
        type TestFacilityId = _c.TestFacilityId
        type MockOracleWmsRecord = Mapping[str, FlextTapOracleWmsTypes.Scalar]
        type MockOracleWmsResponse = Mapping[
            str, Sequence[MockOracleWmsRecord] | bool | str | None
        ]
        type TestOracleWmsScenario = t.ContainerMapping
        type TestOracleWmsValidationResult = Mapping[str, bool | str | Sequence[str]]
        type TestOracleWmsApiResult = t.ContainerMapping


t = FlextTapOracleWmsTestTypes
__all__ = ["FlextTapOracleWmsTestTypes", "t"]
