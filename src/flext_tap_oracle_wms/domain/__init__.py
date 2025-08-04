"""Domain Models - FLEXT Oracle WMS Tap Domain Layer.

Centralized domain models using flext-core patterns with Pydantic + Python 3.13.
Implements Clean Architecture with Domain-Driven Design patterns.

Architecture:
    - Domain entities with rich behavior
    - Value objects for type safety
    - Aggregates for consistency boundaries
    - Domain services for complex business logic
    - Type-safe operations using flext-core types

Design Principles:
    - Single source of truth for all domain models
    - Type-safe operations with comprehensive validation
    - Immutable value objects with business rules
    - Rich domain entities with behavior
    - Clean separation of concerns

Dependencies:
    - flext-core: Foundation library with DDD patterns
    - pydantic: Validation and serialization
    - typing: Type system and annotations

Copyright (c) 2025 FLEXT Team
Licensed under the MIT License
"""

from __future__ import annotations

# Export core domain models
from flext_tap_oracle_wms.domain.models import (
    OracleWmsAuthenticationInfo,
    OracleWmsCatalog,
    # Value objects
    OracleWmsConnectionInfo,
    OracleWmsDiscoveryResult,
    # Domain entities
    OracleWmsEntity,
    # Core domain types
    OracleWmsEntityInfo,
    OracleWmsSchema,
    OracleWmsSchemaInfo,
    # Aggregates
    OracleWmsTapConfiguration,
)
from flext_tap_oracle_wms.domain.types import (
    AllocationId,
    AuthConfigDict,
    CatalogDict,
    CatalogStreamDict,
    # Business domain aliases
    CompanyCode,
    ConnectionConfigDict,
    ContainerNumber,
    DiscoveryConfigDict,
    # Discovery TypedDict definitions
    DiscoveryResultDict,
    EntityConfigDict,
    # Status type aliases
    EntityStatus,
    ExtractionConfigDict,
    FacilityCode,
    ItemCode,
    LocationCode,
    LpnNumber,
    OperationMode,
    OperationResult,
    # Operation type aliases
    OperationType,
    OracleEntityId,
    # Oracle WMS type aliases
    OracleEntityName,
    OracleFieldName,
    OracleFieldValue,
    OracleWmsAuthDict,
    # Configuration type aliases
    OracleWmsConfigDict,
    OracleWmsConnectionDict,
    OrderNumber,
    PickNumber,
    ProcessingStatus,
    ReplicationStatus,
    SchemaConfigDict,
    ShipmentNumber,
    # Singer type aliases
    SingerPropertyName,
    SingerPropertyType,
    SingerSchemaDict,
    SingerStreamDict,
    # Configuration TypedDict definitions
    TapConfigDict,
    ValidationStatus,
)

__all__: list[str] = [
    "AllocationId",
    "AuthConfigDict",
    "CatalogDict",
    "CatalogStreamDict",
    # Business domain aliases
    "CompanyCode",
    "ConnectionConfigDict",
    "ContainerNumber",
    "DiscoveryConfigDict",
    # Discovery TypedDict definitions
    "DiscoveryResultDict",
    "EntityConfigDict",
    # Status type aliases
    "EntityStatus",
    "ExtractionConfigDict",
    "FacilityCode",
    "ItemCode",
    "LocationCode",
    "LpnNumber",
    "OperationMode",
    "OperationResult",
    # Operation type aliases
    "OperationType",
    "OracleEntityId",
    # Oracle WMS type aliases
    "OracleEntityName",
    "OracleFieldName",
    "OracleFieldValue",
    "OracleWmsAuthDict",
    "OracleWmsAuthenticationInfo",
    "OracleWmsCatalog",
    "OracleWmsConfig",
    # Configuration type aliases
    "OracleWmsConfigDict",
    "OracleWmsConnectionDict",
    # Value objects
    "OracleWmsConnectionInfo",
    "OracleWmsDiscoveryResult",
    # Domain entities
    "OracleWmsEntity",
    # Core domain types
    "OracleWmsEntityId",
    "OracleWmsEntityInfo",
    "OracleWmsMetadata",
    "OracleWmsSchema",
    "OracleWmsSchemaInfo",
    # Aggregates
    "OracleWmsTapConfiguration",
    "OrderNumber",
    "PickNumber",
    "ProcessingStatus",
    "ReplicationStatus",
    "SchemaConfigDict",
    "ShipmentNumber",
    # Singer type aliases
    "SingerPropertyName",
    "SingerPropertyType",
    "SingerSchemaDict",
    "SingerStreamDict",
    # Configuration TypedDict definitions
    "TapConfigDict",
    "ValidationStatus",
]
