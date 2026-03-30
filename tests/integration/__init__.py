# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration tests for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from tests.integration import (
        test_functional,
        test_streams_functional,
        test_wms,
        test_wms_connection,
    )
    from tests.integration.test_functional import TestOracleWMSFunctionalComplete
    from tests.integration.test_streams_functional import TestStreamsFunctional, logger
    from tests.integration.test_wms import TestRealWmsIntegration
    from tests.integration.test_wms_connection import (
        TestFilteringAndSelection,
        TestIntegration,
        TestRealConnection,
        TestRealDataExtraction,
        env_path,
        real_config,
        tap,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestFilteringAndSelection": [
        "tests.integration.test_wms_connection",
        "TestFilteringAndSelection",
    ],
    "TestIntegration": ["tests.integration.test_wms_connection", "TestIntegration"],
    "TestOracleWMSFunctionalComplete": [
        "tests.integration.test_functional",
        "TestOracleWMSFunctionalComplete",
    ],
    "TestRealConnection": [
        "tests.integration.test_wms_connection",
        "TestRealConnection",
    ],
    "TestRealDataExtraction": [
        "tests.integration.test_wms_connection",
        "TestRealDataExtraction",
    ],
    "TestRealWmsIntegration": ["tests.integration.test_wms", "TestRealWmsIntegration"],
    "TestStreamsFunctional": [
        "tests.integration.test_streams_functional",
        "TestStreamsFunctional",
    ],
    "env_path": ["tests.integration.test_wms_connection", "env_path"],
    "logger": ["tests.integration.test_streams_functional", "logger"],
    "real_config": ["tests.integration.test_wms_connection", "real_config"],
    "tap": ["tests.integration.test_wms_connection", "tap"],
    "test_functional": ["tests.integration.test_functional", ""],
    "test_streams_functional": ["tests.integration.test_streams_functional", ""],
    "test_wms": ["tests.integration.test_wms", ""],
    "test_wms_connection": ["tests.integration.test_wms_connection", ""],
}

__all__ = [
    "TestFilteringAndSelection",
    "TestIntegration",
    "TestOracleWMSFunctionalComplete",
    "TestRealConnection",
    "TestRealDataExtraction",
    "TestRealWmsIntegration",
    "TestStreamsFunctional",
    "env_path",
    "logger",
    "real_config",
    "tap",
    "test_functional",
    "test_streams_functional",
    "test_wms",
    "test_wms_connection",
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
