#!/usr/bin/env python3
"""Ultra Debug Mode Activator for Oracle WMS Tap.

This script configures maximum logging visibility for sync operations.
Run this before executing the tap to get EXTREME visibility into what's happening.
"""

import logging
import os
import sys


def setup_ultra_debug_logging() -> None:
    """Configure ultra-detailed logging for maximum sync visibility."""
    # 🔥 FORCE MAXIMUM LOGGING LEVEL
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("wms_ultra_debug.log", mode="w"),
        ],
    )

    # 📊 SET ALL LOGGERS TO DEBUG
    loggers_to_debug = [
        "tap_oracle_wms",
        "tap_oracle_wms.tap",
        "tap_oracle_wms.streams",
        "tap_oracle_wms.discovery",
        "tap_oracle_wms.auth",
        "singer_sdk",
        "httpx",
        "requests",
    ]

    for logger_name in loggers_to_debug:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

    # 🎯 CONFIGURE ENVIRONMENT VARIABLES FOR MAXIMUM VISIBILITY
    ultra_debug_env = {
        "PYTHONUNBUFFERED": "1",  # Force immediate output
        "SINGER_SDK_LOG_LEVEL": "DEBUG",  # Singer SDK debug
        "HTTPX_LOG_LEVEL": "DEBUG",  # HTTP client debug
        "TAP_ORACLE_WMS_DEBUG": "true",  # Our custom debug flag
        "TAP_ORACLE_WMS_ULTRA_DEBUG": "true",  # Ultra debug flag
    }

    for key, value in ultra_debug_env.items():
        os.environ[key] = value


def print_usage_examples() -> None:
    """Print example commands for using ultra debug mode."""


def show_log_monitoring_commands() -> None:
    """Show commands for monitoring the ultra debug logs."""


if __name__ == "__main__":
    setup_ultra_debug_logging()
    print_usage_examples()
    show_log_monitoring_commands()
