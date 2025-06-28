"""Comprehensive logging configuration for TAP Oracle WMS.

This module provides a complete 5-level logging system:
- CRITICAL (50): System failures, fatal errors that stop execution
- WARNING (30): Important issues that don't stop execution
- INFO (20): General operational information
- DEBUG (10): Detailed information for troubleshooting
- TRACE (5): Custom level for extremely detailed tracing

FEATURES:
- Structured logging with context information
- Performance tracking and metrics
- Error context capture with stack traces
- Configurable output formats (console, file, JSON)
- Thread-safe operation
- Memory-efficient for large data extractions
"""

from __future__ import annotations

from datetime import datetime, timezone
import functools
import inspect
import logging
import logging.handlers
import os
from pathlib import Path
import sys
import threading
import time
import traceback
from typing import Any, Callable


# Custom TRACE level (lower than DEBUG)
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


class TraceLogger(logging.Logger):
    """Extended logger with TRACE level support."""

    def trace(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log trace level message with extremely detailed information."""
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, message, args, **kwargs)


# Set custom logger class
logging.setLoggerClass(TraceLogger)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records."""

    def __init__(self, context: dict[str, Any] | None = None) -> None:
        """Initialize context filter.

        Args:
            context: Additional context to include in logs
        """
        super().__init__()
        self.context = context or {}
        self._thread_local = threading.local()

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context information to log record."""
        # Add basic context
        record.thread_name = threading.current_thread().name
        record.process_id = os.getpid()
        record.timestamp_iso = datetime.now(timezone.utc).isoformat()

        # Add custom context
        for key, value in self.context.items():
            setattr(record, key, value)

        # Add thread-local context if available
        if hasattr(self._thread_local, "context"):
            for key, value in self._thread_local.context.items():
                setattr(record, key, value)

        # Add caller information for trace level
        if record.levelno <= TRACE_LEVEL:
            frame = inspect.currentframe()
            try:
                # Go up the stack to find the actual caller
                for _ in range(10):  # Safety limit
                    frame = frame.f_back
                    if frame is None:
                        break

                    # Skip logging framework frames
                    filename = frame.f_code.co_filename
                    if "logging" not in filename and "trace" not in filename.lower():
                        record.caller_file = os.path.basename(filename)
                        record.caller_line = frame.f_lineno
                        record.caller_func = frame.f_code.co_name
                        break
            finally:
                del frame

        return True

    def set_thread_context(self, context: dict[str, Any]) -> None:
        """Set context for current thread."""
        if not hasattr(self._thread_local, "context"):
            self._thread_local.context = {}
        self._thread_local.context.update(context)

    def clear_thread_context(self) -> None:
        """Clear context for current thread."""
        if hasattr(self._thread_local, "context"):
            self._thread_local.context.clear()


class PerformanceTracker:
    """Track performance metrics and timing information."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize performance tracker.

        Args:
            logger: Logger instance to use for output
        """
        self.logger = logger
        self._timers: dict[str, float] = {}
        self._counters: dict[str, int] = {}
        self._lock = threading.Lock()

    def start_timer(self, name: str) -> None:
        """Start a performance timer."""
        with self._lock:
            self._timers[name] = time.perf_counter()
            self.logger.trace("⏱️ Started timer: %s", name)

    def end_timer(self, name: str, context: dict[str, Any] | None = None) -> float:
        """End a performance timer and return duration."""
        end_time = time.perf_counter()

        with self._lock:
            start_time = self._timers.pop(name, end_time)
            duration = end_time - start_time

        if context:
            self.logger.info("⏱️ Timer '%s': %.4fs | Context: %s", name, duration, context)
        else:
            self.logger.info("⏱️ Timer '%s': %.4fs", name, duration)

        return duration

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter."""
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value

        if self.logger.isEnabledFor(TRACE_LEVEL):
            self.logger.trace("📊 Counter '%s': +%d = %d", name, value, self._counters[name])

    def get_counter(self, name: str) -> int:
        """Get current counter value."""
        with self._lock:
            return self._counters.get(name, 0)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of all metrics."""
        with self._lock:
            return {
                "counters": self._counters.copy(),
                "active_timers": list(self._timers.keys()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    def log_metrics_summary(self) -> None:
        """Log summary of all collected metrics."""
        summary = self.get_metrics_summary()
        self.logger.info("📊 Metrics Summary: %s", summary)


class ErrorContextCapture:
    """Capture detailed error context and stack traces."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize error context capture.

        Args:
            logger: Logger instance to use for output
        """
        self.logger = logger

    def capture_exception(
        self,
        exc: Exception,
        context: dict[str, Any] | None = None,
        level: int = logging.ERROR,
    ) -> dict[str, Any]:
        """Capture detailed exception information."""
        exc_info = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "exception_args": exc.args,
            "traceback": traceback.format_exc(),
            "context": context or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "thread_name": threading.current_thread().name,
            "process_id": os.getpid(),
        }

        # Add exception chain information
        if exc.__cause__:
            exc_info["caused_by"] = {
                "type": type(exc.__cause__).__name__,
                "message": str(exc.__cause__),
            }

        if exc.__context__:
            exc_info["context_exception"] = {
                "type": type(exc.__context__).__name__,
                "message": str(exc.__context__),
            }

        # Log the exception with full context
        self.logger.log(
            level,
            "🚨 Exception captured: %s: %s",
            exc_info["exception_type"],
            exc_info["exception_message"],
            extra={"exception_context": exc_info},
        )

        return exc_info

    def log_critical_error(
        self,
        message: str,
        exc: Exception | None = None,
        context: dict[str, Any] | None = None,
        fatal: bool = False,
    ) -> None:
        """Log critical error with full context."""
        error_data = {
            "message": message,
            "context": context or {},
            "fatal": fatal,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if exc:
            error_data["exception"] = self.capture_exception(exc, context, logging.CRITICAL)

        self.logger.critical("💀 CRITICAL ERROR: %s", message, extra={"error_data": error_data})

        if fatal:
            self.logger.critical("💀 FATAL ERROR - System terminating")


class StructuredFormatter(logging.Formatter):
    """Structured formatter for consistent log output."""

    def __init__(
        self,
        include_context: bool = True,
        include_performance: bool = False,
        json_format: bool = False,
    ) -> None:
        """Initialize structured formatter.

        Args:
            include_context: Include context information in output
            include_performance: Include performance metrics
            json_format: Output in JSON format
        """
        self.include_context = include_context
        self.include_performance = include_performance
        self.json_format = json_format

        if json_format:
            super().__init__()
        else:
            # Human-readable format with emojis for level identification
            format_str = (
                "%(timestamp_iso)s | %(levelname)s | "
                "%(name)s:%(lineno)d | %(message)s"
            )
            super().__init__(format_str)

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information."""
        # Add level emoji for visual identification
        level_emojis = {
            "CRITICAL": "💀",
            "ERROR": "🚨",
            "WARNING": "⚠️",
            "INFO": "ℹ️",
            "DEBUG": "🔧",
            "TRACE": "🔍",
        }

        record.level_emoji = level_emojis.get(record.levelname, "📝")

        if self.json_format:
            import json
            log_data = {
                "timestamp": getattr(record, "timestamp_iso", record.created),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "thread": getattr(record, "thread_name", "unknown"),
                "process": getattr(record, "process_id", "unknown"),
            }

            # Add context if available
            if self.include_context:
                for attr in dir(record):
                    if not attr.startswith("_") and attr not in log_data:
                        try:
                            value = getattr(record, attr)
                            if isinstance(value, (str, int, float, bool, list, dict)):
                                log_data[attr] = value
                        except:
                            pass

            return json.dumps(log_data, default=str)
        # Human-readable format
        formatted = super().format(record)

        # Add context information if requested
        if self.include_context:
            context_parts = []

            # Add thread info for concurrent operations
            if hasattr(record, "thread_name") and record.thread_name != "MainThread":
                context_parts.append(f"Thread: {record.thread_name}")

            # Add caller info for trace level
            if (record.levelno <= TRACE_LEVEL and
                hasattr(record, "caller_file") and
                hasattr(record, "caller_func")):
                context_parts.append(f"Caller: {record.caller_file}:{record.caller_line} in {record.caller_func}()")

            # Add custom context
            custom_context = [f"{attr}: {getattr(record, attr)}" for attr in ["entity_name", "operation", "record_count", "api_call_count"] if hasattr(record, attr)]

            if custom_context:
                context_parts.append(" | ".join(custom_context))

            if context_parts:
                formatted += f" | {' | '.join(context_parts)}"

        return f"{record.level_emoji} {formatted}"


class LoggingManager:
    """Central logging manager for TAP Oracle WMS."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize logging manager.

        Args:
            config: Logging configuration dictionary
        """
        self.config = config or {}
        self.context_filter = ContextFilter()
        self.performance_tracker = PerformanceTracker(self._get_logger("performance"))
        self.error_capture = ErrorContextCapture(self._get_logger("errors"))
        self._configured = False

    def configure_logging(self) -> None:
        """Configure comprehensive logging system."""
        if self._configured:
            return

        # Get configuration
        log_level = self.config.get("log_level", "INFO").upper()
        log_format = self.config.get("log_format", "structured")  # structured, json, simple
        log_file = self.config.get("log_file")
        console_output = self.config.get("console_output", True)
        include_context = self.config.get("include_context", True)
        max_file_size = self.config.get("max_file_size", 100 * 1024 * 1024)  # 100MB
        backup_count = self.config.get("backup_count", 5)

        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(TRACE_LEVEL)  # Capture everything, filter at handler level

        # Clear existing handlers
        root_logger.handlers.clear()

        # Create formatters
        json_formatter = StructuredFormatter(
            include_context=include_context,
            include_performance=True,
            json_format=True,
        )

        structured_formatter = StructuredFormatter(
            include_context=include_context,
            include_performance=True,
            json_format=False,
        )

        simple_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

        # Choose formatter
        formatter_map = {
            "json": json_formatter,
            "structured": structured_formatter,
            "simple": simple_formatter,
        }
        formatter = formatter_map.get(log_format, structured_formatter)

        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level, logging.INFO))
            console_handler.setFormatter(formatter)
            console_handler.addFilter(self.context_filter)
            root_logger.addHandler(console_handler)

        # File handler with rotation
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(TRACE_LEVEL)  # Log everything to file
            file_handler.setFormatter(json_formatter)  # Always use JSON for files
            file_handler.addFilter(self.context_filter)
            root_logger.addHandler(file_handler)

        # Configure specific loggers
        self._configure_tap_loggers()

        self._configured = True

        # Log configuration completion
        logger = self._get_logger("logging_manager")
        logger.info("🔧 Logging configured: level=%s, format=%s, file=%s", log_level, log_format, log_file)

    def _configure_tap_loggers(self) -> None:
        """Configure specific loggers for TAP components."""
        # TAP Oracle WMS specific loggers
        tap_loggers = [
            "tap_oracle_wms",
            "tap_oracle_wms.tap",
            "tap_oracle_wms.streams",
            "tap_oracle_wms.auth",
            "tap_oracle_wms.discovery",
            "tap_oracle_wms.monitoring",
            "tap_oracle_wms.config",
        ]

        for logger_name in tap_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(TRACE_LEVEL)
            # Inherit handlers from root logger

        # Singer SDK loggers (reduce noise)
        singer_loggers = [
            "singer_sdk",
            "singer_sdk.streams",
            "singer_sdk.pagination",
            "singer_sdk.authenticators",
        ]

        for logger_name in singer_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.WARNING)  # Reduce Singer SDK noise

    def _get_logger(self, name: str) -> TraceLogger:
        """Get logger instance with TRACE support."""
        return logging.getLogger(name)

    def get_logger(self, name: str) -> TraceLogger:
        """Get logger for specific component."""
        if not self._configured:
            self.configure_logging()
        return self._get_logger(name)

    def set_context(self, context: dict[str, Any]) -> None:
        """Set global context for all loggers."""
        self.context_filter.context.update(context)

    def set_thread_context(self, context: dict[str, Any]) -> None:
        """Set context for current thread."""
        self.context_filter.set_thread_context(context)

    def clear_thread_context(self) -> None:
        """Clear context for current thread."""
        self.context_filter.clear_thread_context()


