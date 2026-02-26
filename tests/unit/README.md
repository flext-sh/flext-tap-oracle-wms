# Unit Tests

<!-- TOC START -->

- [Overview](#overview)
- [Test Structure](#test-structure)
  - [**Working Unit Tests**](#working-unit-tests)
  - [**Basic Component Tests**](#basic-component-tests)
- [Test Execution](#test-execution)
  - [**Running Unit Tests**](#running-unit-tests)
  - [**Test Markers**](#test-markers)
- [Test Patterns](#test-patterns)
  - [**Mock Usage Pattern**](#mock-usage-pattern)
  - [**Configuration Testing Pattern**](#configuration-testing-pattern)
  - [**Error Testing Pattern**](#error-testing-pattern)
- [Test Coverage](#test-coverage)
  - [**Current Coverage Status**](#current-coverage-status)
  - [**Coverage Requirements**](#coverage-requirements)
  - [**Coverage Reporting**](#coverage-reporting)
- [Test Quality Standards](#test-quality-standards)
  - [**Test Naming Conventions**](#test-naming-conventions)
  - [**Test Documentation**](#test-documentation)
  - [**Isolation Requirements**](#isolation-requirements)
- [Common Test Utilities](#common-test-utilities)
  - [**Mock Fixtures**](#mock-fixtures)
  - [**Assertion Helpers**](#assertion-helpers)
- [Troubleshooting Tests](#troubleshooting-tests)
  - [**Common Issues**](#common-issues)
  - [**Debugging Tests**](#debugging-tests)
- [Contributing to Unit Tests](#contributing-to-unit-tests)
  - [**Adding New Tests**](#adding-new-tests)
  - [**Test Review Checklist**](#test-review-checklist)

<!-- TOC END -->

## Overview

This directory contains unit tests for FLEXT Tap Oracle WMS components. Unit tests focus on testing individual components in isolation using mocking to eliminate external dependencies.

## Test Structure

### **Working Unit Tests**

#### **Authentication Tests**

- **[test_auth_comprehensive.py](test_auth_comprehensive.py)** - Authentication system testing
  - Basic authentication flow
  - WMS authenticator functionality
  - Header generation and application
  - Error handling for invalid credentials

#### **Client Tests**

- **[test_client_comprehensive.py](test_client_comprehensive.py)** - WMS client wrapper testing
  - HTTP client configuration
  - Request/response handling
  - Authentication integration
  - Error recovery mechanisms

#### **Configuration Tests**

- **[test_config_mapper_comprehensive.py](test_config_mapper_comprehensive.py)** - Configuration mapping

  - Configuration transformation
  - Default value application
  - Validation rule mapping
  - Type conversion handling

- **[test_config.py](test_config.py)** - Basic configuration validation

  - Configuration model testing
  - Required field validation
  - Type checking and constraints

#### **Discovery Tests**

- **[test_entity_discovery_comprehensive.py](test_entity_discovery_comprehensive.py)** - Entity discovery logic
  - WMS entity discovery
  - Metadata extraction
  - Schema generation
  - Error handling for discovery failures

#### **Validation Tests**

- **[test_critical_validation_comprehensive.py](test_critical_validation_comprehensive.py)** - Environment validation
  - Critical environment variable checking
  - Configuration completeness validation
  - Business rule enforcement
  - Error reporting and recovery

#### **Utility Tests**

- **[test_type_mapping_comprehensive.py](test_type_mapping_comprehensive.py)** - Type mapping utilities
  - WMS to Singer type conversion
  - Data type validation
  - Schema compatibility checking

#### **Cache Tests**

- **[test_cache_manager_comprehensive.py](test_cache_manager_comprehensive.py)** - Cache functionality
  - Response caching mechanisms
  - Cache expiration handling
  - Memory management
  - Performance optimization validation

### **Basic Component Tests**

#### **Core Interface Tests**

- **[test_cli.py](test_cli.py)** - Command-line interface testing
- **[test_client.py](test_client.py)** - Basic client functionality
- **[test_main.py](test_main.py)** - Main module entry point
- **[test_models.py](test_models.py)** - Data model validation
- **[test_simple_api.py](test_simple_api.py)** - Simplified API interface
- **[test_schema_flattener.py](test_schema_flattener.py)** - Schema flattening utilities

#### **Stream Tests**

- **[test_streams.py](test_streams.py)** - Stream implementation testing
- **[test_tap.py](test_tap.py)** - Basic tap functionality

## Test Execution

### **Running Unit Tests**

```bash
# Run all unit tests
make test-unit

# Run with verbose output
pytest tests/unit/ -v

# Run specific test files
pytest tests/unit/test_auth_comprehensive.py -v
pytest tests/unit/test_client_comprehensive.py -v
pytest tests/unit/test_config_mapper_comprehensive.py -v

# Run tests with coverage
pytest tests/unit/ --cov=src/flext_tap_oracle_wms --cov-report=html
```

### **Test Markers**

```bash
# Run only unit tests (excludes integration/e2e)
pytest -m unit

# Run fast tests (exclude slow operations)
pytest -m "not slow"

# Run specific component tests
pytest -k "auth" tests/unit/
pytest -k "config" tests/unit/
pytest -k "discovery" tests/unit/
```

## Test Patterns

### **Mock Usage Pattern**

```python
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_wms_client():
    """Standard mock for WMS client dependencies."""
    client = Mock()
    client.get_entities.return_value = ["item", "inventory"]
    client.get_metadata.return_value = {"fields": ["id", "name"]}
    return client

def test_component_with_mock(mock_wms_client):
    """Test component behavior with mocked dependencies."""
    component = ComponentUnderTest(mock_wms_client)
    result = component.perform_operation()

    assert result.success
    mock_wms_client.get_entities.assert_called_once()
```

### **Configuration Testing Pattern**

```python
@pytest.fixture
def valid_config():
    """Standard valid configuration for testing."""
    return {
        "base_url": "https://test-wms.example.com",
        "auth_method": "basic",
        "username": "test_user",
        "password": "test_pass",
        "company_code": "TEST",
        "facility_code": "TEST01"
    }

def test_config_validation_success(valid_config):
    """Test successful configuration validation."""
    validator = ConfigValidator()
    result = validator.validate(valid_config)
    assert result.is_valid
```

### **Error Testing Pattern**

```python
def test_component_handles_network_error():
    """Test component error handling for network failures."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.ConnectionError("Network error")

        component = ComponentUnderTest()
        result = component.fetch_data()

        assert not result.success
        assert "Network error" in result.error_message
```

## Test Coverage

### **Current Coverage Status**

- **Authentication**: ~95% coverage
- **Configuration**: ~90% coverage
- **Client**: ~85% coverage
- **Discovery**: ~80% coverage
- **Validation**: ~95% coverage
- **Utilities**: ~85% coverage

### **Coverage Requirements**

- **Minimum**: 90% line coverage for all components
- **Target**: 95% line coverage with branch coverage
- **Quality**: Meaningful tests, not just coverage metrics

### **Coverage Reporting**

```bash
# Generate HTML coverage report
make test
open reports/coverage/index.html

# Generate terminal coverage report
pytest tests/unit/ --cov --cov-report=term-missing
```

> Coverage thresholds are configured in `pyproject.toml` under `[tool.coverage.report]`.

## Test Quality Standards

### **Test Naming Conventions**

```python
def test_[component]_[scenario]_[expected_outcome]():
    """Test [component] [scenario] returns/raises [expected outcome]."""
    pass

# Examples
def test_auth_with_valid_credentials_returns_success():
    """Test authentication with valid credentials returns success result."""
    pass

def test_config_validation_with_missing_url_raises_error():
    """Test configuration validation with missing URL raises validation error."""
    pass
```

### **Test Documentation**

```python
def test_complex_scenario():
    """
    Test complex business scenario with multiple interactions.

    This test verifies that when component A interacts with component B
    under specific conditions, the expected business outcome occurs.

    Given:
        - Valid configuration with specific settings
        - Mocked WMS client with predefined responses

    When:
        - Component performs multi-step operation

    Then:
        - All interactions occur in correct order
        - Final result matches business expectations
        - No side effects occur
    """
    # Test implementation
```

### **Isolation Requirements**

- **No External Dependencies**: All tests use mocks for external services
- **No Network Calls**: HTTP requests mocked or stubbed
- **No File System**: File operations mocked when necessary
- **No Environment Dependencies**: Environment variables mocked
- **Fast Execution**: Each test completes in milliseconds

## Common Test Utilities

### **Mock Fixtures**

```python
# tests/unit/conftest.py
@pytest.fixture
def mock_flext_wms_client():
    """Mock FlextOracleWmsClient for testing."""
    with patch('flext_tap_oracle_wms.client.FlextOracleWmsClient') as mock:
        client = Mock()
        mock.return_value = client

        # Standard responses
        client.authenticate.return_value = True
        client.get_entities.return_value = ["item", "inventory", "order"]
        client.get_data.return_value = iter([{"id": "1", "name": "test"}])

        yield client

@pytest.fixture
def sample_wms_response():
    """Sample WMS API response for testing."""
    return {
        "items": [
            {"item_id": "ITEM001", "description": "Test Item"},
            {"item_id": "ITEM002", "description": "Another Item"}
        ],
        "pagination": {
            "page": 1,
            "total_pages": 5,
            "next_url": "https://wms.example.com/api/items?page=2"
        }
    }
```

### **Assertion Helpers**

```python
def assert_flext_result_success(result):
    """Assert FlextResult indicates success."""
    assert result.success, f"Expected success, got error: {result.error_message}"
    assert result.data is not None, "Expected result data"

def assert_flext_result_error(result, expected_error_type=None):
    """Assert FlextResult indicates error with optional type check."""
    assert not result.success, "Expected error result"
    assert result.error_message, "Expected error message"
    if expected_error_type:
        assert expected_error_type in result.error_message
```

## Troubleshooting Tests

### **Common Issues**

1. **Import Errors**

   ```bash
   # Fix Python path issues
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   pytest tests/unit/
   ```

1. **Mock Configuration**

   ```bash
   # Debug mock setup
   pytest tests/unit/test_specific.py -v -s --tb=short
   ```

1. **Coverage Issues**

   ```bash
   # Clean coverage data
   rm -rf .coverage htmlcov/
   pytest tests/unit/ --cov=src/flext_tap_oracle_wms
   ```

### **Debugging Tests**

```python
import pytest

def test_debug_example():
    """Example test with debugging techniques."""
    # Use pytest.set_trace() for debugging
    pytest.set_trace()

    # Print debug information
    print(f"Debug info: {variable}")

    # Use assert with custom messages
    assert condition, f"Failed because: {explanation}"
```

## Contributing to Unit Tests

### **Adding New Tests**

1. **Identify Component**: Determine which component needs testing
1. **Create Test File**: Follow naming convention `test_[component].py`
1. **Write Isolated Tests**: Use mocks to eliminate dependencies
1. **Follow Patterns**: Use established test patterns and fixtures
1. **Document Purpose**: Clear docstrings explaining test intent

### **Test Review Checklist**

- [ ] Test is properly isolated with mocks
- [ ] Test name clearly describes scenario and expectation
- [ ] Test has comprehensive docstring
- [ ] Test covers both success and failure paths
- [ ] Test follows project patterns and conventions
- [ ] Test executes quickly (< 100ms per test)
- [ ] Test is deterministic and reliable

______________________________________________________________________

**Status**: Core unit tests working with good coverage · 1.0.0 Release Preparation | **Priority**: Maintain isolation and coverage | **Updated**: 2025-08-13
