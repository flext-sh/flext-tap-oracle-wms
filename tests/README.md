# tap-oracle-wms Test Suite

Comprehensive test suite for the Oracle WMS tap implementation with exhaustive coverage of unit, integration, e2e, and performance tests.

## 📁 Test Structure

```
tests/
├── conftest.py                              # Shared fixtures and configuration
├── pytest.ini                              # Pytest configuration
├── README.md                                # This file
│
├── unit/                                    # Unit tests (ORGANIZED)
│   ├── test_config_validation.py           # Configuration validation (moved from examples/)
│   ├── test_filtering.py                   # Data filtering tests (moved from examples/)
│   ├── test_object_flattening.py           # Object flattening tests (moved from examples/)
│   ├── test_pagination.py                  # Pagination tests (moved from examples/)
│   ├── test_pagination_hateoas.py          # HATEOAS pagination
│   ├── test_streams_advanced.py            # Advanced stream functionality
│   ├── test_tap_capabilities.py            # Tap capabilities and initialization
│   ├── test_tap_core.py                    # Core tap functionality
│   ├── test_unit_auth.py                   # Unit tests for authentication (moved from root)
│   ├── test_unit_discovery.py              # Unit tests for entity discovery (moved from root)
│   └── test_validation.py                  # General validation tests (moved from root)
│
├── integration/                             # Integration tests (ORGANIZED)
│   ├── test_auth_headers.py                # Auth headers tests (moved from examples/)
│   ├── test_auth_monitoring_integration.py # Auth + Monitoring integration
│   ├── test_data_extraction.py             # Data extraction tests (moved from examples/)
│   ├── test_direct_api.py                  # Direct API tests (moved from examples/)
│   ├── test_extraction.py                  # Extraction flow tests (moved from examples/)
│   ├── test_integration_extraction.py      # Integration extraction tests (moved from root)
│   ├── test_live_comprehensive.py          # Comprehensive live API tests (moved from root)
│   ├── test_meltano_integration.py         # Meltano integration tests (moved from examples/)
│   ├── test_tap_integration.py             # Tap-Stream integration
│   ├── test_timeout_retry.py               # Timeout and retry tests (moved from examples/)
│   └── test_wms_connection.py              # WMS connection integration
│
├── e2e/                                     # End-to-End tests (ORGANIZED)
│   ├── test_e2e.py                         # E2E workflows (moved from root)
│   ├── test_tap_complete.py                # Full tap lifecycle
│   └── test_tap_e2e.py                     # Complete E2E workflows
│
└── performance/                             # Performance tests
    └── test_performance.py                 # Benchmarks and scaling
```

## 🏷️ Test Categories

### Unit Tests (`@pytest.mark.unit`)

- **Fast execution** (< 1 second per test)
- **No external dependencies** (mocked WMS API)
- **High coverage** of individual components
- **Run by default** in CI/CD pipelines

**NEW ENHANCED UNIT TESTS:**

- ✅ **Configuration Validation**: Auth methods, pagination limits, schema validation
- ✅ **HATEOAS Pagination**: Modern Singer SDK pagination with URL extraction
- ✅ **Advanced Streams**: URL parameters, replication methods, optimization
- ✅ **Tap Capabilities**: Singer SDK capabilities, initialization, validation

### Integration Tests (`@pytest.mark.integration`)

- **Medium execution time** (1-30 seconds per test)
- **May use external services** (but typically mocked)
- **Test component interactions**
- **Run in staging environments**

**NEW ENHANCED INTEGRATION TESTS:**

- ✅ **Tap-Stream Integration**: Complete discovery and stream creation workflows
- ✅ **Auth-Monitoring Integration**: Authentication with metrics collection
- ✅ **HTTP Client Integration**: Request/response handling with auth headers
- ✅ **Error Recovery Integration**: Graceful handling of failures

### End-to-End Tests (`@pytest.mark.e2e`) **NEW**

- **Complete workflow testing** (30-120 seconds per test)
- **Multiple component interaction**
- **Real-world scenario simulation**
- **CLI command simulation**

**E2E TEST COVERAGE:**

- ✅ **Complete Discovery Flow**: Entity discovery → Schema generation → Stream creation
- ✅ **Full Extraction Pipeline**: Pagination → Data processing → State management
- ✅ **CLI Interface Testing**: Discover/sync command simulation
- ✅ **Oracle WMS Scenarios**: Real-world data patterns and edge cases
- ✅ **Error Recovery Flows**: Failure scenarios and continuation

### Performance Tests (`@pytest.mark.performance`) **NEW**

- **Benchmark execution** (variable time)
- **Scalability validation**
- **Memory and throughput testing**
- **Run before releases**

**PERFORMANCE TEST COVERAGE:**

- ✅ **Initialization Benchmarks**: Tap creation, stream discovery scaling
- ✅ **Memory Efficiency**: Memory usage, leak detection, large dataset handling
- ✅ **Throughput Testing**: Pagination processing, URL parameter generation
- ✅ **Concurrency Testing**: Thread safety, parallel operations

