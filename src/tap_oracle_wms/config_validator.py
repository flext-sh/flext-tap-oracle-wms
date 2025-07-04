"""Configuration validation for Oracle WMS tap.

This module validates configuration values to ensure they meet the requirements
for successful Oracle WMS API integration.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""


class ConfigValidator:
    """Validates Oracle WMS tap configuration."""

    def __init__(self):
        """Initialize the validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate complete configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid, False otherwise

        Raises:
            ConfigValidationError: If critical validation errors are found

        """
        self.errors.clear()
        self.warnings.clear()

        # Core validation
        self._validate_connection_settings(config)
        self._validate_api_settings(config)
        self._validate_performance_settings(config)
        self._validate_business_logic_settings(config)
        self._validate_entity_settings(config)

        # Log results
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"Configuration warning: {warning}")

        if self.errors:
            error_msg = (
                f"Configuration validation failed with {len(self.errors)} errors:\n"
                + "\n".join(f"  - {error}" for error in self.errors)
            )
            logger.error(error_msg)
            raise ConfigValidationError(error_msg)

        logger.info("Configuration validation passed successfully")
        return True

    def _validate_connection_settings(self, config: Dict[str, Any]) -> None:
        """Validate connection settings."""
        base_url = config.get("base_url")
        if not base_url:
            self.errors.append("base_url is required")
        elif not self._is_valid_url(base_url):
            self.errors.append(f"base_url is not a valid URL: {base_url}")

        # Authentication validation
        auth_method = config.get("auth_method", "basic")
        if auth_method == "basic":
            if not config.get("username"):
                self.errors.append("username is required for basic authentication")
            if not config.get("password"):
                self.errors.append("password is required for basic authentication")
        elif auth_method == "oauth2":
            if not config.get("oauth_client_id"):
                self.errors.append(
                    "oauth_client_id is required for OAuth2 authentication"
                )
            if not config.get("oauth_client_secret"):
                self.errors.append(
                    "oauth_client_secret is required for OAuth2 authentication"
                )
            if not config.get("oauth_token_url"):
                self.errors.append(
                    "oauth_token_url is required for OAuth2 authentication"
                )
        else:
            self.errors.append(
                f"Invalid auth_method: {auth_method}. Must be 'basic' or 'oauth2'"
            )

    def _validate_api_settings(self, config: Dict[str, Any]) -> None:
        """Validate API-specific settings."""
        # API version validation
        api_version = config.get("wms_api_version", "v10")
        if not re.match(r"^v\d+$", api_version):
            self.errors.append(
                f"Invalid API version format: {api_version}. Must be 'vN' where N is a number"
            )

        # Endpoint prefix validation
        endpoint_prefix = config.get("endpoint_prefix", "/wms/lgfapi")
        if not endpoint_prefix.startswith("/"):
            self.warnings.append(
                f"endpoint_prefix should start with '/': {endpoint_prefix}"
            )

        # Page mode validation
        page_mode = config.get("page_mode", "sequenced")
        if page_mode not in ["sequenced", "paged"]:
            self.errors.append(
                f"Invalid page_mode: {page_mode}. Must be 'sequenced' or 'paged'"
            )

        # OAuth scope validation
        oauth_scope = config.get("oauth_scope")
        if oauth_scope and not self._is_valid_url(oauth_scope):
            self.warnings.append(f"oauth_scope appears to be malformed: {oauth_scope}")

    def _validate_performance_settings(self, config: Dict[str, Any]) -> None:
        """Validate performance settings."""
        # Page size validation
        page_size = config.get("page_size", 100)
        if not isinstance(page_size, int) or page_size < 1:
            self.errors.append(f"page_size must be a positive integer: {page_size}")
        elif page_size > 10000:
            self.warnings.append(
                f"Large page_size may cause performance issues: {page_size}"
            )

        # Max page size validation
        max_page_size = config.get("max_page_size", 5000)
        if not isinstance(max_page_size, int) or max_page_size < page_size:
            self.errors.append(f"max_page_size must be >= page_size: {max_page_size}")

        # Timeout validation
        request_timeout = config.get("request_timeout", 120)
        if not isinstance(request_timeout, int) or request_timeout < 1:
            self.errors.append(
                f"request_timeout must be a positive integer: {request_timeout}"
            )
        elif request_timeout > 600:
            self.warnings.append(
                f"Very long request_timeout may cause issues: {request_timeout}"
            )

        # Retry validation
        max_retries = config.get("max_retries", 3)
        if not isinstance(max_retries, int) or max_retries < 0:
            self.errors.append(
                f"max_retries must be a non-negative integer: {max_retries}"
            )
        elif max_retries > 10:
            self.warnings.append(
                f"High max_retries may cause slow failure recovery: {max_retries}"
            )

        # Cache TTL validation
        cache_ttl = config.get("cache_ttl_seconds", 3600)
        if not isinstance(cache_ttl, int) or cache_ttl < 0:
            self.errors.append(
                f"cache_ttl_seconds must be a non-negative integer: {cache_ttl}"
            )

    def _validate_business_logic_settings(self, config: Dict[str, Any]) -> None:
        """Validate business logic settings."""
        # Replication key validation
        replication_key = config.get("replication_key", "mod_ts")
        if not isinstance(replication_key, str) or not replication_key:
            self.errors.append("replication_key must be a non-empty string")

        # Overlap minutes validation
        overlap_minutes = config.get("incremental_overlap_minutes", 5)
        if not isinstance(overlap_minutes, int) or overlap_minutes < 0:
            self.errors.append(
                f"incremental_overlap_minutes must be a non-negative integer: {overlap_minutes}"
            )
        elif overlap_minutes > 1440:  # 24 hours
            self.warnings.append(
                f"Large incremental_overlap_minutes may cause performance issues: {overlap_minutes}"
            )

        # Lookback minutes validation
        lookback_minutes = config.get("lookback_minutes", 5)
        if not isinstance(lookback_minutes, int) or lookback_minutes < 0:
            self.errors.append(
                f"lookback_minutes must be a non-negative integer: {lookback_minutes}"
            )

        # Company code validation
        company_code = config.get("company_code", "*")
        if not isinstance(company_code, str):
            self.errors.append("company_code must be a string")

        # Facility code validation
        facility_code = config.get("facility_code", "*")
        if not isinstance(facility_code, str):
            self.errors.append("facility_code must be a string")

        # Timezone validation
        timezone = config.get("company_timezone", "UTC")
        if not isinstance(timezone, str):
            self.errors.append("company_timezone must be a string")

        # Currency validation
        currency = config.get("currency_code", "USD")
        if not isinstance(currency, str) or len(currency) != 3:
            self.errors.append(f"currency_code must be a 3-letter string: {currency}")

    def _validate_entity_settings(self, config: Dict[str, Any]) -> None:
        """Validate entity-specific settings."""
        entities = config.get("entities")
        if entities is not None:
            if not isinstance(entities, list):
                self.errors.append("entities must be a list")
            elif not entities:
                self.warnings.append(
                    "entities list is empty - no data will be extracted"
                )
            else:
                for entity in entities:
                    if not isinstance(entity, str) or not entity:
                        self.errors.append(
                            f"All entity names must be non-empty strings: {entity}"
                        )

        # Entity patterns validation
        entity_patterns = config.get("entity_patterns")
        if entity_patterns is not None:
            if not isinstance(entity_patterns, dict):
                self.errors.append("entity_patterns must be a dictionary")
            else:
                include_patterns = entity_patterns.get("include")
                exclude_patterns = entity_patterns.get("exclude")

                if include_patterns is not None and not isinstance(
                    include_patterns, list
                ):
                    self.errors.append("entity_patterns.include must be a list")

                if exclude_patterns is not None and not isinstance(
                    exclude_patterns, list
                ):
                    self.errors.append("entity_patterns.exclude must be a list")

        # Force full table validation
        force_full_table = config.get("force_full_table")
        if force_full_table is not None and not isinstance(force_full_table, bool):
            self.errors.append("force_full_table must be a boolean")

        # Enable incremental validation
        enable_incremental = config.get("enable_incremental", True)
        if not isinstance(enable_incremental, bool):
            self.errors.append("enable_incremental must be a boolean")

    def _is_valid_url(self, url: str) -> bool:
        """Check if a string is a valid URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except (ValueError, AttributeError):
            return False

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation results.

        Returns:
            Dictionary with validation results

        """
        return {
            "is_valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors.copy(),
            "warnings": self.warnings.copy(),
        }


def validate_config_with_mapper(config_mapper) -> bool:
    """Validate configuration using ConfigMapper.

    Args:
        config_mapper: ConfigMapper instance to validate

    Returns:
        True if configuration is valid

    Raises:
        ConfigValidationError: If validation fails

    """
    validator = ConfigValidator()

    # Build config dictionary from mapper
    config = config_mapper.get_all_config()

    # Add additional settings that aren't in get_all_config
    config.update(
        {
            "auth_method": config_mapper.get_authentication_method(),
            "oauth_scope": config_mapper.get_oauth_scope(),
            "company_code": config_mapper._get_config_value(
                "company_code", env_var="WMS_COMPANY_CODE", default="*"
            ),
            "facility_code": config_mapper._get_config_value(
                "facility_code", env_var="WMS_FACILITY_CODE", default="*"
            ),
            "entities": config_mapper.get_enabled_entities(),
        }
    )

    return validator.validate_config(config)


if __name__ == "__main__":
    # Test validation
    from .config_mapper import ConfigMapper

    mapper = ConfigMapper()
    try:
        validate_config_with_mapper(mapper)
        print("✅ Configuration validation passed")
    except ConfigValidationError as e:
        print(f"❌ Configuration validation failed: {e}")
