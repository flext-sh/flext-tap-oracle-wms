"""Domain exceptions for the Oracle WMS tap package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_oracle_wms/errors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_oracle_wms import e


class FlextTapOracleWmsError(e.BaseError):
    """Base exception for Oracle WMS tap failures."""


class FlextTapOracleWmsValidationError(FlextTapOracleWmsError):
    """Raised when tap configuration or payload validation fails."""


class FlextTapOracleWmsConfigurationError(FlextTapOracleWmsValidationError):
    """Raised when settings are invalid for runtime execution."""
