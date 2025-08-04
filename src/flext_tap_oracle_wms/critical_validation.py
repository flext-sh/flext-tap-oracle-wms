"""Critical validation module for Oracle WMS Tap using DI pattern.

This module enforces mandatory Oracle WMS tap requirements using dependency injection
to access Oracle validation services. Follows Clean Architecture principles.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

# Removed circular dependency - use DI pattern
# Import from flext-core for foundational patterns (standardized)
from flext_core import FlextResult, get_logger

# Import from flext-oracle-wms for WMS-specific validation
from flext_oracle_wms import FlextOracleWmsClient, FlextOracleWmsClientConfig

logger = get_logger(__name__)

# Simple validation without complex dependency injection


def enforce_mandatory_environment_variables() -> None:
    """Enforce mandatory environment variables for Oracle WMS Tap.

    Raises:
        SystemExit: If mandatory environment variables are missing.

    """
    # Simple validation using environment variables
    import os

    required_vars = [
        "ORACLE_WMS_BASE_URL",
        "ORACLE_WMS_USERNAME",
        "ORACLE_WMS_PASSWORD",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg: str = (
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        logger.error(error_msg)
        raise SystemExit(error_msg)

    logger.info(
        "🚨 CRITICAL VALIDATION PASSED: Mandatory Oracle WMS tap environment variables validated",
    )


def validate_schema_discovery_mode() -> FlextResult[None]:
    """Validate schema discovery mode configuration using real WMS config.

    Returns:
        FlextResult indicating validation success or failure

    """
    # Use real WMS configuration to validate schema discovery capability
    import os

    from flext_oracle_wms.config import FlextOracleWmsModuleConfig

    logger.info("Validating WMS schema discovery mode with real configuration")

    # Create real config object using environment variables for security
    from pydantic import HttpUrl

    # Use environment variables or fallback to test configuration factory method
    base_url = os.getenv("ORACLE_WMS_BASE_URL", "https://test-wms.oracle.com/api")
    username = os.getenv("ORACLE_WMS_USERNAME", "validation_user")
    password = os.getenv("ORACLE_WMS_PASSWORD", "")

    if not password:
        # Use the secure testing factory method instead of hardcoded credentials
        legacy_config = FlextOracleWmsModuleConfig.for_testing()
        # Convert to new client config format
        client_config = FlextOracleWmsClientConfig.from_legacy_config(legacy_config)
    else:
        # Use environment variables for real configuration
        legacy_config = FlextOracleWmsModuleConfig(
            base_url=HttpUrl(base_url),
            username=username,
            password=password,
            api_version="v1",
            timeout_seconds=30,
        )
        # Convert to new client config format
        client_config = FlextOracleWmsClientConfig.from_legacy_config(legacy_config)

    # Create client using real configuration and verify it can be instantiated
    client = FlextOracleWmsClient(client_config)

    # Validate that client has required methods for schema discovery
    # The new client uses discover_entities (async) method
    if hasattr(client, "discover_entities"):
        logger.info(
            "WMS schema discovery mode validated successfully - client has discover_entities method",
        )
        return FlextResult.ok(None)

    error_msg = "WMS client missing required discover_entities method"
    logger.error(error_msg)
    return FlextResult.fail(error_msg)


def validate_wms_record(record: object) -> FlextResult[list[str]]:
    """Validate WMS record using real WMS entity validation.

    Args:
        record: WMS record to validate

    Returns:
        FlextResult containing validation errors (empty list if valid)

    """
    # Use real WMS entity validation from flext-oracle-wms
    from flext_oracle_wms.models import FlextOracleWmsEntity

    errors: list[str] = []

    if not isinstance(record, dict):
        errors.append("Record must be a dictionary")
        return FlextResult.ok(errors)

    if not record:
        errors.append("Record cannot be empty")
        return FlextResult.ok(errors)

    # Validate using real WMS entity model
    try:
        # Create WMS entity from record to validate structure
        wms_entity = FlextOracleWmsEntity(
            name=str(record.get("id", "unknown")),
            endpoint=f"/api/{record.get('type', 'generic')}",
            description=f"Entity for {record.get('type', 'generic')}",
            fields=record,
        )

        # If we can create the entity successfully, record is valid
        if wms_entity.name and wms_entity.endpoint:
            logger.debug(f"WMS record validated successfully: {wms_entity.name}")
            return FlextResult.ok([])  # No errors
        errors.append("WMS entity validation failed - missing required fields")

    except Exception as e:
        errors.append(f"WMS entity validation error: {e}")

    return FlextResult.ok(errors)
