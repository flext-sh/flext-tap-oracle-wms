"""Types for flext-tap-oracle-wms tests - uses composition with FlextTestsTypes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Literal

from flext_tap_oracle_wms import t
from flext_tests import FlextTestsTypes


class TestsFlextTapOracleWmsTypes(FlextTestsTypes):
    """Types for flext-tap-oracle-wms tests - uses composition with FlextTestsTypes.

    Architecture: Uses composition (not inheritance) with FlextTestsTypes and FlextTapOracleWmsTypes
    for flext-tap-oracle-wms-specific type definitions.

    Access patterns:
    - TestsFlextTapOracleWmsTypes.Tests.* = flext_tests test types (via composition)
    - TestsFlextTapOracleWmsTypes.TapOracleWms.* = flext-tap-oracle-wms-specific test types
    - TestsFlextTapOracleWmsTypes.* = FlextTestsTypes types (via composition)

    Rules:
    - Use composition, not inheritance (FlextTestsTypes deprecates subclassing)
    - flext-tap-oracle-wms-specific types go in TapOracleWms namespace
    - Generic types accessed via Tests namespace
    """

    # Composition: expose FlextTestsTypes
    # Tests = FlextTestsTypes  # Avoid override issues

    # TapOracleWms-specific test types namespace
    class TapOracleWms:
        """Tap Oracle WMS test types - domain-specific for Oracle WMS tap testing.

        Contains test types specific to Oracle WMS tap functionality including:
        - Test configuration types
        - Mock Oracle WMS data types
        - Test scenario types
        """

        # Test configuration literals
        type TestOracleWmsBaseUrl = Literal[
            "https://test-wms.oraclecloud.com",
            "https://staging-wms.oraclecloud.com",
        ]
        type TestOracleWmsUsername = Literal[
            "test_user",
            "REDACTED_LDAP_BIND_PASSWORD_user",
        ]
        type TestOracleWmsMethod = Literal["GET", "POST", "PUT", "DELETE"]
        type TestFacilityId = Literal["FAC001", "FAC002", "FAC003"]

        # Test data types
        type MockOracleWmsRecord = dict[str, str | int | float | bool]
        type MockOracleWmsResponse = dict[
            str,
            list[MockOracleWmsRecord] | bool | str | None,
        ]
        type TestOracleWmsScenario = dict[str, t.GeneralValueType]

        # Test result types
        type TestOracleWmsValidationResult = dict[str, bool | str | list[str]]
        type TestOracleWmsApiResult = dict[str, t.GeneralValueType]


# Alias for simplified usage
tt = TestsFlextTapOracleWmsTypes

__all__ = [
    "TestsFlextTapOracleWmsTypes",
    "tt",
]
