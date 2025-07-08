"""Configuration profiles system for Oracle WMS tap.

This module provides a hierarchical configuration system that supports:
- Company-specific profiles and presets
- Environment-specific settings (dev/prod/test)
- Configurable business rules and field mappings
- Performance tuning parameters
- API endpoint and authentication patterns

The system transforms hardcoded specifications into flexible configurations,
making the tap suitable for different companies and WMS implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PerformanceConfig:
    """Performance configuration settings."""

    page_size: int = 100
    max_page_size: int = 5000
    request_timeout: int = 120
    max_retries: int = 3
    retry_backoff_factor: float = 1.5
    connection_pool_size: int = 5
    batch_processing_size: int = 100
    cache_ttl_seconds: int = 3600

    def __post_init__(self) -> None:
        """Validate performance settings."""
        if self.page_size <= 0:
            msg = "page_size must be positive"
            raise ValueError(msg)
        if self.max_page_size < self.page_size:
            msg = "max_page_size must be >= page_size"
            raise ValueError(msg)
        if self.request_timeout <= 0:
            msg = "request_timeout must be positive"
            raise ValueError(msg)


@dataclass
class EntityConfig:
    """Entity-specific configuration."""

    name: str
    enabled: bool = True
    replication_method: str = "INCREMENTAL"
    replication_key: str = "mod_ts"
    primary_keys: list[str] = field(default_factory=lambda: ["id"])
    incremental_overlap_minutes: int = 5
    custom_filters: dict[str, Any] = field(default_factory=dict)
    custom_ordering: str | None = None

    def __post_init__(self) -> None:
        """Validate entity configuration."""
        if self.replication_method not in {"INCREMENTAL", "FULL_TABLE"}:
            msg = f"Invalid replication_method: {self.replication_method}"
            raise ValueError(msg)
        if self.incremental_overlap_minutes < 0:
            msg = "incremental_overlap_minutes cannot be negative"
            raise ValueError(msg)


@dataclass
class APIConfig:
    """API endpoint and authentication configuration."""

    api_version: str = "v10"
    endpoint_prefix: str = "/wms/lgfapi"
    entity_endpoint_pattern: str = "/{prefix}/{version}/entity"
    authentication_method: str = "basic"
    custom_headers: dict[str, str] = field(default_factory=dict)
    ssl_verify: bool = True

    def get_entity_endpoint(self) -> str:
        """Get the full entity endpoint pattern."""
        return self.endpoint_prefix + f"/{self.api_version}/entity"

    def get_standard_headers(self) -> dict[str, str]:
        """Get standard WMS headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "tap-oracle-wms/0.2.0",
        }
        headers.update(self.custom_headers)
        return headers


@dataclass
class BusinessRulesConfig:
    """Business rules and field mapping configuration."""

    # Status mappings
    allocation_status_mapping: dict[str, str] = field(
        default_factory=lambda: {
            "ALLOCATED": "Active",
            "RESERVED": "Active",
            "PICKED": "Fulfilled",
            "SHIPPED": "Fulfilled",
            "CANCELLED": "Cancelled",
        },
    )

    order_status_mapping: dict[str, str] = field(
        default_factory=lambda: {
            "NEW": "Created",
            "CONFIRMED": "Confirmed",
            "IN_PROGRESS": "Processing",
            "COMPLETED": "Completed",
            "CANCELLED": "Cancelled",
        },
    )

    # Field type patterns
    field_type_patterns: dict[str, str] = field(
        default_factory=lambda: {
            "_id$": "NUMBER",
            "_qty$": "NUMBER(15,3)",
            "_flg$": "CHAR(1)",
            "_ts$": "TIMESTAMP",
            "_code$": "VARCHAR2(50)",
            "_desc$": "VARCHAR2(500)",
        },
    )

    # Required audit fields
    audit_fields: list[str] = field(
        default_factory=lambda: ["create_user", "create_ts", "mod_user", "mod_ts"],
    )

    # Company-specific business rules
    company_timezone: str = "UTC"
    fiscal_year_start_month: int = 1
    currency_code: str = "USD"

    def get_status_for_allocation(self, wms_status: str) -> str:
        """Get mapped status for allocation entity."""
        return self.allocation_status_mapping.get(wms_status.upper(), "Unknown")

    def get_status_for_order(self, wms_status: str) -> str:
        """Get mapped status for order entity."""
        return self.order_status_mapping.get(wms_status.upper(), "Unknown")