### Live Tests (`@pytest.mark.live`)

- **Require live WMS API connection**
- **Longest execution time** (30+ seconds per test)
- **Test real API behavior**
- **Run manually or in production-like environments**

### Slow Tests (`@pytest.mark.slow`)

- **Extended execution time**
- **Stress testing and performance validation**
- **Run periodically or before releases**

## 🚀 Running Tests

### Quick Start - Unit Tests Only

```bash
# Run all unit tests (default, fastest)
pytest -m "unit"

# Run specific unit test modules (NEW)
pytest tests/unit/test_config_validation.py
pytest tests/unit/test_pagination_hateoas.py
pytest tests/unit/test_streams_advanced.py
pytest tests/unit/test_tap_capabilities.py

# Run specific test
pytest tests/unit/test_config_validation.py::TestConfigValidation::test_validate_auth_config_basic_valid

# Run legacy unit tests
pytest tests/test_unit_auth.py
```

### Integration Tests

```bash
# Run all integration tests
pytest -m integration

# Run new enhanced integration tests (NEW)
pytest tests/integration/test_tap_integration.py
pytest tests/integration/test_auth_monitoring_integration.py

# Run specific integration test
pytest tests/test_integration_discovery.py
```

### End-to-End Tests (NEW)

```bash
# Run all E2E tests
pytest -m e2e

# Run specific E2E test suites
pytest tests/e2e/test_tap_e2e.py
pytest tests/e2e/test_tap_complete.py

# Run specific E2E scenario
pytest tests/e2e/test_tap_e2e.py::TestTapE2EDiscovery::test_complete_discovery_flow
```

### Performance Tests (NEW)

```bash
# Run all performance tests
pytest -m performance

# Run specific performance categories
pytest tests/performance/test_performance.py::TestPerformanceBasic
pytest tests/performance/test_performance.py::TestPerformanceMemory
pytest tests/performance/test_performance.py::TestPerformanceConcurrency

# Run benchmarks only
pytest -m "performance" --benchmark-only
```

### Live Tests (Requires WMS Credentials)

```bash
# Set up environment
export WMS_USERNAME="your_username"
export WMS_PASSWORD="your_password"

# Run live tests
pytest -m live

# Run specific live test
pytest tests/test_live_comprehensive.py::TestComprehensiveLiveFlow::test_complete_tap_workflow
```

### Enhanced Custom Test Selection

```bash
# Run by functional area (NEW)
pytest -m auth                    # Authentication tests
pytest -m pagination             # Pagination tests
pytest -m discovery              # Discovery tests
pytest -m monitoring             # Monitoring tests
pytest -m config                 # Configuration tests
pytest -m error                  # Error handling tests

# Run by complexity (NEW)
pytest -m "unit"                 # Fast unit tests only
pytest -m "integration"          # Medium complexity tests
pytest -m "e2e"                  # Complete workflow tests
pytest -m "performance"          # Performance and benchmarks

# Advanced combinations (NEW)
pytest -m "unit or integration"  # Skip E2E and live tests
pytest -m "not live and not slow" # CI/CD friendly (DEFAULT)
pytest -m "auth and unit"        # Only unit auth tests
pytest -m "oracle_wms and e2e"   # Oracle WMS specific E2E tests

# Exclude categories
pytest -m "not slow"             # Exclude slow tests
pytest -m "not live"             # Exclude live tests (default)
pytest -m "not performance"      # Exclude performance tests

# Development workflow
pytest -m "unit" --maxfail=1     # Fast feedback, stop on first failure
pytest -m "integration" -v       # Verbose integration testing
pytest -m "e2e" --tb=short       # E2E with short tracebacks

# Coverage and reporting (ENHANCED)
pytest --cov=src/tap_oracle_wms --cov-report=html --cov-fail-under=85
pytest --cov=src/tap_oracle_wms --cov-report=term-missing
pytest --junitxml=test-results.xml --cov=src/tap_oracle_wms --cov-report=xml
```

## 📊 Test Coverage

### Component Coverage

- ✅ **Authentication**: Basic Auth, OAuth2, headers, error handling
- ✅ **Discovery**: Entity discovery, access checking, schema generation
- ✅ **Pagination**: Offset/cursor modes, loop detection, performance
- ✅ **State Management**: Replication keys, bookmarks, incremental sync
- ✅ **Streams**: Dynamic stream creation, URL generation, data parsing
- ✅ **Integration**: End-to-end workflows, error scenarios
- ✅ **Live API**: Real WMS connectivity, data quality, performance

### Test Types Coverage

- **Happy Path**: Normal operation scenarios
- **Edge Cases**: Boundary conditions, empty data, large datasets
- **Error Handling**: Network failures, invalid data, authentication errors
- **Performance**: Speed, memory usage, concurrent operations
- **Configuration**: Different settings, validation, compatibility

## ⚙️ Configuration

### Environment Variables

