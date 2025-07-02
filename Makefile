# Oracle WMS Tap - Complete Makefile
# Automatically handles venv, configuration, and all operations

# Auto-detect and setup environment
VENV_PATH := /home/marlonsc/flext/.venv
PYTHON := $(VENV_PATH)/bin/python
ACTIVATE := source $(VENV_PATH)/bin/activate

# Auto-check if environment is ready
ENV_CHECK := $(shell test -f $(VENV_PATH)/bin/python && echo "ready" || echo "missing")

help:
	@echo "Oracle WMS Tap - Complete Automation"
	@echo "===================================="
	@echo "🚀 QUICK START:"
	@echo "  make auto-setup  - Auto-detect credentials and setup everything"
	@echo "  make run-all     - Complete validation and testing"
	@echo ""
	@echo "📊 Real WMS Testing:"
	@echo "  make check-connection - Test Oracle WMS connection"
	@echo "  make test-entity     - Test entity extraction"
	@echo "  make discover        - Discover all entities from WMS"
	@echo "  make extract         - Extract data from WMS"
	@echo "  make e2e-test        - Complete end-to-end test"
	@echo ""
	@echo "🧪 Development Testing:"
	@echo "  make test            - Unit tests"
	@echo "  make test-integration - Integration tests"
	@echo "  make mock            - Mock server test"
	@echo "  make validate        - Complete validation"
	@echo ""
	@echo "🛠️ Utilities:"
	@echo "  make info            - Show environment info"
	@echo "  make clean           - Clean all artifacts"
	@echo "  make perf-test       - Performance testing"

# Check environment and setup if needed
check-env:
	@echo "Checking environment..."
	@if [ "$(ENV_CHECK)" = "missing" ]; then \
		echo "Environment not ready. Run 'make setup' first."; \
		exit 1; \
	else \
		echo "Environment ready"; \
	fi

# Auto-setup with credential detection
auto-setup: check-env
	@echo "🚀 Starting automatic setup..."
	@$(ACTIVATE) && python auto_setup.py

# Setup everything needed
setup:
	@echo "Setting up Oracle WMS Tap environment..."
	@if [ ! -f $(VENV_PATH)/bin/python ]; then \
		echo "Virtual environment not found at $(VENV_PATH)"; \
		echo "Please ensure the FLEXT workspace venv exists"; \
		exit 1; \
	fi
	@echo "Environment setup complete"

# Create config file for testing
config:
	@$(ACTIVATE) && python -c "import os; print('Base URL:', os.getenv('TAP_ORACLE_WMS_BASE_URL', 'NOT_SET'))"
	@if [ -f .env ]; then \
		echo "Using existing .env configuration"; \
	else \
		echo "Warning: .env file not found"; \
	fi

# Run all tests and validation
run-all: check-env config
	@echo "Running complete Oracle WMS Tap validation..."
	@echo ""
	@echo "1. Unit Tests:"
	@$(MAKE) test
	@echo ""
	@echo "2. Integration Tests:"
	@$(MAKE) test-integration
	@echo ""
	@echo "3. Mock Server Test:"
	@$(MAKE) mock
	@echo ""
	@echo "4. Configuration Validation:"
	@$(MAKE) validate-config
	@echo ""
	@echo "5. Singer CLI Test:"
	@$(MAKE) validate-cli
	@echo ""
	@echo "✅ ALL TESTS COMPLETED SUCCESSFULLY"

# Test with real Oracle WMS
test-real: check-env
	@echo "Testing with real Oracle WMS..."
	@$(ACTIVATE) && python test_real_wms.py

# Unit tests
test: check-env
	@$(ACTIVATE) && python -m pytest tests/unit/ -v --tb=short

# Integration tests
test-integration: check-env
	@$(ACTIVATE) && python -m pytest tests/integration/ -v --tb=short

# Mock server test
mock: check-env
	@echo "Testing with mock WMS server..."
	@$(ACTIVATE) && python test_mock_simple.py

# Validate configuration
validate-config: check-env
	@echo "Validating configuration..."
	@$(ACTIVATE) && python tests/e2e/validate_config.py

