"""Comprehensive functional tests for Oracle WMS tap using real .env data.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableSequence,
)

import pytest

from flext_tap_oracle_wms.settings import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from tests.models import m
from tests.typings import t
from tests.utilities import u

logger = u.fetch_logger(__name__)


@pytest.mark.functional
class TestsFlextTapOracleWmsFunctional:
    """COMPREHENSIVE functional tests using REAL Oracle WMS data from .env."""

    @staticmethod
    def _catalog(tap: FlextTapOracleWms) -> m.Meltano.SingerCatalog:
        """Return the typed discovered catalog used by runtime code."""
        result = tap.discovercatalog_typed()
        assert result.success, result.error
        return result.value

    @staticmethod
    def _schema(
        stream: m.Meltano.SingerCatalogEntry,
    ) -> t.JsonMapping:
        """Normalize model schema payload to the runtime stream contract."""
        return t.CONTAINER_VALUE_MAP_ADAPTER.validate_python(
            stream.schema_definition,
        )

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_real_wms_environment_verification(
        self,
        real_wms_config: t.MutableJsonMapping,
    ) -> None:
        """CRITICAL: Verify real Oracle WMS environment is properly loaded."""
        required_config = ["base_url", "username", "password"]
        for key in required_config:
            assert real_wms_config.get(key), f"Missing required settings: {key}"
            assert real_wms_config[key], f"Empty settings value: {key}"
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
        real_wms_config: t.MutableJsonMapping,
    ) -> None:
        """Test tap initializes with REAL Oracle WMS configuration."""
        tap = FlextTapOracleWms(settings=real_wms_config)
        assert tap is not None
        assert tap.settings.get("base_url") == real_wms_config["base_url"]
        logger.info("✅ Tap initialized successfully with real settings")

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
            catalog = self._catalog(real_tap_instance)
            assert catalog is not None, "Catalog is None"
            streams = catalog.streams
            assert streams, "No streams discovered"
            entity_names = [stream.tap_stream_id for stream in streams]
            logger.info(
                f"✅ Discovered {len(entity_names)} entities: {entity_names}",
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
                properties_raw = stream.schema_definition.get("properties")
                assert isinstance(properties_raw, Mapping), (
                    f"Stream {stream.tap_stream_id} properties is not a mapping"
                )
                properties: t.JsonMapping = properties_raw
                assert properties, f"Stream {stream.tap_stream_id} has empty properties"
                logger.info(
                    "✅ Stream %s has %d properties",
                    stream.tap_stream_id,
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
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        for stream in streams[:3]:
            schema = stream.schema_definition
            assert "type" in schema, f"Schema missing type for {stream.tap_stream_id}"
            assert schema["type"] == "t.JsonValue", (
                f"Invalid schema type for {stream.tap_stream_id}"
            )
            assert "properties" in schema, (
                f"Schema missing properties for {stream.tap_stream_id}"
            )
            properties_raw = schema["properties"]
            assert isinstance(properties_raw, Mapping), (
                f"Schema properties is not a mapping for {stream.tap_stream_id}"
            )
            properties: t.JsonMapping = properties_raw
            for prop_name, prop_def in properties.items():
                assert isinstance(prop_def, Mapping), (
                    f"Property {prop_name} not a mapping"
                )
                assert "type" in prop_def, f"Property {prop_name} missing type"
                prop_type = prop_def["type"]
                valid_types: t.JsonList = [
                    "string",
                    "integer",
                    "number",
                    "boolean",
                    "array",
                    "t.JsonValue",
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
                stream.tap_stream_id,
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
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams available for extraction test")
        test_stream = streams[0]
        stream_id = test_stream.tap_stream_id
        logger.info("Testing extraction from stream: %s", stream_id)
        try:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance,
                name=stream_id,
                schema=self._schema(test_stream),
            )
            assert stream.name == stream_id
            assert stream.schema is not None
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
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams available for pagination test")
        test_stream = streams[0]
        stream_id = test_stream.tap_stream_id
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=self._schema(test_stream),
        )
        url_params = stream._build_operation_kwargs(page=1, context=None)
        assert "limit" in url_params, "Missing limit parameter"
        assert isinstance(url_params["limit"], int), "limit must be integer"
        assert url_params["limit"] > 0, "limit must be positive"
        assert url_params["limit"] <= 1250, "limit exceeds Oracle WMS max"
        logger.info(f"✅ Pagination configured: page_size={url_params['page_size']}")

    @pytest.mark.functional
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_replication_key_detection(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test automatic replication key detection."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        streams_with_replication: MutableSequence[tuple[str, t.JsonValue]] = []
        streams_full_table: MutableSequence[str] = []
        for stream in streams:
            table_metadata = None
            for meta in stream.metadata:
                if meta.breadcrumb == []:
                    table_metadata = meta
                    break
            if table_metadata:
                replication_method = table_metadata.metadata.get("replication-method")
                replication_key = table_metadata.metadata.get("replication-key")
                if replication_method == "INCREMENTAL" and isinstance(
                    replication_key,
                    str,
                ):
                    streams_with_replication.append((
                        stream.tap_stream_id,
                        replication_key,
                    ))
                elif replication_method == "FULL_TABLE":
                    streams_full_table.append(stream.tap_stream_id)
        logger.info(
            f"✅ Incremental streams ({len(streams_with_replication)}): {streams_with_replication}",
        )
        logger.info(
            f"✅ Full table streams ({len(streams_full_table)}): {streams_full_table}",
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
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams available for filtering test")
        test_stream = streams[0]
        stream_id = test_stream.tap_stream_id
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=self._schema(test_stream),
        )
        context = {"replication_key_value": "2024-01-01T00:00:00Z"}
        url_params = stream._build_operation_kwargs(page=1, context=context)
        kwargs_filter = url_params.get("filter")
        if kwargs_filter and (">=" in str(kwargs_filter) or "<" in str(kwargs_filter)):
            logger.info(f"✅ Timestamp filters applied: {kwargs_filter}")
        if "ordering" in url_params:
            ordering = url_params["ordering"]
            assert isinstance(ordering, str), "Ordering must be string"
            logger.info("✅ Ordering configured: %s", ordering)
        logger.info(f"✅ URL parameters generated: {list(url_params.keys())}")

    @pytest.mark.functional
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_error_handling_and_validation(
        self,
        real_wms_config: t.MutableJsonMapping,
    ) -> None:
        """Test error handling with invalid configurations."""
        invalid_config: t.MutableJsonMapping = dict(real_wms_config)
        invalid_config["base_url"] = "https://invalid-url-that-does-not-exist.com"
        tap = FlextTapOracleWms(settings=invalid_config)
        try:
            catalog = self._catalog(tap)
            assert catalog.streams is not None, "Catalog should expose typed streams"
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
        settings = real_config
        assert settings is not None, "Config creation failed"
        assert isinstance(settings.page_size, int), "page_size not converted to int"
        assert isinstance(settings.timeout, (int, float)), "timeout not numeric"
        assert isinstance(settings.verify_ssl, bool), "verify_ssl not boolean"
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
        catalog = self._catalog(real_tap_instance)
        assert catalog.streams is not None, "Catalog missing streams"
        for stream in catalog.streams:
            schema = stream.schema_definition
            assert "type" in schema, "Schema missing type"
            assert schema["type"] == "t.JsonValue", "Schema type must be t.JsonValue"
            assert "properties" in schema, "Schema missing properties"
            for meta in stream.metadata:
                assert meta.breadcrumb is not None, "Metadata missing breadcrumb"
                assert meta.metadata is not None, "Metadata missing metadata field"
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
            catalog = self._catalog(real_tap_instance)
            catalog_streams = catalog.streams
            entities_discovered = len(catalog_streams)
            for stream in catalog_streams:
                if stream.schema_definition.get("properties"):
                    schemas_generated += 1
            metadata_streams = [stream for stream in catalog_streams if stream.metadata]
            replication_configured = bool(metadata_streams)
            singer_compliant = all(stream.tap_stream_id for stream in catalog_streams)
            if catalog_streams:
                test_stream = catalog_streams[0]
                stream_obj = FlextTapOracleWmsStream(
                    real_tap_instance,
                    test_stream.tap_stream_id,
                    self._schema(test_stream),
                )
                params = stream_obj._build_operation_kwargs(page=1, context=None)
                pagination_configured = "limit" in params
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
            logger.error(f"  ❌ Errors: {errors}")
        assert environment_loaded, "Environment not loaded"
        assert tap_initialized, "Tap not initialized"
        assert entities_discovered > 0, "No entities discovered"
        assert schemas_generated > 0, "No schemas generated"
        assert singer_compliant, "Not Singer compliant"
        assert not errors, f"Errors found: {errors}"
        logger.info("🎉 ALL FUNCTIONALITY TESTS PASSED!")