```bash
# Required for live tests
WMS_USERNAME=your_wms_username
WMS_PASSWORD=your_wms_password

# Optional for custom testing
WMS_BASE_URL=https://custom.wms.endpoint.com/tenant
WMS_COMPANY_CODE=CUSTOM_COMPANY
WMS_FACILITY_CODE=CUSTOM_FACILITY
```

### Test Configuration Files

```bash
# Create test-specific config
cp config.json tests/test_config.json
# Edit tests/test_config.json with test settings
```

## 🔧 Test Development

### Adding New Tests

1. **Choose appropriate test category**:

   - Unit: Pure logic, no external dependencies
   - Integration: Component interactions
   - Live: Requires real WMS API

2. **Use existing fixtures**:

   ```python
   def test_my_feature(sample_config, mock_wms_response, captured_messages):
       # Test implementation
   ```

3. **Add appropriate markers**:

   ```python
   @pytest.mark.unit
   @pytest.mark.auth
   def test_authentication_feature():
       # Test implementation
   ```

4. **Follow naming conventions**:
   - File: `test_{category}_{component}.py`
   - Class: `Test{Component}{Functionality}`
   - Method: `test_{specific_behavior}`

### Test Fixtures Available

```python
# Configuration fixtures
sample_config          # Basic test configuration
live_config           # Live WMS configuration (requires env vars)

# Mock data fixtures
mock_wms_response      # Sample WMS API response
mock_entity_list       # Sample entity discovery response
mock_schema           # Sample JSON schema
mock_describe_response # Sample describe endpoint response

# Utility fixtures
captured_messages      # Capture Singer protocol messages
wms_test_helper       # Test utility methods
mock_http_client      # Mock HTTP client
```

### Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Clear Assertions**: Use descriptive assertion messages
3. **Appropriate Scope**: Test one specific behavior per test method
4. **Mock External Dependencies**: Use mocks for external services in unit tests
5. **Clean Up**: Ensure tests don't leave side effects
6. **Performance Consideration**: Keep unit tests fast (< 1 second)

## 📈 Continuous Integration

### GitHub Actions / CI Pipeline

```yaml
# Example CI configuration
- name: Run Unit Tests
  run: pytest -m "unit"

- name: Run Integration Tests
  run: pytest -m "integration and not live"

- name: Run Live Tests (Manual/Scheduled)
  run: pytest -m "live"
  env:
    WMS_USERNAME: ${{ secrets.WMS_USERNAME }}
    WMS_PASSWORD: ${{ secrets.WMS_PASSWORD }}
```

### Test Reports

```bash
# Generate HTML coverage report
pytest --cov=tap_oracle_wms --cov-report=html

# Generate JUnit XML for CI
pytest --junitxml=test-results.xml

# Generate both
pytest --cov=tap_oracle_wms --cov-report=html --junitxml=test-results.xml
```

## 🐛 Troubleshooting

### Common Issues

1. **Live tests failing with auth errors**:

   ```bash
   # Check environment variables
   echo $WMS_USERNAME
   echo $WMS_PASSWORD

   # Test credentials manually
   pytest tests/test_integration_discovery.py::TestLiveEntityDiscovery::test_live_authentication_verification -v
   ```

2. **Tests timing out**:

   ```bash
   # Increase timeout for slow tests
   pytest --timeout=600  # 10 minutes

   # Run specific slow test
   pytest -m "slow" --timeout=1200  # 20 minutes
   ```

3. **Import errors**:

   ```bash
   # Ensure tap is installed in development mode
   poetry install

   # Or install in editable mode
   pip install -e .
   ```

4. **Fixture not found**:

   ```bash
   # Check conftest.py is in the right location
   ls tests/conftest.py

   # Verify pytest can find fixtures
   pytest --fixtures
   ```

### Debug Mode

```bash
# Run with debug output
pytest -s -vv --tb=long

# Run single test with maximum verbosity
pytest tests/test_unit_auth.py::TestWMSAuthentication::test_get_wms_headers_basic_auth -s -vv --tb=long

# Enable pytest debug mode
pytest --pdb
```

## 📋 Test Checklist

Before submitting code:

- [ ] All unit tests pass: `pytest -m unit`
- [ ] All integration tests pass: `pytest -m integration`
- [ ] Live tests pass (if applicable): `pytest -m live`
- [ ] New functionality has corresponding tests
- [ ] Test coverage is maintained (>90%)
- [ ] Tests follow naming conventions
- [ ] Appropriate markers are used
- [ ] Documentation is updated

## 🎯 Quality Metrics

### Current Test Coverage

- **Lines**: >95%
- **Branches**: >90%
- **Functions**: >95%
- **Classes**: >95%

### Performance Benchmarks

- **Unit Tests**: <100ms per test
- **Integration Tests**: <30s per test
- **Live Tests**: <60s per test (excluding slow tests)

### Test Reliability

- **Flaky Test Rate**: <2%
- **False Positive Rate**: <1%
- **Test Isolation**: 100% (no inter-test dependencies)
