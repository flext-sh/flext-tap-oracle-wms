"""Centralized typings facade for flext-tap-oracle-wms.

- Extends flext-core types
- Add Tap Oracle WMS-specific type aliases and Protocols here


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import E, F, FlextTypes, FlextTypes as CoreFlextTypes, P, R, T, U, V


class FlextTypes(CoreFlextTypes):
    """Tap Oracle WMS domain-specific types can extend here."""


__all__ = [
    "E",
    "F",
    "FlextTypes",
    "P",
    "R",
    "T",
    "U",
    "V",
]
