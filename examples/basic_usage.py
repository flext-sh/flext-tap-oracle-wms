"""Module basic_usage."""

# !/usr/bin/env python3
"""Basic usage example for tap-oracle-wms."""

import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Constants
MAX_RETRY_COUNT = 5
MIN_REQUIRED_ARGS = 2


def create_config() -> Any:
    """Create configuration from environment variables."""
    config = {
        "base_url": os.environ.get(
            "WMS_BASE_URL",
            "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
        ),
        "auth_method": os.environ.get("WMS_AUTH_METHOD", "basic"),
        "username": os.environ.get("WMS_USERNAME"),
        "password": os.environ.get("WMS_PASSWORD"),
        "company_code": os.environ.get("WMS_COMPANY_CODE", "DEMO"),
        "facility_code": os.environ.get("WMS_FACILITY_CODE", "DC01"),
        "start_date": os.environ.get("WMS_START_DATE", "2024-01-01T00:00:00Z"),
        "page_size": 100,
        "pagination_mode": "offset",
        "schema_discovery_method": "auto",
        "log_level": "INFO",
    }

    # Validate required fields
    if config["auth_method"] == "basic" and (
        not config["username"] or not config["password"]
    ):
        logger.error(
            "Basic auth requires WMS_USERNAME and WMS_PASSWORD environment variables",
        )
        sys.exit(1)

    return config


def discover_entities() -> Any:
    """Discover available entities from WMS."""
    from tap_oracle_wms import TapOracleWMS

    config = create_config()
    tap = TapOracleWMS(config=config)

    logger.info("Discovering available WMS entities...")

    try:
        # This will discover all available streams
        catalog = tap.catalog

        logger.info("Discovered %s entities:", len(catalog.streams))
        for stream in catalog.streams:
            logger.info("  - %s", stream.tap_stream_id)

            # Show primary keys and replication key
            metadata = stream.metadata[0].metadata
            if metadata.get("table-key-properties"):
                logger.info("    Primary keys: %s", metadata["table-key-properties"])
            if metadata.get("replication-key"):
                logger.info("    Replication key: %s", metadata["replication-key"])

        # Save catalog
        with open("catalog.json", "w", encoding="utf-8") as f:
            json.dump(catalog.to_dict(), f, indent=2)
        logger.info("Catalog saved to catalog.json")

        return catalog

    except Exception:
        logger.exception("Discovery failed")
        sys.exit(1)


def extract_sample_data() -> None:
    """Extract sample data from selected entities."""
    from tap_oracle_wms import TapOracleWMS

    config = create_config()

    # Select specific entities to extract
    config["entities"] = ["item", "location", "inventory"]
    config["page_size"] = 10  # Small sample

    tap = TapOracleWMS(config=config)

    logger.info("Extracting sample data from selected entities...")

    # Capture output
    records: list = []
    schemas: dict = {}
    states: dict = {}

    def handle_record(message) -> None:
        if message["type"] == "RECORD":
            stream = message["stream"]
            if stream not in records:
                records[stream] = []
            records[stream].append(message["record"])
        elif message["type"] == "SCHEMA":
            schemas[message["stream"]] = message["schema"]
        elif message["type"] == "STATE":
            states[message["stream"]] = message["value"]

    # Override the write_message method to capture output
    original_write_message = tap.write_message
    tap.write_message = handle_record

    try:
        # Run sync
        tap.sync_all_streams()

        # Display results
        logger.info("\nExtraction Summary:")
        for stream, stream_records in records.items():
            logger.info("\n%s: %s records", stream, len(stream_records))
            if stream_records:
                # Show first record as example
                logger.info("  Sample record:")
                sample = stream_records[0]
                for key, value in list(sample.items())[:5]:  # Show first 5 fields
                    logger.info("    %s: %s", key, value)
                if len(sample) > 5:
                    logger.info("    ... and %s more fields", len(sample) - 5)

        # Save sample data
        with open("sample_data.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "extraction_time": datetime.now(UTC).isoformat(),
                    "records": records,
                    "schemas": schemas,
                    "states": states,
                },
                f,
                indent=2,
            )
        logger.info("\nSample data saved to sample_data.json")

    except Exception:
        logger.exception("Extraction failed")
        sys.exit(1)
    finally:
        # Restore original method
        tap.write_message = original_write_message


def incremental_sync_example() -> None:
    """Example of incremental sync with state management."""
    from tap_oracle_wms import TapOracleWMS

    config = create_config()

    # Configure for incremental sync
    config["entities"] = ["inventory", "order_hdr"]  # Entities with update timestamps
    config["pagination_mode"] = "cursor"  # Better for incremental

    tap = TapOracleWMS(config=config)

    # Load previous state if exists
    state: dict = {}
    if os.path.exists("state.json"):
        with open("state.json", encoding="utf-8") as f:
            state = json.load(f)
        logger.info("Loaded previous state: %s", state)

    tap.state = state

    logger.info("Running incremental sync...")

    # Capture new state
    new_state: dict = {}

    def handle_state(message) -> None:
        if message["type"] == "STATE":
            new_state.update(message["value"])

    original_write_message = tap.write_message
    tap.write_message = lambda message: (
        handle_state(message),
        original_write_message(message),
    )[1]

    try:
        tap.sync_all_streams()

        # Save new state
        if new_state:
            with open("state.json", "w", encoding="utf-8") as f:
                json.dump(new_state, f, indent=2)
            logger.info("Saved new state: %s", new_state)

    except Exception:
        logger.exception("Incremental sync failed")
        sys.exit(1)
    finally:
        tap.write_message = original_write_message


def main() -> None:
    """Run examples based on command line argument."""
    if len(sys.argv) < MIN_REQUIRED_ARGS:
        sys.exit(1)

    command = sys.argv[1]

    if command == "discover":
        discover_entities()
    elif command == "extract":
        extract_sample_data()
    elif command == "incremental":
        incremental_sync_example()
        sys.exit(1)


if __name__ == "__main__":
    main()
