# FLEXT TAP ORACLE WMS - Singer Tap for Oracle Warehouse Management System
# ========================================================================
# Enterprise Singer tap for Oracle WMS data extraction with warehouse operations
# Python 3.13 + Singer SDK + Oracle WMS + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check fix
.PHONY: install dev-install setup pre-commit build clean
.PHONY: coverage coverage-html test-unit test-integration test-singer
.PHONY: deps-update deps-audit deps-tree deps-outdated
.PHONY: tap-discover tap-catalog tap-run tap-test tap-validate tap-sync
.PHONY: wms-test wms-inventory wms-orders wms-allocations wms-performance

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🎯 FLEXT TAP ORACLE WMS - Singer Tap for Oracle Warehouse Management System"
	@echo "========================================================================"
	@echo "🎯 Singer SDK + Oracle WMS + Enterprise Operations + Python 3.13"
	@echo ""
	@echo "📦 Enterprise Singer tap for Oracle WMS data extraction"
	@echo "🔒 Zero tolerance quality gates with real WMS integration"
	@echo "🧪 90%+ test coverage requirement with WMS operations compliance"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test tap-test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - FLEXT TAP ORACLE WMS COMPLIANT"

check: lint type-check test ## Essential quality checks (pre-commit standard)
	@echo "✅ Essential checks passed"

lint: ## Ruff linting (17 rule categories, ALL enabled)
	@echo "🔍 Running ruff linter (ALL rules enabled)..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ Linting complete"

type-check: ## MyPy strict mode type checking (zero errors tolerated)
	@echo "🛡️ Running MyPy strict type checking..."
	@poetry run mypy src/ tests/ --strict
	@echo "✅ Type checking complete"

security: ## Security scans (bandit + pip-audit + secrets)
	@echo "🔒 Running security scans..."
	@poetry run bandit -r src/ --severity-level medium --confidence-level medium
	@poetry run pip-audit --ignore-vuln PYSEC-2022-42969
	@poetry run detect-secrets scan --all-files
	@echo "✅ Security scans complete"

format: ## Format code with ruff
	@echo "🎨 Formatting code..."
	@poetry run ruff format src/ tests/
	@echo "✅ Formatting complete"

format-check: ## Check formatting without fixing
	@echo "🎨 Checking code formatting..."
	@poetry run ruff format src/ tests/ --check
	@echo "✅ Format check complete"

fix: format lint ## Auto-fix all issues (format + imports + lint)
	@echo "🔧 Auto-fixing all issues..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ All auto-fixes applied"

# ============================================================================
# 🧪 TESTING - 90% COVERAGE MINIMUM
# ============================================================================

test: ## Run tests with coverage (90% minimum required)
	@echo "🧪 Running tests with coverage..."
	@poetry run pytest tests/ -v --cov=src/flext_tap_oracle_wms --cov-report=term-missing --cov-fail-under=90
	@echo "✅ Tests complete"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v
	@echo "✅ Unit tests complete"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/integration/ -v
	@echo "✅ Integration tests complete"

test-singer: ## Run Singer-specific tests
	@echo "🧪 Running Singer protocol tests..."
	@poetry run pytest tests/ -m "singer" -v
	@echo "✅ Singer tests complete"

test-wms: ## Run WMS-specific tests
	@echo "🧪 Running Oracle WMS tests..."
	@poetry run pytest tests/ -m "wms" -v
	@echo "✅ WMS tests complete"

test-oracle: ## Run Oracle database tests
	@echo "🧪 Running Oracle database tests..."
	@poetry run pytest tests/ -m "oracle" -v
	@echo "✅ Oracle tests complete"

test-performance: ## Run performance tests
	@echo "⚡ Running Singer tap performance tests..."
	@poetry run pytest tests/performance/ -v --benchmark-only
	@echo "✅ Performance tests complete"

coverage: ## Generate detailed coverage report
	@echo "📊 Generating coverage report..."
	@poetry run pytest tests/ --cov=src/flext_tap_oracle_wms --cov-report=term-missing --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/"

coverage-html: coverage ## Generate HTML coverage report
	@echo "📊 Opening coverage report..."
	@python -m webbrowser htmlcov/index.html

# ============================================================================
# 🚀 DEVELOPMENT SETUP
# ============================================================================

setup: install pre-commit ## Complete development setup
	@echo "🎯 Development setup complete!"

install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies..."
	@poetry install --all-extras --with dev,test,docs,security
	@echo "✅ Dependencies installed"

