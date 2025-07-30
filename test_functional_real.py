#!/usr/bin/env python3
"""Functional test for flext-tap-oracle-wms with real .env configuration.

Tests schema discovery and data extraction with real Oracle WMS credentials.
Following CLAUDE.md guidelines: no fallbacks, no placeholders, real functionality only.

Copyright (c) 2025 FLEXT Team  
Licensed under the MIT License
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from flext_core import FlextResult, get_logger
from flext_oracle_wms import FlextOracleWmsClient
from flext_oracle_wms.config import FlextOracleWmsModuleConfig

# Import the real tap implementation
from flext_tap_oracle_wms.critical_validation import (
    enforce_mandatory_environment_variables,
    validate_schema_discovery_mode,
)
from flext_tap_oracle_wms.tap import TapOracleWMS

logger = get_logger(__name__)


def load_env_configuration() -> FlextOracleWmsModuleConfig:
    """Load real Oracle WMS configuration from .env file.
    
    Returns:
        Real WMS configuration loaded from environment variables
        
    Raises:
        SystemExit: If required environment variables are missing
    """
    # Enforce mandatory environment variables per critical_validation
    enforce_mandatory_environment_variables()
    
    # Load configuration from environment - uses real FlextOracleWmsModuleConfig
    config = FlextOracleWmsModuleConfig()
    
    logger.info(
        "Loaded Oracle WMS configuration",
        base_url=str(config.base_url),
        api_version=config.api_version,
        username=config.username,
        timeout_seconds=config.timeout_seconds,
    )
    
    return config


def test_real_wms_connection(config: FlextOracleWmsModuleConfig) -> FlextResult[bool]:
    """Test real connection to Oracle WMS using flext-oracle-wms library.
    
    Args:
        config: Real WMS configuration
        
    Returns:
        FlextResult indicating connection success
    """
    try:
        # Create real WMS client using flext-oracle-wms library
        client = FlextOracleWmsClient(config)
        
        # Test connection by attempting to get API info
        # This uses real WMS client methods, not mocks
        connection_test = client.test_connection()
        
        if connection_test:
            logger.info("✅ Real Oracle WMS connection successful")
            return FlextResult.ok(True)
        else:
            logger.error("❌ Oracle WMS connection failed")
            return FlextResult.fail("WMS connection test failed")
            
    except Exception as e:
        logger.exception("Real WMS connection test failed")
        return FlextResult.fail(f"Connection failed: {e}")


def test_schema_discovery_real(config: FlextOracleWmsModuleConfig) -> FlextResult[dict[str, Any]]:
    """Test real schema discovery using the WMS configuration.
    
    Args:
        config: Real WMS configuration
        
    Returns:
        FlextResult with discovered schema information
    """
    try:
        # Validate schema discovery mode using real validation
        validation_result = validate_schema_discovery_mode()
        if not validation_result.is_success:
            return FlextResult.fail(f"Schema discovery validation failed: {validation_result.error}")
        
        # Create real tap instance with environment configuration 
        tap_config = {
            "base_url": str(config.base_url),
            "username": config.username,
            "password": config.password,
            "api_version": config.api_version,
            "timeout": config.timeout_seconds,
            "max_retries": config.max_retries,
            "enable_request_logging": config.enable_request_logging,
            "verify_ssl": config.verify_ssl,
        }
        
        # Initialize real tap - no mocking, real functionality
        tap = TapOracleWMS(config=tap_config)
        
        # Perform real schema discovery
        logger.info("🔍 Starting real schema discovery...")
        streams = tap.discover_streams()
        
        if not streams:
            return FlextResult.fail("No streams discovered from real WMS API")
            
        # Extract schema information from discovered streams
        discovered_schemas = {}
        for stream in streams:
            schema_info = {
                "name": stream.name,
                "schema": stream.schema,
                "replication_method": stream.replication_method,
                "replication_key": stream.replication_key,
                "key_properties": stream.key_properties,
            }
            discovered_schemas[stream.name] = schema_info
            
        logger.info(
            "✅ Real schema discovery completed", 
            streams_discovered=len(streams),
            entity_names=list(discovered_schemas.keys()),
        )
        
        return FlextResult.ok(discovered_schemas)
        
    except Exception as e:
        logger.exception("Real schema discovery failed")
        return FlextResult.fail(f"Schema discovery failed: {e}")


def test_real_data_extraction(config: FlextOracleWmsModuleConfig) -> FlextResult[dict[str, Any]]:
    """Test real data extraction from Oracle WMS.
    
    Args:
        config: Real WMS configuration
        
    Returns:
        FlextResult with extracted data sample
    """
    try:
        # Create tap configuration for data extraction
        tap_config = {
            "base_url": str(config.base_url),
            "username": config.username,
            "password": config.password,
            "api_version": config.api_version,
            "timeout": config.timeout_seconds,
            "max_retries": config.max_retries,
            "page_size": 10,  # Small page size for testing
            "enable_request_logging": True,
            "verify_ssl": config.verify_ssl,
        }
        
        # Initialize real tap for data extraction
        tap = TapOracleWMS(config=tap_config)
        
        # Get available streams
        streams = tap.discover_streams()
        if not streams:
            return FlextResult.fail("No streams available for data extraction")
            
        # Extract sample data from the first available stream
        test_stream = streams[0]
        logger.info(f"🔍 Extracting sample data from stream: {test_stream.name}")
        
        # Get records from the real stream
        extracted_records = []
        record_count = 0
        max_sample_records = 5  # Limit for testing
        
        for record in test_stream.get_records(context={}):
            extracted_records.append(record)
            record_count += 1
            
            if record_count >= max_sample_records:
                break
                
        extraction_result = {
            "stream_name": test_stream.name,
            "records_extracted": record_count,
            "sample_records": extracted_records,
            "schema": test_stream.schema,
        }
        
        logger.info(
            "✅ Real data extraction completed",
            stream=test_stream.name,
            records_extracted=record_count,
        )
        
        return FlextResult.ok(extraction_result)
        
    except Exception as e:
        logger.exception("Real data extraction failed")
        return FlextResult.fail(f"Data extraction failed: {e}")


def main() -> int:
    """Main functional test execution.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger.info("🚀 Starting flext-tap-oracle-wms functional test with real .env")
    
    try:
        # Step 1: Load real configuration from .env
        logger.info("📋 Step 1: Loading real .env configuration...")
        config = load_env_configuration()
        
        # Step 2: Test real WMS connection
        logger.info("🔗 Step 2: Testing real WMS connection...")
        connection_result = test_real_wms_connection(config)
        if not connection_result.is_success:
            logger.error(f"Connection test failed: {connection_result.error}")
            return 1
            
        # Step 3: Test real schema discovery
        logger.info("🔍 Step 3: Testing real schema discovery...")
        schema_result = test_schema_discovery_real(config)
        if not schema_result.is_success:
            logger.error(f"Schema discovery failed: {schema_result.error}")
            return 1
            
        discovered_schemas = schema_result.data
        logger.info(f"Discovered {len(discovered_schemas)} schemas successfully")
        
        # Step 4: Test real data extraction
        logger.info("📥 Step 4: Testing real data extraction...")
        extraction_result = test_real_data_extraction(config)
        if not extraction_result.is_success:
            logger.error(f"Data extraction failed: {extraction_result.error}")
            return 1
            
        extraction_data = extraction_result.data
        logger.info(
            f"Extracted {extraction_data['records_extracted']} real records "
            f"from stream '{extraction_data['stream_name']}'"
        )
        
        # Step 5: Display results summary
        logger.info("📊 Functional test results summary:")
        logger.info(f"  ✅ Connection: SUCCESS")
        logger.info(f"  ✅ Schema Discovery: {len(discovered_schemas)} entities found")
        logger.info(f"  ✅ Data Extraction: {extraction_data['records_extracted']} records")
        logger.info(f"  ✅ Test Stream: {extraction_data['stream_name']}")
        
        # Save results to file for inspection
        results_file = Path("functional_test_results.json")
        test_results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "connection_test": "SUCCESS",
            "schemas_discovered": discovered_schemas,
            "data_extraction": {
                "stream": extraction_data["stream_name"],
                "records_count": extraction_data["records_extracted"],
                "sample_data": extraction_data["sample_records"][:2],  # Only first 2 for brevity
            },
        }
        
        with results_file.open("w") as f:
            json.dump(test_results, f, indent=2, default=str)
            
        logger.info(f"📄 Detailed results saved to: {results_file}")
        logger.info("🎉 All functional tests PASSED with real Oracle WMS data!")
        
        return 0
        
    except Exception as e:
        logger.exception("Functional test failed with exception")
        return 1


if __name__ == "__main__":
    # Set environment to load .env file
    os.environ.setdefault("PYTHONPATH", str(Path(__file__).parent / "src"))
    
    exit_code = main()
    sys.exit(exit_code)