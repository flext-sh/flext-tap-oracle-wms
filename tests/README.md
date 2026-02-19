# Test Documentation


<!-- TOC START -->
- [Overview](#overview)
- [Current Test Status](#current-test-status)
  - [Test Coverage Analysis](#test-coverage-analysis)
- [Test Structure](#test-structure)
- [Disabled Tests Analysis](#disabled-tests-analysis)
  - [Critical Disabled Files](#critical-disabled-files)
- [Test Execution Guide](#test-execution-guide)
  - [Working Tests (Current)](#working-tests-current)
  - [Test Markers](#test-markers)
  - [Environment Variables](#environment-variables)
- [Testing Strategy](#testing-strategy)
  - [Unit Testing Strategy](#unit-testing-strategy)
  - [Integration Testing Strategy (Planned)](#integration-testing-strategy-planned)
  - [E2E Testing Strategy (Future)](#e2e-testing-strategy-future)
- [Test Data Management](#test-data-management)
  - [Current Test Data](#current-test-data)
  - [Required Test Data Structure](#required-test-data-structure)
- [Mocking Strategy](#mocking-strategy)
  - [WMS Client Mocking](#wms-client-mocking)
  - [Configuration Mocking](#configuration-mocking)
- [Test Re-enabling Plan](#test-re-enabling-plan)
  - [Phase 1: Infrastructure (Week 1)](#phase-1-infrastructure-week-1)
  - [Phase 2: Core Tests (Week 2)](#phase-2-core-tests-week-2)
  - [Phase 3: Integration Tests (Week 3)](#phase-3-integration-tests-week-3)
  - [Phase 4: E2E Tests (Week 4)](#phase-4-e2e-tests-week-4)
- [Quality Standards](#quality-standards)
  - [Test Quality Requirements](#test-quality-requirements)
  - [Test Naming Conventions](#test-naming-conventions)
- [Troubleshooting Test Issues](#troubleshooting-test-issues)
  - [Common Test Problems](#common-test-problems)
- [Contributing to Tests](#contributing-to-tests)
  - [Adding New Tests](#adding-new-tests)
  - [Test Review Checklist](#test-review-checklist)
<!-- TOC END -->

## Overview

This directory contains the test suite for FLEXT Tap Oracle WMS. The testing strategy covers unit, integration, and end-to-end testing with a focus on Singer protocol compliance and FLEXT ecosystem integration.

## Current Test Status

**⚠️ CRITICAL ISSUE**: 27% of the test suite is currently disabled due to external dependencies

### Test Coverage Analysis

| Test Type             | Status                | Coverage | Issues                             |
| --------------------- | --------------------- | -------- | ---------------------------------- |
| **Unit Tests**        | ✅ Working            | ~70%\*   | Some comprehensive tests available |
| **Integration Tests** | ⚠️ Partially Disabled | ~40%\*   | External WMS dependencies          |
| **E2E Tests**         | ❌ Disabled           | 0%       | Requires live WMS instance         |

\*Coverage percentages are estimates based on enabled tests only

## Test Structure

```
tests/
├── unit/                           # Unit tests (mostly working)
│   ├── test_auth_comprehensive.py      # Authentication testing
│   ├── test_cache_manager_comprehensive.py  # Cache functionality
│   ├── test_client_comprehensive.py    # WMS client wrapper testing
│   ├── test_config_mapper_comprehensive.py  # Configuration mapping
│   ├── test_critical_validation_comprehensive.py  # Environment validation
│   ├── test_entity_discovery_comprehensive.py  # Entity discovery logic
│   ├── test_type_mapping_comprehensive.py
│   └── [other unit tests]
├── integration/                    # Integration tests (some disabled)
│   └── test_simple_integration.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup
├── e2e/                           # End-to-end tests (disabled)
│   └── test_wms_e2e.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup
├── data/                          # Test data and fixtures
│   └── sample_wms_data.json
├── conftest.py                    # Pytest configuration (basic)
└── [disabled test files]         # 7 files with .backup extension
```

## Disabled Tests Analysis

### Critical Disabled Files

The following test files are disabled due to external WMS dependencies:

1. **conftest.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup**
   - **Reason**: Contains live WMS connection fixtures
   - **Impact**: Test configuration unavailable for integration tests
   - **Remediation**: Create mock-based fixtures

2. **test_wms_e2e.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup**
   - **Reason**: Requires live Oracle WMS instance
   - **Impact**: No end-to-end workflow validation
   - **Remediation**: Implement comprehensive mocking strategy

3. **test_simple_integration.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup**
   - **Reason**: Integration tests with external API calls
   - **Impact**: Multi-component integration not validated
   - **Remediation**: Mock WMS API responses

4. **test_tap.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup**
   - **Reason**: Tap-level testing with live connections
   - **Impact**: Core tap functionality not validated
   - **Remediation**: Mock WMS client for tap testing

5. **test_config_validation.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup**
   - **Reason**: Configuration validation with live API checks
   - **Impact**: Configuration edge cases not tested
   - **Remediation**: Separate validation logic from API calls

6. **test_discovery.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup**
   - **Reason**: Entity discovery with live WMS metadata
   - **Impact**: Schema discovery not validated
   - **Remediation**: Mock WMS metadata responses

## Test Execution Guide

### Working Tests (Current)

```bash
# Run all working unit tests
make test-unit

# Run specific unit test modules
pytest tests/unit/test_auth_comprehensive.py -v
pytest tests/unit/test_client_comprehensive.py -v
pytest tests/unit/test_config_mapper_comprehensive.py -v

# Run tests with coverage
make test  # Includes coverage reporting

# Quick test execution (no coverage)
make test-fast
```

### Test Markers

```bash
# Run tests by marker (when enabled)
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests (currently disabled)
pytest -m "not slow"              # Exclude slow tests
pytest -m singer                  # Singer protocol tests
```

### Environment Variables

```bash
# Test configuration
TEST_WMS_BASE_URL=https://mock-wms.example.com
TEST_WMS_USERNAME=test_user
TEST_WMS_PASSWORD=test_password
TEST_COMPANY_CODE=TEST
TEST_FACILITY_CODE=TEST01
```

## Testing Strategy

### Unit Testing Strategy

**Objective**: Test individual components in isolation
**Approach**: Mock all external dependencies
**Coverage Target**: 95% for enabled tests

**Example Pattern**:

```python
@pytest.fixture
def mock_wms_client():
    """Mock WMS client for isolated testing."""
    client = Mock(spec=FlextOracleWmsClient)
    client.get_available_entities.return_value = ["item", "inventory"]
    return client

def test_entity_discovery(mock_wms_client):
    """Test entity discovery with mocked client."""
    discovery = EntityDiscovery(mock_wms_client)
    result = discovery.discover_entities()
    assert result.success
    assert "item" in result.data
```

### Integration Testing Strategy (Planned)

**Objective**: Test component interaction with mocked external services
**Approach**: Mock WMS API responses, test internal integration
**Coverage Target**: 90% of integration scenarios

**Required Implementation**:

- Mock WMS API server for consistent responses
- Test data fixtures for various WMS configurations
- Error scenario testing (network failures, authentication issues)

### E2E Testing Strategy (Future)

**Objective**: Test complete workflows with controlled environment
**Approach**: Dedicated test WMS instance or comprehensive mocking
**Coverage Target**: Core user workflows

## Test Data Management

### Current Test Data

- `tests/data/sample_wms_data.json` - Basic WMS entity samples
- Inline test data in individual test files
- Mock responses embedded in test code

### Required Test Data Structure

```
tests/
├── fixtures/
│   ├── wms_responses/
│   │   ├── entities_list.json           # Available entities response
│   │   ├── item_metadata.json           # Item entity metadata
│   │   ├── inventory_data.json          # Sample inventory records
│   │   └── error_responses.json         # Various error scenarios
│   ├── configurations/
│   │   ├── valid_basic.json             # Basic valid configuration
│   │   ├── valid_oauth.json             # OAuth configuration
│   │   ├── invalid_configs.json         # Invalid configuration examples
│   │   └── edge_cases.json              # Edge case configurations
│   └── schemas/
│       ├── item_schema.json             # Expected item schema
│       ├── inventory_schema.json        # Expected inventory schema
│       └── catalog_sample.json          # Complete catalog example
```

## Mocking Strategy

### WMS Client Mocking

```python
# Standard mock pattern for WMS client
@pytest.fixture
def mock_flext_wms_client():
    """Standard mock for FlextOracleWmsClient."""
    with patch('flext_tap_oracle_wms.tap.FlextOracleWmsClient') as mock:
        client_instance = Mock()
        mock.return_value = client_instance

        # Configure standard responses
        client_instance.get_available_entities.return_value = ["item", "inventory"]
        client_instance.get_entity_metadata.return_value = Mock()
        client_instance.get_entity_data.return_value = iter([{"id": "1", "name": "test"}])

        yield client_instance
```

### Configuration Mocking

```python
# Standard configuration for testing
@pytest.fixture
def valid_tap_config():
    """Standard valid configuration for testing."""
    return {
        "base_url": "https://test-wms.example.com",
        "auth_method": "basic",
        "username": "test_user",
        "password": "test_pass",
        "company_code": "TEST",
        "facility_code": "TEST01",
        "entities": ["item", "inventory"]
    }
```

## Test Re-enabling Plan

### Phase 1: Infrastructure (Week 1)

- [ ] Create comprehensive mock infrastructure
- [ ] Set up test fixtures and data management
- [ ] Implement mock WMS API responses

### Phase 2: Core Tests (Week 2)

- [ ] Re-enable `conftest.py` with mock-based fixtures
- [ ] Re-enable `test_tap.py` with mocked dependencies
- [ ] Re-enable `test_config_validation.py` with separated validation logic

### Phase 3: Integration Tests (Week 3)

- [ ] Re-enable `test_simple_integration.py` with mocked integration
- [ ] Re-enable `test_discovery.py` with mock metadata
- [ ] Implement comprehensive integration test scenarios

### Phase 4: E2E Tests (Week 4)

- [ ] Design E2E test strategy (mock vs test instance)
- [ ] Re-enable `test_wms_e2e.py` with appropriate mocking
- [ ] Implement complete workflow validation

## Quality Standards

### Test Quality Requirements

- **Coverage**: 95% minimum for unit tests, 90% for integration tests
- **Documentation**: All test functions have clear docstrings
- **Isolation**: Unit tests are completely isolated with mocks
- **Reliability**: Tests pass consistently without external dependencies
- **Performance**: Test suite completes in under 2 minutes

### Test Naming Conventions

```python
# Test function naming pattern
def test_[component]_[scenario]_[expected_outcome]():
    """Test [component] [scenario] returns [expected outcome]."""
    pass

# Examples
def test_entity_discovery_with_valid_client_returns_entities():
    """Test entity discovery with valid client returns entity list."""
    pass

def test_config_validation_with_missing_auth_raises_error():
    """Test configuration validation with missing auth raises validation error."""
    pass
```

## Troubleshooting Test Issues

### Common Test Problems

1. **Import Errors**

   ```bash
   # Fix: Ensure proper Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   pytest tests/
   ```

2. **Mock Configuration Issues**

   ```bash
   # Fix: Check mock setup in conftest.py
   pytest tests/unit/test_specific.py -v -s
   ```

3. **Coverage Calculation Issues**

   ```bash
   # Fix: Clean coverage data
   make clean
   make test
   ```

## Contributing to Tests

### Adding New Tests

1. **Choose appropriate test level** (unit/integration/e2e)
2. **Follow naming conventions** for consistency
3. **Use standard mock fixtures** when available
4. **Document test purpose** with clear docstrings
5. **Ensure test isolation** and reliability

### Test Review Checklist

- [ ] Test is properly isolated with mocks
- [ ] Test has clear, descriptive name
- [ ] Test has comprehensive docstring
- [ ] Test covers both success and failure scenarios
- [ ] Test follows project testing patterns
- [ ] Test passes consistently

---

**Status**: Test infrastructure requires significant improvement · 1.0.0 Release Preparation
**Priority**: Re-enable disabled tests before production use  
**Updated**: 2025-08-13
