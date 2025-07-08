"""Modern Oracle WMS Tap - Enterprise-grade Singer tap for Oracle WMS systems."""

from __future__ import annotations

from .client import AuthenticationError, WMSClient, WMSClientError, WMSConnectionError
from .discovery_modern import EntityDiscovery
from .models import StreamState, TapMetrics, WMSConfig, WMSEntity, WMSRecord
from .stream_modern import WMSStream
from .tap_modern import TapOracleWMS

__version__ = "1.0.0"
__author__ = "FLEXT Team"
__email__ = "team@flext.sh"

# Enterprise-ready API
__all__ = [
    "AuthenticationError",
    "EntityDiscovery",
    "StreamState",
    "TapMetrics",
    "TapOracleWMS",
    "WMSClient",
    "WMSClientError",
    "WMSConfig",
    "WMSConnectionError",
    "WMSEntity",
    "WMSRecord",
    "WMSStream",
    "__author__",
    "__email__",
    "__version__",
]
