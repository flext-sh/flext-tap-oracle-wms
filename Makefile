# FLEXT-TAP-ORACLE-WMS Makefile
# Migrated to use base.mk - 2026-01-03

PROJECT_NAME := flext-tap-oracle-wms
MIN_COVERAGE := 100

# Include shared base.mk for standard targets
include ../base.mk

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
