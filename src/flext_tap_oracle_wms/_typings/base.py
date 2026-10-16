"""Tap Oracle WMS type alias and adapter declarations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_core import m
from flext_oracle_wms import FlextOracleWmsTypes


class FlextTapOracleWmsTypingsBase:
    """Tap Oracle WMS type aliases and container adapters for ``t``."""

    type ScalarNormalizer = Callable[
        [FlextOracleWmsTypes.JsonValue],
        FlextOracleWmsTypes.JsonValue,
    ]
    type ContainerValueMapAdapter = m.TypeAdapter[FlextOracleWmsTypes.JsonMapping]
    type ContainerValueListAdapter = m.TypeAdapter[FlextOracleWmsTypes.JsonList]

    CONTAINER_VALUE_MAP_ADAPTER: m.TypeAdapter[FlextOracleWmsTypes.JsonMapping] = (
        FlextOracleWmsTypes.json_mapping_adapter()
    )
    CONTAINER_VALUE_LIST_ADAPTER: m.TypeAdapter[FlextOracleWmsTypes.JsonList] = (
        FlextOracleWmsTypes.json_list_adapter()
    )


__all__: list[str] = [
    "FlextTapOracleWmsTypingsBase",
]