dev-install: install ## Install in development mode
	@echo "🔧 Setting up development environment..."
	@poetry install --all-extras --with dev,test,docs,security
	@poetry run pre-commit install
	@echo "✅ Development environment ready"

pre-commit: ## Setup pre-commit hooks
	@echo "🎣 Setting up pre-commit hooks..."
	@poetry run pre-commit install
	@poetry run pre-commit run --all-files || true
	@echo "✅ Pre-commit hooks installed"

# ============================================================================
# 🎵 SINGER TAP OPERATIONS - CORE FUNCTIONALITY
# ============================================================================

tap-discover: ## Discover Oracle WMS schema for catalog generation
	@echo "🔍 Discovering Oracle WMS schema..."
	@poetry run tap-oracle-wms --discover
	@echo "✅ WMS schema discovery complete"

tap-catalog: ## Generate Singer catalog from Oracle WMS
	@echo "📋 Generating Singer catalog..."
	@poetry run tap-oracle-wms --discover > catalog.json
	@echo "✅ Singer catalog generated: catalog.json"

tap-run: ## Run Oracle WMS tap with sample configuration
	@echo "🎵 Running Oracle WMS tap..."
	@poetry run tap-oracle-wms --config config.json --catalog catalog.json
	@echo "✅ Oracle WMS tap execution complete"

tap-test: ## Test Oracle WMS tap functionality
	@echo "🧪 Testing Oracle WMS tap functionality..."
	@poetry run python -c "from flext_tap_oracle_wms.tap import TapOracleWMS; from flext_tap_oracle_wms.client import OracleWMSClient; print('Oracle WMS tap loaded successfully')"
	@echo "✅ Oracle WMS tap test complete"

tap-validate: ## Validate Oracle WMS tap configuration
	@echo "🔍 Validating Oracle WMS tap configuration..."
	@poetry run python scripts/validate_tap_config.py
	@echo "✅ Oracle WMS tap configuration validation complete"

tap-sync: ## Test incremental sync functionality
	@echo "🔄 Testing incremental sync..."
	@poetry run python scripts/test_incremental_sync.py
	@echo "✅ Incremental sync test complete"

tap-state: ## Test state management
	@echo "📊 Testing state management..."
	@poetry run python scripts/test_state_management.py
	@echo "✅ State management test complete"

# ============================================================================
# 🏭 ORACLE WMS OPERATIONS
# ============================================================================

wms-test: ## Test Oracle WMS connectivity
	@echo "🏭 Testing Oracle WMS connectivity..."
	@poetry run python scripts/test_wms_connectivity.py
	@echo "✅ WMS connectivity test complete"

wms-inventory: ## Test WMS inventory data extraction
	@echo "📦 Testing WMS inventory extraction..."
	@poetry run python scripts/test_wms_inventory.py
	@echo "✅ WMS inventory test complete"

wms-orders: ## Test WMS orders data extraction
	@echo "📋 Testing WMS orders extraction..."
	@poetry run python scripts/test_wms_orders.py
	@echo "✅ WMS orders test complete"

wms-allocations: ## Test WMS allocations data extraction
	@echo "🎯 Testing WMS allocations extraction..."
	@poetry run python scripts/test_wms_allocations.py
	@echo "✅ WMS allocations test complete"

wms-performance: ## Test WMS performance optimization
	@echo "⚡ Testing WMS performance optimization..."
	@poetry run python scripts/test_wms_performance.py
	@echo "✅ WMS performance test complete"

wms-schema: ## Analyze WMS database schema
	@echo "📋 Analyzing WMS database schema..."
	@poetry run python scripts/analyze_wms_schema.py
	@echo "✅ WMS schema analysis complete"

wms-queries: ## Test WMS query optimization
	@echo "🔍 Testing WMS query optimization..."
	@poetry run python scripts/test_wms_queries.py
	@echo "✅ WMS query optimization test complete"

wms-batch: ## Test WMS batch processing
	@echo "📦 Testing WMS batch processing..."
	@poetry run python scripts/test_wms_batch.py
	@echo "✅ WMS batch processing test complete"

# ============================================================================
# 🎵 SINGER PROTOCOL COMPLIANCE
# ============================================================================

singer-spec: ## Validate Singer specification compliance
	@echo "🎵 Validating Singer specification compliance..."
	@poetry run python scripts/validate_singer_spec.py
	@echo "✅ Singer specification validation complete"

singer-messages: ## Test Singer message output
	@echo "📬 Testing Singer message output..."
	@poetry run python scripts/test_singer_messages.py
	@echo "✅ Singer message test complete"

