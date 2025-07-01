"""Advanced error recovery and resilience patterns for Oracle WMS TAP.

This module implements enterprise-grade error recovery with:
- Advanced circuit breaker patterns
- Exponential backoff with jitter
- Bulkhead isolation patterns
- Real-world error scenario handling
- Adaptive retry strategies
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from enum import Enum
import logging
import random
import time
from typing import Any, Callable, TypeVar

import httpx

from .enhanced_logging import get_enhanced_logger


# Type variable for generic functions
T = TypeVar("T")

logger = logging.getLogger(__name__)
enhanced_logger = get_enhanced_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Available recovery actions."""

    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    ESCALATE = "escalate"
    IGNORE = "ignore"


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class ErrorContext:
    """Enhanced error context with comprehensive metadata."""

    def __init__( # noqa: D107
        self,
        error_type: str,
        severity: ErrorSeverity,
        message: str,
        attempt_count: int = 0,
        metadata: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
        correlation_id: str | None = None,
    ) -> None:
        self.error_type = error_type
        self.severity = severity
        self.message = message
        self.attempt_count = attempt_count
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now() # noqa: DTZ005
        self.correlation_id = correlation_id or self._generate_correlation_id()

    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for error tracking."""
        return f"err_{int(time.time() * 1000)}_{random.randint(1000, 9999)}" # noqa: S311

    def to_dict(self) -> dict[str, Any]:
        """Convert error context to dictionary for logging."""
        return {
            "error_type": self.error_type,
            "severity": self.severity.value,
            "message": self.message,
            "attempt_count": self.attempt_count,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }


class RecoveryStrategy:
    """Recovery strategy configuration."""

    def __init__( # noqa: D107
        self,
        action: RecoveryAction,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter_enabled: bool = True,
        conditions: dict[str, Any] | None = None,
    ) -> None:
        self.action = action
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter_enabled = jitter_enabled
        self.conditions = conditions or {}

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt with exponential backoff and jitter."""
        if attempt <= 0:
            return 0

        # Exponential backoff
        delay = self.initial_delay * (self.backoff_multiplier ** (attempt - 1))
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd
        if self.jitter_enabled:
            jitter = delay * 0.1 * random.random()  # Up to 10% jitter # noqa: S311
            delay += jitter

        return delay


class AdvancedCircuitBreaker:
    """Advanced circuit breaker with adaptive thresholds."""

    def __init__( # noqa: D107
        self,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout: float = 60.0,
        sliding_window_size: int = 100,
        minimum_requests: int = 10,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.sliding_window_size = sliding_window_size
        self.minimum_requests = minimum_requests

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: datetime | None = None
        self.request_history: list[bool] = []  # True for success, False for failure

    def call(self, func: Callable[[], T]) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                msg = "Circuit breaker is OPEN"
                raise CircuitBreakerOpenError(msg)

        try:
            result = func()
            self._record_success()
            return result
        except Exception:
            self._record_failure()
            raise

    def _record_success(self) -> None:
        """Record successful operation."""
        self.success_count += 1
        self.request_history.append(True)
        self._trim_history()

        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker CLOSED - service recovered")

    def _record_failure(self) -> None:
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now() # noqa: DTZ005
        self.request_history.append(False)
        self._trim_history()

        if self.state in {CircuitState.CLOSED, CircuitState.HALF_OPEN}:
            if self._should_open():
                self.state = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker OPENED after {self.failure_count} failures"
                )

    def _should_open(self) -> bool:
        """Determine if circuit should open based on failure patterns."""
        if len(self.request_history) < self.minimum_requests:
            return False

        # Calculate failure rate in sliding window
        recent_requests = self.request_history[-self.sliding_window_size :]
        failure_rate = len([r for r in recent_requests if not r]) / len(recent_requests)

        # Open if failure rate exceeds threshold
        threshold_rate = self.failure_threshold / self.sliding_window_size
        return failure_rate >= threshold_rate

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return True

        time_since_failure = datetime.now() - self.last_failure_time # noqa: DTZ005
        return time_since_failure.total_seconds() >= self.timeout

    def _trim_history(self) -> None:
        """Keep request history within sliding window size."""
        if len(self.request_history) > self.sliding_window_size:
            self.request_history = self.request_history[-self.sliding_window_size :]

    @property
    def failure_rate(self) -> float:
        """Calculate current failure rate."""
        if not self.request_history:
            return 0.0

        failures = len([r for r in self.request_history if not r])
        return failures / len(self.request_history)


