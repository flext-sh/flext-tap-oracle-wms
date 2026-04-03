# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_tap_oracle_wms import (
        conftest,
        constants,
        e2e,
        integration,
        models,
        performance,
        protocols,
        test_cli,
        test_config,
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
        unit,
        utilities,
    )
    from flext_tap_oracle_wms.conftest import (
        mock_request,
        mock_response,
        mock_wms_client,
        oracle_wms_environment,
        real_tap_instance,
        reset_environment,
        sample_catalog,
        sample_config,
        sample_state,
        tap_instance,
        test_config_extraction,
    )
    from flext_tap_oracle_wms.constants import (
        FlextTapOracleWmsTestConstants,
        FlextTapOracleWmsTestConstants as c,
    )
    from flext_tap_oracle_wms.e2e import TestOracleWMSE2EComplete
    from flext_tap_oracle_wms.integration import (
        TestOracleWMSFunctionalComplete,
        TestRealWmsIntegration,
        TestStreamsFunctional,
        logger,
        real_config,
    )
    from flext_tap_oracle_wms.models import (
        FlextTapOracleWmsTestModels,
        FlextTapOracleWmsTestModels as m,
    )
    from flext_tap_oracle_wms.performance import (
        TestExtractionPerformance,
        TestRateLimitingPerformance,
        env_path,
        performance_config,
        tap,
    )
    from flext_tap_oracle_wms.protocols import (
        FlextTapOracleWmsTestProtocols,
        FlextTapOracleWmsTestProtocols as p,
    )
    from flext_tap_oracle_wms.typings import (
        FlextTapOracleWmsTestTypes,
        FlextTapOracleWmsTestTypes as t,
    )
    from flext_tap_oracle_wms.unit import (
        TestCLI,
        TestConfigValidation,
        TestFlextTapOracleWms,
        TestFlextTapOracleWmsSettings,
        TestTapInitialization,
    )
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsTestUtilities,
        FlextTapOracleWmsTestUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
    (
        "flext_tap_oracle_wms.e2e",
        "flext_tap_oracle_wms.integration",
        "flext_tap_oracle_wms.performance",
        "flext_tap_oracle_wms.unit",
    ),
    {
        "FlextTapOracleWmsTestConstants": "flext_tap_oracle_wms.constants",
        "FlextTapOracleWmsTestModels": "flext_tap_oracle_wms.models",
        "FlextTapOracleWmsTestProtocols": "flext_tap_oracle_wms.protocols",
        "FlextTapOracleWmsTestTypes": "flext_tap_oracle_wms.typings",
        "FlextTapOracleWmsTestUtilities": "flext_tap_oracle_wms.utilities",
        "c": ("flext_tap_oracle_wms.constants", "FlextTapOracleWmsTestConstants"),
        "conftest": "flext_tap_oracle_wms.conftest",
        "constants": "flext_tap_oracle_wms.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "e2e": "flext_tap_oracle_wms.e2e",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "integration": "flext_tap_oracle_wms.integration",
        "m": ("flext_tap_oracle_wms.models", "FlextTapOracleWmsTestModels"),
        "mock_request": "flext_tap_oracle_wms.conftest",
        "mock_response": "flext_tap_oracle_wms.conftest",
        "mock_wms_client": "flext_tap_oracle_wms.conftest",
        "models": "flext_tap_oracle_wms.models",
        "oracle_wms_environment": "flext_tap_oracle_wms.conftest",
        "p": ("flext_tap_oracle_wms.protocols", "FlextTapOracleWmsTestProtocols"),
        "performance": "flext_tap_oracle_wms.performance",
        "protocols": "flext_tap_oracle_wms.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "real_tap_instance": "flext_tap_oracle_wms.conftest",
        "reset_environment": "flext_tap_oracle_wms.conftest",
        "s": ("flext_core.service", "FlextService"),
        "sample_catalog": "flext_tap_oracle_wms.conftest",
        "sample_config": "flext_tap_oracle_wms.conftest",
        "sample_state": "flext_tap_oracle_wms.conftest",
        "t": ("flext_tap_oracle_wms.typings", "FlextTapOracleWmsTestTypes"),
        "tap_instance": "flext_tap_oracle_wms.conftest",
        "test_cli": "flext_tap_oracle_wms.test_cli",
        "test_config": "flext_tap_oracle_wms.test_config",
        "test_config_extraction": "flext_tap_oracle_wms.conftest",
        "test_config_validation": "flext_tap_oracle_wms.test_config_validation",
        "test_e2e": "flext_tap_oracle_wms.test_e2e",
        "test_extraction_performance": "flext_tap_oracle_wms.test_extraction_performance",
        "test_functional": "flext_tap_oracle_wms.test_functional",
        "test_streams_functional": "flext_tap_oracle_wms.test_streams_functional",
        "test_tap": "flext_tap_oracle_wms.test_tap",
        "test_tap_initialization": "flext_tap_oracle_wms.test_tap_initialization",
        "test_wms": "flext_tap_oracle_wms.test_wms",
        "test_wms_connection": "flext_tap_oracle_wms.test_wms_connection",
        "typings": "flext_tap_oracle_wms.typings",
        "u": ("flext_tap_oracle_wms.utilities", "FlextTapOracleWmsTestUtilities"),
        "unit": "flext_tap_oracle_wms.unit",
        "utilities": "flext_tap_oracle_wms.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
