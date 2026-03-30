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

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = merge_lazy_imports(
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
