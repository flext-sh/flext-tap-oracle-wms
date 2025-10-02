# CLAUDE.md - FLEXT Tap Oracle WMS Quality Refactoring Guide

**Project**: FLEXT Tap Oracle WMS - Enterprise Oracle Warehouse Management System Extraction  
**Status**: Refactored but Quality Enhancement Required · 1.0.0 Release Preparation | **Architecture**: Clean Singer Tap + FLEXT Integration  
**Dependencies**: Python 3.13+, flext-core, flext-oracle-wms, flext-meltano, singer-sdk  
**Coverage Target**: 75% minimum (proven achievable), 100% aspirational target | **Current Status**: MyPy ✅, Ruff ✅, Tests Pending
**Authority**: FLEXT-TAP-ORACLE-WMS | **Last Updated**: 2025-01-08

**Hierarchy**: This document provides project-specific standards based on workspace-level patterns defined in [../CLAUDE.md](../CLAUDE.md). For architectural principles, quality gates, and MCP server usage, reference the main workspace standards.

## 📋 DOCUMENT STRUCTURE & REFERENCES

**Quick Links**:
- **[~/.claude/commands/flext.md](~/.claude/commands/flext.md)**: Optimization command for module refactoring (USE with `/flext` command)
- **[../CLAUDE.md](../CLAUDE.md)**: FLEXT ecosystem standards and domain library rules

**CRITICAL INTEGRATION DEPENDENCIES**:
- **flext-meltano**: MANDATORY for ALL Singer operations (ZERO TOLERANCE for direct singer-sdk without flext-meltano)
- **flext-oracle-wms**: MANDATORY for ALL Oracle WMS operations (ZERO TOLERANCE for bypassing WMS domain)
- **flext-db-oracle**: MANDATORY for ALL Oracle Database operations (ZERO TOLERANCE for direct SQLAlchemy/oracledb imports)
- **flext-core**: Foundation patterns (FlextResult, FlextService, FlextContainer)

## 🔗 MCP SERVER INTEGRATION (MANDATORY)

| MCP Server              | Purpose                                                         | Status          |
| ----------------------- | --------------------------------------------------------------- | --------------- |
| **serena-flext**        | Semantic code analysis, symbol manipulation, refactoring        | **MANDATORY**   |
| **sequential-thinking** | Oracle WMS data processing and Singer protocol architecture     | **RECOMMENDED** |
| **context7**            | Third-party library documentation (Singer SDK, Oracle WMS)      | **RECOMMENDED** |
| **github**              | Repository operations and Singer ecosystem PRs                  | **ACTIVE**      |

**Usage**: `claude mcp list` for available servers, leverage for Singer-specific development patterns and Oracle WMS extraction analysis.

---

## 🎯 PROJECT MISSION STATEMENT

Transform FLEXT Tap Oracle WMS into a **production-ready, enterprise-grade Oracle Warehouse Management System extraction tap** implementing Singer protocol with zero tolerance quality standards. This tap provides comprehensive WMS data extraction capabilities while leveraging the FLEXT ecosystem's proven patterns and infrastructure.

### 🏆 SUCCESS CRITERIA (EVIDENCE-BASED VALIDATION)

- **✅ Architecture Simplification**: Successfully refactored from 26 files/8,179 lines to 11 files/2,121 lines
- **✅ MyPy Excellence**: 0 type errors achieved (previously 37 errors)
- **✅ Ruff Compliance**: All linting rules passing with comprehensive code standards
- **🔄 90% Test Coverage**: Comprehensive test implementation required (measured via `pytest --cov=src --cov-report=term`)
- **🔄 Singer Protocol Compliance**: Full catalog discovery + data extraction validation (verified via `make discover && make run`)
- **🔄 WMS Integration Excellence**: Robust Oracle WMS connectivity with performance optimization (verified via `make wms-test`)

---

## 🚫 PROJECT PROHIBITIONS (ZERO TOLERANCE ENFORCEMENT)

### ⛔ ABSOLUTELY FORBIDDEN ACTIONS

