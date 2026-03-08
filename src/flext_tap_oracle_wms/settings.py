"""Configuration management for FLEXT Tap Oracle WMS.

Type-safe configuration using FLEXT patterns with Pydantic validation.
Consolidates configuration management and constants following PEP8 patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Final

from flext_core import FlextConstants
from flext_oracle_wms import FlextOracleWmsConstants as _WmsConstants


class FlextTapOracleWmsConstants(FlextConstants):
    """Constants for Oracle WMS tap configuration - consuming from flext-oracle-wms API."""

    DEFAULT_API_VERSION: Final[str] = str(_WmsConstants.API_CONFIG["version_default"])
    MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT: Final[int] = 5
    DEFAULT_MAX_RETRIES: Final[int] = 3
    DEFAULT_RETRY_DELAY: Final[float] = 1.0
    MIN_TIMEOUT: Final[int] = 1
    MAX_TIMEOUT: Final[int] = 300
    DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = 100
    MAX_DISCOVERY_SAMPLE_SIZE: Final[int] = (
        FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
    )
