"""Modern configuration schema for tap-oracle-wms using Singer SDK 0.46.4+ patterns."""
from __future__ import annotations

import logging
from typing import Any

from singer_sdk import typing as th

from .logging_config import (
    get_logger,
    log_exception_context,
    log_function_entry_exit,
)


# Use enhanced logger with TRACE support
logger = get_logger(__name__)


# Constants
WMS_MAX_PAGE_SIZE = 1250
OPTIMAL_PAGE_SIZE = 1000

# HTTP Status Codes
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404

# Quality thresholds
QUALITY_THRESHOLD = 0.1
RATE_THRESHOLD = 0.1

# Auth constants
BASIC_AUTH_PREFIX_LENGTH = 6


# Modern Singer SDK 0.46.4+ Configuration Schema
# ===================================================================
# ENHANCED CONFIGURATION WITH JSON SCHEMA VALIDATION
# ===================================================================

config_schema = th.PropertiesList(
    # === CORE CONNECTION CONFIGURATION ===
    th.Property(
        "base_url",
        th.StringType,
        required=True,
        description="Base URL for Oracle WMS instance (e.g., https://wms.company.com)",
        examples=["https://wms.example.com", "https://prod-wms.company.com"],
        pattern=r"^https?://[a-zA-Z0-9.-]+",  # JSON Schema pattern validation
    ),
    # Authentication configuration
    th.Property(
        "auth_method",
        th.StringType,
        default="basic",
        allowed_values=["basic", "oauth2"],
        description="Authentication method to use (basic or oauth2)",
    ),
    # Basic authentication
    th.Property(
        "username",
        th.StringType,
        required=False,
        secret=True,
        description="Username for basic authentication",
    ),
    th.Property(
        "password",
        th.StringType,
        required=False,
        secret=True,
        description="Password for basic authentication",
    ),
    # OAuth2 authentication
    th.Property(
        "oauth_client_id",
        th.StringType,
        required=False,
        secret=True,
        description="OAuth2 client ID for authentication",
    ),
    th.Property(
        "oauth_client_secret",
        th.StringType,
        required=False,
        secret=True,
        description="OAuth2 client secret for authentication",
    ),
    th.Property(
        "oauth_token_url",
        th.StringType,
        required=False,
        description="OAuth2 token endpoint URL",
    ),
    th.Property(
        "oauth_scope",
        th.StringType,
        required=False,
        default="wms.read",
        description="OAuth2 scopes to request (space-separated)",
    ),
    # WMS context configuration
    th.Property(
        "company_code",
        th.StringType,
        required=False,
        default="*",
        description="WMS company code for context headers "
        "(required: * for all companies, or specific company code)",
    ),
    th.Property(
        "facility_code",
        th.StringType,
        required=False,
        default="*",
        description="WMS facility code for context headers "
        "(required: * for all facilities, or specific facility code)",
    ),
    # Data selection configuration
    th.Property(
        "start_date",
        th.DateTimeType,
        required=False,
        description="Initial data extraction date (ISO 8601 format)",
    ),
    th.Property(
        "entities",
        th.ArrayType(th.StringType),
        required=False,
        description="Specific entities to extract (default: all discovered)",
    ),
    th.Property(
        "entity_patterns",
        th.ObjectType(
            th.Property(
                "include",
                th.ArrayType(th.StringType),
                description="Entity name patterns to include",
            ),
            th.Property(
                "exclude",
                th.ArrayType(th.StringType),
                description="Entity name patterns to exclude",
            ),
        ),
        required=False,
        description="Entity filtering patterns",
    ),
    # Performance configuration
    th.Property(
        "pagination_mode",
        th.StringType,
        default="sequenced",
        allowed_values=["offset", "cursor", "sequenced", "paged"],
        description="Pagination mode: sequenced (cursor-based, recommended), "
        "paged (offset-based), offset (legacy), cursor (legacy)",
    ),
    th.Property(
        "page_size",
        th.IntegerType,
        default=1000,
        description="Number of records per page (recommended: 1000, max 1250)",
    ),
    th.Property(
        "max_parallel_streams",
        th.IntegerType,
        default=5,
        description="Maximum number of parallel stream extractions",
    ),
    th.Property(
        "request_timeout",
        th.IntegerType,
        default=7200,
        description="Request timeout in seconds - 2 hours for massive data extractions",
    ),
    th.Property(
        "connect_timeout",
        th.IntegerType,
        default=30,
        description="Connection timeout in seconds",
    ),
    th.Property(
        "read_timeout",
        th.IntegerType,
        default=120,
        description="Read timeout in seconds",
    ),
    th.Property(
        "retry_count",
        th.IntegerType,
        default=3,
        description="Number of retries for failed requests",
    ),
    th.Property(
        "retry_wait_multiplier",
        th.NumberType,
        default=2.0,
        description="Multiplier for exponential backoff between retries",
    ),
    th.Property(
        "retry_max_wait",
        th.IntegerType,
        default=60,
        description="Maximum wait time between retries in seconds",
    ),
    # SSL and security configuration
    th.Property(
        "verify_ssl",
        th.BooleanType,
        default=True,
        description="Verify SSL certificates",
    ),
    th.Property(
        "ssl_ca_file",
        th.StringType,
        required=False,
        description="Path to SSL CA certificate file",
    ),
    th.Property(
        "ssl_cert_file",
        th.StringType,
        required=False,
        description="Path to SSL client certificate file",
    ),
    th.Property(
        "ssl_key_file",
        th.StringType,
        required=False,
        description="Path to SSL client key file",
    ),
    th.Property(
        "user_agent",
        th.StringType,
        default="tap-oracle-wms/1.0",
        description="User agent string for HTTP requests",
    ),
    # Schema discovery configuration
    th.Property(
        "schema_discovery_method",
        th.StringType,
        default="auto",
        allowed_values=["auto", "describe", "sample"],
        description="Method for discovering entity schemas",
    ),
    th.Property(
        "schema_cache_ttl",
        th.IntegerType,
        default=3600,
        description="Schema cache TTL in seconds",
    ),
    th.Property(
        "entity_cache_ttl",
        th.IntegerType,
        default=7200,
        description="Entity discovery cache TTL in seconds",
    ),
    th.Property(
        "access_cache_ttl",
        th.IntegerType,
        default=1800,
        description="Entity access check cache TTL in seconds",
    ),
    th.Property(
        "schema_sample_size",
        th.IntegerType,
        default=5,
        description="Number of sample records for schema inference",
    ),
    # Field selection configuration
    th.Property(
        "field_selection",
        th.ObjectType(),
        required=False,
        description="Field selection per entity "
        "(e.g., {'item': ['id', 'code', 'description']})",
    ),
    th.Property(
        "values_list_mode",
        th.ObjectType(),
        required=False,
        description="Enable values list mode per entity for minimal data transfer",
    ),
    th.Property(
        "distinct_values",
        th.ObjectType(),
        required=False,
        description="Enable distinct values per entity",
    ),
    th.Property(
        "ordering",
        th.ObjectType(),
        required=False,
        description="Field ordering per entity (e.g., {'item': '-mod_ts,code'})",
    ),
    # Advanced filtering
    th.Property(
        "end_date",
        th.DateTimeType,
        required=False,
        description="End date for data extraction (ISO 8601 format)",
    ),
    th.Property(
        "entity_filters",
        th.ObjectType(),
        required=False,
        description="Entity-specific filters (e.g., {'item': {'active': 'Y'}})",
    ),
    th.Property(
        "advanced_filters",
        th.ObjectType(),
        required=False,
        description="Advanced filters with operators per entity",
    ),
    # Performance optimization
    th.Property(
        "http2_enabled",
        th.BooleanType,
        default=False,
        description="Enable HTTP/2 support",
    ),
    th.Property(
        "compression_enabled",
        th.BooleanType,
        default=True,
        description="Enable HTTP compression",
    ),
    th.Property(
        "connection_pool_size",
        th.IntegerType,
        default=20,
        description="HTTP connection pool size",
    ),
    th.Property(
        "connection_pool_maxsize",
        th.IntegerType,
        default=100,
        description="Maximum HTTP connection pool size",
    ),
    # Monitoring configuration
    th.Property(
        "monitoring",
        th.ObjectType(
            th.Property(
                "enabled",
                th.BooleanType,
                default=False,
                description="Enable monitoring and metrics collection",
            ),
            th.Property(
                "metrics_port",
                th.IntegerType,
                default=9090,
                description="Port for metrics endpoint",
            ),
            th.Property(
                "log_level",
                th.StringType,
                default="INFO",
                description="Monitoring log level",
            ),
        ),
        required=False,
        description="Monitoring and metrics configuration",
    ),
    # Circuit breaker configuration
    th.Property(
        "circuit_breaker",
        th.ObjectType(
            th.Property(
                "enabled",
                th.BooleanType,
                default=True,
                description="Enable circuit breaker pattern",
            ),
            th.Property(
                "failure_threshold",
                th.IntegerType,
                default=5,
                description="Number of failures before opening circuit",
            ),
            th.Property(
                "recovery_timeout",
                th.IntegerType,
                default=60,
                description="Recovery timeout in seconds",
            ),
        ),
        required=False,
        description="Circuit breaker configuration",
    ),
    # Advanced features
    th.Property(
        "verify_entity_access",
        th.BooleanType,
        default=False,
        description="Verify access to each entity before extraction",
    ),
    th.Property(
        "max_concurrent_checks",
        th.IntegerType,
        default=10,
        description="Maximum concurrent entity access checks",
    ),
    th.Property(
        "entity_access_timeout",
        th.IntegerType,
        default=300,
        description="Timeout for entity access checks in seconds",
    ),
    th.Property(
        "max_concurrent_schema_gen",
        th.IntegerType,
        default=20,
        description="Maximum concurrent schema generations",
    ),
    th.Property(
        "schema_generation_timeout",
        th.IntegerType,
        default=600,
        description="Timeout for schema generation in seconds",
    ),
    th.Property(
        "test_connection",
        th.BooleanType,
        default=True,
        description="Test connection during initialization",
    ),
    # Bulk operations (Oracle WMS 25B)
    th.Property(
        "bulk_operations",
        th.ObjectType(
            th.Property(
                "enabled",
                th.BooleanType,
                default=False,
                description="Enable bulk operations support",
            ),
            th.Property(
                "batch_size",
                th.IntegerType,
                default=500,
                description="Batch size for bulk operations",
            ),
        ),
        required=False,
        description="Bulk operations configuration",
    ),
    # Data Extract API (Oracle WMS 25B)
    th.Property(
        "data_extract",
        th.ObjectType(
            th.Property(
                "enabled",
                th.BooleanType,
                default=False,
                description="Enable Data Extract API for object store",
            ),
            th.Property(
                "format",
                th.StringType,
                default="json",
                allowed_values=["json", "csv", "parquet"],
                description="Export format",
            ),
            th.Property(
                "compression",
                th.StringType,
                default="gzip",
                allowed_values=["none", "gzip", "snappy"],
                description="Compression type",
            ),
            th.Property(
                "object_store_config",
                th.ObjectType(),
                required=False,
                description="Object store configuration",
            ),
        ),
        required=False,
        description="Data Extract API configuration",
    ),
    th.Property(
        "default_fields",
        th.ArrayType(th.StringType),
        required=False,
        description="Default fields to select if not specified per entity",
    ),
    # Filtering configuration
    th.Property(
        "global_filters",
        th.ObjectType(),
        required=False,
        description="Global filters to apply to all entities",
    ),
    th.Property(
        "entity_filters",
        th.ObjectType(),
        required=False,
        description="Per-entity filter mappings",
    ),
    # Ordering configuration
    th.Property(
        "default_ordering",
        th.StringType,
        default="id",
        description="Default field for sorting results",
    ),
    th.Property(
        "entity_ordering",
        th.ObjectType(),
        required=False,
        description="Per-entity ordering specifications",
    ),
    # Logging configuration
    th.Property(
        "log_level",
        th.StringType,
        default="INFO",
        allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        description="Logging level",
    ),
    th.Property(
        "log_to_file",
        th.BooleanType,
        default=False,
        description="Whether to log to file",
    ),
    th.Property(
        "log_file_path",
        th.StringType,
        default="tap-oracle-wms.log",
        description="Path to log file",
    ),
    # State management configuration
    th.Property(
        "state_persistence",
        th.ObjectType(
            th.Property(
                "enabled",
                th.BooleanType,
                default=True,
                description="Enable state persistence",
            ),
            th.Property(
                "backend",
                th.StringType,
                default="file",
                description="State backend type",
            ),
            th.Property(
                "path",
                th.StringType,
                default="state.json",
                description="State file path",
            ),
            th.Property(
                "checkpoint_interval",
                th.IntegerType,
                default=1000,
                description="Checkpoint interval",
            ),
        ),
        required=False,
        description="State persistence configuration",
    ),
    # Error handling configuration
    th.Property(
        "error_handling",
        th.ObjectType(
            th.Property(
                "max_errors_per_stream",
                th.IntegerType,
                default=10,
                description="Max errors per stream",
            ),
            th.Property(
                "continue_on_error",
                th.BooleanType,
                default=True,
                description="Continue on error",
            ),
            th.Property(
                "error_log_file",
                th.StringType,
                default="errors.log",
                description="Error log file",
            ),
            th.Property(
                "quarantine_failed_records",
                th.BooleanType,
                default=True,
                description="Quarantine failed records",
            ),
        ),
        required=False,
        description="Error handling configuration",
    ),
    # Monitoring configuration
    th.Property(
        "metrics",
        th.ObjectType(
            th.Property(
                "enabled",
                th.BooleanType,
                default=False,
                description="Enable metrics collection",
            ),
            th.Property(
                "interval_seconds",
                th.IntegerType,
                default=60,
                description="Metrics reporting interval",
            ),
            th.Property(
                "include_entity_metrics",
                th.BooleanType,
                default=True,
                description="Include entity metrics",
            ),
            th.Property(
                "include_performance_metrics",
                th.BooleanType,
                default=True,
                description="Include performance metrics",
            ),
        ),
        required=False,
        description="Metrics collection configuration",
    ),
    # Validation configuration
    th.Property(
        "validate_config",
        th.BooleanType,
        default=True,
        description="Validate configuration on startup",
    ),
    th.Property(
        "test_connection",
        th.BooleanType,
        default=True,
        description="Test WMS connection on startup",
    ),
    # BUSINESS-SPECIFIC CONFIGURATION
    # Business area configuration
    th.Property(
        "business_areas",
        th.ArrayType(th.StringType),
        default=["inventory", "orders", "warehouse"],
        description="Business areas to include (inventory, orders, etc.)",
    ),
    # Inventory management configuration
    th.Property(
        "inventory_tracking",
        th.ObjectType(
            th.Property(
                "include_lot_tracking",
                th.BooleanType,
                default=True,
                description="Include lot tracking",
            ),
            th.Property(
                "include_serial_numbers",
                th.BooleanType,
                default=True,
                description="Include serial numbers",
            ),
            th.Property(
                "include_expiry_dates",
                th.BooleanType,
                default=True,
                description="Include expiry tracking",
            ),
            th.Property(
                "include_cycle_counts",
                th.BooleanType,
                default=False,
                description="Include cycle counts",
            ),
            th.Property(
                "include_adjustments",
                th.BooleanType,
                default=True,
                description="Include inventory adjustments",
            ),
            th.Property(
                "track_inventory_moves",
                th.BooleanType,
                default=False,
                description="Track inventory movements",
            ),
        ),
        description="Inventory tracking configuration",
    ),
    # Order management configuration
    th.Property(
        "order_management",
        th.ObjectType(
            th.Property(
                "include_order_details",
                th.BooleanType,
                default=True,
                description="Include order line details",
            ),
            th.Property(
                "include_allocations",
                th.BooleanType,
                default=True,
                description="Include allocations",
            ),
            th.Property(
                "include_picks",
                th.BooleanType,
                default=True,
                description="Include picking operations",
            ),
            th.Property(
                "include_shipments",
                th.BooleanType,
                default=True,
                description="Include shipments",
            ),
            th.Property(
                "include_returns",
                th.BooleanType,
                default=False,
                description="Include return orders",
            ),
            th.Property(
                "track_order_lifecycle",
                th.BooleanType,
                default=True,
                description="Track complete order lifecycle",
            ),
        ),
        description="Order management configuration",
    ),
    # Warehouse operations configuration
    th.Property(
        "warehouse_operations",
        th.ObjectType(
            th.Property(
                "include_tasks",
                th.BooleanType,
                default=True,
                description="Include warehouse tasks",
            ),
            th.Property(
                "include_labor_tracking",
                th.BooleanType,
                default=False,
                description="Include labor management",
            ),
            th.Property(
                "include_equipment",
                th.BooleanType,
                default=False,
                description="Include equipment tracking",
            ),
            th.Property(
                "include_dock_management",
                th.BooleanType,
                default=False,
                description="Include dock operations",
            ),
            th.Property(
                "include_wave_management",
                th.BooleanType,
                default=False,
                description="Include wave planning",
            ),
            th.Property(
                "track_productivity",
                th.BooleanType,
                default=False,
                description="Track productivity metrics",
            ),
        ),
        description="Warehouse operations configuration",
    ),
    # Performance and discovery configuration
    th.Property(
        "verify_entity_access",
        th.BooleanType,
        default=False,
        description="Verify access to each entity during discovery",
    ),
    th.Property(
        "max_concurrent_discovery",
        th.IntegerType,
        default=20,
        description="Maximum concurrent entity discovery operations",
    ),
    th.Property(
        "max_concurrent_schema_gen",
        th.IntegerType,
        default=30,
        description="Maximum concurrent schema generation operations",
    ),
    th.Property(
        "max_concurrent_checks",
        th.IntegerType,
        default=10,
        description="Maximum concurrent entity access checks",
    ),
    th.Property(
        "entity_access_timeout",
        th.IntegerType,
        default=300,
        description="Timeout for entity access verification (seconds)",
    ),
    th.Property(
        "schema_generation_timeout",
        th.IntegerType,
        default=600,
        description="Timeout for schema generation (seconds)",
    ),
    # Data quality and enrichment
    th.Property(
        "data_quality",
        th.ObjectType(
            th.Property(
                "validate_schemas",
                th.BooleanType,
                default=True,
                description="Validate data against schemas",
            ),
            th.Property(
                "validate_business_rules",
                th.BooleanType,
                default=False,
                description="Apply business rule validation",
            ),
            th.Property(
                "skip_invalid_records",
                th.BooleanType,
                default=True,
                description="Skip invalid records",
            ),
            th.Property(
                "log_validation_errors",
                th.BooleanType,
                default=True,
                description="Log validation errors",
            ),
            th.Property(
                "include_data_lineage",
                th.BooleanType,
                default=False,
                description="Include data lineage tracking",
            ),
        ),
        description="Data quality and validation configuration",
    ),
    th.Property(
        "data_enrichment",
        th.ObjectType(
            th.Property(
                "include_descriptions",
                th.BooleanType,
                default=True,
                description="Include lookup descriptions",
            ),
            th.Property(
                "resolve_foreign_keys",
                th.BooleanType,
                default=False,
                description="Resolve foreign key references",
            ),
            th.Property(
                "calculate_derived_fields",
                th.BooleanType,
                default=False,
                description="Calculate derived fields",
            ),
            th.Property(
                "include_business_context",
                th.BooleanType,
                default=True,
                description="Add business context metadata",
            ),
        ),
        description="Data enrichment configuration",
    ),
    # Incremental sync configuration
    th.Property(
        "enable_incremental",
        th.BooleanType,
        default=True,
        description="Enable incremental sync for timestamp entities",
    ),
    th.Property(
        "replication_key_override",
        th.ObjectType(),
        description="Override replication keys for specific entities",
    ),
    th.Property(
        "incremental_lookback_hours",
        th.IntegerType,
        default=24,
        description="Hours to look back for incremental sync safety buffer",
    ),
    # Date range filtering
    th.Property(
        "date_range",
        th.ObjectType(
            th.Property(
                "start_date",
                th.StringType,
                description="Start date for filtering (ISO 8601)",
            ),
            th.Property(
                "end_date",
                th.StringType,
                description="End date for filtering (ISO 8601)",
            ),
        ),
        description="Date range for data filtering",
    ),
    # Advanced analytics configuration
    th.Property(
        "analytics",
        th.ObjectType(
            th.Property(
                "enable_kpi_calculation",
                th.BooleanType,
                default=False,
                description="Calculate KPIs",
            ),
            th.Property(
                "include_trend_analysis",
                th.BooleanType,
                default=False,
                description="Include trend analysis",
            ),
            th.Property(
                "generate_insights",
                th.BooleanType,
                default=False,
                description="Generate business insights",
            ),
            th.Property(
                "export_dashboards",
                th.BooleanType,
                default=False,
                description="Export dashboard data",
            ),
        ),
        description="Advanced analytics configuration",
    ),
    # Integration and workflow configuration
    th.Property(
        "workflow_integration",
        th.ObjectType(
            th.Property(
                "enable_webhooks",
                th.BooleanType,
                default=False,
                description="Enable webhook notifications",
            ),
            th.Property(
                "webhook_endpoints",
                th.ArrayType(th.StringType),
                description="Webhook endpoint URLs",
            ),
            th.Property(
                "enable_real_time",
                th.BooleanType,
                default=False,
                description="Enable real-time sync",
            ),
            th.Property(
                "integration_mappings",
                th.ObjectType(),
                description="Field mappings for integrations",
            ),
        ),
        description="Workflow and integration configuration",
    ),
).to_dict()