1. **Architecture Regression**:
   - NEVER return to over-engineered patterns (previous 26 files)
   - NEVER create unnecessary abstractions for Singer tap functionality
   - NEVER duplicate functionality available in flext-oracle-wms
   - NEVER ignore the simplified architecture achievements

2. **Quality Degradation**:
   - NEVER reintroduce MyPy type errors (maintain 0 errors)
   - NEVER compromise Ruff linting compliance
   - NEVER disable security scanning (Bandit/pip-audit)
   - NEVER reduce test coverage below 90% target

3. **WMS Integration Violations**:
   - NEVER implement WMS API communication directly (use flext-oracle-wms)
   - NEVER hardcode WMS endpoints or configuration
   - NEVER ignore Oracle WMS pagination and rate limiting
   - NEVER bypass WMS authentication and security requirements

4. **Singer Protocol Violations**:
   - NEVER return data without proper Singer RECORD messages
   - NEVER skip catalog discovery implementation
   - NEVER ignore incremental replication for applicable streams
   - NEVER create non-compliant stream schemas

---

## 🏗️ PROJECT ARCHITECTURE (CURRENT SIMPLIFIED STATE)

### Successfully Refactored Architecture

```python
# CURRENT CLEAN STRUCTURE (11 files, 2,121 lines - MAINTAIN THIS SIMPLICITY)
src/flext_tap_oracle_wms/
   tap_cli.py                 # Main tap CLI entry point (Singer SDK integration)
   tap_client.py              # Oracle WMS client integration (uses flext-oracle-wms)
   tap_config.py              # Configuration management with Pydantic validation
   tap_streams.py             # Singer stream implementations for WMS entities
   tap_models.py              # Data models and schemas for WMS data
   utils.py                   # Utility functions for data processing
   typings.py                 # Type definitions and type aliases
   tap_exceptions.py          # Project-specific exception hierarchy
   # Additional supporting files: __init__.py, py.typed, __version__.py
```

### Service Architecture Pattern (MANDATORY)

