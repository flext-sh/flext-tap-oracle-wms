"""Module skeleton for FlextTapOracleWmsTestConstants.

Test constants for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsConstants

from flext_tap_oracle_wms import FlextTapOracleWmsConstants


class FlextTapOracleWmsTestConstants(FlextTestsConstants, FlextTapOracleWmsConstants):
    """Test constants for flext-tap-oracle-wms."""


c = FlextTapOracleWmsTestConstants
__all__ = ["FlextTapOracleWmsTestConstants", "c"]
