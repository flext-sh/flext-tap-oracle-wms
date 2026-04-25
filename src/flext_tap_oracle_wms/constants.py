"""FLEXT Tap Oracle WMS Constants - Oracle WMS tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import TYPE_CHECKING, Final

from flext_meltano import FlextMeltanoConstants
from flext_oracle_wms import FlextOracleWmsConstants

if TYPE_CHECKING:
    from flext_tap_oracle_wms import t


class FlextTapOracleWmsConstants(FlextMeltanoConstants, FlextOracleWmsConstants):
    """Oracle WMS tap extraction-specific constants following flext-core patterns.

    Composes with FlextOracleWmsConstants to avoid duplication and ensure consistency.
    Note: Does not override Authentication from parent classes to avoid conflicts.
    """

    DEFAULT_WMS_TIMEOUT: Final[int] = FlextMeltanoConstants.DEFAULT_TIMEOUT_SECONDS
    DEFAULT_FETCH_SIZE: Final[int] = (
        FlextOracleWmsConstants.OracleWms.WmsProcessing.DEFAULT_BATCH_SIZE
    )
    TAP_MAX_BATCH_SIZE: Final[int] = FlextMeltanoConstants.MAX_ITEMS

    class TapOracleWms:
        """Oracle WMS tap-specific constants."""

        DEFAULT_TIMEOUT: Final[int] = (
            FlextMeltanoConstants.Meltano.DEFAULT_TIMEOUT_SECONDS
        )
        MAX_RETRIES: Final[int] = 3
        REQUIRED_CONFIG_FIELDS: Final[frozenset[str]] = frozenset({
            "base_url",
            "username",
            "password",
        })
        SCHEMA_TYPE_STRING: Final[str] = "string"
        SCHEMA_TYPE_OBJECT: Final[str] = "object"
        SCHEMA_TYPE_BOOLEAN: Final[str] = "boolean"
        SCHEMA_TYPE_INTEGER: Final[str] = "integer"
        SCHEMA_TYPE_NULL: Final[str] = "null"
        SCHEMA_FORMAT_DATETIME: Final[str] = "date-time"
        SCHEMA_TYPE_STRING_OR_NULL: Final[t.StrSequence] = ("string", "null")

        @unique
        class TapWmsEntityType(StrEnum):
            """Oracle WMS entity types using StrEnum for type safety.

            DRY Pattern:
                StrEnum is the single source of truth. Use TapWmsEntityType.INVENTORY.value
                or TapWmsEntityType.INVENTORY directly - no base strings needed.
            """

            INVENTORY = "INVENTORY"
            SHIPMENT = "SHIPMENT"
            PICKING = "PICKING"
            RECEIVING = "RECEIVING"

        class Authentication(
            FlextOracleWmsConstants.OracleWms.Authentication,
        ):
            """Merged authentication constants from both parent hierarchies."""

        class TapWmsProcessing:
            """WMS tap processing configuration.

            Note: Does not override parent Processing class to avoid inheritance conflicts.
            """

            DEFAULT_PAGE_SIZE: Final[int] = (
                FlextOracleWmsConstants.OracleWms.WmsProcessing.DEFAULT_BATCH_SIZE
            )
            MAX_RECORDS_PER_BATCH: Final[int] = (
                FlextOracleWmsConstants.OracleWms.WmsProcessing.MAX_BATCH_SIZE
            )
            DEFAULT_API_TIMEOUT: Final[int] = (
                FlextMeltanoConstants.DEFAULT_TIMEOUT_SECONDS
            )
            ORACLE_WMS_PAGE_SIZE_LIMIT: Final[int] = 1250
            USERNAME_TRUNCATION_LENGTH: Final[int] = 3
            HIGH_ALLOCATION_THRESHOLD: Final[float] = 0.8
            MEDIUM_ALLOCATION_THRESHOLD: Final[float] = 0.5

        class Extraction:
            """WMS-specific extraction configuration."""

            DEFAULT_ENTITY_LIMIT: Final[int] = (
                FlextOracleWmsConstants.OracleWms.WmsProcessing.DEFAULT_BATCH_SIZE
            )
            DEFAULT_DISCOVERY_TIMEOUT: Final[int] = (
                FlextMeltanoConstants.DEFAULT_TIMEOUT_SECONDS
            )
            MAX_ENTITY_BATCH_SIZE: Final[int] = (
                FlextOracleWmsConstants.OracleWms.WmsProcessing.MAX_BATCH_SIZE
            )

        class Settings:
            """Configuration constants for tap settings."""

            DEFAULT_API_VERSION: Final[str] = "V1"
            MAX_PARALLEL_STREAMS_WITHOUT_RATE_LIMIT: Final[int] = 5
            TAP_DEFAULT_MAX_RETRIES: Final[int] = 3
            TAP_DEFAULT_RETRY_DELAY: Final[float] = 1.0
            TAP_MIN_TIMEOUT: Final[int] = 1
            TAP_MAX_TIMEOUT: Final[int] = 300
            TAP_DEFAULT_TIMEOUT: Final[int] = 30
            TAP_DEFAULT_PAGE_SIZE: Final[int] = 10
            DEFAULT_DISCOVERY_SAMPLE_SIZE: Final[int] = 100
            MAX_DISCOVERY_SAMPLE_SIZE: Final[int] = FlextMeltanoConstants.DEFAULT_SIZE
            DEFAULT_MAX_PARALLEL_STREAMS: Final[int] = 5
            DEFAULT_FLATTENING_DEPTH: Final[int] = 10
            DEFAULT_VERIFY_SSL: Final[bool] = True
            DEFAULT_ENABLE_PARALLEL_EXTRACTION: Final[bool] = False
            DEFAULT_ENABLE_RATE_LIMITING: Final[bool] = True
            DEFAULT_MAX_REQUESTS_PER_MINUTE: Final[int] = 60
            DEFAULT_ENABLE_SCHEMA_FLATTENING: Final[bool] = True
            DEFAULT_LOG_LEVEL: Final[str] = "INFO"
            DEFAULT_ENABLE_REQUEST_LOGGING: Final[bool] = False
            DEFAULT_VALIDATE_CONFIG: Final[bool] = True
            DEFAULT_VALIDATE_SCHEMAS: Final[bool] = True
            ISO_DATE_PATTERN: Final[str] = (
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
            )


c = FlextTapOracleWmsConstants
__all__: list[str] = ["FlextTapOracleWmsConstants", "c"]