class BulkheadIsolation:
    """Bulkhead pattern for resource isolation."""

    def __init__(self, max_concurrent_requests: int = 10) -> None: # noqa: D107
        self.max_concurrent_requests = max_concurrent_requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.active_requests = 0

    async def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with bulkhead isolation."""
        async with self.semaphore:
            self.active_requests += 1
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)
            finally:
                self.active_requests -= 1

    @property
    def utilization(self) -> float:
        """Get current resource utilization."""
        return self.active_requests / self.max_concurrent_requests


class AdvancedErrorRecoveryManager:
    """Advanced error recovery manager with comprehensive strategies."""

    def __init__(self, config: dict[str, Any]) -> None: # noqa: D107
        enhanced_logger.trace("🔧 Initializing Advanced Error Recovery Manager")
        self.config = config
        
        enhanced_logger.trace("🚪 Setting up circuit breaker with thresholds: %d/%d",
                             config.get("circuit_breaker_failure_threshold", 5),
                             config.get("circuit_breaker_success_threshold", 3))
        self.circuit_breaker = AdvancedCircuitBreaker(
            failure_threshold=config.get("circuit_breaker_failure_threshold", 5),
            success_threshold=config.get("circuit_breaker_success_threshold", 3),
            timeout=config.get("circuit_breaker_timeout", 60.0),
        )
        
        enhanced_logger.trace("🛡️ Setting up bulkhead isolation with max concurrent: %d",
                             config.get("max_concurrent_requests", 10))
        self.bulkhead = BulkheadIsolation(
            max_concurrent_requests=config.get("max_concurrent_requests", 10)
        )

        # Error pattern learning
        self.error_patterns: dict[str, list[ErrorContext]] = {}
        self.adaptive_strategies: dict[str, RecoveryStrategy] = {}

        # Initialize default strategies
        enhanced_logger.trace("⚙️ Initializing default recovery strategies")
        self._initialize_default_strategies()
        enhanced_logger.trace("✅ Advanced Error Recovery Manager initialization complete")

    def _initialize_default_strategies(self) -> None:
        """Initialize default recovery strategies."""
        self.adaptive_strategies = {
            "network_error": RecoveryStrategy(
                action=RecoveryAction.RETRY,
                max_attempts=3,
                initial_delay=1.0,
                max_delay=30.0,
                backoff_multiplier=2.0,
            ),
            "timeout_error": RecoveryStrategy(
                action=RecoveryAction.RETRY,
                max_attempts=2,
                initial_delay=2.0,
                max_delay=60.0,
                backoff_multiplier=1.5,
            ),
            "authentication_error": RecoveryStrategy(
                action=RecoveryAction.ESCALATE,
                max_attempts=1,
            ),
            "rate_limit_error": RecoveryStrategy(
                action=RecoveryAction.RETRY,
                max_attempts=5,
                initial_delay=5.0,
                max_delay=300.0,
                backoff_multiplier=1.2,
            ),
            "server_error": RecoveryStrategy(
                action=RecoveryAction.CIRCUIT_BREAK,
                max_attempts=2,
                initial_delay=10.0,
            ),
            "data_error": RecoveryStrategy(
                action=RecoveryAction.FALLBACK,
                max_attempts=1,
            ),
        }

    async def handle_error_with_recovery(
        self,
        error: Exception,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Handle error with advanced recovery strategies."""
        error_context = self._create_error_context(error)
        self._learn_error_pattern(error_context)

        strategy = self._select_recovery_strategy(error_context)

        enhanced_logger.trace(
            "🛠️ Handling error with strategy: %s for error: %s",
            strategy.action.value, error_context.error_type
        )
        enhanced_logger.trace("📄 Error context details: %s", error_context.to_dict())
        logger.info(
            "Handling error with strategy: %s", strategy.action.value,
            extra={"error_context": error_context.to_dict()},
        )

        if strategy.action == RecoveryAction.RETRY:
            return await self._execute_retry_strategy(
                error_context, strategy, operation, *args, **kwargs
            )
        if strategy.action == RecoveryAction.FALLBACK:
            return await self._execute_fallback_strategy(error_context)
        if strategy.action == RecoveryAction.CIRCUIT_BREAK:
            return await self._execute_circuit_break_strategy(error_context)
        if strategy.action == RecoveryAction.ESCALATE:
            return await self._execute_escalation_strategy(error_context)
        # IGNORE strategy
        logger.warning("Ignoring error: %s", error_context.message)
        return None

    def _create_error_context(self, error: Exception) -> ErrorContext:
        """Create comprehensive error context."""
        error_type = self._classify_error_type(error)
        severity = self._determine_error_severity(error)

        metadata = {
            "exception_type": type(error).__name__,
            "exception_args": str(error.args) if error.args else "",
        }

        # Add HTTP-specific metadata
        if isinstance(error, httpx.HTTPStatusError):
            metadata.update(
                {
                    "status_code": str(error.response.status_code),
                    "response_text": error.response.text[:500],  # Limit size
                    "request_url": str(error.request.url),
                    "request_method": error.request.method,
                }
            )
        elif isinstance(error, httpx.RequestError):
            metadata.update(
                {
                    "request_url": str(error.request.url)
                    if error.request
                    else "unknown",
                    "request_method": error.request.method
                    if error.request
                    else "unknown",
                }
            )

        return ErrorContext(
            error_type=error_type,
            severity=severity,
            message=str(error),
            metadata=metadata,
        )

    def _classify_error_type(self, error: Exception) -> str:
        """Classify error into recovery categories."""
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            if status_code == 401:
                return "authentication_error"
            if status_code == 429:
                return "rate_limit_error"
            if 500 <= status_code < 600:
                return "server_error"
            if 400 <= status_code < 500:
                return "client_error"
        elif isinstance(error, (httpx.TimeoutException, asyncio.TimeoutError)):
            return "timeout_error"
        elif isinstance(error, (httpx.NetworkError, httpx.ConnectError)):
            return "network_error"
        elif isinstance(error, (ValueError, TypeError, KeyError)):
            return "data_error"

        return "unknown_error"

    def _determine_error_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity for prioritization."""
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            if status_code == 401:
                return ErrorSeverity.CRITICAL
            if status_code == 429:
                return ErrorSeverity.MEDIUM
            if 500 <= status_code < 600:
                return ErrorSeverity.HIGH
            return ErrorSeverity.MEDIUM
        if isinstance(error, (httpx.TimeoutException, asyncio.TimeoutError)):
            return ErrorSeverity.MEDIUM
        if isinstance(error, (httpx.NetworkError, httpx.ConnectError)):
            return ErrorSeverity.HIGH

        return ErrorSeverity.LOW

    def _learn_error_pattern(self, error_context: ErrorContext) -> None:
        """Learn from error patterns to improve recovery strategies."""
        error_type = error_context.error_type

        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = []

        self.error_patterns[error_type].append(error_context)

        # Keep only recent errors (last 100)
        if len(self.error_patterns[error_type]) > 100:
            self.error_patterns[error_type] = self.error_patterns[error_type][-100:]

        # Adapt strategies based on patterns
        self._adapt_strategy_for_error_type(error_type)

    def _adapt_strategy_for_error_type(self, error_type: str) -> None:
        """Adapt recovery strategy based on historical patterns."""
        if error_type not in self.error_patterns:
            return

        recent_errors = self.error_patterns[error_type][-20:]  # Last 20 errors

        if len(recent_errors) < 5:
            return  # Not enough data

        # Calculate average failure rate
        failure_rate = len(recent_errors) / 20

        # Adapt strategy based on failure patterns
        if error_type in self.adaptive_strategies:
            strategy = self.adaptive_strategies[error_type]

            if failure_rate > 0.5:  # High failure rate
                # Increase delays and reduce attempts
                strategy.initial_delay = min(strategy.initial_delay * 1.2, 30.0)
                strategy.max_attempts = max(strategy.max_attempts - 1, 1)
            elif failure_rate < 0.1:  # Low failure rate
                # Decrease delays and increase attempts
                strategy.initial_delay = max(strategy.initial_delay * 0.9, 0.5)
                strategy.max_attempts = min(strategy.max_attempts + 1, 5)

    def _select_recovery_strategy(
        self, error_context: ErrorContext
    ) -> RecoveryStrategy:
        """Select appropriate recovery strategy."""
        error_type = error_context.error_type

        if error_type in self.adaptive_strategies:
            return self.adaptive_strategies[error_type]

        # Default strategy for unknown errors
        return RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_attempts=2,
            initial_delay=1.0,
        )

    async def _execute_retry_strategy(
        self,
        error_context: ErrorContext,
        strategy: RecoveryStrategy,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute retry strategy with exponential backoff."""
        for attempt in range(1, strategy.max_attempts + 1):
            if attempt > 1:
                delay = strategy.calculate_delay(attempt - 1)
                logger.info("Retrying in %s seconds (attempt %s)", f"{delay:.2f}", attempt)
                await asyncio.sleep(delay)

            try:
                # Use bulkhead isolation for retries
                return await self.bulkhead.execute(operation, *args, **kwargs)
            except Exception as retry_error:
                error_context.attempt_count = attempt

                if attempt == strategy.max_attempts:
                    logger.exception("Retry strategy failed after %s attempts", attempt)
                    raise

                logger.warning(
                    f"Retry attempt {attempt} failed: {retry_error}",
                    extra={"correlation_id": error_context.correlation_id},
                )
        return None

    async def _execute_fallback_strategy(self, error_context: ErrorContext) -> Any:
        """Execute fallback strategy - PRODUCTION: Fail explicitly, no fake data."""
        enhanced_logger.critical(
            "❌ Fallback strategy triggered for error: %s - FAILING EXPLICITLY",
            error_context.error_type
        )
        logger.critical("Fallback strategy not allowed in production: %s", error_context.error_type)
        
        # PRODUCTION: Never return fake data - always fail explicitly
        raise ProductionFallbackNotAllowedError(
            f"Fallback strategy not allowed in production for error: {error_context.error_type}"
        )

    async def _execute_circuit_break_strategy(self, error_context: ErrorContext) -> Any:
        """Execute circuit breaker strategy."""
        logger.warning("Circuit breaker activated for: %s", error_context.error_type)
        self.circuit_breaker._record_failure()

        msg = f"Circuit breaker opened due to: {error_context.message}"
        raise CircuitBreakerOpenError(msg)

    async def _execute_escalation_strategy(self, error_context: ErrorContext) -> Any:
        """Execute escalation strategy."""
        logger.critical(
            f"Escalating error: {error_context.error_type}",
            extra={"error_context": error_context.to_dict()},
        )

        # In real implementation, this would notify REDACTED_LDAP_BIND_PASSWORDistrators,
        # send alerts, or trigger incident management
        raise CriticalErrorRequiresEscalation(error_context.message)

    def get_health_metrics(self) -> dict[str, Any]:
        """Get current health and recovery metrics."""
        return {
            "circuit_breaker": {
                "state": self.circuit_breaker.state.value,
                "failure_count": self.circuit_breaker.failure_count,
                "failure_rate": self.circuit_breaker.failure_rate,
            },
            "bulkhead": {
                "utilization": self.bulkhead.utilization,
                "active_requests": self.bulkhead.active_requests,
            },
            "error_patterns": {
                error_type: len(errors)
                for error_type, errors in self.error_patterns.items()
            },
            "adaptive_strategies": {
                error_type: {
                    "action": strategy.action.value,
                    "max_attempts": strategy.max_attempts,
                    "initial_delay": strategy.initial_delay,
                }
                for error_type, strategy in self.adaptive_strategies.items()
            },
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""


class CriticalErrorRequiresEscalation(Exception):
    """Exception for errors requiring escalation."""


class ProductionFallbackNotAllowedError(Exception):
    """Exception raised when fallback strategies are attempted in production."""


# Factory function for easy integration
def create_advanced_error_recovery(
    config: dict[str, Any],
) -> AdvancedErrorRecoveryManager:
    """Create advanced error recovery manager with configuration."""
    return AdvancedErrorRecoveryManager(config)
