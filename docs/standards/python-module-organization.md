# Python Module Organization & Semantic Patterns

**FLEXT Tap Oracle WMS - Singer Tap Module Architecture & Best Practices**

---

## 🏗️ **Module Architecture Overview**

FLEXT Tap Oracle WMS follows a **simplified layered module architecture** aligned with Singer SDK patterns and FLEXT ecosystem standards. This document defines the target architecture after refactoring from the current over-engineered 26-component structure.

### **Core Design Principles**

1. **Singer SDK Compliance**: Follows Singer specification and SDK patterns
2. **FLEXT Integration**: Leverages flext-core foundation and ecosystem libraries
3. **Single Responsibility**: Each module has one clear purpose
4. **Railway-Oriented**: FlextResult[T] threading through all operations
5. **Simplicity Over Complexity**: Favor maintainable solutions over engineering sophistication

---

## 📁 **Target Module Structure & Responsibilities**

### **Current State Analysis**

```python
# CURRENT OVER-ENGINEERED STRUCTURE (26 files, 8,179 lines)
src/flext_tap_oracle_wms/
├── tap.py                    # 1,042 lines - BLOATED main tap class
├── config_mapper.py          # 1,030 lines - UNNECESSARY mapping layer
├── streams.py                # 897 lines - OVER-ENGINEERED stream implementation
├── modern_discovery.py       # 791 lines - REDUNDANT "modern" discovery
├── config_validator.py       # 516 lines - COMPLEX validation system
├── entity_discovery.py       # 500 lines - THIRD discovery system
├── schema_flattener.py       # 484 lines - OVER-COMPLEX schema handling
├── schema_generator.py       # 425 lines - DUPLICATED schema logic
├── discovery.py              # 418 lines - LEGACY discovery system
├── exceptions.py             # 316 lines - OVER-ENGINEERED error hierarchy
├── models.py                 # 314 lines - DUPLICATED domain models
├── interfaces.py             # 287 lines - UNNECESSARY abstractions
├── config.py                 # 265 lines - COMPLEX configuration system
├── cache.py                  # 200 lines - OVER-ENGINEERED caching
├── simple_api.py             # 149 lines - IRONIC "simple" API
├── critical_validation.py    # 148 lines - SPECIALIZED validation
├── auth.py                   # 109 lines - REIMPLEMENTED authentication
├── type_mapping.py           # 101 lines - UNNECESSARY type aliases
├── client.py                 # 32 lines - WRAPPER around flext-oracle-wms
├── domain/                   # ADDITIONAL domain layer complexity
│   ├── models.py             # MORE domain models
│   ├── types.py              # MORE type definitions
│   └── __init__.py
└── [13 other support files]  # Additional complexity
```

**Issues**:

- **26 modules** where 6-8 would suffice
- **Multiple competing systems** (3 discovery, 4 configuration)
- **Massive files** (1,042 lines in tap.py vs target ~100-150 lines)
- **Code duplication** across similar modules
- **Over-abstraction** with unnecessary interfaces and patterns

### **Target Simplified Structure**

Following FLEXT Core patterns and Singer SDK best practices:

```python
# TARGET SIMPLIFIED STRUCTURE (6-8 files, ~800 lines total)
src/flext_tap_oracle_wms/
├── __init__.py               # 🎯 Public API gateway (~20 lines)
├── __version__.py            # 🎯 Version management (~10 lines)
├── tap.py                    # 🚀 Main tap class (~150 lines)
├── streams.py                # 🚀 Stream implementations (~200 lines)
├── config.py                 # ⚙️ Configuration using flext-core (~100 lines)
├── discovery.py              # 🏛️ Unified entity discovery (~150 lines)
├── schema.py                 # 🏛️ Schema utilities (~100 lines)
├── auth.py                   # 🔧 Authentication wrapper (~50 lines)
└── exceptions.py             # 🔧 Project-specific exceptions (~30 lines)
```

**Benefits**:

