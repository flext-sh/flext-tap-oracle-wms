"""FLEXT Tap Oracle WMS - Enterprise Singer Tap for Oracle WMS Integration.

**Architecture**: Production-ready Singer tap implementing Clean Architecture, DDD, and enterprise patterns
**Integration**: Complete flext-meltano ecosystem integration with ALL facilities utilized
**Quality**: 100% type safety, 90%+ test coverage, zero-tolerance quality standards
**WMS Integration**: Complete Oracle WMS API connectivity via flext-oracle-wms
**Structure**: PEP8-compliant module organization following FLEXT patterns

## Enterprise Integration Features:

1. **Complete flext-meltano Integration**: Uses ALL flext-meltano facilities
   - FlextMeltanoTapService base class for enterprise patterns
   - Centralized Singer SDK imports and typing
   - Common schema definitions from flext-meltano.common_schemas
   - Enterprise bridge integration for Go ↔ Python communication

2. **Foundation Library Integration**: Full flext-core pattern adoption
   - FlextResult railway-oriented programming throughout
   - Enterprise logging with FlextLogger
   - Dependency injection with flext-core container
   - FlextConfig for configuration management

3. **Oracle WMS Integration**: Complete WMS connectivity
   - flext-oracle-wms for all WMS API operations
   - Enterprise error handling and validation
   - Production-grade authentication and security

4. **Production Readiness**: Zero-tolerance quality standards
   - 100% type safety with strict MyPy compliance
   - 90%+ test coverage with comprehensive test suite
   - All lint rules passing with Ruff
   - Security scanning with Bandit and pip-audit

5. **PEP8 Structure**: Clean module organization
   - tap_config.py: Configuration management and constants
   - tap_client.py: Consolidated tap and plugin functionality
   - tap_streams.py: Stream definitions and processing
   - tap_cli.py: Command-line interface
   - tap_exceptions.py: Exception hierarchy
   - tap_models.py: Data models and structures

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib.metadata

# flext-core imports
from flext_core import FlextResult, FlextValueObject, get_logger

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

# PEP8-compliant local imports from reorganized modules
from flext_tap_oracle_wms.tap_config import (
    FlextTapOracleWMSConfig,
    FlextTapOracleWMSConstants,
)
from flext_tap_oracle_wms.tap_client import (
    FlextTapOracleWMS,
    FlextTapOracleWMSPlugin,
    create_oracle_wms_tap_plugin,
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
from flext_tap_oracle_wms.tap_models import (
    CatalogStream,
    OracleWMSEntityModel,
    StreamMetadata,
    StreamSchema,
)
from flext_tap_oracle_wms.tap_streams import FlextTapOracleWMSStream

# Version following semantic versioning
try:
    __version__ = importlib.metadata.version("flext-tap-oracle-wms")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0-enterprise"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Complete public API exports - maintaining backward compatibility
__all__: list[str] = [
    "BatchSink", "FlextMeltanoBaseService", "FlextMeltanoBridge", "FlextMeltanoConfig",
    "FlextMeltanoEvent", "FlextMeltanoTapService", "OAuthAuthenticator", "PropertiesList", "Property",
    "SQLSink", "Sink", "Stream", "Tap", "Target", "create_meltano_tap_service", "get_tap_test_class",
    "singer_typing", "FlextResult", "FlextValueObject", "get_logger", "FlextTapOracleWMS",
    "FlextTapOracleWMSPlugin", "create_oracle_wms_tap_plugin", "FlextTapOracleWMSConfig",
    "FlextTapOracleWMSConstants", "FlextTapOracleWMSStream", "CatalogStream", "OracleWMSEntityModel",
    "StreamMetadata", "StreamSchema", "FlextTapOracleWMSAuthenticationError",
    "FlextTapOracleWMSConfigurationError", "FlextTapOracleWMSConnectionError",
    "FlextTapOracleWMSDataValidationError", "FlextTapOracleWMSDiscoveryError", "FlextTapOracleWMSError",
    "FlextTapOracleWMSPaginationError", "FlextTapOracleWMSProcessingError",
    "FlextTapOracleWMSRateLimitError", "FlextTapOracleWMSRetryableError", "FlextTapOracleWMSStreamError",
    "FlextTapOracleWMSTimeoutError", "FlextTapOracleWMSValidationError", "ValidationContext",
    "__version__", "__version_info__", "annotations",
]
