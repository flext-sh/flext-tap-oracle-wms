# Integration Tests


<!-- TOC START -->
- [Overview](#overview)
- [Current Status](#current-status)
- [Test Structure](#test-structure)
  - [**Disabled Integration Tests**](#disabled-integration-tests)
- [Integration Test Strategy](#integration-test-strategy)
  - [**Component Integration Patterns**](#component-integration-patterns)
  - [**Configuration Integration Testing**](#configuration-integration-testing)
  - [**Data Flow Integration Testing**](#data-flow-integration-testing)
- [Mock Infrastructure Requirements](#mock-infrastructure-requirements)
  - [**Mock WMS API Server**](#mock-wms-api-server)
  - [**Test Data Fixtures**](#test-data-fixtures)
- [Test Execution Strategy](#test-execution-strategy)
  - [**Planned Test Commands**](#planned-test-commands)
  - [**Test Environment Setup**](#test-environment-setup)
- [Re-enabling Strategy](#re-enabling-strategy)
  - [**Phase 1: Mock Infrastructure (Week 1)**](#phase-1-mock-infrastructure-week-1)
  - [**Phase 2: Core Integration Tests (Week 2)**](#phase-2-core-integration-tests-week-2)
  - [**Phase 3: Advanced Integration (Week 3)**](#phase-3-advanced-integration-week-3)
  - [**Phase 4: Comprehensive Coverage (Week 4)**](#phase-4-comprehensive-coverage-week-4)
- [Integration Test Patterns](#integration-test-patterns)
  - [**Mock Server Pattern**](#mock-server-pattern)
  - [**Configuration Test Pattern**](#configuration-test-pattern)
  - [**Data Validation Pattern**](#data-validation-pattern)
- [Performance Integration Testing](#performance-integration-testing)
  - [**Load Testing Integration**](#load-testing-integration)
  - [**Concurrent Operation Testing**](#concurrent-operation-testing)
- [Error Handling Integration](#error-handling-integration)
  - [**Network Failure Testing**](#network-failure-testing)
- [Quality Standards](#quality-standards)
  - [**Integration Test Requirements**](#integration-test-requirements)
  - [**Mock Quality Standards**](#mock-quality-standards)
<!-- TOC END -->

## Overview

This directory contains integration tests for FLEXT Tap Oracle WMS, focusing on testing component interactions and end-to-end workflows with controlled external dependencies.

## Current Status

⚠️ **CRITICAL ISSUE**: Integration tests are currently disabled due to external WMS dependencies.

**Status Summary**:

- **Integration Tests**: Partially disabled (external dependencies)
- **Test Coverage**: Requires re-enabling with mock infrastructure
- **Priority**: High - Essential for production readiness

## Test Structure

### **Disabled Integration Tests**

#### **[test_simple_integration.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup](test_simple_integration.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup)**

**Purpose**: Multi-component integration testing
**Current State**: Disabled due to live WMS API dependencies
**Scope**:

- Tap initialization with real configuration
- Stream discovery and catalog generation
- Data extraction workflow
- Authentication and client integration
- Error handling across component boundaries

**Remediation Required**:

- Replace live WMS calls with comprehensive mocks
- Create mock WMS API server for consistent responses
- Implement test data fixtures for various scenarios
- Add error injection for resilience testing

## Integration Test Strategy

### **Component Integration Patterns**

#### **Tap ↔ Stream Integration**

```python
# Planned integration test pattern
def test_tap_stream_integration():
    """Test tap and stream components working together."""
    with mock_wms_server():
        tap = FlextTapOracleWms(test_config)
        streams = tap.discover_streams()

        # Verify stream discovery
        assert len(streams) > 0

        # Test stream data extraction
        stream = streams[0]
        records = list(stream.get_records({}))
        assert len(records) > 0
```

#### **Authentication ↔ Client Integration**

```python
def test_auth_client_integration():
    """Test authentication integration with client requests."""
    with mock_wms_auth_server():
        auth = get_wms_authenticator(stream, config)
        client = WMSClient(config, auth)

        # Test authenticated request flow
        response = client.get_entities()
        assert response.status_code == 200
```

#### **Discovery ↔ Schema Integration**

```python
def test_discovery_schema_integration():
    """Test entity discovery with schema generation."""
    with mock_wms_metadata():
        discovery = EntityDiscovery(mock_client)
        entities = discovery.discover_entities()

        schema_gen = SchemaGenerator()
        schemas = schema_gen.generate_schemas(entities)

        # Verify end-to-end schema generation
        assert "item" in schemas
        assert "properties" in schemas["item"]
```

### **Configuration Integration Testing**

#### **Configuration Validation Chain**

```python
def test_config_validation_chain():
    """Test complete configuration validation workflow."""
    config = load_test_config("complex_config.json")

    # Test validation chain
    mapper = ConfigMapper()
    mapped_config = mapper.map_config(config)

    validator = ConfigValidator()
    validation_result = validator.validate(mapped_config)

    critical_validator = CriticalValidation()
    critical_result = critical_validator.validate_environment(mapped_config)

    # Verify all validation steps pass
    assert validation_result.is_valid
    assert critical_result.success
```

### **Data Flow Integration Testing**

#### **Extract-Transform-Load Flow**

```python
def test_etl_integration_flow():
    """Test complete data extraction and transformation flow."""
    with mock_wms_data_server():
        # Initialize tap with test configuration
        tap = FlextTapOracleWms(test_config)

        # Discover available streams
        catalog = tap.discover_streams()

        # Extract data from each stream
        for stream_def in catalog:
            stream = tap.get_stream(stream_def.tap_stream_id)
            records = list(stream.get_records({}))

            # Verify data extraction
            assert len(records) > 0

            # Verify data transformation
            for record in records:
                assert "item_id" in record.record
                assert isinstance(record.record["item_id"], str)
```

## Mock Infrastructure Requirements

### **Mock WMS API Server**

```python
# Planned mock server implementation
class MockWMSServer:
    """Mock WMS API server for integration testing."""

    def __init__(self):
        self.entities = ["item", "inventory", "order", "shipment"]
        self.auth_tokens = {}

    def setup_responses(self):
        """Configure mock HTTP responses."""
        responses.add(
            responses.GET,
            "https://mock-wms.test.com/api/entities",
            json={"entities": self.entities},
            status=200
        )

        responses.add(
            responses.GET,
            "https://mock-wms.test.com/api/items",
            json=self.load_test_data("items.json"),
            status=200
        )
```

### **Test Data Fixtures**

```
tests/fixtures/integration/
├── wms_responses/
│   ├── entities_list.json          # Available entities
│   ├── item_data.json              # Sample items data
│   ├── inventory_data.json         # Sample inventory data
│   ├── pagination_responses.json   # Paginated responses
│   └── error_responses.json        # Error scenarios
├── configurations/
│   ├── basic_integration.json      # Basic integration config
│   ├── oauth_integration.json      # OAuth integration config
│   └── complex_integration.json    # Complex scenario config
└── expected_outputs/
    ├── catalog_schema.json         # Expected catalog output
    ├── item_records.json           # Expected item records
    └── error_outputs.json          # Expected error formats
```

## Test Execution Strategy

### **Planned Test Commands**

```bash
# Run integration tests (when re-enabled)
make test-integration

# Run with mock server
pytest tests/integration/ -v --mock-server

# Run specific integration scenarios
pytest tests/integration/ -k "auth_flow"
pytest tests/integration/ -k "discovery_flow"
pytest tests/integration/ -k "extraction_flow"

# Integration tests with coverage
pytest tests/integration/ --cov=src/flext_tap_oracle_wms --cov-report=html
```

### **Test Environment Setup**

```bash
# Environment variables for integration testing
export INTEGRATION_TEST_MODE=true
export MOCK_WMS_SERVER=true
export TEST_WMS_BASE_URL=https://mock-wms.test.com
export TEST_COMPANY_CODE=TEST
export TEST_FACILITY_CODE=TEST01
```

## Re-enabling Strategy

### **Phase 1: Mock Infrastructure (Week 1)**

- [ ] Create comprehensive mock WMS API server
- [ ] Implement test data fixtures and responses
- [ ] Set up mock authentication flows
- [ ] Create configurable mock scenarios

### **Phase 2: Core Integration Tests (Week 2)**

- [ ] Re-enable `test_simple_integration.py` with mocks
- [ ] Implement tap-stream integration tests
- [ ] Add authentication-client integration tests
- [ ] Create configuration validation integration tests

### **Phase 3: Advanced Integration (Week 3)**

- [ ] Add discovery-schema integration tests
- [ ] Implement data flow integration tests
- [ ] Create error handling integration tests
- [ ] Add performance integration tests

### **Phase 4: Comprehensive Coverage (Week 4)**

- [ ] Add edge case integration scenarios
- [ ] Implement concurrent operation tests
- [ ] Create stress testing for integration flows
- [ ] Add monitoring and observability integration

## Integration Test Patterns

### **Mock Server Pattern**

```python
@pytest.fixture
def mock_wms_server():
    """Mock WMS server for integration testing."""
    with responses.RequestsMock() as rsps:
        # Setup standard responses
        rsps.add(responses.GET,
                "https://mock-wms.test.com/api/entities",
                json={"entities": ["item", "inventory"]})

        rsps.add(responses.POST,
                "https://mock-wms.test.com/auth/token",
                json={"access_token": "test_token"})

        yield rsps
```

### **Configuration Test Pattern**

```python
@pytest.fixture
def integration_config():
    """Standard integration test configuration."""
    return {
        "base_url": "https://mock-wms.test.com",
        "auth_method": "basic",
        "username": "integration_test",
        "password": "test_password",
        "company_code": "TEST",
        "facility_code": "TEST01",
        "entities": ["item", "inventory"],
        "page_size": 100
    }
```

### **Data Validation Pattern**

```python
def test_data_integration_flow(mock_wms_server, integration_config):
    """Test complete data integration workflow."""
    # Setup mock responses
    mock_wms_server.add(responses.GET,
                       "https://mock-wms.test.com/api/items",
                       json=load_fixture("item_data.json"))

    # Execute integration flow
    tap = FlextTapOracleWms(integration_config)
    catalog = tap.discover_streams()

    # Validate results
    assert len(catalog) > 0

    # Test data extraction
    item_stream = next(s for s in catalog if s.tap_stream_id == "item")
    records = list(item_stream.get_records({}))

    # Validate extracted data structure
    assert len(records) > 0
    assert all("item_id" in record.record for record in records)
```

## Performance Integration Testing

### **Load Testing Integration**

```python
def test_high_volume_integration():
    """Test integration with high-volume data extraction."""
    with mock_large_dataset():
        tap = FlextTapOracleWms(high_volume_config)

        # Test with large dataset
        records = list(tap.extract_all_data())

        # Verify performance characteristics
        assert len(records) > 10000
        assert extraction_time < 300  # seconds
```

### **Concurrent Operation Testing**

```python
def test_concurrent_stream_integration():
    """Test concurrent stream operations integration."""
    import concurrent.futures

    with mock_wms_server():
        tap = FlextTapOracleWms(test_config)
        streams = tap.discover_streams()

        # Test concurrent extraction
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(stream.extract_data)
                      for stream in streams]

            results = [future.result() for future in futures]

        # Verify all streams completed successfully
        assert all(result.success for result in results)
```

## Error Handling Integration

### **Network Failure Testing**

```python
def test_network_failure_integration():
    """Test integration behavior during network failures."""
    with mock_network_failures():
        tap = FlextTapOracleWms(test_config)

        # Simulate network issues
        with pytest.raises(NetworkError):
            tap.discover_streams()

        # Test recovery mechanisms
        tap.retry_with_backoff()
        streams = tap.discover_streams()
        assert len(streams) > 0
```

## Quality Standards

### **Integration Test Requirements**

- **Isolation**: Tests use mocks, no external dependencies
- **Reliability**: Tests pass consistently without flakiness
- **Performance**: Integration tests complete in under 5 minutes
- **Coverage**: 90% coverage of integration scenarios
- **Documentation**: Clear test purpose and expected behavior

### **Mock Quality Standards**

- **Realistic Responses**: Mock data matches real WMS API patterns
- **Error Scenarios**: Comprehensive error condition coverage
- **Performance**: Mock responses have realistic timing
- **Maintainability**: Mock configurations are easy to update

---

**Status**: Disabled - Requires comprehensive re-enabling · 1.0.0 Release Preparation | **Priority**: High - Critical for production | **Updated**: 2025-08-13