- **90% code reduction** (8,179 → ~800 lines)
- **Single responsibility** per module
- **Clear dependency flow** following Clean Architecture
- **FLEXT ecosystem integration** using foundation patterns
- **Singer SDK compliance** without over-engineering

---

## 📦 **Module Definitions & Semantic Patterns**

### **Foundation Layer - Public API**

```python
# __init__.py - Public API Gateway
"""
FLEXT Tap Oracle WMS - Singer-compliant Oracle WMS data extraction.

This module provides the main entry points for the Oracle WMS tap,
following Singer SDK patterns and FLEXT ecosystem standards.
"""

from flext_tap_oracle_wms.tap import FlextTapOracleWMS
from flext_tap_oracle_wms.config import WMSConfig
from flext_tap_oracle_wms.__version__ import __version__

__all__: FlextTypes.Core.StringList = [
    "FlextTapOracleWMS",
    "WMSConfig",
    "__version__",
]

# __version__.py - Version Management
"""Version information for FLEXT Tap Oracle WMS."""
__version__ = "0.9.0"
```

**Responsibility**: Establish clean public API and version management.

**Import Pattern**:

```python
# Standard ecosystem usage
from flext_tap_oracle_wms import FlextTapOracleWMS, WMSConfig
```

### **Application Layer - Tap Implementation**

```python
# tap.py - Main Tap Class (~150 lines)
"""
Oracle WMS Tap implementation using Singer SDK and FLEXT patterns.

Implements the main tap class following Singer specification with
FLEXT ecosystem integration for configuration, logging, and error handling.
"""

from singer_sdk import Tap
from flext_core import FlextLogger, FlextResult
from flext_oracle_wms import FlextOracleWmsClient

from flext_tap_oracle_wms.config import WMSConfig
from flext_tap_oracle_wms.streams import FlextTapOracleWMSStream
from flext_tap_oracle_wms.discovery import EntityDiscovery

class FlextTapOracleWMS(Tap):
    """
    Oracle WMS Singer tap implementation.

    Provides data extraction from Oracle Warehouse Management Systems
    using Singer protocol with FLEXT ecosystem integration.
    """

    name = "tap-oracle-wms"
    config_jsonschema = WMSConfig.schema()

    def __init__(self, config: dict):
        super().__init__(config)
        self.config = WMSConfig(**config)
        self.logger = FlextLogger(__name__)
        self._wms_client = None

    @property
    def wms_client(self) -> FlextOracleWmsClient:
        """Get configured WMS client using flext-oracle-wms library."""
        if not self._wms_client:
            self._wms_client = FlextOracleWmsClient(
                base_url=self.config.base_url,
                auth_method=self.config.auth_method,
                username=self.config.username,
                password=self.config.password,
                company_code=self.config.company_code,
                facility_code=self.config.facility_code,
            )
        return self._wms_client

    def discover_streams(self) -> List[Stream]:
        """Discover available streams from WMS API."""
        discovery = EntityDiscovery(self.wms_client)
        entities_result = discovery.discover_entities()

        if not entities_result.success:
            raise RuntimeError(f"Stream discovery failed: {entities_result.error}")

        return [
            FlextTapOracleWMSStream(tap=self, name=entity)
            for entity in entities_result.data
            if entity in self.config.entities
        ]
```

**Responsibility**: Main tap orchestration using Singer SDK with FLEXT integration.

**Usage Pattern**:

```python
from flext_tap_oracle_wms import FlextTapOracleWMS

config = {
    "base_url": "https://wms.example.com",
    "auth_method": "basic",
    "username": "user",
    # ... other config
}

tap = FlextTapOracleWMS(config)
streams = tap.discover_streams()
```

### **Application Layer - Stream Implementation**

