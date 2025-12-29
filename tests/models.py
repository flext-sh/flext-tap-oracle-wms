"""Test models for flext-tap-oracle-wms tests.

Provides TestsFlextTapOracleWmsModels, extending FlextTestsModels with
flext-tap-oracle-wms-specific models using COMPOSITION INHERITANCE.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests.models import FlextTestsModels

from flext_tap_oracle_wms.models import FlextTapOracleWmsModels


class TestsFlextTapOracleWmsModels(FlextTestsModels, FlextTapOracleWmsModels):
    """Models for flext-tap-oracle-wms tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. FlextTestsModels - for test infrastructure (.Tests.*)
    2. FlextTapOracleWmsModels - for domain models

    Access patterns:
    - tm.Tests.* (generic test models from FlextTestsModels)
    - tm.* (Tap Oracle WMS domain models)
    - m.* (production models via alternative alias)
    """


# Short aliases per FLEXT convention
tm = TestsFlextTapOracleWmsModels
m = TestsFlextTapOracleWmsModels

__all__ = [
    "TestsFlextTapOracleWmsModels",
    "m",
    "tm",
]
