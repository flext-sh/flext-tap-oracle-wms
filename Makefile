# FLEXT-TAP-ORACLE-WMS Makefile
# Migrated to use base.mk - 2026-01-03

PROJECT_NAME := flext-tap-oracle-wms
# Include shared base.mk for standard targets
ifneq ("$(wildcard ../base.mk)", "")
include ../base.mk
else
# =============================================================================
# STANDALONE BOOTSTRAP — auto-generates base.mk via flext-infra
# =============================================================================
# GNU Make auto-rebuild: if base.mk is missing, Make builds this target first,
# then restarts with base.mk loaded. All standard verbs become available.
# =============================================================================

PYTHON_VERSION ?= 3.13
PYTHON_CMD := $(firstword $(shell command -v python$(PYTHON_VERSION) python3 python 2>/dev/null))
BOOTSTRAP_VENV := .venv
BOOTSTRAP_PIP := $(BOOTSTRAP_VENV)/bin/pip
BOOTSTRAP_PYTHON := $(BOOTSTRAP_VENV)/bin/python

-include base.mk

base.mk: Makefile
	@echo "==> Resolving base.mk for $(PROJECT_NAME)..."
	@if [ -d "$(BOOTSTRAP_VENV)" ] && $(BOOTSTRAP_PYTHON) -c 'import flext_infra' 2>/dev/null; then \
		$(BOOTSTRAP_PYTHON) -m flext_infra basemk generate \
			--project-name $(PROJECT_NAME) --output $@; \
	elif $(PYTHON_CMD) -c 'import flext_infra' 2>/dev/null; then \
		$(PYTHON_CMD) -m flext_infra basemk generate \
			--project-name $(PROJECT_NAME) --output $@; \
	else \
		echo "==> flext-infra not found. Bootstrapping standalone environment..."; \
		$(MAKE) _bootstrap-venv; \
		$(BOOTSTRAP_PIP) install -q flext-infra; \
		$(BOOTSTRAP_PYTHON) -m flext_infra basemk generate \
			--project-name $(PROJECT_NAME) --output $@; \
	fi
	@test -s $@ || { echo "ERROR: base.mk generation failed"; rm -f $@; exit 1; }
	@echo "==> base.mk generated. Restarting make..."

.PHONY: _bootstrap-venv venv setup help

_bootstrap-venv:
	@if [ ! -d "$(BOOTSTRAP_VENV)" ]; then \
		echo "==> Creating virtual environment with $(PYTHON_CMD)..."; \
		if [ -z "$(PYTHON_CMD)" ]; then \
			echo "ERROR: Python $(PYTHON_VERSION) not found. Install it first."; \
			exit 1; \
		fi; \
		$(PYTHON_CMD) -m venv $(BOOTSTRAP_VENV); \
		$(BOOTSTRAP_PIP) install -q -U pip; \
	fi

venv: _bootstrap-venv ## Create standalone virtual environment
	@$(BOOTSTRAP_PIP) install -q -U pip poetry
	@echo "Virtual environment ready at $(BOOTSTRAP_VENV)"

setup: venv ## Full standalone setup (venv + dependencies + base.mk)
	@echo "==> Installing project dependencies..."
	@$(BOOTSTRAP_PIP) install -q flext-infra
	@$(BOOTSTRAP_PYTHON) -m flext_infra deps internal-sync \
		--project-root "$(CURDIR)" 2>/dev/null || true
	@$(BOOTSTRAP_VENV)/bin/poetry lock
	@$(BOOTSTRAP_VENV)/bin/poetry install --all-extras --all-groups
	@if git rev-parse --git-dir >/dev/null 2>&1; then \
		$(BOOTSTRAP_VENV)/bin/poetry run pre-commit install 2>/dev/null || true; \
	fi
	@$(BOOTSTRAP_PYTHON) -m flext_infra basemk generate \
		--project-name $(PROJECT_NAME) --output base.mk
	@echo "==> Setup complete. All 'make' verbs now available."

help: ## Show available commands
	@echo "================================================"
	@echo "  $(PROJECT_NAME) (standalone bootstrap)"
	@echo "================================================"
	@echo ""
	@echo "Bootstrap targets (no base.mk required):"
	@printf "  %-14s %s\n" "venv"   "Create virtual environment"
	@printf "  %-14s %s\n" "setup"  "Full standalone setup"
	@printf "  %-14s %s\n" "help"   "Show this help"
	@echo ""
	@echo "After 'make setup', all standard verbs become available:"
	@echo "  check, test, format, build, validate, clean, docs, pr"
	@echo ""
	@echo "Run 'make setup' first, then 'make help' for full verb list."
endif

# =============================================================================
# SINGER TAP CONFIGURATION
# =============================================================================

TAP_CONFIG ?= config.json
TAP_CATALOG ?= catalog.json
TAP_STATE ?= state.json

# =============================================================================
# SINGER TAP OPERATIONS
# =============================================================================

.PHONY: discover run catalog sync validate-config test-singer

discover: ## Run tap discovery mode
	$(POETRY) run tap-oracle-wms --config $(TAP_CONFIG) --discover > $(TAP_CATALOG)

run: ## Run tap extraction
	$(POETRY) run tap-oracle-wms --config $(TAP_CONFIG) --catalog $(TAP_CATALOG) --state $(TAP_STATE)

catalog: discover ## Alias for discover

sync: run ## Alias for run

validate-config: ## Validate tap configuration
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "import json; json.load(open('$(TAP_CONFIG)'))"

# =============================================================================
# WMS-SPECIFIC TARGETS
# =============================================================================

.PHONY: wms-test wms-entities wms-performance

wms-test: ## Test Oracle WMS connectivity
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_tap_oracle_wms.client import test_connection; test_connection()"

wms-entities: ## List available WMS entities
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_tap_oracle_wms.discovery import list_entities; list_entities()"

wms-performance: ## Run WMS performance test
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_tap_oracle_wms.performance import run_performance_test; run_performance_test()"

# =============================================================================
# PROJECT-SPECIFIC TEST TARGETS
# =============================================================================

test-singer: ## Run Singer protocol tests
	$(POETRY) run pytest $(TESTS_DIR) -m singer -v