```python
# streams.py - Stream Definitions (~200 lines)
"""
Oracle WMS stream implementations using Singer SDK patterns.

Implements data extraction streams for various WMS entities with
pagination, error handling, and schema management.
"""

from singer_sdk.streams import RESTStream
from singer_sdk.pagination import BaseHATEOASPaginator
from flext_core import FlextLogger, TAnyDict

from flext_tap_oracle_wms.schema import SchemaGenerator

class WMSPaginator(BaseHATEOASPaginator):
    """Oracle WMS HATEOAS pagination handler."""

    def get_next_url(self, response) -> Optional[str]:
        """Extract next page URL from HATEOAS links."""
        links = response.json().get("links", {})
        return links.get("next")

class FlextTapOracleWMSStream(RESTStream):
    """
    Base WMS stream for entity data extraction.

    Implements Singer RESTStream with WMS-specific pagination,
    authentication, and error handling.
    """

    def __init__(self, tap, name: str):
        super().__init__(tap)
        self.name = name
        self.path = f"/api/rest/v1/{name}"
        self.logger = FlextLogger(f"{__name__}.{name}")
        self._schema_generator = SchemaGenerator(tap.wms_client)

    @property
    def schema(self) -> Dict[str, object]:
        """Get stream schema from WMS metadata."""
        schema_result = self._schema_generator.generate_schema(self.name)
        if not schema_result.success:
            raise RuntimeError(f"Schema generation failed: {schema_result.error}")
        return schema_result.data

    def get_new_paginator(self) -> WMSPaginator:
        """Get paginator for WMS HATEOAS pagination."""
        return WMSPaginator()

    def get_url_params(self, context, next_page_token) -> Dict[str, object]:
        """Build URL parameters for WMS API requests."""
        params = {
            "limit": min(self.config.get("page_size", 1000), 1250),
            "companyCode": self.tap.config.company_code,
            "facilityCode": self.tap.config.facility_code,
        }

        # Add incremental extraction parameters
        if self.replication_key and self.get_starting_timestamp(context):
            params["lastModified"] = self.get_starting_timestamp(context).isoformat()

        return params

    def get_records(self, context) -> Iterator[TAnyDict]:
        """Extract records from WMS API."""
        self.logger.info(f"Starting extraction for entity: {self.name}")

        try:
            record_count = 0
            for record in super().get_records(context):
                record_count += 1
                if record_count % 1000 == 0:
                    self.logger.info(f"Extracted {record_count} records from {self.name}")
                yield record

            self.logger.info(f"Completed extraction: {record_count} records from {self.name}")

        except Exception as e:
            self.logger.error(f"Extraction failed for {self.name}: {e}", exc_info=True)
            raise
```

**Responsibility**: Data stream implementation with Singer SDK compliance.

### **Infrastructure Layer - Configuration**

```python
# config.py - Configuration Management (~100 lines)
"""
Configuration management using FLEXT Core patterns and Pydantic validation.

Implements unified configuration system with environment variable support,
validation, and FLEXT ecosystem integration.
"""

from typing import List, Optional
from pydantic import Field, validator
from flext_core import FlextConfig

class WMSConfig(FlextConfig):
    """
    Oracle WMS tap configuration using FLEXT patterns.

    Provides comprehensive configuration management with validation,
    environment variable support, and FLEXT ecosystem integration.
    """

    # Connection settings
    base_url: str = Field(..., description="Oracle WMS instance URL")
    auth_method: str = Field(..., regex="^(basic|oauth2)$", description="Authentication method")
    company_code: str = Field(..., description="WMS company code")
    facility_code: str = Field(..., description="WMS facility code")

    # Authentication settings
    username: Optional[str] = Field(None, description="Username for basic auth")
    password: Optional[str] = Field(None, description="Password for basic auth", repr=False)
    oauth_client_id: Optional[str] = Field(None, description="OAuth2 client ID")
    oauth_client_secret: Optional[str] = Field(None, description="OAuth2 client secret", repr=False)

    # Extraction settings
    entities: List[str] = Field(
        default=["item", "inventory"],
        description="List of WMS entities to extract"
    )
    page_size: int = Field(
        default=1000,
        le=1250,
        description="Records per page (max 1250)"
    )
    start_date: Optional[str] = Field(
        None,
        description="Start date for incremental extraction (ISO8601)"
    )

    class Config:
        """Pydantic configuration."""
        env_prefix = "TAP_ORACLE_WMS_"
        env_file = ".env"
        case_sensitive = False

    @validator("entities")
    def validate_entities(cls, v):
        """Validate entity names against available entities."""
        valid_entities = [
            "item", "location", "inventory", "order", "shipment",
            "receipt", "pick", "replenishment", "cycle_count"
        ]
        invalid = set(v) - set(valid_entities)
        if invalid:
            raise ValueError(f"Invalid entities: {invalid}")
        return v

    @validator("password", "oauth_client_secret")
    def validate_auth_config(cls, v, values):
        """Validate authentication configuration completeness."""
        auth_method = values.get("auth_method")

        if auth_method == "basic" and not values.get("username"):
            raise ValueError("Username required for basic authentication")
        if auth_method == "oauth2" and not values.get("oauth_client_id"):
            raise ValueError("OAuth client ID required for OAuth2 authentication")

        return v
```

