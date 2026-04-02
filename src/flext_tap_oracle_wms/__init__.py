# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports
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

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_meltano import d, e, h, r, s, x
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
    from flext_tap_oracle_wms.tap import (
        FlextTapOracleWms,
        FlextTapOracleWmsPlugin,
        logger,
    )
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
    "api": "flext_tap_oracle_wms.api",
    "c": ("flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"),
    "cli": "flext_tap_oracle_wms.cli",
    "constants": "flext_tap_oracle_wms.constants",
    "d": "flext_meltano",
    "e": "flext_meltano",
    "errors": "flext_tap_oracle_wms.errors",
    "h": "flext_meltano",
    "logger": "flext_tap_oracle_wms.tap",
    "m": ("flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"),
    "main": "flext_tap_oracle_wms.cli",
    "models": "flext_tap_oracle_wms.models",
    "p": ("flext_tap_oracle_wms.protocols", "FlextTapOracleWmsProtocols"),
    "protocols": "flext_tap_oracle_wms.protocols",
    "r": "flext_meltano",
    "s": "flext_meltano",
    "settings": "flext_tap_oracle_wms.settings",
    "streams": "flext_tap_oracle_wms.streams",
    "t": ("flext_tap_oracle_wms.typings", "FlextTapOracleWmsTypes"),
    "tap": "flext_tap_oracle_wms.tap",
    "typings": "flext_tap_oracle_wms.typings",
    "u": ("flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"),
    "utilities": "flext_tap_oracle_wms.utilities",
    "x": "flext_meltano",
}


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
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
