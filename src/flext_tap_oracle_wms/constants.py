# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT Tap Oracle WMS Constants - Oracle WMS tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_meltano import c
from flext_oracle_wms import c as flext_oracle_wms_c

from flext_tap_oracle_wms._constants import (
    FlextTapOracleWmsConstantsBase,
    FlextTapOracleWmsConstantsValues,
)


class FlextTapOracleWmsConstants(
    c,
    flext_oracle_wms_c,
    FlextTapOracleWmsConstantsValues,
):
    """Oracle WMS tap extraction-specific constants following flext-core patterns.

    Composes with FlextOracleWmsConstants to avoid duplication and ensure consistency.
    Note: Does not override Authentication from parent classes to avoid conflicts.
    """

    class TapOracleWms(
        FlextTapOracleWmsConstantsBase,
        FlextTapOracleWmsConstantsValues.TapOracleWms,
    ):
        """Oracle WMS tap-specific constants."""


c = FlextTapOracleWmsConstants
__all__: list[str] = ["FlextTapOracleWmsConstants", "c"]
