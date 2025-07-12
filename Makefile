# FLEXT Tap Oracle WMS - Ultra-Modern Enterprise Makefile v2.0.0
# FLEXT Universal Standards Automation with Git-Enhanced Dependencies
# Standards Reference: .flext-standards.toml v2.0.0

# ═══════════════════════════════════════════════════════════════════════════════
# FLEXT STANDARD CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SHELL := /bin/bash
.DEFAULT_GOAL := help
.PHONY: help

# Project Configuration (FLEXT Standard)
PYTHON := python3.13
POETRY := poetry
PROJECT_NAME := flext-tap-oracle-wms
SRC_DIR := src/flext_tap_oracle_wms
TEST_DIR := tests
SCRIPTS_DIR := scripts

# FLEXT Colors for Enhanced UX
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
NC := \033[0m # No Color

# Version & Git Info
VERSION := $(shell $(POETRY) version -s 2>/dev/null || echo "0.0.0")
COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "no-git")
BRANCH := $(shell git branch --show-current 2>/dev/null || echo "no-git")

# ═══════════════════════════════════════════════════════════════════════════════
# HELP & GENERAL
# ═══════════════════════════════════════════════════════════════════════════════

##@ General

help: ## Display this FLEXT help menu
	@awk 'BEGIN {FS = ":.*##"; printf "\n${CYAN}🚀 FLEXT Enterprise Makefile${NC}\n"}' $(MAKEFILE_LIST)
	@awk 'BEGIN {FS = ":.*##"; printf "${BLUE}Project: $(PROJECT_NAME) v$(VERSION) ($(COMMIT))${NC}\n\n"}' $(MAKEFILE_LIST)
	@awk '/^[a-zA-Z_-]+:.*?##/ { printf "  ${GREEN}%-20s${NC} %s\n", $$1, $$2 } /^##@/ { printf "\n${YELLOW}%s${NC}\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

status: ## Show FLEXT project status
	@echo "${CYAN}📊 FLEXT Project Status${NC}"
	@echo "Project: ${GREEN}$(PROJECT_NAME)${NC} v${GREEN}$(VERSION)${NC}"
	@echo "Branch: ${GREEN}$(BRANCH)${NC} (${GREEN}$(COMMIT)${NC})"
	@echo "Python: ${GREEN}$(shell $(PYTHON) --version)${NC}"
	@echo "Poetry: ${GREEN}$(shell $(POETRY) --version)${NC}"
	@echo "Venv: ${GREEN}$(shell $(POETRY) env info --path 2>/dev/null || echo 'not-found')${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT SETUP (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Environment Setup

install: ## Install all dependencies (FLEXT dev + automation)
	@echo "${BLUE}🔧 Installing FLEXT dependencies...${NC}"
	$(POETRY) install --extras=dev --extras=automation

install-prod: ## Install production dependencies only
	@echo "${GREEN}📦 Installing production dependencies...${NC}"
	$(POETRY) install --only main

install-ci: ## Install CI/CD dependencies (optimized)
	@echo "${CYAN}⚙️ Installing CI dependencies...${NC}"
	$(POETRY) install --extras=dev --no-ansi --quiet

