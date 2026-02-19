"""Domain exceptions for the Oracle WMS tap package."""

from __future__ import annotations


class FlextTapOracleWmsError(Exception):
    """Base exception for Oracle WMS tap failures."""


class FlextTapOracleWmsConnectionError(FlextTapOracleWmsError):
    """Raised when connection to Oracle WMS fails."""


class FlextTapOracleWmsValidationError(FlextTapOracleWmsError):
    """Raised when tap configuration or payload validation fails."""


class FlextTapOracleWmsSettingsurationError(FlextTapOracleWmsValidationError):
    """Raised when settings are invalid for runtime execution."""
