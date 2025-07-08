"""Configuration schema for Oracle WMS tap using Singer SDK 0.47.4+.

This module defines the complete configuration schema with all useful Singer SDK
parameters for maximum flexibility and control.
"""

# Oracle WMS API constants - UNLIMITED by default, configurable only for optimization
from __future__ import annotations

import os
from typing import Any

from singer_sdk import typing as th

# API settings - configurable for different WMS versions/environments
WMS_API_VERSION = os.getenv("WMS_API_VERSION", "v10")
WMS_API_PATH_PATTERN = os.getenv("WMS_API_PATH_PATTERN", "/wms/lgfapi/{version}/entity")
WMS_DEFAULT_PAGE_MODE = os.getenv("WMS_DEFAULT_PAGE_MODE", "sequenced")
WMS_DEFAULT_ORDERING = os.getenv("WMS_DEFAULT_ORDERING", "mod_ts")
WMS_DEFAULT_REPLICATION_KEY = os.getenv("WMS_DEFAULT_REPLICATION_KEY", "mod_ts")

# WMS API limits - THESE ARE THE REAL API LIMITS, NOT ARTIFICIAL RESTRICTIONS
WMS_MAX_PAGE_SIZE = int(
    os.getenv("WMS_MAX_PAGE_SIZE", "1250"),
)  # Oracle WMS API real limit
WMS_DEFAULT_PAGE_SIZE = int(
    os.getenv("WMS_DEFAULT_PAGE_SIZE", "100"),
)  # TAP default, meltano project can override

# Performance and reliability constants - for optimization, not limitation
DEFAULT_REQUEST_TIMEOUT = int(os.getenv("WMS_REQUEST_TIMEOUT", "0"))  # 0 = UNLIMITED
DEFAULT_MAX_RETRIES = int(
    os.getenv("WMS_MAX_RETRIES", "10"),
)  # High default for reliability
DEFAULT_RETRY_WAIT_MULTIPLIER = float(os.getenv("WMS_RETRY_WAIT_MULTIPLIER", "2.0"))
DEFAULT_RETRY_MAX_WAIT = int(
    os.getenv("WMS_RETRY_MAX_WAIT", "300"),
)  # 5 minutes max wait
DEFAULT_HTTP_CLIENT_TIMEOUT = int(
    os.getenv("WMS_HTTP_CLIENT_TIMEOUT", "300"),
)  # 5 minutes

# OAuth and security constants
DEFAULT_OAUTH_SCOPE = os.getenv("WMS_OAUTH_SCOPE", "wms.read")
DEFAULT_TOKEN_BUFFER_SECONDS = int(os.getenv("WMS_TOKEN_BUFFER_SECONDS", "30"))
USER_AGENT_STRING = os.getenv("WMS_USER_AGENT", "tap-oracle-wms/1.0.0")

# Cache settings - long TTL by default for performance
DEFAULT_CATALOG_CACHE_TTL = int(os.getenv("WMS_CATALOG_CACHE_TTL", "14400"))  # 4 hours
DEFAULT_SCHEMA_CACHE_TTL = int(os.getenv("WMS_SCHEMA_CACHE_TTL", "14400"))  # 4 hours
DEFAULT_INCREMENTAL_OVERLAP = int(os.getenv("WMS_INCREMENTAL_OVERLAP_MINUTES", "30"))
DEFAULT_LOOKBACK_MINUTES = int(os.getenv("WMS_LOOKBACK_MINUTES", "5"))

# REMOVED: PROGRESS_LOG_FREQUENCY - SEM LIMITAÇÕES DE LOG

# REMOVED ALL ARTIFICIAL SCHEMA LIMITS - UNLIMITED FIELDS AND DATA
# NO MAX_STRING_LENGTH - Oracle supports up to 32KB in VARCHAR2, CLOB is unlimited
# NO MAX_TEXT_LENGTH - CLOB is unlimited
# NO SIMPLE_OBJECT_MAX_FIELDS - unlimited fields allowed
# 🚨 SCHEMA DISCOVERY: HARD-CODED to use ONLY API metadata describe
# No other methods exist

# REMOVED ALL ARTIFICIAL LIMITATIONS - SISTEMA COMPLETAMENTE ILIMITADO
# NO MAX_PARAM_KEY_LENGTH - aceita qualquer tamanho
# NO MAX_REASONABLE_ID - aceita qualquer ID que o WMS fornecer
# NO MIN_USERNAME_LENGTH - aceita qualquer username
# NO MIN_PASSWORD_LENGTH - aceita qualquer password
# NO MAX_OVERLAP_MINUTES - aceita qualquer overlap necessário

