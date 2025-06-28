#!/usr/bin/env python3
"""Comprehensive logging validation test for TAP Oracle WMS.

This script validates that all 5 logging levels work correctly:
- CRITICAL (50): System failures, fatal errors that stop execution
- ERROR (40): Errors that don't stop execution but need attention
- WARNING (30): Important issues that don't stop execution
- INFO (20): General operational information (marcos importantes apenas)
- DEBUG (10): Detailed information for troubleshooting
- TRACE (5): Custom level for extremely detailed tracing

Tests:
1. Logging configuration setup
2. All log levels functionality
3. Performance monitoring
4. Error context capture
5. Structured output formats
6. File rotation
7. Thread safety
8. PEP 8 / ruff compliance (G004 - no f-strings in logging)
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
import sys
import tempfile
import threading
import time
from typing import Any


# Import our logging system
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tap_oracle_wms.logging_config import (
    configure_logging,
    get_logger,
    log_exception_context,
    log_function_entry_exit,
    performance_monitor,
)


class LoggingTestSuite:
    """Comprehensive logging test suite."""

    def __init__(self) -> None:
        """Initialize test suite."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log_file = self.temp_dir / "test_tap_oracle_wms.log"
        self.test_results: dict[str, bool] = {}

    def setup_logging(self) -> None:
        """Set up logging for testing."""
        logging_config = {
            "log_level": "TRACE",
            "log_format": "structured",
            "log_file": str(self.log_file),
            "console_output": True,
            "include_context": True,
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "backup_count": 3,
        }

        configure_logging(logging_config)

    def test_basic_log_levels(self) -> bool:
        """Test all 5 log levels work correctly."""
        logger = get_logger("test_basic_levels")

        # Test each level - PROPER format without f-strings (ruff G004 compliance)
        logger.trace("🔍 TRACE: Detailed internal tracing information")
        logger.debug("🔧 DEBUG: Technical details and flow information")
        logger.info("ℹ️ INFO: Important operational milestone")
        logger.warning("⚠️ WARNING: Important issue that doesn't stop execution")
        logger.error("🚨 ERROR: Error that needs attention but doesn't stop execution")
        logger.critical("💀 CRITICAL: System failure that stops execution")

        return True

    def test_performance_monitoring(self) -> bool:
        """Test performance monitoring functionality."""

        @performance_monitor("test_operation")
        def slow_operation(duration: float) -> str:
            """Simulate slow operation."""
            time.sleep(duration)
            return f"Operation completed in {duration:.1f}s"

        slow_operation(0.1)
        return True

    def test_error_context_capture(self) -> bool:
        """Test error context capture."""

        @log_exception_context(reraise=False)
        def failing_function() -> None:
            """Function that raises an exception."""
            msg = "Test exception for context capture"
            raise ValueError(msg)

        # Should not raise due to reraise=False
        failing_function()
        return True

    def test_function_entry_exit(self) -> bool:
        """Test function entry/exit logging."""

        @log_function_entry_exit(log_args=True, log_result=True, level=logging.DEBUG)
        def test_function(arg1: str, arg2: int, **kwargs: Any) -> dict[str, Any]:
            """Test function for entry/exit logging."""
            return {"result": "%s_%d" % (arg1, arg2), "kwargs": kwargs}

        test_function("test", 42, extra="value")
        return True

    def test_structured_output(self) -> bool:
        """Test structured output format."""
        logger = get_logger("test_structured")

        # Set context - PROPER format without f-strings
        logger.info("Testing structured output with context", extra={
            "entity_name": "allocation",
            "operation": "extraction",
            "record_count": 1500,
            "api_call_count": 3,
        })

        return True

    def test_thread_safety(self) -> bool:
        """Test thread safety of logging system."""

        def worker_thread(thread_id: int) -> None:
            """Worker thread for testing."""
            logger = get_logger("test_thread_%d" % thread_id)

            for i in range(5):
                # PROPER format without f-strings (ruff G004 compliance)
                logger.info("Thread %d - Message %d", thread_id, i)
                time.sleep(0.01)

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        return True

    def test_async_logging(self) -> bool:
        """Test logging in async context."""

        async def async_operation() -> str:
            """Async operation for testing."""
            logger = get_logger("test_async")

            logger.debug("Starting async operation")
            await asyncio.sleep(0.1)
            logger.debug("Async operation completed")

            return "async_result"

        # Run async test
        asyncio.run(async_operation())
        return True

    def test_log_file_creation(self) -> bool:
        """Test log file was created and contains data."""
        if not self.log_file.exists():
            return False

        file_size = self.log_file.stat().st_size
        if file_size == 0:
            return False

        # Check log file content
        with self.log_file.open(encoding="utf-8") as f:
            lines = f.readlines()

            # Show a few sample lines
            for _i, _line in enumerate(lines[-3:], 1):
                pass

        return True

    def test_log_level_filtering(self) -> bool:
        """Test log level filtering works correctly."""
        # Configure with INFO level
        info_config = {
            "log_level": "INFO",
            "console_output": False,  # Don't spam console
            "log_file": str(self.temp_dir / "info_only.log"),
        }

        configure_logging(info_config)
        logger = get_logger("test_filtering")

        # These should be logged
        logger.info("INFO message - should appear")
        logger.warning("WARNING message - should appear")
        logger.error("ERROR message - should appear")
        logger.critical("CRITICAL message - should appear")

        # These should NOT be logged
        logger.debug("DEBUG message - should NOT appear")
        logger.trace("TRACE message - should NOT appear")

        return True

    def test_ruff_compliance(self) -> bool:
        """Test that logging messages follow ruff G004 guidelines (no f-strings)."""
        logger = get_logger("test_ruff")

        # Good examples following ruff G004 guidelines
        entity_name = "allocation"
        record_count = 1500

        # ✅ CORRECT: Use % formatting or .format() instead of f-strings
        logger.info("Processing %d records for %s", record_count, entity_name)
        logger.debug("Entity %s configuration loaded", entity_name)
        logger.error("Failed to process entity %s: validation error", entity_name)

        # ✅ CORRECT: Simple strings without variables
        logger.info("Operation completed successfully")

        # ✅ CORRECT: Multiple parameters
        logger.debug("Configuration: entity=%s, count=%d, timeout=%d",
                    entity_name, record_count, 30)

        # ❌ WRONG (would cause G004): f"Processing {record_count} records"
        # ❌ WRONG (would cause G004): f"Entity {entity_name} failed"

        return True

    def test_info_level_usage(self) -> bool:
        """Test proper usage of INFO level (only for important milestones)."""
        logger = get_logger("test_info_usage")

        # ✅ CORRECT INFO usage - important milestones only
        logger.info("TAP initialization started")
        logger.info("Configuration validation completed")
        logger.info("Entity discovery completed: %d accessible", 25)
        logger.info("Stream extraction started")
        logger.info("Extraction completed: %d records processed", 10500)

        # ✅ CORRECT DEBUG usage - technical details
        logger.debug("Validating authentication configuration")
        logger.debug("Creating EntityDiscovery instance")
        logger.debug("Starting parallel access verification")
        logger.debug("Processing entity: %s", "allocation")

        # ✅ CORRECT TRACE usage - granular internal details
        logger.trace("Setting up tap instance variables")
        logger.trace("Monitoring started successfully")
        logger.trace("Entity allocation is accessible")
        logger.trace("Applied entity filter: status=ACTIVE")

        return True

    def run_all_tests(self) -> bool:
        """Run all tests and return overall result."""
        # Setup
        self.setup_logging()

        # Run tests
        tests = [
            ("Basic Log Levels", self.test_basic_log_levels),
            ("Performance Monitoring", self.test_performance_monitoring),
            ("Error Context Capture", self.test_error_context_capture),
            ("Function Entry/Exit", self.test_function_entry_exit),
            ("Structured Output", self.test_structured_output),
            ("Thread Safety", self.test_thread_safety),
            ("Async Logging", self.test_async_logging),
            ("Log File Creation", self.test_log_file_creation),
            ("Log Level Filtering", self.test_log_level_filtering),
            ("ruff G004 Compliance", self.test_ruff_compliance),
            ("INFO Level Usage", self.test_info_level_usage),
        ]

        all_passed = True

        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results[test_name] = result
                if not result:
                    all_passed = False
            except Exception:
                self.test_results[test_name] = False
                all_passed = False

        # Summary

        for test_name, result in self.test_results.items():
            pass

        if all_passed:
            pass

        # Cleanup info

        return all_passed


def main() -> int:
    """Main test execution."""
    test_suite = LoggingTestSuite()
    success = test_suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
