"""Enterprise Singer Tap for Oracle WMS data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from typing import Final

from flext_meltano import FlextMeltanoBridge, FlextMeltanoConfig, FlextMeltanoService

from flext_core import FlextLogger, FlextModels, FlextResult, FlextTypes
from flext_tap_oracle_wms.cli import main
from flext_tap_oracle_wms.client import FlextTapOracleWMS, FlextTapOracleWMSPlugin
from flext_tap_oracle_wms.config import (
    FlextTapOracleWMSConfig,
    FlextTapOracleWMSConstants,
)
from flext_tap_oracle_wms.exceptions import (
    FlextTapOracleWMSConfigurationError,
    FlextTapOracleWMSConnectionError,
    FlextTapOracleWMSError,
    FlextTapOracleWMSValidationError,
)
from flext_tap_oracle_wms.models import FlextTapOracleWmsModels
from flext_tap_oracle_wms.protocols import FlextTapOracleWmsProtocols
from flext_tap_oracle_wms.streams import FlextTapOracleWMSStream
from flext_tap_oracle_wms.utilities import FlextTapOracleWmsUtilities
from flext_tap_oracle_wms.version import VERSION, FlextTapOracleWmsVersion

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
    "FlextTapOracleWMS",
    "FlextTapOracleWMSConfig",
    "FlextTapOracleWMSConfigurationError",
    "FlextTapOracleWMSConnectionError",
    "FlextTapOracleWMSConstants",
    "FlextTapOracleWMSError",
    "FlextTapOracleWMSPlugin",
    "FlextTapOracleWMSStream",
    "FlextTapOracleWMSValidationError",
    "FlextTapOracleWmsModels",
    "FlextTapOracleWmsProtocols",
    "FlextTapOracleWmsUtilities",
    "FlextTapOracleWmsVersion",
    "FlextTypes",
    "__version__",
    "__version_info__",
    "main",
]
