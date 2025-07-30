# FLEXT-TAP-ORACLE-WMS Makefile
PROJECT_NAME := flext-tap-oracle-wms
PYTHON_VERSION := 3.13
POETRY := poetry
SRC_DIR := src
TESTS_DIR := tests

# Quality standards
MIN_COVERAGE := 90

# Singer configuration
TAP_CONFIG := config.json
TAP_CATALOG := catalog.json
TAP_STATE := state.json

# Help
help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-18s\\033[0m %s\\n", $$1, $$2}'

# Installation
install: ## Install dependencies
	$(POETRY) install

install-dev: ## Install dev dependencies
	$(POETRY) install --with dev,test,docs

setup: install-dev ## Complete project setup
	$(POETRY) run pre-commit install

# Quality gates
validate: lint type-check security test ## Run all quality gates

check: lint type-check ## Quick health check

lint: ## Run linting
	$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR)

format: ## Format code
	$(POETRY) run ruff format $(SRC_DIR) $(TESTS_DIR)

type-check: ## Run type checking
	$(POETRY) run mypy $(SRC_DIR) --strict

security: ## Run security scanning
	$(POETRY) run bandit -r $(SRC_DIR)
	$(POETRY) run pip-audit

fix: ## Auto-fix issues
	$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR) --fix
	$(POETRY) run ruff format $(SRC_DIR) $(TESTS_DIR)

# Testing
test: ## Run tests with coverage
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=term-missing --cov-fail-under=$(MIN_COVERAGE)

test-unit: ## Run unit tests
	$(POETRY) run pytest $(TESTS_DIR) -m "not integration" -v

test-integration: ## Run integration tests
	$(POETRY) run pytest $(TESTS_DIR) -m integration -v

test-singer: ## Run Singer protocol tests
	$(POETRY) run pytest $(TESTS_DIR) -m singer -v

test-fast: ## Run tests without coverage
	$(POETRY) run pytest $(TESTS_DIR) -v

coverage-html: ## Generate HTML coverage report
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html

# Singer tap operations
discover: ## Run tap discovery mode
	$(POETRY) run tap-oracle-wms --config $(TAP_CONFIG) --discover > $(TAP_CATALOG)

run: ## Run tap extraction
	$(POETRY) run tap-oracle-wms --config $(TAP_CONFIG) --catalog $(TAP_CATALOG) --state $(TAP_STATE)

validate-config: ## Validate tap configuration
	$(POETRY) run python -c "import json; json.load(open('$(TAP_CONFIG)'))"

catalog: discover ## Alias for discover

sync: run ## Alias for run

# WMS operations
wms-test: ## Test Oracle WMS connectivity
	$(POETRY) run python -c "from flext_tap_oracle_wms.client import test_connection; test_connection()"

wms-entities: ## List available WMS entities
	$(POETRY) run python -c "from flext_tap_oracle_wms.discovery import list_entities; list_entities()"

wms-performance: ## Run WMS performance test
	$(POETRY) run python -c "from flext_tap_oracle_wms.performance import run_performance_test; run_performance_test()"

# Build
build: ## Build package
	$(POETRY) build

build-clean: clean build ## Clean and build

# Documentation
docs: ## Build documentation
	$(POETRY) run mkdocs build

docs-serve: ## Serve documentation
	$(POETRY) run mkdocs serve

# Dependencies
deps-update: ## Update dependencies
	$(POETRY) update

deps-show: ## Show dependency tree
	$(POETRY) show --tree

deps-audit: ## Audit dependencies
	$(POETRY) run pip-audit

# Development
shell: ## Open Python shell
	$(POETRY) run python

pre-commit: ## Run pre-commit hooks
	$(POETRY) run pre-commit run --all-files

# Maintenance
clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/
	rm -rf $(TAP_CATALOG) $(TAP_STATE)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-all: clean ## Deep clean including venv
	rm -rf .venv/

reset: clean-all setup ## Reset project

# Diagnostics
diagnose: ## Project diagnostics
	@echo "Python: $$(python --version)"
	@echo "Poetry: $$($(POETRY) --version)"
	@echo "Singer SDK: $$($(POETRY) run python -c 'import singer_sdk; print(singer_sdk.__version__)' 2>/dev/null || echo 'Not available')"
	@$(POETRY) env info

doctor: diagnose check ## Health check

# Aliases
t: test
l: lint
f: format
tc: type-check
c: clean
i: install
v: validate
d: discover
r: run

.DEFAULT_GOAL := help
.PHONY: help install install-dev setup validate check lint format type-check security fix test test-unit test-integration test-singer test-fast coverage-html discover run validate-config catalog sync wms-test wms-entities wms-performance build build-clean docs docs-serve deps-update deps-show deps-audit shell pre-commit clean clean-all reset diagnose doctor t l f tc c i v d r