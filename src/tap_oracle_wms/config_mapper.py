"""Configuration mapper for transforming hardcoded specifications into configurable parameters.

This module identifies and externalizes hardcoded values throughout the codebase,
making them configurable through environment variables or profile settings.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConfigMapper:
    """Maps hardcoded specifications to configurable parameters."""

    def __init__(self, profile_config: Optional[Dict[str, Any]] = None):
        """Initialize with optional profile configuration.

        Args:
            profile_config: Configuration from profile system

        """
        self.profile_config = profile_config or {}
        self._config_cache: Dict[str, Any] = {}

    # API Configuration

    def get_api_version(self) -> str:
        """Get API version (previously hardcoded as 'v10')."""
        return self._get_config_value(
            "api_version",
            env_var="WMS_API_VERSION",
            default="v10",
            profile_path="api.api_version",
        )

    def get_endpoint_prefix(self) -> str:
        """Get API endpoint prefix (previously hardcoded as '/wms/lgfapi')."""
        return self._get_config_value(
            "endpoint_prefix",
            env_var="WMS_ENDPOINT_PREFIX",
            default="/wms/lgfapi",
            profile_path="api.endpoint_prefix",
        )

    def get_entity_endpoint_pattern(self) -> str:
        """Get entity endpoint pattern."""
        return self._get_config_value(
            "entity_endpoint_pattern",
            env_var="WMS_ENTITY_ENDPOINT_PATTERN",
            default="/{prefix}/{version}/entity",
            profile_path="api.entity_endpoint_pattern",
        )

    def get_authentication_method(self) -> str:
        """Get authentication method (previously hardcoded as 'basic')."""
        return self._get_config_value(
            "auth_method",
            env_var="WMS_AUTH_METHOD",
            default="basic",
            profile_path="api.authentication_method",
        )

    # Performance Configuration

    def get_page_size(self) -> int:
        """Get page size - TAP default 100 (API limit 1250)."""
        return int(
            self._get_config_value(
                "page_size",
                env_var="WMS_PAGE_SIZE",
                default=100,  # TAP standard default (project can configure to 10)
                profile_path="performance.page_size",
            )
        )

    def get_max_page_size(self) -> int:
        """Get maximum page size - Oracle WMS API real limit."""
        return int(
            self._get_config_value(
                "max_page_size",
                env_var="WMS_MAX_PAGE_SIZE",
                default=1250,  # Oracle WMS API real maximum limit
                profile_path="performance.max_page_size",
            )
        )

    def get_request_timeout(self) -> int:
        """Get request timeout - UNLIMITED for large data extractions."""
        return int(
            self._get_config_value(
                "request_timeout",
                env_var="WMS_REQUEST_TIMEOUT",
                default=600,  # UNLIMITED: 10 minutes for large datasets
                profile_path="performance.request_timeout",
            )
        )

    def get_max_retries(self) -> int:
        """Get max retries (previously hardcoded as 3)."""
        return int(
            self._get_config_value(
                "max_retries",
                env_var="WMS_MAX_RETRIES",
                default=3,
                profile_path="performance.max_retries",
            )
        )

    def get_retry_backoff_factor(self) -> float:
        """Get retry backoff factor."""
        return float(
            self._get_config_value(
                "retry_backoff_factor",
                env_var="WMS_RETRY_BACKOFF_FACTOR",
                default=1.5,
                profile_path="performance.retry_backoff_factor",
            )
        )

    def get_cache_ttl_seconds(self) -> int:
        """Get cache TTL (previously hardcoded as 3600)."""
        return int(
            self._get_config_value(
                "cache_ttl_seconds",
                env_var="WMS_CACHE_TTL_SECONDS",
                default=3600,
                profile_path="performance.cache_ttl_seconds",
            )
        )

    def get_connection_pool_size(self) -> int:
        """Get connection pool size."""
        return int(
            self._get_config_value(
                "connection_pool_size",
                env_var="WMS_CONNECTION_POOL_SIZE",
                default=5,
                profile_path="performance.connection_pool_size",
            )
        )

    # Business Logic Configuration

    def get_replication_key(self) -> str:
        """Get default replication key (previously hardcoded as 'mod_ts')."""
        return self._get_config_value(
            "replication_key",
            env_var="WMS_REPLICATION_KEY",
            default="mod_ts",
            profile_path="business_rules.default_replication_key",
        )

    def get_pagination_mode(self) -> str:
        """Get pagination mode (previously hardcoded as 'sequenced')."""
        return self._get_config_value(
            "page_mode",
            env_var="WMS_PAGE_MODE",
            default="sequenced",
            profile_path="business_rules.pagination_mode",
        )

    def get_incremental_overlap_minutes(self) -> int:
        """Get incremental overlap minutes (previously hardcoded as 5)."""
        return int(
            self._get_config_value(
                "incremental_overlap_minutes",
                env_var="WMS_INCREMENTAL_OVERLAP_MINUTES",
                default=5,
                profile_path="business_rules.incremental_overlap_minutes",
            )
        )

    def get_lookback_minutes(self) -> int:
        """Get lookback minutes for initial state."""
        return int(
            self._get_config_value(
                "lookback_minutes",
                env_var="WMS_LOOKBACK_MINUTES",
                default=5,
                profile_path="business_rules.lookback_minutes",
            )
        )

    # Entity Configuration

    def get_enabled_entities(self) -> List[str]:
        """Get list of enabled entities."""
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

    def get_entity_primary_keys(self, entity_name: str) -> List[str]:
        """Get primary keys for specific entity."""
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

    def get_custom_headers(self) -> Dict[str, str]:
        """Get custom headers for API requests."""
        headers = {}

        # Standard headers (previously hardcoded)
        headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": self._get_config_value(
                    "user_agent",
                    env_var="WMS_USER_AGENT",
                    default="tap-oracle-wms/0.2.0",
                    profile_path="api.user_agent",
                ),
            }
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
                "X-WMS-Company": company_code,
                "X-WMS-Facility": facility_code,
            }
        )

        # Additional custom headers from profile or environment
        custom_headers = self._get_config_value(
            "custom_headers",
            env_var="WMS_CUSTOM_HEADERS_JSON",
            default={},
            profile_path="api.custom_headers",
        )

        if isinstance(custom_headers, str):
            import json

            try:
                custom_headers = json.loads(custom_headers)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in WMS_CUSTOM_HEADERS_JSON, ignoring")
                custom_headers = {}

        headers.update(custom_headers)
        return headers

    # OAuth Configuration

    def get_oauth_scope(self) -> str:
        """Get OAuth scope (previously hardcoded)."""
        return self._get_config_value(
            "oauth_scope",
            env_var="WMS_OAUTH_SCOPE",
            default="https://instance.wms.ocs.oraclecloud.com:443/urn:opc:resource:consumer::all",
            profile_path="api.oauth_scope",
        )

    # Database/Target Configuration

    def get_target_schema(self) -> str:
        """Get target schema name."""
        return self._get_config_value(
            "target_schema",
            env_var="WMS_TARGET_SCHEMA",
            default="WMS_SYNC",
            profile_path="target_schema",
        )

    def get_table_prefix(self) -> str:
        """Get table prefix for target tables."""
        return self._get_config_value(
            "table_prefix",
            env_var="WMS_TABLE_PREFIX",
            default="WMS_",
            profile_path="table_prefix",
        )

    # Status Mapping Configuration

    def get_allocation_status_mapping(self) -> Dict[str, str]:
        """Get allocation status mapping (previously hardcoded)."""
        mapping = self._get_config_value(
            "allocation_status_mapping",
            env_var="WMS_ALLOCATION_STATUS_MAPPING_JSON",
            default={
                "ALLOCATED": "Active",
                "RESERVED": "Active",
                "PICKED": "Fulfilled",
                "SHIPPED": "Fulfilled",
                "CANCELLED": "Cancelled",
            },
            profile_path="business_rules.allocation_status_mapping",
        )

        if isinstance(mapping, str):
            import json

            try:
                mapping = json.loads(mapping)
            except json.JSONDecodeError:
                logger.warning(
                    "Invalid JSON in allocation status mapping, using defaults"
                )
                mapping = {
                    "ALLOCATED": "Active",
                    "RESERVED": "Active",
                    "PICKED": "Fulfilled",
                    "SHIPPED": "Fulfilled",
                    "CANCELLED": "Cancelled",
                }

        return mapping

    def get_order_status_mapping(self) -> Dict[str, str]:
        """Get order status mapping."""
        mapping = self._get_config_value(
            "order_status_mapping",
            env_var="WMS_ORDER_STATUS_MAPPING_JSON",
            default={
                "NEW": "Created",
                "CONFIRMED": "Confirmed",
                "IN_PROGRESS": "Processing",
                "COMPLETED": "Completed",
                "CANCELLED": "Cancelled",
            },
            profile_path="business_rules.order_status_mapping",
        )

        if isinstance(mapping, str):
            import json

            try:
                mapping = json.loads(mapping)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in order status mapping, using defaults")
                mapping = {
                    "NEW": "Created",
                    "CONFIRMED": "Confirmed",
                    "IN_PROGRESS": "Processing",
                    "COMPLETED": "Completed",
                    "CANCELLED": "Cancelled",
                }

        return mapping

    # Field Type Patterns

    def get_field_type_patterns(self) -> Dict[str, str]:
        """Get field type patterns for Oracle DDL generation."""
        patterns = self._get_config_value(
            "field_type_patterns",
            env_var="WMS_FIELD_TYPE_PATTERNS_JSON",
            default={
                "_id$": "NUMBER",
                "_qty$": "NUMBER(15,3)",
                "_flg$": "CHAR(1)",
                "_ts$": "TIMESTAMP",
                "_code$": "VARCHAR2(50)",
                "_desc$": "VARCHAR2(500)",
            },
            profile_path="business_rules.field_type_patterns",
        )

        if isinstance(patterns, str):
            import json

            try:
                patterns = json.loads(patterns)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in field type patterns, using defaults")
                patterns = {
                    "_id$": "NUMBER",
                    "_qty$": "NUMBER(15,3)",
                    "_flg$": "CHAR(1)",
                    "_ts$": "TIMESTAMP",
                    "_code$": "VARCHAR2(50)",
                    "_desc$": "VARCHAR2(500)",
                }

        return patterns

    # Company-Specific Settings

    def get_company_timezone(self) -> str:
        """Get company timezone."""
        return self._get_config_value(
            "company_timezone",
            env_var="WMS_COMPANY_TIMEZONE",
            default="UTC",
            profile_path="business_rules.company_timezone",
        )

    def get_currency_code(self) -> str:
        """Get company currency code."""
        return self._get_config_value(
            "currency_code",
            env_var="WMS_CURRENCY_CODE",
            default="USD",
            profile_path="business_rules.currency_code",
        )

    def get_fiscal_year_start_month(self) -> int:
        """Get fiscal year start month."""
        return int(
            self._get_config_value(
                "fiscal_year_start_month",
                env_var="WMS_FISCAL_YEAR_START_MONTH",
                default=1,
                profile_path="business_rules.fiscal_year_start_month",
            )
        )

    # Utility Methods

    def _get_config_value(
        self,
        key: str,
        env_var: Optional[str] = None,
        default: Any = None,
        profile_path: Optional[str] = None,
    ) -> Any:
        """Get configuration value with precedence: cache > env > profile > default.

        Args:
            key: Configuration key
            env_var: Environment variable name
            default: Default value
            profile_path: Dot-notation path in profile config

        Returns:
            Configuration value

        """
        # Check cache first
        cache_key = f"{key}_{env_var}_{profile_path}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]

        value = default

        # Check profile configuration
        if profile_path and self.profile_config:
            value = self._get_nested_value(self.profile_config, profile_path) or value

        # Check environment variable (highest precedence)
        if env_var:
            env_value = os.getenv(env_var)
            if env_value is not None:
                value = env_value

        # Cache the result
        self._config_cache[cache_key] = value

        return value

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation.

        Args:
            data: Dictionary to search
            path: Dot-notation path (e.g., 'api.version')

        Returns:
            Value if found, None otherwise

        """
        keys = path.split(".")
        current = data

        try:
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
        except (KeyError, TypeError):
            return None

    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary for debugging."""
        return {
            # API
            "api_version": self.get_api_version(),
            "endpoint_prefix": self.get_endpoint_prefix(),
            "auth_method": self.get_authentication_method(),
            # Performance
            "page_size": self.get_page_size(),
            "max_page_size": self.get_max_page_size(),
            "request_timeout": self.get_request_timeout(),
            "max_retries": self.get_max_retries(),
            "cache_ttl_seconds": self.get_cache_ttl_seconds(),
            # Business Logic
            "replication_key": self.get_replication_key(),
            "pagination_mode": self.get_pagination_mode(),
            "incremental_overlap_minutes": self.get_incremental_overlap_minutes(),
            # Entities
            "enabled_entities": self.get_enabled_entities(),
            # Target
            "target_schema": self.get_target_schema(),
            "table_prefix": self.get_table_prefix(),
            # Company
            "company_timezone": self.get_company_timezone(),
            "currency_code": self.get_currency_code(),
        }


def create_config_mapper_from_profile(
    profile_config: Optional[Dict[str, Any]] = None,
) -> ConfigMapper:
    """Create ConfigMapper instance with profile configuration.

    Args:
        profile_config: Configuration from profile system

    Returns:
        ConfigMapper instance

    """
    return ConfigMapper(profile_config)


# Global instance for easy access
_global_mapper: Optional[ConfigMapper] = None


def get_global_config_mapper() -> ConfigMapper:
    """Get global ConfigMapper instance.

    Returns:
        Global ConfigMapper instance

    """
    global _global_mapper
    if _global_mapper is None:
        _global_mapper = ConfigMapper()
    return _global_mapper


def set_global_config_mapper(mapper: ConfigMapper) -> None:
    """Set global ConfigMapper instance.

    Args:
        mapper: ConfigMapper instance to set as global

    """
    global _global_mapper
    _global_mapper = mapper


if __name__ == "__main__":
    # Example usage
    mapper = ConfigMapper()

    print("Configuration values:")
    config = mapper.get_all_config()
    for key, value in config.items():
        print(f"  {key}: {value}")

    print("\nEntity primary keys:")
    for entity in mapper.get_enabled_entities():
        keys = mapper.get_entity_primary_keys(entity)
        print(f"  {entity}: {keys}")

    print("\nStatus mappings:")
    allocation_mapping = mapper.get_allocation_status_mapping()
    for wms_status, mapped_status in allocation_mapping.items():
        print(f"  allocation.{wms_status} -> {mapped_status}")