```python
class FlextTapOracleWmsService(FlextDomainService):
    """Single unified service class following flext-core patterns.

    This class consolidates all Oracle WMS tap-related operations,
    leveraging flext-oracle-wms infrastructure while maintaining
    the simplified architecture achieved through refactoring.
    """

    def __init__(self, **data) -> None:
        """Initialize service with proper dependency injection."""
        super().__init__(**data)
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
        self._wms_client = self._container.get(FlextOracleWmsClient)  # From flext-oracle-wms

    def extract_wms_entity(
        self,
        config: dict,
        entity_type: str,
        page_size: int = 1000
    ) -> FlextResult[Iterator[dict]]:
        """Extract data from Oracle WMS entity with comprehensive error handling."""
        if not config or not entity_type:
            return FlextResult[Iterator[dict]].fail("Configuration and entity type are required")

        try:
            # Authenticate using flext-oracle-wms
            auth_result = self._wms_client.authenticate(
                base_url=config["base_url"],
                username=config["username"],
                password=config["password"],
                auth_method=config.get("auth_method", "basic"),
                company_code=config.get("company_code"),
                facility_code=config.get("facility_code")
            )

            if auth_result.is_failure:
                return FlextResult[Iterator[dict]].fail(f"WMS authentication failed: {auth_result.error}")

            # Extract entity data with pagination
            extraction_result = self._wms_client.extract_entity_paginated(
                entity_type=entity_type,
                page_size=min(page_size, 1250),  # Oracle WMS limit
                entity_filters=config.get("entity_filters", {}),
                field_selection=config.get("field_selection", {}),
                start_date=config.get("start_date")
            )

            if extraction_result.is_success:
                return FlextResult[Iterator[dict]].ok(extraction_result.value)
            else:
                return FlextResult[Iterator[dict]].fail(f"WMS extraction failed: {extraction_result.error}")

        except Exception as e:
            self._logger.error(f"Oracle WMS extraction error: {e}")
            return FlextResult[Iterator[dict]].fail(f"WMS extraction error: {str(e)}")

    def discover_wms_schema(self, config: dict, entity_type: str) -> FlextResult[dict]:
        """Discover WMS entity schema for Singer catalog generation."""
        try:
            schema_result = self._wms_client.get_entity_schema(entity_type)

            if schema_result.is_success:
                # Convert WMS schema to Singer schema format
                singer_schema = self._convert_wms_schema_to_singer(schema_result.value)
                return FlextResult[dict].ok(singer_schema)
            else:
                return FlextResult[dict].fail(f"WMS schema discovery failed: {schema_result.error}")

        except Exception as e:
            self._logger.error(f"WMS schema discovery error: {e}")
            return FlextResult[dict].fail(f"Schema discovery error: {str(e)}")

    def _convert_wms_schema_to_singer(self, wms_schema: dict) -> dict:
        """Convert Oracle WMS schema to Singer schema format."""
        properties = {}

        for field in wms_schema.get("fields", []):
            field_name = field["name"]
            wms_type = field["type"]

            # Oracle WMS to Singer type mapping
            if wms_type in ["String", "VARCHAR2", "CHAR"]:
                singer_type = {"type": "string"}
            elif wms_type in ["Number", "INTEGER", "DECIMAL"]:
                singer_type = {"type": "number"}
            elif wms_type in ["Date", "TIMESTAMP", "DATETIME"]:
                singer_type = {"type": "string", "format": "date-time"}
            elif wms_type == "Boolean":
                singer_type = {"type": "boolean"}
            else:
                singer_type = {"type": "string"}  # Default fallback

            # Add nullability
            if field.get("nullable", True):
                singer_type = {"anyOf": [singer_type, {"type": "null"}]}

            properties[field_name] = singer_type

        return {
            "type": "object",
            "properties": properties,
            "required": []  # WMS typically doesn't enforce required fields strictly
        }

    def validate_configuration(self, config: dict) -> FlextResult[bool]:
        """Validate tap configuration with business rules."""
        required_fields = ["base_url", "username", "password"]
        for field in required_fields:
            if not config.get(field):
                return FlextResult[bool].fail(f"Required configuration field missing: {field}")

        # Validate page_size limits
        page_size = config.get("page_size", 1000)
        if page_size > 1250:
            return FlextResult[bool].fail("Oracle WMS page_size cannot exceed 1250")

        return FlextResult[bool].ok(True)
```

---

## ⚡ IMPLEMENTATION STRATEGY (PRIORITY-BASED EXECUTION)

### Phase 1: Foundation Assessment & Test Implementation (MANDATORY FIRST)

#### 1.1 Current State Validation (MAINTAIN ACHIEVEMENTS)

```bash
# VERIFY: Refactoring achievements maintained
find src/ -name "*.py" | wc -l  # Should be 11 files (not 26+)
wc -l src/flext_tap_oracle_wms/*.py | tail -1  # Should be ~2,121 lines (not 8,179+)

# VERIFY: Quality achievements maintained
mypy src/ --strict --show-error-codes 2>&1 | wc -l  # Should be 0 errors
ruff check src/ --statistics | grep "errors"  # Should be 0 errors

# ASSESS: Current test coverage state
pytest --cov=src --cov-report=term | grep "TOTAL"
# Document baseline before test implementation

# MAP: Current functionality status
python -c "from flext_tap_oracle_wms import FlextTapOracleWms; tap = FlextTapOracleWms(); print('✅ Import successful')"
# Verify basic functionality works
```

#### 1.2 Test Implementation Strategy

```bash
# PRIORITY 1: Unit tests for core functionality
pytest tests/unit/ --cov=src/flext_tap_oracle_wms --cov-report=term-missing
# Target: Achieve 70% coverage with unit tests

# PRIORITY 2: Integration tests with WMS connectivity
pytest tests/integration/ --cov=src/flext_tap_oracle_wms --cov-report=term-missing
# Target: Achieve 85% coverage with integration tests

# PRIORITY 3: Singer protocol tests
pytest tests/unit/ -m singer --cov=src/flext_tap_oracle_wms --cov-report=term-missing
# Target: Achieve 90% coverage with Singer protocol tests
```

