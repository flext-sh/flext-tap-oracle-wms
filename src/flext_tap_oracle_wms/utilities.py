# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT Tap Oracle WMS Utilities - Domain-specific utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import u
from flext_oracle_wms import u as flext_oracle_wms_u

from flext_tap_oracle_wms._utilities import FlextTapOracleWmsUtilitiesConversion


class FlextTapOracleWmsUtilities(u, flext_oracle_wms_u):
    """Domain-specific Oracle WMS tap utilities.

    Inherits from u to avoid duplication.
    """

    class TapOracleWms(FlextTapOracleWmsUtilitiesConversion):
        """Oracle WMS tap utilities namespace."""


u = FlextTapOracleWmsUtilities
"""Facade assignment for module-level utility access."""
__all__: list[str] = ["FlextTapOracleWmsUtilities", "u"]
