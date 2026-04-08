"""Test models for flext-tap-oracle-wms tests.

Provides TestsFlextTapOracleWmsModels, extending TestsFlextModels with
flext-tap-oracle-wms-specific models using COMPOSITION INHERITANCE.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsModels

from flext_tap_oracle_wms import FlextTapOracleWmsModels


class TestsFlextTapOracleWmsModels(FlextTestsModels, FlextTapOracleWmsModels):
    """Models for flext-tap-oracle-wms tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. TestsFlextModels - for test infrastructure (.Tests.*)
    2. FlextTapOracleWmsModels - for domain models

    Access patterns:
    - TestsFlextTapOracleWmsModels.Tests.* (generic test models from TestsFlextModels)
    - TestsFlextTapOracleWmsModels.TapOracleWms.* (Tap Oracle WMS domain models)
    """

    class TapOracleWms(FlextTapOracleWmsModels.TapOracleWms):
        """TapOracleWms domain models extending project models."""

        class Tests:
            """Internal tests declarations."""


m = TestsFlextTapOracleWmsModels

__all__ = [
    "TestsFlextTapOracleWmsModels",
    "m",
]