**Responsibility**: Unified configuration with validation and environment support.

### **Domain Layer - Discovery & Schema**

```python
# discovery.py - Entity Discovery (~150 lines)
"""
Unified entity discovery using flext-oracle-wms library.

Implements entity discovery and metadata retrieval from Oracle WMS API
using FLEXT ecosystem patterns and error handling.
"""

from typing import List, Dict, object
from flext_core import FlextLogger, FlextResult
from flext_oracle_wms import FlextOracleWmsClient, WMSEntityMetadata

class EntityDiscovery:
    """
    Unified entity discovery for Oracle WMS.

    Handles entity discovery, metadata retrieval, and availability
    checking using the flext-oracle-wms library.
    """

    def __init__(self, wms_client: FlextOracleWmsClient):
        self.wms_client = wms_client
        self.logger = FlextLogger(__name__)

    def discover_entities(self) -> FlextResult[List[str]]:
        """Discover available entities from WMS API."""
        try:
            entities = self.wms_client.get_available_entities()
            self.logger.info(f"Discovered {len(entities)} WMS entities")
            return FlextResult[None].ok(entities)
        except Exception as e:
            self.logger.error(f"Entity discovery failed: {e}")
            return FlextResult[None].fail(f"Discovery error: {e}")

    def get_entity_metadata(self, entity: str) -> FlextResult[WMSEntityMetadata]:
        """Get metadata for specific entity."""
        try:
            metadata = self.wms_client.get_entity_metadata(entity)
            return FlextResult[None].ok(metadata)
        except Exception as e:
            self.logger.error(f"Metadata retrieval failed for {entity}: {e}")
            return FlextResult[None].fail(f"Metadata error: {e}")

# schema.py - Schema Generation (~100 lines)
"""
Schema generation utilities for Oracle WMS entities.

Converts WMS metadata to Singer JSON schemas with proper type mapping
and validation rules.
"""

from typing import Dict, object
from flext_core import FlextResult, FlextLogger
from flext_oracle_wms import FlextOracleWmsClient

from flext_tap_oracle_wms.discovery import EntityDiscovery

class SchemaGenerator:
    """
    Schema generation for WMS entities.

    Converts WMS entity metadata to Singer-compliant JSON schemas
    with proper type mapping and field definitions.
    """

    def __init__(self, wms_client: FlextOracleWmsClient):
        self.wms_client = wms_client
        self.discovery = EntityDiscovery(wms_client)
        self.logger = FlextLogger(__name__)

    def generate_schema(self, entity: str) -> FlextResult[Dict[str, object]]:
        """Generate Singer schema for WMS entity."""
        metadata_result = self.discovery.get_entity_metadata(entity)
        if not metadata_result.success:
            return FlextResult[None].fail(metadata_result.error)

        try:
            schema = self._convert_metadata_to_schema(metadata_result.data)
            return FlextResult[None].ok(schema)
        except Exception as e:
            return FlextResult[None].fail(f"Schema generation error: {e}")

    def _convert_metadata_to_schema(self, metadata) -> Dict[str, object]:
        """Convert WMS metadata to Singer JSON schema."""
        return {
            "type": "object",
            "properties": {
                field.name: self._map_field_type(field)
                for field in metadata.fields
            }
        }

    def _map_field_type(self, field) -> Dict[str, object]:
        """Map WMS field type to Singer type."""
        type_mapping = {
            "STRING": {"type": "string"},
            "NUMBER": {"type": "number"},
            "DATE": {"type": "string", "format": "date-time"},
            "BOOLEAN": {"type": "boolean"},
        }
        return type_mapping.get(field.type, {"type": "string"})
```

