# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_meltano import s
    from flext_oracle_wms import e

    from examples.constants import ExamplesFlextTapOracleWmsConstants
    from examples.models import ExamplesFlextTapOracleWmsModels
    from examples.protocols import ExamplesFlextTapOracleWmsProtocols
    from examples.typings import ExamplesFlextTapOracleWmsTypes
    from examples.utilities import ExamplesFlextTapOracleWmsUtilities, u
    from flext_tap_oracle_wms import c, d, h, m, p, r, t, x


__all__: tuple[str, ...] = (
    "ExamplesFlextTapOracleWmsConstants",
    "ExamplesFlextTapOracleWmsModels",
    "ExamplesFlextTapOracleWmsProtocols",
    "ExamplesFlextTapOracleWmsTypes",
    "ExamplesFlextTapOracleWmsUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "ExamplesFlextTapOracleWmsConstants": ".constants",
        "ExamplesFlextTapOracleWmsModels": ".models",
        "ExamplesFlextTapOracleWmsProtocols": ".protocols",
        "ExamplesFlextTapOracleWmsTypes": ".typings",
        "ExamplesFlextTapOracleWmsUtilities": ".utilities",
        "c": "flext_tap_oracle_wms",
        "d": "flext_tap_oracle_wms",
        "e": "flext_oracle_wms",
        "h": "flext_tap_oracle_wms",
        "m": "flext_tap_oracle_wms",
        "p": "flext_tap_oracle_wms",
        "r": "flext_tap_oracle_wms",
        "s": "flext_meltano",
        "t": "flext_tap_oracle_wms",
        "u": ".utilities",
        "x": "flext_tap_oracle_wms",
    }),
    public_exports=__all__,
)
