"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from flext_core import FlextLogger, FlextModels, FlextResult
from flext_meltano import FlextMeltanoBridge, FlextMeltanoService, FlextMeltanoSettings

from flext_tap_oracle_wms.cli import main
from flext_tap_oracle_wms.typings import t
from flext_tap_oracle_wms.client import (
from flext_tap_oracle_wms.typings import t
    FlextTapOracleWms,
    FlextTapOracleWmsPlugin,
)
from flext_tap_oracle_wms.constants import (
from flext_tap_oracle_wms.typings import t
    FlextTapOracleWmsConstants,
)
from flext_tap_oracle_wms.exceptions import (
from flext_tap_oracle_wms.typings import t
    FlextTapOracleWmsConnectionError,
    FlextTapOracleWmsError,
    FlextTapOracleWmsSettingsurationError,
    FlextTapOracleWmsValidationError,
)
from flext_tap_oracle_wms.models import FlextTapOracleWmsModels, m, m_tap_oracle_wms
from flext_tap_oracle_wms.typings import t
from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols
from flext_tap_oracle_wms.typings import t
from flext_tap_oracle_wms.settings import (
from flext_tap_oracle_wms.typings import t
    FlextTapOracleWmsSettings,
)
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
from flext_tap_oracle_wms.typings import t
from flext_tap_oracle_wms.utilities import (
from flext_tap_oracle_wms.typings import t
    FlextTapOracleWmsUtilities,
    FlextTapOracleWmsUtilities as u,
)
from flext_tap_oracle_wms.version import (
from flext_tap_oracle_wms.typings import t
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
    "FlextModels",
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
    "t",
    "__version__",
    "__version_info__",
    "m",
    "m_tap_oracle_wms",
    "main",
    # Domain-specific aliases
    "u",
]
