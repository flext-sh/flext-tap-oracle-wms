# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples import (
        ExamplesFlextTapOracleWmsConstants,
        ExamplesFlextTapOracleWmsModels,
        ExamplesFlextTapOracleWmsProtocols,
        ExamplesFlextTapOracleWmsTypes,
        ExamplesFlextTapOracleWmsUtilities,
    )
    from flext_oracle_wms import e
    from flext_tests import api, d, h, r, td, tf, tk, tm, x

    from flext_tap_oracle_wms import (
        FlextTapOracleWms,
        FlextTapOracleWmsConfig,
        FlextTapOracleWmsConstants,
        FlextTapOracleWmsModels,
        FlextTapOracleWmsProtocols,
        FlextTapOracleWmsService,
        FlextTapOracleWmsSettings,
        FlextTapOracleWmsStreams,
        FlextTapOracleWmsTypes,
        FlextTapOracleWmsUtilities,
        FlextTapOracleWmsVersion,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
        config,
        main,
        settings,
        tap_oracle_wms,
    )
    from tests.base import TestsFlextTapOracleWmsServiceBase, s
    from tests.constants import TestsFlextTapOracleWmsConstants, c
    from tests.helpers import TestsFlextTapOracleWmsHelpers
    from tests.models import TestsFlextTapOracleWmsModels, m
    from tests.protocols import TestsFlextTapOracleWmsProtocols, p
    from tests.settings import TestsFlextTapOracleWmsSettings
    from tests.typings import TestsFlextTapOracleWmsTypes, t
    from tests.utilities import TestsFlextTapOracleWmsUtilities, u


__all__: tuple[str, ...] = (
    "ExamplesFlextTapOracleWmsConstants",
    "ExamplesFlextTapOracleWmsModels",
    "ExamplesFlextTapOracleWmsProtocols",
    "ExamplesFlextTapOracleWmsTypes",
    "ExamplesFlextTapOracleWmsUtilities",
    "FlextTapOracleWms",
    "FlextTapOracleWmsConfig",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsProtocols",
    "FlextTapOracleWmsService",
    "FlextTapOracleWmsSettings",
    "FlextTapOracleWmsStreams",
    "FlextTapOracleWmsTypes",
    "FlextTapOracleWmsUtilities",
    "FlextTapOracleWmsVersion",
    "TestsFlextTapOracleWmsConstants",
    "TestsFlextTapOracleWmsHelpers",
    "TestsFlextTapOracleWmsModels",
    "TestsFlextTapOracleWmsProtocols",
    "TestsFlextTapOracleWmsServiceBase",
    "TestsFlextTapOracleWmsSettings",
    "TestsFlextTapOracleWmsTypes",
    "TestsFlextTapOracleWmsUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "api",
    "c",
    "config",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "tap_oracle_wms",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "ExamplesFlextTapOracleWmsConstants": "examples",
        "ExamplesFlextTapOracleWmsModels": "examples",
        "ExamplesFlextTapOracleWmsProtocols": "examples",
        "ExamplesFlextTapOracleWmsTypes": "examples",
        "ExamplesFlextTapOracleWmsUtilities": "examples",
        "FlextTapOracleWms": "flext_tap_oracle_wms",
        "FlextTapOracleWmsConfig": "flext_tap_oracle_wms",
        "FlextTapOracleWmsConstants": "flext_tap_oracle_wms",
        "FlextTapOracleWmsModels": "flext_tap_oracle_wms",
        "FlextTapOracleWmsProtocols": "flext_tap_oracle_wms",
        "FlextTapOracleWmsService": "flext_tap_oracle_wms",
        "FlextTapOracleWmsSettings": "flext_tap_oracle_wms",
        "FlextTapOracleWmsStreams": "flext_tap_oracle_wms",
        "FlextTapOracleWmsTypes": "flext_tap_oracle_wms",
        "FlextTapOracleWmsUtilities": "flext_tap_oracle_wms",
        "FlextTapOracleWmsVersion": "flext_tap_oracle_wms",
        "TestsFlextTapOracleWmsConstants": ".constants",
        "TestsFlextTapOracleWmsHelpers": ".helpers",
        "TestsFlextTapOracleWmsModels": ".models",
        "TestsFlextTapOracleWmsProtocols": ".protocols",
        "TestsFlextTapOracleWmsServiceBase": ".base",
        "TestsFlextTapOracleWmsSettings": ".settings",
        "TestsFlextTapOracleWmsTypes": ".typings",
        "TestsFlextTapOracleWmsUtilities": ".utilities",
        "__author__": "flext_tap_oracle_wms",
        "__author_email__": "flext_tap_oracle_wms",
        "__description__": "flext_tap_oracle_wms",
        "__license__": "flext_tap_oracle_wms",
        "__title__": "flext_tap_oracle_wms",
        "__url__": "flext_tap_oracle_wms",
        "__version__": "flext_tap_oracle_wms",
        "__version_info__": "flext_tap_oracle_wms",
        "api": "flext_tests",
        "c": ".constants",
        "config": "flext_tap_oracle_wms",
        "d": "flext_tests",
        "e": "flext_oracle_wms",
        "h": "flext_tests",
        "m": ".models",
        "main": "flext_tap_oracle_wms",
        "p": ".protocols",
        "r": "flext_tests",
        "s": ".base",
        "settings": "flext_tap_oracle_wms",
        "t": ".typings",
        "tap_oracle_wms": "flext_tap_oracle_wms",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "x": "flext_tests",
    },
    public_exports=__all__,
)
