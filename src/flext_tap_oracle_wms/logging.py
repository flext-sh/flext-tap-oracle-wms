"""Enterprise Singer SDK Logging - Centralized FLEXT Integration for TAP.

This module implements a comprehensive enterprise logging system with heavy emphasis on TRACE level
for maximum operational visibility and debugging capabilities in Singer SDK Oracle WMS tap
using the centralized FLEXT logging system.

TRACE Level Usage:
- Every Singer SDK operation and hook
- All WMS API calls and responses
- Singer SDK stream operations
- Authentication and connection details
- Performance metrics and timing information
- State transitions and data flow tracking
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Add shared logging to path
sys.path.insert(0, "/home/marlonsc/flext/shared")

from logging_config import (
    FlextEnterpriseLogger,
    LogLevel,
    TraceContext,
    TraceOperationContext,
    configure_flext_logging,
    get_flext_logger,
)

if TYPE_CHECKING:
    from types import TracebackType

# Configure centralized logging for Singer SDK tap operations with TRACE emphasis
configure_flext_logging(
    level=LogLevel.TRACE,
    enable_trace=True,
    log_dir="logs",
    enable_console=True,
    enable_file=True,
)

# Singer SDK-specific logger factory using centralized system
def get_singer_logger(name: str) -> FlextEnterpriseLogger:
    """Get Singer SDK logger with centralized FLEXT logging."""
    return get_flext_logger(f"singer.{name}")

# Legacy compatibility aliases using centralized system
SingerSDKLogger = FlextEnterpriseLogger

def configure_singer_logging(
    level: LogLevel = LogLevel.TRACE,
    *,
    enable_trace: bool = True,
    log_file: str | None = None,
    log_dir: str | None = None,
) -> None:
    """Configure global logging for Singer SDK tap operations - legacy compatibility."""
    configure_flext_logging(
        level=level,
        enable_trace=enable_trace,
        log_dir=log_dir or "logs",
        enable_console=True,
        enable_file=True,
    )

# Create specialized functions for Singer SDK operations
def trace_singer_operation(
    logger: FlextEnterpriseLogger,
    operation: str,
    stream_name: str | None = None,
    record_count: int | None = None,
    timing_ms: float | None = None,
    **kwargs: Any,
) -> None:
    """Specialized TRACE logging for Singer SDK operations."""
    context = TraceContext(
        operation=f"singer_{operation}",
        module="singer_sdk",
        timing_ms=timing_ms,
        metadata={
            "stream_name": stream_name,
            "record_count": record_count,
            **kwargs,
        },
    )
    logger.trace(f"Singer SDK {operation}", context)

def trace_wms_api_call(
    logger: FlextEnterpriseLogger,
    method: str,
    endpoint: str,
    status_code: int | None = None,
    timing_ms: float | None = None,
    request_size: int | None = None,
    response_size: int | None = None,
    **kwargs: Any,
) -> None:
    """Specialized TRACE logging for WMS API calls."""
    context = TraceContext(
        operation="wms_api_call",
        module="wms_client",
        api_endpoint=endpoint,
        http_method=method,
        timing_ms=timing_ms,
        metadata={
            "status_code": status_code,
            "request_size": request_size,
            "response_size": response_size,
            **kwargs,
        },
    )
    logger.trace(f"WMS API: {method} {endpoint}", context)

def trace_stream_operation(
    logger: FlextEnterpriseLogger,
    stream_name: str,
    operation: str,
    record_count: int | None = None,
    batch_size: int | None = None,
    timing_ms: float | None = None,
    **kwargs: Any,
) -> None:
    """Specialized TRACE logging for Singer SDK stream operations."""
    context = TraceContext(
        operation=f"stream_{operation}",
        module="singer_stream",
        timing_ms=timing_ms,
        metadata={
            "stream_name": stream_name,
            "record_count": record_count,
            "batch_size": batch_size,
            **kwargs,
        },
    )
    logger.trace(f"Stream {operation}: {stream_name}", context)

def trace_authentication(
    logger: FlextEnterpriseLogger,
    auth_method: str,
    status: str,
    timing_ms: float | None = None,
    **kwargs: Any,
) -> None:
    """Specialized TRACE logging for authentication operations."""
    context = TraceContext(
        operation="authentication",
        module="auth",
        timing_ms=timing_ms,
        metadata={
            "auth_method": auth_method,
            "status": status,
            **kwargs,
        },
    )
    logger.trace(f"Authentication {auth_method}: {status}", context)

def trace_discovery_operation(
    logger: FlextEnterpriseLogger,
    operation: str,
    entity_count: int | None = None,
    timing_ms: float | None = None,
    **kwargs: Any,
) -> None:
    """Specialized TRACE logging for discovery operations."""
    context = TraceContext(
        operation=f"discovery_{operation}",
        module="discovery",
        timing_ms=timing_ms,
        metadata={
            "entity_count": entity_count,
            **kwargs,
        },
    )
    logger.trace(f"Discovery {operation}", context)

# Legacy compatibility function
def get_logger(name: str, level: LogLevel = LogLevel.TRACE) -> FlextEnterpriseLogger:
    """Get enterprise Singer SDK logger instance - legacy compatibility."""
    return get_singer_logger(name)

# Default configuration
configure_singer_logging()

# Module-level logger for immediate use
logger = get_singer_logger(__name__)

# Export main classes and functions
__all__ = [
    "FlextEnterpriseLogger",
    "LogLevel",
    "SingerSDKLogger",
    "TraceContext",
    "TraceOperationContext",
    "configure_singer_logging",
    "get_logger",
    "get_singer_logger",
    "logger",
    "trace_authentication",
    "trace_discovery_operation",
    "trace_singer_operation",
    "trace_stream_operation",
    "trace_wms_api_call",
]

