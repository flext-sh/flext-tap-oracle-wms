"""Comprehensive monitoring and metrics for Oracle WMS TAP.

This module provides real-time monitoring, performance metrics collection,
health checks, alerting capabilities, and operational insights for the
Oracle WMS Singer TAP implementation.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict, deque
import contextlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
import logging
import time
from typing import TYPE_CHECKING, Any

import psutil
from typing_extensions import Self

from .logging_config import (
    TRACE_LEVEL,
    get_logger,
    log_exception_context,
    log_function_entry_exit,
    performance_monitor,
)


if TYPE_CHECKING:
    from collections.abc import Callable
    import types


# Use enhanced logger with TRACE support
logger = get_logger(__name__)

# Constants
MAX_TIMER_VALUES = 100
MEMORY_LIMIT_MB = 512
TASK_LIMIT = 50
MEMORY_ALERT_THRESHOLD_MB = 400
TASK_ALERT_THRESHOLD = 30


@dataclass
class MetricPoint:
    """Individual metric data point."""

    timestamp: datetime
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check definition and results."""

    name: str
    description: str
    check_function: Callable[[], bool]
    last_check: datetime | None = None
    last_result: bool | None = None
    consecutive_failures: int = 0
    enabled: bool = True


@dataclass
class Alert:
    """Alert definition and state."""

    name: str
    description: str
    condition: Callable[[float], bool]
    severity: str  # CRITICAL, WARNING, INFO
    threshold: float
    metric_name: str
    last_triggered: datetime | None = None
    active: bool = False
    enabled: bool = True