**Responsibility**: Entity discovery and schema generation using WMS metadata.

### **Infrastructure Layer - Authentication & Utilities**

```python
# auth.py - Authentication Wrapper (~50 lines)
"""
Authentication wrapper using flext-oracle-wms library.

Provides authentication abstraction using the FLEXT ecosystem
WMS library without reimplementing authentication logic.
"""

from flext_oracle_wms import FlextOracleWmsClient
from flext_tap_oracle_wms.config import WMSConfig

class AuthenticationManager:
    """
    Authentication manager using flext-oracle-wms.

    Delegates authentication to the WMS library for consistency
    and to avoid code duplication across the ecosystem.
    """

    @staticmethod
    def create_authenticated_client(config: WMSConfig) -> FlextOracleWmsClient:
        """Create authenticated WMS client."""
        return FlextOracleWmsClient(
            base_url=config.base_url,
            auth_method=config.auth_method,
            username=config.username,
            password=config.password,
            company_code=config.company_code,
            facility_code=config.facility_code,
        )

# exceptions.py - Project-Specific Exceptions (~30 lines)
"""
Project-specific exceptions for Oracle WMS tap.

Defines tap-specific exceptions while leveraging FLEXT core
exception hierarchy for consistency.
"""

from flext_core import FlextExceptions.Error

class WMSTapError(FlextExceptions.Error):
    """Base exception for WMS tap errors."""
    pass

class WMSConfigurationError(WMSTapError):
    """Configuration validation errors."""
    pass

class WMSDiscoveryError(WMSTapError):
    """Entity discovery errors."""
    pass

class WMSSchemaError(WMSTapError):
    """Schema generation errors."""
    pass
```

**Responsibility**: Authentication delegation and project-specific error handling.

---

## 🎯 **Semantic Naming Conventions**

### **Module Naming Standards**

Following FLEXT ecosystem patterns with Singer tap specificity:

```python
# Core modules - descriptive and focused
tap.py                      # Main tap implementation (FlextTapOracleWMS)
streams.py                  # Stream definitions (FlextTapOracleWMSStream, WMSPaginator)
config.py                   # Configuration management (WMSConfig)
discovery.py                # Entity discovery (EntityDiscovery)
schema.py                   # Schema utilities (SchemaGenerator)
auth.py                     # Authentication (AuthenticationManager)
exceptions.py               # Project exceptions (WMSTapError, etc.)
```

**Pattern**: Each module name clearly indicates its primary responsibility.

### **Class Naming Standards**

```python
# Main classes follow FLEXT + Singer patterns
FlextTapOracleWMS               # Main tap class (Singer SDK pattern)
WMSConfig                  # Configuration (FLEXT pattern)
FlextTapOracleWMSStream                  # Stream implementation (Singer + WMS context)
WMSPaginator              # Pagination handler (Singer + WMS context)
EntityDiscovery           # Business logic class (descriptive)
SchemaGenerator           # Utility class (descriptive)
AuthenticationManager     # Service class (descriptive)

# Error classes follow FLEXT hierarchy
WMSTapError               # Base error (FLEXT pattern)
WMSConfigurationError     # Specific error (descriptive)
WMSDiscoveryError         # Specific error (descriptive)
```

**Pattern**: Classes use descriptive names with context (WMS) and purpose.

### **Function and Method Naming**

```python
# Action-oriented naming
def discover_streams() -> List[Stream]:           # Singer SDK pattern
def discover_entities() -> FlextResult[List[str]]: # FLEXT pattern
def generate_schema(entity: str) -> FlextResult[Dict]: # Business action
def create_authenticated_client(config) -> Client:    # Factory pattern

# Property naming
@property
def wms_client(self) -> FlextOracleWmsClient:     # Resource access
@property
def schema(self) -> Dict[str, object]:               # Computed property
```

