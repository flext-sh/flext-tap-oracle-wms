"""Test models for flext-tap-oracle-wms tests.

Provides FlextTapOracleWmsTestModels, extending FlextTestsModels with
flext-tap-oracle-wms-specific models using COMPOSITION INHERITANCE.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsModels

from flext_tap_oracle_wms import FlextTapOracleWmsModels


class FlextTapOracleWmsTestModels(FlextTestsModels, FlextTapOracleWmsModels):
    """Models for flext-tap-oracle-wms tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. FlextTestsModels - for test infrastructure (.Tests.*)
    2. FlextTapOracleWmsModels - for domain models

    Access patterns:
    - FlextTapOracleWmsTestModels.Tests.* (generic test models from FlextTestsModels)
    - FlextTapOracleWmsTestModels.TapOracleWms.* (Tap Oracle WMS domain models)
    """

    class TapOracleWms(FlextTapOracleWmsModels.TapOracleWms):
        """TapOracleWms domain models extending project models."""

        class Tests:
            """Internal tests declarations."""


m = FlextTapOracleWmsTestModels

__all__ = [
    "FlextTapOracleWmsTestModels",
    "m",
]
