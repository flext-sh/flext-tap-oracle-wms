"""Enhanced 5-level logging system with TRACE emphasis for Oracle WMS TAP.

This module provides a comprehensive logging system with five levels:
- TRACE (5): Most detailed debugging information, emphasized for development
- DEBUG (10): Detailed debugging information
- INFO (20): General information about application flow
- WARNING (30): Warning messages for potential issues
- CRITICAL (50): Critical errors that require immediate attention

The system emphasizes TRACE level logging for comprehensive debugging and monitoring.
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


# Define TRACE level (lower than DEBUG)
TRACE_LEVEL = 5

# Add TRACE level to logging module
logging.addLevelName(TRACE_LEVEL, "TRACE")


class TraceLogger(logging.Logger):
    """Enhanced logger with TRACE level support."""

    def trace(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log with TRACE level - most detailed debugging."""
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, message, args, **kwargs)


# Set custom logger class
logging.setLoggerClass(TraceLogger)


class EnhancedFormatter(logging.Formatter):
    """Enhanced formatter with color support and detailed formatting."""

    # Color codes for different log levels
    COLORS: ClassVar[dict[str, str]] = {
        "TRACE": "\033[36m",  # Cyan
        "DEBUG": "\033[34m",  # Blue
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "CRITICAL": "\033[31m",  # Red
        "RESET": "\033[0m",  # Reset
    }

    def __init__(
        self,
        use_colors: bool = True,
        include_trace_details: bool = True,
    ) -> None:
        """Initialize enhanced formatter.

        Args:
            use_colors: Whether to use color output
            include_trace_details: Whether to include detailed trace information
        """
        super().__init__()
        self.use_colors = use_colors
        self.include_trace_details = include_trace_details

        # Detailed format for TRACE level
        self.trace_format = (
            "{color}[{levelname}] {asctime} | {name} | "
            "{filename}:{lineno} | {funcName}() | "
            "PID:{process} | Thread:{thread} | {message}{reset}"
        )

        # Standard format for other levels
        self.standard_format = (
            "{color}[{levelname}] {asctime} | {name} | "
            "{filename}:{lineno} | {message}{reset}"
        )

        # Minimal format for INFO level
        self.info_format = "{color}[{levelname}] {asctime} | {message}{reset}"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with appropriate detail level."""
        # Add timestamp
        record.asctime = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[
            :-3
        ]

        # Select format based on level
        if record.levelno == TRACE_LEVEL and self.include_trace_details:
            format_str = self.trace_format
        elif record.levelno == logging.INFO:
            format_str = self.info_format
        else:
            format_str = self.standard_format

        # Add colors if enabled
        if self.use_colors and sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, "")
            reset = self.COLORS["RESET"]
        else:
            color = reset = ""

        # Format the message
        try:
            return format_str.format(
                color=color,
                reset=reset,
                levelname=record.levelname,
                asctime=record.asctime,
                name=record.name,
                filename=Path(record.pathname).name,
                lineno=record.lineno,
                funcName=record.funcName,
                process=record.process,
                thread=record.thread,
                message=record.getMessage(),
            )
        except Exception:
            # Fallback to basic formatting
            return f"[{record.levelname}] {record.getMessage()}"


class PerformanceTracer:
    """Performance tracing utility for detailed timing analysis."""

    def __init__(self, logger: TraceLogger, operation_name: str) -> None:
        """Initialize performance tracer.

        Args:
            logger: Logger instance to use
            operation_name: Name of the operation being traced
        """
        self.logger = logger
        self.operation_name = operation_name
        self.start_time: float | None = None
        self.checkpoints: list[tuple[str, float]] = []

    def __enter__(self) -> Self:
        """Start performance tracing."""
        self.start_time = time.perf_counter()
        self.logger.trace(f"🚀 Starting {self.operation_name}")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """End performance tracing."""
        if self.start_time is not None:
            total_time = (time.perf_counter() - self.start_time) * 1000

            if exc_type is None:
                self.logger.trace(
                    f"✅ Completed {self.operation_name} in {total_time:.2f}ms",
                )
            else:
                self.logger.trace(
                    f"❌ Failed {self.operation_name} after "
                    f"{total_time:.2f}ms: {exc_val}",
                )

            # Log checkpoint details if any
            if self.checkpoints:
                self.logger.trace(f"📊 {self.operation_name} checkpoints:")
                prev_time = 0
                for checkpoint_name, checkpoint_time in self.checkpoints:
                    duration = (checkpoint_time - prev_time) * 1000
                    self.logger.trace(f"  ⏱️  {checkpoint_name}: {duration:.2f}ms")
                    prev_time = int(checkpoint_time)

    def checkpoint(self, name: str) -> None:
        """Add a performance checkpoint."""
        if self.start_time is not None:
            checkpoint_time = time.perf_counter() - self.start_time
            self.checkpoints.append((name, checkpoint_time))
            self.logger.trace(f"📍 {self.operation_name} checkpoint: {name}")


def setup_enhanced_logging(
    module_name: str = "tap_oracle_wms",
    level: str | int = "TRACE",
    log_file: str | None = None,
    use_colors: bool = True,
    include_trace_details: bool = True,
    enable_performance_tracing: bool = True,
    disable_trace_logs: bool = True,
) -> TraceLogger:
    """Setup enhanced logging system with 5-level support.

    Args:
        module_name: Name of the module/logger
        level: Logging level (TRACE, DEBUG, INFO, WARNING, CRITICAL)
        log_file: Optional file to log to
        use_colors: Whether to use colored output
        include_trace_details: Whether to include detailed trace information
        enable_performance_tracing: Whether to enable performance tracing
        disable_trace_logs: Whether to disable TRACE level logs
    Returns:
        Configured TraceLogger instance
    """
    # Get logger instance
    logger = logging.getLogger(module_name)
    logger.setLevel(TRACE_LEVEL)  # Always capture all levels

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = EnhancedFormatter(
        use_colors=use_colors,
        include_trace_details=include_trace_details,
    )

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)

    # Set appropriate level
    if isinstance(level, str):
        if level.upper() == "TRACE" and not disable_trace_logs:
            console_level = TRACE_LEVEL
        elif level.upper() == "TRACE" and disable_trace_logs:
            console_level = logging.DEBUG  # Fall back to DEBUG if TRACE disabled
        else:
            console_level = getattr(logging, level.upper(), logging.INFO)
    else:
        console_level = level

    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    # Setup file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(TRACE_LEVEL)  # Always log all levels to file
        logger.addHandler(file_handler)

    # Add performance tracing if enabled
    if enable_performance_tracing:
        logger.trace(f"🔧 Enhanced logging initialized for {module_name}")  # type: ignore[attr-defined]
        logger.trace(f"📊 Console level: {logging.getLevelName(console_level)}")  # type: ignore[attr-defined]
        logger.trace(f"📁 File logging: {'enabled' if log_file else 'disabled'}")  # type: ignore[attr-defined]
        logger.trace(f"🎨 Colors: {'enabled' if use_colors else 'disabled'}")  # type: ignore[attr-defined]
        logger.trace(  # type: ignore[attr-defined]
            f"🔍 Trace details: {'enabled' if include_trace_details else 'disabled'}",
        )

    return logger  # type: ignore[return-value]


def trace_performance(
    operation_name: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for automatic performance tracing.

    Args:
        operation_name: Name of the operation to trace
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get logger from module
            logger = logging.getLogger(func.__module__)

            with PerformanceTracer(logger, f"{operation_name} ({func.__name__})"):  # type: ignore[arg-type]
                return func(*args, **kwargs)

        return wrapper

    return decorator


def get_enhanced_logger(name: str) -> TraceLogger:
    """Get an enhanced logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        TraceLogger instance
    """
    return logging.getLogger(name)  # type: ignore[return-value]


# CLI integration function
def setup_cli_logging(config: dict[str, Any]) -> TraceLogger:
    """Setup logging specifically for CLI usage.

    Args:
        config: Configuration dictionary from CLI
    Returns:
        Configured TraceLogger for CLI usage
    """
    # Determine log level from config
    log_level = config.get("log_level", "INFO").upper()

    # Enable TRACE by default in debug mode
    if config.get("debug"):
        log_level = "TRACE"

    # Setup file logging in debug mode
    log_file = None
    if config.get("debug") or config.get("enable_file_logging"):
        log_file = config.get("log_file", "tap-oracle-wms.log")

    # Setup enhanced logging
    logger = setup_enhanced_logging(
        module_name="tap-oracle-wms-cli",
        level=log_level,
        log_file=log_file,
        use_colors=config.get("use_colors", True),
        include_trace_details=config.get("include_trace_details", True),
        enable_performance_tracing=config.get("enable_performance_tracing", True),
    )

    # Log CLI startup
    logger.trace("🎯 CLI logging system initialized")
    logger.trace("⚙️  Configuration: %s", config)

    return logger
