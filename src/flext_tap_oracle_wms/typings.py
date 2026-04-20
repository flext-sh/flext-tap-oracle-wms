"""FLEXT Tap Oracle WMS Types — MRO composition of parent type namespaces.

All Singer protocol types are in ``FlextMeltanoTypes.Meltano.*``.
All Oracle WMS domain types are in ``FlextOracleWmsTypes.OracleWms.*``.
This facade composes both via MRO — access as ``t.Meltano.*`` and ``t.OracleWms.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Callable,
)

from flext_meltano import FlextMeltanoTypes
from flext_oracle_wms import FlextOracleWmsTypes
from flext_tap_oracle_wms import m


class FlextTapOracleWmsTypes(FlextMeltanoTypes, FlextOracleWmsTypes):
    """MRO facade composing Meltano + Oracle WMS type namespaces."""

    type ScalarNormalizer = Callable[
        [FlextMeltanoTypes.ContainerValue], FlextMeltanoTypes.Scalar
    ]
    type ContainerValueMapAdapter = m.TypeAdapter[
        FlextMeltanoTypes.ContainerValueMapping
    ]
    type ContainerValueListAdapter = m.TypeAdapter[FlextMeltanoTypes.ContainerValueList]

    CONTAINER_VALUE_MAP_ADAPTER: m.TypeAdapter[
        FlextMeltanoTypes.ContainerValueMapping
    ] = m.TypeAdapter(FlextMeltanoTypes.ContainerValueMapping)
    CONTAINER_VALUE_LIST_ADAPTER: m.TypeAdapter[
        FlextMeltanoTypes.ContainerValueList
    ] = m.TypeAdapter(FlextMeltanoTypes.ContainerValueList)


t = FlextTapOracleWmsTypes
__all__: list[str] = ["FlextTapOracleWmsTypes", "t"]
