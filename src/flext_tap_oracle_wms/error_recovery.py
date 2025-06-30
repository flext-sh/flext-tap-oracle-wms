"""Advanced error handling and recovery mechanisms for Oracle WMS TAP."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
import logging
import operator
import time
from typing import Any, Callable

import httpx


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Available recovery actions."""

    RETRY = "retry"
    SKIP = "skip"
    FALLBACK = "fallback"
    ABORT = "abort"
    ESCALATE = "escalate"


@dataclass
class ErrorContext:
    """Context information for an error."""

    error_type: str
    severity: ErrorSeverity
    message: str
    entity_name: str | None = None
    record_id: str | None = None
    attempt_count: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryStrategy:
    """Strategy for recovering from an error."""

    action: RecoveryAction
    max_attempts: int = 3
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0
    fallback_function: Callable[..., Any] | None = None
    condition_checker: Callable[[ErrorContext], bool] | None = None


class ErrorRecoveryManager:
    """Manages error handling and recovery for the WMS TAP."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize error recovery manager.

        Args:
        ----
            config: Configuration dictionary

        """
        self.config = config
        self.error_history: list[ErrorContext] = []
        self.recovery_strategies: dict[str, RecoveryStrategy] = {}
        self.circuit_breaker_state: dict[str, dict[str, Any]] = {}

        # Configuration
        self.max_error_history = config.get("max_error_history", 1000)
        self.circuit_breaker_enabled = config.get("circuit_breaker_enabled", True)
        self.global_retry_limit = config.get("global_retry_limit", 10)

        # Register default strategies
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register default recovery strategies."""
        # Network errors - retry with exponential backoff
        self.recovery_strategies["network_error"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_attempts=5,
            backoff_multiplier=2.0,
            initial_delay=1.0,
        )

        # Rate limiting - wait and retry
        self.recovery_strategies["rate_limit"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_attempts=3,
            backoff_multiplier=3.0,
            initial_delay=5.0,
        )

        # Authentication errors - escalate immediately
        self.recovery_strategies["auth_error"] = RecoveryStrategy(
            action=RecoveryAction.ESCALATE, max_attempts=1
        )

        # Server errors - retry with longer delays
        self.recovery_strategies["server_error"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_attempts=3,
            backoff_multiplier=2.5,
            initial_delay=10.0,
        )

        # Data validation errors - skip record
        self.recovery_strategies["data_validation"] = RecoveryStrategy(
            action=RecoveryAction.SKIP, max_attempts=1
        )

        # Configuration errors - abort immediately
        self.recovery_strategies["config_error"] = RecoveryStrategy(
            action=RecoveryAction.ABORT, max_attempts=1
        )

    def classify_error(
        self, error: Exception, context: dict[str, Any] | None = None
    ) -> ErrorContext:
        """Classify an error and determine its severity.

        Args:
        ----
            error: The exception that occurred
            context: Additional context about the error

        Returns:
        -------
            Error context with classification

        """
        context = context or {}

        # Classify HTTP errors
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code

            if status_code == 401:
                return ErrorContext(
                    error_type="auth_error",
                    severity=ErrorSeverity.CRITICAL,
                    message="Authentication failed",
                    entity_name=context.get("entity_name"),
                    metadata={"status_code": status_code},
                )
            if status_code == 403:
                return ErrorContext(
                    error_type="auth_error",
                    severity=ErrorSeverity.HIGH,
                    message="Access denied",
                    entity_name=context.get("entity_name"),
                    metadata={"status_code": status_code},
                )
            if status_code == 429:
                return ErrorContext(
                    error_type="rate_limit",
                    severity=ErrorSeverity.MEDIUM,
                    message="Rate limited",
                    entity_name=context.get("entity_name"),
                    metadata={"status_code": status_code},
                )
            if status_code >= 500:
                return ErrorContext(
                    error_type="server_error",
                    severity=ErrorSeverity.HIGH,
                    message=f"Server error {status_code}",
                    entity_name=context.get("entity_name"),
                    metadata={"status_code": status_code},
                )

        # Classify network errors
        elif isinstance(error, (httpx.ConnectError, httpx.TimeoutException)):
            return ErrorContext(
                error_type="network_error",
                severity=ErrorSeverity.MEDIUM,
                message="Network connectivity issue",
                entity_name=context.get("entity_name"),
                metadata={"error_class": error.__class__.__name__},
            )

        # Classify validation errors
        elif isinstance(error, (ValueError, KeyError)):
            return ErrorContext(
                error_type="data_validation",
                severity=ErrorSeverity.LOW,
                message="Data validation failed",
                entity_name=context.get("entity_name"),
                record_id=context.get("record_id"),
                metadata={"error_class": error.__class__.__name__},
            )

        # Default classification
        else:
            return ErrorContext(
                error_type="unknown_error",
                severity=ErrorSeverity.MEDIUM,
                message=str(error),
                entity_name=context.get("entity_name"),
                metadata={"error_class": error.__class__.__name__},
            )
        return None

    def should_recover(
        self, error_context: ErrorContext
    ) -> tuple[bool, RecoveryStrategy | None]:
        """Determine if error recovery should be attempted.

        Args:
        ----
            error_context: Context about the error

        Returns:
        -------
            Tuple of (should_recover, recovery_strategy)

        """
        # Check if we have a strategy for this error type
        strategy = self.recovery_strategies.get(error_context.error_type)
        if not strategy:
            return False, None

        # Check attempt count
        if error_context.attempt_count >= strategy.max_attempts:
            logger.warning(
                "Max recovery attempts reached for %s (attempts: %d)",
                error_context.error_type,
                error_context.attempt_count,
            )
            return False, None

        # Check global retry limit
        total_retries = sum(
            1 for e in self.error_history if e.error_type == error_context.error_type
        )
        if total_retries >= self.global_retry_limit:
            logger.warning(
                "Global retry limit reached for %s (total: %d)",
                error_context.error_type,
                total_retries,
            )
            return False, None

        # Check circuit breaker state
        if self.circuit_breaker_enabled and self._is_circuit_open(error_context):
            logger.warning("Circuit breaker is open for %s", error_context.error_type)
            return False, None

        # Check custom condition if present
        if strategy.condition_checker and not strategy.condition_checker(error_context):
            return False, None

        return True, strategy

    async def handle_error(
        self, error: Exception, operation: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Any:
        """Handle an error with appropriate recovery strategy.

        Args:
        ----
            error: The exception that occurred
            operation: The operation to retry
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
        -------
            Result of successful operation or raises final error

        """
        # Classify the error
        context = kwargs.pop("error_context", {}) if kwargs else {}
        error_context = self.classify_error(error, context)

        # Record the error
        self.record_error(error_context)

        # Determine recovery strategy
        should_recover, strategy = self.should_recover(error_context)

        if not should_recover or not strategy:
            logger.error("No recovery possible for error: %s", error_context.message)
            raise error

        # Execute recovery action
        if strategy.action == RecoveryAction.RETRY:
            return await self._retry_operation(
                error_context, strategy, operation, *args, **kwargs
            )
        if strategy.action == RecoveryAction.SKIP:
            logger.warning("Skipping operation due to error: %s", error_context.message)
            return None
        if strategy.action == RecoveryAction.FALLBACK:
            if strategy.fallback_function:
                logger.info("Using fallback for error: %s", error_context.message)
                return await strategy.fallback_function(*args, **kwargs)
            logger.error(
                "No fallback function defined for %s", error_context.error_type
            )
            raise error
        if strategy.action == RecoveryAction.ESCALATE:
            logger.critical("Escalating error: %s", error_context.message)
            raise error
        if strategy.action == RecoveryAction.ABORT:
            logger.critical("Aborting due to critical error: %s", error_context.message)
            raise error

        # Should not reach here
        raise error

    async def _retry_operation(
        self,
        error_context: ErrorContext,
        strategy: RecoveryStrategy,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Retry an operation with exponential backoff.

        Args:
        ----
            error_context: Context about the error
            strategy: Recovery strategy to use
            operation: Operation to retry
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
        -------
            Result of successful operation

        """
        # Calculate delay
        delay = strategy.initial_delay * (
            strategy.backoff_multiplier**error_context.attempt_count
        )

        logger.info(
            "Retrying operation after %s error (attempt %d/%d, delay: %.1fs)",
            error_context.error_type,
            error_context.attempt_count + 1,
            strategy.max_attempts,
            delay,
        )

        # Wait before retry
        await asyncio.sleep(delay)

        # Update attempt count
        error_context.attempt_count += 1

        # Retry the operation
        try:
            return await operation(*args, **kwargs)
        except Exception as retry_error:
            # If retry fails, check if we can try again
            if error_context.attempt_count < strategy.max_attempts:
                logger.warning(
                    "Retry %d failed, attempting again: %s",
                    error_context.attempt_count,
                    retry_error,
                )
                return await self._retry_operation(
                    error_context, strategy, operation, *args, **kwargs
                )
            logger.exception(
                "All retry attempts exhausted (%d/%d), giving up",
                error_context.attempt_count,
                strategy.max_attempts,
            )
            raise

    def record_error(self, error_context: ErrorContext) -> None:
        """Record an error in the history.

        Args:
        ----
            error_context: Context about the error

        """
        self.error_history.append(error_context)

        # Trim history if too long
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history :]

        # Update circuit breaker state
        if self.circuit_breaker_enabled:
            self._update_circuit_breaker(error_context)

        # Log the error
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
        }.get(error_context.severity, logging.ERROR)

        logger.log(
            log_level,
            "Error recorded: %s (%s) - %s",
            error_context.error_type,
            error_context.severity.value,
            error_context.message,
        )

    def _is_circuit_open(self, error_context: ErrorContext) -> bool:
        """Check if circuit breaker is open for this error type.

        Args:
        ----
            error_context: Context about the error

        Returns:
        -------
            True if circuit is open

        """
        circuit_state = self.circuit_breaker_state.get(error_context.error_type)
        if not circuit_state:
            return False

        # Check if circuit is open
        if circuit_state["state"] == "open":
            # Check if recovery timeout has passed
            if (
                time.time() - circuit_state["last_failure"]
                > circuit_state["recovery_timeout"]
            ):
                circuit_state["state"] = "half_open"
                logger.info(
                    "Circuit breaker entering half-open state for %s",
                    error_context.error_type,
                )
                return False
            return True

        return False

    def _update_circuit_breaker(self, error_context: ErrorContext) -> None:
        """Update circuit breaker state based on error.

        Args:
        ----
            error_context: Context about the error

        """
        error_type = error_context.error_type

        if error_type not in self.circuit_breaker_state:
            self.circuit_breaker_state[error_type] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": 0,
                "failure_threshold": 5,
                "recovery_timeout": 60,
            }

        state = self.circuit_breaker_state[error_type]

        # Record failure
        state["failure_count"] += 1
        state["last_failure"] = time.time()

        # Check if we should open the circuit
        if (
            state["failure_count"] >= state["failure_threshold"]
            and state["state"] == "closed"
        ):
            state["state"] = "open"
            logger.warning(
                "Circuit breaker opened for %s after %d failures",
                error_type,
                state["failure_count"],
            )

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of error history.

        Returns:
        -------
            Summary of errors and recovery actions

        """
        if not self.error_history:
            return {"total_errors": 0, "error_types": {}, "severity_distribution": {}}

        # Count errors by type
        error_types: dict[str, int] = {}
        severity_counts: dict[str, int] = {}

        for error in self.error_history:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            severity_counts[error.severity.value] = (
                severity_counts.get(error.severity.value, 0) + 1
            )

        # Calculate recent error rate (last 5 minutes)
        recent_cutoff = time.time() - 300
        recent_errors = sum(
            1 for e in self.error_history if e.timestamp > recent_cutoff
        )

        return {
            "total_errors": len(self.error_history),
            "recent_errors": recent_errors,
            "error_types": error_types,
            "severity_distribution": severity_counts,
            "circuit_breaker_states": self.circuit_breaker_state,
            "most_common_error": max(error_types.items(), key=operator.itemgetter(1))[0]
            if error_types
            else None,
        }