class TimerContext:
    """Context manager for timing operations."""

    def __init__(self, collector: MetricsCollector, name: str) -> None:
        """Initialize timer context.

        Args:
        ----
            collector: Metrics collector instance
            name: Timer metric name

        """
        self.collector = collector
        self.name = name
        self.start_time: float = 0

    def __enter__(self) -> Self:
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Stop timing and record metric."""
        duration_ms = (time.time() - self.start_time) * 1000
        self.collector.record_timer(self.name, duration_ms)


class MetricsCollector:
    """Collects and manages performance metrics."""

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("metrics_collector_init")
    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize metrics collector.

        Args:
        ----
            config: Configuration dictionary

        """
        logger.info("Initializing Oracle WMS Metrics Collector")
        logger.debug("Metrics config validation starting")
        logger.trace("Setting up metrics collector instance variables")

        self.config = config
        self.metrics_config = config.get("metrics", {})
        logger.debug("Metrics configuration loaded: %d settings",
                     len(self.metrics_config))

        # Metrics storage
        logger.trace("Initializing metrics storage structures")
        self._metrics: dict[str, deque[MetricPoint]] = defaultdict(
            lambda: deque(maxlen=1000),
        )
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = defaultdict(float)
        self._timers: dict[str, list[float]] = defaultdict(list)
        logger.trace("Metrics storage structures initialized")

        # Configuration
        logger.trace("Processing metrics collection configuration")
        self.enabled = self.metrics_config.get("enabled", False)
        self.collection_interval = self.metrics_config.get("interval_seconds", 60)
        self.include_entity_metrics = self.metrics_config.get(
            "include_entity_metrics",
            True,
        )
        self.include_performance_metrics = self.metrics_config.get(
            "include_performance_metrics",
            True,
        )
        logger.debug("Metrics config: enabled=%s, interval=%ds, entity_metrics=%s",
                    self.enabled, self.collection_interval,
                    self.include_entity_metrics)

        # Background collection task
        logger.trace("Initializing background collection task variables")
        self._collection_task: asyncio.Task[None] | None = None
        self._running = False
        logger.trace("Background task variables initialized")

        logger.info("Oracle WMS Metrics Collector initialized successfully")
        logger.debug("Metrics collector ready (enabled: %s)", self.enabled)

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("metrics_collection_start")
    def start_collection(self) -> None:
        """Start background metrics collection."""
        logger.debug("Starting metrics collection background task")
        logger.trace("Checking metrics collection enabled state")

        if not self.enabled:
            logger.debug("Metrics collection disabled, not starting")
            logger.trace("Metrics collection skipped (disabled in config)")
            return

        logger.trace("Checking if collection task already running")
        if self._collection_task and not self._collection_task.done():
            logger.warning("Metrics collection already running")
            logger.trace("Collection task exists and not done, aborting start")
            return

        logger.debug("Setting up background metrics collection")
        logger.trace("Setting running flag and creating asyncio task")
        self._running = True
        self._collection_task = asyncio.create_task(self._collection_loop())

        logger.info("Background metrics collection started successfully")
        logger.debug("Collection task created with interval: %ds",
                   self.collection_interval)
        logger.trace("Start collection process completed")
        logger.trace("Metrics collection background task is now active")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("metrics_collection_stop")
    async def stop_collection(self) -> None:
        """Stop background metrics collection."""
        logger.debug("Stopping background metrics collection")
        logger.trace("Setting running flag to False")
        self._running = False

        if self._collection_task:
            logger.debug("Cancelling active collection task")
            logger.trace("Requesting task cancellation")
            self._collection_task.cancel()

            logger.trace("Waiting for task cleanup completion")
            with contextlib.suppress(asyncio.CancelledError):
                await self._collection_task
            logger.debug("Collection task cleanup completed")
        else:
            logger.trace("No active collection task to cancel")

        logger.info("Background metrics collection stopped successfully")
        logger.trace("Metrics collection fully shut down")

    @log_exception_context(reraise=True)
    @performance_monitor("metrics_collection_loop")
    async def _collection_loop(self) -> None:
        """Background metrics collection loop."""
        logger.debug("Starting metrics collection background loop")
        logger.trace("Collection loop entering main execution cycle")

        try:
            loop_iteration = 0
            while self._running:
                logger.trace("Collection loop iteration %d starting", loop_iteration)

                logger.trace("Sleeping for %ds before next collection",
                            self.collection_interval)
                await asyncio.sleep(self.collection_interval)

                if self._running:
                    logger.trace("Collecting system metrics (iteration %d)",
                                loop_iteration)
                    await self._collect_system_metrics()
                    logger.trace("System metrics collection completed")
                else:
                    logger.trace("Running flag false, exiting collection loop")
                    break

                loop_iteration += 1

        except asyncio.CancelledError:
            logger.debug("Metrics collection loop cancelled")
            logger.trace("Collection loop received cancellation signal")
        except Exception:
            logger.exception("Error in metrics collection loop")
            raise

        logger.debug("Metrics collection loop exited")
        logger.trace("Collection loop background execution completed")

    @log_exception_context(reraise=True)
    @performance_monitor("system_metrics_collection")
    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        logger.trace("Starting system metrics collection")

        try:
            logger.trace("Getting process instance for metrics")
            # Memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            logger.trace("Memory info obtained: RSS=%d, VMS=%d",
                        memory_info.rss, memory_info.vms)

            # Convert bytes to MB for readability
            rss_mb = memory_info.rss / 1024 / 1024
            vms_mb = memory_info.vms / 1024 / 1024
            cpu_percent = process.cpu_percent()

            logger.trace("Recording memory metrics: RSS=%.2fMB, VMS=%.2fMB, CPU=%.2f%%",
                        rss_mb, vms_mb, cpu_percent)

            self.record_gauge("system.memory.rss_mb", rss_mb)
            self.record_gauge("system.memory.vms_mb", vms_mb)
            self.record_gauge("system.cpu.percent", cpu_percent)
            logger.debug("System resource metrics recorded successfully")

            # Async tasks
            logger.trace("Collecting async task metrics")
            asyncio.get_event_loop()
            tasks = [task for task in asyncio.all_tasks() if not task.done()]
            active_task_count = len(tasks)

            logger.trace("Active async tasks: %d", active_task_count)
            self.record_gauge("system.async.active_tasks", float(active_task_count))
            logger.debug("Async task metrics recorded successfully")

        except ImportError:
            logger.warning("psutil not available, skipping system metrics collection")
            logger.trace("ImportError: psutil module not installed")
            # psutil not available, skip system metrics
        except Exception as e:
            logger.warning("Error collecting system metrics: %s", str(e))
            logger.exception("Full system metrics collection error details")
            raise

        logger.trace("System metrics collection completed")

    @log_function_entry_exit(log_args=False, log_result=False, level=TRACE_LEVEL)
    @log_exception_context(reraise=True)
    def record_counter(
        self,
        name: str,
        value: int = 1,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a counter metric.

        Args:
        ----
            name: Metric name
            value: Counter increment value
            tags: Optional tags

        """
        logger.trace("Recording counter metric: %s", name)

        if not self.enabled:
            logger.trace("Metrics disabled, skipping counter: %s", name)
            return

        logger.trace("Incrementing counter %s by %d", name, value)
        self._counters[name] += value
        new_total = self._counters[name]
        logger.trace("Counter %s updated: +%d = %d total", name, value, new_total)

        # Store metric point
        logger.trace("Creating metric point for counter: %s", name)
        point = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            value=float(value),
            tags=tags or {},
            metadata={"type": "counter"},
        )
        self._metrics[name].append(point)
        logger.trace("Counter metric point stored: %s", name)

    @log_function_entry_exit(log_args=False, log_result=False, level=TRACE_LEVEL)
    @log_exception_context(reraise=True)
    def record_gauge(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a gauge metric.

        Args:
        ----
            name: Metric name
            value: Gauge value
            tags: Optional tags

        """
        logger.trace("Recording gauge metric: %s", name)

        if not self.enabled:
            logger.trace("Metrics disabled, skipping gauge: %s", name)
            return

        logger.trace("Setting gauge %s to value: %.4f", name, value)
        self._gauges[name] = value
        logger.trace("Gauge %s updated successfully", name)

        # Store metric point
        logger.trace("Creating metric point for gauge: %s", name)
        point = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            value=value,
            tags=tags or {},
            metadata={"type": "gauge"},
        )
        self._metrics[name].append(point)
        logger.trace("Gauge metric point stored: %s", name)

    @log_function_entry_exit(log_args=False, log_result=False, level=TRACE_LEVEL)
    @log_exception_context(reraise=True)
    def record_timer(
        self,
        name: str,
        duration_ms: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a timer metric.

        Args:
        ----
            name: Metric name
            duration_ms: Duration in milliseconds
            tags: Optional tags

        """
        logger.trace("Recording timer metric: %s", name)

        if not self.enabled:
            logger.trace("Metrics disabled, skipping timer: %s", name)
            return

        logger.trace("Adding timer value: %s = %.4fms", name, duration_ms)
        self._timers[name].append(duration_ms)
        timer_count = len(self._timers[name])
        logger.trace("Timer %s now has %d values", name, timer_count)

        # Keep only last MAX_TIMER_VALUES timer values
        if timer_count > MAX_TIMER_VALUES:
            logger.trace("Trimming timer values for %s (>%d entries)",
                        name, MAX_TIMER_VALUES)
            self._timers[name] = self._timers[name][-MAX_TIMER_VALUES:]
            logger.trace("Timer %s trimmed to last %d values", name, MAX_TIMER_VALUES)

        # Store metric point
        logger.trace("Creating metric point for timer: %s", name)
        point = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            value=duration_ms,
            tags=tags or {},
            metadata={"type": "timer"},
        )
        self._metrics[name].append(point)
        logger.trace("Timer metric point stored: %s", name)

    @log_function_entry_exit(log_args=False, log_result=False, level=TRACE_LEVEL)
    @log_exception_context(reraise=True)
    def start_timer(self, name: str) -> TimerContext:
        """Start a timer context for measuring duration.

        Args:
        ----
            name: Timer metric name

        Returns:
        -------
            Timer context manager

        """
        logger.trace("Creating timer context for: %s", name)
        timer_context = TimerContext(self, name)
        logger.trace("Timer context created successfully: %s", name)
        return timer_context

    @log_function_entry_exit(log_args=False, log_result=False, level=TRACE_LEVEL)
    @log_exception_context(reraise=True)
    def get_counter(self, name: str) -> int:
        """Get current counter value."""
        logger.trace("Getting counter value for: %s", name)
        value = self._counters.get(name, 0)
        logger.trace("Counter %s current value: %d", name, value)
        return value

    @log_function_entry_exit(log_args=False, log_result=False, level=TRACE_LEVEL)
    @log_exception_context(reraise=True)
    def get_gauge(self, name: str) -> float:
        """Get current gauge value."""
        logger.trace("Getting gauge value for: %s", name)
        value = self._gauges.get(name, 0.0)
        logger.trace("Gauge %s current value: %.4f", name, value)
        return value

    @log_function_entry_exit(log_args=False, log_result=False, level=TRACE_LEVEL)
    @log_exception_context(reraise=True)
    def get_timer_stats(self, name: str) -> dict[str, float]:
        """Get timer statistics.

        Args:
        ----
            name: Timer metric name

        Returns:
        -------
            Dictionary with min, max, avg, count statistics

        """
        logger.trace("Computing timer statistics for: %s", name)
        values = self._timers.get(name, [])

        if not values:
            logger.trace("No timer values found for %s, returning zeros", name)
            return {"min": 0, "max": 0, "avg": 0, "count": 0}

        logger.trace("Timer %s has %d values for statistics", name, len(values))
        stats = {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values),
        }
        logger.trace("Timer %s statistics: min=%.4f, max=%.4f, avg=%.4f, count=%d",
                    name, stats["min"], stats["max"], stats["avg"], stats["count"])
        return stats

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("metrics_snapshot")
    def get_metrics_snapshot(self) -> dict[str, Any]:
        """Get current metrics snapshot.

        Returns:
        -------
            Dictionary with all current metrics

        """
        logger.debug("Generating metrics snapshot")
        logger.trace("Collecting current metrics state")

        counter_count = len(self._counters)
        gauge_count = len(self._gauges)
        timer_count = len(self._timers)

        logger.trace("Metrics counts: %d counters, %d gauges, %d timers",
                    counter_count, gauge_count, timer_count)

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "timers": {name: self.get_timer_stats(name) for name in self._timers},
        }

        logger.debug("Metrics snapshot generated successfully")
        logger.trace("Snapshot contains %d total metric types", len(snapshot) - 1)
        return snapshot

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("metric_history_query")
    def get_metric_history(self, name: str, minutes: int = 60) -> list[MetricPoint]:
        """Get metric history for specified time period.

        Args:
        ----
            name: Metric name
            minutes: Time period in minutes

        Returns:
        -------
            List of metric points

        """
        logger.debug("Getting metric history for %s (last %d minutes)", name, minutes)
        logger.trace("Calculating cutoff time for history query")

        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        logger.trace("History cutoff time: %s", cutoff_time)

        logger.trace("Retrieving metric points for: %s", name)
        points = self._metrics.get(name, deque())
        total_points = len(points)
        logger.trace("Total metric points available for %s: %d", name, total_points)

        filtered_points = [point for point in points if point.timestamp >= cutoff_time]
        filtered_count = len(filtered_points)

        logger.debug("Metric history for %s: %d points in last %d minutes",
                    name, filtered_count, minutes)
        logger.trace("Filtered %d points from %d total points",
                    filtered_count, total_points)

        return filtered_points


# TimerContext class removed - using the one defined earlier in the file


class HealthMonitor:
    """Monitors system health and performs health checks."""

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("health_monitor_init")
    def __init__(
        self,
        config: dict[str, Any],
        metrics_collector: MetricsCollector,
    ) -> None:
        """Initialize health monitor.

        Args:
        ----
            config: Configuration dictionary
            metrics_collector: Metrics collector instance

        """
        logger.info("Initializing Oracle WMS Health Monitor")
        logger.debug("Health monitor setup starting")
        logger.trace("Setting up health monitor instance variables")

        self.config = config
        self.metrics = metrics_collector
        logger.debug("Health monitor dependencies configured")

        # Health checks registry
        logger.trace("Initializing health checks registry")
        self._health_checks: dict[str, HealthCheck] = {}
        logger.trace("Health checks registry initialized")

        # Health status
        logger.trace("Setting up health status tracking")
        self._overall_health = True
        self._last_health_check = None
        logger.trace("Health status tracking initialized")

        # Configuration
        logger.trace("Setting up health monitor configuration")
        self.check_interval = 60  # seconds
        self._check_task: asyncio.Task[None] | None = None
        self._running = False
        logger.debug("Health monitor config: check_interval=%ds", self.check_interval)

        # Register default health checks
        logger.debug("Registering default health checks")
        logger.trace("Setting up standard health check suite")
        self._register_default_checks()

        logger.info("Oracle WMS Health Monitor initialized successfully")
        logger.debug("Health monitor ready with %d checks", len(self._health_checks))

    @log_exception_context(reraise=True)
    @performance_monitor("register_default_checks")
    def _register_default_checks(self) -> None:
        """Register default health checks."""
        logger.debug("Registering default health checks")
        logger.trace("Setting up standard health check suite")

        # Basic connectivity check
        logger.trace("Registering connectivity health check")
        self.register_check(
            "connectivity",
            "Oracle WMS API connectivity",
            self._check_api_connectivity,
        )

        # Memory usage check
        logger.trace("Registering memory usage health check")
        self.register_check(
            "memory_usage",
            "Memory usage within limits",
            self._check_memory_usage,
        )

        # Active tasks check
        logger.trace("Registering async tasks health check")
        self.register_check(
            "async_tasks",
            "Async tasks within limits",
            self._check_async_tasks,
        )

        logger.debug("Default health checks registered successfully")
        logger.trace("Health check suite setup completed")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    def register_check(
        self,
        name: str,
        description: str,
        check_function: Callable[[], bool],
    ) -> None:
        """Register a new health check.

        Args:
        ----
            name: Check name
            description: Check description
            check_function: Function that returns True if healthy

        """
        logger.debug("Registering health check: %s", name)
        logger.trace("Health check description: %s", description)

        self._health_checks[name] = HealthCheck(
            name=name,
            description=description,
            check_function=check_function,
        )

        total_checks = len(self._health_checks)
        logger.debug("Health check %s registered successfully (%d total)",
                    name, total_checks)
        logger.trace("Health check registry updated")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("health_monitoring_start")
    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        logger.debug("Starting health monitoring background task")
        logger.trace("Checking if health monitoring already running")

        if self._check_task and not self._check_task.done():
            logger.warning("Health monitoring already running")
            logger.trace("Health monitoring task exists and not done, aborting start")
            return

        logger.debug("Setting up background health monitoring")
        logger.trace("Setting running flag and creating monitoring task")
        self._running = True
        self._check_task = asyncio.create_task(self._monitoring_loop())

        logger.info("Background health monitoring started successfully")
        logger.debug("Health monitoring task created with %d checks",
                    len(self._health_checks))
        logger.trace("Health monitoring background task is now active")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("health_monitoring_stop")
    async def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        logger.debug("Stopping background health monitoring")
        logger.trace("Setting health monitoring running flag to False")
        self._running = False

        if self._check_task:
            logger.debug("Cancelling active health monitoring task")
            logger.trace("Requesting health monitoring task cancellation")
            self._check_task.cancel()

            logger.trace("Waiting for health monitoring task cleanup")
            with contextlib.suppress(asyncio.CancelledError):
                await self._check_task
            logger.debug("Health monitoring task cleanup completed")
        else:
            logger.trace("No active health monitoring task to cancel")

        logger.info("Background health monitoring stopped successfully")
        logger.trace("Health monitoring fully shut down")

    @log_exception_context(reraise=True)
    @performance_monitor("health_monitoring_loop")
    async def _monitoring_loop(self) -> None:
        """Background health monitoring loop."""
        logger.debug("Starting health monitoring background loop")
        logger.trace("Health monitoring loop entering main execution cycle")

        try:
            loop_iteration = 0
            while self._running:
                logger.trace("Health monitoring loop iteration %d starting",
                            loop_iteration)

                logger.trace("Sleeping for %ds before next health check",
                            self.check_interval)
                await asyncio.sleep(self.check_interval)

                if self._running:
                    logger.trace("Running health checks (iteration %d)",
                                loop_iteration)
                    await self.run_health_checks()
                    logger.trace("Health checks completed")
                else:
                    logger.trace("Running flag false, exiting health monitoring loop")
                    break

                loop_iteration += 1

        except asyncio.CancelledError:
            logger.debug("Health monitoring loop cancelled")
            logger.trace("Health monitoring loop received cancellation signal")
        except Exception:
            logger.exception("Error in health monitoring loop")
            raise

        logger.debug("Health monitoring loop exited")
        logger.trace("Health monitoring loop background execution completed")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("health_checks_execution")
    async def run_health_checks(self) -> dict[str, bool]:
        """Run all health checks.

        Returns:
        -------
            Dictionary with check results

        """
        logger.debug("Running health checks")
        logger.trace("Starting health check execution cycle")

        results: dict[str, bool] = {}
        overall_healthy = True
        total_checks = len(self._health_checks)
        enabled_checks = 0

        logger.debug("Total health checks available: %d", total_checks)

        for check in self._health_checks.values():
            if not check.enabled:
                logger.trace("Skipping disabled health check: %s", check.name)
                continue

            enabled_checks += 1
            logger.trace("Executing health check: %s", check.name)

            try:
                # Run health check
                result = check.check_function()
                check.last_check = datetime.now(timezone.utc)
                check.last_result = result

                logger.trace("Health check %s result: %s", check.name, result)

                if result:
                    check.consecutive_failures = 0
                    logger.trace("Health check %s passed, reset failure count",
                                check.name)
                else:
                    check.consecutive_failures += 1
                    overall_healthy = False
                    logger.warning("Health check %s failed (consecutive failures: %d)",
                                  check.name, check.consecutive_failures)

                results[check.name] = result
                logger.trace("Health check %s recorded in results", check.name)

                # Record metrics
                logger.trace("Recording metrics for health check: %s", check.name)
                self.metrics.record_gauge(
                    f"health.{check.name}",
                    1.0 if result else 0.0,
                    tags={"check": check.name},
                )
                logger.trace("Metrics recorded for health check: %s", check.name)

            except Exception:
                logger.exception("Error running health check %s", check.name)

                check.consecutive_failures += 1
                results[check.name] = False
                overall_healthy = False

                logger.warning("Health check %s exception failure (consecutive: %d)",
                              check.name, check.consecutive_failures)

                logger.trace("Recording failure metrics for health check: %s",
                            check.name)
                self.metrics.record_gauge(
                    f"health.{check.name}",
                    0.0,
                    tags={"check": check.name, "error": "exception"},
                )
                logger.trace("Failure metrics recorded for health check: %s",
                            check.name)

        logger.debug("Health checks completed: %d enabled checks executed",
                    enabled_checks)

        # Update overall health status
        logger.trace("Updating overall health status")
        self._overall_health = overall_healthy
        self._last_health_check = datetime.now(timezone.utc)
        health_status_text = "HEALTHY" if overall_healthy else "UNHEALTHY"
        logger.debug("Overall health status: %s", health_status_text)

        # Record overall health
        logger.trace("Recording overall health metrics")
        self.metrics.record_gauge("health.overall", 1.0 if overall_healthy else 0.0)
        logger.trace("Overall health metrics recorded")

        logger.debug("Health check cycle completed: %d results", len(results))
        return results

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("health_status_query")
    def get_health_status(self) -> dict[str, Any]:
        """Get current health status.

        Returns:
        -------
            Dictionary with health status

        """
        logger.debug("Getting current health status")
        logger.trace("Building health status summary")

        status: dict[str, Any] = {
            "overall_healthy": self._overall_health,
            "last_check": (
                self._last_health_check.isoformat() if self._last_health_check else None
            ),
            "checks": {},
        }

        logger.trace("Overall health status: %s",
                    "HEALTHY" if self._overall_health else "UNHEALTHY")
        logger.trace("Last health check: %s",
                    status["last_check"] or "Never")

        check_count = 0
        healthy_checks = 0

        for check in self._health_checks.values():
            check_count += 1
            if check.last_result:
                healthy_checks += 1

            logger.trace("Processing health check status: %s", check.name)
            status["checks"][check.name] = {
                "name": check.name,
                "description": check.description,
                "enabled": check.enabled,
                "last_result": check.last_result,
                "last_check": (
                    check.last_check.isoformat() if check.last_check else None
                ),
                "consecutive_failures": check.consecutive_failures,
            }
            logger.trace("Health check %s status: %s (failures: %d)",
                        check.name,
                        "PASS" if check.last_result else "FAIL",
                        check.consecutive_failures)

        logger.debug("Health status compiled: %d/%d checks healthy",
                    healthy_checks, check_count)
        logger.trace("Health status generation completed")
        return status

    @log_exception_context(reraise=False)
    @performance_monitor("api_connectivity_check")
    def _check_api_connectivity(self) -> bool:
        """Check Oracle WMS API connectivity."""
        logger.trace("Performing API connectivity health check")
        # This would normally make a lightweight API call
        # For now, return True (would be implemented with actual API check)
        logger.trace("API connectivity check passed (mock implementation)")
        return True

    @log_exception_context(reraise=False)
    @performance_monitor("memory_usage_check")
    def _check_memory_usage(self) -> bool:
        """Check memory usage is within acceptable limits."""
        logger.trace("Performing memory usage health check")

        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            limit_mb = MEMORY_LIMIT_MB

            logger.trace("Memory usage: %.2fMB (limit: %dMB)", memory_mb, limit_mb)

            # Alert if memory usage > 512MB
            is_healthy = memory_mb < limit_mb

            if not is_healthy:
                logger.warning("Memory usage health check failed: %.2fMB > %dMB",
                              memory_mb, limit_mb)
            else:
                logger.trace("Memory usage health check passed: %.2fMB < %dMB",
                            memory_mb, limit_mb)

        except (OSError, AttributeError) as e:
            logger.warning("Memory usage health check error: %s", str(e))
            logger.trace("Memory usage check failed due to exception")
            return False
        else:
            return is_healthy

    @log_exception_context(reraise=False)
    @performance_monitor("async_tasks_check")
    def _check_async_tasks(self) -> bool:
        """Check async task count is reasonable."""
        logger.trace("Performing async tasks health check")

        try:
            asyncio.get_event_loop()
            active_tasks = len(
                [task for task in asyncio.all_tasks() if not task.done()],
            )
            task_limit = TASK_LIMIT

            logger.trace("Active async tasks: %d (limit: %d)", active_tasks, task_limit)

            # Alert if more than 50 active tasks
            is_healthy = active_tasks < task_limit

            if not is_healthy:
                logger.warning("Async tasks health check failed: %d > %d tasks",
                              active_tasks, task_limit)
            else:
                logger.trace("Async tasks health check passed: %d < %d tasks",
                            active_tasks, task_limit)

        except (OSError, AttributeError) as e:
            logger.warning("Async tasks health check error: %s", str(e))
            logger.trace("Async tasks check failed due to exception")
            return False
        else:
            return is_healthy


class AlertManager:
    """Manages alerts and notifications."""

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("alert_manager_init")
    def __init__(
        self,
        config: dict[str, Any],
        metrics_collector: MetricsCollector,
    ) -> None:
        """Initialize alert manager.

        Args:
        ----
            config: Configuration dictionary
            metrics_collector: Metrics collector instance

        """
        logger.info("Initializing Oracle WMS Alert Manager")
        logger.debug("Alert manager setup starting")
        logger.trace("Setting up alert manager instance variables")

        self.config = config
        self.metrics = metrics_collector
        logger.debug("Alert manager dependencies configured")

        # Alerts registry
        logger.trace("Initializing alerts registry")
        self._alerts: dict[str, Alert] = {}
        logger.trace("Alerts registry initialized")

        # Alert configuration
        logger.trace("Setting up alert manager configuration")
        self.check_interval = 30  # seconds
        self._alert_task: asyncio.Task[None] | None = None
        self._running = False
        logger.debug("Alert manager config: check_interval=%ds", self.check_interval)

        # Register default alerts
        logger.debug("Registering default alerts")
        logger.trace("Setting up standard alert suite")
        self._register_default_alerts()

        logger.info("Oracle WMS Alert Manager initialized successfully")
        logger.debug("Alert manager ready with %d alerts", len(self._alerts))

    @log_exception_context(reraise=True)
    @performance_monitor("register_default_alerts")
    def _register_default_alerts(self) -> None:
        """Register default alerts."""
        logger.debug("Registering default alerts")
        logger.trace("Setting up standard alert suite")

        # High memory usage alert
        logger.trace("Registering high memory usage alert")
        self.register_alert(
            "high_memory_usage",
            "Memory usage exceeds threshold",
            lambda value: value > MEMORY_ALERT_THRESHOLD_MB,  # > 400MB
            "WARNING",
            float(MEMORY_ALERT_THRESHOLD_MB),
            "system.memory.rss_mb",
        )

        # High task count alert
        logger.trace("Registering high task count alert")
        self.register_alert(
            "high_task_count",
            "Too many active async tasks",
            lambda value: value > TASK_ALERT_THRESHOLD,
            "WARNING",
            float(TASK_ALERT_THRESHOLD),
            "system.async.active_tasks",
        )

        logger.debug("Default alerts registered successfully")
        logger.trace("Alert suite setup completed")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    def register_alert(
        self,
        name: str,
        description: str,
        condition: Callable[[float], bool],
        severity: str,
        threshold: float,
        metric_name: str,
    ) -> None:
        """Register a new alert.

        Args:
        ----
            name: Alert name
            description: Alert description
            condition: Function that returns True if alert should trigger
            severity: Alert severity (CRITICAL, WARNING, INFO)
            threshold: Alert threshold value
            metric_name: Metric to monitor

        """
        logger.debug("Registering alert: %s", name)
        logger.trace("Alert details: severity=%s, threshold=%.2f, metric=%s",
                    severity, threshold, metric_name)
        logger.trace("Alert description: %s", description)

        self._alerts[name] = Alert(
            name=name,
            description=description,
            condition=condition,
            severity=severity,
            threshold=threshold,
            metric_name=metric_name,
        )

        total_alerts = len(self._alerts)
        logger.debug("Alert %s registered successfully (%d total)",
                    name, total_alerts)
        logger.trace("Alert registry updated")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("alert_monitoring_start")
    def start_monitoring(self) -> None:
        """Start background alert monitoring."""
        logger.debug("Starting alert monitoring background task")
        logger.trace("Checking if alert monitoring already running")

        if self._alert_task and not self._alert_task.done():
            logger.warning("Alert monitoring already running")
            logger.trace("Alert monitoring task exists and not done, aborting start")
            return

        logger.debug("Setting up background alert monitoring")
        logger.trace("Setting running flag and creating alert monitoring task")
        self._running = True
        self._alert_task = asyncio.create_task(self._monitoring_loop())

        logger.info("Background alert monitoring started successfully")
        logger.debug("Alert monitoring task created with %d alerts",
                    len(self._alerts))
        logger.trace("Alert monitoring background task is now active")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("alert_monitoring_stop")
    async def stop_monitoring(self) -> None:
        """Stop background alert monitoring."""
        logger.debug("Stopping background alert monitoring")
        logger.trace("Setting alert monitoring running flag to False")
        self._running = False

        if self._alert_task:
            logger.debug("Cancelling active alert monitoring task")
            logger.trace("Requesting alert monitoring task cancellation")
            self._alert_task.cancel()

            logger.trace("Waiting for alert monitoring task cleanup")
            with contextlib.suppress(asyncio.CancelledError):
                await self._alert_task
            logger.debug("Alert monitoring task cleanup completed")
        else:
            logger.trace("No active alert monitoring task to cancel")

        logger.info("Background alert monitoring stopped successfully")
        logger.trace("Alert monitoring fully shut down")

    @log_exception_context(reraise=True)
    @performance_monitor("alert_monitoring_loop")
    async def _monitoring_loop(self) -> None:
        """Background alert monitoring loop."""
        logger.debug("Starting alert monitoring background loop")
        logger.trace("Alert monitoring loop entering main execution cycle")

        try:
            loop_iteration = 0
            while self._running:
                logger.trace("Alert monitoring loop iteration %d starting",
                            loop_iteration)

                logger.trace("Sleeping for %ds before next alert check",
                            self.check_interval)
                await asyncio.sleep(self.check_interval)

                if self._running:
                    logger.trace("Checking alerts (iteration %d)",
                                loop_iteration)
                    await self.check_alerts()
                    logger.trace("Alert checks completed")
                else:
                    logger.trace("Running flag false, exiting alert monitoring loop")
                    break

                loop_iteration += 1

        except asyncio.CancelledError:
            logger.debug("Alert monitoring loop cancelled")
            logger.trace("Alert monitoring loop received cancellation signal")
        except Exception:
            logger.exception("Error in alert monitoring loop")
            raise

        logger.debug("Alert monitoring loop exited")
        logger.trace("Alert monitoring loop background execution completed")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("alerts_check_execution")
    async def check_alerts(self) -> list[str]:
        """Check all alerts and trigger as needed.

        Returns:
        -------
            List of triggered alert names

        """
        logger.debug("Checking alerts")
        logger.trace("Starting alert check execution cycle")

        triggered: list[str] = []
        total_alerts = len(self._alerts)
        enabled_alerts = 0

        logger.debug("Total alerts available: %d", total_alerts)

        for alert in self._alerts.values():
            if not alert.enabled:
                logger.trace("Skipping disabled alert: %s", alert.name)
                continue

            enabled_alerts += 1
            logger.trace("Checking alert: %s", alert.name)

            try:
                # Get current metric value
                logger.trace("Getting metric value for alert %s: %s",
                            alert.name, alert.metric_name)
                current_value = self.metrics.get_gauge(alert.metric_name)
                logger.trace("Alert %s metric value: %.4f (threshold: %.4f)",
                            alert.name, current_value, alert.threshold)

                # Check condition
                should_trigger = alert.condition(current_value)
                logger.trace(
                    "Alert %s condition result: %s", alert.name, should_trigger,
                )

                if should_trigger and not alert.active:
                    # Trigger alert
                    logger.trace("Triggering alert: %s", alert.name)
                    alert.active = True
                    alert.last_triggered = datetime.now(timezone.utc)
                    triggered.append(alert.name)

                    logger.warning(
                        "ALERT TRIGGERED: %s - %s (value: %s, threshold: %s)",
                        alert.name,
                        alert.description,
                        current_value,
                        alert.threshold,
                    )

                    # Record alert metric
                    logger.trace("Recording alert triggered metric: %s", alert.name)
                    self.metrics.record_counter(
                        "alerts.triggered",
                        tags={"alert": alert.name, "severity": alert.severity},
                    )
                    logger.trace("Alert triggered metric recorded: %s", alert.name)

                elif not should_trigger and alert.active:
                    # Clear alert
                    logger.trace("Clearing alert: %s", alert.name)
                    alert.active = False
                    logger.info(
                        "ALERT CLEARED: %s (value: %s)",
                        alert.name,
                        current_value,
                    )

                    # Record alert cleared metric
                    logger.trace("Recording alert cleared metric: %s", alert.name)
                    self.metrics.record_counter(
                        "alerts.cleared",
                        tags={"alert": alert.name, "severity": alert.severity},
                    )
                    logger.trace("Alert cleared metric recorded: %s", alert.name)
                else:
                    logger.trace("Alert %s state unchanged (active: %s)",
                                alert.name, alert.active)

            except Exception:
                logger.exception("Error checking alert %s", alert.name)

        logger.debug("Alert checks completed: %d enabled alerts, %d triggered",
                    enabled_alerts, len(triggered))
        logger.trace("Alert check cycle completed")
        return triggered

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("active_alerts_query")
    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get list of active alerts.

        Returns:
        -------
            List of active alert dictionaries

        """
        logger.debug("Getting active alerts")
        logger.trace("Filtering active alerts from registry")

        active_alerts = [
            {
                "name": alert.name,
                "description": alert.description,
                "severity": alert.severity,
                "threshold": alert.threshold,
                "metric_name": alert.metric_name,
                "triggered_at": (
                    alert.last_triggered.isoformat() if alert.last_triggered else None
                ),
            }
            for alert in self._alerts.values()
            if alert.active
        ]

        active_count = len(active_alerts)
        total_count = len(self._alerts)

        logger.debug("Active alerts: %d out of %d total alerts",
                    active_count, total_count)
        logger.trace("Active alerts compilation completed")

        return active_alerts


class PerformanceProfiler:
    """Profiles performance of TAP operations."""

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("performance_profiler_init")
    def __init__(self, metrics_collector: MetricsCollector) -> None:
        """Initialize performance profiler.

        Args:
        ----
            metrics_collector: Metrics collector instance

        """
        logger.info("Initializing Oracle WMS Performance Profiler")
        logger.debug("Performance profiler setup starting")
        logger.trace("Setting up performance profiler instance variables")

        self.metrics = metrics_collector
        self._active_profiles: dict[str, float] = {}

        logger.debug("Performance profiler dependencies configured")
        logger.trace("Active profiles tracking initialized")
        logger.info("Oracle WMS Performance Profiler initialized successfully")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    def start_profile(self, operation: str) -> str:
        """Start profiling an operation.

        Args:
        ----
            operation: Operation name

        Returns:
        -------
            Profile ID

        """
        logger.debug("Starting performance profile for operation: %s", operation)
        logger.trace("Generating profile ID for operation: %s", operation)

        profile_id = f"{operation}_{int(time.time() * 1000000)}"
        self._active_profiles[profile_id] = time.time()

        active_count = len(self._active_profiles)
        logger.debug("Performance profile started: %s (%d active profiles)",
                    profile_id, active_count)
        logger.trace("Profile tracking started for: %s", profile_id)

        return profile_id

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("profile_completion")
    def end_profile(
        self,
        profile_id: str,
        entity_name: str | None = None,
        record_count: int | None = None,
    ) -> float:
        """End profiling and record metrics.

        Args:
        ----
            profile_id: Profile ID from start_profile
            entity_name: Optional entity name for tagging
            record_count: Optional record count for rate calculations

        Returns:
        -------
            Duration in milliseconds

        """
        logger.debug("Ending performance profile: %s", profile_id)
        logger.trace("Looking up profile start time for: %s", profile_id)

        if profile_id not in self._active_profiles:
            logger.warning("Profile ID not found: %s", profile_id)
            logger.trace("Profile ID %s not in active profiles registry", profile_id)
            return 0.0

        logger.trace("Calculating profile duration for: %s", profile_id)
        start_time = self._active_profiles.pop(profile_id)
        duration_ms = (time.time() - start_time) * 1000

        remaining_profiles = len(self._active_profiles)
        logger.debug("Profile completed: %s in %.4fms (%d profiles remaining)",
                    profile_id, duration_ms, remaining_profiles)

        # Extract operation from profile_id
        logger.trace("Extracting operation name from profile ID: %s", profile_id)
        operation = profile_id.split("_")[0]
        logger.trace("Operation extracted: %s", operation)

        # Record timing metric
        logger.trace("Preparing metric tags for operation: %s", operation)
        tags = {"operation": operation}
        if entity_name:
            tags["entity"] = entity_name
            logger.trace("Entity tag added: %s", entity_name)

        logger.trace("Recording timer metric for operation: %s", operation)
        self.metrics.record_timer(
            f"performance.{operation}.duration_ms",
            duration_ms,
            tags,
        )
        logger.debug("Timer metric recorded: %s = %.4fms", operation, duration_ms)

        # Record rate metrics if record count provided
        if record_count is not None:
            logger.trace("Calculating records per second for %d records", record_count)
            records_per_second = (
                record_count / (duration_ms / 1000) if duration_ms > 0 else 0
            )
            logger.trace("Rate calculated: %.2f records/second", records_per_second)

            self.metrics.record_gauge(
                f"performance.{operation}.records_per_second",
                records_per_second,
                tags,
            )
            logger.debug("Rate metric recorded: %s = %.2f records/second",
                        operation, records_per_second)
        else:
            logger.trace("No record count provided, skipping rate metrics")

        logger.debug("Performance profile ended successfully: %s", profile_id)
        return duration_ms


class TAPMonitor:
    """Main monitoring coordinator for Oracle WMS TAP."""

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("tap_monitor_init")
    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize TAP monitor.

        Args:
        ----
            config: Configuration dictionary

        """
        logger.info("Initializing Oracle WMS TAP Monitor")
        logger.debug("TAP monitor setup starting")
        logger.trace("Setting up TAP monitor configuration")

        self.config = config
        logger.debug("TAP monitor configuration loaded")

        # Initialize components
        logger.debug("Initializing monitoring components")
        logger.trace("Creating metrics collector")
        self.metrics = MetricsCollector(config)

        logger.trace("Creating health monitor")
        self.health = HealthMonitor(config, self.metrics)

        logger.trace("Creating alert manager")
        self.alerts = AlertManager(config, self.metrics)

        logger.trace("Creating performance profiler")
        self.profiler = PerformanceProfiler(self.metrics)

        logger.debug("All monitoring components initialized successfully")
        logger.info("Oracle WMS TAP Monitor initialized successfully")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("monitoring_start")
    async def start_monitoring(self) -> None:
        """Start all monitoring components."""
        logger.info("Starting all monitoring components")
        logger.debug("Starting monitoring component suite")

        logger.trace("Starting metrics collection")
        self.metrics.start_collection()
        logger.debug("Metrics collection started")

        logger.trace("Starting health monitoring")
        self.health.start_monitoring()
        logger.debug("Health monitoring started")

        logger.trace("Starting alert monitoring")
        self.alerts.start_monitoring()
        logger.debug("Alert monitoring started")

        logger.info("All monitoring components started successfully")
        logger.trace("Monitoring system fully operational")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("monitoring_stop")
    async def stop_monitoring(self) -> None:
        """Stop all monitoring components."""
        logger.info("Stopping all monitoring components")
        logger.debug("Shutting down monitoring component suite")

        logger.trace("Stopping metrics collection")
        await self.metrics.stop_collection()
        logger.debug("Metrics collection stopped")

        logger.trace("Stopping health monitoring")
        await self.health.stop_monitoring()
        logger.debug("Health monitoring stopped")

        logger.trace("Stopping alert monitoring")
        await self.alerts.stop_monitoring()
        logger.debug("Alert monitoring stopped")

        logger.info("All monitoring components stopped successfully")
        logger.trace("Monitoring system fully shut down")

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("monitoring_status_query")
    def get_monitoring_status(self) -> dict[str, Any]:
        """Get comprehensive monitoring status.

        Returns:
        -------
            Dictionary with monitoring status

        """
        logger.debug("Getting comprehensive monitoring status")
        logger.trace("Collecting status from all monitoring components")

        logger.trace("Getting metrics snapshot")
        metrics_snapshot = self.metrics.get_metrics_snapshot()

        logger.trace("Getting health status")
        health_status = self.health.get_health_status()

        logger.trace("Getting active alerts")
        active_alerts = self.alerts.get_active_alerts()

        status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics_snapshot,
            "health": health_status,
            "active_alerts": active_alerts,
            "monitoring_enabled": self.metrics.enabled,
        }

        logger.debug("Monitoring status compiled: enabled=%s, alerts=%d",
                    status["monitoring_enabled"], len(active_alerts))
        logger.trace("Comprehensive monitoring status generation completed")

        return status

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("metrics_export")
    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format.

        Args:
        ----
            format_type: Export format ("json", "prometheus")

        Returns:
        -------
            Formatted metrics string

        """
        logger.debug("Exporting metrics in format: %s", format_type)
        logger.trace("Starting metrics export process")

        if format_type == "json":
            logger.trace("Exporting metrics in JSON format")
            monitoring_status = self.get_monitoring_status()
            result = json.dumps(monitoring_status, indent=2)
            logger.debug("JSON metrics export completed: %d characters", len(result))
            return result

        if format_type == "prometheus":
            logger.trace("Exporting metrics in Prometheus format")
            result = self._export_prometheus_format()
            logger.debug("Prometheus metrics export completed: %d characters",
                        len(result))
            return result

        error_msg = f"Unsupported export format: {format_type}"
        logger.error("Metrics export failed: %s", error_msg)
        raise ValueError(error_msg)

    @log_exception_context(reraise=True)
    @performance_monitor("prometheus_export")
    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        logger.debug("Converting metrics to Prometheus format")
        logger.trace("Starting Prometheus format generation")

        lines: list[str] = []
        snapshot = self.metrics.get_metrics_snapshot()

        logger.trace("Processing %d counter metrics",
                    len(snapshot["counters"]))

        # Export counters
        for name, value in snapshot["counters"].items():
            safe_name = name.replace(".", "_").replace("-", "_")
            lines.extend((f"# TYPE {safe_name} counter",
                         f"{safe_name} {value}"))
            logger.trace("Counter exported: %s = %s", safe_name, value)

        logger.trace("Processing %d gauge metrics",
                    len(snapshot["gauges"]))

        # Export gauges
        for name, value in snapshot["gauges"].items():
            safe_name = name.replace(".", "_").replace("-", "_")
            lines.extend((f"# TYPE {safe_name} gauge",
                         f"{safe_name} {value}"))
            logger.trace("Gauge exported: %s = %s", safe_name, value)

        logger.trace("Processing %d timer metrics",
                    len(snapshot["timers"]))

        # Export timer summaries
        for name, stats in snapshot["timers"].items():
            safe_name = name.replace(".", "_").replace("-", "_")
            lines.extend(
                (
                    f"# TYPE {safe_name} summary",
                    "{}_count {}".format(safe_name, stats["count"]),
                    "{}_sum {}".format(safe_name, stats["avg"] * stats["count"]),
                ),
            )
            logger.trace("Timer exported: %s (count=%d, sum=%.4f)",
                        safe_name, stats["count"],
                        stats["avg"] * stats["count"])

        result = "\n".join(lines)
        logger.debug("Prometheus format generated: %d lines, %d characters",
                    len(lines), len(result))
        logger.trace("Prometheus format generation completed")

        return result
