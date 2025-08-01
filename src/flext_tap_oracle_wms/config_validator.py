"""Configuration validation for Oracle WMS tap.

This module validates configuration values to ensure they meet the requirements
for successful Oracle WMS API integration.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import contextlib

# Removed circular dependency - use DI pattern
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

# Use simple validation patterns
from flext_core import FlextError, get_logger

# API and Performance Constants
MAX_PAGE_SIZE = 1250
MAX_REQUEST_TIMEOUT = 600
MAX_RETRIES = 10
MAX_OVERLAP_MINUTES = 1440  # 24 hours
CURRENCY_CODE_LENGTH = 3  # ISO 4217 standard

logger = get_logger(__name__)


# =============================================================================
# REFACTORING: Strategy Pattern for reducing validation complexity
# =============================================================================


class ValidationResult:
    """Parameter Object: Encapsulates validation result data.

    SOLID REFACTORING: Reduces validation method complexity by encapsulating
    validation state and results in a single object.
    """

    def __init__(self) -> None:
        """Initialize validation result with empty lists."""
        self.is_valid: bool = True
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, message: str) -> None:
        """Add validation error."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add validation warning."""
        self.warnings.append(message)

    def merge(self, other: ValidationResult) -> None:
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False


class ValidationStrategy(ABC):
    """Strategy Pattern: Abstract base for configuration validation strategies."""

    @abstractmethod
    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate specific aspect of configuration."""


class ConnectionValidationStrategy(ValidationStrategy):
    """Strategy Pattern: Handles connection settings validation."""

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate connection configuration settings."""
        result = ValidationResult()

        # Base URL validation
        base_url = config.get("base_url")
        if not base_url:
            result.add_error("base_url is required")
        elif not self._is_valid_url(base_url):
            result.add_error(f"base_url is not a valid URL: {base_url}")

        # Authentication validation using Chain of Responsibility
        auth_method = config.get("auth_method", "basic")
        if auth_method == "basic":
            self._validate_basic_auth(config, result)
        elif auth_method == "oauth2":
            self._validate_oauth2_auth(config, result)
        else:
            result.add_error(
                f"Invalid auth_method: {auth_method}. Must be 'basic' or 'oauth2'",
            )

        return result

    def _validate_basic_auth(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate basic authentication settings."""
        if not config.get("username"):
            result.add_error("username is required for basic authentication")
        if not config.get("password"):
            result.add_error("password is required for basic authentication")

    def _validate_oauth2_auth(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate OAuth2 authentication settings."""
        required_oauth_fields = [
            (
                "oauth_client_id",
                "oauth_client_id is required for OAuth2 authentication",
            ),
            (
                "oauth_client_secret",
                "oauth_client_secret is required for OAuth2 authentication",
            ),
            (
                "oauth_token_url",
                "oauth_token_url is required for OAuth2 authentication",
            ),
        ]

        for field, error_msg in required_oauth_fields:
            if not config.get(field):
                result.add_error(error_msg)

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except (ValueError, AttributeError):
            return False


class ApiValidationStrategy(ValidationStrategy):
    """Strategy Pattern: Handles API settings validation."""

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate API configuration settings."""
        result = ValidationResult()

        # API version validation
        api_version = config.get("wms_api_version", "v10")
        if not re.match(r"^v\d+$", api_version):
            result.add_error(
                f"Invalid API version format: {api_version}. "
                f"Must be 'vN' where N is a number",
            )

        # Endpoint prefix validation
        endpoint_prefix = config.get("endpoint_prefix", "/wms/lgfapi")
        if not endpoint_prefix.startswith("/"):
            result.add_warning(
                f"endpoint_prefix should start with '/': {endpoint_prefix}",
            )

        # Page mode validation
        page_mode = config.get("page_mode", "sequenced")
        if page_mode not in {"sequenced", "paged"}:
            result.add_error(
                f"Invalid page_mode: {page_mode}. Must be 'sequenced' or 'paged'",
            )

        # OAuth scope validation
        oauth_scope = config.get("oauth_scope")
        if oauth_scope and not self._is_valid_url(oauth_scope):
            result.add_warning(f"oauth_scope appears to be malformed: {oauth_scope}")

        return result

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except (ValueError, AttributeError):
            return False


class PerformanceValidationStrategy(ValidationStrategy):
    """Strategy Pattern: Handles performance settings validation."""

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate performance configuration settings."""
        result = ValidationResult()

        # Page size validation
        page_size = config.get("page_size", 100)
        if not isinstance(page_size, int) or page_size < 1:
            result.add_error(f"page_size must be a positive integer: {page_size}")
        elif page_size > MAX_PAGE_SIZE:
            result.add_error(
                f"page_size exceeds Oracle WMS API limit "
                f"(max {MAX_PAGE_SIZE}): {page_size}",
            )

        # Max page size validation
        max_page_size = config.get("max_page_size", 5000)
        if not isinstance(max_page_size, int) or max_page_size < page_size:
            result.add_error(f"max_page_size must be >= page_size: {max_page_size}")

        # Timeout validation
        request_timeout = config.get("request_timeout", 120)
        if not isinstance(request_timeout, int) or request_timeout < 1:
            result.add_error(
                f"request_timeout must be a positive integer: {request_timeout}",
            )
        elif request_timeout > MAX_REQUEST_TIMEOUT:
            result.add_warning(
                f"Very long request_timeout may cause issues: {request_timeout}",
            )

        # Retry validation
        max_retries = config.get("max_retries", 3)
        if not isinstance(max_retries, int) or max_retries < 0:
            result.add_error(
                f"max_retries must be a non-negative integer: {max_retries}",
            )
        elif max_retries > MAX_RETRIES:
            result.add_warning(
                f"High max_retries may cause slow failure recovery: {max_retries}",
            )

        # Cache TTL validation
        cache_ttl = config.get("cache_ttl_seconds", 3600)
        if not isinstance(cache_ttl, int) or cache_ttl < 0:
            result.add_error(
                f"cache_ttl_seconds must be a non-negative integer: {cache_ttl}",
            )

        return result


class BusinessLogicValidationStrategy(ValidationStrategy):
    """Strategy Pattern: Handles business logic settings validation."""

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate business logic configuration settings."""
        result = ValidationResult()

        # Use validation helper methods for complex logic
        self._validate_replication_settings(config, result)
        self._validate_company_settings(config, result)
        self._validate_time_settings(config, result)

        return result

    def _validate_replication_settings(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate replication-related settings."""
        replication_key = config.get("replication_key", "mod_ts")
        if not isinstance(replication_key, str) or not replication_key:
            result.add_error("replication_key must be a non-empty string")

        # Overlap minutes validation
        overlap_minutes = config.get("incremental_overlap_minutes", 5)
        if not isinstance(overlap_minutes, int) or overlap_minutes < 0:
            result.add_error(
                f"incremental_overlap_minutes must be a non-negative integer: "
                f"{overlap_minutes}",
            )
        elif overlap_minutes > MAX_OVERLAP_MINUTES:
            result.add_warning(
                f"Large incremental_overlap_minutes may cause performance issues: "
                f"{overlap_minutes}",
            )

        # Lookback minutes validation
        lookback_minutes = config.get("lookback_minutes", 5)
        if not isinstance(lookback_minutes, int) or lookback_minutes < 0:
            result.add_error(
                f"lookback_minutes must be a non-negative integer: {lookback_minutes}",
            )

    def _validate_company_settings(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate company-related settings."""
        company_code = config.get("company_code", "*")
        if not isinstance(company_code, str):
            result.add_error("company_code must be a string")

        facility_code = config.get("facility_code", "*")
        if not isinstance(facility_code, str):
            result.add_error("facility_code must be a string")

        # Currency validation
        currency = config.get("currency_code", "USD")
        if not isinstance(currency, str) or len(currency) != CURRENCY_CODE_LENGTH:
            result.add_error(f"currency_code must be a 3-letter string: {currency}")

    def _validate_time_settings(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate time-related settings."""
        timezone = config.get("company_timezone", "UTC")
        if not isinstance(timezone, str):
            result.add_error("company_timezone must be a string")


class EntityValidationStrategy(ValidationStrategy):
    """Strategy Pattern: Handles entity settings validation."""

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate entity configuration settings."""
        result = ValidationResult()

        self._validate_entities_list(config, result)
        self._validate_entity_patterns(config, result)
        self._validate_entity_flags(config, result)

        return result

    def _validate_entities_list(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate entities list configuration."""
        entities = config.get("entities")
        if entities is not None:
            if not isinstance(entities, list):
                result.add_error("entities must be a list")
            elif not entities:
                result.add_warning(
                    "entities list is empty - no data will be extracted",
                )
            else:
                for entity in entities:
                    if not isinstance(entity, str) or not entity:
                        result.add_error(
                            f"All entity names must be non-empty strings: {entity}",
                        )

    def _validate_entity_patterns(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate entity patterns configuration."""
        entity_patterns = config.get("entity_patterns")
        if entity_patterns is not None:
            if not isinstance(entity_patterns, dict):
                result.add_error("entity_patterns must be a dictionary")
            else:
                include_patterns = entity_patterns.get("include")
                exclude_patterns = entity_patterns.get("exclude")

                if include_patterns is not None and not isinstance(
                    include_patterns, list
                ):
                    result.add_error("entity_patterns.include must be a list")

                if exclude_patterns is not None and not isinstance(
                    exclude_patterns, list
                ):
                    result.add_error("entity_patterns.exclude must be a list")

    def _validate_entity_flags(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate entity flags configuration."""
        force_full_table = config.get("force_full_table")
        if force_full_table is not None and not isinstance(force_full_table, bool):
            result.add_error("force_full_table must be a boolean")

        enable_incremental = config.get("enable_incremental", True)
        if not isinstance(enable_incremental, bool):
            result.add_error("enable_incremental must be a boolean")


# Simple validation error
class ConfigValidationError(FlextError):
    """Configuration validation error."""


class ConfigValidator:
    """Validates Oracle WMS tap configuration using SOLID principles.

    SOLID REFACTORING: Reduced complexity from 68 to ~15 using Strategy Pattern
    to separate validation concerns into dedicated strategy classes.
    """

    def __init__(self) -> None:
        """Initialize ConfigValidator with validation strategies."""
        # Strategy Pattern: Initialize all validation strategies
        self.strategies: list[ValidationStrategy] = [
            ConnectionValidationStrategy(),
            ApiValidationStrategy(),
            PerformanceValidationStrategy(),
            BusinessLogicValidationStrategy(),
            EntityValidationStrategy(),
        ]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate complete Oracle WMS tap configuration using Strategy Pattern.

        SOLID REFACTORING: Reduced method complexity by delegating validation
        to specialized strategy classes, following Single Responsibility Principle.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid

        Raises:
            ConfigValidationError: If critical validation errors are found.

        """
        # Execute all validation strategies and collect results
        overall_result = ValidationResult()

        for strategy in self.strategies:
            strategy_result = strategy.validate(config)
            overall_result.merge(strategy_result)

        # Log results
        if overall_result.warnings:
            for warning in overall_result.warnings:
                logger.warning("Configuration warning: %s", warning)

        if overall_result.errors:
            error_msg = (
                f"Configuration validation failed with {len(overall_result.errors)} errors:\n"
                + "\n".join(f"  - {error}" for error in overall_result.errors)
            )
            raise ConfigValidationError(error_msg)

        logger.info("Configuration validation passed successfully")
        return True

    def get_validation_summary(self) -> dict[str, Any]:
        """Get summary of validation results.

        Returns:
            Dictionary with validation results

        """
        # Run validation to get current results
        temp_result = ValidationResult()
        for strategy in self.strategies:
            strategy_result = strategy.validate({})
            temp_result.merge(strategy_result)

        return {
            "is_valid": temp_result.is_valid,
            "error_count": len(temp_result.errors),
            "warning_count": len(temp_result.warnings),
            "errors": temp_result.errors.copy(),
            "warnings": temp_result.warnings.copy(),
        }


def validate_config_with_mapper(config_mapper: Any) -> bool:
    """Validate configuration using a config mapper.

    Args:
        config_mapper: Configuration mapper instance.

    Returns:
        True if configuration is valid, False otherwise.

    """
    validator = ConfigValidator()

    # Build config dictionary from mapper
    config = config_mapper.get_all_config()

    # Add additional settings that aren't in get_all_config
    config.update(
        {
            "auth_method": config_mapper.get_authentication_method(),
            "oauth_scope": config_mapper.get_oauth_scope(),
            "company_code": config_mapper.get_company_code(),
            "facility_code": config_mapper.get_facility_code(),
            "entities": config_mapper.get_enabled_entities(),
        },
    )

    return validator.validate_config(config)


if __name__ == "__main__":
    # Test validation
    from flext_tap_oracle_wms.config_mapper import ConfigMapper

    mapper = ConfigMapper()
    with contextlib.suppress(ConfigValidationError):
        validate_config_with_mapper(mapper)
