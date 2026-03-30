# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""End-to-end tests for FLEXT Tap Oracle WMS.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.e2e.test_e2e import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "TestOracleWMSE2EComplete": "tests.e2e.test_e2e",
    "logger": "tests.e2e.test_e2e",
    "test_e2e": "tests.e2e.test_e2e",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