# Global logging manager instance
_logging_manager: LoggingManager | None = None


def configure_logging(config: dict[str, Any] | None = None) -> LoggingManager:
    """Configure global logging system."""
    global _logging_manager

    if _logging_manager is None:
        _logging_manager = LoggingManager(config)

    _logging_manager.configure_logging()
    return _logging_manager


def get_logger(name: str) -> TraceLogger:
    """Get logger instance with proper configuration."""
    global _logging_manager

    if _logging_manager is None:
        _logging_manager = LoggingManager()
        _logging_manager.configure_logging()

    # Create logger instance with TRACE support
    logger_instance = logging.getLogger(name)

    # Ensure logger class has trace method
    if not hasattr(logger_instance, "trace"):
        def trace(self, message: str, *args: Any, **kwargs: Any) -> None:
            if self.isEnabledFor(TRACE_LEVEL):
                self._log(TRACE_LEVEL, message, args, **kwargs)

        # Add trace method to logger instance
        import types
        logger_instance.trace = types.MethodType(trace, logger_instance)

    return logger_instance


def log_function_entry_exit(
    logger: TraceLogger | None = None,
    log_args: bool = True,
    log_result: bool = False,
    level: int = TRACE_LEVEL,
) -> Callable:
    """Decorator to log function entry and exit."""
    def decorator(func: Callable) -> Callable:
        nonlocal logger
        if logger is None:
            logger = get_logger(f"{func.__module__}.{func.__qualname__}")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__qualname__}"

            # Log entry
            if log_args:
                args_str = f"args={args}, kwargs={kwargs}"
            else:
                args_str = f"arg_count={len(args)}, kwarg_count={len(kwargs)}"

            logger.log(level, "🔍 ENTER %s(%s)", func_name, args_str)

            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)

                # Log successful exit
                duration = time.perf_counter() - start_time
                if log_result and result is not None:
                    logger.log(level, "🔍 EXIT %s -> %s (%.4fs)", func_name, result, duration)
                else:
                    logger.log(level, "🔍 EXIT %s (%.4fs)", func_name, duration)

                return result

            except Exception as e:
                # Log exception exit
                duration = time.perf_counter() - start_time
                logger.log(level, "🔍 EXIT %s -> EXCEPTION: %s: %s (%.4fs)", func_name, type(e).__name__, e, duration)
                raise

        return wrapper
    return decorator


