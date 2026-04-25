"""FLEXT Tap Oracle WMS Types — MRO composition of parent type namespaces.

Singer protocol types come from the inherited ``t.Meltano.*`` namespace.
Oracle WMS domain types come from the inherited ``t.OracleWms.*`` namespace.
This facade composes both via MRO — access as ``t.Meltano.*`` and ``t.OracleWms.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Callable,
)

from flext_meltano import t as meltano_t
from flext_oracle_wms import t

from flext_tap_oracle_wms import m


class FlextTapOracleWmsTypes(meltano_t, t):
    """MRO facade composing Meltano + Oracle WMS type namespaces."""

    type ScalarNormalizer = Callable[[t.JsonValue], t.JsonValue]
    type ContainerValueMapAdapter = m.TypeAdapter[t.JsonMapping]
    type ContainerValueListAdapter = m.TypeAdapter[t.JsonList]

    CONTAINER_VALUE_MAP_ADAPTER: m.TypeAdapter[t.JsonMapping] = m.TypeAdapter(
        t.JsonMapping
    )
    CONTAINER_VALUE_LIST_ADAPTER: m.TypeAdapter[t.JsonList] = m.TypeAdapter(t.JsonList)


t = FlextTapOracleWmsTypes
__all__: list[str] = ["FlextTapOracleWmsTypes", "t"]
