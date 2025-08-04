"""Configuration mapper for transforming hardcoded specifications.

Copyright (c) 2025 FLEXT Team
Licensed under the MIT License

Transforms hardcoded values into configurable parameters.

This module identifies and externalizes hardcoded values throughout the codebase,
making them configurable through environment variables or profile settings.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TypedDict, Union, cast

from flext_core import get_logger

# Constants
MAX_PAGE_SIZE = 1250
MAX_REQUEST_TIMEOUT = 600
MAX_RETRIES = 10

logger = get_logger(__name__)


class ConfigTemplate(TypedDict):
    """Type definition for configuration template structure."""

    env_var: str
    default: str | int | float | bool | dict[str, object] | list[object]
    profile_path: str
    type: str


# =============================================================================
# REFACTORING: Parameter Object Pattern for reducing method complexity
# =============================================================================


@dataclass
class ConfigValueRequest:
    """Parameter Object: Encapsulates configuration value request data.

    SOLID REFACTORING: Reduces parameter count in configuration methods
    using Parameter Object Pattern.
    """

    key: str
    env_var: str | None = None
    default: object = None
    profile_path: str | None = None


@dataclass
class WmsStatusMappingConfig:
    """Parameter Object: Configuration for WMS status mapping operations.

    SOLID REFACTORING: Centralizes status mapping configuration to eliminate
    duplicated code between allocation and order status mapping methods.
    """

    mapping_name: str
    env_var: str
    profile_path: str
    default_mapping: dict[str, str]


# Configuration Templates - SOLID DRY refactoring
CONFIG_TEMPLATES: dict[str, ConfigTemplate] = {
    "max_retries": {
        "env_var": "WMS_MAX_RETRIES",
        "default": 3,
        "profile_path": "performance.max_retries",
        "type": "int",
    },
    "cache_ttl_seconds": {
        "env_var": "WMS_CACHE_TTL_SECONDS",
        "default": 3600,
        "profile_path": "performance.cache_ttl_seconds",
        "type": "int",
    },
    "connection_pool_size": {
        "env_var": "WMS_CONNECTION_POOL_SIZE",
        "default": 5,
        "profile_path": "performance.connection_pool_size",
        "type": "int",
    },
    "incremental_overlap_minutes": {
        "env_var": "WMS_INCREMENTAL_OVERLAP_MINUTES",
        "default": 5,
        "profile_path": "sync.incremental_overlap_minutes",
        "type": "int",
    },
    "lookback_minutes": {
        "env_var": "WMS_LOOKBACK_MINUTES",
        "default": 10,
        "profile_path": "sync.lookback_minutes",
        "type": "int",
    },
    "fiscal_year_start_month": {
        "env_var": "WMS_FISCAL_YEAR_START_MONTH",
        "default": 1,
        "profile_path": "business.fiscal_year_start_month",
        "type": "int",
    },
    "allocation_status_mapping": {
        "env_var": "WMS_ALLOCATION_STATUS_MAPPING",
        "default": {
            "10": "available",
            "20": "allocated",
            "30": "picked",
            "40": "shipped",
        },
        "profile_path": "mappings.allocation_status",
        "type": "dict",
    },
    "order_status_mapping": {
        "env_var": "WMS_ORDER_STATUS_MAPPING",
        "default": {
            "10": "created",
            "20": "released",
            "30": "allocated",
            "40": "picked",
            "50": "shipped",
        },
        "profile_path": "mappings.order_status",
        "type": "dict",
    },
}


def _create_int_config_template(
    config_key: str,
    env_var: str,
    default_value: int,
    profile_path: str,
) -> ConfigValueRequest:
    """Template Method: Create integer configuration request.

    DEPRECATED: Use _get_templated_config_value instead for DRY compliance.
    """
    return ConfigValueRequest(
        key=config_key,
        env_var=env_var,
        default=default_value,
        profile_path=profile_path,
    )


def _safe_int_conversion_with_validation(value: object, default: int) -> int:
    """DRY Helper: Safely convert value to integer - delegates to flext-core.

    SOLID REFACTORING: Eliminates duplication by using centralized utility
    from flext-core across all FLEXT ecosystem projects.
    """
    # REFACTORING: Use centralized utility from flext-core
    from flext_core.utilities import safe_int_conversion_with_default

    return safe_int_conversion_with_default(value, default)


class ConfigMapper:
    """Maps hardcoded specifications to configurable parameters.

    This class has many methods due to the extensive WMS configuration options.
    Each method group handles a specific aspect of WMS configuration.
    """

    def __init__(self, profile_config: dict[str, object] | None = None) -> None:
        """Initialize ConfigMapper with optional profile configuration.

        Args:
            profile_config: Optional configuration profile dictionary

        """
        self.profile_config = profile_config or {}
        self._config_cache: dict[str, object] = {}

    def _get_templated_config_value(self, template_key: str) -> str | int | float | bool | dict[str, object] | list[object]:
        """Template Method Pattern: Get configuration value using predefined template.

        SOLID REFACTORING: Eliminates 21 lines of duplication in config methods.

        Args:
            template_key: Key from CONFIG_TEMPLATES

        Returns:
            Configuration value with appropriate type conversion

        """
        if template_key not in CONFIG_TEMPLATES:
            msg: str = f"Unknown config template: {template_key}"
            raise ValueError(msg)

        template = CONFIG_TEMPLATES[template_key]

        value = self._get_config_value(
            template_key,
            env_var=template["env_var"],
            default=template["default"],
            profile_path=template["profile_path"],
        )

        # Type conversion based on template
        if template["type"] == "int":
            if isinstance(value, int):
                return value
            if isinstance(template["default"], int):
                return _safe_int_conversion_with_validation(int(value) if isinstance(value, (str, float)) else 0, template["default"])
            return int(value) if isinstance(value, (str, float)) else 0
        if template["type"] == "dict":
            if isinstance(value, dict):
                return value
            return template["default"]
        # For other types, return the value as-is with proper type casting
        from typing import cast
        return cast("str | int | float | bool | dict[str, object] | list[object]", value)

    # Connection Configuration

    def get_base_url(self) -> str:
        """Get Oracle WMS base URL from configuration.

        Returns:
            Base URL for Oracle WMS API endpoints.

        """
        return str(
            self._get_config_value(
                "base_url",
                env_var="TAP_ORACLE_WMS_BASE_URL",
                default="",
                profile_path="api.base_url",
            ),
        )

    def get_username(self) -> str:
        """Get Oracle WMS username from configuration.

        Returns:
            Username for Oracle WMS authentication.

        """
        return str(
            self._get_config_value(
                "username",
                env_var="TAP_ORACLE_WMS_USERNAME",
                default="",
                profile_path="api.username",
            ),
        )

    def get_password(self) -> str:
        """Get Oracle WMS password from configuration.

        Returns:
            Password for Oracle WMS authentication.

        """
        return str(
            self._get_config_value(
                "password",
                env_var="TAP_ORACLE_WMS_PASSWORD",
                default="",
                profile_path="api.password",
            ),
        )

    # API Configuration

    def get_api_version(self) -> str:
        """Get Oracle WMS API version from configuration.

        Returns:
            API version string for WMS endpoints.

        """
        return str(
            self._get_config_value(
                "api_version",
                env_var="WMS_API_VERSION",
                default="v10",
                profile_path="api.version",
            ),
        )

    def get_endpoint_prefix(self) -> str:
        """Get Oracle WMS endpoint prefix from configuration.

        Returns:
            Endpoint prefix for WMS API paths.

        """
        return str(
            self._get_config_value(
                "endpoint_prefix",
                env_var="WMS_ENDPOINT_PREFIX",
                default="/wms/lgfapi",
                profile_path="api.endpoint_prefix",
            ),
        )

    def get_entity_endpoint_pattern(self) -> str:
        """Get Oracle WMS entity endpoint pattern from configuration.

        Returns:
            URL pattern template for entity-specific API endpoints.

        """
        return str(
            self._get_config_value(
                "entity_endpoint_pattern",
                env_var="WMS_ENTITY_ENDPOINT_PATTERN",
                default="/{prefix}/{version}/entity/{entity}",
                profile_path="api.entity_endpoint_pattern",
            ),
        )

    def get_authentication_method(self) -> str:
        """Get Oracle WMS authentication method from configuration.

        Returns:
            Authentication method type (basic, oauth, token) for WMS API.

        """
        return str(
            self._get_config_value(
                "auth_method",
                env_var="WMS_AUTH_METHOD",
                default="basic",
                profile_path="api.authentication_method",
            ),
        )

    # Performance Configuration

    def get_page_size(self) -> int:
        """Get page size for API pagination.

        Returns:
            Number of records per page for WMS API requests.

        """
        value = self._get_config_value(
            "page_size",
            env_var="WMS_PAGE_SIZE",
            default=500,  # WMS performance default
            profile_path="performance.page_size",
        )
        result = self._safe_int_conversion(value, 100)
        # Cap at maximum page size
        return min(result, MAX_PAGE_SIZE)

    def get_max_page_size(self) -> int:
        """Get maximum page size allowed by Oracle WMS API.

        Returns:
            Maximum number of records per page supported by WMS.

        """
        value = self._get_config_value(
            "max_page_size",
            env_var="WMS_MAX_PAGE_SIZE",
            default=MAX_PAGE_SIZE,  # Oracle WMS API real maximum limit
            profile_path="performance.max_page_size",
        )
        return self._safe_int_conversion(value, MAX_PAGE_SIZE)

    def get_request_timeout(self) -> int:
        """Get request timeout in seconds.

        Returns:
            Timeout value for HTTP requests to WMS API.

        """
        value = self._get_config_value(
            "request_timeout",
            env_var="WMS_REQUEST_TIMEOUT",
            default=MAX_REQUEST_TIMEOUT,  # UNLIMITED: 10 minutes for large datasets
            profile_path="performance.request_timeout",
        )
        return self._safe_int_conversion(value, MAX_REQUEST_TIMEOUT)

    @staticmethod
    def _safe_int_conversion(value: object, default: int) -> int:
        """Safely convert value to integer - delegates to flext-core.

        SOLID REFACTORING: Eliminates duplication by using centralized utility
        from flext-core across all FLEXT ecosystem projects.

        Args:
            value: Value to convert to integer.
            default: Default value if conversion fails.

        Returns:
            Integer value or default if conversion fails.

        """
        # REFACTORING: Use centralized utility from flext-core
        from flext_core.utilities import safe_int_conversion_with_default

        return safe_int_conversion_with_default(value, default)

    def get_max_retries(self) -> int:
        """Get maximum number of retries for failed requests.

        Returns:
            Maximum retry attempts for HTTP requests.

        """
        return cast("int", self._get_templated_config_value("max_retries"))

    def get_retry_backoff_factor(self) -> float:
        """Get exponential backoff factor for retries.

        Returns:
            Multiplier for exponential backoff between retry attempts.

        """
        value = self._get_config_value(
            "retry_backoff_factor",
            env_var="WMS_RETRY_BACKOFF_FACTOR",
            default=1.5,
            profile_path="performance.retry_backoff_factor",
        )
        if isinstance(value, int | float):
            return float(value)
        try:
            return float(str(value))
        except ValueError:
            pass
        return 1.5  # default

    def get_cache_ttl_seconds(self) -> int:
        """Get cache time-to-live in seconds.

        Returns:
            Duration in seconds for caching API responses.

        """
        return cast("int", self._get_templated_config_value("cache_ttl_seconds"))

    def get_connection_pool_size(self) -> int:
        """Get HTTP connection pool size for WMS API.

        Returns:
            Maximum number of concurrent connections to maintain.

        """
        return cast("int", self._get_templated_config_value("connection_pool_size"))

    # Business Logic Configuration

    def get_replication_key(self) -> str:
        """Get default replication key for incremental sync.

        Returns:
            Field name to use for incremental data extraction.

        """
        return str(
            self._get_config_value(
                "replication_key",
                env_var="WMS_REPLICATION_KEY",
                default="mod_ts",
                profile_path="business_rules.default_replication_key",
            ),
        )

    def get_pagination_mode(self) -> str:
        """Get pagination mode for WMS API requests.

        Returns:
            Pagination strategy (sequenced, offset, cursor) for data retrieval.

        """
        return str(
            self._get_config_value(
                "page_mode",
                env_var="WMS_PAGE_MODE",
                default="sequenced",
                profile_path="business_rules.pagination_mode",
            ),
        )

    def get_incremental_overlap_minutes(self) -> int:
        """Get incremental sync overlap window in minutes.

        Returns:
            Minutes to overlap with previous sync to avoid missed records.

        """
        return cast(
            "int",
            self._get_templated_config_value("incremental_overlap_minutes"),
        )

    def get_lookback_minutes(self) -> int:
        """Get lookback window for incremental sync start time.

        Returns:
            Minutes to look back from last bookmark for safety margin.

        """
        return cast("int", self._get_templated_config_value("lookback_minutes"))

    # Entity Configuration

    def get_enabled_entities(self) -> list[str]:
        """Get list of WMS entities enabled for extraction.

        Returns:
            List of entity names to extract from Oracle WMS.

        """
        entities_str = self._get_config_value(
            "entities",
            env_var="WMS_ENTITIES",
            default="allocation,order_hdr,order_dtl",
            profile_path="entities",
        )

        if isinstance(entities_str, list):
            return entities_str

        if isinstance(entities_str, str):
            return [e.strip() for e in entities_str.split(",")]

        return ["allocation", "order_hdr", "order_dtl"]

    def get_entity_primary_keys(self, entity_name: str) -> list[str]:
        """Get primary keys for specific WMS entity.

        Args:
            entity_name: Name of the WMS entity.

        Returns:
            List of field names that form the primary key.

        """
        # Try entity-specific configuration first
        keys_str = self._get_config_value(
            f"entity_{entity_name}_primary_keys",
            env_var=f"WMS_ENTITY_{entity_name.upper()}_PRIMARY_KEYS",
            default=None,
            profile_path=f"entities.{entity_name}.primary_keys",
        )

        if keys_str:
            if isinstance(keys_str, list):
                return keys_str
            if isinstance(keys_str, str):
                return [k.strip() for k in keys_str.split(",")]

        # Fallback to default primary keys per entity
        entity_defaults = {
            "allocation": ["company_code", "facility_code", "allocation_id"],
            "order_hdr": ["company_code", "facility_code", "order_nbr"],
            "order_dtl": [
                "company_code",
                "facility_code",
                "order_nbr",
                "order_line_nbr",
            ],
            "item_master": ["company_code", "item_id"],
        }

        return entity_defaults.get(entity_name, ["id"])

    # Headers Configuration

    def get_custom_headers(self) -> dict[str, str]:
        """Get HTTP headers for WMS API requests.

        Returns:
            Dictionary of headers including content type, user agent, and company.

        """
        headers: dict[str, str] = {}

        # Standard headers (previously hardcoded)
        headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": str(
                    self._get_config_value(
                        "user_agent",
                        env_var="WMS_USER_AGENT",
                        default="tap-oracle-wms/0.2.0",
                        profile_path="api.user_agent",
                    ),
                ),
            },
        )

        # Company context headers
        company_code = self._get_config_value(
            "company_code",
            env_var="WMS_COMPANY_CODE",
            default="*",
            profile_path="company_code",
        )

        facility_code = self._get_config_value(
            "facility_code",
            env_var="WMS_FACILITY_CODE",
            default="*",
            profile_path="facility_code",
        )

        headers.update(
            {
                "X-WMS-Company": str(company_code),
                "X-WMS-Facility": str(facility_code),
            },
        )

        # Additional custom headers from profile or environment
        custom_headers = self._get_config_value(
            "custom_headers",
            env_var="WMS_CUSTOM_HEADERS_JSON",
            default={},
            profile_path="api.custom_headers",
        )

        # If already a dict, use directly; otherwise try to parse JSON
        if not isinstance(custom_headers, dict):
            try:
                custom_headers = json.loads(str(custom_headers))
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in WMS_CUSTOM_HEADERS_JSON, ignoring")
                custom_headers = {}

        if isinstance(custom_headers, dict):
            # Ensure all custom header values are strings
            for key, value in custom_headers.items():
                headers[str(key)] = str(value)
        return headers

    # OAuth Configuration

    def get_oauth_scope(self) -> str:
        """Get OAuth scope for WMS API authentication.

        Returns:
            OAuth scope string for WMS resource access.

        """
        return str(
            self._get_config_value(
                "oauth_scope",
                env_var="WMS_OAUTH_SCOPE",
                default=(
                    "https://instance.wms.ocs.oraclecloud.com:443/"
                    "urn:opc:resource:consumer:all"
                ),
                profile_path="api.oauth_scope",
            ),
        )

    # Database/Target Configuration

    # 🚨 CRITICAL: get_target_schema METHOD PERMANENTLY DELETED
    # TAP must NOT know about target/destination schemas - Singer SDK separation of
    # concerns

    def get_table_prefix(self) -> str:
        """Get table prefix for WMS data tables.

        Returns:
            Prefix string to prepend to table names.

        """
        return str(
            self._get_config_value(
                "table_prefix",
                env_var="WMS_TABLE_PREFIX",
                default="WMS_",
                profile_path="table_prefix",
            ),
        )

    # Status Mapping Configuration

    def get_allocation_status_mapping(self) -> dict[str, str]:
        """Get allocation status mapping from WMS to standardized values.

        Returns:
            Dictionary mapping WMS allocation statuses to standardized status names.

        """
        return cast(
            "dict[str, str]",
            self._get_templated_config_value("allocation_status_mapping"),
        )

    def get_order_status_mapping(self) -> dict[str, str]:
        """Get order status mapping from WMS to standardized values.

        Returns:
            Dictionary mapping WMS order statuses to standardized status names.

        """
        return cast(
            "dict[str, str]",
            self._get_templated_config_value("order_status_mapping"),
        )

    # Field Type Patterns

    def get_field_type_patterns(self) -> dict[str, str]:
        """Get field type patterns for SQL schema generation.

        Returns:
            Dictionary mapping field name patterns to SQL data types.

        """
        patterns = self._get_config_value(
            "field_type_patterns",
            env_var="WMS_FIELD_TYPE_PATTERNS_JSON",
            default={
                "_id$": "INTEGER",
                "_qty$": "DECIMAL(15,3)",
                "_flg$": "CHAR(1)",
                "_ts$": "TIMESTAMP",
                "_code$": "VARCHAR(50)",
                "_desc$": "VARCHAR(500)",
            },
            profile_path="business_rules.field_type_patterns",
        )
        try:
            patterns = json.loads(str(patterns))
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in field type patterns, using defaults")
            patterns = {
                "_id$": "INTEGER",
                "_qty$": "DECIMAL(15,3)",
                "_flg$": "CHAR(1)",
                "_ts$": "TIMESTAMP",
                "_code$": "VARCHAR(50)",
                "_desc$": "VARCHAR(500)",
            }

        if isinstance(patterns, dict):
            return patterns
        return {
            "_id$": "INTEGER",
            "_qty$": "DECIMAL(15,3)",
            "_flg$": "CHAR(1)",
            "_ts$": "TIMESTAMP",
            "_code$": "VARCHAR(50)",
            "_desc$": "VARCHAR(500)",
        }

    # Company-Specific Settings

    def get_company_timezone(self) -> str:
        """Get company timezone for timestamp conversion.

        Returns:
            Timezone string (e.g., 'UTC', 'America/New_York') for data processing.

        """
        return str(
            self._get_config_value(
                "company_timezone",
                env_var="WMS_COMPANY_TIMEZONE",
                default="UTC",
                profile_path="business_rules.company_timezone",
            ),
        )

    def get_currency_code(self) -> str:
        """Get default currency code for financial data.

        Returns:
            ISO currency code (e.g., 'USD', 'EUR') for monetary values.

        """
        return str(
            self._get_config_value(
                "currency_code",
                env_var="WMS_CURRENCY_CODE",
                default="USD",
                profile_path="business_rules.currency_code",
            ),
        )

    def get_fiscal_year_start_month(self) -> int:
        """Get fiscal year start month for business reporting.

        Returns:
            Month number (1-12) when fiscal year begins.

        """
        return cast("int", self._get_templated_config_value("fiscal_year_start_month"))

    def get_company_code(self) -> str:
        """Get Oracle WMS company code from configuration.

        Returns:
            Company code for multi-tenant WMS filtering.

        """
        return str(
            self._get_config_value(
                "company_code",
                env_var="WMS_COMPANY_CODE",
                default="*",
            ),
        )

    def get_facility_code(self) -> str:
        """Get Oracle WMS facility code from configuration.

        Returns:
            Facility code for location-specific data filtering.

        """
        return str(
            self._get_config_value(
                "facility_code",
                env_var="WMS_FACILITY_CODE",
                default="*",
            ),
        )

    def _process_status_mapping_template(
        self,
        config: WmsStatusMappingConfig,
    ) -> dict[str, str]:
        """Template Method Pattern: Common status mapping processing logic.

        SOLID REFACTORING: Eliminates 82 lines of duplicated code between
        allocation and order status mapping methods using Template Method pattern.
        """
        mapping = self._get_config_value(
            config.mapping_name,
            env_var=config.env_var,
            default=config.default_mapping,
            profile_path=config.profile_path,
        )

        # Handle JSON parsing if needed
        if not isinstance(mapping, dict):
            try:
                mapping = json.loads(str(mapping))
            except json.JSONDecodeError:
                logger.warning(
                    f"Invalid JSON in {config.mapping_name}, using defaults",
                )
                mapping = config.default_mapping

        # Validate and return with fallback
        if isinstance(mapping, dict):
            return mapping
        return config.default_mapping

    # Utility Methods

    def _get_config_value(
        self,
        key: str,
        env_var: str | None = None,
        default: object = None,
        profile_path: str | None = None,
    ) -> object:
        # Check cache first
        cache_key = f"{key}_{env_var}_{profile_path}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]

        value = default

        # Check direct key in profile configuration first (highest precedence)
        if self.profile_config and key in self.profile_config:
            value = self.profile_config[key]
        # Check nested profile configuration path only if direct key not found
        elif profile_path and self.profile_config:
            nested_value = self._get_nested_value(self.profile_config, profile_path)
            if nested_value is not None:
                value = nested_value

        # Check environment variable (highest precedence)
        if env_var:
            env_value = os.getenv(env_var)
            if env_value is not None:
                value = env_value

        # Cache the result
        self._config_cache[cache_key] = value

        return value

    @staticmethod
    def _get_nested_value(data: dict[str, object], path: str) -> object | None:
        """Get value from nested dictionary using dot notation.

        Args:
            data: Dictionary to search
            path: Dot-notation path (e.g., 'api.version')

        Returns:
            Value if found, None otherwise

        """
        path_keys = path.split(".")
        current: object = data
        try:
            for key in path_keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
        except (KeyError, TypeError):
            return None
        return current

    def get_all_config(self) -> dict[str, object]:
        """Get all configuration values as a consolidated dictionary.

        Returns:
            Dictionary containing all configuration values for WMS tap.

        """
        return {
            # Connection (most important - must be first)
            "base_url": self.get_base_url(),
            "username": self.get_username(),
            "password": self.get_password(),
            # API
            "api_version": self.get_api_version(),
            "endpoint_prefix": self.get_endpoint_prefix(),
            "auth_method": self.get_authentication_method(),
            # Performance - ensure proper types
            "page_size": int(self.get_page_size()),
            "max_page_size": int(self.get_max_page_size()),
            "request_timeout": int(self.get_request_timeout()),
            "max_retries": int(self.get_max_retries()),
            "cache_ttl_seconds": int(self.get_cache_ttl_seconds()),
            # Business Logic
            "replication_key": self.get_replication_key(),
            "pagination_mode": self.get_pagination_mode(),
            "incremental_overlap_minutes": int(self.get_incremental_overlap_minutes()),
            # Entities
            "enabled_entities": self.get_enabled_entities(),
            # Target
            # 🚨 CRITICAL: target_schema REMOVED - TAP must NOT know about destination
            "table_prefix": self.get_table_prefix(),
            # Company
            "company_timezone": self.get_company_timezone(),
            "currency_code": self.get_currency_code(),
        }


def create_config_mapper_from_profile(
    profile_config: dict[str, object] | None = None,
) -> ConfigMapper:
    """Create ConfigMapper from profile configuration.

    Args:
        profile_config: Profile configuration dictionary.

    Returns:
        ConfigMapper instance.

    """
    return ConfigMapper(profile_config)


class ConfigMapperSingleton:
    """Singleton pattern for ConfigMapper without global variables."""

    _instance: ConfigMapper | None = None

    @classmethod
    def get_instance(cls) -> ConfigMapper:
        """Get singleton instance of ConfigMapper.

        Returns:
            Singleton ConfigMapper instance.

        """
        if cls._instance is None:
            cls._instance = ConfigMapper()
        return cls._instance

    @classmethod
    def set_instance(cls, instance: ConfigMapper) -> None:
        """Set singleton instance of ConfigMapper.

        Args:
            instance: ConfigMapper instance to set as singleton.

        """
        cls._instance = instance


def get_global_config_mapper() -> ConfigMapper:
    """Get global ConfigMapper singleton instance.

    Returns:
        Global ConfigMapper instance.

    """
    return ConfigMapperSingleton.get_instance()


def set_global_config_mapper(instance: ConfigMapper) -> None:
    """Set global ConfigMapper singleton instance.

    Args:
        instance: ConfigMapper instance to set as global.

    """
    ConfigMapperSingleton.set_instance(instance)


if __name__ == "__main__":
    # Example usage
    mapper = ConfigMapper()

    config = mapper.get_all_config()
    for _key, _value in config.items():
        pass

    for entity in mapper.get_enabled_entities():
        keys = mapper.get_entity_primary_keys(entity)

    allocation_mapping = mapper.get_allocation_status_mapping()
    for _wms_status, _mapped_status in allocation_mapping.items():
        pass