# Validate CLI commands
validate-cli: check-env
	@echo "Validating CLI commands..."
	@$(ACTIVATE) && python -m tap_oracle_wms --help > /dev/null && echo "  ✅ --help: OK"
	@$(ACTIVATE) && python -m tap_oracle_wms --version && echo "  ✅ --version: OK"
	@$(ACTIVATE) && python -m tap_oracle_wms --about > /dev/null && echo "  ✅ --about: OK"

# Complete validation
validate: check-env validate-config validate-cli mock
	@echo "✅ Complete validation successful"

# Discover entities from WMS
discover: check-env
	@echo "Discovering entities from Oracle WMS..."
	@$(ACTIVATE) && python -m tap_oracle_wms --config .env --discover

# Extract data from WMS
extract: check-env
	@echo "Extracting data from Oracle WMS..."
	@if [ ! -f catalog.json ]; then \
		echo "Catalog not found. Running discovery first..."; \
		$(MAKE) discover > catalog.json; \
	fi
	@$(ACTIVATE) && python -m tap_oracle_wms --config .env --catalog catalog.json

# Generate catalog file
catalog: check-env
	@echo "Generating catalog file..."
	@$(ACTIVATE) && python -m tap_oracle_wms --config .env --discover > catalog.json
	@echo "✅ Catalog saved to catalog.json"

# Test specific entity
test-entity: check-env
	@echo "Testing specific entity extraction..."
	@$(ACTIVATE) && python -c "\
import asyncio; \
from tap_oracle_wms.discovery import EntityDiscovery; \
import os; \
from dotenv import load_dotenv; \
load_dotenv(); \
config = { \
    'base_url': os.getenv('TAP_ORACLE_WMS_BASE_URL'), \
    'username': os.getenv('TAP_ORACLE_WMS_USERNAME'), \
    'password': os.getenv('TAP_ORACLE_WMS_PASSWORD'), \
    'company_code': os.getenv('TAP_ORACLE_WMS_COMPANY_CODE', '*'), \
    'facility_code': os.getenv('TAP_ORACLE_WMS_FACILITY_CODE', '*'), \
    'verify_ssl': os.getenv('TAP_ORACLE_WMS_VERIFY_SSL', 'true').lower() == 'true', \
    'record_limit': 5 \
}; \
discovery = EntityDiscovery(config); \
entities = asyncio.run(discovery.discover_entities()); \
if entities: \
    first_entity = list(entities.keys())[0]; \
    print(f'Testing entity: {first_entity}'); \
    samples = asyncio.run(discovery.get_entity_sample(first_entity, limit=3)); \
    print(f'✅ Got {len(samples)} sample records'); \
    if samples: print(f'Fields: {list(samples[0].keys())}'); \
else: \
    print('❌ No entities found') \
"

# Check WMS connectivity
check-connection: check-env
	@echo "Checking Oracle WMS connectivity..."
	@$(ACTIVATE) && python -c "\
import asyncio; \
from tap_oracle_wms.discovery import EntityDiscovery; \
import os; \
from dotenv import load_dotenv; \
load_dotenv(); \
config = { \
    'base_url': os.getenv('TAP_ORACLE_WMS_BASE_URL'), \
    'username': os.getenv('TAP_ORACLE_WMS_USERNAME'), \
    'password': os.getenv('TAP_ORACLE_WMS_PASSWORD'), \
    'company_code': os.getenv('TAP_ORACLE_WMS_COMPANY_CODE', '*'), \
    'facility_code': os.getenv('TAP_ORACLE_WMS_FACILITY_CODE', '*'), \
    'verify_ssl': os.getenv('TAP_ORACLE_WMS_VERIFY_SSL', 'true').lower() == 'true' \
}; \
print(f'Connecting to: {config[\"base_url\"]}'); \
print(f'Username: {config[\"username\"]}'); \
print(f'Company: {config[\"company_code\"]}'); \
print(f'Facility: {config[\"facility_code\"]}'); \
discovery = EntityDiscovery(config); \
try: \
    entities = asyncio.run(discovery.discover_entities()); \
    print(f'✅ Connection successful! Found {len(entities)} entities'); \
    for i, entity in enumerate(list(entities.keys())[:3], 1): \
        print(f'  {i}. {entity}'); \
    if len(entities) > 3: print(f'  ... and {len(entities) - 3} more'); \
except Exception as e: \
    print(f'❌ Connection failed: {e}'); \
    import sys; sys.exit(1) \
"

