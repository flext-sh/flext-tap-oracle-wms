"""Comprehensive functional tests for Oracle WMS tap using real .env data.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence

import pytest
from flext_core import FlextLogger

from flext_tap_oracle_wms import (
    FlextTapOracleWms,
    FlextTapOracleWmsSettings,
    FlextTapOracleWmsStream,
)
from tests import t

logger = FlextLogger(__name__)


@pytest.mark.functional
class TestOracleWMSFunctionalComplete:
    """COMPREHENSIVE functional tests using REAL Oracle WMS data from .env."""

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_real_wms_environment_verification(
        self,
        real_wms_config: MutableMapping[str, t.NormalizedValue],
    ) -> None:
        """CRITICAL: Verify real Oracle WMS environment is properly loaded."""
        required_config = ["base_url", "username", "password"]
        for key in required_config:
            assert real_wms_config.get(key), f"Missing required config: {key}"
            assert real_wms_config[key], f"Empty config value: {key}"
        base_url = str(real_wms_config["base_url"])
        assert "invalid.wms.ocs.oraclecloud.com" in base_url, (
            f"Not ta29 environment: {base_url}"
        )
        assert "company_unknow" in base_url, (
            f"Not company_unknow environment: {base_url}"
        )
        logger.info("✅ Real Oracle WMS environment verified: %s", base_url)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_tap_initialization_real_config(
        self,
        real_wms_config: MutableMapping[str, t.NormalizedValue],
    ) -> None:
        """Test tap initializes with REAL Oracle WMS configuration."""
        tap = FlextTapOracleWms(config=real_wms_config)
        assert tap is not None
        assert hasattr(tap, "config")
        assert tap.config.get("base_url") == real_wms_config["base_url"]
        logger.info("✅ Tap initialized successfully with real config")

    @pytest.mark.discovery
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_automatic_entity_discovery(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """CRITICAL: Test automatic entity discovery with REAL Oracle WMS."""
        try:
            catalog = real_tap_instance.catalog_dict
            assert catalog is not None, "Catalog is None"
            assert "streams" in catalog, "No streams in catalog"
            assert isinstance(catalog["streams"], list), "Streams is not a list"
            streams = catalog["streams"]
            assert streams, "No streams discovered"
            entity_names = [stream["tap_stream_id"] for stream in streams]
            logger.info(
                "✅ Discovered %d entities: %s",
                len(entity_names),
                entity_names,
            )
            essential_entities = ["allocation"]
            for entity in essential_entities:
                found_entities = [
                    name for name in entity_names if entity in name.lower()
                ]
                assert found_entities, (
                    f"Essential entity '{entity}' not found in: {entity_names}"
                )
            core_wms_patterns = ["allocation", "company", "location"]
            found_core = 0
            for pattern in core_wms_patterns:
                if any(pattern in name.lower() for name in entity_names):
                    found_core += 1
            assert found_core >= 2, (
                f"Not enough core WMS entities found. Got: {entity_names}"
            )
            for stream in streams:
                assert "schema" in stream, (
                    f"Stream {stream['tap_stream_id']} missing schema"
                )
                assert "properties" in stream["schema"], (
                    f"Stream {stream['tap_stream_id']} schema missing properties"
                )
                properties_raw = stream["schema"]["properties"]
                assert isinstance(properties_raw, Mapping), (
                    f"Stream {stream['tap_stream_id']} properties is not a mapping"
                )
                properties: Mapping[str, t.ContainerValue] = properties_raw
                assert properties, (
                    f"Stream {stream['tap_stream_id']} has empty properties"
                )
                logger.info(
                    "✅ Stream %s has %d properties",
                    stream["tap_stream_id"],
                    len(properties),
                )
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ):
            logger.exception("❌ Entity discovery failed")
            raise

    @pytest.mark.singer
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_valid_singer_schema_generation(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test schema generation produces valid Singer schemas."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]
        for stream in streams[:3]:
            schema = stream["schema"]
            assert "type" in schema, (
                f"Schema missing type for {stream['tap_stream_id']}"
            )
            assert schema["type"] == "t.NormalizedValue", (
                f"Invalid schema type for {stream['tap_stream_id']}"
            )
            assert "properties" in schema, (
                f"Schema missing properties for {stream['tap_stream_id']}"
            )
            properties_raw = schema["properties"]
            assert isinstance(properties_raw, Mapping), (
                f"Schema properties is not a mapping for {stream['tap_stream_id']}"
            )
            properties: Mapping[str, t.ContainerValue] = properties_raw
            for prop_name, prop_def in properties.items():
                assert isinstance(prop_def, Mapping), (
                    f"Property {prop_name} not a mapping"
                )
                assert "type" in prop_def, f"Property {prop_name} missing type"
                prop_type = prop_def["type"]
                valid_types: Sequence[t.ContainerValue] = [
                    "string",
                    "integer",
                    "number",
                    "boolean",
                    "array",
                    "t.NormalizedValue",
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
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_real_data_extraction_sample(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test REAL data extraction with small sample."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]
        if not streams:
            pytest.skip("No streams available for extraction test")
        test_stream = streams[0]
        stream_id = test_stream["tap_stream_id"]
        logger.info("Testing extraction from stream: %s", stream_id)
        try:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance,
                name=stream_id,
                schema=test_stream["schema"],
            )
            assert stream.name == stream_id
            assert stream.schema is not None  # type: ignore[reportUnknownMemberType]
            assert hasattr(stream, "url_base")
            assert hasattr(stream, "authenticator")
            logger.info("✅ Stream created successfully: %s", stream_id)
            url = stream.url_base
            assert url is not None, "Stream URL is None"
            assert url, "Stream URL is empty"
            assert "invalid.wms.ocs.oraclecloud.com" in url, f"Invalid URL: {url}"
            logger.info("✅ Stream URL generated: %s", url)
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ):
            logger.exception("❌ Stream creation failed for %s", stream_id)
            raise

    @pytest.mark.singer
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_pagination_functionality(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test pagination parameters are correctly configured."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]
        if not streams:
            pytest.skip("No streams available for pagination test")
        test_stream = streams[0]
        stream_id = test_stream["tap_stream_id"]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=test_stream["schema"],
        )
        url_params = stream.get_url_params(context=None, next_page_token=None)
        assert "page_size" in url_params, "Missing page_size parameter"
        assert isinstance(url_params["page_size"], int), "page_size must be integer"
        assert url_params["page_size"] > 0, "page_size must be positive"
        assert url_params["page_size"] <= 1250, "page_size exceeds Oracle WMS limit"
        if "page_mode" in url_params:
            assert url_params["page_mode"] in {"sequenced", "offset"}, (
                f"Invalid page_mode: {url_params['page_mode']}"
            )
        logger.info("✅ Pagination configured: page_size=%s", url_params["page_size"])

    @pytest.mark.functional
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_replication_key_detection(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test automatic replication key detection."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]
        streams_with_replication: MutableSequence[tuple[str, t.ContainerValue]] = []
        streams_full_table: MutableSequence[str] = []
        for stream in streams:
            metadata = stream.get("metadata", [])
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
                    streams_with_replication.append((
                        stream["tap_stream_id"],
                        replication_key,
                    ))
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
        assert streams_with_replication or streams_full_table, (
            "No replication methods detected"
        )

    @pytest.mark.functional
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_filtering_and_ordering_parameters(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test filtering and ordering parameters."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog["streams"]
        if not streams:
            pytest.skip("No streams available for filtering test")
        test_stream = streams[0]
        stream_id = test_stream["tap_stream_id"]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=test_stream["schema"],
        )
        context = {"replication_key_value": "2024-01-01T00:00:00Z"}
        url_params = stream.get_url_params(context=context, next_page_token=None)
        timestamp_filters = [
            key for key in url_params if "__gte" in key or "__lt" in key
        ]
        if timestamp_filters:
            logger.info("✅ Timestamp filters applied: %s", timestamp_filters)
        if "ordering" in url_params:
            ordering = url_params["ordering"]
            assert isinstance(ordering, str), "Ordering must be string"
            logger.info("✅ Ordering configured: %s", ordering)
        logger.info("✅ URL parameters generated: %s", list(url_params.keys()))

    @pytest.mark.functional
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_error_handling_and_validation(
        self,
        real_wms_config: MutableMapping[str, t.NormalizedValue],
    ) -> None:
        """Test error handling with invalid configurations."""
        invalid_config: MutableMapping[str, t.NormalizedValue] = dict(real_wms_config)
        invalid_config["base_url"] = "https://invalid-url-that-does-not-exist.com"
        tap = FlextTapOracleWms(config=invalid_config)
        try:
            catalog = tap.catalog_dict
            assert isinstance(catalog, dict), (
                "Catalog should be t.ContainerMapping even on errors"
            )
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ) as e:
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
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_configuration_validation(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test configuration validation and type conversion."""
        config = real_config
        assert config is not None, "Config creation failed"
        assert hasattr(config, "username"), "Config missing username"
        assert hasattr(config, "password"), "Config missing password"
        assert hasattr(config, "base_url"), "Config missing base_url"
        assert isinstance(config.page_size, int), "page_size not converted to int"
        assert isinstance(config.timeout, (int, float)), "timeout not numeric"
        assert isinstance(config.verify_ssl, bool), "verify_ssl not boolean"
        logger.info("✅ Configuration validated and types converted correctly")

    @pytest.mark.singer
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_singer_protocol_compliance(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test Singer protocol compliance."""
        catalog = real_tap_instance.catalog_dict
        assert catalog["streams"] is not None, "Catalog missing streams"
        assert isinstance(catalog["streams"], list), "Streams must be list"
        for stream in catalog["streams"]:
            assert "tap_stream_id" in stream, "Stream missing tap_stream_id"
            assert "schema" in stream, "Stream missing schema"
            assert "metadata" in stream, "Stream missing metadata"
            schema = stream["schema"]
            assert "type" in schema, "Schema missing type"
            assert schema["type"] == "t.NormalizedValue", (
                "Schema type must be t.NormalizedValue"
            )
            assert "properties" in schema, "Schema missing properties"
            metadata = stream["metadata"]
            assert isinstance(metadata, list), "Metadata must be list"
            for meta in metadata:
                assert "breadcrumb" in meta, "Metadata missing breadcrumb"
                assert "metadata" in meta, "Metadata missing metadata field"
        logger.info("✅ Singer protocol compliance verified")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_comprehensive_functionality_summary(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """FINAL COMPREHENSIVE TEST: Verify all functionality works together."""
        environment_loaded: bool = False
        tap_initialized: bool = False
        entities_discovered: int = 0
        schemas_generated: int = 0
        replication_configured: bool = False
        pagination_configured: bool = False
        singer_compliant: bool = False
        errors: MutableSequence[str] = []
        try:
            assert real_tap_instance is not None
            environment_loaded = True
            tap_initialized = True
            catalog = real_tap_instance.catalog_dict
            catalog_streams = catalog["streams"]
            entities_discovered = len(catalog_streams)
            for stream in catalog_streams:
                if "schema" in stream and "properties" in stream["schema"]:
                    schemas_generated += 1
            metadata_streams = [s for s in catalog_streams if s.get("metadata")]
            replication_configured = bool(metadata_streams)
            singer_compliant = all("tap_stream_id" in s for s in catalog_streams)
            if catalog_streams:
                test_stream = catalog_streams[0]
                stream_obj = FlextTapOracleWmsStream(
                    real_tap_instance,
                    test_stream["tap_stream_id"],
                    test_stream["schema"],
                )
                params = stream_obj.get_url_params(None, None)
                pagination_configured = "page_size" in params
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ) as e:
            errors.append(str(e))
        logger.info("🔍 COMPREHENSIVE FUNCTIONALITY SUMMARY:")
        logger.info("  ✅ Environment loaded: %s", environment_loaded)
        logger.info("  ✅ Tap initialized: %s", tap_initialized)
        logger.info("  📊 Entities discovered: %d", entities_discovered)
        logger.info("  📋 Schemas generated: %d", schemas_generated)
        logger.info("  🔄 Replication configured: %s", replication_configured)
        logger.info("  📄 Pagination configured: %s", pagination_configured)
        logger.info("  🎵 Singer compliant: %s", singer_compliant)
        if errors:
            logger.error("  ❌ Errors: %s", errors)
        assert environment_loaded, "Environment not loaded"
        assert tap_initialized, "Tap not initialized"
        assert entities_discovered > 0, "No entities discovered"
        assert schemas_generated > 0, "No schemas generated"
        assert singer_compliant, "Not Singer compliant"
        assert not errors, f"Errors found: {errors}"
        logger.info("🎉 ALL FUNCTIONALITY TESTS PASSED!")