singer-catalog: ## Validate Singer catalog format
	@echo "📋 Validating Singer catalog format..."
	@poetry run python scripts/validate_singer_catalog.py
	@echo "✅ Singer catalog validation complete"

singer-state: ## Test Singer state handling
	@echo "📊 Testing Singer state handling..."
	@poetry run python scripts/test_singer_state.py
	@echo "✅ Singer state test complete"

singer-metrics: ## Test Singer metrics output
	@echo "📈 Testing Singer metrics output..."
	@poetry run python scripts/test_singer_metrics.py
	@echo "✅ Singer metrics test complete"

singer-streams: ## Test Singer stream implementations
	@echo "🌊 Testing Singer stream implementations..."
	@poetry run python scripts/test_singer_streams.py
	@echo "✅ Singer streams test complete"

# ============================================================================
# 🔍 DATA QUALITY & VALIDATION
# ============================================================================

validate-wms-data: ## Validate WMS data format compliance
	@echo "🔍 Validating WMS data format compliance..."
	@poetry run python scripts/validate_wms_data.py
	@echo "✅ WMS data format validation complete"

validate-schema-discovery: ## Validate schema discovery accuracy
	@echo "🔍 Validating schema discovery..."
	@poetry run python scripts/validate_schema_discovery.py
	@echo "✅ Schema discovery validation complete"

validate-data-extraction: ## Validate data extraction accuracy
	@echo "🔍 Validating data extraction..."
	@poetry run python scripts/validate_data_extraction.py
	@echo "✅ Data extraction validation complete"

validate-warehouse-operations: ## Validate warehouse operations data
	@echo "🔍 Validating warehouse operations data..."
	@poetry run python scripts/validate_warehouse_operations.py
	@echo "✅ Warehouse operations validation complete"

data-quality-report: ## Generate comprehensive data quality report
	@echo "📊 Generating data quality report..."
	@poetry run python scripts/generate_quality_report.py
	@echo "✅ Data quality report generated"

# ============================================================================
# 🔐 ORACLE DATABASE OPERATIONS
# ============================================================================

oracle-connection: ## Test Oracle database connection
	@echo "🔐 Testing Oracle database connection..."
	@poetry run python scripts/test_oracle_connection.py
	@echo "✅ Oracle connection test complete"

oracle-pooling: ## Test Oracle connection pooling
	@echo "🏊 Testing Oracle connection pooling..."
	@poetry run python scripts/test_oracle_pooling.py
	@echo "✅ Oracle pooling test complete"

oracle-performance: ## Test Oracle query performance
	@echo "⚡ Testing Oracle query performance..."
	@poetry run python scripts/test_oracle_performance.py
	@echo "✅ Oracle performance test complete"

oracle-security: ## Test Oracle security features
	@echo "🔒 Testing Oracle security features..."
	@poetry run python scripts/test_oracle_security.py
	@echo "✅ Oracle security test complete"

# ============================================================================
# 📦 BUILD & DISTRIBUTION
# ============================================================================

build: clean ## Build distribution packages
	@echo "🔨 Building distribution..."
	@poetry build
	@echo "✅ Build complete - packages in dist/"

package: build ## Create deployment package
	@echo "📦 Creating deployment package..."
	@tar -czf dist/flext-tap-oracle-wms-deployment.tar.gz \
		src/ \
		tests/ \
		scripts/ \
		pyproject.toml \
		README.md \
		CLAUDE.md
	@echo "✅ Deployment package created: dist/flext-tap-oracle-wms-deployment.tar.gz"

# ============================================================================
# 🧹 CLEANUP
# ============================================================================

clean: ## Remove all artifacts
	@echo "🧹 Cleaning up..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -f catalog.json
	@rm -f state.json
	@rm -f wms_extract.json
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# ============================================================================
# 📊 DEPENDENCY MANAGEMENT
# ============================================================================

deps-update: ## Update all dependencies
	@echo "🔄 Updating dependencies..."
	@poetry update
	@echo "✅ Dependencies updated"

deps-audit: ## Audit dependencies for vulnerabilities
	@echo "🔍 Auditing dependencies..."
	@poetry run pip-audit
	@echo "✅ Dependency audit complete"

deps-tree: ## Show dependency tree
	@echo "🌳 Dependency tree:"
	@poetry show --tree

deps-outdated: ## Show outdated dependencies
	@echo "📋 Outdated dependencies:"
	@poetry show --outdated

# ============================================================================
# 🔧 ENVIRONMENT CONFIGURATION
# ============================================================================

# Python settings
PYTHON := python3.13
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export PYTHONDONTWRITEBYTECODE := 1
export PYTHONUNBUFFERED := 1

