# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext tap oracle wms package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports
from flext_tap_oracle_wms.__version__ import (
    __all__,
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_tap_oracle_wms import (
        api,
        cli,
        constants,
        errors,
        models,
        protocols,
        settings,
        streams,
        tap,
        typings,
        utilities,
    )
    from flext_tap_oracle_wms.api import FlextTapOracleWmsService
    from flext_tap_oracle_wms.cli import main
    from flext_tap_oracle_wms.constants import (
        FlextTapOracleWmsConstants,
        FlextTapOracleWmsConstants as c,
    )
    from flext_tap_oracle_wms.errors import FlextTapOracleWmsError
    from flext_tap_oracle_wms.models import (
        FlextTapOracleWmsModels,
        FlextTapOracleWmsModels as m,
    )
    from flext_tap_oracle_wms.protocols import (
        FlextTapOracleWmsProtocols,
        FlextTapOracleWmsProtocols as p,
    )
    from flext_tap_oracle_wms.settings import FlextTapOracleWmsSettings
    from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
    from flext_tap_oracle_wms.tap import FlextTapOracleWms, logger
    from flext_tap_oracle_wms.typings import (
        FlextTapOracleWmsTypes,
        FlextTapOracleWmsTypes as t,
    )
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsUtilities,
        FlextTapOracleWmsUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextTapOracleWms": "flext_tap_oracle_wms.tap",
    "FlextTapOracleWmsConstants": "flext_tap_oracle_wms.constants",
    "FlextTapOracleWmsError": "flext_tap_oracle_wms.errors",
    "FlextTapOracleWmsModels": "flext_tap_oracle_wms.models",
    "FlextTapOracleWmsProtocols": "flext_tap_oracle_wms.protocols",
    "FlextTapOracleWmsService": "flext_tap_oracle_wms.api",
    "FlextTapOracleWmsSettings": "flext_tap_oracle_wms.settings",
    "FlextTapOracleWmsStream": "flext_tap_oracle_wms.streams",
    "FlextTapOracleWmsTypes": "flext_tap_oracle_wms.typings",
    "FlextTapOracleWmsUtilities": "flext_tap_oracle_wms.utilities",
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
    "s": ("flext_core.service", "FlextService"),
    "settings": "flext_tap_oracle_wms.settings",
    "streams": "flext_tap_oracle_wms.streams",
    "t": ("flext_tap_oracle_wms.typings", "FlextTapOracleWmsTypes"),
    "tap": "flext_tap_oracle_wms.tap",
    "typings": "flext_tap_oracle_wms.typings",
    "u": ("flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"),
    "utilities": "flext_tap_oracle_wms.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
        "__all__",
        "__author__",
        "__author_email__",
        "__description__",
        "__license__",
        "__title__",
        "__url__",
        "__version__",
        "__version_info__",
    ],
)
