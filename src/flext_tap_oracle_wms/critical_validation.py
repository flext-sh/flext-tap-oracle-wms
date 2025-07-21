"""Critical validation module for Oracle WMS Tap.

This module enforces mandatory Oracle WMS tap requirements using the centralized
Oracle validation patterns from flext-core. Eliminates code duplication across
Oracle projects by using the base validation classes.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.config.oracle import OracleWMSValidator
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from flext_core.domain.types import ServiceResult

logger = get_logger(__name__)

# Initialize Oracle WMS validator with project-specific prefix
_wms_validator = OracleWMSValidator("TAP_ORACLE_WMS")


def enforce_mandatory_environment_variables() -> None:
    """Enforce mandatory environment variables for Oracle WMS Tap.

    Raises:
        SystemExit: If mandatory environment variables are missing.

    """
    # Use centralized Oracle WMS validation
    validation_result = _wms_validator.enforce_critical_environment_variables()

    if not validation_result.is_success:
        error_msg = validation_result.error
        logger.error(error_msg)
        raise SystemExit(error_msg)

    logger.info(
        "🚨 CRITICAL VALIDATION PASSED: Mandatory Oracle WMS tap environment variables validated"
    )


def validate_schema_discovery_mode() -> ServiceResult[None]:
    """Validate schema discovery mode configuration.

    Returns:
        ServiceResult indicating validation success or failure

    """
    return _wms_validator.enforce_critical_environment_variables()


def validate_wms_record(record: dict) -> ServiceResult[list[str]]:
    """Validate WMS record using centralized validation.

    Args:
        record: WMS record to validate

    Returns:
        ServiceResult containing validation errors (empty list if valid)

    """
    return _wms_validator.validate_wms_record(record)
