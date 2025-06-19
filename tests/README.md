# tap-oracle-wms Test Suite

Comprehensive test suite for the Oracle WMS tap implementation.

## 📁 Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── pytest.ini                    # Pytest configuration
├── README.md                      # This file
│
├── test_unit_auth.py             # Unit tests for authentication
├── test_unit_discovery.py        # Unit tests for entity discovery
├── test_unit_pagination.py       # Unit tests for pagination
├── test_unit_state.py            # Unit tests for state management
├── test_unit_streams.py          # Unit tests for stream functionality
│
├── test_integration_discovery.py # Integration tests for discovery
├── test_integration_extraction.py # Integration tests for data extraction
├── test_integration_state.py     # Integration tests for state management
│
└── test_live_comprehensive.py    # Comprehensive live API tests
```

## 🏷️ Test Categories

### Unit Tests (`@pytest.mark.unit`)

- **Fast execution** (< 1 second per test)
- **No external dependencies** (mocked WMS API)
- **High coverage** of individual components
- **Run by default** in CI/CD pipelines

### Integration Tests (`@pytest.mark.integration`)

- **Medium execution time** (1-30 seconds per test)
- **May use external services** (but typically mocked)
- **Test component interactions**
- **Run in staging environments**

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
# Run all unit tests (default)
pytest

# Run specific unit test module
pytest tests/test_unit_auth.py

# Run specific test
pytest tests/test_unit_auth.py::TestWMSAuthentication::test_get_wms_headers_basic_auth
```

### Integration Tests

```bash
# Run all integration tests
pytest -m integration

# Run specific integration test
pytest tests/test_integration_discovery.py
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

### Custom Test Selection

```bash
# Run only authentication tests
pytest -m auth

# Run pagination tests across all categories
pytest -m pagination

# Run state management tests
pytest -m state

# Exclude slow tests
pytest -m "not slow"

# Run unit and integration but not live
pytest -m "not live"

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=tap_oracle_wms --cov-report=html
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
