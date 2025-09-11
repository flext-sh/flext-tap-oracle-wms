"""Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from flext_core import FlextTypes

"""Enterprise Singer Tap for Oracle WMS data extraction."""
"""
Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


import importlib.metadata

# flext-core imports
from flext_core import FlextLogger, FlextModels, FlextResult

# === FLEXT-MELTANO COMPLETE INTEGRATION ===
# Re-export ALL flext-meltano facilities for full ecosystem integration
from flext_meltano import (
    BatchSink,
    FlextMeltanoBaseService,
    # Bridge integration
    FlextMeltanoBridge,
    # Configuration and validation
    FlextMeltanoConfig,
    FlextMeltanoEvent,
    # Enterprise services from flext-meltano.base
    FlextMeltanoTapService,
    # Authentication patterns
    OAuthAuthenticator,
    # Typing definitions
    PropertiesList,
    Property,
    Sink,
    SQLSink,
    # Core Singer SDK classes (centralized from flext-meltano)
    Stream,
    Tap,
    Target,
    create_meltano_tap_service,
    # Testing utilities
    get_tap_test_class,
    # Singer typing utilities (centralized)
    singer_typing,
)

from flext_tap_oracle_wms.models import (
    CatalogStream,
    OracleWMSEntityModel,
    StreamMetadata,
    StreamSchema,
)
from flext_tap_oracle_wms.tap_client import (
    FlextTapOracleWMS,
    FlextTapOracleWMSPlugin,
    create_oracle_wms_tap_plugin,
)

# PEP8-compliant local imports from reorganized modules
from flext_tap_oracle_wms.tap_config import (
    FlextTapOracleWMSConfig,
    FlextTapOracleWMSConstants,
)
from flext_tap_oracle_wms.tap_exceptions import (
    FlextTapOracleWMSAuthenticationError,
    FlextTapOracleWMSConfigurationError,
    FlextTapOracleWMSConnectionError,
    FlextTapOracleWMSDataValidationError,
    FlextTapOracleWMSDiscoveryError,
    FlextTapOracleWMSError,
    FlextTapOracleWMSPaginationError,
    FlextTapOracleWMSProcessingError,
    FlextTapOracleWMSRateLimitError,
    FlextTapOracleWMSRetryableError,
    FlextTapOracleWMSStreamError,
    FlextTapOracleWMSTimeoutError,
    FlextTapOracleWMSValidationError,
    ValidationContext,
)
from flext_tap_oracle_wms.tap_streams import FlextTapOracleWMSStream

# Version following semantic versioning
try:
    __version__ = importlib.metadata.version("flext-tap-oracle-wms")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0-enterprise"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Complete public API exports - maintaining backward compatibility
__all__: FlextTypes.Core.StringList = [
    "BatchSink",
    "CatalogStream",
    "FlextLogger",
    "FlextMeltanoBaseService",
    "FlextMeltanoBridge",
    "FlextMeltanoConfig",
    "FlextMeltanoEvent",
    "FlextMeltanoTapService",
    "FlextModels",
    "FlextResult",
    "FlextTapOracleWMS",
    "FlextTapOracleWMSAuthenticationError",
    "FlextTapOracleWMSConfig",
    "FlextTapOracleWMSConfigurationError",
    "FlextTapOracleWMSConnectionError",
    "FlextTapOracleWMSConstants",
    "FlextTapOracleWMSDataValidationError",
    "FlextTapOracleWMSDiscoveryError",
    "FlextTapOracleWMSError",
    "FlextTapOracleWMSPaginationError",
    "FlextTapOracleWMSPlugin",
    "FlextTapOracleWMSProcessingError",
    "FlextTapOracleWMSRateLimitError",
    "FlextTapOracleWMSRetryableError",
    "FlextTapOracleWMSStream",
    "FlextTapOracleWMSStreamError",
    "FlextTapOracleWMSTimeoutError",
    "FlextTapOracleWMSValidationError",
    "OAuthAuthenticator",
    "OracleWMSEntityModel",
    "PropertiesList",
    "Property",
    "SQLSink",
    "Sink",
    "Stream",
    "StreamMetadata",
    "StreamSchema",
    "Tap",
    "Target",
    "ValidationContext",
    "__version__",
    "__version_info__",
    "annotations",
    "create_meltano_tap_service",
    "create_oracle_wms_tap_plugin",
    "get_tap_test_class",
    "singer_typing",
]
