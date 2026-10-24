"""FLEXT Tap Oracle WMS Types — MRO composition of parent type namespaces.

Singer protocol types come from the inherited ``t.Meltano.*`` namespace.
Oracle WMS domain types come from the inherited ``t.OracleWms.*`` namespace.
This facade composes both via MRO — access as ``t.Meltano.*`` and ``t.OracleWms.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import FlextMeltanoTypes
from flext_oracle_wms import FlextOracleWmsTypes

from flext_tap_oracle_wms._typings.base import FlextTapOracleWmsTypingsBase


class FlextTapOracleWmsTypes(FlextMeltanoTypes, FlextOracleWmsTypes):
    """MRO facade composing Meltano + Oracle WMS type namespaces."""

    ScalarNormalizer = FlextTapOracleWmsTypingsBase.ScalarNormalizer
    ContainerValueMapAdapter = FlextTapOracleWmsTypingsBase.ContainerValueMapAdapter
    ContainerValueListAdapter = FlextTapOracleWmsTypingsBase.ContainerValueListAdapter

    CONTAINER_VALUE_MAP_ADAPTER = (
        FlextTapOracleWmsTypingsBase.CONTAINER_VALUE_MAP_ADAPTER
    )
    CONTAINER_VALUE_LIST_ADAPTER = (
        FlextTapOracleWmsTypingsBase.CONTAINER_VALUE_LIST_ADAPTER
    )


t = FlextTapOracleWmsTypes
__all__: list[str] = ["FlextTapOracleWmsTypes", "t"]
