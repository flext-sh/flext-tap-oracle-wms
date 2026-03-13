"""Configuration contracts for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, Final

from flext_core import FlextConstants
from flext_oracle_wms import FlextOracleWmsConstants as _WmsConstants
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from pydantic.networks import AnyUrl

from flext_tap_oracle_wms.constants import c


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


class FlextTapOracleWmsSettings(BaseModel):
    """Validated settings consumed by the Oracle WMS tap runtime."""

    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    base_url: Annotated[
        AnyUrl,
        Field(
            description="Base Oracle WMS API URL.",
        ),
    ]
    username: Annotated[
        str,
        Field(
            min_length=1,
            description="Oracle WMS username.",
        ),
    ]
    password: Annotated[
        SecretStr,
        Field(
            description="Oracle WMS password.",
        ),
    ]
    api_version: Annotated[
        str,
        Field(
            default=FlextTapOracleWmsConstants.DEFAULT_API_VERSION,
            min_length=1,
            description="Oracle WMS API version.",
        ),
    ]
    timeout: Annotated[
        int,
        Field(
            default=c.TapOracleWms.DEFAULT_TIMEOUT,
            ge=FlextTapOracleWmsConstants.MIN_TIMEOUT,
            le=FlextTapOracleWmsConstants.MAX_TIMEOUT,
            description="Request timeout in seconds.",
        ),
    ]
    max_retries: Annotated[
        int,
        Field(
            default=c.TapOracleWms.MAX_RETRIES,
            ge=0,
            description="Maximum request retries.",
        ),
    ]
    verify_ssl: Annotated[
        bool,
        Field(
            default=True,
            description="Enable SSL verification.",
        ),
    ]
    page_size: Annotated[
        int,
        Field(
            default=FlextTapOracleWmsConstants.DEFAULT_DISCOVERY_SAMPLE_SIZE,
            ge=1,
            description="Page size used for extraction requests.",
        ),
    ]
    effective_log_level: Annotated[
        str,
        Field(
            default="INFO",
            min_length=1,
            description="Optional effective log level inherited from runtime.",
        ),
    ]


__all__ = ["FlextTapOracleWmsConstants", "FlextTapOracleWmsSettings"]
