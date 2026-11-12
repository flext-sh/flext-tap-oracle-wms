"""Module skeleton for TestsFlextTapOracleWmsConstants.

Test constants for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import secrets
from typing import Final

from flext_tests import FlextTestsConstants

from flext_tap_oracle_wms import FlextTapOracleWmsConstants


class TestsFlextTapOracleWmsConstants(FlextTestsConstants, FlextTapOracleWmsConstants):
    """Test constants for flext-tap-oracle-wms."""

    class TapOracleWms(FlextTapOracleWmsConstants.TapOracleWms):
        """Tap Oracle WMS domain constants extended with test declarations."""

        class Tests:
            """Internal tests declarations for test-only objects."""

            CREDENTIAL: Final[str] = secrets.token_urlsafe()
            "Generated credential shared by the tap settings tests."


c = TestsFlextTapOracleWmsConstants
__all__: list[str] = ["TestsFlextTapOracleWmsConstants", "c"]
