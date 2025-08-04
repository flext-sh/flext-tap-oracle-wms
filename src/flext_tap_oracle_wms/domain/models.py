"""Domain Models - FLEXT Oracle WMS Tap Domain Layer.

Centralized domain models using flext-core patterns with Pydantic + Python 3.13.
Refactored from existing modules to eliminate duplication and provide single source of truth.

Architecture:
    - Extends flext-core models for Oracle WMS specific domain
    - Value objects for type safety and validation
    - Domain entities with rich behavior using DDD patterns
    - TypedDict definitions for configuration structures
    - Factory functions for model creation

Design Principles:
    - Single source of truth for all Oracle WMS domain models
    - Type-safe operations with comprehensive validation
    - Immutable value objects with business rules
    - Rich domain entities with behavior
    - Clean separation of concerns

Dependencies:
    - flext-core: Foundation library with DDD patterns and models
    - pydantic: Validation and serialization
    - typing: Type system and annotations

Copyright (c) 2025 FLEXT Team
Licensed under the MIT License
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, ClassVar, cast

# Import centralized models from flext-core
from flext_core import (
    # Base models from flext-core
    FlextBaseModel,
    # TypedDict definitions
    FlextDomainEntity,
    FlextDomainValueObject,
    TAnyDict,
)
from pydantic import Field, field_validator, model_validator

# =============================================================================
# ORACLE WMS SPECIFIC ENUMS
# =============================================================================


class OracleWmsConnectionType(StrEnum):
    """Oracle WMS connection types."""

    BASIC = "basic"
    BEARER = "bearer"
    OAUTH2 = "oauth2"


class OracleWmsReplicationMethod(StrEnum):
    """Oracle WMS replication methods."""

    FULL_TABLE = "FULL_TABLE"
    INCREMENTAL = "INCREMENTAL"


class OracleWmsEntityStatus(StrEnum):
    """Oracle WMS entity status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISCOVERED = "DISCOVERED"
    CONFIGURED = "CONFIGURED"


# =============================================================================
# ORACLE WMS VALUE OBJECTS - Immutable business concepts
# =============================================================================


class OracleWmsConnectionInfo(FlextDomainValueObject):
    """Value object for Oracle WMS connection information.

    Extends flext-core FlextDomainValueObject with Oracle WMS specific validation.
    """

    base_url: str = Field(..., description="Oracle WMS base URL")
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Connection timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
    )
    verify_ssl: bool = Field(default=True, description="SSL certificate verification")
    api_version: str = Field(default="v10", description="Oracle WMS API version")

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        if not v.startswith(("http://", "https://")):
            msg = "Base URL must start with http:// or https://"
            raise ValueError(msg)
        return v.rstrip("/")


class OracleWmsAuthenticationInfo(FlextDomainValueObject):
    """Value object for Oracle WMS authentication information."""

    username: str = Field(..., description="Oracle WMS username")
    password: str = Field(..., description="Oracle WMS password")
    auth_method: OracleWmsConnectionType = Field(
        default=OracleWmsConnectionType.BASIC,
        description="Authentication method",
    )
    company_code: str | None = Field(
        default=None,
        description="Company code for multi-tenant",
    )
    facility_code: str | None = Field(
        default=None,
        description="Facility code for multi-tenant",
    )


