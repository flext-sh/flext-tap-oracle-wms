# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Test module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr


if TYPE_CHECKING:
    from flext_core import FlextTypes
    from tests.unit.test_cli import TestCLI
    from tests.unit.test_config import TestFlextTapOracleWmsSettings
    from tests.unit.test_config_validation import TestConfigValidation
    from tests.unit.test_tap import TestFlextTapOracleWms
    from tests.unit.test_tap_initialization import TestTapInitialization

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestCLI": ["tests.unit.test_cli", "TestCLI"],
    "TestConfigValidation": ["tests.unit.test_config_validation", "TestConfigValidation"],
    "TestFlextTapOracleWms": ["tests.unit.test_tap", "TestFlextTapOracleWms"],
    "TestFlextTapOracleWmsSettings": ["tests.unit.test_config", "TestFlextTapOracleWmsSettings"],
    "TestTapInitialization": ["tests.unit.test_tap_initialization", "TestTapInitialization"],
}

__all__ = [
    "TestCLI",
    "TestConfigValidation",
    "TestFlextTapOracleWms",
    "TestFlextTapOracleWmsSettings",
    "TestTapInitialization",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.
    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.
    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)