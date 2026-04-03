# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext tap oracle wms package."""

from __future__ import annotations

import typing as _t

from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.result import FlextResult as r
from flext_tap_oracle_wms.__version__ import *
from flext_tap_oracle_wms.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if _t.TYPE_CHECKING:
    import flext_tap_oracle_wms.api as _flext_tap_oracle_wms_api

    api = _flext_tap_oracle_wms_api
    import flext_tap_oracle_wms.cli as _flext_tap_oracle_wms_cli

    cli = _flext_tap_oracle_wms_cli
    import flext_tap_oracle_wms.constants as _flext_tap_oracle_wms_constants

    constants = _flext_tap_oracle_wms_constants
    import flext_tap_oracle_wms.errors as _flext_tap_oracle_wms_errors

    errors = _flext_tap_oracle_wms_errors
    import flext_tap_oracle_wms.models as _flext_tap_oracle_wms_models

    models = _flext_tap_oracle_wms_models
    import flext_tap_oracle_wms.protocols as _flext_tap_oracle_wms_protocols

    protocols = _flext_tap_oracle_wms_protocols
    import flext_tap_oracle_wms.settings as _flext_tap_oracle_wms_settings

    settings = _flext_tap_oracle_wms_settings
    import flext_tap_oracle_wms.streams as _flext_tap_oracle_wms_streams

    streams = _flext_tap_oracle_wms_streams
    import flext_tap_oracle_wms.tap as _flext_tap_oracle_wms_tap

    tap = _flext_tap_oracle_wms_tap
    import flext_tap_oracle_wms.typings as _flext_tap_oracle_wms_typings

    typings = _flext_tap_oracle_wms_typings
    import flext_tap_oracle_wms.utilities as _flext_tap_oracle_wms_utilities

    utilities = _flext_tap_oracle_wms_utilities

    _ = (
        FlextTapOracleWms,
        FlextTapOracleWmsConfigurationError,
        FlextTapOracleWmsConnectionError,
        FlextTapOracleWmsConstants,
        FlextTapOracleWmsError,
        FlextTapOracleWmsModels,
        FlextTapOracleWmsPlugin,
        FlextTapOracleWmsProtocols,
        FlextTapOracleWmsService,
        FlextTapOracleWmsSettings,
        FlextTapOracleWmsStream,
        FlextTapOracleWmsTypes,
        FlextTapOracleWmsUtilities,
        FlextTapOracleWmsValidationError,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
        api,
        c,
        cli,
        constants,
        d,
        e,
        errors,
        h,
        logger,
        m,
        main,
        models,
        p,
        protocols,
        r,
        s,
        settings,
        streams,
        t,
        tap,
        typings,
        u,
        utilities,
        x,
    )
_LAZY_IMPORTS = {
    "FlextTapOracleWms": "flext_tap_oracle_wms.tap",
    "FlextTapOracleWmsConfigurationError": "flext_tap_oracle_wms.errors",
    "FlextTapOracleWmsConnectionError": "flext_tap_oracle_wms.errors",
    "FlextTapOracleWmsConstants": "flext_tap_oracle_wms.constants",
    "FlextTapOracleWmsError": "flext_tap_oracle_wms.errors",
    "FlextTapOracleWmsModels": "flext_tap_oracle_wms.models",
    "FlextTapOracleWmsPlugin": "flext_tap_oracle_wms.tap",
    "FlextTapOracleWmsProtocols": "flext_tap_oracle_wms.protocols",
    "FlextTapOracleWmsService": "flext_tap_oracle_wms.api",
    "FlextTapOracleWmsSettings": "flext_tap_oracle_wms.settings",
    "FlextTapOracleWmsStream": "flext_tap_oracle_wms.streams",
    "FlextTapOracleWmsTypes": "flext_tap_oracle_wms.typings",
    "FlextTapOracleWmsUtilities": "flext_tap_oracle_wms.utilities",
    "FlextTapOracleWmsValidationError": "flext_tap_oracle_wms.errors",
    "__author__": "flext_tap_oracle_wms.__version__",
    "__author_email__": "flext_tap_oracle_wms.__version__",
    "__description__": "flext_tap_oracle_wms.__version__",
    "__license__": "flext_tap_oracle_wms.__version__",
    "__title__": "flext_tap_oracle_wms.__version__",
    "__url__": "flext_tap_oracle_wms.__version__",
    "__version__": "flext_tap_oracle_wms.__version__",
    "__version_info__": "flext_tap_oracle_wms.__version__",
    "api": "flext_tap_oracle_wms.api",
    "c": ("flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"),
    "cli": "flext_tap_oracle_wms.cli",
    "constants": "flext_tap_oracle_wms.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "errors": "flext_tap_oracle_wms.errors",
    "h": ("flext_core.handlers", "FlextHandlers"),
    "logger": "flext_tap_oracle_wms.tap",
    "m": ("flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"),
    "main": "flext_tap_oracle_wms.cli",
    "models": "flext_tap_oracle_wms.models",
    "p": ("flext_tap_oracle_wms.protocols", "FlextTapOracleWmsProtocols"),
    "protocols": "flext_tap_oracle_wms.protocols",
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_tap_oracle_wms.api", "FlextTapOracleWmsService"),
    "settings": "flext_tap_oracle_wms.settings",
    "streams": "flext_tap_oracle_wms.streams",
    "t": ("flext_tap_oracle_wms.typings", "FlextTapOracleWmsTypes"),
    "tap": "flext_tap_oracle_wms.tap",
    "typings": "flext_tap_oracle_wms.typings",
    "u": ("flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"),
    "utilities": "flext_tap_oracle_wms.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
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
    "api",
    "c",
    "cli",
    "constants",
    "d",
    "e",
    "errors",
    "h",
    "logger",
    "m",
    "main",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "settings",
    "streams",
    "t",
    "tap",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
