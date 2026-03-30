# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import *

    from tests import conftest, constants, models, protocols, typings, utilities
    from tests.conftest import *
    from tests.constants import *
    from tests.e2e import *
    from tests.integration import *
    from tests.models import *
    from tests.performance import *
    from tests.protocols import *
    from tests.typings import *
    from tests.unit import *
    from tests.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextTapOracleWmsTestConstants": "tests.constants",
    "FlextTapOracleWmsTestModels": "tests.models",
    "FlextTapOracleWmsTestProtocols": "tests.protocols",
    "FlextTapOracleWmsTestTypes": "tests.typings",
    "FlextTapOracleWmsTestUtilities": "tests.utilities",
    "TestCLI": "tests.unit.test_cli",
    "TestConfigValidation": "tests.unit.test_config_validation",
    "TestExtractionPerformance": "tests.performance.test_extraction_performance",
    "TestFilteringAndSelection": "tests.integration.test_wms_connection",
    "TestFlextTapOracleWms": "tests.unit.test_tap",
    "TestFlextTapOracleWmsSettings": "tests.unit.test_config",
    "TestIntegration": "tests.integration.test_wms_connection",
    "TestOracleWMSE2EComplete": "tests.e2e.test_e2e",
    "TestOracleWMSFunctionalComplete": "tests.integration.test_functional",
    "TestRateLimitingPerformance": "tests.performance.test_extraction_performance",
    "TestRealConnection": "tests.integration.test_wms_connection",
    "TestRealDataExtraction": "tests.integration.test_wms_connection",
    "TestRealWmsIntegration": "tests.integration.test_wms",
    "TestStreamsFunctional": "tests.integration.test_streams_functional",
    "TestTapInitialization": "tests.unit.test_tap_initialization",
    "c": ["tests.constants", "FlextTapOracleWmsTestConstants"],
    "conftest": "tests.conftest",
    "constants": "tests.constants",
    "d": "flext_tests",
    "e": "flext_tests",
    "e2e": "tests.e2e",
    "env_path": "tests.performance.test_extraction_performance",
    "h": "flext_tests",
    "integration": "tests.integration",
    "logger": "tests.integration.test_streams_functional",
    "m": ["tests.models", "FlextTapOracleWmsTestModels"],
    "mock_request": "tests.conftest",
    "mock_response": "tests.conftest",
    "mock_wms_client": "tests.conftest",
    "models": "tests.models",
    "oracle_wms_environment": "tests.conftest",
    "p": ["tests.protocols", "FlextTapOracleWmsTestProtocols"],
    "performance": "tests.performance",
    "performance_config": "tests.performance.test_extraction_performance",
    "protocols": "tests.protocols",
    "pytest_collection_modifyitems": "tests.conftest",
    "r": "flext_tests",
    "real_config": "tests.integration.test_wms_connection",
    "real_tap_instance": "tests.conftest",
    "reset_environment": "tests.conftest",
    "s": "flext_tests",
    "sample_catalog": "tests.conftest",
    "sample_config": "tests.conftest",
    "sample_state": "tests.conftest",
    "t": ["tests.typings", "FlextTapOracleWmsTestTypes"],
    "tap": "tests.performance.test_extraction_performance",
    "tap_instance": "tests.conftest",
    "test_cli": "tests.unit.test_cli",
    "test_config": "tests.unit.test_config",
    "test_config_extraction": "tests.conftest",
    "test_config_validation": "tests.unit.test_config_validation",
    "test_e2e": "tests.e2e.test_e2e",
    "test_extraction_performance": "tests.performance.test_extraction_performance",
    "test_functional": "tests.integration.test_functional",
    "test_streams_functional": "tests.integration.test_streams_functional",
    "test_tap": "tests.unit.test_tap",
    "test_tap_initialization": "tests.unit.test_tap_initialization",
    "test_wms": "tests.integration.test_wms",
    "test_wms_connection": "tests.integration.test_wms_connection",
    "typings": "tests.typings",
    "u": ["tests.utilities", "FlextTapOracleWmsTestUtilities"],
    "unit": "tests.unit",
    "utilities": "tests.utilities",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