### Phase 2: Service Architecture Enhancement (MAINTAIN SIMPLICITY)

#### 2.1 Unified Service Implementation (DO NOT OVER-ENGINEER)

```python
# MAINTAIN: Simple, focused service implementation
class FlextTapOracleWmsService(FlextDomainService):
    """Unified WMS service - keep simple, avoid over-abstraction."""

    def __init__(self, **data) -> None:
        super().__init__(**data)
        # Simple dependency injection
        self._wms_client = self._container.get(FlextOracleWmsClient)

    # IMPLEMENT: Only essential methods
    def extract_wms_entity(self, config: dict, entity_type: str) -> FlextResult[Iterator[dict]]:
        """Core extraction method - no unnecessary complexity."""
        pass

    def discover_wms_schema(self, config: dict, entity_type: str) -> FlextResult[dict]:
        """Schema discovery - leverage flext-oracle-wms capabilities."""
        pass
```

#### 2.2 Stream Implementation Optimization

```python
class WMSEntityStream(Stream):
    """Simple, focused WMS stream implementation."""

    def get_records(self, context: dict | None) -> Iterable[dict[str, object]]:
        """Extract WMS records - maintain simplicity."""
        service = self._container.get(FlextTapOracleWmsService)
        config = self.tap.config.model_dump()

        result = service.extract_wms_entity(config, self.name)

        if result.is_success:
            for record in result.value:
                yield self._process_wms_record(record)
        else:
            raise RuntimeError(f"WMS extraction failed: {result.error}")

    def _process_wms_record(self, record: dict) -> dict:
        """Simple record processing - avoid over-engineering."""
        # Basic data type conversions and Singer compliance
        return record
```

### Phase 3: Testing Excellence Implementation (90% COVERAGE TARGET)

#### 3.1 Comprehensive Test Suite Development

```python
# Unit tests for core functionality
@pytest.mark.unit
def test_wms_service_extract_entity():
    """Test WMS entity extraction with mocked WMS client."""
    # Test successful extraction
    # Test authentication failures
    # Test API errors
    # Test data transformation
    pass

@pytest.mark.unit
def test_wms_schema_discovery():
    """Test WMS schema discovery and Singer conversion."""
    # Test schema retrieval
    # Test WMS to Singer type mapping
    # Test error handling
    pass

@pytest.mark.integration
def test_wms_connectivity():
    """Test real WMS connectivity (when available)."""
    # Test authentication flow
    # Test entity extraction
    # Test pagination
    # Test error recovery
    pass

@pytest.mark.singer
def test_singer_protocol_compliance():
    """Test Singer protocol compliance."""
    # Test catalog discovery
    # Test data extraction format
    # Test incremental replication
    # Test schema validation
    pass
```

#### 3.2 Performance and Load Testing

```python
@pytest.mark.performance
def test_large_wms_extraction():
    """Test performance with large WMS datasets."""
    # Test memory usage with large datasets
    # Test pagination performance
    # Test timeout handling
    # Test concurrent stream processing
    pass

@pytest.mark.slow
def test_wms_api_limits():
    """Test WMS API limits and rate limiting."""
    # Test page size limits (max 1250)
    # Test request timeout limits (max 600s)
    # Test retry logic (max 10 retries)
    # Test rate limiting handling
    pass
```

### Phase 4: Production Readiness (DEPLOYMENT EXCELLENCE)

#### 4.1 Configuration and Security Validation

```python
@pytest.mark.security
def test_configuration_security():
    """Test configuration security and validation."""
    # Test password handling
    # Test environment variable loading
    # Test configuration validation
    # Test error message sanitization
    pass

@pytest.mark.integration
def test_meltano_integration():
    """Test Meltano orchestration integration."""
    # Test meltano.yml configuration
    # Test environment-specific configs
    # Test job and schedule definitions
    # Test metadata accuracy
    pass
```

---

## 🔧 ESSENTIAL COMMANDS (DAILY DEVELOPMENT)

