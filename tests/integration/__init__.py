# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration tests for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.integration import (
        test_functional as test_functional,
        test_streams_functional as test_streams_functional,
        test_wms as test_wms,
        test_wms_connection as test_wms_connection,
    )
    from tests.integration.test_functional import (
        TestOracleWMSFunctionalComplete as TestOracleWMSFunctionalComplete,
    )
    from tests.integration.test_streams_functional import (
        TestStreamsFunctional as TestStreamsFunctional,
        logger as logger,
    )
    from tests.integration.test_wms import (
        TestRealWmsIntegration as TestRealWmsIntegration,
    )
    from tests.integration.test_wms_connection import (
        TestFilteringAndSelection as TestFilteringAndSelection,
        TestIntegration as TestIntegration,
        TestRealConnection as TestRealConnection,
        TestRealDataExtraction as TestRealDataExtraction,
        env_path as env_path,
        real_config as real_config,
        tap as tap,
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

_EXPORTS: Sequence[str] = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
