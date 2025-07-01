"""Advanced 5-Level Logging System for Oracle WMS Singer Tap.

This module implements enterprise-grade logging with 5-level system.
ZERO TOLERANCE for mock/fallback implementations - production-ready logging only.

Architecture:
    - Centralized logger factory with consistent configuration
    - Performance-optimized with structured logging
    - CLI integration for runtime log level control
    - Thread-safe with correlation IDs for distributed tracing
    - TRACE-heavy implementation for detailed debugging

Logging Levels:
    - TRACE (5): Most verbose - function entry/exit, variable states, SQL queries
    - DEBUG (10): Debug information - data flows, conditions, API responses
    - INFO (20): Normal operations - major steps, confirmations
    - WARNING (30): Warnings - recoverable issues, deprecations
    - CRITICAL (50): Critical errors - system failures, data corruption
"""

from __future__ import annotations

import contextvars
from datetime import datetime, timezone
from enum import IntEnum
import logging
from pathlib import Path
import sys
import threading
import time
from typing import Any, ClassVar

from rich.console import Console
from rich.logging import RichHandler
from structlog import configure
from structlog import get_logger as _structlog_get_logger
from structlog.processors import CallsiteParameterAdder, JSONRenderer, TimeStamper
from structlog.stdlib import BoundLogger, LoggerFactory, add_log_level


class LogLevel(IntEnum):
    """5-Level logging system with proper ordering and TRACE emphasis."""

    TRACE = 5      # Most verbose - function entry/exit, variable states, SQL queries
    DEBUG = 10     # Debug information - data flows, conditions, API responses
    INFO = 20      # Normal operations - major steps, confirmations
    WARNING = 30   # Warnings - recoverable issues, deprecations
    CRITICAL = 50  # Critical errors - system failures, data corruption