### Quality Gates (MANDATORY BEFORE ANY COMMIT)

```bash
# NEVER SKIP: Complete validation pipeline (maintain achievements)
make validate                # lint + type + security + test (90% coverage target)

# Quick validation during development
make check                   # lint + type-check + test

# Individual quality components
make lint                    # Ruff linting (ALL rules enabled) - should pass
make type-check              # MyPy strict mode validation - should be 0 errors
make security                # Bandit + pip-audit security scanning
make format                  # Auto-format code with Ruff
make fix                     # Auto-fix code issues and format
```

### Singer Tap Operations

```bash
# Essential Singer protocol operations
make discover                # Generate catalog.json schema (test Singer compliance)
make run                     # Run data extraction (validate full pipeline)
make validate-config         # Validate tap configuration JSON

# WMS-specific testing
make wms-test                # Test Oracle WMS connectivity via flext-oracle-wms
make diagnose                # Run project diagnostics and health checks
make doctor                  # Comprehensive health check + diagnostics
```

### Testing Strategy (90% COVERAGE TARGET)

```bash
# Comprehensive testing approach
make test                    # All tests with 90% coverage requirement
make test-unit               # Unit tests only (exclude integration)
make test-integration        # Integration tests with Oracle WMS connectivity
make test-singer             # Singer protocol compliance tests
make coverage-html           # Generate HTML coverage report for analysis

# Performance and specific tests
pytest -m performance        # Performance tests with large datasets
pytest -m "not slow"         # Fast tests for quick feedback loop
pytest -m security           # Security and configuration validation tests
```

### WMS Development Environment

```bash
# Configuration setup
export TAP_ORACLE_WMS_BASE_URL="https://your-wms.oraclecloud.com"
export TAP_ORACLE_WMS_USERNAME="api_user"
export TAP_ORACLE_WMS_PASSWORD="secure_password"
export TAP_ORACLE_WMS_AUTH_METHOD="basic"
export TAP_ORACLE_WMS_COMPANY_CODE="COMPANY"
export TAP_ORACLE_WMS_FACILITY_CODE="FACILITY"

# Test configuration and extraction
poetry run tap-oracle-wms --config config.json --discover > catalog.json
poetry run tap-oracle-wms --config config.json --catalog catalog.json --state state.json
```

---

## 📊 SUCCESS METRICS (EVIDENCE-BASED MEASUREMENT)

### Architecture Simplification (MAINTAIN ACHIEVEMENTS)

```bash
# File count validation (TARGET: 11 files, not 26+)
find src/flext_tap_oracle_wms -name "*.py" | wc -l

# Line count validation (TARGET: ~2,121 lines, not 8,179+)
wc -l src/flext_tap_oracle_wms/*.py | tail -1 | awk '{print $1}'

# Type errors validation (TARGET: 0 errors)
mypy src/ --strict --show-error-codes 2>&1 | wc -l

# Linting compliance (TARGET: 0 errors)
ruff check src/ --statistics | grep -o "[0-9]\+ errors"
```

### Code Quality Metrics (AUTOMATED VALIDATION)

```bash
# Coverage measurement (TARGET: 90%)
pytest --cov=src --cov-report=term | grep "TOTAL" | awk '{print $4}'

# Security assessment (TARGET: 0 critical vulnerabilities)
bandit -r src/ -f json 2>/dev/null | jq '.metrics._totals.SEVERITY_RISK_HIGH' || echo 0

# Import validation (verify simplicity maintained)
python -c "from flext_tap_oracle_wms import FlextTapOracleWms; print('✅ Simple import works')"
```

### Singer Protocol Compliance (FUNCTIONAL VALIDATION)

```bash
# Catalog discovery success
make discover >/dev/null 2>&1 && echo "✅ Discovery OK" || echo "❌ Discovery FAILED"

# Data extraction success
make run >/dev/null 2>&1 && echo "✅ Extraction OK" || echo "❌ Extraction FAILED"

# Schema validation
singer-check-tap --catalog catalog.json < /dev/null && echo "✅ Schema OK" || echo "❌ Schema FAILED"
```

