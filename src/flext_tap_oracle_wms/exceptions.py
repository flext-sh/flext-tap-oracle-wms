"""Oracle WMS Tap Exception Hierarchy.

 Tap-specific exception hierarchy built on FLEXT ecosystem error handling patterns
with specialized exceptions for Oracle WMS tap operations, validation, and data processing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

from flext_core import FlextExceptions


# Define exceptions inheriting from FlextExceptions
class FlextTapOracleWMSError(FlextExceptions.Error):
    """Base exception for Oracle WMS tap operations."""


class FlextTapOracleWMSValidationError(FlextExceptions.ValidationError):
    """Validation error for Oracle WMS tap operations."""


class FlextTapOracleWMSConfigurationError(FlextExceptions.ConfigurationError):
    """Configuration error for Oracle WMS tap operations."""


class FlextTapOracleWMSProcessingError(FlextExceptions.ProcessingError):
    """Processing error for Oracle WMS tap operations."""


class FlextTapOracleWMSConnectionError(FlextExceptions.ConnectionError):
    """Connection error for Oracle WMS tap operations."""


class FlextTapOracleWMSAuthenticationError(FlextExceptions.AuthenticationError):
    """Authentication error for Oracle WMS tap operations."""


class FlextTapOracleWMSTimeoutError(FlextExceptions.TimeoutError):
    """Timeout error for Oracle WMS tap operations."""


# Use flext-core exceptions directly - no aliases needed


@dataclass
class ValidationContext:
    """Context information for validation errors."""

    stream_name: str | None = None
    field_name: str | None = None
    expected_type: str | None = None
    actual_value: object = None


__all__ = [
    "FlextTapOracleWMSAuthenticationError",
    "FlextTapOracleWMSConfigurationError",
    "FlextTapOracleWMSConnectionError",
    "FlextTapOracleWMSError",
    "FlextTapOracleWMSProcessingError",
    "FlextTapOracleWMSTimeoutError",
    "FlextTapOracleWMSValidationError",
    "ValidationContext",
]