**Pattern**: Verbs for actions, nouns for properties, clear business intent.

---

## 📦 **Import Patterns & Dependencies**

### **Dependency Hierarchy**

```python
# Dependencies flow following Clean Architecture
Application Layer (tap.py, streams.py)
    ↓
Domain Layer (discovery.py, schema.py, config.py)
    ↓
Infrastructure Layer (auth.py, exceptions.py)
    ↓
FLEXT Foundation (flext-core, flext-oracle-wms)
    ↓
External Libraries (singer-sdk, pydantic)
```

**Rule**: Higher layers depend on lower layers, never the reverse.

### **Standard Import Patterns**

```python
# External dependencies first
from typing import List, Dict, Optional, Iterator

from pydantic import Field, validator
from singer_sdk import Tap
from singer_sdk.streams import RESTStream

# FLEXT ecosystem imports
from flext_core import FlextConfig, FlextLogger, FlextResult, TAnyDict
from flext_oracle_wms import FlextOracleWmsClient, WMSEntityMetadata

# Project imports (relative)
from flext_tap_oracle_wms.config import WMSConfig
from flext_tap_oracle_wms.discovery import EntityDiscovery
from flext_tap_oracle_wms.schema import SchemaGenerator
```

**Pattern**: External → FLEXT ecosystem → Project modules.

### **Anti-Patterns (Forbidden)**

```python
# ❌ Don't import everything
from flext_tap_oracle_wms import *

# ❌ Don't create circular dependencies
# config.py importing from tap.py

# ❌ Don't bypass abstraction layers
# tap.py directly importing from flext_oracle_wms internals

# ❌ Don't duplicate FLEXT functionality
from custom_result import CustomResult  # Use FlextResult instead
```

---

## 🏛️ **Architectural Patterns for Singer Taps**

### **Singer SDK Integration Pattern**

```python
# Standard Singer tap structure
class FlextTapOracleWMS(Tap):
    """Main tap following Singer SDK patterns."""

    name = "tap-oracle-wms"                    # Tap identifier
    config_jsonschema = WMSConfig.schema()     # Configuration schema

    def discover_streams(self) -> List[Stream]: # Required method
        """Discover available data streams."""
        pass

    def sync_all(self) -> None:                # Optional override
        """Custom sync logic if needed."""
        pass

class FlextTapOracleWMSStream(RESTStream):
    """Stream following Singer RESTStream pattern."""

    @property
    def schema(self) -> Dict[str, object]:        # Required property
        """JSON schema for stream records."""
        pass

    def get_records(self, context) -> Iterator: # Required method
        """Generate stream records."""
        pass
```

### **FLEXT Integration Pattern**

```python
# Configuration using FlextConfig
class WMSConfig(FlextConfig):
    """Configuration with FLEXT patterns."""

    class Config:
        env_prefix = "TAP_ORACLE_WMS_"

# Error handling using FlextResult
def discover_entities(self) -> FlextResult[List[str]]:
    """Business logic with railway-oriented programming."""
    try:
        entities = self.wms_client.get_available_entities()
        return FlextResult[None].ok(entities)
    except Exception as e:
        return FlextResult[None].fail(f"Discovery failed: {e}")

# Logging using FLEXT patterns
self.logger = FlextLogger(__name__)
self.logger.info("Starting extraction", entity=entity_name)
```

### **Clean Architecture Boundaries**

```python
# Application Layer - orchestrates business logic
class FlextTapOracleWMS:
    def discover_streams(self):
        # Orchestrates discovery without business logic
        discovery = EntityDiscovery(self.wms_client)
        return discovery.discover_entities()

# Domain Layer - contains business logic
class EntityDiscovery:
    def discover_entities(self):
        # Business logic for entity discovery
        pass

# Infrastructure Layer - external concerns
class AuthenticationManager:
    def create_authenticated_client(self):
        # Infrastructure concern - external API client
        pass
```

