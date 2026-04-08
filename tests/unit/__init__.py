# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "test_cli": "tests.unit.test_cli",
    "test_config": "tests.unit.test_config",
    "test_config_validation": "tests.unit.test_config_validation",
    "test_tap": "tests.unit.test_tap",
    "test_tap_initialization": "tests.unit.test_tap_initialization",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