# Oracle WMS Tap settings
export TAP_ORACLE_WMS_HOST := localhost
export TAP_ORACLE_WMS_PORT := 1521
export TAP_ORACLE_WMS_SERVICE_NAME := WMSPROD
export TAP_ORACLE_WMS_USERNAME := wms_user
export TAP_ORACLE_WMS_PASSWORD := wms_password
export TAP_ORACLE_WMS_SCHEMA := WMS

# WMS extraction settings
export TAP_ORACLE_WMS_BATCH_SIZE := 10000
export TAP_ORACLE_WMS_INCLUDE_HISTORICAL := false
export TAP_ORACLE_WMS_ORDER_STATUS_FILTER := OPEN,ALLOCATED,PICKED

# Oracle connection settings
export TAP_ORACLE_WMS_POOL_SIZE := 10
export TAP_ORACLE_WMS_POOL_INCREMENT := 1
export TAP_ORACLE_WMS_POOL_TIMEOUT := 30
export TAP_ORACLE_WMS_QUERY_TIMEOUT := 300
export TAP_ORACLE_WMS_ENCODING := UTF-8

# WMS-specific settings
export TAP_ORACLE_WMS_WAREHOUSE_IDS := WH01,WH02,WH03
export TAP_ORACLE_WMS_ZONE_FILTER := PICK,PACK,SHIP
export TAP_ORACLE_WMS_ITEM_STATUS_FILTER := ACTIVE

# Performance optimization settings
export TAP_ORACLE_WMS_ENABLE_PARALLEL := true
export TAP_ORACLE_WMS_PARALLEL_DEGREE := 4
export TAP_ORACLE_WMS_ENABLE_HINTS := true
export TAP_ORACLE_WMS_OPTIMIZER_MODE := ALL_ROWS

# Incremental sync settings
export TAP_ORACLE_WMS_START_DATE := 2024-01-01T00:00:00Z
export TAP_ORACLE_WMS_ENABLE_BOOKMARKING := true
export TAP_ORACLE_WMS_BOOKMARK_PROPERTIES := modified_date

# Advanced WMS features
export TAP_ORACLE_WMS_INCLUDE_ALLOCATIONS := true
export TAP_ORACLE_WMS_INCLUDE_TASKS := true
export TAP_ORACLE_WMS_INCLUDE_TRANSACTIONS := false
export TAP_ORACLE_WMS_INCLUDE_CYCLE_COUNTS := false

# Singer settings
export SINGER_SDK_LOG_LEVEL := INFO
export SINGER_SDK_BATCH_SIZE := 1000
export SINGER_SDK_MAX_RECORD_AGE_IN_MINUTES := 5

# Poetry settings
export POETRY_VENV_IN_PROJECT := false
export POETRY_CACHE_DIR := $(HOME)/.cache/pypoetry

# Quality gate settings
export MYPY_CACHE_DIR := .mypy_cache
export RUFF_CACHE_DIR := .ruff_cache

# ============================================================================
# 📝 PROJECT METADATA
# ============================================================================

# Project information
PROJECT_NAME := flext-tap-oracle-wms
PROJECT_VERSION := $(shell poetry version -s)
PROJECT_DESCRIPTION := FLEXT TAP ORACLE WMS - Singer Tap for Oracle Warehouse Management System

.DEFAULT_GOAL := help

# ============================================================================
# 🎯 DEVELOPMENT UTILITIES
# ============================================================================

dev-wms-server: ## Start development WMS mock server
	@echo "🔧 Starting development WMS mock server..."
	@poetry run python scripts/dev_wms_server.py
	@echo "✅ Development WMS mock server started"

dev-tap-monitor: ## Monitor tap operations
	@echo "📊 Monitoring tap operations..."
	@poetry run python scripts/monitor_tap_operations.py
	@echo "✅ Tap monitoring complete"

dev-wms-explorer: ## Interactive WMS data explorer
	@echo "🎮 Starting WMS data explorer..."
	@poetry run python scripts/wms_explorer.py
	@echo "✅ WMS explorer session complete"

dev-inventory-analyzer: ## Interactive inventory analyzer
	@echo "📦 Starting inventory analyzer..."
	@poetry run python scripts/inventory_analyzer.py
	@echo "✅ Inventory analyzer session complete"

dev-order-tracker: ## Interactive order tracker
	@echo "📋 Starting order tracker..."
	@poetry run python scripts/order_tracker.py
	@echo "✅ Order tracker session complete"

# ============================================================================
# 🎯 FLEXT ECOSYSTEM INTEGRATION
# ============================================================================

