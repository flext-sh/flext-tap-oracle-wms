"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from flext_core import FlextLogger, FlextResult, t
from flext_meltano import FlextMeltanoBridge, FlextMeltanoService, FlextMeltanoSettings

from flext_tap_oracle_wms.cli import main
from flext_tap_oracle_wms.constants import (
    FlextTapOracleWmsConstants,
    c,
)
from flext_tap_oracle_wms.exceptions import (
    FlextTapOracleWmsConnectionError,
    FlextTapOracleWmsError,
    FlextTapOracleWmsSettingsurationError,
    FlextTapOracleWmsValidationError,
)
from flext_tap_oracle_wms.models import FlextTapOracleWmsModels, m
from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols
from flext_tap_oracle_wms.settings import (
    FlextTapOracleWmsSettings,
)
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
from flext_tap_oracle_wms.tap import (
    FlextTapOracleWms,
    FlextTapOracleWmsPlugin,
)
from flext_tap_oracle_wms.utilities import (
    FlextTapOracleWmsUtilities,
    u,
)
from flext_tap_oracle_wms.version import (
    VERSION,
    VERSION as PROJECT_VERSION,
    FlextTapOracleWmsVersion,
    __version__,
    __version_info__,
)

__all__ = [
    "PROJECT_VERSION",
    "VERSION",
    "FlextLogger",
    "FlextMeltanoBridge",
    "FlextMeltanoService",
    "FlextMeltanoSettings",
    "FlextResult",
    "FlextTapOracleWms",
    "FlextTapOracleWmsConnectionError",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsError",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsPlugin",
    "FlextTapOracleWmsProtocols",
    "FlextTapOracleWmsSettings",
    "FlextTapOracleWmsSettingsurationError",
    "FlextTapOracleWmsStream",
    "FlextTapOracleWmsUtilities",
    "FlextTapOracleWmsValidationError",
    "FlextTapOracleWmsVersion",
    "__version__",
    "__version_info__",
    "c",
    "m",
    "main",
    "t",
    # Domain-specific aliases
    "u",
]
