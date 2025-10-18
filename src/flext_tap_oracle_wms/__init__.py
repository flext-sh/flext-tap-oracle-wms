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
    FlextMeltanoTapOracleWMS,
    FlextMeltanoTapOracleWMSPlugin,
)
from flext_tap_oracle_wms.config import (
    FlextMeltanoTapOracleWMSConfig,
    FlextMeltanoTapOracleWMSConstants,
)
from flext_tap_oracle_wms.models import FlextMeltanoTapOracleWmsModels
from flext_tap_oracle_wms.protocols import FlextMeltanoTapOracleWmsProtocols
from flext_tap_oracle_wms.streams import FlextMeltanoTapOracleWMSStream
from flext_tap_oracle_wms.utilities import FlextMeltanoTapOracleWmsUtilities
from flext_tap_oracle_wms.version import VERSION, FlextMeltanoTapOracleWmsVersion

PROJECT_VERSION: Final[FlextMeltanoTapOracleWmsVersion] = VERSION

__version__: str = VERSION.version
__version_info__: tuple[int | str, ...] = VERSION.version_info

__all__ = [
    "PROJECT_VERSION",
    "VERSION",
    "FlextLogger",
    "FlextMeltanoBridge",
    "FlextMeltanoConfig",
    "FlextMeltanoService",
    "FlextMeltanoTapOracleWMS",
    "FlextMeltanoTapOracleWMSConfig",
    "FlextMeltanoTapOracleWMSConfigurationError",
    "FlextMeltanoTapOracleWMSConnectionError",
    "FlextMeltanoTapOracleWMSConstants",
    "FlextMeltanoTapOracleWMSError",
    "FlextMeltanoTapOracleWMSPlugin",
    "FlextMeltanoTapOracleWMSStream",
    "FlextMeltanoTapOracleWMSValidationError",
    "FlextMeltanoTapOracleWmsModels",
    "FlextMeltanoTapOracleWmsProtocols",
    "FlextMeltanoTapOracleWmsUtilities",
    "FlextMeltanoTapOracleWmsVersion",
    "FlextModels",
    "FlextResult",
    "__version__",
    "__version_info__",
    "dict[str, object]",
    "main",
]
