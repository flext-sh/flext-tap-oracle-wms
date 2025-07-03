#!/usr/bin/env python3
"""Ultra Debug Mode Activator for Oracle WMS Tap.

This script configures maximum logging visibility for sync operations.
Run this before executing the tap to get EXTREME visibility into what's happening.
"""

import logging
import os
import sys


def setup_ultra_debug_logging():
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
        print(f"🔧 DEBUG ENABLED - Logger: {logger_name}")

    # 🎯 CONFIGURE ENVIRONMENT VARIABLES FOR MAXIMUM VISIBILITY
    ultra_debug_env = {
        "PYTHONUNBUFFERED": "1",          # Force immediate output
        "SINGER_SDK_LOG_LEVEL": "DEBUG",   # Singer SDK debug
        "HTTPX_LOG_LEVEL": "DEBUG",        # HTTP client debug
        "TAP_ORACLE_WMS_DEBUG": "true",    # Our custom debug flag
        "TAP_ORACLE_WMS_ULTRA_DEBUG": "true",  # Ultra debug flag
    }

    for key, value in ultra_debug_env.items():
        os.environ[key] = value
        print(f"🌍 ENV SET - {key}={value}")

    print("\n🚀 ULTRA DEBUG MODE ACTIVATED!")
    print("📝 Log file: wms_ultra_debug.log")
    print("📊 All logging levels set to DEBUG")
    print("💥 Maximum visibility enabled for sync operations")
    print("\nNow run your tap command to see EXTREME logging detail!")

def print_usage_examples():
    """Print example commands for using ultra debug mode."""
    print("\n📚 USAGE EXAMPLES:")
    print("=" * 50)

    print("\n1. 🔍 Discovery Mode (ultra debug):")
    print("   python -m tap_oracle_wms --config config.ultra-debug.json --discover")

    print("\n2. 🎯 Sync Mode (ultra debug):")
    print("   python -m tap_oracle_wms --config config.ultra-debug.json")

    print("\n3. 📊 With Meltano (ultra debug):")
    print("   meltano invoke tap-oracle-wms --config-override log_level=DEBUG")

    print("\n4. 🔬 Python script with ultra debug:")
    print("""   python << EOF
import sys
sys.path.insert(0, 'src')
from tap_oracle_wms import TapOracleWMS

# Configure ultra debug
config = {
    'base_url': 'https://your-wms.com',
    'username': 'user',
    'password': 'pass',
    'entities': ['allocation'],
    'log_level': 'DEBUG',
    'verbose_sync': True,
    'dev_mode': True
}

# Run with maximum logging
tap = TapOracleWMS(config=config)
tap.sync_all()
EOF""")

def show_log_monitoring_commands():
    """Show commands for monitoring the ultra debug logs."""
    print("\n🔍 LOG MONITORING COMMANDS:")
    print("=" * 40)

    print("\n📊 Real-time log monitoring:")
    print("   tail -f wms_ultra_debug.log")

    print("\n🎯 Filter for specific entity:")
    print("   tail -f wms_ultra_debug.log | grep 'allocation'")

    print("\n📈 Filter for progress updates:")
    print("   tail -f wms_ultra_debug.log | grep 'PROGRESS\\|SUCCESS\\|COMPLETE'")

    print("\n🔍 Filter for HTTP operations:")
    print("   tail -f wms_ultra_debug.log | grep 'HTTP\\|REQUEST\\|RESPONSE'")

    print("\n💥 Filter for critical operations:")
    print("   tail -f wms_ultra_debug.log | grep '🚀\\|✅\\|❌\\|⚠️'")

if __name__ == "__main__":
    print("🔥 ORACLE WMS TAP - ULTRA DEBUG MODE ACTIVATOR")
    print("=" * 55)

    setup_ultra_debug_logging()
    print_usage_examples()
    show_log_monitoring_commands()

    print("\n✨ Ultra debug mode is now ACTIVE!")
    print("Run your tap commands to see MAXIMUM logging detail.")
