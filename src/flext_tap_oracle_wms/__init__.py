# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

from flext_tap_oracle_wms.__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)

if TYPE_CHECKING:
    from flext_meltano import d, e, h, r, s, x

    from flext_tap_oracle_wms import (
        cli as cli,
        constants as constants,
        errors as errors,
        models as models,
        protocols as protocols,
        settings as settings,
        streams as streams,
        tap as tap,
        typings as typings,
        utilities as utilities,
    )
    from flext_tap_oracle_wms.cli import main as main
    from flext_tap_oracle_wms.constants import (
        FlextTapOracleWmsConstants as FlextTapOracleWmsConstants,
        FlextTapOracleWmsConstants as c,
    )
    from flext_tap_oracle_wms.errors import (
        FlextTapOracleWmsConfigurationError as FlextTapOracleWmsConfigurationError,
        FlextTapOracleWmsConnectionError as FlextTapOracleWmsConnectionError,
        FlextTapOracleWmsError as FlextTapOracleWmsError,
        FlextTapOracleWmsValidationError as FlextTapOracleWmsValidationError,
    )
    from flext_tap_oracle_wms.models import (
        FlextTapOracleWmsModels as FlextTapOracleWmsModels,
        FlextTapOracleWmsModels as m,
    )
    from flext_tap_oracle_wms.protocols import (
        FlextTapOracleWmsProtocols as FlextTapOracleWmsProtocols,
        FlextTapOracleWmsProtocols as p,
    )
    from flext_tap_oracle_wms.settings import (
        FlextTapOracleWmsSettings as FlextTapOracleWmsSettings,
    )
    from flext_tap_oracle_wms.streams import (
        FlextTapOracleWmsStream as FlextTapOracleWmsStream,
    )
    from flext_tap_oracle_wms.tap import (
        FlextTapOracleWms as FlextTapOracleWms,
        FlextTapOracleWmsPlugin as FlextTapOracleWmsPlugin,
        logger as logger,
    )
    from flext_tap_oracle_wms.typings import (
        FlextTapOracleWmsTypes as FlextTapOracleWmsTypes,
        FlextTapOracleWmsTypes as t,
    )
    from flext_tap_oracle_wms.utilities import (
        FlextTapOracleWmsUtilities as FlextTapOracleWmsUtilities,
        FlextTapOracleWmsUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextTapOracleWms": ["flext_tap_oracle_wms.tap", "FlextTapOracleWms"],
    "FlextTapOracleWmsConfigurationError": ["flext_tap_oracle_wms.errors", "FlextTapOracleWmsConfigurationError"],
    "FlextTapOracleWmsConnectionError": ["flext_tap_oracle_wms.errors", "FlextTapOracleWmsConnectionError"],
    "FlextTapOracleWmsConstants": ["flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"],
    "FlextTapOracleWmsError": ["flext_tap_oracle_wms.errors", "FlextTapOracleWmsError"],
    "FlextTapOracleWmsModels": ["flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"],
    "FlextTapOracleWmsPlugin": ["flext_tap_oracle_wms.tap", "FlextTapOracleWmsPlugin"],
    "FlextTapOracleWmsProtocols": ["flext_tap_oracle_wms.protocols", "FlextTapOracleWmsProtocols"],
    "FlextTapOracleWmsSettings": ["flext_tap_oracle_wms.settings", "FlextTapOracleWmsSettings"],
    "FlextTapOracleWmsStream": ["flext_tap_oracle_wms.streams", "FlextTapOracleWmsStream"],
    "FlextTapOracleWmsTypes": ["flext_tap_oracle_wms.typings", "FlextTapOracleWmsTypes"],
    "FlextTapOracleWmsUtilities": ["flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"],
    "FlextTapOracleWmsValidationError": ["flext_tap_oracle_wms.errors", "FlextTapOracleWmsValidationError"],
    "c": ["flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"],
    "cli": ["flext_tap_oracle_wms.cli", ""],
    "constants": ["flext_tap_oracle_wms.constants", ""],
    "d": ["flext_meltano", "d"],
    "e": ["flext_meltano", "e"],
    "errors": ["flext_tap_oracle_wms.errors", ""],
    "h": ["flext_meltano", "h"],
    "logger": ["flext_tap_oracle_wms.tap", "logger"],
    "m": ["flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"],
    "main": ["flext_tap_oracle_wms.cli", "main"],
    "models": ["flext_tap_oracle_wms.models", ""],
    "p": ["flext_tap_oracle_wms.protocols", "FlextTapOracleWmsProtocols"],
    "protocols": ["flext_tap_oracle_wms.protocols", ""],
    "r": ["flext_meltano", "r"],
    "s": ["flext_meltano", "s"],
    "settings": ["flext_tap_oracle_wms.settings", ""],
    "streams": ["flext_tap_oracle_wms.streams", ""],
    "t": ["flext_tap_oracle_wms.typings", "FlextTapOracleWmsTypes"],
    "tap": ["flext_tap_oracle_wms.tap", ""],
    "typings": ["flext_tap_oracle_wms.typings", ""],
    "u": ["flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"],
    "utilities": ["flext_tap_oracle_wms.utilities", ""],
    "x": ["flext_meltano", "x"],
}

_EXPORTS: Sequence[str] = [
    "FlextTapOracleWms",
    "FlextTapOracleWmsConfigurationError",
    "FlextTapOracleWmsConnectionError",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsError",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsPlugin",
    "FlextTapOracleWmsProtocols",
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