@log_function_entry_exit(log_args=False, log_result=True, level=logging.DEBUG)
@log_exception_context(reraise=False)
def validate_auth_config(config: dict[str, Any]) -> str | None:
    """Validate authentication configuration.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Error message if validation fails, None otherwise

    """
    auth_method = config.get("auth_method", "basic")
    logger.debug("🔧 Validating auth config for method: %s", auth_method)

    if auth_method == "basic":
        logger.trace("🔍 Validating basic authentication credentials")
        username_present = bool(config.get("username"))
        password_present = bool(config.get("password"))

        if not username_present or not password_present:
            error_msg = "Basic authentication requires username and password"
            logger.warning("⚠️ Auth validation failed: %s", error_msg)
            return error_msg

        logger.debug("✅ Basic authentication credentials validated")

    elif auth_method == "oauth2":
        logger.trace("🔍 Validating OAuth2 authentication configuration")
        required = [
            "oauth_client_id",
            "oauth_client_secret",
            "oauth_token_url",
        ]
        missing = [field for field in required if not config.get(field)]

        if missing:
            error_msg = "OAuth2 authentication requires: {}".format(", ".join(missing))
            logger.warning("⚠️ OAuth2 validation failed: %s", error_msg)
            return error_msg

        logger.debug("✅ OAuth2 authentication configuration validated")
    else:
        error_msg = f"Unknown authentication method: {auth_method}"
        logger.error("🚨 Invalid auth method: %s", error_msg)
        return error_msg

    logger.debug("✅ Authentication configuration validation successful")
    return None


