# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from flext_tap_oracle_wms import (
        test_functional,
        test_streams_functional,
        test_wms,
        test_wms_connection,
    )
    from flext_tap_oracle_wms.test_functional import TestOracleWMSFunctionalComplete
    from flext_tap_oracle_wms.test_streams_functional import (
        TestStreamsFunctional,
        logger,
    )
    from flext_tap_oracle_wms.test_wms import TestRealWmsIntegration
    from flext_tap_oracle_wms.test_wms_connection import env_path, real_config, tap

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "TestOracleWMSFunctionalComplete": "flext_tap_oracle_wms.test_functional",
    "TestRealWmsIntegration": "flext_tap_oracle_wms.test_wms",
    "TestStreamsFunctional": "flext_tap_oracle_wms.test_streams_functional",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "env_path": "flext_tap_oracle_wms.test_wms_connection",
    "h": ("flext_core.handlers", "FlextHandlers"),
    "logger": "flext_tap_oracle_wms.test_streams_functional",
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "real_config": "flext_tap_oracle_wms.test_wms_connection",
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "tap": "flext_tap_oracle_wms.test_wms_connection",
    "test_functional": "flext_tap_oracle_wms.test_functional",
    "test_streams_functional": "flext_tap_oracle_wms.test_streams_functional",
    "test_wms": "flext_tap_oracle_wms.test_wms",
    "test_wms_connection": "flext_tap_oracle_wms.test_wms_connection",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
