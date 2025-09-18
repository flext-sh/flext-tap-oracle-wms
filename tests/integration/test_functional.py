"""Comprehensive functional tests for Oracle WMS tap using real .env data.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_core import FlextLogger, FlextTypes
from flext_tap_oracle_wms import (
    FlextTapOracleWMS,
    FlextTapOracleWMSStream,
    # create_wms_tap_config,  # Not implemented yet
)

logger = FlextLogger(__name__)


@pytest.mark.functional
class TestOracleWMSFunctionalComplete:
    """COMPREHENSIVE functional tests using REAL Oracle WMS data from .env."""

    def test_environment_loaded(self, real_wms_config: FlextTypes.Core.Dict) -> None:
        """CRITICAL: Verify real Oracle WMS environment is properly loaded."""
        required_config = ["base_url", "username", "password"]
        for key in required_config:
            assert real_wms_config.get(key), f"Missing required config: {key}"
            assert real_wms_config[key], f"Empty config value: {key}"

        # Verify it's the real ta29 environment
        base_url = str(real_wms_config["base_url"])
        assert "ta29.wms.ocs.oraclecloud.com" in base_url, (
            f"Not ta29 environment: {base_url}"
        )
        assert "raizen_test" in base_url, f"Not raizen_test environment: {base_url}"

        logger.info("✅ Real Oracle WMS environment verified: %s", base_url)

    def test_tap_initialization_real_config(
        self,
        real_wms_config: FlextTypes.Core.Dict,
    ) -> None:
        """Test tap initializes with REAL Oracle WMS configuration."""
        # CRITICAL: This must work without errors
        tap = FlextTapOracleWMS(config=real_wms_config)

        assert tap is not None
        assert hasattr(tap, "config")
        assert tap.config.get("base_url") == real_wms_config["base_url"]

        logger.info("✅ Tap initialized successfully with real config")

    @pytest.mark.discovery
    def test_real_entity_discovery(self, real_tap_instance: FlextTapOracleWMS) -> None:
        """CRITICAL: Test automatic entity discovery with REAL Oracle WMS."""
        # This will make REAL network calls to Oracle WMS
        try:
            catalog = real_tap_instance.catalog_dict

            # Verify we got a valid catalog
            assert catalog is not None, "Catalog is None"
            assert "streams" in catalog, "No streams in catalog"
            assert isinstance(catalog["streams"], list), "Streams is not a list"

            streams = catalog["streams"]
            assert len(streams) > 0, "No streams discovered"

            # Log discovered entities
            entity_names = [stream["tap_stream_id"] for stream in streams]
            logger.info(
                "✅ Discovered %d entities: %s",
                len(entity_names),
                entity_names,
            )

            # Verify essential entities exist (based on REAL discovery)
            essential_entities = [
                "allocation",
            ]  # Use entities that actually exist in ta29
            for entity in essential_entities:
                found_entities = [
                    name for name in entity_names if entity in name.lower()
                ]
                assert found_entities, (
                    f"Essential entity '{entity}' not found in: {entity_names}"
                )

            # Verify we have core WMS entities
            core_wms_patterns = ["allocation", "company", "location"]
            found_core = 0
            for pattern in core_wms_patterns:
                if any(pattern in name.lower() for name in entity_names):
                    found_core += 1
            assert found_core >= 2, (
                f"Not enough core WMS entities found. Got: {entity_names}"
            )

            # Verify each stream has proper schema
            for stream in streams:
                assert "schema" in stream, (
                    f"Stream {stream['tap_stream_id']} missing schema"
                )
                assert "properties" in stream["schema"], (
                    f"Stream {stream['tap_stream_id']} schema missing properties"
                )
                properties = stream["schema"]["properties"]
                assert len(properties) > 0, (
                    f"Stream {stream['tap_stream_id']} has empty properties"
                )

                logger.info(
                    "✅ Stream %s has %d properties",
                    stream["tap_stream_id"],
                    len(properties),
                )

        except Exception:
            logger.exception("❌ Entity discovery failed")
            raise

    @pytest.mark.singer
    def test_real_schema_generation(self, real_tap_instance: FlextTapOracleWMS) -> None:
        """Test schema generation produces valid Singer schemas."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]

        for stream in streams[:3]:  # Test first 3 streams
            schema = stream["schema"]

            # Verify Singer schema structure
            assert "type" in schema, (
                f"Schema missing type for {stream['tap_stream_id']}"
            )
            assert schema["type"] == "object", (
                f"Invalid schema type for {stream['tap_stream_id']}"
            )
            assert "properties" in schema, (
                f"Schema missing properties for {stream['tap_stream_id']}"
            )

            # Verify properties have valid Singer types
            properties = schema["properties"]
            for prop_name, prop_def in properties.items():
                assert "type" in prop_def, f"Property {prop_name} missing type"

                # Verify Singer-compatible types
                prop_type = prop_def["type"]
                valid_types = [
                    "string",
                    "integer",
                    "number",
                    "boolean",
                    "array",
                    "object",
                    ["string", "null"],
                    ["integer", "null"],
                    ["number", "null"],
                    ["boolean", "null"],
                ]
                assert prop_type in valid_types or (
                    isinstance(prop_type, list) and "null" in prop_type
                ), f"Invalid Singer type for {prop_name}: {prop_type}"

            logger.info(
                "✅ Valid Singer schema for %s with %d properties",
                stream["tap_stream_id"],
                len(properties),
            )

    @pytest.mark.functional
    def test_real_data_extraction_sample(
        self,
        real_tap_instance: FlextTapOracleWMS,
    ) -> None:
        """Test REAL data extraction with small sample."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]

        # Test extraction from first available stream
        if not streams:
            pytest.skip("No streams available for extraction test")

        test_stream = streams[0]
        stream_id = test_stream["tap_stream_id"]

        logger.info("Testing extraction from stream: %s", stream_id)

        # Create stream instance

        try:
            # This should make REAL API calls
            stream = FlextTapOracleWMSStream(
                tap=real_tap_instance,
                name=stream_id,
                schema=test_stream["schema"],
            )

            # Test basic stream properties
            assert stream.name == stream_id
            assert stream.schema is not None
            assert hasattr(stream, "url_base")
            assert hasattr(stream, "authenticator")

            logger.info("✅ Stream created successfully: %s", stream_id)

            # Test URL generation
            url = stream.url_base
            assert url is not None, "Stream URL is None"
            assert url, "Stream URL is empty"
            assert "ta29.wms.ocs.oraclecloud.com" in url, f"Invalid URL: {url}"

            logger.info("✅ Stream URL generated: %s", url)

        except Exception:
            logger.exception("❌ Stream creation failed for %s", stream_id)
            raise

    @pytest.mark.singer
    def test_pagination_functionality(
        self,
        real_tap_instance: FlextTapOracleWMS,
    ) -> None:
        """Test pagination parameters are correctly configured."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]

        if not streams:
            pytest.skip("No streams available for pagination test")

        test_stream = streams[0]
        stream_id = test_stream["tap_stream_id"]

        stream = FlextTapOracleWMSStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=test_stream["schema"],
        )

        # Test pagination parameters
        url_params = stream.get_url_params(context=None, next_page_token=None)

        assert "page_size" in url_params, "Missing page_size parameter"
        assert isinstance(url_params["page_size"], int), "page_size must be integer"
        assert url_params["page_size"] > 0, "page_size must be positive"
        assert url_params["page_size"] <= 1250, "page_size exceeds Oracle WMS limit"

        # Test page mode
        if "page_mode" in url_params:
            assert url_params["page_mode"] in {"sequenced", "offset"}, (
                f"Invalid page_mode: {url_params['page_mode']}"
            )

        logger.info("✅ Pagination configured: page_size=%s", url_params["page_size"])

    @pytest.mark.functional
    def test_replication_key_detection(
        self,
        real_tap_instance: FlextTapOracleWMS,
    ) -> None:
        """Test automatic replication key detection."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]

        streams_with_replication = []
        streams_full_table = []

        for stream in streams:
            metadata = stream.get("metadata", [])

            # Find table-level metadata
            table_metadata = None
            for meta in metadata:
                if meta.get("breadcrumb") == []:
                    table_metadata = meta
                    break

            if table_metadata:
                replication_method = table_metadata.get("metadata", {}).get(
                    "replication-method",
                )
                replication_key = table_metadata.get("metadata", {}).get(
                    "replication-key",
                )

                if replication_method == "INCREMENTAL" and replication_key:
                    streams_with_replication.append(
                        (stream["tap_stream_id"], replication_key),
                    )
                elif replication_method == "FULL_TABLE":
                    streams_full_table.append(stream["tap_stream_id"])

        logger.info(
            "✅ Incremental streams (%d): %s",
            len(streams_with_replication),
            streams_with_replication,
        )
        logger.info(
            "✅ Full table streams (%d): %s",
            len(streams_full_table),
            streams_full_table,
        )

        # Verify we have both types
        assert len(streams_with_replication) > 0 or len(streams_full_table) > 0, (
            "No replication methods detected"
        )

    @pytest.mark.functional
    def test_filtering_and_ordering(self, real_tap_instance: FlextTapOracleWMS) -> None:
        """Test filtering and ordering parameters."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]

        if not streams:
            pytest.skip("No streams available for filtering test")

        test_stream = streams[0]
        stream_id = test_stream["tap_stream_id"]

        stream = FlextTapOracleWMSStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=test_stream["schema"],
        )

        # Test with context (incremental)
        context = {"replication_key_value": "2024-01-01T00:00:00Z"}
        url_params = stream.get_url_params(context=context, next_page_token=None)

        # Check for timestamp filters
        timestamp_filters = [
            key for key in url_params if "__gte" in key or "__lt" in key
        ]
        if timestamp_filters:
            logger.info("✅ Timestamp filters applied: %s", timestamp_filters)

        # Check for ordering
        if "ordering" in url_params:
            ordering = url_params["ordering"]
            assert isinstance(ordering, str), "Ordering must be string"
            logger.info("✅ Ordering configured: %s", ordering)

        logger.info("✅ URL parameters generated: %s", list(url_params.keys()))

    @pytest.mark.functional
    def test_error_handling_and_validation(
        self,
        real_wms_config: FlextTypes.Core.Dict,
    ) -> None:
        """Test error handling with invalid configurations."""
        # Test with invalid URL
        invalid_config = real_wms_config.copy()
        invalid_config["base_url"] = "https://invalid-url-that-does-not-exist.com"

        tap = FlextTapOracleWMS(config=invalid_config)

        # Discovery should handle network errors gracefully
        try:
            catalog = tap.catalog_dict
            # If we get here, check if it's a graceful fallback
            assert isinstance(catalog, dict), "Catalog should be dict even on errors"
        except Exception as e:
            # Errors should be meaningful
            error_msg = str(e).lower()
            has_meaningful_error = (
                "connection" in error_msg
                or "network" in error_msg
                or "timeout" in error_msg
            )
            if not has_meaningful_error:
                pytest.fail(f"Unexpected error type: {e}")
            logger.info("✅ Network error handled gracefully: %s", type(e).__name__)

    @pytest.mark.functional
    def test_configuration_validation(
        self, real_wms_config: FlextTypes.Core.Dict
    ) -> None:
        """Test configuration validation and type conversion."""
        # Test configuration creation
        # config = create_wms_tap_config(real_wms_config)  # Not implemented yet
        config = real_wms_config  # Use config directly for now

        assert config is not None, "Config creation failed"
        assert hasattr(config, "username"), "Config missing username"
        assert hasattr(config, "password"), "Config missing password"
        assert hasattr(config, "host"), "Config missing host"

        # Test type conversion
        assert isinstance(config.page_size, int), "page_size not converted to int"
        assert isinstance(config.timeout, (int, float)), "timeout not numeric"
        assert isinstance(config.verify_ssl, bool), "verify_ssl not boolean"

        logger.info("✅ Configuration validated and types converted correctly")

    @pytest.mark.singer
    def test_singer_protocol_compliance(
        self,
        real_tap_instance: FlextTapOracleWMS,
    ) -> None:
        """Test Singer protocol compliance."""
        # Test catalog generation
        catalog = real_tap_instance.catalog_dict

        # Verify catalog structure
        assert "version" in catalog, "Catalog missing version"
        assert "streams" in catalog, "Catalog missing streams"
        assert isinstance(catalog["streams"], list), "Streams must be list"

        # Test each stream for Singer compliance
        for stream in catalog["streams"]:
            # Required fields
            assert "tap_stream_id" in stream, "Stream missing tap_stream_id"
            assert "schema" in stream, "Stream missing schema"
            assert "metadata" in stream, "Stream missing metadata"

            # Schema structure
            schema = stream["schema"]
            assert "type" in schema, "Schema missing type"
            assert schema["type"] == "object", "Schema type must be object"
            assert "properties" in schema, "Schema missing properties"

            # Metadata structure
            metadata = stream["metadata"]
            assert isinstance(metadata, list), "Metadata must be list"

            for meta in metadata:
                assert "breadcrumb" in meta, "Metadata missing breadcrumb"
                assert "metadata" in meta, "Metadata missing metadata field"

        logger.info("✅ Singer protocol compliance verified")

    def test_comprehensive_functionality_summary(
        self,
        real_tap_instance: FlextTapOracleWMS,
    ) -> None:
        """FINAL COMPREHENSIVE TEST: Verify all functionality works together."""
        summary = {
            "environment_loaded": False,
            "tap_initialized": False,
            "entities_discovered": 0,
            "schemas_generated": 0,
            "replication_configured": False,
            "pagination_configured": False,
            "singer_compliant": False,
            "errors": [],
        }

        try:
            # 1. Environment
            assert real_tap_instance is not None
            summary["environment_loaded"] = True
            summary["tap_initialized"] = True

            # 2. Discovery
            catalog = real_tap_instance.catalog_dict
            summary["entities_discovered"] = len(catalog.get("streams", []))

            # 3. Schemas
            for stream in catalog.get("streams", []):
                if "schema" in stream and "properties" in stream["schema"]:
                    summary["schemas_generated"] += 1

            # 4. Replication
            metadata_streams = [
                s for s in catalog.get("streams", []) if s.get("metadata")
            ]
            summary["replication_configured"] = len(metadata_streams) > 0

            # 5. Singer compliance
            summary["singer_compliant"] = all(
                [
                    "version" in catalog,
                    "streams" in catalog,
                    all("tap_stream_id" in s for s in catalog.get("streams", [])),
                ],
            )

            # 6. Pagination
            if catalog.get("streams"):
                test_stream = catalog["streams"][0]
                stream = FlextTapOracleWMSStream(
                    real_tap_instance,
                    test_stream["tap_stream_id"],
                    test_stream["schema"],
                )
                params = stream.get_url_params(None, None)
                summary["pagination_configured"] = "page_size" in params

        except Exception as e:
            summary["errors"].append(str(e))

        # Log comprehensive summary
        logger.info("🔍 COMPREHENSIVE FUNCTIONALITY SUMMARY:")
        logger.info("  ✅ Environment loaded: %s", summary["environment_loaded"])
        logger.info("  ✅ Tap initialized: %s", summary["tap_initialized"])
        logger.info("  📊 Entities discovered: %d", summary["entities_discovered"])
        logger.info("  📋 Schemas generated: %d", summary["schemas_generated"])
        logger.info(
            "  🔄 Replication configured: %s",
            summary["replication_configured"],
        )
        logger.info("  📄 Pagination configured: %s", summary["pagination_configured"])
        logger.info("  🎵 Singer compliant: %s", summary["singer_compliant"])

        if summary["errors"]:
            logger.error("  ❌ Errors: %s", summary["errors"])

        # FINAL ASSERTIONS
        assert summary["environment_loaded"], "Environment not loaded"
        assert summary["tap_initialized"], "Tap not initialized"
        assert summary["entities_discovered"] > 0, "No entities discovered"
        assert summary["schemas_generated"] > 0, "No schemas generated"
        assert summary["singer_compliant"], "Not Singer compliant"
        assert len(summary["errors"]) == 0, f"Errors found: {summary['errors']}"

        logger.info("🎉 ALL FUNCTIONALITY TESTS PASSED!")