### WMS Integration Functionality (DOMAIN-SPECIFIC VALIDATION)

```bash
# WMS connectivity test
make wms-test >/dev/null 2>&1 && echo "✅ WMS OK" || echo "❌ WMS FAILED"

# flext-oracle-wms integration test
python -c "
from flext_oracle_wms import FlextOracleWmsClient
from flext_core import FlextContainer
client = FlextContainer.get_global().get(FlextOracleWmsClient)
print('✅ WMS client integration OK')
" && echo "WMS integration OK"

# Configuration validation test
python -c "
from flext_tap_oracle_wms.tap_config import TapOracleWmsConfig
config = TapOracleWmsConfig(base_url='test', username='test', password='test')
print('✅ Configuration validation OK')
" && echo "Configuration OK"
```

---

## 🔍 PROJECT-SPECIFIC CONTEXT (ORACLE WMS DOMAIN EXPERTISE)

### Oracle Warehouse Management System Integration Excellence

#### WMS Entity Types and Characteristics

```python
WMS_ENTITY_MODEL = {
    # Core Inventory Entities
    "item": {
        "description": "Item master data and specifications",
        "primary_key": "item_id",
        "replication_key": "date_time_stamp",
        "page_size_recommendation": 1000,
        "api_complexity": "medium"
    },
    "location": {
        "description": "Warehouse location definitions",
        "primary_key": "location_id",
        "replication_key": "date_time_stamp",
        "page_size_recommendation": 1250,  # Max allowed
        "api_complexity": "low"
    },
    "inventory": {
        "description": "Current inventory levels and status",
        "primary_key": ["item_id", "location_id"],
        "replication_key": "date_time_stamp",
        "page_size_recommendation": 500,  # Complex data
        "api_complexity": "high"
    },

    # Order Management Entities
    "order": {
        "description": "Warehouse orders and fulfillment",
        "primary_key": "order_id",
        "replication_key": "date_time_stamp",
        "page_size_recommendation": 750,
        "api_complexity": "high"
    },
    "shipment": {
        "description": "Shipment creation and tracking",
        "primary_key": "shipment_id",
        "replication_key": "date_time_stamp",
        "page_size_recommendation": 800,
        "api_complexity": "medium"
    },

    # Operational Entities
    "user": {
        "description": "WMS user accounts and permissions",
        "primary_key": "user_id",
        "replication_key": "date_time_stamp",
        "page_size_recommendation": 1250,  # Max allowed
        "api_complexity": "low"
    }
}
```

#### Oracle WMS API Performance Characteristics

```python
class OracleWmsApiLimits:
    """Oracle WMS API limits and optimization guidelines."""

    API_LIMITS = {
        "max_page_size": 1250,           # Hard limit from Oracle WMS
        "max_request_timeout": 600,      # 10 minutes maximum
        "max_retries": 10,               # Maximum retry attempts
        "max_concurrent_requests": 5,    # Safe concurrent requests
        "min_page_size": 1,              # Minimum page size
        "default_page_size": 1000        # Recommended default
    }

    PERFORMANCE_RECOMMENDATIONS = {
        "complex_entities": {           # inventory, order
            "page_size": 500,
            "timeout": 300,
            "concurrent_requests": 2
        },
        "medium_entities": {            # item, shipment
            "page_size": 1000,
            "timeout": 120,
            "concurrent_requests": 3
        },
        "simple_entities": {            # location, user
            "page_size": 1250,
            "timeout": 60,
            "concurrent_requests": 5
        }
    }

    ERROR_HANDLING_PATTERNS = {
        "timeout_errors": "exponential_backoff_retry",
        "rate_limit_errors": "linear_backoff_retry",
        "authentication_errors": "reauthenticate_and_retry",
        "server_errors": "circuit_breaker_pattern"
    }
```

#### Authentication and Security Patterns

