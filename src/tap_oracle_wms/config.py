"""Configuration schema for Oracle WMS tap using Singer SDK 0.47.4+.

This module defines the complete configuration schema with all useful Singer SDK
parameters for maximum flexibility and control.
"""

from typing import Any

from singer_sdk import typing as th

# Oracle WMS API constants
WMS_MAX_PAGE_SIZE = 1250
WMS_DEFAULT_PAGE_SIZE = 1000

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
        default="wms.read",
        description="OAuth2 scopes (space-separated)",
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
        default=5,
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
        default=120,
        description="Request timeout in seconds",
    ),
    th.Property(
        "max_retries",
        th.IntegerType,
        default=3,
        description="Maximum number of retry attempts",
    ),
    th.Property(
        "retry_wait_multiplier",
        th.NumberType,
        default=2.0,
        description="Exponential backoff multiplier",
    ),
    th.Property(
        "retry_max_wait",
        th.IntegerType,
        default=60,
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
    th.Property(
        "load_sample_data_batch_size",
        th.IntegerType,
        default=5,
        description="Number of sample records for schema inference",
    ),
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
        default=3600,
        description="Catalog cache TTL in seconds",
    ),
    th.Property(
        "schema_cache_ttl",
        th.IntegerType,
        default=3600,
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