# Default retry behavior - ÚNICA configuração que faz sentido
DEFAULT_RETRY_AFTER = int(os.getenv("WMS_DEFAULT_RETRY_AFTER", "60"))

# 🚨 SCHEMA DISCOVERY: HARD-CODED to use ONLY API metadata describe
# This tap uses EXCLUSIVELY API metadata - this is not configurable
# NO other methods exist or are mentioned in this codebase

# HTTP status codes
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_TOO_MANY_REQUESTS = 429


def validate_auth_config(config: dict[str, Any]) -> bool:
    """Validate authentication configuration."""
    auth_method = config.get("auth_method", "basic")

    if auth_method == "basic":
        return bool(config.get("username") and config.get("password"))
    if auth_method == "oauth2":
        return bool(
            config.get("oauth_client_id")
            and config.get("oauth_client_secret")
            and config.get("oauth_token_url"),
        )

    return False


def validate_pagination_config(config: dict[str, Any]) -> bool:
    """Validate pagination configuration."""
    page_size = config.get("page_size", WMS_DEFAULT_PAGE_SIZE)
    return bool(1 <= page_size <= WMS_MAX_PAGE_SIZE)


# Complete configuration schema with all useful Singer SDK parameters
config_jsonschema = th.PropertiesList(
    # === CORE CONNECTION SETTINGS ===
    th.Property(
        "base_url",
        th.StringType,
        required=True,
        description="Base URL for Oracle WMS instance (e.g., https://wms.company.com)",
        examples=["https://wms.example.com", "https://prod-wms.company.com"],
    ),
    # === AUTHENTICATION ===
    th.Property(
        "auth_method",
        th.StringType,
        default="basic",
        allowed_values=["basic", "oauth2"],
        description="Authentication method to use",
    ),
    th.Property(
        "username",
        th.StringType,
        secret=True,
        description="Username for basic authentication",
    ),
    th.Property(
        "password",
        th.StringType,
        secret=True,
        description="Password for basic authentication",
    ),
    th.Property(
        "oauth_client_id",
        th.StringType,
        secret=True,
        description="OAuth2 client ID",
    ),
    th.Property(
        "oauth_client_secret",
        th.StringType,
        secret=True,
        description="OAuth2 client secret",
    ),
    th.Property(
        "oauth_token_url",
        th.StringType,
        description="OAuth2 token endpoint URL",
    ),
    th.Property(
        "oauth_scope",
        th.StringType,
        default=DEFAULT_OAUTH_SCOPE,
        description="OAuth2 scopes (space-separated)",
    ),
    # === WMS API SETTINGS ===
    th.Property(
        "wms_api_version",
        th.StringType,
        default=WMS_API_VERSION,
        description="WMS API version to use",
    ),
    th.Property(
        "wms_api_path_pattern",
        th.StringType,
        default=WMS_API_PATH_PATTERN,
        description="WMS API path pattern with {version} placeholder",
    ),
    th.Property(
        "page_mode",
        th.StringType,
        default=WMS_DEFAULT_PAGE_MODE,
        description="Pagination mode: sequenced or standard",
    ),
    th.Property(
        "ordering",
        th.StringType,
        default=WMS_DEFAULT_ORDERING,
        description="Default field for ordering results",
    ),
    th.Property(
        "replication_key",
        th.StringType,
        default=WMS_DEFAULT_REPLICATION_KEY,
        description="Field to use for incremental replication",
    ),
    # === WMS CONTEXT ===
    th.Property(
        "company_code",
        th.StringType,
        default="*",
        description="WMS company code (* for all companies)",
    ),
    th.Property(
        "facility_code",
        th.StringType,
        default="*",
        description="WMS facility code (* for all facilities)",
    ),
    # === ENTITY SELECTION ===
    th.Property(
        "entities",
        th.ArrayType(th.StringType),
        description="Specific entities to extract (default: auto-discover all)",
    ),
    th.Property(
        "entity_patterns",
        th.ObjectType(
            th.Property("include", th.ArrayType(th.StringType)),
            th.Property("exclude", th.ArrayType(th.StringType)),
        ),
        description="Entity filtering patterns (supports wildcards)",
    ),
    th.Property(
        "entity_filters",
        th.ObjectType(),
        description=(
            "Entity-specific filters (e.g., {'allocation': {'status': 'active'}})"
        ),
    ),
    # === INCREMENTAL SYNC ===
    th.Property(
        "start_date",
        th.DateTimeType,
        description="Start date for data extraction (ISO 8601)",
    ),
    th.Property(
        "enable_incremental",
        th.BooleanType,
        default=True,
        description="Enable incremental sync using MOD_TS field",
    ),
    th.Property(
        "incremental_overlap_minutes",
        th.IntegerType,
        default=DEFAULT_INCREMENTAL_OVERLAP,
        description="Safety overlap in minutes for incremental sync",
    ),
    # === PERFORMANCE SETTINGS ===
    th.Property(
        "page_size",
        th.IntegerType,
        default=WMS_DEFAULT_PAGE_SIZE,
        description=f"Records per page (1-{WMS_MAX_PAGE_SIZE})",
    ),
    th.Property(
        "request_timeout",
        th.IntegerType,
        default=DEFAULT_REQUEST_TIMEOUT,
        description="Request timeout in seconds",
    ),
    th.Property(
        "max_retries",
        th.IntegerType,
        default=DEFAULT_MAX_RETRIES,
        description="Maximum number of retry attempts",
    ),
    th.Property(
        "retry_wait_multiplier",
        th.NumberType,
        default=DEFAULT_RETRY_WAIT_MULTIPLIER,
        description="Exponential backoff multiplier",
    ),
    th.Property(
        "retry_max_wait",
        th.IntegerType,
        default=DEFAULT_RETRY_MAX_WAIT,
        description="Maximum wait time between retries (seconds)",
    ),
    # === ADVANCED SINGER SDK FEATURES ===
    th.Property(
        "stream_maps",
        th.ObjectType(),
        description="Inline transformations using Singer SDK stream maps",
    ),
    th.Property(
        "stream_map_config",
        th.ObjectType(),
        description="Additional stream map configuration",
    ),
    th.Property(
        "state_partitioning_keys",
        th.ArrayType(th.StringType),
        description="Keys for partitioned state management",
    ),
    # 🚨 SCHEMA DISCOVERY: HARD-CODED to use ONLY API metadata describe
    # This functionality is not configurable
    # No environment variables or config options exist
    # === DISCOVERY SETTINGS ===
    th.Property(
        "discover_catalog",
        th.BooleanType,
        default=True,
        description="Auto-discover catalog on startup",
    ),
    th.Property(
        "catalog_cache_ttl",
        th.IntegerType,
        default=DEFAULT_CATALOG_CACHE_TTL,
        description="Catalog cache TTL in seconds",
    ),
    th.Property(
        "schema_cache_ttl",
        th.IntegerType,
        default=DEFAULT_SCHEMA_CACHE_TTL,
        description="Schema cache TTL in seconds",
    ),
    # === SSL/TLS SETTINGS ===
    th.Property(
        "verify_ssl",
        th.BooleanType,
        default=True,
        description="Verify SSL certificates",
    ),
    th.Property(
        "ssl_ca_file",
        th.StringType,
        description="Path to CA bundle file",
    ),
    # === LOGGING AND MONITORING ===
    th.Property(
        "log_level",
        th.StringType,
        default="INFO",
        allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        description="Logging level",
    ),
    th.Property(
        "metrics_log_level",
        th.StringType,
        default="INFO",
        allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        description="Metrics logging level",
    ),
    # === FLATTENING SETTINGS ===
    th.Property(
        "flattening_enabled",
        th.BooleanType,
        default=True,
        description="Enable automatic schema flattening",
    ),
    th.Property(
        "flattening_max_depth",
        th.IntegerType,
        default=3,
        description="Maximum depth for schema flattening",
    ),
    # === VALIDATION SETTINGS ===
    th.Property(
        "validate_records",
        th.BooleanType,
        default=True,
        description="Validate records against schema",
    ),
    # === DEVELOPER SETTINGS ===
    th.Property(
        "dev_mode",
        th.BooleanType,
        default=False,
        description="Enable developer mode with additional logging",
    ),
    th.Property(
        "mock_api_calls",
        th.BooleanType,
        default=False,
        description="Mock API calls for testing",
    ),
).to_dict()
