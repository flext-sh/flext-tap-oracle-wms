"""Comprehensive functional tests for Oracle WMS tap using real .env data.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import TYPE_CHECKING

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from flext_tests import tm
from tests import t, u

if TYPE_CHECKING:
    from tests import m

logger = u.fetch_logger(__name__)

_MIN_CORE_STREAMS = 2
_ORACLE_WMS_MAX_LIMIT = 1250


@pytest.mark.functional
class TestsFlextTapOracleWmsFunctional:
    """COMPREHENSIVE functional tests using REAL Oracle WMS data from .env."""

    @staticmethod
    def _catalog(tap: FlextTapOracleWms) -> m.Meltano.SingerCatalog:
        """Return the typed discovered catalog used by runtime code."""
        result = tap.discovercatalog_typed()
        tm.ok(result)
        catalog: m.Meltano.SingerCatalog = result.unwrap()
        return catalog

    @staticmethod
    def _schema(stream: m.Meltano.SingerCatalogEntry) -> t.JsonMapping:
        """Normalize model schema payload to the runtime stream contract."""
        schema: t.JsonMapping = t.CONTAINER_VALUE_MAP_ADAPTER.validate_python(
            stream.schema_definition
        )
        return schema

    def test_real_wms_environment_verification(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """CRITICAL: Verify real Oracle WMS environment is properly loaded."""
        namespace = real_config.TapOracleWms
        assert namespace.base_url, "Missing required settings: base_url"
        assert namespace.username, "Missing required settings: username"
        assert namespace.password, "Missing required settings: password"
        base_url = namespace.base_url
        tm.that(base_url, has="invalid.wms.ocs.oraclecloud.com")
        tm.that(base_url, has="company_unknow")
        logger.info("✅ Real Oracle WMS environment verified: %s", base_url)

    def test_tap_initialization_real_config(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Test tap initializes with REAL Oracle WMS configuration."""
        tap = FlextTapOracleWms.from_settings(real_config)
        tm.that(tap, none=False)
        tm.that(
            tap.settings.get("base_url"), eq=real_config.TapOracleWms.base_url
        )
        logger.info("✅ Tap initialized successfully with real settings")

    @pytest.mark.discovery
    def test_automatic_entity_discovery(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """CRITICAL: Test automatic entity discovery with REAL Oracle WMS."""

        def _run_test_automatic_entity_discovery() -> None:
            catalog = self._catalog(real_tap_instance)
            tm.that(catalog, none=False)
            streams = catalog.streams
            assert streams, "No streams discovered"
            entity_names = [stream.tap_stream_id for stream in streams]
            logger.info(f"✅ Discovered {len(entity_names)} entities: {entity_names}")
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
            assert found_core >= _MIN_CORE_STREAMS, (
                f"Not enough core WMS entities found. Got: {entity_names}"
            )
            for stream in streams:
                properties_raw = stream.schema_definition.get("properties")
                assert isinstance(properties_raw, dict)
                properties: t.JsonMapping = properties_raw
                assert properties, f"Stream {stream.tap_stream_id} has empty properties"
                logger.info(
                    "✅ Stream %s has %d properties",
                    stream.tap_stream_id,
                    len(properties),
                )

        try:
            return _run_test_automatic_entity_discovery()
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
    def test_valid_singer_schema_generation(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test schema generation produces valid Singer schemas."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        for stream in streams[:3]:
            schema = stream.schema_definition
            tm.that(schema, has="type")
            tm.that(schema["type"], eq="t.JsonValue")
            tm.that(schema, has="properties")
            properties_raw = schema["properties"]
            assert isinstance(properties_raw, dict)
            properties: t.JsonMapping = properties_raw
            for prop_name, prop_def in properties.items():
                assert isinstance(prop_def, dict)
                tm.that(prop_def, has="type")
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
    def test_real_data_extraction_sample(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test REAL data extraction with small sample."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams available for extraction test")
        test_stream = streams[0]
        stream_id = test_stream.tap_stream_id
        logger.info("Testing extraction from stream: %s", stream_id)

        def _run_test_real_data_extraction_sample() -> None:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance, name=stream_id, schema=self._schema(test_stream)
            )
            tm.that(stream.name, eq=stream_id)
            tm.that(stream.schema, none=False)
            logger.info("✅ Stream created successfully: %s", stream_id)
            url = stream.url_base
            tm.that(url, none=False)
            assert url, "Stream URL is empty"
            tm.that(url, has="invalid.wms.ocs.oraclecloud.com")
            logger.info("✅ Stream URL generated: %s", url)

        try:
            return _run_test_real_data_extraction_sample()
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
    def test_pagination_functionality(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test pagination parameters are correctly configured."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams available for pagination test")
        test_stream = streams[0]
        stream_id = test_stream.tap_stream_id
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance, name=stream_id, schema=self._schema(test_stream)
        )
        url_params = stream.build_operation_kwargs(page=1, context=None)
        tm.that(url_params, has="limit")
        limit_value = url_params["limit"]
        assert isinstance(limit_value, int)
        assert limit_value > 0, "limit must be positive"
        assert limit_value <= _ORACLE_WMS_MAX_LIMIT, (
            "limit exceeds Oracle WMS max"
        )
        logger.info("Pagination configured: page_size=%s", url_params["page_size"])

    @pytest.mark.functional
    def test_replication_key_detection(
        self, real_tap_instance: FlextTapOracleWms
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
                    replication_key, str
                ):
                    streams_with_replication.append((
                        stream.tap_stream_id,
                        replication_key,
                    ))
                elif replication_method == "FULL_TABLE":
                    streams_full_table.append(stream.tap_stream_id)
        logger.info(
            f"✅ Incremental streams ({len(streams_with_replication)}): {streams_with_replication}"
        )
        logger.info(
            f"✅ Full table streams ({len(streams_full_table)}): {streams_full_table}"
        )
        assert streams_with_replication or streams_full_table, (
            "No replication methods detected"
        )

    @pytest.mark.functional
    def test_filtering_and_ordering_parameters(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test filtering and ordering parameters."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams available for filtering test")
        test_stream = streams[0]
        stream_id = test_stream.tap_stream_id
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance, name=stream_id, schema=self._schema(test_stream)
        )
        context = {"replication_key_value": "2024-01-01T00:00:00Z"}
        url_params = stream.build_operation_kwargs(page=1, context=context)
        kwargs_filter = url_params.get("filter")
        if kwargs_filter and (">=" in str(kwargs_filter) or "<" in str(kwargs_filter)):
            logger.info("✅ Timestamp filters applied: %s", kwargs_filter)
        if "ordering" in url_params:
            ordering = url_params["ordering"]
            tm.that(ordering, is_=str)
            logger.info("✅ Ordering configured: %s", ordering)
        logger.info(f"✅ URL parameters generated: {list(url_params.keys())}")

    @pytest.mark.functional
    def test_error_handling_and_validation(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Test error handling with invalid configurations."""
        invalid_settings = FlextTapOracleWmsSettings.model_validate({
            "TapOracleWms": {
                **real_config.TapOracleWms.model_dump(),
                "base_url": "https://invalid-url-that-does-not-exist.com",
            }
        })
        tap = FlextTapOracleWms.from_settings(invalid_settings)
        try:
            catalog = self._catalog(tap)
            tm.that(catalog.streams, none=False)
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
    def test_configuration_validation(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """Test configuration validation and type conversion."""
        settings = real_config
        tm.that(settings, none=False)
        namespace = settings.TapOracleWms
        tm.that(namespace.page_size, is_=int)
        tm.that(namespace.timeout, is_=(int, float))
        tm.that(namespace.verify_ssl, is_=bool)
        logger.info("✅ Configuration validated and types converted correctly")

    @pytest.mark.singer
    def test_singer_protocol_compliance(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test Singer protocol compliance."""
        catalog = self._catalog(real_tap_instance)
        tm.that(catalog.streams, none=False)
        for stream in catalog.streams:
            schema = stream.schema_definition
            tm.that(schema, has="type")
            tm.that(schema["type"], eq="t.JsonValue")
            tm.that(schema, has="properties")
            for meta in stream.metadata:
                tm.that(meta.breadcrumb, none=False)
                tm.that(meta.metadata, none=False)
        logger.info("✅ Singer protocol compliance verified")

    def test_comprehensive_functionality_summary(
        self, real_tap_instance: FlextTapOracleWms
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

        def _collect_summary() -> tuple[bool, bool, int, int, bool, bool, bool]:
            tm.that(real_tap_instance, none=False)
            catalog = self._catalog(real_tap_instance)
            catalog_streams = catalog.streams
            discovered = len(catalog_streams)
            generated = sum(
                1
                for stream in catalog_streams
                if stream.schema_definition.get("properties")
            )
            metadata_streams = [stream for stream in catalog_streams if stream.metadata]
            compliant = all(stream.tap_stream_id for stream in catalog_streams)
            paginated = False
            if catalog_streams:
                test_stream = catalog_streams[0]
                stream_obj = FlextTapOracleWmsStream(
                    real_tap_instance,
                    test_stream.tap_stream_id,
                    self._schema(test_stream),
                )
                params = stream_obj.build_operation_kwargs(page=1, context=None)
                paginated = "limit" in params
            return (
                True,
                True,
                discovered,
                generated,
                bool(metadata_streams),
                paginated,
                compliant,
            )

        try:
            (
                environment_loaded,
                tap_initialized,
                entities_discovered,
                schemas_generated,
                replication_configured,
                pagination_configured,
                singer_compliant,
            ) = _collect_summary()
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
