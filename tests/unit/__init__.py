# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Test module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from tests.unit.test_cli import TestCLI
    from tests.unit.test_config import TestFlextTapOracleWmsSettings
    from tests.unit.test_config_validation import TestConfigValidation
    from tests.unit.test_tap import TestFlextTapOracleWms
    from tests.unit.test_tap_initialization import TestTapInitialization

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestCLI": ("tests.unit.test_cli", "TestCLI"),
    "TestConfigValidation": (
        "tests.unit.test_config_validation",
        "TestConfigValidation",
    ),
    "TestFlextTapOracleWms": ("tests.unit.test_tap", "TestFlextTapOracleWms"),
    "TestFlextTapOracleWmsSettings": (
        "tests.unit.test_config",
        "TestFlextTapOracleWmsSettings",
    ),
    "TestTapInitialization": (
        "tests.unit.test_tap_initialization",
        "TestTapInitialization",
    ),
}

__all__ = [
    "TestCLI",
    "TestConfigValidation",
    "TestFlextTapOracleWms",
    "TestFlextTapOracleWmsSettings",
    "TestTapInitialization",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
