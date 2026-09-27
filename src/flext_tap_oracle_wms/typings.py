"""FLEXT Tap Oracle WMS Types — MRO composition of parent type namespaces.

Singer protocol types come from the inherited ``t.Meltano.*`` namespace.
Oracle WMS domain types come from the inherited ``t.OracleWms.*`` namespace.
This facade composes both via MRO — access as ``t.Meltano.*`` and ``t.OracleWms.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_meltano import FlextMeltanoTypes
from flext_oracle_wms import FlextOracleWmsTypes

from flext_tap_oracle_wms import m


class FlextTapOracleWmsTypes(FlextMeltanoTypes, FlextOracleWmsTypes):
    """MRO facade composing Meltano + Oracle WMS type namespaces."""

    type ScalarNormalizer = Callable[
        [FlextOracleWmsTypes.JsonValue], FlextOracleWmsTypes.JsonValue
    ]
    type ContainerValueMapAdapter = m.TypeAdapter[FlextOracleWmsTypes.JsonMapping]
    type ContainerValueListAdapter = m.TypeAdapter[FlextOracleWmsTypes.JsonList]

    CONTAINER_VALUE_MAP_ADAPTER: m.TypeAdapter[FlextOracleWmsTypes.JsonMapping] = (
        FlextOracleWmsTypes.json_mapping_adapter()
    )
    CONTAINER_VALUE_LIST_ADAPTER: m.TypeAdapter[FlextOracleWmsTypes.JsonList] = (
        FlextOracleWmsTypes.json_list_adapter()
    )


t = FlextTapOracleWmsTypes
__all__: list[str] = ["FlextTapOracleWmsTypes", "t"]
