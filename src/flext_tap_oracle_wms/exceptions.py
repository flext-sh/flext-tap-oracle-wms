"""Oracle WMS Tap Exception Hierarchy.

 Tap-specific exception hierarchy built on FLEXT ecosystem error handling patterns
with specialized exceptions for Oracle WMS tap operations, validation, and data processing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

from flext_core import FlextCore


# Define exceptions inheriting from FlextCore.Exceptions
class FlextMeltanoTapOracleWMSError(FlextCore.Exceptions.Error):
    """Base exception for Oracle WMS tap operations."""


class FlextMeltanoTapOracleWMSValidationError(FlextCore.Exceptions.ValidationError):
    """Validation error for Oracle WMS tap operations."""


class FlextMeltanoTapOracleWMSConfigurationError(
    FlextCore.Exceptions.ConfigurationError
):
    """Configuration error for Oracle WMS tap operations."""


class FlextMeltanoTapOracleWMSProcessingError(FlextCore.Exceptions.ProcessingError):
    """Processing error for Oracle WMS tap operations."""


class FlextMeltanoTapOracleWMSConnectionError(FlextCore.Exceptions.ConnectionError):
    """Connection error for Oracle WMS tap operations."""


class FlextMeltanoTapOracleWMSAuthenticationError(
    FlextCore.Exceptions.AuthenticationError
):
    """Authentication error for Oracle WMS tap operations."""


class FlextMeltanoTapOracleWMSTimeoutError(FlextCore.Exceptions.TimeoutError):
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
    "FlextMeltanoTapOracleWMSAuthenticationError",
    "FlextMeltanoTapOracleWMSConfigurationError",
    "FlextMeltanoTapOracleWMSConnectionError",
    "FlextMeltanoTapOracleWMSError",
    "FlextMeltanoTapOracleWMSProcessingError",
    "FlextMeltanoTapOracleWMSTimeoutError",
    "FlextMeltanoTapOracleWMSValidationError",
    "ValidationContext",
]