```python
class OracleWmsAuthenticationManager:
    """Oracle WMS authentication patterns and security."""

    AUTHENTICATION_METHODS = {
        "basic": {
            "description": "Basic HTTP authentication",
            "required_fields": ["username", "password"],
            "security_level": "medium",
            "token_management": False
        },
        "oauth2": {
            "description": "OAuth2 client credentials flow",
            "required_fields": ["client_id", "client_secret", "token_url"],
            "security_level": "high",
            "token_management": True
        }
    }

    ORGANIZATIONAL_STRUCTURE = {
        "company_code": {
            "required": True,
            "description": "Top-level organizational identifier",
            "validation_pattern": r"^[A-Z0-9]{1,10}$"
        },
        "facility_code": {
            "required": True,
            "description": "Facility/warehouse identifier",
            "validation_pattern": r"^[A-Z0-9]{1,10}$"
        }
    }

    SECURITY_CONSIDERATIONS = {
        "password_handling": "never_log_or_expose",
        "token_caching": "memory_only_no_persistence",
        "error_messages": "sanitize_credential_information",
        "connection_security": "https_only_in_production"
    }
```

### flext-oracle-wms Integration Patterns

#### Infrastructure Service Integration

```python
# MANDATORY: Use flext-oracle-wms for all WMS operations (NEVER implement directly)
from flext_oracle_wms import (
    FlextOracleWmsClient,      # Primary WMS API client interface
    WmsAuthenticationManager,  # Authentication handling
    WmsEntityExtractor,        # Entity extraction utilities
    WmsSchemaAnalyzer,         # Schema discovery and analysis
    WmsErrorHandler           # Error handling and recovery
)

class FlextTapOracleWmsService(FlextDomainService):
    """Service leveraging flext-oracle-wms infrastructure."""

    def __init__(self, **data) -> None:
        super().__init__(**data)
        # Get WMS services from infrastructure layer
        self._wms_client = self._container.get(FlextOracleWmsClient)
        self._auth_manager = self._container.get(WmsAuthenticationManager)
        self._entity_extractor = self._container.get(WmsEntityExtractor)
        self._schema_analyzer = self._container.get(WmsSchemaAnalyzer)
```

### Configuration Excellence

#### Comprehensive Configuration Support

```python
class TapOracleWmsConfig(FlextModel):
    """Comprehensive WMS tap configuration with validation."""

    # Connection Configuration (required)
    base_url: str = Field(..., description="Oracle WMS instance URL")
    username: str = Field(..., description="WMS username")
    password: SecretStr = Field(..., description="WMS password")
    auth_method: str = Field(default="basic", pattern="^(basic|oauth2)$")

    # Organizational Configuration (required)
    company_code: str = Field(..., pattern=r"^[A-Z0-9]{1,10}$")
    facility_code: str = Field(..., pattern=r"^[A-Z0-9]{1,10}$")

    # Extraction Configuration
    entities: list[str] = Field(default_factory=list, description="WMS entities to extract")
    page_size: int = Field(default=1000, ge=1, le=1250, description="Records per page")
    start_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    # Filtering Configuration
    entity_filters: dict[str, dict] = Field(default_factory=dict)
    field_selection: dict[str, list[str]] = Field(default_factory=dict)

    # Performance Configuration
    request_timeout: int = Field(default=120, ge=30, le=600)
    max_retries: int = Field(default=3, ge=1, le=10)
    concurrent_requests: int = Field(default=3, ge=1, le=5)

    @model_validator(mode='after')
    def validate_entity_configuration(self) -> 'TapOracleWmsConfig':
        """Validate entity-specific configuration."""
        if self.entities:
            # Validate entity names against supported entities
            supported_entities = list(WMS_ENTITY_MODEL.keys())
            invalid_entities = [e for e in self.entities if e not in supported_entities]
            if invalid_entities:
                raise ValueError(f"Unsupported entities: {invalid_entities}")

        return self
```

### Singer Protocol Implementation Details

#### Stream Implementation Patterns

