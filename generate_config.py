"""Module generate_config."""

# !/usr/bin/env python3
from typing import Any

"""Generate config.json from .env file for tap-oracle-wms."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_tap_config() -> Any:
    """Generate tap configuration from environment variables."""
    config = {
        "base_url": os.getenv("WMS_BASE_URL", "https://test.oracle.com/wms/api/v1"),
        "username": os.getenv("WMS_USERNAME", "test_user"),
        "password": os.getenv("WMS_PASSWORD", "test_password"),
        "timeout": int(os.getenv("WMS_TIMEOUT", "300")),
        "page_size": int(os.getenv("WMS_PAGE_SIZE", "1000")),
        "start_date": os.getenv("WMS_START_DATE", "2024-01-01T00:00:00Z"),
        "api_version": os.getenv("WMS_API_VERSION", "v2"),
        "retry_count": int(os.getenv("WMS_RETRY_COUNT", "3")),
        "retry_delay": int(os.getenv("WMS_RETRY_DELAY", "5")),
        "user_agent": "tap-oracle-wms/1.0.0",
    }

    # Add test mode flag if enabled
    if os.getenv("WMS_TEST_MODE", "false").lower() == "true":
        config["test_mode"] = True

    return config


def main() -> None:
    """Generate config.json file."""
    config_path = Path("config.json")

    if config_path.exists():
        config_path.rename("config.json.bak")

    config = generate_tap_config()

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    main()