---

## 🔄 **Migration Strategy from Current Architecture**

### **Refactoring Approach**

#### **Phase 1: Elimination (Week 1)**

```python
# REMOVE these over-engineered modules:
❌ config_mapper.py          # 1,030 lines → merge into config.py
❌ modern_discovery.py       # 791 lines → merge into discovery.py
❌ config_validator.py       # 516 lines → merge into config.py validation
❌ entity_discovery.py       # 500 lines → merge into discovery.py
❌ schema_flattener.py       # 484 lines → simplify in schema.py
❌ schema_generator.py       # 425 lines → merge into schema.py
❌ interfaces.py             # 287 lines → remove unnecessary abstractions
❌ models.py                 # 314 lines → use flext-oracle-wms models
❌ cache.py                  # 200 lines → remove caching complexity
❌ simple_api.py             # 149 lines → integrate into streams.py
❌ critical_validation.py    # 148 lines → merge into config.py
❌ type_mapping.py           # 101 lines → merge into schema.py
❌ client.py                 # 32 lines → remove wrapper
❌ domain/ directory         # Use flext-oracle-wms domain models
```

#### **Phase 2: Consolidation (Week 2)**

```python
# CONSOLIDATE remaining modules:
✅ tap.py           # 1,042 → ~150 lines (remove complexity)
✅ streams.py       # 897 → ~200 lines (simplify implementation)
✅ discovery.py     # 418 → ~150 lines (unified discovery)
✅ config.py        # 265 → ~100 lines (use FlextConfig)
✅ auth.py          # 109 → ~50 lines (wrapper around flext-oracle-wms)
✅ exceptions.py    # 316 → ~30 lines (use FlextExceptions.Error hierarchy)
✅ schema.py        # NEW → ~100 lines (unified schema handling)
```

#### **Phase 3: Integration (Week 3)**

```python
# INTEGRATE with FLEXT ecosystem:
from flext_core import FlextConfig, FlextResult, FlextLogger
from flext_oracle_wms import FlextOracleWmsClient, WMSEntityMetadata

# REMOVE custom implementations:
- Custom configuration classes → use FlextConfig
- Custom error handling → use FlextResult railway pattern
- Custom logging → use FlextLogger()
- Custom WMS client → use FlextOracleWmsClient
- Custom result types → use FlextResult[T]
```

### **Migration Validation**

```python
# BEFORE (current):
Lines of Code: 8,179
Module Count: 26
Discovery Systems: 3 competing implementations
Configuration Systems: 4 different approaches
Test Coverage: ~70% (27% disabled)

# AFTER (target):
Lines of Code: ~800 (90% reduction)
Module Count: 8 (69% reduction)
Discovery Systems: 1 unified implementation
Configuration Systems: 1 FlextConfig-based
Test Coverage: 100% (all tests enabled)
```

---

## 🧪 **Testing Module Organization**

### **Test Structure Alignment**

```python
# Test structure mirrors simplified source structure
tests/
├── unit/                          # Unit tests for each module
│   ├── test_tap.py               # Tests for tap.py
│   ├── test_streams.py           # Tests for streams.py
│   ├── test_config.py            # Tests for config.py
│   ├── test_discovery.py         # Tests for discovery.py
│   ├── test_schema.py            # Tests for schema.py
│   ├── test_auth.py              # Tests for auth.py
│   └── test_exceptions.py        # Tests for exceptions.py
├── integration/                   # Integration tests
│   ├── test_wms_integration.py   # WMS API integration
│   ├── test_singer_compliance.py # Singer protocol compliance
│   └── test_flext_integration.py # FLEXT ecosystem integration
├── fixtures/                     # Test data and mocks
│   ├── wms_responses.json        # Mock WMS API responses
│   ├── config_samples.json       # Configuration examples
│   └── schema_samples.json       # Schema definitions
└── conftest.py                   # Pytest configuration and fixtures
```

### **Testing Patterns**

