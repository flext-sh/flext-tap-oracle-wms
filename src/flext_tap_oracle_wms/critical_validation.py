"""Critical validation module for Oracle WMS Tap using DI pattern.

This module enforces mandatory Oracle WMS tap requirements using dependency injection
to access Oracle validation services. Follows Clean Architecture principles.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

# Removed circular dependency - use DI pattern
from typing import TYPE_CHECKING

# Import from flext-core for foundational patterns (standardized)
from flext_core import FlextResult as FlextResult, get_logger
from flext_db_oracle.patterns.oracle_patterns import (
    FlextDbOracleWMSValidator as OracleValidationProvider,
)

logger = get_logger(__name__)

# Oracle validation provider will be injected at runtime
_validation_provider: OracleValidationProvider | None = None


def set_validation_provider(provider: OracleValidationProvider) -> None:
    """Set the Oracle validation provider via dependency injection.

    Args:
        provider: Oracle validation provider implementation

    """
    global _validation_provider
    _validation_provider = provider


def _get_validation_provider() -> OracleValidationProvider:
    """Get validation provider or raise error if not set.

    Returns:
        Oracle validation provider

    Raises:
        RuntimeError: If no validation provider has been injected

    """
    if _validation_provider is None:
        error_msg = "Oracle validation provider not injected - call set_validation_provider() first"
        logger.error(error_msg)
        raise FlextServiceError(error_msg)
    return _validation_provider


def enforce_mandatory_environment_variables() -> None:
    """Enforce mandatory environment variables for Oracle WMS Tap using DI.

    Raises:
        SystemExit: If mandatory environment variables are missing.

    """
    provider = _get_validation_provider()
    validation_result = provider.enforce_critical_environment_variables()

    if not validation_result.is_success:
        error_msg = validation_result.error or "Validation failed"
        logger.error(error_msg)
        raise SystemExit(error_msg)

    logger.info(
        "🚨 CRITICAL VALIDATION PASSED: Mandatory Oracle WMS tap environment variables validated"
    )


def validate_schema_discovery_mode() -> FlextResult[None]:
    """Validate schema discovery mode configuration using DI.

    Returns:
        FlextResult indicating validation success or failure

    """
    provider = _get_validation_provider()
    return provider.enforce_critical_environment_variables()


def validate_wms_record(record: dict[str, object]) -> FlextResult[list[str]]:
    """Validate WMS record using dependency injection.

    Args:
        record: WMS record to validate

    Returns:
        FlextResult containing validation errors (empty list if valid)

    """
    provider = _get_validation_provider()
    return provider.validate_wms_record(record)
