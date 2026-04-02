# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_tests import d, e, h, r, s, x

    from flext_core import FlextTypes
    from tests import (
        conftest,
        constants,
        e2e,
        integration,
        models,
        performance,
        protocols,
        typings,
        unit,
        utilities,
    )
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
    from tests.e2e import TestOracleWMSE2EComplete, test_e2e
    from tests.integration import (
        TestFilteringAndSelection,
        TestIntegration,
        TestOracleWMSFunctionalComplete,
        TestRealConnection,
        TestRealDataExtraction,
        TestRealWmsIntegration,
        TestStreamsFunctional,
        logger,
        real_config,
        test_functional,
        test_streams_functional,
        test_wms,
        test_wms_connection,
    )
    from tests.models import (
        FlextTapOracleWmsTestModels,
        FlextTapOracleWmsTestModels as m,
    )
    from tests.performance import (
        TestExtractionPerformance,
        TestRateLimitingPerformance,
        env_path,
        performance_config,
        tap,
        test_extraction_performance,
    )
    from tests.protocols import (
        FlextTapOracleWmsTestProtocols,
        FlextTapOracleWmsTestProtocols as p,
    )
    from tests.typings import (
        FlextTapOracleWmsTestTypes,
        FlextTapOracleWmsTestTypes as t,
    )
    from tests.unit import (
        TestCLI,
        TestConfigValidation,
        TestFlextTapOracleWms,
        TestFlextTapOracleWmsSettings,
        TestTapInitialization,
        test_cli,
        test_config,
        test_config_validation,
        test_tap,
        test_tap_initialization,
    )
    from tests.utilities import (
        FlextTapOracleWmsTestUtilities,
        FlextTapOracleWmsTestUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
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
        "d": "flext_tests",
        "e": "flext_tests",
        "e2e": "tests.e2e",
        "h": "flext_tests",
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
        "r": "flext_tests",
        "real_tap_instance": "tests.conftest",
        "reset_environment": "tests.conftest",
        "s": "flext_tests",
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
        "x": "flext_tests",
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
