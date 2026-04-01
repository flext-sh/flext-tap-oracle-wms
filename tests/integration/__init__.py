# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration tests for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes

    from tests.integration.test_functional import *
    from tests.integration.test_streams_functional import *
    from tests.integration.test_wms import *
    from tests.integration.test_wms_connection import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "TestFilteringAndSelection": "tests.integration.test_wms_connection",
    "TestIntegration": "tests.integration.test_wms_connection",
    "TestOracleWMSFunctionalComplete": "tests.integration.test_functional",
    "TestRealConnection": "tests.integration.test_wms_connection",
    "TestRealDataExtraction": "tests.integration.test_wms_connection",
    "TestRealWmsIntegration": "tests.integration.test_wms",
    "TestStreamsFunctional": "tests.integration.test_streams_functional",
    "env_path": "tests.integration.test_wms_connection",
    "logger": "tests.integration.test_streams_functional",
    "real_config": "tests.integration.test_wms_connection",
    "tap": "tests.integration.test_wms_connection",
    "test_functional": "tests.integration.test_functional",
    "test_streams_functional": "tests.integration.test_streams_functional",
    "test_wms": "tests.integration.test_wms",
    "test_wms_connection": "tests.integration.test_wms_connection",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