@dataclass
class CompanyProfile:
    """Complete company configuration profile."""

    # Company identification
    company_name: str
    company_code: str
    domain: str

    # Environment
    environment: str = "dev"  # dev, test, prod

    # Configuration sections
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    api: APIConfig = field(default_factory=APIConfig)
    business_rules: BusinessRulesConfig = field(default_factory=BusinessRulesConfig)

    # Entity configuration
    entities: dict[str, EntityConfig] = field(default_factory=dict)

    # 🚨 CRITICAL: TAP must NOT know about destination schemas - only table prefixes
    # for naming
    table_prefix: str = "WMS_"

    def __post_init__(self) -> None:
        """Initialize default entities if none specified."""
        if not self.entities:
            self.entities = self._get_default_entities()

    def _get_default_entities(self) -> dict[str, EntityConfig]:
        """Get default WMS entities configuration."""
        return {
            "allocation": EntityConfig(
                name="allocation",
                replication_method="INCREMENTAL",
                replication_key="mod_ts",
                primary_keys=["company_code", "facility_code", "allocation_id"],
                incremental_overlap_minutes=5,
            ),
            "order_hdr": EntityConfig(
                name="order_hdr",
                replication_method="INCREMENTAL",
                replication_key="mod_ts",
                primary_keys=["company_code", "facility_code", "order_nbr"],
                incremental_overlap_minutes=5,
            ),
            "order_dtl": EntityConfig(
                name="order_dtl",
                replication_method="INCREMENTAL",
                replication_key="mod_ts",
                primary_keys=[
                    "company_code",
                    "facility_code",
                    "order_nbr",
                    "order_line_nbr",
                ],
                incremental_overlap_minutes=5,
            ),
            "item_master": EntityConfig(
                name="item_master",
                replication_method="FULL_TABLE",
                replication_key="id",
                primary_keys=["company_code", "item_id"],
                incremental_overlap_minutes=0,
            ),
        }

    def get_enabled_entities(self) -> list[str]:
        """Get list of enabled entity names."""
        return [name for name, config in self.entities.items() if config.enabled]

    def get_entity_config(self, entity_name: str) -> EntityConfig | None:
        """Get configuration for specific entity."""
        return self.entities.get(entity_name)

    def to_singer_config(self) -> dict[str, Any]:
        """Convert to Singer tap configuration format."""
        config = {
            # Basic connection
            "base_url": f"https://wms-{self.environment}.{self.domain}",
            "api_endpoint_prefix": self.api.endpoint_prefix,
            "wms_api_version": self.api.api_version,
            # Authentication
            "auth_method": self.api.authentication_method,
            "verify_ssl": self.api.ssl_verify,
            # Company context
            "company_code": self.company_code,
            "facility_code": "*",  # Often configurable per extraction
            # Performance settings
            "page_size": self.performance.page_size,
            "max_page_size": self.performance.max_page_size,
            "request_timeout": self.performance.request_timeout,
            "max_retries": self.performance.max_retries,
            "catalog_cache_ttl": self.performance.cache_ttl_seconds,
            # Entities to extract
            "entities": self.get_enabled_entities(),
            # Business rules
            "replication_key": "mod_ts",  # Default, can be overridden per entity
            "enable_incremental": True,
            "incremental_overlap_minutes": 5,
            # Custom headers
            "custom_headers": self.api.get_standard_headers(),
            # Table naming settings (for reference only)
            "_table_prefix": self.table_prefix,
        }

        # Add environment variables references for sensitive data
        config.update(
            {
                "username": f"${{TAP_ORACLE_WMS_USERNAME_{self.company_code.upper()}}}",
                "password": f"${{TAP_ORACLE_WMS_PASSWORD_{self.company_code.upper()}}}",
            },
        )

        return config