```python
# Test organization follows module responsibility
def test_tap_discover_streams():
    """Test main tap stream discovery functionality."""
    pass

def test_wms_stream_get_records():
    """Test stream record extraction."""
    pass

def test_config_validation():
    """Test configuration validation with FlextConfig."""
    pass

def test_entity_discovery():
    """Test entity discovery using FlextResult patterns."""
    pass
```

---

## 📏 **Quality Standards & Validation**

### **Module Quality Metrics**

```python
# Target metrics per module
Lines per Module: 50-200 (max 200)
Cyclomatic Complexity: <10 per function
Test Coverage: 95% minimum
Type Annotation Coverage: 100%
Documentation Coverage: 100%

# Quality gates
make lint
make type-check           # MyPy strict mode
make test                 # 95% coverage minimum
make security             # Bandit + pip-audit
```

### **Documentation Standards**

```python
def discover_entities(self) -> FlextResult[List[str]]:
    """
    Discover available entities from Oracle WMS API.

    Connects to the WMS instance and retrieves the list of available
    entities for data extraction. Uses the flext-oracle-wms library
    for consistent API interaction across the FLEXT ecosystem.

    Returns:
        FlextResult[List[str]]: Success contains list of entity names,
        failure contains detailed error message explaining the issue.

    Example:
        >>> discovery = EntityDiscovery(wms_client)
        >>> result = discovery.discover_entities()
        >>> if result.success:
        ...     print(f"Found entities: {result.data}")
        ... else:
        ...     print(f"Discovery failed: {result.error}")
    """
    pass
```

---

## 🌐 **FLEXT Ecosystem Integration Standards**

### **Consistent Pattern Usage**

```python
# ✅ Use FLEXT patterns consistently
from flext_core import FlextConfig, FlextResult, FlextLogger

class WMSConfig(FlextConfig):          # Configuration
    pass

def process_data() -> FlextResult[Data]:     # Error handling
    pass

logger = FlextLogger(__name__)                # Logging

# ❌ Don't create project-specific alternatives
class CustomConfig(BaseModel):               # Use FlextConfig
class CustomResult[T]:                       # Use FlextResult
custom_logger = logging.getLogger()          # Use FlextLogger()
```

### **Library Integration**

```python
# ✅ Use ecosystem libraries
from flext_oracle_wms import FlextOracleWmsClient, WMSEntityMetadata
from flext_meltano import Tap, Stream

# ❌ Don't reimplement library functionality
class CustomWMSClient:                       # Use FlextOracleWmsClient
class CustomTap(BaseTap):                    # Use flext_meltano.Tap
```

---

## 📋 **Module Creation Checklist**

### **New Module Standards**

- [ ] **Single Responsibility**: Module has one clear purpose
- [ ] **Appropriate Layer**: Placed in correct architectural layer
- [ ] **FLEXT Integration**: Uses ecosystem patterns consistently
- [ ] **Type Annotations**: 100% type coverage with MyPy compliance
- [ ] **Error Handling**: Uses FlextResult for all error conditions
- [ ] **Documentation**: Comprehensive docstrings with examples
- [ ] **Testing**: 95% coverage with unit and integration tests
- [ ] **Import Standards**: Follows dependency hierarchy rules
- [ ] **Line Limit**: 50-200 lines maximum per module
- [ ] **Quality Gates**: Passes all linting, type checking, and security scans

### **Refactoring Validation**

- [ ] **Code Reduction**: Achieved 80%+ line reduction from current
- [ ] **Module Consolidation**: Reduced from 26 to 6-8 modules
- [ ] **Functionality Preservation**: All current features maintained
- [ ] **Performance**: No performance regressions
- [ ] **Test Coverage**: 100% of tests enabled and passing
- [ ] **FLEXT Compliance**: Full ecosystem integration validated
- [ ] **Singer Compliance**: Singer protocol tests passing
- [ ] **Documentation**: Complete documentation update

---

**Last Updated**: August 4, 2025
**Target Audience**: FLEXT Tap Oracle WMS developers and architects
**Scope**: Module organization for Singer tap refactoring
**Status**: Architecture defined, implementation pending