# Complete end-to-end test
e2e-test: check-env
	@echo "Running complete end-to-end test..."
	@echo "1. Checking connection..."
	@$(MAKE) check-connection
	@echo ""
	@echo "2. Testing entity access..."
	@$(MAKE) test-entity
	@echo ""
	@echo "3. Generating catalog..."
	@$(MAKE) catalog
	@echo ""
	@echo "✅ End-to-end test completed successfully"

# Performance test
perf-test: check-env
	@echo "Running performance test..."
	@$(ACTIVATE) && python -c "\
import asyncio; \
import time; \
from tap_oracle_wms.discovery import EntityDiscovery; \
import os; \
from dotenv import load_dotenv; \
load_dotenv(); \
config = { \
    'base_url': os.getenv('TAP_ORACLE_WMS_BASE_URL'), \
    'username': os.getenv('TAP_ORACLE_WMS_USERNAME'), \
    'password': os.getenv('TAP_ORACLE_WMS_PASSWORD'), \
    'company_code': os.getenv('TAP_ORACLE_WMS_COMPANY_CODE', '*'), \
    'facility_code': os.getenv('TAP_ORACLE_WMS_FACILITY_CODE', '*'), \
    'verify_ssl': os.getenv('TAP_ORACLE_WMS_VERIFY_SSL', 'true').lower() == 'true', \
    'page_size': 100 \
}; \
discovery = EntityDiscovery(config); \
start = time.time(); \
entities = asyncio.run(discovery.discover_entities()); \
discovery_time = time.time() - start; \
print(f'Discovery: {discovery_time:.2f}s for {len(entities)} entities'); \
if entities: \
    entity = list(entities.keys())[0]; \
    start = time.time(); \
    samples = asyncio.run(discovery.get_entity_sample(entity, limit=10)); \
    sample_time = time.time() - start; \
    print(f'Sample extraction: {sample_time:.2f}s for {len(samples)} records'); \
    print(f'✅ Performance test completed') \
"

# Clean artifacts
clean:
	@echo "Cleaning artifacts..."
	@rm -f catalog.json schema.json state.json messages.jsonl test_config.json
	@rm -rf .pytest_cache __pycache__ *.egg-info build dist
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Show environment info
info: check-env
	@echo "Oracle WMS Tap Environment Info"
	@echo "==============================="
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Virtual Env: $(VENV_PATH)"
	@echo "Working Dir: $(shell pwd)"
	@$(ACTIVATE) && python -c "import tap_oracle_wms; print(f'TAP Version: {tap_oracle_wms.__version__ if hasattr(tap_oracle_wms, \"__version__\") else \"0.1.0\"}')"
	@echo ""
	@echo "Configuration Status:"
	@$(ACTIVATE) && python -c "\
import os; \
from dotenv import load_dotenv; \
load_dotenv(); \
print(f'  Base URL: {\"SET\" if os.getenv(\"TAP_ORACLE_WMS_BASE_URL\") and not \"your-\" in os.getenv(\"TAP_ORACLE_WMS_BASE_URL\", \"\") else \"NOT SET\"}'); \
print(f'  Username: {\"SET\" if os.getenv(\"TAP_ORACLE_WMS_USERNAME\") and not \"your_\" in os.getenv(\"TAP_ORACLE_WMS_USERNAME\", \"\") else \"NOT SET\"}'); \
print(f'  Password: {\"SET\" if os.getenv(\"TAP_ORACLE_WMS_PASSWORD\") and not \"your_\" in os.getenv(\"TAP_ORACLE_WMS_PASSWORD\", \"\") else \"NOT SET\"}') \
"

.PHONY: help check-env auto-setup setup config run-all test-real test test-integration mock validate-config validate-cli validate discover extract catalog test-entity check-connection e2e-test perf-test clean info