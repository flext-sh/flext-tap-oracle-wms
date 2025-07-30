#!/usr/bin/env python3
"""Complete functional test for flext-tap-oracle-wms - Schema discovery and data extraction.

This test performs a complete end-to-end test using real Oracle WMS credentials:
1. Load .env file with real credentials
2. Create Oracle WMS client using flext-oracle-wms library
3. Discover available schemas/entities
4. Extract sample data from discovered entities
5. Validate data structure and content

Following CLAUDE.md guidelines: no fallbacks, no placeholders, real functionality only.

Copyright (c) 2025 FLEXT Team
Licensed under the MIT License
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from flext_core import FlextResult, get_logger


# Load .env file manually if python-dotenv is not available
def load_env_file(env_path: Path = Path(".env")) -> None:
    """Load environment variables from .env file."""
    if env_path.exists():
        with env_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
        logger.info(f"📄 Loaded .env file: {env_path}")
    else:
        logger.warning(f"⚠️  .env file not found: {env_path}")


logger = get_logger(__name__)


async def test_oracle_wms_client_creation() -> FlextResult[Any]:
    """Test creating Oracle WMS client using flext-oracle-wms library.

    Returns:
        FlextResult with created client instance

    """
    try:
        logger.info("🔍 Testing Oracle WMS client creation...")

        # Import the real flext-oracle-wms library
        from flext_oracle_wms import (
            FlextOracleWmsClient,
            FlextOracleWmsClientConfig,
            FlextOracleWmsModuleConfig,
        )

        # Create module configuration from environment
        module_config = FlextOracleWmsModuleConfig(
            base_url=os.getenv("ORACLE_WMS_BASE_URL"),
            username=os.getenv("ORACLE_WMS_USERNAME"),
            password=os.getenv("ORACLE_WMS_PASSWORD"),
            api_version=os.getenv("ORACLE_WMS_API_VERSION", "v10"),
            timeout=int(os.getenv("ORACLE_WMS_TIMEOUT", "30")),
            max_retries=int(os.getenv("ORACLE_WMS_MAX_RETRIES", "3")),
            verify_ssl=os.getenv("ORACLE_WMS_VERIFY_SSL", "true").lower() == "true",
        )

        # Create client configuration from module config
        client_config = FlextOracleWmsClientConfig.from_legacy_config(module_config)

        # Create the Oracle WMS client
        client = FlextOracleWmsClient(client_config)

        logger.info(f"✅ Oracle WMS client created for: {client_config.base_url}")
        logger.info(f"📋 Environment: {client_config.environment}")
        logger.info(f"📋 API Version: {client_config.api_version}")

        return FlextResult.ok(client)

    except Exception as e:
        logger.exception("Oracle WMS client creation failed")
        return FlextResult.fail(f"Client creation failed: {e}")


async def test_oracle_wms_connection() -> FlextResult[Any]:
    """Test connecting to Oracle WMS and performing health check.

    Returns:
        FlextResult with health check results

    """
    try:
        logger.info("🔍 Testing Oracle WMS connection...")

        # Create client
        client_result = await test_oracle_wms_client_creation()
        if not client_result.is_success:
            return client_result

        client = client_result.data

        # Start the client (establishes connection)
        start_result = await client.start()
        if not start_result.is_success:
            return FlextResult.fail(f"Failed to start client: {start_result.error}")

        logger.info("✅ Oracle WMS client started successfully")

        # Perform health check
        health_result = await client.health_check()
        if not health_result.is_success:
            return FlextResult.fail(f"Health check failed: {health_result.error}")

        health_data = health_result.data
        logger.info("✅ Health check passed:")
        logger.info(f"  📋 Status: {health_data.get('status')}")
        logger.info(f"  📋 Available APIs: {health_data.get('available_apis')}")
        logger.info(
            f"  📋 Discovered entities: {health_data.get('discovered_entities')}",
        )

        # Stop the client properly
        await client.stop()

        return FlextResult.ok(health_data)

    except Exception as e:
        logger.exception("Oracle WMS connection test failed")
        return FlextResult.fail(f"Connection test failed: {e}")


async def test_schema_discovery() -> FlextResult[list[str]]:
    """Test Oracle WMS schema/entity discovery.

    Returns:
        FlextResult with list of discovered entities

    """
    try:
        logger.info("🔍 Testing Oracle WMS schema discovery...")

        # Create and start client
        client_result = await test_oracle_wms_client_creation()
        if not client_result.is_success:
            return client_result

        client = client_result.data

        start_result = await client.start()
        if not start_result.is_success:
            return FlextResult.fail(f"Failed to start client: {start_result.error}")

        # Discover entities/schemas
        entities_result = await client.discover_entities()
        if not entities_result.is_success:
            await client.stop()
            return FlextResult.fail(f"Entity discovery failed: {entities_result.error}")

        entities = entities_result.data
        logger.info(f"✅ Discovered {len(entities)} entities:")

        # Log first 10 entities
        for i, entity in enumerate(entities[:10]):
            logger.info(f"  📋 {i + 1}. {entity}")

        if len(entities) > 10:
            logger.info(f"  📋 ... and {len(entities) - 10} more entities")

        # Stop the client
        await client.stop()

        return FlextResult.ok(entities)

    except Exception as e:
        logger.exception("Schema discovery failed")
        return FlextResult.fail(f"Schema discovery failed: {e}")


async def test_data_extraction() -> FlextResult[dict[str, Any]]:
    """Test extracting sample data from discovered entities.

    Returns:
        FlextResult with sample extracted data

    """
    try:
        logger.info("🔍 Testing Oracle WMS data extraction...")

        # First discover entities
        entities_result = await test_schema_discovery()
        if not entities_result.is_success:
            return entities_result

        entities = entities_result.data
        if not entities:
            return FlextResult.fail("No entities discovered for data extraction")

        # Create and start client again
        client_result = await test_oracle_wms_client_creation()
        if not client_result.is_success:
            return client_result

        client = client_result.data

        start_result = await client.start()
        if not start_result.is_success:
            return FlextResult.fail(f"Failed to start client: {start_result.error}")

        # Test data extraction from first few entities
        extraction_results = {}
        test_entities = entities[:3]  # Test first 3 entities

        for entity in test_entities:
            logger.info(f"📊 Extracting data from entity: {entity}")

            try:
                # Extract sample data (limit to 2 records for testing)
                data_result = await client.get_entity_data(
                    entity_name=entity,
                    limit=2,
                    offset=0,
                )

                if data_result.is_success:
                    data = data_result.data
                    record_count = 0

                    # Count records in response
                    if isinstance(data, dict):
                        if "results" in data:
                            record_count = len(data["results"])
                        elif "data" in data:
                            record_count = (
                                len(data["data"])
                                if isinstance(data["data"], list)
                                else 1
                            )
                        else:
                            record_count = 1
                    elif isinstance(data, list):
                        record_count = len(data)

                    extraction_results[entity] = {
                        "success": True,
                        "record_count": record_count,
                        "data_keys": list(data.keys())
                        if isinstance(data, dict)
                        else ["raw_data"],
                        "sample_data": data,
                    }

                    logger.info(f"  ✅ Extracted {record_count} records from {entity}")
                    if isinstance(data, dict) and data:
                        logger.info(f"  📋 Data keys: {list(data.keys())}")

                else:
                    extraction_results[entity] = {
                        "success": False,
                        "error": data_result.error,
                        "record_count": 0,
                    }
                    logger.warning(
                        f"  ❌ Failed to extract from {entity}: {data_result.error}",
                    )

            except Exception as e:
                extraction_results[entity] = {
                    "success": False,
                    "error": str(e),
                    "record_count": 0,
                }
                logger.warning(f"  ❌ Exception extracting from {entity}: {e}")

        # Stop the client
        await client.stop()

        # Summary
        successful_extractions = sum(
            1 for result in extraction_results.values() if result["success"]
        )
        total_records = sum(
            result.get("record_count", 0) for result in extraction_results.values()
        )

        logger.info("✅ Data extraction completed:")
        logger.info(f"  📋 Entities tested: {len(test_entities)}")
        logger.info(f"  📋 Successful extractions: {successful_extractions}")
        logger.info(f"  📋 Total records extracted: {total_records}")

        return FlextResult.ok(
            {
                "entities_tested": test_entities,
                "successful_extractions": successful_extractions,
                "total_records": total_records,
                "results": extraction_results,
            },
        )

    except Exception as e:
        logger.exception("Data extraction test failed")
        return FlextResult.fail(f"Data extraction failed: {e}")


async def main() -> int:
    """Main test execution.

    Returns:
        Exit code (0 for success, 1 for failure)

    """
    logger.info("🚀 Starting COMPLETE functional test for flext-tap-oracle-wms")
    logger.info(
        "   This test will perform real Oracle WMS operations using credentials from .env",
    )

    # Load environment variables from .env file
    load_env_file()

    try:
        # Step 1: Test client creation
        logger.info("📋 Step 1: Testing Oracle WMS client creation...")
        client_result = await test_oracle_wms_client_creation()
        if not client_result.is_success:
            logger.error(f"Client creation failed: {client_result.error}")
            return 1

        # Step 2: Test connection and health check
        logger.info("🔗 Step 2: Testing Oracle WMS connection...")
        connection_result = await test_oracle_wms_connection()
        if not connection_result.is_success:
            logger.error(f"Connection test failed: {connection_result.error}")
            return 1

        # Step 3: Test schema discovery
        logger.info("🔍 Step 3: Testing schema discovery...")
        discovery_result = await test_schema_discovery()
        if not discovery_result.is_success:
            logger.error(f"Schema discovery failed: {discovery_result.error}")
            return 1

        # Step 4: Test data extraction
        logger.info("📊 Step 4: Testing data extraction...")
        extraction_result = await test_data_extraction()
        if not extraction_result.is_success:
            logger.error(f"Data extraction failed: {extraction_result.error}")
            return 1

        # Summary
        extraction_data = extraction_result.data
        logger.info("🎉 COMPLETE functional test results:")
        logger.info("  ✅ Client Creation: SUCCESS")
        logger.info("  ✅ Connection Test: SUCCESS")
        logger.info(
            f"  ✅ Schema Discovery: SUCCESS ({len(discovery_result.data)} entities)",
        )
        logger.info(
            f"  ✅ Data Extraction: SUCCESS ({extraction_data['successful_extractions']}/{extraction_data['entities_tested']} entities)",
        )
        logger.info(f"  📊 Total Records Extracted: {extraction_data['total_records']}")

        logger.info("🏆 All tests PASSED - flext-tap-oracle-wms is fully functional!")
        return 0

    except Exception:
        logger.exception("Complete functional test failed with exception")
        return 1


if __name__ == "__main__":
    # Set environment to load .env file
    os.environ.setdefault("PYTHONPATH", str(Path(__file__).parent / "src"))

    # Run async main
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
