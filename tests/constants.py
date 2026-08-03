"""Module skeleton for TestsFlextTapOracleWmsConstants.

Test constants for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_oracle_wms import FlextTapOracleWmsConstants
from flext_tests import FlextTestsConstants


class TestsFlextTapOracleWmsConstants(FlextTestsConstants, FlextTapOracleWmsConstants):
    """Test constants for flext-tap-oracle-wms."""


c = TestsFlextTapOracleWmsConstants
__all__: list[str] = ["TestsFlextTapOracleWmsConstants", "c"]
