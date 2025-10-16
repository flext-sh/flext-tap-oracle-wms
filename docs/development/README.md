# Development Documentation

## Overview

This directory contains comprehensive development documentation for FLEXT Tap Oracle WMS, including testing strategies, quality standards, and development workflows.

## Development Documentation Structure

### Testing Documentation

- **[testing-strategy.md](testing-strategy.md)** - Comprehensive testing approach and disabled tests analysis
- **[test-architecture.md](test-architecture.md)** - Test organization and structure
- **[mocking-strategy.md](mocking-strategy.md)** - Mock implementation for external dependencies

### Quality Standards

- **[quality-gates.md](quality-gates.md)** - Quality validation requirements and standards
- **[code-standards.md](code-standards.md)** - Code quality and style guidelines
- **[security-standards.md](security-standards.md)** - Security requirements and validation

### Development Workflows

- **[development-workflow.md](development-workflow.md)** - Complete development process
- **[singer-compliance.md](singer-compliance.md)** - Singer SDK specification compliance
- **[debugging-guide.md](debugging-guide.md)** - Debugging and troubleshooting guide

### Refactoring Documentation

- **[refactoring-guidelines.md](refactoring-guidelines.md)** - Guidelines for the major refactoring
- **[migration-strategy.md](migration-strategy.md)** - Migration from current to target architecture
- **[validation-checklist.md](validation-checklist.md)** - Validation steps for refactored code

## Current Development Status

### Critical Issues

| Issue                 | Impact                  | Status   | Action Required             |
| --------------------- | ----------------------- | -------- | --------------------------- |
| **Disabled Tests**    | 27% test coverage loss  | Critical | Re-enable with proper mocks |
| **Over-Engineering**  | High maintenance burden | Critical | Simplify architecture       |
| **Config Chaos**      | Development confusion   | High     | Consolidate configuration   |
| **FLEXT Integration** | Ecosystem inconsistency | Medium   | Standardize patterns        |

### Quality Metrics

| Metric              | Current              | Target  | Status                  |
| ------------------- | -------------------- | ------- | ----------------------- |
| **Test Coverage**   | ~70% (with disabled) | 100%    | ❌ Requires work        |
| **Code Complexity** | Very High            | Low     | ❌ Requires refactoring |
| **Type Coverage**   | ~85%                 | 100%    | ⚠️ Needs improvement    |
| **Security Scan**   | Clean                | Clean   | ✅ Passing              |
| **Lint Score**      | Passing              | Passing | ✅ Passing              |

## Development Environment Setup

### Prerequisites

```bash
# System requirements
Python 3.13+
Poetry 1.8+
Make 4.0+
Git 2.30+

# FLEXT ecosystem dependencies
flext-core (local development)
flext-oracle-wms (local development)
flext-meltano (local development)
flext-observability (local development)
```

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/flext-sh/flext-tap-oracle-wms
cd flext-tap-oracle-wms
make setup

# Verify installation
make diagnose
make doctor
```

### Development Dependencies

```bash
# Install development dependencies
make install-dev

# Verify quality tools
make validate    # Should pass all quality gates
```

## Development Workflow

### 1. Feature Development

```bash
# Start new feature
git checkout -b feature/your-feature-name

# Development cycle
make test-unit           # Run unit tests
make lint               # Check code quality
make type-check         # Verify type safety
make format             # Format code

# Complete validation
make validate           # All quality gates
```

### 2. Testing Strategy

```bash
# Test categories
make test-unit          # Unit tests (working)
make test-integration   # Integration tests (some disabled)
pytest -m "not slow"    # Fast tests only

# Specific test execution
pytest tests/unit/test_specific.py -v
pytest -k "test_pattern" --tb=short
```

### 3. Quality Assurance

```bash
# Pre-commit validation
make validate           # Complete validation pipeline
make security          # Security scanning
make deps-audit        # Dependency vulnerability check

# Code quality
make lint
make type-check
make format            # Auto-format with Ruff
```

## Testing Architecture

### Current Test Issues

#### Disabled Tests Analysis

```bash
# Count disabled tests
find tests/ -name "*.backup" | wc -l  # Result: 7 files

# Disabled test files
tests/conftest.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup
tests/e2e/test_wms_e2e.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup
tests/integration/test_simple_integration.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup
tests/test_tap.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup
tests/unit/test_config_validation.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup
tests/unit/test_discovery.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup
```

**Impact**: 27% of test suite disabled, critical functionality untested

#### Working Test Structure

```
tests/
├── unit/                           # Unit tests (mostly working)
│   ├── test_auth_comprehensive.py
│   ├── test_cache_manager_comprehensive.py
│   ├── test_client_comprehensive.py
│   ├── test_config_mapper_comprehensive.py
│   ├── test_critical_validation_comprehensive.py
│   ├── test_entity_discovery_comprehensive.py
│   └── test_type_mapping_comprehensive.py
├── test_streams.py                 # Stream testing (working)
├── test_tap_initialization.py     # Tap initialization (working)
└── data/                          # Test data and fixtures
    └── sample_wms_data.json
```

### Target Test Architecture

```
tests/
├── unit/                          # Unit tests (100% coverage)
│   ├── test_tap.py               # Main tap functionality
│   ├── test_streams.py           # Stream implementation
│   ├── test_config.py            # Configuration validation
│   ├── test_discovery.py         # Entity discovery
│   ├── test_auth.py              # Authentication
│   └── test_schema.py            # Schema generation
├── integration/                   # Integration tests (with mocks)
│   ├── test_wms_integration.py   # WMS API integration
│   ├── test_singer_compliance.py # Singer protocol
│   └── test_flext_integration.py # FLEXT ecosystem
├── e2e/                          # End-to-end tests (optional)
│   └── test_full_extraction.py   # Complete extraction workflow
├── fixtures/                     # Test data and mocks
│   ├── wms_responses.json        # Mock WMS API responses
│   ├── config_samples.json       # Configuration examples
│   └── schema_samples.json       # Schema definitions
└── conftest.py                   # Pytest configuration
```

## Code Quality Standards

### FLEXT Standards Compliance

```python
# Example of FLEXT-compliant code
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities
from flext_oracle_wms import FlextOracleWmsClient
from pydantic import Field, validator

