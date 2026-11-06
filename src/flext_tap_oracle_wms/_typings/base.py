"""Tap Oracle WMS type alias and adapter declarations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_oracle_wms import t, u


class FlextTapOracleWmsTypingsBase:
    """Tap Oracle WMS type aliases and container adapters for ``t``."""

    type ScalarNormalizer = Callable[
        [t.JsonValue],
        t.JsonValue,
    ]
    type ContainerValueMapAdapter = t.TypeAdapter[t.JsonMapping]
    type ContainerValueListAdapter = t.TypeAdapter[t.JsonList]

    CONTAINER_VALUE_MAP_ADAPTER: t.TypeAdapter[t.JsonMapping] = u.json_mapping_adapter()
    CONTAINER_VALUE_LIST_ADAPTER: t.TypeAdapter[t.JsonList] = u.json_list_adapter()


__all__: list[str] = [
    "FlextTapOracleWmsTypingsBase",
]
