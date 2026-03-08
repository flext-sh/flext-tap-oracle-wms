"""Configuration management for FLEXT Tap Oracle WMS.

Type-safe configuration using FLEXT patterns with Pydantic validation.
Consolidates configuration management and constants following PEP8 patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Final

from flext_core import (
    FlextConstants,
)
from flext_oracle_wms import (
    FlextOracleWmsConstants as _WmsConstants,
)


class FlextTapOracleWmsConstants(FlextConstants):
    """Constants for Oracle WMS tap configuration - consuming from flext-oracle-wms API."""

    # API defaults from flext-oracle-wms (using available constants)
    DEFAULT_API_VERSION: Final[str] = str(_WmsConstants.API_CONFIG["version_default"])

    # Validation limits - using FlextConstants as SOURCE OF TRUTH
    MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT: Final[int] = 5
    # DEFAULT_PAGE_SIZE: Final[int] = _WmsConstants.DEFAULT_PAGE_SIZE - Removed to avoid override conflict
    # DEFAULT_TIMEOUT: Final[int] = _WmsConstants.Api.DEFAULT_TIMEOUT - Removed
    DEFAULT_MAX_RETRIES: Final[int] = 3
    DEFAULT_RETRY_DELAY: Final[float] = 1.0  # Standard retry delay

    # Pagination limits (hardcoded since not available in nested structure)
    # MIN_PAGE_SIZE: Final[int] = 1 - Removed
    # MAX_PAGE_SIZE: Final[int] = 1000 - Removed
    MIN_TIMEOUT: Final[int] = 1  # Singer-specific minimum
    MAX_TIMEOUT: Final[int] = 300  # Singer-specific maximum

    # Discovery settings (hardcoded since not available)

    DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = 100
    MAX_DISCOVERY_SAMPLE_SIZE: Final[int] = (
        FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
    )  # Singer-specific maximum