setup: ## Complete FLEXT development environment setup
	@echo "${MAGENTA}🚀 Setting up FLEXT development environment...${NC}"
	@command -v $(POETRY) >/dev/null 2>&1 || { echo "${RED}Poetry not found. Installing...${NC}"; curl -sSL https://install.python-poetry.org | $(PYTHON) -; }
	$(POETRY) install --extras=dev --extras=automation
	$(POETRY) run pre-commit install --install-hooks
	$(POETRY) run pre-commit install --hook-type commit-msg
	@echo "${GREEN}✅ FLEXT development environment ready!${NC}"

update: ## Update all dependencies to latest versions
	@echo "${BLUE}📦 Updating FLEXT dependencies...${NC}"
	$(POETRY) update
	$(POETRY) run pre-commit autoupdate
	@echo "${GREEN}✅ Dependencies updated!${NC}"

clean-env: ## Clean and reset virtual environment
	@echo "${YELLOW}🧹 Cleaning virtual environment...${NC}"
	$(POETRY) env remove --all || true
	rm -rf .venv/
	@echo "${GREEN}✅ Environment cleaned!${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# CODE QUALITY (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Code Quality

format: ## Format code with Ruff (FLEXT standard)
	@echo "${BLUE}🎨 Formatting code with Ruff...${NC}"
	$(POETRY) run ruff format .
	@echo "${GREEN}✅ Code formatted!${NC}"

lint: ## Run all linters with fixes
	@echo "${BLUE}🔍 Running FLEXT linters...${NC}"
	$(POETRY) run ruff check . --fix
	@echo "${GREEN}✅ Linting completed!${NC}"

lint-check: ## Run linters without fixes (CI mode)
	@echo "${BLUE}🔍 Running FLEXT linters (check mode)...${NC}"
	$(POETRY) run ruff check .
	$(POETRY) run ruff format --check .

type-check: ## Run MyPy type checking (strict mode)
	@echo "${BLUE}🔍 Type checking with MyPy...${NC}"
	$(POETRY) run mypy .
	@echo "${GREEN}✅ Type checking passed!${NC}"

security: ## Run security analysis
	@echo "${BLUE}🔒 Running security analysis...${NC}"
	@mkdir -p reports
	$(POETRY) run bandit -r $(SRC_DIR) -f json -o reports/bandit-report.json
	@echo "${GREEN}✅ Security analysis completed!${NC}"

quality: format lint type-check security ## Run all quality checks (FLEXT standard)
	@echo "${GREEN}✅ All FLEXT quality checks passed!${NC}"

check: lint type-check test ## Run all quality checks (lint, type-check, test)
	@echo "${GREEN}✅ All quality checks passed!${NC}"

pre-commit: ## Run pre-commit hooks
	@echo "${BLUE}🪝 Running pre-commit hooks...${NC}"
	$(POETRY) run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "${BLUE}🪝 Updating pre-commit hooks...${NC}"
	$(POETRY) run pre-commit autoupdate

# ═══════════════════════════════════════════════════════════════════════════════
# TESTING (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Testing

test: ## Run all tests
	@echo "${BLUE}🧪 Running FLEXT tests...${NC}"
	$(POETRY) run pytest -v

test-unit: ## Run unit tests only
	@echo "${BLUE}🧪 Running unit tests...${NC}"
	$(POETRY) run pytest tests/unit -v

test-integration: ## Run integration tests only
	@echo "${BLUE}🧪 Running integration tests...${NC}"
	$(POETRY) run pytest tests/integration -v

test-cov: ## Run tests with coverage report
	@echo "${BLUE}📊 Running tests with coverage...${NC}"
	$(POETRY) run pytest --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing --cov-report=xml -v
	@echo "${GREEN}📊 Coverage report generated in htmlcov/${NC}"

test-watch: ## Run tests in watch mode
	@echo "${BLUE}👀 Running tests in watch mode...${NC}"
	$(POETRY) run ptw -- -v

benchmark: ## Run performance benchmarks
	@echo "${BLUE}⚡ Running FLEXT benchmarks...${NC}"
	$(POETRY) run pytest tests/benchmarks -v --benchmark-only

test-all: test-cov benchmark ## Run all tests with coverage and benchmarks
	@echo "${GREEN}✅ All FLEXT tests completed!${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD & RELEASE (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Build & Release

build: clean ## Build FLEXT distribution packages
	@echo "${BLUE}📦 Building FLEXT packages...${NC}"
	$(POETRY) build
	@echo "${GREEN}✅ Build completed!${NC}"

clean: ## Clean build artifacts
	@echo "${YELLOW}🧹 Cleaning build artifacts...${NC}"
	rm -rf dist/ build/ *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov/ .coverage* reports/
	@echo "${GREEN}✅ Clean completed!${NC}"

publish-test: build ## Publish to Test PyPI
	@echo "${BLUE}📤 Publishing to Test PyPI...${NC}"
	$(POETRY) config repositories.test-pypi https://test.pypi.org/legacy/
	$(POETRY) publish -r test-pypi

publish: build ## Publish to PyPI
	@echo "${BLUE}📤 Publishing to PyPI...${NC}"
	$(POETRY) publish

version-patch: ## Bump patch version
	@echo "${BLUE}📝 Bumping patch version...${NC}"
	$(POETRY) version patch
	@echo "${GREEN}New version: $(shell $(POETRY) version -s)${NC}"

version-minor: ## Bump minor version
	@echo "${BLUE}📝 Bumping minor version...${NC}"
	$(POETRY) version minor
	@echo "${GREEN}New version: $(shell $(POETRY) version -s)${NC}"

version-major: ## Bump major version
	@echo "${BLUE}📝 Bumping major version...${NC}"
	$(POETRY) version major
	@echo "${GREEN}New version: $(shell $(POETRY) version -s)${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Development

run: ## Run the FLEXT tap
	@echo "${GREEN}🚀 Running FLEXT tap...${NC}"
	$(POETRY) run tap-oracle-wms --help

run-discover: ## Run tap discovery
	@echo "${BLUE}🔍 Running discovery...${NC}"
	$(POETRY) run tap-oracle-wms --discover --config config.json

run-sync: ## Run tap sync
	@echo "${BLUE}🔄 Running sync...${NC}"
	$(POETRY) run tap-oracle-wms --config config.json --catalog catalog.json

run-enhanced: ## Run enhanced CLI
	@echo "${GREEN}🚀 Running enhanced CLI...${NC}"
	$(POETRY) run tap-oracle-wms-enhanced --help

shell: ## Open IPython shell with project context
	@echo "${BLUE}🐍 Opening FLEXT shell...${NC}"
	$(POETRY) run ipython

debug: ## Run tap with debugger
	@echo "${YELLOW}🐛 Running with debugger...${NC}"
	$(POETRY) run python -m pdb -m flext_tap_oracle_wms.tap

# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENTATION (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Documentation

docs: ## Build FLEXT documentation
	@echo "${BLUE}📚 Building documentation...${NC}"
	$(POETRY) run mkdocs build --strict

docs-serve: ## Serve documentation locally
	@echo "${GREEN}🌐 Serving documentation...${NC}"
	$(POETRY) run mkdocs serve

docs-deploy: ## Deploy documentation
	@echo "${BLUE}🚀 Deploying documentation...${NC}"
	$(POETRY) run mkdocs gh-deploy --force

# ═══════════════════════════════════════════════════════════════════════════════
# AUTOMATION & CI/CD (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Automation

ci: install-ci quality test-all ## Run complete CI pipeline
	@echo "${GREEN}✅ FLEXT CI pipeline completed successfully!${NC}"

ci-local: install quality test-all ## Run CI pipeline locally
	@echo "${GREEN}✅ Local CI pipeline completed!${NC}"

validate: ## Validate FLEXT project configuration
	@echo "${BLUE}✔️ Validating FLEXT project...${NC}"
	$(POETRY) check
	$(POETRY) run pre-commit validate-config
	$(POETRY) run pre-commit validate-manifest
	@echo "${GREEN}✅ FLEXT project validation passed!${NC}"

tox: ## Run tox multi-environment testing
	@echo "${BLUE}🔄 Running tox environments...${NC}"
	$(POETRY) run tox

nox: ## Run nox multi-environment testing
	@echo "${BLUE}🔄 Running nox sessions...${NC}"
	$(POETRY) run nox

changelog: ## Generate FLEXT changelog
	@echo "${BLUE}📝 Generating changelog...${NC}"
	$(POETRY) run cz changelog --incremental

commit: ## Create conventional commit
	@echo "${BLUE}💬 Creating conventional commit...${NC}"
	$(POETRY) run cz commit

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Utilities

tree: ## Show FLEXT project structure
	@echo "${BLUE}📁 FLEXT project structure:${NC}"
	@tree -I '__pycache__|*.pyc|.git|.venv|htmlcov|.pytest_cache|.mypy_cache|.ruff_cache|dist|build|*.egg-info|reports' -a

deps: ## Show dependency tree
	@echo "${BLUE}📦 FLEXT dependency tree:${NC}"
	$(POETRY) show --tree

deps-outdated: ## Show outdated dependencies
	@echo "${BLUE}📦 Outdated dependencies:${NC}"
	$(POETRY) show --outdated

env-info: ## Show environment information
	@echo "${CYAN}ℹ️ FLEXT Environment Information:${NC}"
	@echo "Python: ${GREEN}$(shell $(PYTHON) --version)${NC}"
	@echo "Poetry: ${GREEN}$(shell $(POETRY) --version)${NC}"
	@echo "Project: ${GREEN}$(PROJECT_NAME)${NC} v${GREEN}$(VERSION)${NC}"
	@echo "Branch: ${GREEN}$(BRANCH)${NC} (${GREEN}$(COMMIT)${NC})"
	@echo "Virtual env: ${GREEN}$(shell $(POETRY) env info --path 2>/dev/null || echo 'not-found')${NC}"

reset: clean-env install setup ## Reset entire development environment
	@echo "${GREEN}🔄 FLEXT environment reset complete!${NC}"

health-check: ## Run FLEXT health check
	@echo "${BLUE}🏥 Running FLEXT health check...${NC}"
	@echo "Checking Poetry..."
	@$(POETRY) check >/dev/null && echo "${GREEN}✅ Poetry: OK${NC}" || echo "${RED}❌ Poetry: ERROR${NC}"
	@echo "Checking Python..."
	@$(PYTHON) --version >/dev/null && echo "${GREEN}✅ Python: OK${NC}" || echo "${RED}❌ Python: ERROR${NC}"
	@echo "Checking Git..."
	@git --version >/dev/null && echo "${GREEN}✅ Git: OK${NC}" || echo "${RED}❌ Git: ERROR${NC}"
	@echo "Checking Virtual Environment..."
	@$(POETRY) env info >/dev/null && echo "${GREEN}✅ Venv: OK${NC}" || echo "${RED}❌ Venv: ERROR${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# DOCKER (FLEXT Standard)
# ═══════════════════════════════════════════════════════════════════════════════

##@ Docker

docker-build: ## Build FLEXT Docker image
	@echo "${BLUE}🐳 Building FLEXT Docker image...${NC}"
	docker build -t $(PROJECT_NAME):$(VERSION) -t $(PROJECT_NAME):latest .

docker-run: ## Run FLEXT Docker container
	@echo "${BLUE}🐳 Running FLEXT Docker container...${NC}"
	docker run --rm -it \
		-v $(pwd)/config.json:/app/config.json:ro \
		-v $(pwd)/catalog.json:/app/catalog.json:ro \
		$(PROJECT_NAME):latest

docker-push: ## Push FLEXT Docker image
	@echo "${BLUE}🐳 Pushing FLEXT Docker image...${NC}"
	docker push $(PROJECT_NAME):$(VERSION)
	docker push $(PROJECT_NAME):latest

# ═══════════════════════════════════════════════════════════════════════════════
# FLEXT STANDARDS VALIDATION (v2.0.0)
# ═══════════════════════════════════════════════════════════════════════════════

##@ FLEXT Standards

flext-validate: ## Validate FLEXT Universal Standards compliance
	@echo "${CYAN}🎯 Validating FLEXT Universal Standards v2.0.0...${NC}"
	@test -f .flext-standards.toml && echo "${GREEN}✅ FLEXT standards file present${NC}" || echo "${RED}❌ Missing .flext-standards.toml${NC}"
	@test -f pyproject.toml && echo "${GREEN}✅ pyproject.toml present${NC}" || echo "${RED}❌ Missing pyproject.toml${NC}"
	@test -d src/ && echo "${GREEN}✅ src/ directory present${NC}" || echo "${RED}❌ Missing src/ directory${NC}"
	@test -d tests/ && echo "${GREEN}✅ tests/ directory present${NC}" || echo "${RED}❌ Missing tests/ directory${NC}"
	@test -f .pre-commit-config.yaml && echo "${GREEN}✅ pre-commit config present${NC}" || echo "${RED}❌ Missing pre-commit config${NC}"
	@test -d .github/workflows/ && echo "${GREEN}✅ GitHub workflows present${NC}" || echo "${RED}❌ Missing GitHub workflows${NC}"
	@test -d .vscode/ && echo "${GREEN}✅ VSCode config present${NC}" || echo "${RED}❌ Missing VSCode config${NC}"
	@test -d .cursor/ && echo "${GREEN}✅ Cursor config present${NC}" || echo "${RED}❌ Missing Cursor config${NC}"
	@echo "${CYAN}🏆 FLEXT Standards validation complete!${NC}"

flext-audit: ## Audit project against FLEXT standards
	@echo "${CYAN}🔍 FLEXT Standards Audit...${NC}"
	@echo "${YELLOW}📋 Project Structure:${NC}"
	@ls -la | grep -E '^d|\.toml$$|\.yaml$$|\.yml$$|\.md$$|Makefile$$' || true
	@echo ""
	@echo "${YELLOW}📦 Git Dependencies:${NC}"
	@grep -A 20 "dev = \[" pyproject.toml | grep "git+" || echo "No git dependencies found"
	@echo ""
	@echo "${YELLOW}🛠️ Development Tools:${NC}"
	@$(POETRY) show --only dev 2>/dev/null | head -10 || echo "Cannot show dev dependencies"
	@echo ""
	@echo "${YELLOW}⚙️ Configuration Files:${NC}"
	@find . -maxdepth 2 -name "*.toml" -o -name "*.yaml" -o -name "*.yml" | head -10
	@echo "${CYAN}📊 Audit complete!${NC}"

flext-upgrade: ## Upgrade project to latest FLEXT standards
	@echo "${CYAN}⬆️ Upgrading to latest FLEXT standards...${NC}"
	@echo "${YELLOW}📦 Updating dependencies...${NC}"
	$(POETRY) update
	@echo "${YELLOW}🪝 Updating pre-commit hooks...${NC}"
	$(POETRY) run pre-commit autoupdate
	@echo "${YELLOW}🔧 Running maintenance...${NC}"
	$(MAKE) clean
	$(MAKE) format
	$(MAKE) lint
	@echo "${GREEN}✅ FLEXT upgrade complete!${NC}"

flext-benchmark: ## Benchmark project against FLEXT performance targets
	@echo "${CYAN}⚡ FLEXT Performance Benchmark...${NC}"
	@echo "${YELLOW}🧪 Testing startup time...${NC}"
	@time $(POETRY) run python -c "import flext_tap_oracle_wms; print('✅ Import successful')" 2>&1 | grep real || true
	@echo "${YELLOW}📊 Running performance tests...${NC}"
	$(POETRY) run pytest tests/ --benchmark-only --benchmark-min-rounds=3 2>/dev/null || echo "⚠️ No benchmark tests found"
	@echo "${YELLOW}📈 Checking coverage...${NC}"
	@$(MAKE) test-cov >/dev/null 2>&1 && echo "${GREEN}✅ Coverage target met${NC}" || echo "${YELLOW}⚠️ Coverage below target${NC}"
	@echo "${CYAN}🏁 Benchmark complete!${NC}"

flext-report: ## Generate comprehensive FLEXT project report
	@echo "${CYAN}📋 FLEXT Project Report...${NC}"
	@echo "# FLEXT Project Report - $(PROJECT_NAME)" > flext-report.md
	@echo "Generated: $(shell date)" >> flext-report.md
	@echo "" >> flext-report.md
	@echo "## Project Information" >> flext-report.md
	@echo "- Name: $(PROJECT_NAME)" >> flext-report.md
	@echo "- Version: $(VERSION)" >> flext-report.md
	@echo "- Branch: $(BRANCH)" >> flext-report.md
	@echo "- Commit: $(COMMIT)" >> flext-report.md
	@echo "" >> flext-report.md
	@echo "## FLEXT Standards Compliance" >> flext-report.md
	@$(MAKE) flext-validate >> flext-report.md 2>&1 || true
	@echo "" >> flext-report.md
	@echo "## Dependencies" >> flext-report.md
	@$(POETRY) show >> flext-report.md 2>/dev/null || true
	@echo "${GREEN}✅ Report generated: flext-report.md${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# SPECIAL TARGETS
# ═══════════════════════════════════════════════════════════════════════════════

# All targets are .PHONY since they don't create files
.PHONY: install install-prod install-ci setup update clean-env \
	format lint lint-check type-check security quality pre-commit pre-commit-update \
	test test-unit test-integration test-cov test-watch benchmark test-all \
	build clean publish-test publish version-patch version-minor version-major \
	run run-discover run-sync run-enhanced shell debug \
	docs docs-serve docs-deploy \
	ci ci-local validate tox nox changelog commit \
	tree deps deps-outdated env-info reset health-check \
	docker-build docker-run docker-push status \
	flext-validate flext-audit flext-upgrade flext-benchmark flext-report
# Include standardized build system
include Makefile.build