class OracleWmsEntityInfo(FlextDomainValueObject):
    """Value object for Oracle WMS entity information."""

    name: str = Field(..., description="Entity name")
    display_name: str | None = Field(
        default=None,
        description="Human readable display name",
    )
    description: str | None = Field(default=None, description="Entity description")
    status: OracleWmsEntityStatus = Field(default=OracleWmsEntityStatus.DISCOVERED)
    primary_keys: list[str] = Field(
        default_factory=list,
        description="Primary key fields",
    )
    replication_key: str | None = Field(
        default=None,
        description="Replication key field",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate entity name format."""
        if not v or not v.replace("_", "").isalnum():
            msg = "Entity name must be alphanumeric with underscores"
            raise ValueError(msg)
        return v.lower()


class OracleWmsSchemaInfo(FlextDomainValueObject):
    """Value object for Oracle WMS schema information."""

    entity_name: str = Field(..., description="Entity name this schema belongs to")
    properties: dict[str, dict[str, object]] = Field(
        default_factory=dict,
        description="JSON schema properties",
    )
    required_fields: list[str] = Field(
        default_factory=list,
        description="Required field names",
    )
    discovered_at: datetime = Field(
        default_factory=datetime.now,
        description="Discovery timestamp",
    )
    field_count: int = Field(ge=0, description="Number of fields in schema")

    @model_validator(mode="after")
    def _calculate_field_count(self) -> OracleWmsSchemaInfo:
        """Calculate field count from properties after model creation."""
        if self.field_count == 0:
            object.__setattr__(self, "field_count", len(self.properties))
        return self


# =============================================================================
# ORACLE WMS DOMAIN ENTITIES - Rich domain objects with behavior
# =============================================================================


class OracleWmsEntity(FlextDomainEntity):
    """Domain entity for Oracle WMS entities.

    Extends flext-core FlextDomainEntity with Oracle WMS specific behavior.
    """

    # Entity information
    info: OracleWmsEntityInfo
    schema_info: OracleWmsSchemaInfo | None = None

    # Replication configuration
    replication_method: OracleWmsReplicationMethod = Field(
        default=OracleWmsReplicationMethod.INCREMENTAL,
    )

    # Operational metadata
    last_sync_at: datetime | None = Field(
        default=None,
        description="Last synchronization timestamp",
    )
    record_count: int = Field(
        default=0,
        ge=0,
        description="Number of records extracted",
    )

    # Constants
    DEFAULT_PAGE_SIZE: ClassVar[int] = 1000
    MAX_PAGE_SIZE: ClassVar[int] = 10000

    def is_incremental_capable(self) -> bool:
        """Check if entity supports incremental replication."""
        return (
            self.info.replication_key is not None
            and self.schema_info is not None
            and self.info.replication_key in self.schema_info.properties
        )

    def get_replication_config(self) -> dict[str, object]:
        """Get replication configuration for this entity."""
        return {
            "method": self.replication_method.value,
            "key": self.info.replication_key,
            "incremental_capable": self.is_incremental_capable(),
        }

    def update_sync_metadata(self, record_count: int) -> None:
        """Update synchronization metadata after extraction."""
        object.__setattr__(self, "last_sync_at", datetime.now())
        object.__setattr__(self, "record_count", record_count)


class OracleWmsSchema(FlextDomainEntity):
    """Domain entity for Oracle WMS schema definitions."""

    entity_name: str = Field(..., description="Entity name")
    json_schema: dict[str, object] = Field(..., description="Complete JSON schema")
    singer_schema: dict[str, object] = Field(..., description="Singer-compatible schema")
    metadata: dict[str, object] = Field(
        default_factory=dict,
        description="Schema metadata",
    )

    def get_field_names(self) -> list[str]:
        """Get all field names from schema properties."""
        properties = self.json_schema.get("properties", {})
        if isinstance(properties, dict):
            return list(properties.keys())
        return []

    def get_required_fields(self) -> list[str]:
        """Get required field names from schema."""
        required = self.json_schema.get("required", [])
        return required if isinstance(required, list) else []

    def is_field_required(self, field_name: str) -> bool:
        """Check if a field is required."""
        return field_name in self.get_required_fields()


# =============================================================================
# ORACLE WMS AGGREGATES - Complex domain objects with consistency boundaries
# =============================================================================


class OracleWmsTapConfiguration(FlextBaseModel):
    """Aggregate for complete Oracle WMS tap configuration.

    Root aggregate that ensures consistency across all configuration aspects.
    """

    # Connection configuration
    connection: OracleWmsConnectionInfo
    authentication: OracleWmsAuthenticationInfo

    # Entity configuration
    entities: list[OracleWmsEntityInfo] = Field(default_factory=list)

    # Operational configuration
    page_size: int = Field(default=1000, ge=1, le=10000)
    page_mode: str = Field(default="sequenced", pattern="^(sequenced|paged)$")
    enable_incremental: bool = Field(default=True)
    incremental_overlap_minutes: int = Field(default=5, ge=0, le=60)
    lookback_minutes: int = Field(default=5, ge=0, le=1440)

    # Feature flags
    enable_caching: bool = Field(default=True)
    enable_discovery: bool = Field(default=True)
    force_full_table: bool = Field(default=False)

    def get_entity_by_name(self, name: str) -> OracleWmsEntityInfo | None:
        """Get entity information by name."""
        return next((e for e in self.entities if e.name == name), None)

    def add_entity(self, entity: OracleWmsEntityInfo) -> None:
        """Add entity to configuration with validation."""
        if self.get_entity_by_name(entity.name) is not None:
            msg: str = f"Entity {entity.name} already exists in configuration"
            raise ValueError(msg)
        self.entities.append(entity)

    def get_connection_url(self) -> str:
        """Get complete connection URL."""
        return f"{self.connection.base_url}/wms/lgfapi/{self.connection.api_version}"


class OracleWmsCatalog(FlextBaseModel):
    """Aggregate for Oracle WMS catalog containing all discovered entities and schemas."""

    entities: list[OracleWmsEntity] = Field(default_factory=list)
    schemas: list[OracleWmsSchema] = Field(default_factory=list)
    discovery_metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    def get_entity_names(self) -> list[str]:
        """Get all entity names in catalog."""
        return [e.info.name for e in self.entities]

    def get_schema_by_entity(self, entity_name: str) -> OracleWmsSchema | None:
        """Get schema for specific entity."""
        return next((s for s in self.schemas if s.entity_name == entity_name), None)

    def add_discovered_entity(
        self,
        entity_info: OracleWmsEntityInfo,
        schema_info: OracleWmsSchemaInfo,
        json_schema: dict[str, object],
    ) -> None:
        """Add discovered entity with schema to catalog."""
        # Create entity
        entity = OracleWmsEntity(
            id=entity_info.name,
            info=entity_info,
            schema_info=schema_info,
        )
        self.entities.append(entity)

        # Create schema
        schema = OracleWmsSchema(
            id=f"{entity_info.name}_schema",
            entity_name=entity_info.name,
            json_schema=json_schema,
            singer_schema=json_schema,  # For now, same as JSON schema
        )
        self.schemas.append(schema)


# =============================================================================
# ORACLE WMS DISCOVERY RESULT - Specialized result object
# =============================================================================


class OracleWmsDiscoveryResult(FlextBaseModel):
    """Result object for Oracle WMS entity discovery operations."""

    success: bool = Field(..., description="Discovery success status")
    entity_name: str = Field(..., description="Discovered entity name")
    entity_schema: dict[str, object] = Field(
        default_factory=dict,
        description="Discovered schema",
    )
    metadata: dict[str, object] = Field(
        default_factory=dict,
        description="Discovery metadata",
    )
    errors: list[str] = Field(default_factory=list, description="Discovery errors")
    field_count: int = Field(default=0, ge=0, description="Number of fields discovered")
    discovery_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Discovery time in milliseconds",
    )

    def successful(self) -> bool:
        """Check if discovery was successful."""
        return self.success and not self.errors and self.field_count > 0

    def add_error(self, error: str) -> None:
        """Add error to discovery result."""
        self.errors.append(error)
        object.__setattr__(self, "success", False)


# =============================================================================
# FACTORY FUNCTIONS - Using flext-core patterns
# =============================================================================


def create_oracle_wms_tap_config(config_dict: TAnyDict) -> OracleWmsTapConfiguration:
    """Factory function to create Oracle WMS tap configuration from dictionary.

    Args:
        config_dict: Configuration dictionary

    Returns:
        Validated Oracle WMS tap configuration

    Raises:
        ValueError: If configuration is invalid

    """
    # Extract connection info with proper type conversions
    connection = OracleWmsConnectionInfo(
        base_url=str(config_dict["base_url"]),
        timeout=cast("int", config_dict.get("timeout", 30)),
        max_retries=cast("int", config_dict.get("max_retries", 3)),
        verify_ssl=bool(config_dict.get("verify_ssl", True)),
        api_version=str(config_dict.get("wms_api_version", "v10")),
    )

    # Extract authentication info with proper type conversions
    authentication = OracleWmsAuthenticationInfo(
        username=str(config_dict["username"]),
        password=str(config_dict["password"]),
        auth_method=OracleWmsConnectionType(
            str(config_dict.get("auth_method", "basic")),
        ),
        company_code=str(config_dict.get("company_code", "*")),
        facility_code=str(config_dict.get("facility_code", "*")),
    )

    # Extract entity configurations with proper type handling
    entities: list[OracleWmsEntityInfo] = []
    if "entities" in config_dict:
        entities_data = config_dict["entities"]
        if isinstance(entities_data, list):
            for entity_name in entities_data:
                if entity_name:  # Guard clause to satisfy MyPy reachability analysis
                    entity_info = OracleWmsEntityInfo(name=str(entity_name))
                    entities.append(entity_info)

    return OracleWmsTapConfiguration(
        connection=connection,
        authentication=authentication,
        entities=entities,
        page_size=cast("int", config_dict.get("page_size", 1000)),
        page_mode=str(config_dict.get("page_mode", "sequenced")),
        enable_incremental=bool(config_dict.get("enable_incremental", True)),
        incremental_overlap_minutes=cast(
            "int", config_dict.get("incremental_overlap_minutes", 5),
        ),
        lookback_minutes=cast("int", config_dict.get("lookback_minutes", 5)),
        enable_caching=bool(config_dict.get("enable_caching", True)),
        enable_discovery=bool(config_dict.get("enable_discovery", True)),
        force_full_table=bool(config_dict.get("force_full_table", False)),
    )


def create_oracle_wms_discovery_result(
    entity_name: str,
    schema: dict[str, object] | None = None,
    success: bool = True,
    errors: list[str] | None = None,
) -> OracleWmsDiscoveryResult:
    """Factory function to create Oracle WMS discovery result.

    Args:
        entity_name: Name of discovered entity
        schema: Discovered schema dictionary
        success: Discovery success status
        errors: List of discovery errors

    Returns:
        Oracle WMS discovery result object

    """
    schema = schema or {}
    errors = errors or []

    # Type casting for len() compatibility
    from typing import cast
    properties = cast("dict[str, object]", schema.get("properties", {}))
    field_count = len(properties)

    return OracleWmsDiscoveryResult(
        success=success and not errors,
        entity_name=entity_name,
        entity_schema=schema,
        field_count=field_count,
        errors=errors,
    )
