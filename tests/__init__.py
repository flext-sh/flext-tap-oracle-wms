# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from . import (
        e2e as e2e,
        integration as integration,
        performance as performance,
        unit as unit,
    )
    from .conftest import (
        mock_request,
        mock_response,
        mock_wms_client,
        oracle_wms_environment,
        pytest_collection_modifyitems,
        real_tap_instance,
        reset_environment,
        sample_catalog,
        sample_config,
        sample_state,
        tap_instance,
    )
    from .constants import (
        TestsFlextTapOracleWmsConstants,
        TestsFlextTapOracleWmsConstants as c,
    )
    from .e2e.test_e2e import TestOracleWMSE2EComplete
    from .integration.test_functional import TestOracleWMSFunctionalComplete
    from .integration.test_streams_functional import (
        TestStreamsFunctional,
        TestWMSPaginatorUnit,
        logger,
    )
    from .integration.test_wms import TestRealWmsIntegration
    from .integration.test_wms_connection import (
        TestFilteringAndSelection,
        TestIntegration,
        TestRealConnection,
        TestRealDataExtraction,
        real_config,
    )
    from .models import (
        TestsFlextTapOracleWmsModels,
        TestsFlextTapOracleWmsModels as m,
        tm,
    )
    from .performance.test_extraction_performance import (
        TestExtractionPerformance,
        TestRateLimitingPerformance,
        env_path,
        performance_config,
        tap,
    )
    from .protocols import (
        TestsFlextTapOracleWmsProtocols,
        TestsFlextTapOracleWmsProtocols as p,
    )
    from .typings import (
        TestsFlextTapOracleWmsTypes,
        TestsFlextTapOracleWmsTypes as t,
        tt,
    )
    from .unit.test_cli import TestCLI
    from .unit.test_config import TestFlextTapOracleWmsSettings
    from .unit.test_config_validation import TestConfigValidation
    from .unit.test_tap import TestFlextTapOracleWms
    from .unit.test_tap_initialization import TestTapInitialization
    from .utilities import (
        TestsFlextTapOracleWmsUtilities,
        TestsFlextTapOracleWmsUtilities as u,
    )

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
    "e2e": ("tests.e2e", ""),
    "env_path": ("tests.performance.test_extraction_performance", "env_path"),
    "integration": ("tests.integration", ""),
    "logger": ("tests.integration.test_streams_functional", "logger"),
    "m": ("tests.models", "TestsFlextTapOracleWmsModels"),
    "mock_request": ("tests.conftest", "mock_request"),
    "mock_response": ("tests.conftest", "mock_response"),
    "mock_wms_client": ("tests.conftest", "mock_wms_client"),
    "oracle_wms_environment": ("tests.conftest", "oracle_wms_environment"),
    "p": ("tests.protocols", "TestsFlextTapOracleWmsProtocols"),
    "performance": ("tests.performance", ""),
    "performance_config": (
        "tests.performance.test_extraction_performance",
        "performance_config",
    ),
    "pytest_collection_modifyitems": (
        "tests.conftest",
        "pytest_collection_modifyitems",
    ),
    "real_config": ("tests.integration.test_wms_connection", "real_config"),
    "real_tap_instance": ("tests.conftest", "real_tap_instance"),
    "reset_environment": ("tests.conftest", "reset_environment"),
    "sample_catalog": ("tests.conftest", "sample_catalog"),
    "sample_config": ("tests.conftest", "sample_config"),
    "sample_state": ("tests.conftest", "sample_state"),
    "t": ("tests.typings", "TestsFlextTapOracleWmsTypes"),
    "tap": ("tests.performance.test_extraction_performance", "tap"),
    "tap_instance": ("tests.conftest", "tap_instance"),
    "tm": ("tests.models", "tm"),
    "tt": ("tests.typings", "tt"),
    "u": ("tests.utilities", "TestsFlextTapOracleWmsUtilities"),
    "unit": ("tests.unit", ""),
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
    "e2e",
    "env_path",
    "integration",
    "logger",
    "m",
    "mock_request",
    "mock_response",
    "mock_wms_client",
    "oracle_wms_environment",
    "p",
    "performance",
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
    "unit",
]


_LAZY_CACHE: dict[str, object] = {}


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


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