class WMSConfig(FlextConfig):
    """FLEXT-compliant configuration."""

    base_url: str = Field(..., description="WMS instance URL")
    auth_method: str = Field(..., regex="^(basic|oauth2)$")

    class Config:
        env_prefix = "TAP_ORACLE_WMS_"

    @validator("entities")
    def validate_entities(cls, v):
        # Business logic validation
        return v

class FlextMeltanoTapOracleWMS:
    """FLEXT-compliant tap implementation."""

    def __init__(self, config: dict):
        self.config = WMSConfig(**config)
        self.logger = FlextLogger(__name__)

    def discover_streams(self) -> FlextResult[List[Stream]]:
        """Use FlextResult pattern for error handling."""
        try:
            streams = self._build_streams()
            return FlextResult.success(streams)
        except Exception as e:
            self.logger.error(f"Discovery failed: {e}")
            return FlextResult.failure(str(e))
```

### Type Safety Requirements

```python
# Strict type annotations required
from typing import List, Dict, Optional, Iterator

from flext_core import TAnyDict

def extract_records(
    entity: str,
    config: TAnyDict,
    filters: Optional[FlextTypes.Dict] = None
) -> Iterator[TAnyDict]:
    """Fully typed function signature."""
    # Implementation with type safety
    pass
```

### Error Handling Standards

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

class WMSTapError(FlextExceptions.Error):
    """Base error for WMS tap."""
    pass

class WMSConfigurationError(WMSTapError):
    """Configuration validation errors."""
    pass

# Usage with proper error context
try:
    result = perform_operation()
except WMSConfigurationError as e:
    logger.error(f"Configuration error: {e}", exc_info=True)
    raise
```

## Development Tools

### IDE Configuration

**VS Code Settings** (recommended):

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll": true
    }
  }
}
```

### Git Hooks

```bash
# Pre-commit hooks (automatically installed with make setup)
pre-commit install

# Manual hook execution
pre-commit run --all-files
```

### Debugging Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Tap Discovery",
      "type": "python",
      "request": "launch",
      "module": "flext_tap_oracle_wms.tap",
      "args": ["--config", "config.json", "--discover"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Debug Tap Extraction",
      "type": "python",
      "request": "launch",
      "module": "flext_tap_oracle_wms.tap",
      "args": ["--config", "config.json", "--catalog", "catalog.json"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

## Common Development Tasks

### Adding New WMS Entity

1. **Update Configuration**:

```python
# Add entity to valid entities list
VALID_ENTITIES = [
    "item", "location", "inventory", "order",
    "shipment", "receipt", "pick", "new_entity"  # Add here
]
```

2. **Create Entity Tests**:

```python
def test_new_entity_extraction(mock_wms_client):
    """Test new entity extraction."""
    # Implementation
    pass
```

3. **Update Documentation**:

- Add entity to README.md entity table
- Update configuration examples
- Add entity to schema documentation

### Debugging Common Issues

#### Authentication Issues

```bash
# Test WMS connection
make wms-test

# Debug authentication
TAP_ORACLE_WMS_LOG_LEVEL=DEBUG python -m flext_tap_oracle_wms.tap --config config.json --discover
```

#### Schema Issues

```bash
# Validate schema generation
python -c "
from flext_tap_oracle_wms.discovery import EntityDiscovery
discovery = EntityDiscovery()
schema = discovery.get_entity_schema('item')
print(schema)
"
```

#### Performance Issues

```bash
# Profile extraction
python -m cProfile -o profile.stats -m flext_tap_oracle_wms.tap --config config.json --catalog catalog.json

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

## Contributing Guidelines

### Code Review Checklist

- [ ] **Functionality**: Code works as intended
- [ ] **Tests**: Comprehensive test coverage (unit + integration)
- [ ] **Types**: Full type annotations with MyPy validation
- [ ] **Documentation**: Code is well documented
- [ ] **FLEXT Patterns**: Uses ecosystem patterns consistently
- [ ] **Performance**: No performance regressions
- [ ] **Security**: No security vulnerabilities
- [ ] **Error Handling**: Proper error handling and logging

### Pull Request Process

1. **Create Feature Branch**: `git checkout -b feature/description`
2. **Implement Changes**: Follow development workflow
3. **Validate Quality**: `make validate` must pass
4. **Write Tests**: Maintain 100% coverage target
5. **Update Documentation**: Keep docs current
6. **Create PR**: Include detailed description and testing notes

## Migration Considerations

### Current → Target Architecture

1. **Preparation Phase**:
   - Document all current functionality
   - Create comprehensive test suite
   - Set up FLEXT integration foundation

2. **Implementation Phase**:
   - Implement simplified architecture
   - Migrate functionality incrementally
   - Validate each component thoroughly

3. **Validation Phase**:
   - Compare outputs between old and new
   - Performance benchmarking
   - Integration testing

4. **Deployment Phase**:
   - Switch to new implementation
   - Monitor production performance
   - Address any issues quickly

---

**Updated**: 2025-08-13 | **Status**: Development Guide Complete · 1.0.0 Release Preparation | **Next**: Implementation Execution
