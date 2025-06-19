# Makefile for tap-oracle-wms
# Strict PEP8 compliance with Poetry

.PHONY: help install dev-install clean test test-cov lint format type-check security check pre-commit build docs run discover extract validate config-gen

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON_VERSION = 3.9+
PROJECT_NAME = tap-oracle-wms
SRC_DIR = src/tap_oracle_wms
TEST_DIR = tests
DOCS_DIR = docs

# Colors for output
BLUE = \033[34m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)$(PROJECT_NAME) Makefile Commands$(NC)"
	@echo "$(YELLOW)Setup Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

## SETUP COMMANDS

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	poetry install --only=main --no-interaction --no-ansi

dev-install: ## Install all dependencies including dev
	@echo "$(BLUE)Installing all dependencies...$(NC)"
	poetry install --no-interaction --no-ansi
	poetry run pre-commit install

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .tox/
	rm -rf **/__pycache__/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

## QUALITY ASSURANCE COMMANDS

lint: ## Run all linters (ruff, black, isort)
	@echo "$(BLUE)Running linters...$(NC)"
	poetry run ruff check $(SRC_DIR) $(TEST_DIR) --fix
	poetry run black --check $(SRC_DIR) $(TEST_DIR)
	poetry run isort --check-only $(SRC_DIR) $(TEST_DIR)

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	poetry run black $(SRC_DIR) $(TEST_DIR)
	poetry run isort $(SRC_DIR) $(TEST_DIR)
	poetry run ruff check $(SRC_DIR) $(TEST_DIR) --fix

type-check: ## Run mypy type checking
	@echo "$(BLUE)Running type checking...$(NC)"
	poetry run mypy $(SRC_DIR)

security: ## Run security checks (bandit, safety)
	@echo "$(BLUE)Running security checks...$(NC)"
	poetry run bandit -r $(SRC_DIR) -f json -o bandit-report.json
	poetry run safety check --json --output safety-report.json

check: lint type-check security ## Run all quality checks

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	poetry run pre-commit run --all-files

## TESTING COMMANDS

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	poetry run pytest $(TEST_DIR) -v

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	poetry run pytest $(TEST_DIR) -v \
		--cov=$(SRC_DIR) \
		--cov-report=html \
		--cov-report=xml \
		--cov-report=term-missing \
		--cov-fail-under=90

test-e2e: ## Run E2E tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	poetry run python $(TEST_DIR)/e2e/test_tap_e2e.py

## BUILD COMMANDS

build: ## Build the package
	@echo "$(BLUE)Building package...$(NC)"
	poetry build

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	poetry run mkdocs build

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	poetry run mkdocs serve

## APPLICATION COMMANDS

config-gen: ## Generate config.json from .env
	@echo "$(BLUE)Generating config from .env...$(NC)"
	poetry run python generate_config.py

discover: config-gen ## Run discovery command
	@echo "$(BLUE)Running discovery...$(NC)"
	poetry run tap-oracle-wms --config config.json --discover

extract: config-gen ## Run extraction
	@echo "$(BLUE)Running extraction...$(NC)"
	poetry run tap-oracle-wms --config config.json --catalog catalog.json

validate: ## Validate configuration
	@echo "$(BLUE)Validating configuration...$(NC)"
	poetry run python -c "from tap_oracle_wms.tap import TapOracleWMS; import json; tap = TapOracleWMS(config=json.load(open('config.json'))); tap.validate_config(); print('✅ Configuration is valid')"

run: extract ## Alias for extract

## DEVELOPMENT COMMANDS

shell: ## Open Poetry shell
	poetry shell

install-hooks: ## Install git hooks
	poetry run pre-commit install

update: ## Update dependencies
	poetry update

lock: ## Update poetry.lock
	poetry lock

version: ## Show version
	poetry version

bump-patch: ## Bump patch version
	poetry version patch

bump-minor: ## Bump minor version
	poetry version minor

bump-major: ## Bump major version
	poetry version major

## CI/CD COMMANDS

ci-test: ## Run CI test suite
	$(MAKE) clean
	$(MAKE) dev-install
	$(MAKE) check
	$(MAKE) test-cov
	$(MAKE) build

publish: ## Publish to PyPI
	poetry publish

publish-test: ## Publish to test PyPI
	poetry publish --repository testpypi

## MONITORING COMMANDS

metrics: ## Show project metrics
	@echo "$(BLUE)Project Metrics:$(NC)"
	@echo "Lines of code:"
	@find $(SRC_DIR) -name "*.py" -exec wc -l {} + | tail -1
	@echo "Test coverage:"
	@poetry run pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=term-missing --quiet | grep "TOTAL"
	@echo "Dependencies:"
	@poetry show --tree | head -20

debug: ## Show debug information
	@echo "$(BLUE)Debug Information:$(NC)"
	@echo "Python version: $(shell python --version)"
	@echo "Poetry version: $(shell poetry --version)"
	@echo "Project root: $(shell pwd)"
	@echo "Virtual env: $(shell poetry env info --path)"
	@echo "Dependencies status:"
	@poetry check