class OracleWMSLogger:
    """Enterprise-grade logger with 5-level system for Oracle WMS operations."""

    _loggers: ClassVar[dict[str, BoundLogger]] = {}
    _lock: ClassVar[threading.RLock] = threading.RLock()
    _configured: ClassVar[bool] = False
    _current_level: ClassVar[LogLevel] = LogLevel.TRACE  # Default to TRACE for maximum visibility
    _console: ClassVar[Console] = Console(stderr=True, force_terminal=True)

    # Context variables for distributed tracing
    _correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
        "correlation_id",
        default="main"
    )
    _request_id: contextvars.ContextVar[str] = contextvars.ContextVar(
        "request_id",
        default="startup"
    )
    _extraction_context: contextvars.ContextVar[str] = contextvars.ContextVar(
        "extraction_context",
        default="general"
    )

    @classmethod
    def configure_logging(
        cls,
        level: LogLevel = LogLevel.TRACE,
        log_file: Path | None = None,
        enable_rich: bool = True,
        enable_json: bool = False,
    ) -> None:
        """Configure the global logging system with enterprise settings."""
        with cls._lock:
            if cls._configured:
                return

            # Add custom TRACE level to stdlib logging
            logging.addLevelName(LogLevel.TRACE, "TRACE")

            # Configure structlog processors
            processors: list[Any] = [
                TimeStamper(fmt="iso"),
                add_log_level,
                CallsiteParameterAdder(),
                cls._add_correlation_context,
                cls._add_oracle_wms_context,
            ]

            if enable_json:
                processors.append(JSONRenderer())

            # Configure stdlib logging with TRACE support
            logging.basicConfig(
                format="%(message)s",
                stream=sys.stderr,
                level=level.value,
            )

            # Add Rich handler for beautiful console output
            if enable_rich:
                rich_handler = RichHandler(
                    console=cls._console,
                    show_time=True,
                    show_level=True,
                    show_path=True,
                    rich_tracebacks=True,
                    markup=True,
                    log_time_format="[%X]",
                )
                # Set Rich handler level to TRACE for maximum detail
                rich_handler.setLevel(LogLevel.TRACE)
                logging.getLogger().addHandler(rich_handler)

            # Configure file logging if specified
            if log_file:
                log_file.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(LogLevel.TRACE)  # File gets everything
                file_handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s | %(levelname)8s | %(name)s | %(message)s"
                    )
                )
                logging.getLogger().addHandler(file_handler)

            # Configure structlog
            configure(
                processors=processors,
                wrapper_class=BoundLogger,
                logger_factory=LoggerFactory(),
                cache_logger_on_first_use=True,
            )

            cls._current_level = level
            cls._configured = True

    @classmethod
    def _add_correlation_context(cls, _logger: Any, _name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        """Add correlation context to log entries."""
        event_dict["correlation_id"] = cls._correlation_id.get()
        event_dict["request_id"] = cls._request_id.get()
        event_dict["extraction_context"] = cls._extraction_context.get()
        event_dict["thread_id"] = threading.get_ident()
        return event_dict

    @classmethod
    def _add_oracle_wms_context(cls, _logger: Any, name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        """Add Oracle WMS specific context to log entries."""
        event_dict["service"] = "oracle-wms-tap"
        event_dict["component"] = name.split(".")[-1] if "." in name else name
        event_dict["timestamp_ns"] = time.time_ns()
        return event_dict

    @classmethod
    def create_logger(cls, name: str) -> OracleWMSLoggerInstance:
        """Get a configured logger instance for the given name."""
        if not cls._configured:
            cls.configure_logging()

        with cls._lock:
            if name not in cls._loggers:
                struct_logger = _structlog_get_logger(name)
                cls._loggers[name] = struct_logger

            return OracleWMSLoggerInstance(cls._loggers[name], name)

    @classmethod
    def set_level(cls, level: LogLevel) -> None:
        """Change the global logging level at runtime."""
        with cls._lock:
            cls._current_level = level
            logging.getLogger().setLevel(level.value)
            # Update all handlers
            for handler in logging.getLogger().handlers:
                handler.setLevel(level.value)

    @classmethod
    def set_correlation_id(cls, correlation_id: str) -> None:
        """Set correlation ID for distributed tracing."""
        cls._correlation_id.set(correlation_id)

    @classmethod
    def set_request_id(cls, request_id: str) -> None:
        """Set request ID for request tracing."""
        cls._request_id.set(request_id)

    @classmethod
    def set_extraction_context(cls, context: str) -> None:
        """Set extraction context (entity name, sync type, etc.)."""
        cls._extraction_context.set(context)

    @classmethod
    def get_current_level(cls) -> LogLevel:
        """Get current logging level."""
        return cls._current_level


class OracleWMSLoggerInstance:
    """Logger instance with 5-level methods and Oracle WMS specific optimizations."""

    def __init__(self, struct_logger: BoundLogger, name: str) -> None:
        """Initialize logger instance."""
        self._logger = struct_logger
        self._name = name
        self._start_times: dict[str, float] = {}
        self._sql_queries: list[dict[str, Any]] = []

    def trace(self, message: str, **kwargs: Any) -> None:
        """Log TRACE level - function entry/exit, variable states, SQL queries."""
        if OracleWMSLogger.get_current_level() <= LogLevel.TRACE:
            # Use native structlog info method with TRACE level marker
            self._logger.info(
                message,
                level="TRACE",
                logger_name=self._name,
                trace_marker="🔍",
                **kwargs
            )

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log DEBUG level - data flows, conditions, API responses."""
        if OracleWMSLogger.get_current_level() <= LogLevel.DEBUG:
            self._logger.info(
                message,
                level="DEBUG",
                logger_name=self._name,
                debug_marker="🐛",
                **kwargs
            )

    def info(self, message: str, **kwargs: Any) -> None:
        """Log INFO level - Normal operations, major steps, confirmations."""
        if OracleWMSLogger.get_current_level() <= LogLevel.INFO:
            self._logger.info(
                message,
                level="INFO",
                logger_name=self._name,
                info_marker="INFO",
                **kwargs
            )

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log WARNING level - Recoverable issues, deprecations."""
        if OracleWMSLogger.get_current_level() <= LogLevel.WARNING:
            self._logger.warning(
                message,
                level="WARNING",
                logger_name=self._name,
                warning_marker="⚠️",
                **kwargs
            )

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log CRITICAL level - System failures, data corruption."""
        self._logger.error(
            message,
            level="CRITICAL",
            logger_name=self._name,
            critical_marker="🚨",
            **kwargs
        )

    def exception(self, message: str, exc_info: bool = True, **kwargs: Any) -> None:
        """Log exception with full traceback."""
        self._logger.exception(
            message,
            exc_info=exc_info,
            level="CRITICAL",
            logger_name=self._name,
            exception_marker="❌",
            **kwargs
        )

    # Oracle WMS specific logging methods

    def trace_function_entry(self, function_name: str, **kwargs: Any) -> None:
        """Trace function entry with parameters."""
        self.trace(
            f"🔍 ENTRY: {function_name}",
            function=function_name,
            entry_type="function_entry",
            **kwargs
        )

    def trace_function_exit(self, function_name: str, result: Any = None, **kwargs: Any) -> None:
        """Trace function exit with result."""
        result_info: dict[str, Any] = {}
        if result is not None:
            if hasattr(result, "__len__"):
                try:
                    result_info["result_length"] = len(result)
                except TypeError:
                    result_info["result_length"] = 0
            result_info["result_type"] = type(result).__name__

        self.trace(
            f"🔍 EXIT: {function_name}",
            function=function_name,
            entry_type="function_exit",
            **result_info,
            **kwargs
        )

    def trace_sql_query(self, query: str, params: dict[str, Any] | None = None, duration_ms: float | None = None) -> None:
        """Trace SQL query execution with parameters and performance."""
        query_info = {
            "query_type": "sql_execution",
            "query_preview": query[:100] + "..." if len(query) > 100 else query,
            "query_length": len(query),
        }

        if params:
            query_info["param_count"] = len(params)
            query_info["params"] = params

        if duration_ms is not None:
            query_info["duration_ms"] = duration_ms

        self.trace(
            f"🔍 SQL: {query_info['query_preview']}",
            **query_info
        )

    def trace_api_request(self, url: str, method: str = "GET", params: dict[str, Any] | None = None) -> None:
        """Trace API request details."""
        self.trace(
            f"🔍 API REQUEST: {method} {url}",
            api_method=method,
            api_url=url,
            api_params=params,
            request_type="api_request"
        )

    def trace_api_response(self, url: str, status_code: int, response_size: int, duration_ms: float) -> None:
        """Trace API response details."""
        self.trace(
            f"🔍 API RESPONSE: {status_code} ({response_size} bytes, {duration_ms:.2f}ms)",
            api_url=url,
            status_code=status_code,
            response_size=response_size,
            duration_ms=duration_ms,
            request_type="api_response"
        )

    def trace_data_processing(self, operation: str, record_count: int, entity: str | None = None) -> None:
        """Trace data processing operations."""
        self.trace(
            f"🔍 DATA PROCESSING: {operation} - {record_count} records",
            operation=operation,
            record_count=record_count,
            entity=entity,
            processing_type="data_operation"
        )

    def trace_variable_state(self, variable_name: str, value: Any, context: str | None = None) -> None:
        """Trace variable state for debugging."""
        value_info: dict[str, Any] = {
            "variable_name": variable_name,
            "value_type": type(value).__name__,
            "context": context or "general"
        }

        # Safely represent the value
        if hasattr(value, "__len__") and not isinstance(value, str):
            try:
                value_info["value_length"] = len(value)
                value_info["value_preview"] = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
            except TypeError:
                value_info["value_length"] = 0
                value_info["value_preview"] = str(value)
        else:
            value_info["value"] = value

        # Build display value safely
        if "value" in value_info:
            display_value = value_info["value"]
        else:
            value_type = value_info.get("value_type", "unknown")
            value_length = value_info.get("value_length", "N/A")
            display_value = f"{value_type}[{value_length}]"

        self.trace(
            f"🔍 VAR STATE: {variable_name} = {display_value}",
            **value_info
        )

    def start_operation(self, operation: str) -> None:
        """Start timing an operation for performance monitoring."""
        self._start_times[operation] = time.perf_counter()
        self.trace(f"🔍 OPERATION START: {operation}")

    def end_operation(self, operation: str, **kwargs: Any) -> None:
        """End timing an operation and log duration."""
        if operation in self._start_times:
            duration = time.perf_counter() - self._start_times[operation]
            del self._start_times[operation]
            self.debug(
                f"🐛 OPERATION COMPLETE: {operation}",
                duration_ms=round(duration * 1000, 2),
                operation=operation,
                **kwargs
            )
        else:
            self.warning(f"⚠️ Operation {operation} was not started or already ended")

    def log_extraction_metrics(self, entity: str, records_extracted: int, pages_processed: int, duration_ms: float) -> None:
        """Log extraction metrics for monitoring."""
        rate = records_extracted / (duration_ms / 1000) if duration_ms > 0 else 0
        self.info(
            f"EXTRACTION COMPLETE: {entity}",
            entity=entity,
            records_extracted=records_extracted,
            pages_processed=pages_processed,
            duration_ms=duration_ms,
            extraction_rate=round(rate, 2),
            extraction_type="metrics"
        )


def get_logger(name: str) -> OracleWMSLoggerInstance:
    """Get a configured Oracle WMS logger instance.

    Args:
        name: Logger name, typically __name__

    Returns:
        Configured logger instance with 5-level support and Oracle WMS optimizations
    """
    return OracleWMSLogger.create_logger(name)


def configure_cli_logging(level: str = "TRACE", log_file_path: str | None = None) -> None:
    """Configure logging for CLI usage with level control.

    Args:
        level: Log level string (TRACE, DEBUG, INFO, WARNING, CRITICAL)
        log_file_path: Optional path for log file output
    """
    level_map = {
        "TRACE": LogLevel.TRACE,
        "DEBUG": LogLevel.DEBUG,
        "INFO": LogLevel.INFO,
        "WARNING": LogLevel.WARNING,
        "CRITICAL": LogLevel.CRITICAL,
    }

    log_level = level_map.get(level.upper(), LogLevel.TRACE)  # Default to TRACE

    # Configure with file output for CLI
    log_file = None
    if log_file_path:
        log_file = Path(log_file_path)
    else:
        log_file = Path("logs") / f"oracle_wms_tap_{datetime.now(timezone.utc).strftime('%Y%m%d')}.log"

    OracleWMSLogger.configure_logging(
        level=log_level,
        log_file=log_file,
        enable_rich=True,
        enable_json=False,
    )

    # Set extraction context for CLI
    OracleWMSLogger.set_extraction_context("cli_extraction")


def set_log_level(level: str) -> None:
    """Set logging level at runtime.

    Args:
        level: Log level string (TRACE, DEBUG, INFO, WARNING, CRITICAL)
    """
    level_map = {
        "TRACE": LogLevel.TRACE,
        "DEBUG": LogLevel.DEBUG,
        "INFO": LogLevel.INFO,
        "WARNING": LogLevel.WARNING,
        "CRITICAL": LogLevel.CRITICAL,
    }

    log_level = level_map.get(level.upper(), LogLevel.TRACE)
    OracleWMSLogger.set_level(log_level)


__all__ = [
    "LogLevel",
    "OracleWMSLogger",
    "configure_cli_logging",
    "get_logger",
    "set_log_level"
]
