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
    from tests.conftest import *
    from tests.constants import *
    from tests.e2e import test_e2e
    from tests.e2e.test_e2e import *
    from tests.integration import (
        test_functional,
        test_streams_functional,
        test_wms,
        test_wms_connection,
    )
    from tests.integration.test_functional import *
    from tests.integration.test_streams_functional import *
    from tests.integration.test_wms import *
    from tests.integration.test_wms_connection import *
    from tests.models import *
    from tests.performance import test_extraction_performance
    from tests.performance.test_extraction_performance import *
    from tests.protocols import *
    from tests.typings import *
    from tests.unit import (
        test_cli,
        test_config,
        test_config_validation,
        test_tap,
        test_tap_initialization,
    )
    from tests.unit.test_cli import *
    from tests.unit.test_config import *
    from tests.unit.test_config_validation import *
    from tests.unit.test_tap import *
    from tests.unit.test_tap_initialization import *
    from tests.utilities import *

from tests.e2e import _LAZY_IMPORTS as _E2E_LAZY
from tests.integration import _LAZY_IMPORTS as _INTEGRATION_LAZY
from tests.performance import _LAZY_IMPORTS as _PERFORMANCE_LAZY
from tests.unit import _LAZY_IMPORTS as _UNIT_LAZY

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    **_E2E_LAZY,
    **_INTEGRATION_LAZY,
    **_PERFORMANCE_LAZY,
    **_UNIT_LAZY,
    "FlextTapOracleWmsTestConstants": "tests.constants",
    "FlextTapOracleWmsTestModels": "tests.models",
    "FlextTapOracleWmsTestProtocols": "tests.protocols",
    "FlextTapOracleWmsTestTypes": "tests.typings",
    "FlextTapOracleWmsTestUtilities": "tests.utilities",
    "c": ["tests.constants", "FlextTapOracleWmsTestConstants"],
    "conftest": "tests.conftest",
    "constants": "tests.constants",
    "d": "flext_tests",
    "e": "flext_tests",
    "e2e": "tests.e2e",
    "h": "flext_tests",
    "integration": "tests.integration",
    "m": ["tests.models", "FlextTapOracleWmsTestModels"],
    "mock_request": "tests.conftest",
    "mock_response": "tests.conftest",
    "mock_wms_client": "tests.conftest",
    "models": "tests.models",
    "oracle_wms_environment": "tests.conftest",
    "p": ["tests.protocols", "FlextTapOracleWmsTestProtocols"],
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
    "t": ["tests.typings", "FlextTapOracleWmsTestTypes"],
    "tap_instance": "tests.conftest",
    "test_config_extraction": "tests.conftest",
    "typings": "tests.typings",
    "u": ["tests.utilities", "FlextTapOracleWmsTestUtilities"],
    "unit": "tests.unit",
    "utilities": "tests.utilities",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
