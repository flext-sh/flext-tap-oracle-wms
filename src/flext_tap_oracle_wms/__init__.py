# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext tap oracle wms package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports
from flext_tap_oracle_wms.__version__ import *

if _t.TYPE_CHECKING:
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
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
    from flext_tap_oracle_wms.api import (
        FlextTapOracleWmsService,
        FlextTapOracleWmsService as s,
    )
    from flext_tap_oracle_wms.cli import FlextTapOracleWmsCli
    from flext_tap_oracle_wms.constants import (
        FlextTapOracleWmsConstants,
        FlextTapOracleWmsConstants as c,
    )
    from flext_tap_oracle_wms.errors import (
        FlextTapOracleWmsConfigurationError,
        FlextTapOracleWmsConnectionError,
        FlextTapOracleWmsError,
        FlextTapOracleWmsValidationError,
    )
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
    from flext_tap_oracle_wms.tap import FlextTapOracleWms, FlextTapOracleWmsPlugin
    from flext_tap_oracle_wms.typings import (
        FlextTapOracleWmsTypes,
        FlextTapOracleWmsTypes as t,
    )
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsUtilities,
        FlextTapOracleWmsUtilities as u,
    )
_LAZY_IMPORTS = {
    "FlextTapOracleWms": ("flext_tap_oracle_wms.tap", "FlextTapOracleWms"),
    "FlextTapOracleWmsCli": ("flext_tap_oracle_wms.cli", "FlextTapOracleWmsCli"),
    "FlextTapOracleWmsConfigurationError": (
        "flext_tap_oracle_wms.errors",
        "FlextTapOracleWmsConfigurationError",
    ),
    "FlextTapOracleWmsConnectionError": (
        "flext_tap_oracle_wms.errors",
        "FlextTapOracleWmsConnectionError",
    ),
    "FlextTapOracleWmsConstants": (
        "flext_tap_oracle_wms.constants",
        "FlextTapOracleWmsConstants",
    ),
    "FlextTapOracleWmsError": ("flext_tap_oracle_wms.errors", "FlextTapOracleWmsError"),
    "FlextTapOracleWmsModels": (
        "flext_tap_oracle_wms.models",
        "FlextTapOracleWmsModels",
    ),
    "FlextTapOracleWmsPlugin": ("flext_tap_oracle_wms.tap", "FlextTapOracleWmsPlugin"),
    "FlextTapOracleWmsProtocols": (
        "flext_tap_oracle_wms.protocols",
        "FlextTapOracleWmsProtocols",
    ),
    "FlextTapOracleWmsService": (
        "flext_tap_oracle_wms.api",
        "FlextTapOracleWmsService",
    ),
    "FlextTapOracleWmsSettings": (
        "flext_tap_oracle_wms.settings",
        "FlextTapOracleWmsSettings",
    ),
    "FlextTapOracleWmsStream": (
        "flext_tap_oracle_wms.streams",
        "FlextTapOracleWmsStream",
    ),
    "FlextTapOracleWmsTypes": (
        "flext_tap_oracle_wms.typings",
        "FlextTapOracleWmsTypes",
    ),
    "FlextTapOracleWmsUtilities": (
        "flext_tap_oracle_wms.utilities",
        "FlextTapOracleWmsUtilities",
    ),
    "FlextTapOracleWmsValidationError": (
        "flext_tap_oracle_wms.errors",
        "FlextTapOracleWmsValidationError",
    ),
    "__author__": ("flext_tap_oracle_wms.__version__", "__author__"),
    "__author_email__": ("flext_tap_oracle_wms.__version__", "__author_email__"),
    "__description__": ("flext_tap_oracle_wms.__version__", "__description__"),
    "__license__": ("flext_tap_oracle_wms.__version__", "__license__"),
    "__title__": ("flext_tap_oracle_wms.__version__", "__title__"),
    "__url__": ("flext_tap_oracle_wms.__version__", "__url__"),
    "__version__": ("flext_tap_oracle_wms.__version__", "__version__"),
    "__version_info__": ("flext_tap_oracle_wms.__version__", "__version_info__"),
    "api": "flext_tap_oracle_wms.api",
    "c": ("flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"),
    "cli": "flext_tap_oracle_wms.cli",
    "constants": "flext_tap_oracle_wms.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "errors": "flext_tap_oracle_wms.errors",
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"),
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
    "FlextTapOracleWmsCli",
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
    "m",
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
