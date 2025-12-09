"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from typing import Final

from flext_core import FlextLogger, FlextModels, FlextResult
from flext_meltano import FlextMeltanoBridge, FlextMeltanoConfig, FlextMeltanoService

from flext_tap_oracle_wms.cli import main
from flext_tap_oracle_wms.client import (
    FlextTapOracleWms,
    FlextTapOracleWmsPlugin,
)
from flext_tap_oracle_wms.config import (
    FlextTapOracleWmsConfig,
    FlextTapOracleWmsConstants,
)
from flext_tap_oracle_wms.exceptions import (
    FlextTapOracleWmsConfigurationError,
    FlextTapOracleWmsConnectionError,
    FlextTapOracleWmsError,
    FlextTapOracleWmsValidationError,
)
from flext_tap_oracle_wms.models import FlextTapOracleWmsModels, m, m_tap_oracle_wms
from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
from flext_tap_oracle_wms.utilities import FlextTapOracleWmsUtilities
from flext_tap_oracle_wms.version import VERSION, FlextTapOracleWmsVersion

# Domain-specific aliases
u = FlextTapOracleWmsUtilities  # Utilities (FlextTapOracleWmsUtilities extends FlextUtilities)

PROJECT_VERSION: Final[FlextTapOracleWmsVersion] = VERSION

__version__: str = VERSION.version
__version_info__: tuple[int | str, ...] = VERSION.version_info

__all__ = [
    "PROJECT_VERSION",
    "VERSION",
    "FlextLogger",
    "FlextMeltanoBridge",
    "FlextMeltanoConfig",
    "FlextMeltanoService",
    "FlextModels",
    "FlextResult",
    "FlextTapOracleWms",
    "FlextTapOracleWmsConfig",
    "FlextTapOracleWmsConfigurationError",
    "FlextTapOracleWmsConnectionError",
    "FlextTapOracleWmsConstants",
    "FlextTapOracleWmsError",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsPlugin",
    "FlextTapOracleWmsProtocols",
    "FlextTapOracleWmsStream",
    "FlextTapOracleWmsUtilities",
    "FlextTapOracleWmsValidationError",
    "FlextTapOracleWmsVersion",
    "__version__",
    "__version_info__",
    "m",
    "m_tap_oracle_wms",
    "main",
    # Domain-specific aliases
    "u",
]