class ConfigProfileManager:
    """Manages configuration profiles for different companies and environments."""

    def __init__(self, config_dir: Path | None = None) -> None:
        """Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files.
                       Defaults to config/ relative to project root.

        """
        if config_dir is None:
            # Default to config directory relative to this file
            self.config_dir = Path(__file__).parent.parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)

        self.config_dir.mkdir(exist_ok=True)
        self._profiles: dict[str, CompanyProfile] = {}

    def load_profile(self, profile_name: str) -> CompanyProfile:
        """Load configuration profile from file or environment.

        Args:
            profile_name: Name of the profile to load

        Returns:
            CompanyProfile instance

        Raises:
            FileNotFoundError: If profile file doesn't exist
            ValueError: If profile configuration is invalid

        """
        if profile_name in self._profiles:
            return self._profiles[profile_name]

        # Try to load from file first
        profile_file = self.config_dir / "profiles" / f"{profile_name}.json"
        if profile_file.exists():
            profile = self._load_from_file(profile_file)
        else:
            # Try to create from environment variables
            profile = self._load_from_environment(profile_name)

        self._profiles[profile_name] = profile
        return profile

    def save_profile(
        self,
        profile: CompanyProfile,
        profile_name: str | None = None,
    ) -> None:
        """Save configuration profile to file.

        Args:
            profile: CompanyProfile to save
            profile_name: Name to save under (defaults to company_name)

        """
        if profile_name is None:
            profile_name = profile.company_name.lower().replace(" ", "_")

        profiles_dir = self.config_dir / "profiles"
        profiles_dir.mkdir(exist_ok=True)

        profile_file = profiles_dir / f"{profile_name}.json"

        # Convert to JSON-serializable format
        profile_data = {
            "company_name": profile.company_name,
            "company_code": profile.company_code,
            "domain": profile.domain,
            "environment": profile.environment,
            "table_prefix": profile.table_prefix,
            "performance": profile.performance.__dict__,
            "api": profile.api.__dict__,
            "business_rules": {
                "allocation_status_mapping": (
                    profile.business_rules.allocation_status_mapping
                ),
                "order_status_mapping": profile.business_rules.order_status_mapping,
                "field_type_patterns": profile.business_rules.field_type_patterns,
                "audit_fields": profile.business_rules.audit_fields,
                "company_timezone": profile.business_rules.company_timezone,
                "fiscal_year_start_month": (
                    profile.business_rules.fiscal_year_start_month
                ),
                "currency_code": profile.business_rules.currency_code,
            },
            "entities": {
                name: {
                    "name": config.name,
                    "enabled": config.enabled,
                    "replication_method": config.replication_method,
                    "replication_key": config.replication_key,
                    "primary_keys": config.primary_keys,
                    "incremental_overlap_minutes": config.incremental_overlap_minutes,
                    "custom_filters": config.custom_filters,
                    "custom_ordering": config.custom_ordering,
                }
                for name, config in profile.entities.items()
            },
        }

        with profile_file.open("w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2)

        logger.info("Saved profile '%s' to %s", profile_name, profile_file)

    def _load_from_file(self, profile_file: Path) -> CompanyProfile:
        """Load profile from JSON file."""
        with profile_file.open(encoding="utf-8") as f:
            data = json.load(f)

        # Parse performance config
        performance = PerformanceConfig(**data.get("performance", {}))

        # Parse API config
        api = APIConfig(**data.get("api", {}))

        # Parse business rules
        business_rules_data = data.get("business_rules", {})
        business_rules = BusinessRulesConfig(**business_rules_data)

        # Parse entities
        entities = {}
        for name, entity_data in data.get("entities", {}).items():
            entities[name] = EntityConfig(**entity_data)

        return CompanyProfile(
            company_name=data["company_name"],
            company_code=data["company_code"],
            domain=data["domain"],
            environment=data.get("environment", "dev"),
            table_prefix=data.get("table_prefix", "WMS_"),
            performance=performance,
            api=api,
            business_rules=business_rules,
            entities=entities,
        )

    def load_profile_from_environment(self, profile_name: str) -> CompanyProfile:
        """Public method to load profile from environment."""
        return self._load_from_environment(profile_name)

    def _load_from_environment(self, profile_name: str) -> CompanyProfile:
        """Create profile from environment variables."""
        company_name = os.getenv(
            f"WMS_COMPANY_NAME_{profile_name.upper()}",
            profile_name.title(),
        )
        company_code = os.getenv(
            f"WMS_COMPANY_CODE_{profile_name.upper()}",
            profile_name.upper(),
        )
        domain = os.getenv(f"WMS_DOMAIN_{profile_name.upper()}", "example.com")
        environment = os.getenv("WMS_ENVIRONMENT", "dev")

        # Create profile with defaults, allowing environment overrides
        performance = PerformanceConfig(
            page_size=int(os.getenv("WMS_PAGE_SIZE", "100")),
            max_page_size=int(os.getenv("WMS_MAX_PAGE_SIZE", "5000")),
            request_timeout=int(os.getenv("WMS_REQUEST_TIMEOUT", "120")),
            max_retries=int(os.getenv("WMS_MAX_RETRIES", "3")),
        )

        api = APIConfig(
            api_version=os.getenv("WMS_API_VERSION", "v10"),
            endpoint_prefix=os.getenv("WMS_ENDPOINT_PREFIX", "/wms/lgfapi"),
            authentication_method=os.getenv("WMS_AUTH_METHOD", "basic"),
        )

        return CompanyProfile(
            company_name=company_name,
            company_code=company_code,
            domain=domain,
            environment=environment,
            performance=performance,
            api=api,
        )

    def list_available_profiles(self) -> list[str]:
        """List all available configuration profiles."""
        profiles_dir = self.config_dir / "profiles"
        if not profiles_dir.exists():
            return []

        return [f.stem for f in profiles_dir.glob("*.json") if f.is_file()]

    def create_client-b_profile(self) -> CompanyProfile:
        """Create default client-b profile based on current usage patterns."""
        # Performance settings optimized for client-b usage
        performance = PerformanceConfig(
            page_size=100,  # Standard page size for consistent performance
            max_page_size=5000,
            request_timeout=300,  # Larger timeout for complex queries
            max_retries=3,
            batch_processing_size=100,
            cache_ttl_seconds=1800,  # 30 minutes cache
        )

        # API settings for client-b WMS
        api = APIConfig(
            api_version="v10",
            endpoint_prefix="/wms/lgfapi",
            authentication_method="basic",
            custom_headers={
                "X-Integration-Source": "client-b-meltano-nativo",
                "X-Data-Source": "WMS-Oracle",
            },
        )

        # client-b-specific business rules
        business_rules = BusinessRulesConfig(
            company_timezone="America/Sao_Paulo",
            currency_code="BRL",
            fiscal_year_start_month=1,
        )

        # client-b entity configuration
        entities = {
            "allocation": EntityConfig(
                name="allocation",
                enabled=True,
                replication_method="INCREMENTAL",
                replication_key="mod_ts",
                primary_keys=["company_code", "facility_code", "allocation_id"],
                incremental_overlap_minutes=5,
            ),
            "order_hdr": EntityConfig(
                name="order_hdr",
                enabled=True,
                replication_method="INCREMENTAL",
                replication_key="mod_ts",
                primary_keys=["company_code", "facility_code", "order_nbr"],
                incremental_overlap_minutes=5,
            ),
            "order_dtl": EntityConfig(
                name="order_dtl",
                enabled=True,
                replication_method="INCREMENTAL",
                replication_key="mod_ts",
                primary_keys=[
                    "company_code",
                    "facility_code",
                    "order_nbr",
                    "order_line_nbr",
                ],
                incremental_overlap_minutes=5,
            ),
        }

        return CompanyProfile(
            company_name="client-b",
            company_code="GNOS",
            domain="client-b.com.br",
            environment="prod",
            table_prefix="WMS_",
            performance=performance,
            api=api,
            business_rules=business_rules,
            entities=entities,
        )


def load_profile_for_environment() -> CompanyProfile:
    """Load configuration profile from environment variables.

    This is the main entry point for getting configuration in production.

    Returns:
        CompanyProfile configured from environment

    """
    profile_name = os.getenv("WMS_PROFILE_NAME", "default")
    manager = ConfigProfileManager()

    # Try to load named profile first
    try:
        return manager.load_profile(profile_name)
    except FileNotFoundError:
        logger.warning(
            "Profile '%s' not found, creating from environment", profile_name
        )
        # Create from environment using load_profile method recursively
        return manager.load_profile_from_environment(profile_name)


# Convenience function for tap configuration
def get_singer_config_from_profile(
    profile_name: str | None = None,
) -> dict[str, Any]:
    """Get Singer tap configuration from profile.

    Args:
        profile_name: Profile to load (defaults to environment variable)

    Returns:
        Dictionary suitable for Singer tap configuration

    """
    if profile_name is None:
        profile_name = os.getenv("WMS_PROFILE_NAME", "default")

    manager = ConfigProfileManager()
    profile = manager.load_profile(profile_name)
    return profile.to_singer_config()


if __name__ == "__main__":
    # Example usage and testing
    manager = ConfigProfileManager()

    # Create and save client-b profile
    client-b_profile = manager.create_client-b_profile()
    manager.save_profile(client-b_profile, "client-b")

    # Create a generic template profile
    template_profile = CompanyProfile(
        company_name="Template Company",
        company_code="TMPL",
        domain="example.com",
        environment="dev",
    )
    manager.save_profile(template_profile, "template")

    # Show Singer configuration
    config = get_singer_config_from_profile("client-b")
