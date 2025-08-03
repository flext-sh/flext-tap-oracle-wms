"""Oracle WMS Domain Types - TypedDict definitions and type aliases.

Centralized TypedDict definitions using flext-core patterns with Python 3.13.
Provides type-safe configuration and data structures for Oracle WMS tap.

Architecture:
    - TypedDict definitions for all configuration structures
    - Type aliases for Oracle WMS specific types
    - Compatibility with flext-core type system
    - Integration with Pydantic models

Design Principles:
    - Single source of truth for all Oracle WMS type definitions
    - Type-safe operations through comprehensive typing
    - Domain-specific type aliases for business clarity
    - Compatibility with flext-core type system

Dependencies:
    - flext-core: Foundation library type system
    - typing: Type system and TypedDict support
    - Standard library: Built-in type annotations

Copyright (c) 2025 FLEXT Team
Licensed under the MIT License
"""

from __future__ import annotations

from typing import NotRequired, TypedDict

# Import core types from flext-core
from flext_core import (
    TAnyDict,
    TConfigDict,
    TEntityId,
    TValue,
)

# =============================================================================
# ORACLE WMS CONFIGURATION TYPEDDICTS
# =============================================================================


class ConnectionConfigDict(TypedDict):
    """TypedDict for Oracle WMS connection configuration."""

    base_url: str
    timeout: int
    max_retries: int
    verify_ssl: bool
    api_version: NotRequired[str]


class AuthConfigDict(TypedDict):
    """TypedDict for Oracle WMS authentication configuration."""

    username: str
    password: str
    auth_method: NotRequired[str]
    company_code: NotRequired[str]
    facility_code: NotRequired[str]


class EntityConfigDict(TypedDict):
    """TypedDict for Oracle WMS entity configuration."""

    name: str
    display_name: NotRequired[str]
    description: NotRequired[str]
    primary_keys: NotRequired[list[str]]
    replication_key: NotRequired[str]
    status: NotRequired[str]


class SchemaConfigDict(TypedDict):
    """TypedDict for Oracle WMS schema configuration."""

    entity_name: str
    properties: TAnyDict
    required_fields: list[str]
    field_count: int
    discovered_at: NotRequired[str]


class DiscoveryConfigDict(TypedDict):
    """TypedDict for Oracle WMS discovery configuration."""

    enable_discovery: bool
    enable_caching: bool
    auto_discover: NotRequired[bool]
    max_entities: NotRequired[int]
    entity_filter: NotRequired[list[str]]
    exclude_entities: NotRequired[list[str]]


class ExtractionConfigDict(TypedDict):
    """TypedDict for Oracle WMS extraction configuration."""

    page_size: int
    batch_size: int
    page_mode: str
    start_date: NotRequired[str]
    enable_incremental: NotRequired[bool]
    force_full_table: NotRequired[bool]
    incremental_overlap_minutes: NotRequired[int]
    lookback_minutes: NotRequired[int]


class TapConfigDict(TypedDict):
    """TypedDict for complete Oracle WMS tap configuration."""

    # Connection and authentication
    connection: ConnectionConfigDict
    authentication: AuthConfigDict

    # Oracle WMS specific
    company_code: str
    facility_code: str
    wms_api_version: str
    page_mode: str

    # Entity and extraction configuration
    entities: list[str]
    entity_filters: NotRequired[dict[str, dict[str, str]]]
    extraction: ExtractionConfigDict
    discovery: NotRequired[DiscoveryConfigDict]

    # Singer protocol
    singer_config: NotRequired[TAnyDict]


# =============================================================================
# ORACLE WMS DISCOVERY TYPEDDICTS
# =============================================================================


class DiscoveryResultDict(TypedDict):
    """TypedDict for Oracle WMS discovery result."""

    success: bool
    entity_name: str
    schema: TAnyDict
    metadata: TAnyDict
    errors: list[str]
    field_count: int
    discovery_time_ms: NotRequired[float]


