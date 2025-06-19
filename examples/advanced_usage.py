#!/usr/bin/env python3
"""Advanced usage examples for tap-oracle-wms."""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from tap_oracle_wms import TapOracleWMS
from tap_oracle_wms.discovery import EntityDiscovery, SchemaGenerator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Constants
HIGH_PRIORITY_THRESHOLD = 5
GRACE_RETRIES = 2


async def analyze_entity_relationships():
    """Analyze relationships between WMS entities."""
    config = {
        "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
        "auth_method": "basic",
        "username": "${WMS_USERNAME}",
        "password": "${WMS_PASSWORD}",
        "company_code": "DEMO",
        "facility_code": "DC01",
        "start_date": "2024-01-01T00:00:00Z",
    }

    discovery = EntityDiscovery(config)
    SchemaGenerator()

    # Discover all entities
    entities = await discovery.discover_entities()
    logger.info("Found %s", len(entities) entities")

    # Analyze relationships
    relationships = {}

    for entity_name in sorted(entities.keys())[:10]:  # Analyze first 10 for demo
        logger.info("Analyzing %s", entity_name...")

        # Get entity metadata
        metadata = await discovery.describe_entity(entity_name)
        if not metadata:
            continue

        # Look for foreign key relationships
        entity_relationships = []
        for param in metadata.get("parameters", []):
            param_name = param.get("name", "")

            # Common foreign key patterns
            if param_name.endswith("_id") and param_name != "id":
                # Try to determine related entity
                related_entity = param_name[:-3]  # Remove _id suffix
                if related_entity in entities:
                    entity_relationships.append(
                        {
                            "field": param_name,
                            "related_entity": related_entity,
                            "type": "foreign_key",
                        }
                    )

        if entity_relationships:
            relationships[entity_name] = entity_relationships

    # Display relationship graph
    logger.info("\nEntity Relationship Summary:")
    for entity, rels in relationships.items():
        logger.info("\n%s", entity:")
        for rel in rels:
            logger.info("  -> %s", rel['related_entity'] (via %s", rel['field'])")

    return relationships


async def performance_optimization_demo():
    """Demonstrate performance optimization techniques."""
    config = {
        "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
        "auth_method": "basic",
        "username": "${WMS_USERNAME}",
        "password": "${WMS_PASSWORD}",
        "company_code": "DEMO",
        "facility_code": "DC01",
        "start_date": "2024-01-01T00:00:00Z",
    }

    # Test different pagination strategies
    test_configs = [
        {
            "name": "Offset Pagination (Small Pages)",
            "pagination_mode": "offset",
            "page_size": 100,
        },
        {
            "name": "Offset Pagination (Large Pages)",
            "pagination_mode": "offset",
            "page_size": 1000,
        },
        {"name": "Cursor Pagination", "pagination_mode": "cursor", "page_size": 1000},
    ]

    results = []

    for test_config in test_configs:
        logger.info("\nTesting: %s", test_config['name']")

        # Update config
        config.update(
            {
                "pagination_mode": test_config["pagination_mode"],
                "page_size": test_config["page_size"],
                "entities": ["inventory"],  # Test with inventory entity
            }
        )

        tap = TapOracleWMS(config=config)

        # Measure extraction time
        start_time = datetime.now(UTC)
        record_count = 0

        def count_records(message) -> None:
            nonlocal record_count
            if message["type"] == "RECORD":
                record_count += 1

        # Override write_message to count records
        tap.write_message = count_records

        try:
            # Extract first 5000 records
            tap.sync_all_streams()

            elapsed = (datetime.now(UTC) - start_time).total_seconds()
            throughput = record_count / elapsed if elapsed > 0 else 0

            results.append(
                {
                    "strategy": test_config["name"],
                    "records": record_count,
                    "elapsed_seconds": elapsed,
                    "records_per_second": throughput,
                }
            )

            logger.info("  Records: %s", record_count")
            logger.info("  Time: %s", elapsed:.2fs")
            logger.info("  Throughput: %s", throughput:.0f records/sec")

        except Exception:
            logger.exception("  Failed")

    # Compare results
    logger.info("\nPerformance Comparison:")
    for result in sorted(results, key=lambda x: x["records_per_second"], reverse=True):
        logger.info("  %s", result['strategy']: %s", result['records_per_second']:.0f rec/s")

    return results


def custom_filtering_example() -> None:
    """Demonstrate advanced filtering capabilities."""
    config = {
        "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
        "auth_method": "basic",
        "username": "${WMS_USERNAME}",
        "password": "${WMS_PASSWORD}",
        "company_code": "DEMO",
        "facility_code": "DC01",
        "start_date": "2024-01-01T00:00:00Z",
        # Complex filtering example
        "entities": ["inventory", "order_hdr"],
        # Global filters apply to all entities
        "global_filters": {"status": "ACTIVE"},
        # Entity-specific filters
        "entity_filters": {
            "inventory": {
                "on_hand_qty__gt": 0,
                "location_id__startswith": "A",
                "item_id__status": "ACTIVE",
            },
            "order_hdr": {
                "order_date__gte": (datetime.now(UTC) - timedelta(days=7)).isoformat(),
                "status__in": "PENDING,PROCESSING,SHIPPED",
                "priority__gte": 5,
            },
        },
        # Custom ordering
        "entity_ordering": {
            "inventory": "-on_hand_qty,location_id",
            "order_hdr": "-order_date,-priority",
        },
        # Field selection for performance
        "field_selection": {
            "inventory": [
                "id",
                "item_id",
                "location_id",
                "on_hand_qty",
                "allocated_qty",
                "available_qty",
            ],
            "order_hdr": [
                "id",
                "order_nbr",
                "status",
                "priority",
                "order_date",
                "customer_id",
                "total_amount",
            ],
        },
    }

    tap = TapOracleWMS(config=config)

    logger.info("Running extraction with complex filters...")

    # Track filtered records
    filtered_records = {"inventory": [], "order_hdr": []}

    def capture_records(message) -> None:
        if message["type"] == "RECORD":
            stream = message["stream"]
            if stream in filtered_records:
                filtered_records[stream].append(message["record"])

    tap.write_message = capture_records

    try:
        tap.sync_all_streams()

        # Analyze results
        logger.info("\nFiltered Results:")
        for stream, records in filtered_records.items():
            logger.info("\n%s", stream: %s", len(records) records")

            if records and stream == "inventory":
                # Verify filters worked
                locations_starting_with_a = sum(
                    1 for r in records if r.get("location_id", "").startswith("A")
                )
                positive_qty = sum(1 for r in records if r.get("on_hand_qty", 0) > 0)
                logger.info(
                    f"  Locations starting with 'A': {locations_starting_with_a}"
                )
                logger.info("  Positive quantities: %s", positive_qty")

            elif records and stream == "order_hdr":
                # Check date range
                recent_orders = sum(
                    1
                    for r in records
                    if r.get("order_date", "")
                    >= (datetime.now(UTC) - timedelta(days=7)).isoformat()
                )
                high_priority = sum(
                    1
                    for r in records
                    if r.get("priority", 0) >= HIGH_PRIORITY_THRESHOLD
                )
                logger.info("  Recent orders (last 7 days): %s", recent_orders")
                logger.info("  High priority orders: %s", high_priority")

    except Exception:
        logger.exception("Filtering example failed")


async def parallel_entity_extraction():
    """Extract multiple entities in parallel for better performance."""
    config = {
        "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
        "auth_method": "basic",
        "username": "${WMS_USERNAME}",
        "password": "${WMS_PASSWORD}",
        "company_code": "DEMO",
        "facility_code": "DC01",
        "start_date": "2024-01-01T00:00:00Z",
        "pagination_mode": "cursor",
        "page_size": 1000,
    }

    # Entities to extract in parallel
    target_entities = ["item", "location", "inventory", "order_hdr", "order_dtl"]

    async def extract_entity(entity_name: str) -> dict[str, Any]:
        """Extract a single entity asynchronously."""
        entity_config = config.copy()
        entity_config["entities"] = [entity_name]

        tap = TapOracleWMS(config=entity_config)

        records = []
        start_time = datetime.now(UTC)

        def capture_records(message) -> None:
            if message["type"] == "RECORD":
                records.append(message["record"])

        tap.write_message = capture_records

        try:
            # Run sync in thread pool to avoid blocking
            await asyncio.get_event_loop().run_in_executor(None, tap.sync_all_streams)

            elapsed = (datetime.now(UTC) - start_time).total_seconds()

            return {
                "entity": entity_name,
                "records": len(records),
                "elapsed": elapsed,
                "success": True,
            }
        except Exception as e:
            return {
                "entity": entity_name,
                "records": 0,
                "elapsed": 0,
                "success": False,
                "error": str(e),
            }

    logger.info("Starting parallel extraction...")
    start_time = datetime.now(UTC)

    # Extract all entities in parallel
    tasks = [extract_entity(entity) for entity in target_entities]
    results = await asyncio.gather(*tasks)

    total_elapsed = (datetime.now(UTC) - start_time).total_seconds()

    # Display results
    logger.info("\nParallel Extraction Complete in %s", total_elapsed:.2fs")
    logger.info("\nResults by Entity:")

    total_records = 0
    for result in results:
        if result["success"]:
            logger.info(
                f"  {result['entity']}: {result['records']} records in {result['elapsed']:.2f}s"
            )
            total_records += result["records"]
        else:
            logger.info("  %s", result['entity']: FAILED - %s", result['error']")

    logger.info("\nTotal: %s", total_records records")
    logger.info("Throughput: %s", total_records / total_elapsed:.0f records/sec")

    return results


def main() -> None:
    """Run advanced examples."""
    import sys

    examples = {
        "relationships": lambda: asyncio.run(analyze_entity_relationships()),
        "performance": lambda: asyncio.run(performance_optimization_demo()),
        "filtering": custom_filtering_example,
        "parallel": lambda: asyncio.run(parallel_entity_extraction()),
    }

    if len(sys.argv) < GRACE_RETRIES or sys.argv[1] not in examples:
        sys.exit(1)

    example = sys.argv[1]
    logger.info("Running %s", example example...")

    try:
        examples[example]()
    except Exception:
        logger.exception("Example failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
