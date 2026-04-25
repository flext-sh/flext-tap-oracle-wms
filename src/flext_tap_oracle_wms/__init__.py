# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Oracle Wms package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from flext_tap_oracle_wms.__version__ import *

if _t.TYPE_CHECKING:
    from flext_oracle_wms import d, e, h, r, s, x

    from flext_tap_oracle_wms.api import FlextTapOracleWmsService, tap_oracle_wms
    from flext_tap_oracle_wms.cli import main
    from flext_tap_oracle_wms.constants import FlextTapOracleWmsConstants, c
    from flext_tap_oracle_wms.errors import (
        FlextTapOracleWmsConfigurationError,
        FlextTapOracleWmsConnectionError,
        FlextTapOracleWmsError,
        FlextTapOracleWmsValidationError,
    )
    from flext_tap_oracle_wms.models import FlextTapOracleWmsModels, m
    from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols, p
    from flext_tap_oracle_wms.settings import FlextTapOracleWmsSettings
    from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
    from flext_tap_oracle_wms.tap import FlextTapOracleWms, FlextTapOracleWmsPlugin
    from flext_tap_oracle_wms.typings import FlextTapOracleWmsTypes, t
    from flext_tap_oracle_wms.utilities import FlextTapOracleWmsUtilities, u
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".__version__": (
            "__author__",
            "__author_email__",
            "__description__",
            "__license__",
            "__title__",
            "__url__",
            "__version__",
            "__version_info__",
        ),
        ".api": (
            "FlextTapOracleWmsService",
            "tap_oracle_wms",
        ),
        ".cli": ("main",),
        ".constants": (
            "FlextTapOracleWmsConstants",
            "c",
        ),
        ".errors": (
            "FlextTapOracleWmsConfigurationError",
            "FlextTapOracleWmsConnectionError",
            "FlextTapOracleWmsError",
            "FlextTapOracleWmsValidationError",
        ),
        ".models": (
            "FlextTapOracleWmsModels",
            "m",
        ),
        ".protocols": (
            "FlextTapOracleWmsProtocols",
            "p",
        ),
        ".settings": ("FlextTapOracleWmsSettings",),
        ".streams": ("FlextTapOracleWmsStream",),
        ".tap": (
            "FlextTapOracleWms",
            "FlextTapOracleWmsPlugin",
        ),
        ".typings": (
            "FlextTapOracleWmsTypes",
            "t",
        ),
        ".utilities": (
            "FlextTapOracleWmsUtilities",
            "u",
        ),
        "flext_oracle_wms": (
            "d",
            "e",
            "h",
            "r",
            "s",
            "x",
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "FlextTapOracleWms",
    "FlextTapOracleWmsConfigurationError",
    "FlextTapOracleWmsConnectionError",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsError",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsPlugin",
    "FlextTapOracleWmsProtocols",
    "FlextTapOracleWmsService",
    "FlextTapOracleWmsSettings",
    "FlextTapOracleWmsStream",
    "FlextTapOracleWmsTypes",
    "FlextTapOracleWmsUtilities",
    "FlextTapOracleWmsValidationError",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "t",
    "tap_oracle_wms",
    "u",
    "x",
]
