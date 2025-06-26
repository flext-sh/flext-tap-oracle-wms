"""Comprehensive monitoring and metrics for Oracle WMS TAP.

This module provides real-time monitoring, performance metrics collection,
health checks, alerting capabilities, and operational insights for the
Oracle WMS Singer TAP implementation.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

import psutil
from typing_extensions import Self

if TYPE_CHECKING:
    from collections.abc import Callable


logger = logging.getLogger(__name__)


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

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop timing and record metric."""
        duration_ms = (time.time() - self.start_time) * 1000
        self.collector.record_timer(self.name, duration_ms)


class MetricsCollector:
    """Collects and manages performance metrics."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize metrics collector.

        Args:
        ----
            config: Configuration dictionary

        """
        self.config = config
        self.metrics_config = config.get("metrics", {})

        # Metrics storage
        self._metrics: dict[str, deque[MetricPoint]] = defaultdict(
            lambda: deque(maxlen=1000),
        )
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = defaultdict(float)
        self._timers: dict[str, list[float]] = defaultdict(list)

        # Configuration
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

        # Background collection task
        self._collection_task: asyncio.Task[None] | None = None
        self._running = False

        logger.info("Metrics collector initialized (enabled: %s)", self.enabled)

    def start_collection(self) -> None:
        """Start background metrics collection."""
        if not self.enabled:
            logger.debug("Metrics collection disabled, not starting")
            return

        if self._collection_task and not self._collection_task.done():
            logger.warning("Metrics collection already running")
            return

        self._running = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Started background metrics collection")

    async def stop_collection(self) -> None:
        """Stop background metrics collection."""
        self._running = False

        if self._collection_task:
            self._collection_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._collection_task

        logger.info("Stopped background metrics collection")

    async def _collection_loop(self) -> None:
        """Background metrics collection loop."""
        try:
            while self._running:
                await asyncio.sleep(self.collection_interval)
                if self._running:
                    await self._collect_system_metrics()
        except asyncio.CancelledError:
            logger.debug("Metrics collection loop cancelled")
        except Exception as e:
            logger.exception("Error in metrics collection loop: %s", e)

    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        try:
            # Memory usage
            process = psutil.Process()
            memory_info = process.memory_info()

            self.record_gauge("system.memory.rss_mb", memory_info.rss / 1024 / 1024)
            self.record_gauge("system.memory.vms_mb", memory_info.vms / 1024 / 1024)
            self.record_gauge("system.cpu.percent", process.cpu_percent())

            # Async tasks
            asyncio.get_event_loop()
            tasks = [task for task in asyncio.all_tasks() if not task.done()]
            self.record_gauge("system.async.active_tasks", len(tasks))

        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            logger.warning("Error collecting system metrics: %s", e)

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
        if not self.enabled:
            return

        self._counters[name] += value

        # Store metric point
        point = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            value=float(value),
            tags=tags or {},
            metadata={"type": "counter"},
        )
        self._metrics[name].append(point)

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
        if not self.enabled:
            return

        self._gauges[name] = value

        # Store metric point
        point = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            value=value,
            tags=tags or {},
            metadata={"type": "gauge"},
        )
        self._metrics[name].append(point)

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
        if not self.enabled:
            return

        self._timers[name].append(duration_ms)

        # Keep only last 100 timer values
        if len(self._timers[name]) > 100:
            self._timers[name] = self._timers[name][-100:]

        # Store metric point
        point = MetricPoint(
            timestamp=datetime.now(timezone.utc),
            value=duration_ms,
            tags=tags or {},
            metadata={"type": "timer"},
        )
        self._metrics[name].append(point)

    def start_timer(self, name: str) -> TimerContext:
        """Start a timer context for measuring duration.

        Args:
        ----
            name: Timer metric name

        Returns:
        -------
            Timer context manager

        """
        return TimerContext(self, name)

    def get_counter(self, name: str) -> int:
        """Get current counter value."""
        return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> float:
        """Get current gauge value."""
        return self._gauges.get(name, 0.0)

    def get_timer_stats(self, name: str) -> dict[str, float]:
        """Get timer statistics.

        Args:
        ----
            name: Timer metric name

        Returns:
        -------
            Dictionary with min, max, avg, count statistics

        """
        values = self._timers.get(name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}

        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values),
        }

    def get_metrics_snapshot(self) -> dict[str, Any]:
        """Get current metrics snapshot.

        Returns
        -------
            Dictionary with all current metrics

        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "timers": {name: self.get_timer_stats(name) for name in self._timers},
        }

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
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        points = self._metrics.get(name, deque())
        return [point for point in points if point.timestamp >= cutoff_time]


class TimerContext:
    """Context manager for timing operations."""

    def __init__(self, collector: MetricsCollector, name: str) -> None:
        """Initialize timer context.

        Args:
        ----
            collector: Metrics collector instance
            name: Timer name

        """
        self.collector = collector
        self.name = name
        self.start_time: float | None = None

    def __enter__(self) -> Self:
        self.start_time = time.time()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.record_timer(self.name, duration_ms)


class HealthMonitor:
    """Monitors system health and performs health checks."""

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
        self.config = config
        self.metrics = metrics_collector

        # Health checks registry
        self._health_checks: dict[str, HealthCheck] = {}

        # Health status
        self._overall_health = True
        self._last_health_check = None

        # Configuration
        self.check_interval = 60  # seconds
        self._check_task: asyncio.Task[None] | None = None
        self._running = False

        # Register default health checks
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default health checks."""
        # Basic connectivity check
        self.register_check(
            "connectivity",
            "Oracle WMS API connectivity",
            self._check_api_connectivity,
        )

        # Memory usage check
        self.register_check(
            "memory_usage",
            "Memory usage within limits",
            self._check_memory_usage,
        )

        # Active tasks check
        self.register_check(
            "async_tasks",
            "Async tasks within limits",
            self._check_async_tasks,
        )

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
        self._health_checks[name] = HealthCheck(
            name=name,
            description=description,
            check_function=check_function,
        )
        logger.debug("Registered health check: %s", name)

    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        if self._check_task and not self._check_task.done():
            logger.warning("Health monitoring already running")
            return

        self._running = True
        self._check_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started background health monitoring")

    async def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        self._running = False

        if self._check_task:
            self._check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._check_task

        logger.info("Stopped background health monitoring")

    async def _monitoring_loop(self) -> None:
        """Background health monitoring loop."""
        try:
            while self._running:
                await asyncio.sleep(self.check_interval)
                if self._running:
                    await self.run_health_checks()
        except asyncio.CancelledError:
            logger.debug("Health monitoring loop cancelled")
        except Exception as e:
            logger.exception("Error in health monitoring loop: %s", e)

    async def run_health_checks(self) -> dict[str, bool]:
        """Run all health checks.

        Returns
        -------
            Dictionary with check results

        """
        results: dict[str, bool] = {}
        overall_healthy = True

        for check in self._health_checks.values():
            if not check.enabled:
                continue

            try:
                # Run health check
                result = check.check_function()
                check.last_check = datetime.now(timezone.utc)
                check.last_result = result

                if result:
                    check.consecutive_failures = 0
                else:
                    check.consecutive_failures += 1
                    overall_healthy = False

                results[check.name] = result

                # Record metrics
                self.metrics.record_gauge(
                    f"health.{check.name}",
                    1.0 if result else 0.0,
                    tags={"check": check.name},
                )

            except Exception as e:
                logger.exception("Error running health check %s: %s", check.name, e)
                check.consecutive_failures += 1
                results[check.name] = False
                overall_healthy = False

                self.metrics.record_gauge(
                    f"health.{check.name}",
                    0.0,
                    tags={"check": check.name, "error": "exception"},
                )

        self._overall_health = overall_healthy
        self._last_health_check = datetime.now(timezone.utc)

        # Record overall health
        self.metrics.record_gauge("health.overall", 1.0 if overall_healthy else 0.0)

        return results

    def get_health_status(self) -> dict[str, Any]:
        """Get current health status.

        Returns
        -------
            Dictionary with health status

        """
        status: dict[str, Any] = {
            "overall_healthy": self._overall_health,
            "last_check": (
                self._last_health_check.isoformat() if self._last_health_check else None
            ),
            "checks": {},
        }

        for check in self._health_checks.values():
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

        return status

    def _check_api_connectivity(self) -> bool:
        """Check Oracle WMS API connectivity."""
        # This would normally make a lightweight API call
        # For now, return True (would be implemented with actual API check)
        return True

    def _check_memory_usage(self) -> bool:
        """Check memory usage is within acceptable limits."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            # Alert if memory usage > 512MB
            return memory_mb < 512
        except Exception:
            return False

    def _check_async_tasks(self) -> bool:
        """Check async task count is reasonable."""
        try:
            asyncio.get_event_loop()
            active_tasks = len(
                [task for task in asyncio.all_tasks() if not task.done()],
            )

            # Alert if more than 50 active tasks
            return active_tasks < 50
        except Exception:
            return False


class AlertManager:
    """Manages alerts and notifications."""

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
        self.config = config
        self.metrics = metrics_collector

        # Alerts registry
        self._alerts: dict[str, Alert] = {}

        # Alert configuration
        self.check_interval = 30  # seconds
        self._alert_task: asyncio.Task[None] | None = None
        self._running = False

        # Register default alerts
        self._register_default_alerts()

    def _register_default_alerts(self) -> None:
        """Register default alerts."""
        # High memory usage alert
        self.register_alert(
            "high_memory_usage",
            "Memory usage exceeds threshold",
            lambda value: value > 400,  # > 400MB
            "WARNING",
            400.0,
            "system.memory.rss_mb",
        )

        # High task count alert
        self.register_alert(
            "high_task_count",
            "Too many active async tasks",
            lambda value: value > 30,
            "WARNING",
            30.0,
            "system.async.active_tasks",
        )

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
        self._alerts[name] = Alert(
            name=name,
            description=description,
            condition=condition,
            severity=severity,
            threshold=threshold,
            metric_name=metric_name,
        )
        logger.debug("Registered alert: %s", name)

    def start_monitoring(self) -> None:
        """Start background alert monitoring."""
        if self._alert_task and not self._alert_task.done():
            logger.warning("Alert monitoring already running")
            return

        self._running = True
        self._alert_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started background alert monitoring")

    async def stop_monitoring(self) -> None:
        """Stop background alert monitoring."""
        self._running = False

        if self._alert_task:
            self._alert_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._alert_task

        logger.info("Stopped background alert monitoring")

    async def _monitoring_loop(self) -> None:
        """Background alert monitoring loop."""
        try:
            while self._running:
                await asyncio.sleep(self.check_interval)
                if self._running:
                    await self.check_alerts()
        except asyncio.CancelledError:
            logger.debug("Alert monitoring loop cancelled")
        except Exception as e:
            logger.exception("Error in alert monitoring loop: %s", e)

    async def check_alerts(self) -> list[str]:
        """Check all alerts and trigger as needed.

        Returns
        -------
            List of triggered alert names

        """
        triggered: list[str] = []

        for alert in self._alerts.values():
            if not alert.enabled:
                continue

            try:
                # Get current metric value
                current_value = self.metrics.get_gauge(alert.metric_name)

                # Check condition
                should_trigger = alert.condition(current_value)

                if should_trigger and not alert.active:
                    # Trigger alert
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
                    self.metrics.record_counter(
                        "alerts.triggered",
                        tags={"alert": alert.name, "severity": alert.severity},
                    )

                elif not should_trigger and alert.active:
                    # Clear alert
                    alert.active = False
                    logger.info(
                        "ALERT CLEARED: %s (value: %s)",
                        alert.name,
                        current_value,
                    )

                    # Record alert cleared metric
                    self.metrics.record_counter(
                        "alerts.cleared",
                        tags={"alert": alert.name, "severity": alert.severity},
                    )

            except Exception as e:
                logger.exception("Error checking alert %s: %s", alert.name, e)

        return triggered

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get list of active alerts.

        Returns
        -------
            List of active alert dictionaries

        """
        return [
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


class PerformanceProfiler:
    """Profiles performance of TAP operations."""

    def __init__(self, metrics_collector: MetricsCollector) -> None:
        """Initialize performance profiler.

        Args:
        ----
            metrics_collector: Metrics collector instance

        """
        self.metrics = metrics_collector
        self._active_profiles: dict[str, float] = {}

    def start_profile(self, operation: str) -> str:
        """Start profiling an operation.

        Args:
        ----
            operation: Operation name

        Returns:
        -------
            Profile ID

        """
        profile_id = f"{operation}_{int(time.time() * 1000000)}"
        self._active_profiles[profile_id] = time.time()
        return profile_id

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
        if profile_id not in self._active_profiles:
            logger.warning("Profile ID not found: %s", profile_id)
            return 0.0

        start_time = self._active_profiles.pop(profile_id)
        duration_ms = (time.time() - start_time) * 1000

        # Extract operation from profile_id
        operation = profile_id.split("_")[0]

        # Record timing metric
        tags = {"operation": operation}
        if entity_name:
            tags["entity"] = entity_name

        self.metrics.record_timer(
            f"performance.{operation}.duration_ms",
            duration_ms,
            tags,
        )

        # Record rate metrics if record count provided
        if record_count is not None:
            records_per_second = (
                record_count / (duration_ms / 1000) if duration_ms > 0 else 0
            )
            self.metrics.record_gauge(
                f"performance.{operation}.records_per_second",
                records_per_second,
                tags,
            )

        return duration_ms


class TAPMonitor:
    """Main monitoring coordinator for Oracle WMS TAP."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize TAP monitor.

        Args:
        ----
            config: Configuration dictionary

        """
        self.config = config

        # Initialize components
        self.metrics = MetricsCollector(config)
        self.health = HealthMonitor(config, self.metrics)
        self.alerts = AlertManager(config, self.metrics)
        self.profiler = PerformanceProfiler(self.metrics)

        logger.info("TAP monitoring initialized")

    async def start_monitoring(self) -> None:
        """Start all monitoring components."""
        self.metrics.start_collection()
        self.health.start_monitoring()
        self.alerts.start_monitoring()
        logger.info("All monitoring components started")

    async def stop_monitoring(self) -> None:
        """Stop all monitoring components."""
        await self.metrics.stop_collection()
        await self.health.stop_monitoring()
        await self.alerts.stop_monitoring()
        logger.info("All monitoring components stopped")

    def get_monitoring_status(self) -> dict[str, Any]:
        """Get comprehensive monitoring status.

        Returns
        -------
            Dictionary with monitoring status

        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": self.metrics.get_metrics_snapshot(),
            "health": self.health.get_health_status(),
            "active_alerts": self.alerts.get_active_alerts(),
            "monitoring_enabled": self.metrics.enabled,
        }

    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format.

        Args:
        ----
            format_type: Export format ("json", "prometheus")

        Returns:
        -------
            Formatted metrics string

        """
        if format_type == "json":
            return json.dumps(self.get_monitoring_status(), indent=2)
        if format_type == "prometheus":
            return self._export_prometheus_format()
        msg = f"Unsupported export format: {format_type}"
        raise ValueError(msg)

    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        lines: list[str] = []
        snapshot = self.metrics.get_metrics_snapshot()

        # Export counters
        for name, value in snapshot["counters"].items():
            safe_name = name.replace(".", "_").replace("-", "_")
            lines.extend((f"# TYPE {safe_name} counter", f"{safe_name} {value}"))

        # Export gauges
        for name, value in snapshot["gauges"].items():
            safe_name = name.replace(".", "_").replace("-", "_")
            lines.extend((f"# TYPE {safe_name} gauge", f"{safe_name} {value}"))

        # Export timer summaries
        for name, stats in snapshot["timers"].items():
            safe_name = name.replace(".", "_").replace("-", "_")
            lines.extend(
                (
                    f"# TYPE {safe_name} summary",
                    f"{safe_name}_count {stats['count']}",
                    f"{safe_name}_sum {stats['avg'] * stats['count']}",
                )
            )

        return "\n".join(lines)