class CatalogStreamDict(TypedDict):
    """TypedDict for Oracle WMS catalog stream definition."""

    tap_stream_id: str
    stream: str
    schema: TAnyDict
    key_properties: list[str]
    metadata: list[TAnyDict]


class CatalogDict(TypedDict):
    """TypedDict for Oracle WMS Singer catalog."""

    version: int
    streams: list[CatalogStreamDict]


# =============================================================================
# ORACLE WMS TYPE ALIASES
# =============================================================================

# Entity types
OracleEntityName = str
OracleEntityId = TEntityId
OracleFieldName = str
OracleFieldValue = TValue

# Singer types
SingerPropertyName = str
SingerPropertyType = str
SingerSchemaDict = TAnyDict
SingerStreamDict = TAnyDict

# Configuration types
OracleWmsConfigDict = TConfigDict
OracleWmsConnectionDict = TAnyDict
OracleWmsAuthDict = TAnyDict

# Discovery types
OracleWmsDiscoveryDict = TAnyDict
OracleWmsSchemaDict = TAnyDict
OracleWmsMetadataDict = TAnyDict

# Stream types
OracleWmsStreamDict = TAnyDict
OracleWmsRecordDict = TAnyDict

# API types
OracleWmsApiVersion = str
OracleWmsEnvironment = str
OracleWmsCompanyCode = str
OracleWmsFacilityCode = str

# Pagination types
OracleWmsPageMode = str
OracleWmsPageSize = int
OracleWmsPageToken = str

# Replication types
OracleWmsReplicationMode = str
OracleWmsReplicationKey = str
OracleWmsBookmark = str

# Error types
OracleWmsErrorCode = str
OracleWmsErrorMessage = str

# =============================================================================
# ORACLE WMS BUSINESS DOMAIN ALIASES
# =============================================================================

# Business entity identifiers
CompanyCode = str
FacilityCode = str
ItemCode = str
LocationCode = str
OrderNumber = str
AllocationId = str
PickNumber = str
ShipmentNumber = str
ContainerNumber = str
LpnNumber = str

# Business status types
EntityStatus = str
ProcessingStatus = str
ReplicationStatus = str
ValidationStatus = str

# Business operation types
OperationType = str
OperationMode = str
OperationResult = str

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AllocationId",
    "AuthConfigDict",
    "CatalogDict",
    "CatalogStreamDict",
    # Business domain aliases
    "CompanyCode",
    # Configuration TypedDicts
    "ConnectionConfigDict",
    "ContainerNumber",
    "DiscoveryConfigDict",
    # Discovery TypedDicts
    "DiscoveryResultDict",
    "EntityConfigDict",
    # Business status aliases
    "EntityStatus",
    "ExtractionConfigDict",
    "FacilityCode",
    "ItemCode",
    "LocationCode",
    "LpnNumber",
    "OperationMode",
    "OperationResult",
    # Business operation aliases
    "OperationType",
    "OracleEntityId",
    # Oracle WMS type aliases
    "OracleEntityName",
    "OracleFieldName",
    "OracleFieldValue",
    # API type aliases
    "OracleWmsApiVersion",
    "OracleWmsAuthDict",
    "OracleWmsBookmark",
    "OracleWmsCompanyCode",
    # Configuration type aliases
    "OracleWmsConfigDict",
    "OracleWmsConnectionDict",
    # Discovery type aliases
    "OracleWmsDiscoveryDict",
    "OracleWmsEnvironment",
    # Error type aliases
    "OracleWmsErrorCode",
    "OracleWmsErrorMessage",
    "OracleWmsFacilityCode",
    "OracleWmsMetadataDict",
    # Pagination type aliases
    "OracleWmsPageMode",
    "OracleWmsPageSize",
    "OracleWmsPageToken",
    "OracleWmsRecordDict",
    "OracleWmsReplicationKey",
    # Replication type aliases
    "OracleWmsReplicationMode",
    "OracleWmsSchemaDict",
    # Stream type aliases
    "OracleWmsStreamDict",
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
    "TapConfigDict",
    "ValidationStatus",
]
