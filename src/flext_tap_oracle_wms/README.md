# FLEXT Tap Oracle WMS - Core Module

## Overview

This directory contains the core implementation of FLEXT Tap Oracle WMS, a Singer-compliant tap for extracting data from Oracle Warehouse Management Systems. The module provides comprehensive WMS integration capabilities while following FLEXT ecosystem patterns.

## Module Structure

### Core Components

#### **Main Interface**

- [`tap.py`](tap.py) - Main FlextTapOracleWMS class implementing Singer SDK patterns
- [`cli.py`](cli.py) - Command-line interface and entry point
- [`streams.py`](streams.py) - Stream definitions with WMS-specific pagination

#### **Authentication & Client**

- [`auth.py`](auth.py) - Authentication management (Basic Auth, OAuth2)
- [`client.py`](client.py) - HTTP client with Oracle WMS API integration

#### **Configuration Management**

- [`config.py`](config.py) - Configuration models using Pydantic
- [`config_mapper.py`](config_mapper.py) - Configuration mapping utilities
- [`config_validator.py`](config_validator.py) - Business rule validation
- [`critical_validation.py`](critical_validation.py) - Environment validation

#### **Discovery & Schema**

- [`discovery.py`](discovery.py) - Entity discovery and schema generation
- [`entity_discovery.py`](entity_discovery.py) - WMS entity discovery logic
- [`schema_generator.py`](schema_generator.py) - Singer schema generation
- [`schema_flattener.py`](schema_flattener.py) - Nested data structure flattening
- [`type_mapping.py`](type_mapping.py) - WMS to Singer type mapping

#### **Performance & Utilities**

- [`cache.py`](cache.py) - Response caching for performance optimization
- [`simple_api.py`](simple_api.py) - Simplified API interface
- [`interfaces.py`](interfaces.py) - Abstract interfaces and protocols

#### **Domain Models**

- [`models.py`](models.py) - Data models and business entities
- [`domain/`](domain/) - Domain-driven design components
  - [`models.py`](domain/models.py) - Core domain models
  - [`types.py`](domain/types.py) - Domain-specific types

#### **Support Files**

- [`exceptions.py`](exceptions.py) - Custom exception hierarchy
- [`__init__.py`](__init__.py) - Module initialization and exports
- [`__main__.py`](__main__.py) - Module execution entry point
- [`__version__.py`](__version__.py) - Version information
- [`py.typed`](py.typed) - Type hint marker for MyPy

## Architecture Overview

### **Current Architecture Status**

⚠️ **OVER-ENGINEERED**: This module contains 26 Python files with 8,179 lines of code, representing significant architectural complexity that will be simplified in future releases.

**Target Simplification**:

- **Current**: 26 files, 8,179 lines
- **Target**: 6-8 files, ~800 lines
- **Reduction**: ~90% code reduction while maintaining functionality

### **FLEXT Ecosystem Integration**

The module integrates with FLEXT ecosystem components:

- **flext-core**: Foundation patterns, logging, result handling
- **flext-oracle-wms**: Oracle WMS API client and data models
- **flext-meltano**: Singer/Meltano orchestration
- **flext-observability**: Monitoring and health checks

### **Singer SDK Compliance**

- Inherits from `singer_sdk.Tap` and `singer_sdk.streams.RESTStream`
- Implements custom `WMSPaginator` for Oracle WMS HATEOAS pagination
- Uses Singer SDK typing for schema definitions
- Supports both full table and incremental replication

## Key Components Usage

### **Main Tap Usage**

```python
from flext_tap_oracle_wms.tap import FlextTapOracleWMS

config = {
    "base_url": "https://wms.example.com",
    "auth_method": "basic",
    "username": "user",
    "password": "pass",
    "company_code": "COMPANY",
    "facility_code": "FACILITY"
}

tap = FlextTapOracleWMS(config)
streams = tap.discover_streams()
```

### **Authentication**

```python
from flext_tap_oracle_wms.auth import get_wms_authenticator

auth = get_wms_authenticator(stream, config)
authenticated_request = auth(request)
```

### **Entity Discovery**

```python
from flext_tap_oracle_wms.entity_discovery import EntityDiscovery

discovery = EntityDiscovery(wms_client)
entities = discovery.discover_entities()
```

### **Configuration Validation**

```python
from flext_tap_oracle_wms.config_validator import ConfigValidator

validator = ConfigValidator()
result = validator.validate_config(config)
```

## Development Guidelines

### **Quality Standards**

- **Python 3.13+** with strict type hints
- **MyPy strict mode** type checking
- **Ruff linting** with comprehensive rules
- **90% test coverage** requirement
- **Enterprise-grade documentation** with comprehensive docstrings

### **Code Patterns**

- Follow Clean Architecture principles
- Use dependency injection patterns from flext-core
- Implement proper error handling with custom exceptions
- Use Pydantic models for configuration and validation
- Follow Singer SDK patterns for stream implementation

### **FLEXT Integration**

- Use `flext_core.FlextLogger()` for logging
- Implement `FlextResult` patterns for error handling
- Follow FLEXT configuration patterns
- Integrate with FLEXT observability standards

## Refactoring Notes

### **Architectural Issues**

1. **Excessive Component Count**: 26 files for a Singer tap is over-engineered
2. **Code Duplication**: Multiple discovery and configuration systems
3. **Complex Abstractions**: Unnecessary abstraction layers
4. **Integration Complexity**: Overlapping responsibilities with flext-oracle-wms

### **Simplification Strategy**

1. **Consolidate Discovery**: Merge discovery components into single module
2. **Simplify Configuration**: Single configuration approach using FLEXT patterns
3. **Reduce Abstractions**: Eliminate unnecessary interfaces and adapters
4. **Leverage FLEXT Libraries**: Use flext-oracle-wms instead of duplicating functionality

See [docs/TODO.md](../../docs/TODO.md) for complete refactoring plan.

## Testing

### **Test Coverage**

- Unit tests available for most components
- Integration tests currently disabled (external dependencies)
- E2E tests disabled pending refactoring

### **Running Tests**

```bash
# Run unit tests for this module
pytest tests/unit/ -v

# Test specific components
pytest tests/unit/test_auth_comprehensive.py
pytest tests/unit/test_client_comprehensive.py
```

See [tests/README.md](../../tests/README.md) for complete testing documentation.

## Contributing

### **Development Workflow**

1. Follow FLEXT ecosystem patterns
2. Maintain Singer SDK compliance
3. Use comprehensive type hints
4. Write enterprise-grade documentation
5. Ensure test coverage above 90%

### **Code Review Focus**

- Architectural simplification opportunities
- FLEXT ecosystem integration
- Singer protocol compliance
- Performance optimization
- Security best practices

---

**Status**: 1.0.0 Release Preparation | **Architecture**: Requires Refactoring | **Updated**: 2025-08-13