@log_function_entry_exit(log_args=False, log_result=True, level=logging.DEBUG)
@log_exception_context(reraise=False)
def validate_pagination_config(config: dict[str, Any]) -> str | None:
    """Validate pagination configuration.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Error message if validation fails, None otherwise

    """
    page_size = config.get("page_size", 100)
    logger.debug("🔧 Validating pagination config with page_size: %s", page_size)
    logger.trace("🔍 Page size limits: min=1, max=%s", WMS_MAX_PAGE_SIZE)

    if page_size < 1:
        error_msg = "Page size must be at least 1"
        logger.error("🚨 Invalid page size: %s (provided: %s)", error_msg, page_size)
        return error_msg

    if page_size > WMS_MAX_PAGE_SIZE:
        error_msg = f"Page size cannot exceed {WMS_MAX_PAGE_SIZE} (Oracle WMS limit)"
        logger.error(
            "🚨 Page size too large: %s (provided: %s)", error_msg, page_size,
        )
        return error_msg

    if page_size > OPTIMAL_PAGE_SIZE:
        logger.info(
            "ℹ️ Large page size configured: %s (recommended: %s for optimal perf)",
            page_size,
            OPTIMAL_PAGE_SIZE,
        )

    logger.debug("✅ Pagination configuration validation successful")
    return None
