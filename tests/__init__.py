# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""init module.

This module is part of the FLEXT ecosystem. Docstrings follow PEP 257 and Google style.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from tests.conftest import (
        mock_request,
        mock_response,
        mock_wms_client,
        oracle_wms_environment,
        pytest_collection_modifyitems,
        real_config,
        real_tap_instance,
        reset_environment,
        sample_catalog,
        sample_config,
        sample_state,
        tap_instance,
    )
    from tests.constants import (
        TestsFlextTapOracleWmsConstants,
        TestsFlextTapOracleWmsConstants as c,
    )
    from tests.e2e.test_e2e import TestOracleWMSE2EComplete, logger
    from tests.integration.test_functional import TestOracleWMSFunctionalComplete
    from tests.integration.test_streams_functional import (
        TestStreamsFunctional,
        TestWMSPaginatorUnit,
    )
    from tests.integration.test_wms import TestRealWmsIntegration
    from tests.integration.test_wms_connection import (
        TestFilteringAndSelection,
        TestIntegration,
        TestRealConnection,
        TestRealDataExtraction,
        env_path,
        tap,
    )
    from tests.models import TestsFlextTapOracleWmsModels, m, tm
    from tests.performance.test_extraction_performance import (
        TestExtractionPerformance,
        TestRateLimitingPerformance,
        performance_config,
    )
    from tests.protocols import TestsFlextTapOracleWmsProtocols, p
    from tests.typings import (
        TestsFlextTapOracleWmsTypes,
        TestsFlextTapOracleWmsTypes as t,
        tt,
    )
    from tests.unit.test_cli import TestCLI
    from tests.unit.test_config import TestFlextTapOracleWmsSettings
    from tests.unit.test_config_validation import TestConfigValidation
    from tests.unit.test_tap import TestFlextTapOracleWms
    from tests.unit.test_tap_initialization import TestTapInitialization
    from tests.utilities import TestsFlextTapOracleWmsUtilities, u

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestCLI": ("tests.unit.test_cli", "TestCLI"),
    "TestConfigValidation": (
        "tests.unit.test_config_validation",
        "TestConfigValidation",
    ),
    "TestExtractionPerformance": (
        "tests.performance.test_extraction_performance",
        "TestExtractionPerformance",
    ),
    "TestFilteringAndSelection": (
        "tests.integration.test_wms_connection",
        "TestFilteringAndSelection",
    ),
    "TestFlextTapOracleWms": ("tests.unit.test_tap", "TestFlextTapOracleWms"),
    "TestFlextTapOracleWmsSettings": (
        "tests.unit.test_config",
        "TestFlextTapOracleWmsSettings",
    ),
    "TestIntegration": ("tests.integration.test_wms_connection", "TestIntegration"),
    "TestOracleWMSE2EComplete": ("tests.e2e.test_e2e", "TestOracleWMSE2EComplete"),
    "TestOracleWMSFunctionalComplete": (
        "tests.integration.test_functional",
        "TestOracleWMSFunctionalComplete",
    ),
    "TestRateLimitingPerformance": (
        "tests.performance.test_extraction_performance",
        "TestRateLimitingPerformance",
    ),
    "TestRealConnection": (
        "tests.integration.test_wms_connection",
        "TestRealConnection",
    ),
    "TestRealDataExtraction": (
        "tests.integration.test_wms_connection",
        "TestRealDataExtraction",
    ),
    "TestRealWmsIntegration": ("tests.integration.test_wms", "TestRealWmsIntegration"),
    "TestStreamsFunctional": (
        "tests.integration.test_streams_functional",
        "TestStreamsFunctional",
    ),
    "TestTapInitialization": (
        "tests.unit.test_tap_initialization",
        "TestTapInitialization",
    ),
    "TestWMSPaginatorUnit": (
        "tests.integration.test_streams_functional",
        "TestWMSPaginatorUnit",
    ),
    "TestsFlextTapOracleWmsConstants": (
        "tests.constants",
        "TestsFlextTapOracleWmsConstants",
    ),
    "TestsFlextTapOracleWmsModels": ("tests.models", "TestsFlextTapOracleWmsModels"),
    "TestsFlextTapOracleWmsProtocols": (
        "tests.protocols",
        "TestsFlextTapOracleWmsProtocols",
    ),
    "TestsFlextTapOracleWmsTypes": ("tests.typings", "TestsFlextTapOracleWmsTypes"),
    "TestsFlextTapOracleWmsUtilities": (
        "tests.utilities",
        "TestsFlextTapOracleWmsUtilities",
    ),
    "c": ("tests.constants", "TestsFlextTapOracleWmsConstants"),
    "env_path": ("tests.integration.test_wms_connection", "env_path"),
    "logger": ("tests.e2e.test_e2e", "logger"),
    "m": ("tests.models", "m"),
    "mock_request": ("tests.conftest", "mock_request"),
    "mock_response": ("tests.conftest", "mock_response"),
    "mock_wms_client": ("tests.conftest", "mock_wms_client"),
    "oracle_wms_environment": ("tests.conftest", "oracle_wms_environment"),
    "p": ("tests.protocols", "p"),
    "performance_config": (
        "tests.performance.test_extraction_performance",
        "performance_config",
    ),
    "pytest_collection_modifyitems": (
        "tests.conftest",
        "pytest_collection_modifyitems",
    ),
    "real_config": ("tests.conftest", "real_config"),
    "real_tap_instance": ("tests.conftest", "real_tap_instance"),
    "reset_environment": ("tests.conftest", "reset_environment"),
    "sample_catalog": ("tests.conftest", "sample_catalog"),
    "sample_config": ("tests.conftest", "sample_config"),
    "sample_state": ("tests.conftest", "sample_state"),
    "t": ("tests.typings", "TestsFlextTapOracleWmsTypes"),
    "tap": ("tests.integration.test_wms_connection", "tap"),
    "tap_instance": ("tests.conftest", "tap_instance"),
    "tm": ("tests.models", "tm"),
    "tt": ("tests.typings", "tt"),
    "u": ("tests.utilities", "u"),
}

__all__ = [
    "TestCLI",
    "TestConfigValidation",
    "TestExtractionPerformance",
    "TestFilteringAndSelection",
    "TestFlextTapOracleWms",
    "TestFlextTapOracleWmsSettings",
    "TestIntegration",
    "TestOracleWMSE2EComplete",
    "TestOracleWMSFunctionalComplete",
    "TestRateLimitingPerformance",
    "TestRealConnection",
    "TestRealDataExtraction",
    "TestRealWmsIntegration",
    "TestStreamsFunctional",
    "TestTapInitialization",
    "TestWMSPaginatorUnit",
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "c",
    "env_path",
    "logger",
    "m",
    "mock_request",
    "mock_response",
    "mock_wms_client",
    "oracle_wms_environment",
    "p",
    "performance_config",
    "pytest_collection_modifyitems",
    "real_config",
    "real_tap_instance",
    "reset_environment",
    "sample_catalog",
    "sample_config",
    "sample_state",
    "t",
    "tap",
    "tap_instance",
    "tm",
    "tt",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
