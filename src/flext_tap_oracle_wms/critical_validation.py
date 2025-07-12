"""Critical validation module for non-negotiable requirements.

This module enforces mandatory environment variables that cannot be overridden
or disabled. These validations are CRITICAL and will cause immediate abort
if the required values are not set correctly.:
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import os

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

logger = get_logger(__name__)


def enforce_mandatory_environment_variables() -> None:
    """Enforce mandatory environment variables.

    Raises:
        SystemExit: If mandatory environment variables are missing.

    """
    # CRITICAL VALIDATION 1: USE_METADATA_ONLY must be 'true'
    use_metadata_only = os.getenv("TAP_ORACLE_WMS_USE_METADATA_ONLY", "").lower()
    if use_metadata_only != "true":
        error_msg = (
            f"❌ CRITICAL FAILURE: TAP_ORACLE_WMS_USE_METADATA_ONLY must be 'true' "
            f"but got '{use_metadata_only}'. This is a NON-NEGOTIABLE "
            f"requirement. ABORTING!"
        )
        logger.error(error_msg)
        raise SystemExit(error_msg)

    # CRITICAL VALIDATION 2: DISCOVERY_SAMPLE_SIZE must be '0'
    try:
        discovery_sample_size = int(
            os.getenv("TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE", "-1"),
        )
    except (ValueError, TypeError):
        discovery_sample_size = -1

    if discovery_sample_size != 0:
        error_msg = (
            f"❌ CRITICAL FAILURE: TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE must be '0' "
            f"but got '{discovery_sample_size}'. Sample-based discovery is "
            f"FORBIDDEN. ABORTING!"
        )
        logger.error(error_msg)
        raise SystemExit(error_msg)

    logger.info(
        "🚨 CRITICAL VALIDATION PASSED: Mandatory schema discovery rules enforced",
    )


def validate_schema_discovery_mode() -> None:
    """Validate schema discovery mode configuration."""
    # Log the current state for verification
    use_metadata_only = os.getenv("TAP_ORACLE_WMS_USE_METADATA_ONLY", "not_set")
    discovery_sample_size = os.getenv("TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE", "not_set")

    logger.info(
        "Schema discovery mode: USE_METADATA_ONLY=%s, DISCOVERY_SAMPLE_SIZE=%s",
        use_metadata_only,
        discovery_sample_size,
    )

    # Ensure both values are correct
    if use_metadata_only.lower() == "true" and discovery_sample_size == "0":
        logger.info("✅ Schema discovery correctly configured for metadata-only mode")
    else:
        logger.warning(
            "⚠️ Schema discovery configuration may not be optimal. "
            "Ensure TAP_ORACLE_WMS_USE_METADATA_ONLY=true and "
            "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE=0",
        )
