"""FLEXT Tap Oracle WMS Utilities - Domain-specific utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import FlextMeltanoUtilities
from flext_oracle_wms import FlextOracleWmsUtilities

from flext_tap_oracle_wms._utilities.mapping import FlextTapOracleWmsUtilitiesConversion


class FlextTapOracleWmsUtilities(FlextMeltanoUtilities, FlextOracleWmsUtilities):
    """Domain-specific Oracle WMS tap utilities.

    Inherits from u to avoid duplication.
    """

    class TapOracleWms(FlextTapOracleWmsUtilitiesConversion):
        """Oracle WMS tap utilities namespace."""

        MappingConversion = FlextTapOracleWmsUtilitiesConversion.MappingConversion


u = FlextTapOracleWmsUtilities
"""Facade assignment for module-level utility access."""

__all__: list[str] = ["FlextTapOracleWmsUtilities", "u"]
