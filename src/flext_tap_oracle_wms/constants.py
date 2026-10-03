"""FLEXT Tap Oracle WMS Constants - Oracle WMS tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_meltano import FlextMeltanoConstants
from flext_oracle_wms import FlextOracleWmsConstants

from flext_tap_oracle_wms._constants.values import FlextTapOracleWmsConstantsValues

if TYPE_CHECKING:
    from flext_tap_oracle_wms import t


class FlextTapOracleWmsConstants(
    FlextMeltanoConstants, FlextOracleWmsConstants, FlextTapOracleWmsConstantsValues
):
    """Oracle WMS tap extraction-specific constants following flext-core patterns.

    Composes with FlextOracleWmsConstants to avoid duplication and ensure consistency.
    Note: Does not override Authentication from parent classes to avoid conflicts.
    """

    class TapOracleWms(FlextTapOracleWmsConstantsValues.TapOracleWms):
        """Oracle WMS tap-specific constants."""


c = FlextTapOracleWmsConstants
__all__: t.StrSequence = ("FlextTapOracleWmsConstants", "c")
