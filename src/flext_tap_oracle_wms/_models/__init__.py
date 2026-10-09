# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Oracle Wms. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_oracle_wms._models.base import FlextTapOracleWmsModelsBase


__all__: tuple[str, ...] = ("FlextTapOracleWmsModelsBase",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextTapOracleWmsModelsBase": ".base"}),
    public_exports=__all__,
)
