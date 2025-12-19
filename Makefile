# flext-tap-oracle-wms - Oracle WMS Singer Tap
PROJECT_NAME := flext-tap-oracle-wms
COV_DIR := flext_tap_oracle_wms
MIN_COVERAGE := 90

include ../base.mk

# === PROJECT-SPECIFIC TARGETS ===
.PHONY: tap-run tap-discover test-unit test-integration build shell

tap-run: ## Run tap with config
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run tap-oracle-wms --config config.json

tap-discover: ## Run discovery mode
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run tap-oracle-wms --config config.json --discover

.DEFAULT_GOAL := help
