# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_core.mixins import FlextMixins as x
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from tests.conftest import (
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
    test_config_extraction,
)
from tests.constants import (
    FlextTapOracleWmsTestConstants,
    FlextTapOracleWmsTestConstants as c,
)
from tests.e2e.test_e2e import TestOracleWMSE2EComplete
from tests.integration.test_functional import TestOracleWMSFunctionalComplete
from tests.integration.test_streams_functional import TestStreamsFunctional, logger
from tests.integration.test_wms import TestRealWmsIntegration
from tests.integration.test_wms_connection import (
    TestFilteringAndSelection,
    TestIntegration,
    TestRealConnection,
    TestRealDataExtraction,
    real_config,
)
from tests.models import (
    FlextTapOracleWmsTestModels,
    FlextTapOracleWmsTestModels as m,
)
from tests.performance.test_extraction_performance import (
    TestExtractionPerformance,
    TestRateLimitingPerformance,
    env_path,
    performance_config,
    tap,
)
from tests.protocols import (
    FlextTapOracleWmsTestProtocols,
    FlextTapOracleWmsTestProtocols as p,
)
from tests.typings import (
    FlextTapOracleWmsTestTypes,
    FlextTapOracleWmsTestTypes as t,
)
from tests.unit.test_cli import TestCLI
from tests.unit.test_config import TestFlextTapOracleWmsSettings
from tests.unit.test_config_validation import TestConfigValidation
from tests.unit.test_tap import TestFlextTapOracleWms
from tests.unit.test_tap_initialization import TestTapInitialization
from tests.utilities import (
    FlextTapOracleWmsTestUtilities,
    FlextTapOracleWmsTestUtilities as u,
)

if _t.TYPE_CHECKING:
    import tests.conftest as _tests_conftest

    conftest = _tests_conftest
    import tests.constants as _tests_constants

    constants = _tests_constants
    import tests.e2e as _tests_e2e

    e2e = _tests_e2e
    import tests.e2e.test_e2e as _tests_e2e_test_e2e

    test_e2e = _tests_e2e_test_e2e
    import tests.integration as _tests_integration

    integration = _tests_integration
    import tests.integration.test_functional as _tests_integration_test_functional

    test_functional = _tests_integration_test_functional
    import tests.integration.test_streams_functional as _tests_integration_test_streams_functional

    test_streams_functional = _tests_integration_test_streams_functional
    import tests.integration.test_wms as _tests_integration_test_wms

    test_wms = _tests_integration_test_wms
    import tests.integration.test_wms_connection as _tests_integration_test_wms_connection

    test_wms_connection = _tests_integration_test_wms_connection
    import tests.models as _tests_models

    models = _tests_models
    import tests.performance as _tests_performance

    performance = _tests_performance
    import tests.performance.test_extraction_performance as _tests_performance_test_extraction_performance

    test_extraction_performance = _tests_performance_test_extraction_performance
    import tests.protocols as _tests_protocols

    protocols = _tests_protocols
    import tests.typings as _tests_typings

    typings = _tests_typings
    import tests.unit as _tests_unit

    unit = _tests_unit
    import tests.unit.test_cli as _tests_unit_test_cli

    test_cli = _tests_unit_test_cli
    import tests.unit.test_config as _tests_unit_test_config

    test_config = _tests_unit_test_config
    import tests.unit.test_config_validation as _tests_unit_test_config_validation

    test_config_validation = _tests_unit_test_config_validation
    import tests.unit.test_tap as _tests_unit_test_tap

    test_tap = _tests_unit_test_tap
    import tests.unit.test_tap_initialization as _tests_unit_test_tap_initialization

    test_tap_initialization = _tests_unit_test_tap_initialization
    import tests.utilities as _tests_utilities

    utilities = _tests_utilities

    _ = (
        FlextTapOracleWmsTestConstants,
        FlextTapOracleWmsTestModels,
        FlextTapOracleWmsTestProtocols,
        FlextTapOracleWmsTestTypes,
        FlextTapOracleWmsTestUtilities,
        TestCLI,
        TestConfigValidation,
        TestExtractionPerformance,
        TestFilteringAndSelection,
        TestFlextTapOracleWms,
        TestFlextTapOracleWmsSettings,
        TestIntegration,
        TestOracleWMSE2EComplete,
        TestOracleWMSFunctionalComplete,
        TestRateLimitingPerformance,
        TestRealConnection,
        TestRealDataExtraction,
        TestRealWmsIntegration,
        TestStreamsFunctional,
        TestTapInitialization,
        c,
        conftest,
        constants,
        d,
        e,
        e2e,
        env_path,
        h,
        integration,
        logger,
        m,
        mock_request,
        mock_response,
        mock_wms_client,
        models,
        oracle_wms_environment,
        p,
        performance,
        performance_config,
        protocols,
        pytest_collection_modifyitems,
        r,
        real_config,
        real_tap_instance,
        reset_environment,
        s,
        sample_catalog,
        sample_config,
        sample_state,
        t,
        tap,
        tap_instance,
        test_cli,
        test_config,
        test_config_extraction,
        test_config_validation,
        test_e2e,
        test_extraction_performance,
        test_functional,
        test_streams_functional,
        test_tap,
        test_tap_initialization,
        test_wms,
        test_wms_connection,
        typings,
        u,
        unit,
        utilities,
        x,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "tests.e2e",
        "tests.integration",
        "tests.performance",
        "tests.unit",
    ),
    {
        "FlextTapOracleWmsTestConstants": "tests.constants",
        "FlextTapOracleWmsTestModels": "tests.models",
        "FlextTapOracleWmsTestProtocols": "tests.protocols",
        "FlextTapOracleWmsTestTypes": "tests.typings",
        "FlextTapOracleWmsTestUtilities": "tests.utilities",
        "c": ("tests.constants", "FlextTapOracleWmsTestConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "e2e": "tests.e2e",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "integration": "tests.integration",
        "m": ("tests.models", "FlextTapOracleWmsTestModels"),
        "mock_request": "tests.conftest",
        "mock_response": "tests.conftest",
        "mock_wms_client": "tests.conftest",
        "models": "tests.models",
        "oracle_wms_environment": "tests.conftest",
        "p": ("tests.protocols", "FlextTapOracleWmsTestProtocols"),
        "performance": "tests.performance",
        "protocols": "tests.protocols",
        "pytest_collection_modifyitems": "tests.conftest",
        "r": ("flext_core.result", "FlextResult"),
        "real_tap_instance": "tests.conftest",
        "reset_environment": "tests.conftest",
        "s": ("flext_core.service", "FlextService"),
        "sample_catalog": "tests.conftest",
        "sample_config": "tests.conftest",
        "sample_state": "tests.conftest",
        "t": ("tests.typings", "FlextTapOracleWmsTestTypes"),
        "tap_instance": "tests.conftest",
        "test_config_extraction": "tests.conftest",
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextTapOracleWmsTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)

__all__ = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
