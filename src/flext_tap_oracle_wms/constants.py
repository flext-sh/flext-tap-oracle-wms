"""FLEXT Tap Oracle WMS Constants - Oracle WMS tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import Final, Literal

from flext_meltano import FlextMeltanoConstants
from flext_oracle_wms import FlextOracleWmsConstants

from flext_tap_oracle_wms import t


class FlextTapOracleWmsConstants(FlextMeltanoConstants, FlextOracleWmsConstants):
    """Oracle WMS tap extraction-specific constants following flext-core patterns.

    Composes with FlextOracleWmsConstants to avoid duplication and ensure consistency.
    Note: Does not override Authentication from parent classes to avoid conflicts.
    """

    class Authentication(
        FlextMeltanoConstants.Authentication,
        FlextOracleWmsConstants.Authentication,
    ):
        """Merged authentication constants from both parent hierarchies."""

    DEFAULT_WMS_TIMEOUT: Final[int] = FlextMeltanoConstants.DEFAULT_TIMEOUT_SECONDS
    DEFAULT_FETCH_SIZE: Final[int] = (
        FlextOracleWmsConstants.WmsProcessing.DEFAULT_BATCH_SIZE
    )
    TAP_MAX_BATCH_SIZE: Final[int] = FlextMeltanoConstants.MAX_ITEMS

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

    class TapOracleWms:
        """Oracle WMS connection configuration."""

        DEFAULT_TIMEOUT: Final[int] = FlextMeltanoConstants.DEFAULT_TIMEOUT_SECONDS
        MAX_RETRIES: Final[int] = FlextMeltanoConstants.DEFAULT_MAX_RETRY_ATTEMPTS
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
        SCHEMA_TYPE_STRING_OR_NULL: Final[t.StrSequence] = ["string", "null"]

    class TapWmsProcessing:
        """WMS tap processing configuration.

        Note: Does not override parent Processing class to avoid inheritance conflicts.
        """

        DEFAULT_PAGE_SIZE: Final[int] = (
            FlextOracleWmsConstants.WmsProcessing.DEFAULT_BATCH_SIZE
        )
        MAX_RECORDS_PER_BATCH: Final[int] = (
            FlextOracleWmsConstants.WmsProcessing.MAX_BATCH_SIZE
        )
        DEFAULT_API_TIMEOUT: Final[int] = FlextMeltanoConstants.DEFAULT_TIMEOUT_SECONDS
        ORACLE_WMS_PAGE_SIZE_LIMIT: Final[int] = 1250
        USERNAME_TRUNCATION_LENGTH: Final[int] = 3
        HIGH_ALLOCATION_THRESHOLD: Final[float] = 0.8
        MEDIUM_ALLOCATION_THRESHOLD: Final[float] = 0.5

    class Extraction:
        """WMS-specific extraction configuration."""

        DEFAULT_ENTITY_LIMIT: Final[int] = (
            FlextOracleWmsConstants.WmsProcessing.DEFAULT_BATCH_SIZE
        )
        DEFAULT_DISCOVERY_TIMEOUT: Final[int] = (
            FlextMeltanoConstants.DEFAULT_TIMEOUT_SECONDS
        )
        MAX_ENTITY_BATCH_SIZE: Final[int] = (
            FlextOracleWmsConstants.WmsProcessing.MAX_BATCH_SIZE
        )

    @unique
    class ReplicationMethod(StrEnum):
        """Replication method types using StrEnum for type safety."""

        FULL_TABLE = "FULL_TABLE"
        INCREMENTAL = "INCREMENTAL"

    @unique
    class AuthenticationMethod(StrEnum):
        """Authentication method types using StrEnum for type safety."""

        BASIC = "basic"
        OAUTH2 = "oauth2"

    @unique
    class StreamInclusion(StrEnum):
        """Stream inclusion status types using StrEnum for type safety."""

        AVAILABLE = "available"
        AUTOMATIC = "automatic"
        UNSUPPORTED = "unsupported"

    @unique
    class BackoffStrategy(StrEnum):
        """Backoff strategy types using StrEnum for type safety."""

        LINEAR = "linear"
        EXPONENTIAL = "exponential"
        FIXED = "fixed"

    type TapWmsEntityTypeLiteral = Literal[
        "INVENTORY",
        "SHIPMENT",
        "PICKING",
        "RECEIVING",
    ]
    "Oracle WMS entity type literal - references WmsEntityType StrEnum members."

    @unique
    class TapProjectType(StrEnum):
        """Project type literals for tap package metadata."""

        SINGER_TAP = "singer-tap"
        WMS_EXTRACTOR = "wms-extractor"
        WAREHOUSE_EXTRACTOR = "warehouse-extractor"
        SINGER_TAP_ORACLE_WMS = "singer-tap-oracle-wms"
        TAP_ORACLE_WMS = "tap-oracle-wms"
        WMS_CONNECTOR = "wms-connector"
        WAREHOUSE_CONNECTOR = "warehouse-connector"
        SINGER_PROTOCOL = "singer-protocol"
        WMS_INTEGRATION = "wms-integration"
        ORACLE_WMS = "oracle-wms"
        WAREHOUSE_MANAGEMENT = "warehouse-management"
        SINGER_STREAM = "singer-stream"
        ETL_TAP = "etl-tap"
        DATA_PIPELINE = "data-pipeline"
        WMS_TAP = "wms-tap"
        SINGER_INTEGRATION = "singer-integration"

    @unique
    class ReplicationMethodLiteral(StrEnum):
        """Replication strategy literals for extraction mode."""

        FULL_TABLE = "FULL_TABLE"
        INCREMENTAL = "INCREMENTAL"

    @unique
    class AuthenticationMethodLiteral(StrEnum):
        """Authentication method literals for endpoint access."""

        BASIC = "basic"
        OAUTH2 = "oauth2"

    @unique
    class StreamInclusionLiteral(StrEnum):
        """Singer stream inclusion policy literals."""

        AVAILABLE = "available"
        AUTOMATIC = "automatic"
        UNSUPPORTED = "unsupported"

    @unique
    class ErrorTypeLiteral(StrEnum):
        """Error category literals for tap failures."""

        AUTHENTICATION = "AUTHENTICATION"
        AUTHORIZATION = "AUTHORIZATION"
        RATE_LIMIT = "RATE_LIMIT"
        TIMEOUT = "TIMEOUT"
        SERVER_ERROR = "SERVER_ERROR"
        NETWORK = "NETWORK"
        VALIDATION = "VALIDATION"

    @unique
    class BackoffStrategyLiteral(StrEnum):
        """Retry backoff strategy literals."""

        LINEAR = "linear"
        EXPONENTIAL = "exponential"
        FIXED = "fixed"

    @unique
    class TestOracleWmsBaseUrl(StrEnum):
        """Test Oracle WMS base URL literals."""

        HTTPS_TEST_WMS_ORACLECLOUD_COM = "https://test-wms.oraclecloud.com"
        HTTPS_STAGING_WMS_ORACLECLOUD_COM = "https://staging-wms.oraclecloud.com"

    @unique
    class TestOracleWmsUsername(StrEnum):
        """Test Oracle WMS username literals."""

        TEST_USER = "test_user"
        REDACTED_LDAP_BIND_PASSWORD_USER = "REDACTED_LDAP_BIND_PASSWORD_user"

    @unique
    class TestOracleWmsMethod(StrEnum):
        """Test HTTP method literals for Oracle WMS calls."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"

    @unique
    class TestFacilityId(StrEnum):
        """Test facility identifier literals."""

        FAC001 = "FAC001"
        FAC002 = "FAC002"
        FAC003 = "FAC003"

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
        ISO_DATE_PATTERN: Final[str] = (
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
        )


c = FlextTapOracleWmsConstants
__all__ = ["FlextTapOracleWmsConstants", "c"]