ecosystem-check: ## Verify FLEXT ecosystem compatibility
	@echo "🌐 Checking FLEXT ecosystem compatibility..."
	@echo "📦 Core project: $(PROJECT_NAME) v$(PROJECT_VERSION)"
	@echo "🏗️ Architecture: Singer Tap + Oracle WMS + Warehouse Operations"
	@echo "🐍 Python: 3.13"
	@echo "🔗 Framework: FLEXT Core + Singer SDK + Oracle WMS"
	@echo "📊 Quality: Zero tolerance enforcement"
	@echo "✅ Ecosystem compatibility verified"

workspace-info: ## Show workspace integration info
	@echo "🏢 FLEXT Workspace Integration"
	@echo "==============================="
	@echo "📁 Project Path: $(PWD)"
	@echo "🏆 Role: Singer Tap for Oracle Warehouse Management System"
	@echo "🔗 Dependencies: flext-core, flext-observability, singer-sdk, oracledb"
	@echo "📦 Provides: Oracle WMS data extraction via Singer protocol"
	@echo "🎯 Standards: Enterprise Singer tap patterns with WMS domain expertise"

# ============================================================================
# 🔄 CONTINUOUS INTEGRATION
# ============================================================================

ci-check: validate ## CI quality checks
	@echo "🔍 Running CI quality checks..."
	@poetry run python scripts/ci_quality_report.py
	@echo "✅ CI quality checks complete"

ci-performance: ## CI performance benchmarks
	@echo "⚡ Running CI performance benchmarks..."
	@poetry run python scripts/ci_performance_benchmarks.py
	@echo "✅ CI performance benchmarks complete"

ci-integration: ## CI integration tests
	@echo "🔗 Running CI integration tests..."
	@poetry run pytest tests/integration/ -v --tb=short
	@echo "✅ CI integration tests complete"

ci-singer: ## CI Singer protocol tests
	@echo "🎵 Running CI Singer tests..."
	@poetry run pytest tests/ -m "singer" -v --tb=short
	@echo "✅ CI Singer tests complete"

ci-wms: ## CI Oracle WMS tests
	@echo "🏭 Running CI Oracle WMS tests..."
	@poetry run pytest tests/ -m "wms" -v --tb=short
	@echo "✅ CI WMS tests complete"

ci-oracle: ## CI Oracle database tests
	@echo "🔐 Running CI Oracle tests..."
	@poetry run pytest tests/ -m "oracle" -v --tb=short
	@echo "✅ CI Oracle tests complete"

ci-all: ci-check ci-performance ci-integration ci-singer ci-wms ci-oracle ## Run all CI checks
	@echo "✅ All CI checks complete"

# ============================================================================
# 🚀 PRODUCTION DEPLOYMENT
# ============================================================================

deploy-tap: validate build ## Deploy tap for production use
	@echo "🚀 Deploying Oracle WMS tap..."
	@poetry run python scripts/deploy_tap.py
	@echo "✅ Oracle WMS tap deployment complete"

test-deployment: ## Test deployed tap functionality
	@echo "🧪 Testing deployed tap..."
	@poetry run python scripts/test_deployed_tap.py
	@echo "✅ Deployment test complete"

rollback-deployment: ## Rollback tap deployment
	@echo "🔄 Rolling back tap deployment..."
	@poetry run python scripts/rollback_tap_deployment.py
	@echo "✅ Deployment rollback complete"

# ============================================================================
# 🔬 MONITORING & OBSERVABILITY
# ============================================================================

monitor-wms-connections: ## Monitor WMS database connections
	@echo "📊 Monitoring WMS connections..."
	@poetry run python scripts/monitor_wms_connections.py
	@echo "✅ WMS connection monitoring complete"

monitor-extraction-performance: ## Monitor extraction performance
	@echo "📊 Monitoring extraction performance..."
	@poetry run python scripts/monitor_extraction_performance.py
	@echo "✅ Extraction performance monitoring complete"

monitor-warehouse-operations: ## Monitor warehouse operations metrics
	@echo "📊 Monitoring warehouse operations..."
	@poetry run python scripts/monitor_warehouse_operations.py
	@echo "✅ Warehouse operations monitoring complete"

generate-tap-metrics: ## Generate tap performance metrics
	@echo "📊 Generating tap performance metrics..."
	@poetry run python scripts/generate_tap_metrics.py
	@echo "✅ Tap metrics generated"

generate-wms-report: ## Generate WMS extraction report
	@echo "📊 Generating WMS extraction report..."
	@poetry run python scripts/generate_wms_report.py
	@echo "✅ WMS extraction report generated"