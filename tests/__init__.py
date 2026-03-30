# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import d, e, h, r, s, x

    from tests import (
        conftest as conftest,
        constants as constants,
        e2e as e2e,
        integration as integration,
        models as models,
        performance as performance,
        protocols as protocols,
        typings as typings,
        unit as unit,
        utilities as utilities,
    )
    from tests.conftest import (
        mock_request as mock_request,
        mock_response as mock_response,
        mock_wms_client as mock_wms_client,
        oracle_wms_environment as oracle_wms_environment,
        pytest_collection_modifyitems as pytest_collection_modifyitems,
        real_tap_instance as real_tap_instance,
        reset_environment as reset_environment,
        sample_catalog as sample_catalog,
        sample_config as sample_config,
        sample_state as sample_state,
        tap_instance as tap_instance,
        test_config_extraction as test_config_extraction,
    )
    from tests.constants import (
        FlextTapOracleWmsTestConstants as FlextTapOracleWmsTestConstants,
        FlextTapOracleWmsTestConstants as c,
    )
    from tests.e2e import test_e2e as test_e2e
    from tests.e2e.test_e2e import TestOracleWMSE2EComplete as TestOracleWMSE2EComplete
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
        real_config as real_config,
    )
    from tests.models import (
        FlextTapOracleWmsTestModels as FlextTapOracleWmsTestModels,
        FlextTapOracleWmsTestModels as m,
    )
    from tests.performance import (
        test_extraction_performance as test_extraction_performance,
    )
    from tests.performance.test_extraction_performance import (
        TestExtractionPerformance as TestExtractionPerformance,
        TestRateLimitingPerformance as TestRateLimitingPerformance,
        env_path as env_path,
        performance_config as performance_config,
        tap as tap,
    )
    from tests.protocols import (
        FlextTapOracleWmsTestProtocols as FlextTapOracleWmsTestProtocols,
        FlextTapOracleWmsTestProtocols as p,
    )
    from tests.typings import (
        FlextTapOracleWmsTestTypes as FlextTapOracleWmsTestTypes,
        FlextTapOracleWmsTestTypes as t,
    )
    from tests.unit import (
        test_cli as test_cli,
        test_config as test_config,
        test_config_validation as test_config_validation,
        test_tap as test_tap,
        test_tap_initialization as test_tap_initialization,
    )
    from tests.unit.test_cli import TestCLI as TestCLI
    from tests.unit.test_config import (
        TestFlextTapOracleWmsSettings as TestFlextTapOracleWmsSettings,
    )
    from tests.unit.test_config_validation import (
        TestConfigValidation as TestConfigValidation,
    )
    from tests.unit.test_tap import TestFlextTapOracleWms as TestFlextTapOracleWms
    from tests.unit.test_tap_initialization import (
        TestTapInitialization as TestTapInitialization,
    )
    from tests.utilities import (
        FlextTapOracleWmsTestUtilities as FlextTapOracleWmsTestUtilities,
        FlextTapOracleWmsTestUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextTapOracleWmsTestConstants": ["tests.constants", "FlextTapOracleWmsTestConstants"],
    "FlextTapOracleWmsTestModels": ["tests.models", "FlextTapOracleWmsTestModels"],
    "FlextTapOracleWmsTestProtocols": ["tests.protocols", "FlextTapOracleWmsTestProtocols"],
    "FlextTapOracleWmsTestTypes": ["tests.typings", "FlextTapOracleWmsTestTypes"],
    "FlextTapOracleWmsTestUtilities": ["tests.utilities", "FlextTapOracleWmsTestUtilities"],
    "TestCLI": ["tests.unit.test_cli", "TestCLI"],
    "TestConfigValidation": ["tests.unit.test_config_validation", "TestConfigValidation"],
    "TestExtractionPerformance": ["tests.performance.test_extraction_performance", "TestExtractionPerformance"],
    "TestFilteringAndSelection": ["tests.integration.test_wms_connection", "TestFilteringAndSelection"],
    "TestFlextTapOracleWms": ["tests.unit.test_tap", "TestFlextTapOracleWms"],
    "TestFlextTapOracleWmsSettings": ["tests.unit.test_config", "TestFlextTapOracleWmsSettings"],
    "TestIntegration": ["tests.integration.test_wms_connection", "TestIntegration"],
    "TestOracleWMSE2EComplete": ["tests.e2e.test_e2e", "TestOracleWMSE2EComplete"],
    "TestOracleWMSFunctionalComplete": ["tests.integration.test_functional", "TestOracleWMSFunctionalComplete"],
    "TestRateLimitingPerformance": ["tests.performance.test_extraction_performance", "TestRateLimitingPerformance"],
    "TestRealConnection": ["tests.integration.test_wms_connection", "TestRealConnection"],
    "TestRealDataExtraction": ["tests.integration.test_wms_connection", "TestRealDataExtraction"],
    "TestRealWmsIntegration": ["tests.integration.test_wms", "TestRealWmsIntegration"],
    "TestStreamsFunctional": ["tests.integration.test_streams_functional", "TestStreamsFunctional"],
    "TestTapInitialization": ["tests.unit.test_tap_initialization", "TestTapInitialization"],
    "c": ["tests.constants", "FlextTapOracleWmsTestConstants"],
    "conftest": ["tests.conftest", ""],
    "constants": ["tests.constants", ""],
    "d": ["flext_tests", "d"],
    "e": ["flext_tests", "e"],
    "e2e": ["tests.e2e", ""],
    "env_path": ["tests.performance.test_extraction_performance", "env_path"],
    "h": ["flext_tests", "h"],
    "integration": ["tests.integration", ""],
    "logger": ["tests.integration.test_streams_functional", "logger"],
    "m": ["tests.models", "FlextTapOracleWmsTestModels"],
    "mock_request": ["tests.conftest", "mock_request"],
    "mock_response": ["tests.conftest", "mock_response"],
    "mock_wms_client": ["tests.conftest", "mock_wms_client"],
    "models": ["tests.models", ""],
    "oracle_wms_environment": ["tests.conftest", "oracle_wms_environment"],
    "p": ["tests.protocols", "FlextTapOracleWmsTestProtocols"],
    "performance": ["tests.performance", ""],
    "performance_config": ["tests.performance.test_extraction_performance", "performance_config"],
    "protocols": ["tests.protocols", ""],
    "pytest_collection_modifyitems": ["tests.conftest", "pytest_collection_modifyitems"],
    "r": ["flext_tests", "r"],
    "real_config": ["tests.integration.test_wms_connection", "real_config"],
    "real_tap_instance": ["tests.conftest", "real_tap_instance"],
    "reset_environment": ["tests.conftest", "reset_environment"],
    "s": ["flext_tests", "s"],
    "sample_catalog": ["tests.conftest", "sample_catalog"],
    "sample_config": ["tests.conftest", "sample_config"],
    "sample_state": ["tests.conftest", "sample_state"],
    "t": ["tests.typings", "FlextTapOracleWmsTestTypes"],
    "tap": ["tests.performance.test_extraction_performance", "tap"],
    "tap_instance": ["tests.conftest", "tap_instance"],
    "test_cli": ["tests.unit.test_cli", ""],
    "test_config": ["tests.unit.test_config", ""],
    "test_config_extraction": ["tests.conftest", "test_config_extraction"],
    "test_config_validation": ["tests.unit.test_config_validation", ""],
    "test_e2e": ["tests.e2e.test_e2e", ""],
    "test_extraction_performance": ["tests.performance.test_extraction_performance", ""],
    "test_functional": ["tests.integration.test_functional", ""],
    "test_streams_functional": ["tests.integration.test_streams_functional", ""],
    "test_tap": ["tests.unit.test_tap", ""],
    "test_tap_initialization": ["tests.unit.test_tap_initialization", ""],
    "test_wms": ["tests.integration.test_wms", ""],
    "test_wms_connection": ["tests.integration.test_wms_connection", ""],
    "typings": ["tests.typings", ""],
    "u": ["tests.utilities", "FlextTapOracleWmsTestUtilities"],
    "unit": ["tests.unit", ""],
    "utilities": ["tests.utilities", ""],
    "x": ["flext_tests", "x"],
}

_EXPORTS: Sequence[str] = [
    "FlextTapOracleWmsTestConstants",
    "FlextTapOracleWmsTestModels",
    "FlextTapOracleWmsTestProtocols",
    "FlextTapOracleWmsTestTypes",
    "FlextTapOracleWmsTestUtilities",
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
    "c",
    "conftest",
    "constants",
    "d",
    "e",
    "e2e",
    "env_path",
    "h",
    "integration",
    "logger",
    "m",
    "mock_request",
    "mock_response",
    "mock_wms_client",
    "models",
    "oracle_wms_environment",
    "p",
    "performance",
    "performance_config",
    "protocols",
    "pytest_collection_modifyitems",
    "r",
    "real_config",
    "real_tap_instance",
    "reset_environment",
    "s",
    "sample_catalog",
    "sample_config",
    "sample_state",
    "t",
    "tap",
    "tap_instance",
    "test_cli",
    "test_config",
    "test_config_extraction",
    "test_config_validation",
    "test_e2e",
    "test_extraction_performance",
    "test_functional",
    "test_streams_functional",
    "test_tap",
    "test_tap_initialization",
    "test_wms",
    "test_wms_connection",
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