def performance_monitor(
    operation_name: str | None = None,
    logger: TraceLogger | None = None,
    log_level: int = logging.INFO,
) -> Callable:
    """Decorator to monitor performance of operations."""
    def decorator(func: Callable) -> Callable:
        nonlocal logger, operation_name

        if logger is None:
            logger = get_logger(f"{func.__module__}.{func.__qualname__}")

        if operation_name is None:
            operation_name = f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global _logging_manager

            if _logging_manager:
                _logging_manager.performance_tracker.start_timer(operation_name)

            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)

                duration = time.perf_counter() - start_time
                logger.log(log_level, "⏱️ %s completed in %.4fs", operation_name, duration)

                if _logging_manager:
                    _logging_manager.performance_tracker.end_timer(operation_name)

                return result

            except Exception as e:
                duration = time.perf_counter() - start_time
                logger.exception("⏱️ %s failed after %.4fs: %s", operation_name, duration, e)

                if _logging_manager:
                    _logging_manager.performance_tracker.end_timer(operation_name)
                    _logging_manager.error_capture.capture_exception(
                        e,
                        context={"operation": operation_name, "duration": duration},
                    )

                raise

        return wrapper
    return decorator


def log_exception_context(
    logger: TraceLogger | None = None,
    level: int = logging.ERROR,
    reraise: bool = True,
) -> Callable:
    """Decorator to capture and log exception context."""
    def decorator(func: Callable) -> Callable:
        nonlocal logger

        if logger is None:
            logger = get_logger(f"{func.__module__}.{func.__qualname__}")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                global _logging_manager

                context = {
                    "function": f"{func.__module__}.{func.__qualname__}",
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()) if kwargs else [],
                }

                if _logging_manager:
                    _logging_manager.error_capture.capture_exception(e, context, level)
                else:
                    logger.log(level, "🚨 Exception in %s: %s: %s", context["function"], type(e).__name__, e)

                if reraise:
                    raise

                return None

        return wrapper
    return decorator
