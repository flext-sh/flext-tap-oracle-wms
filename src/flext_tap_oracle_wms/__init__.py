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

if TYPE_CHECKING:
    from flext_tap_oracle_wms.__version__ import *
    from flext_tap_oracle_wms.cli import *
    from flext_tap_oracle_wms.constants import *
    from flext_tap_oracle_wms.errors import *
    from flext_tap_oracle_wms.models import *
    from flext_tap_oracle_wms.protocols import *
    from flext_tap_oracle_wms.settings import *
    from flext_tap_oracle_wms.streams import *
    from flext_tap_oracle_wms.tap import *
    from flext_tap_oracle_wms.typings import *
    from flext_tap_oracle_wms.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextTapOracleWms": "flext_tap_oracle_wms.tap",
    "FlextTapOracleWmsConfigurationError": "flext_tap_oracle_wms.errors",
    "FlextTapOracleWmsConnectionError": "flext_tap_oracle_wms.errors",
    "FlextTapOracleWmsConstants": "flext_tap_oracle_wms.constants",
    "FlextTapOracleWmsError": "flext_tap_oracle_wms.errors",
    "FlextTapOracleWmsModels": "flext_tap_oracle_wms.models",
    "FlextTapOracleWmsPlugin": "flext_tap_oracle_wms.tap",
    "FlextTapOracleWmsProtocols": "flext_tap_oracle_wms.protocols",
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
    "c": ["flext_tap_oracle_wms.constants", "FlextTapOracleWmsConstants"],
    "cli": "flext_tap_oracle_wms.cli",
    "constants": "flext_tap_oracle_wms.constants",
    "d": "flext_meltano",
    "e": "flext_meltano",
    "errors": "flext_tap_oracle_wms.errors",
    "h": "flext_meltano",
    "logger": "flext_tap_oracle_wms.tap",
    "m": ["flext_tap_oracle_wms.models", "FlextTapOracleWmsModels"],
    "main": "flext_tap_oracle_wms.cli",
    "models": "flext_tap_oracle_wms.models",
    "p": ["flext_tap_oracle_wms.protocols", "FlextTapOracleWmsProtocols"],
    "protocols": "flext_tap_oracle_wms.protocols",
    "r": "flext_meltano",
    "s": "flext_meltano",
    "settings": "flext_tap_oracle_wms.settings",
    "streams": "flext_tap_oracle_wms.streams",
    "t": ["flext_tap_oracle_wms.typings", "FlextTapOracleWmsTypes"],
    "tap": "flext_tap_oracle_wms.tap",
    "typings": "flext_tap_oracle_wms.typings",
    "u": ["flext_tap_oracle_wms.utilities", "FlextTapOracleWmsUtilities"],
    "utilities": "flext_tap_oracle_wms.utilities",
    "x": "flext_meltano",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