```python
class WMSInventoryStream(Stream):
    """WMS Inventory stream with optimized configuration."""

    name = "inventory"
    primary_keys = ["item_id", "location_id"]
    replication_key = "date_time_stamp"
    replication_method = "INCREMENTAL"

    def get_records(self, context: dict | None) -> Iterable[dict[str, object]]:
        """Extract inventory records with optimized pagination."""
        service = self._container.get(FlextTapOracleWmsService)
        config = self.tap.config.model_dump()

        # Use entity-specific page size for complex inventory data
        optimized_page_size = min(config.get("page_size", 1000), 500)

        result = service.extract_wms_entity(config, "inventory", optimized_page_size)

        if result.is_success:
            for record in result.value:
                # Process WMS-specific data types
                processed_record = self._process_inventory_record(record)
                yield processed_record
        else:
            raise RuntimeError(f"Inventory extraction failed: {result.error}")

    def _process_inventory_record(self, record: dict) -> dict:
        """Process inventory record for Singer compliance."""
        # Handle WMS-specific date formats
        if "date_time_stamp" in record:
            record["date_time_stamp"] = self._normalize_wms_timestamp(record["date_time_stamp"])

        # Handle WMS numeric formats
        numeric_fields = ["quantity_on_hand", "quantity_allocated", "quantity_available"]
        for field in numeric_fields:
            if field in record and record[field] is not None:
                record[field] = float(record[field])

        return record
```

---

## 🎯 QUALITY ACHIEVEMENT ROADMAP (PHASE-BY-PHASE SUCCESS)

### Week 1: Test Implementation & Coverage Achievement (MAINTAIN SIMPLICITY)

- [ ] **Architecture Validation**: Verify 11-file structure and 0 MyPy errors maintained
- [ ] **Unit Test Implementation**: Achieve 70% coverage with comprehensive unit tests
- [ ] **Integration Test Development**: WMS connectivity and authentication testing
- [ ] **Singer Protocol Tests**: Catalog discovery and data extraction validation

### Week 2: Service Enhancement & Integration Excellence (NO OVER-ENGINEERING)

- [ ] **Unified Service Implementation**: `FlextTapOracleWmsService` with essential functionality only
- [ ] **Stream Optimization**: Efficient WMS entity streams with proper error handling
- [ ] **Configuration Enhancement**: Comprehensive validation with WMS-specific business rules
- [ ] **FlextResult Integration**: Complete migration to FlextResult patterns

### Week 3: Performance & Security Excellence (WMS OPTIMIZATION)

- [ ] **Performance Testing**: Large dataset extraction with pagination optimization
- [ ] **Security Implementation**: Configuration security and credential handling
- [ ] **Error Recovery**: Comprehensive error handling for WMS API scenarios
- [ ] **Meltano Integration**: Complete orchestration platform integration

### Week 4: Production Readiness & Coverage Target (90% COVERAGE)

- [ ] **Coverage Achievement**: Reach and maintain 90% test coverage
- [ ] **Performance Validation**: Large-scale WMS environment testing
- [ ] **Security Scanning**: Complete Bandit and pip-audit compliance
- [ ] **Documentation Excellence**: Comprehensive configuration and usage documentation

### Success Validation (EVIDENCE-BASED CONFIRMATION)

```bash
# Final success confirmation (ALL must pass)
make validate                    # ✅ Zero errors (maintain achievements)
pytest --cov=src --cov-report=term | grep "90%"  # ✅ Coverage target
make discover && make run        # ✅ Singer compliance
make wms-test                    # ✅ WMS integration excellence
find src/flext_tap_oracle_wms -name "*.py" | wc -l  # ✅ Maintain 11 files (not 26+)
python -c "from flext_oracle_wms import FlextOracleWmsClient; print('✅ Infrastructure integration')"
```

---

**PROJECT AUTHORITY**: FLEXT-TAP-ORACLE-WMS  
**REFACTORING AUTHORITY**: Maintain simplified architecture achievements - NEVER return to over-engineering  
**QUALITY AUTHORITY**: Zero tolerance - 90% coverage, zero type errors, full Singer compliance  
**ARCHITECTURE AUTHORITY**: Maintain 11-file simplicity while leveraging flext-oracle-wms infrastructure efficiently
