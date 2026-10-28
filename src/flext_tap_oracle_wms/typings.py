# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT Tap Oracle WMS Types — MRO composition of parent type namespaces.

Singer protocol types come from the inherited ``t.Meltano.*`` namespace.
Oracle WMS domain types come from the inherited ``t.OracleWms.*`` namespace.
This facade composes both via MRO — access as ``t.Meltano.*`` and ``t.OracleWms.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import t as flext_meltano_t
from flext_oracle_wms import t as flext_oracle_wms_t

from flext_tap_oracle_wms._typings import FlextTapOracleWmsTypingsBase


class FlextTapOracleWmsTypes(flext_meltano_t, flext_oracle_wms_t):
    """MRO facade composing Meltano + Oracle WMS type namespaces."""

    class TapOracleWms(FlextTapOracleWmsTypingsBase):
        """Tap Oracle WMS namespace composing the ``_typings`` family base."""


t = FlextTapOracleWmsTypes
__all__: list[str] = ["FlextTapOracleWmsTypes", "t"]
