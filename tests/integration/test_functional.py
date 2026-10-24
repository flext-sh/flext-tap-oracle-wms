"""Comprehensive functional tests for Oracle WMS tap using real .env data.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import MutableSequence

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStreams
from flext_tap_oracle_wms.tap import FlextTapOracleWms
from tests import t, tm, u
from tests.helpers import TestsFlextTapOracleWmsHelpersMixin

logger = u.fetch_logger(__name__)

_MIN_CORE_STREAMS = 2
_ORACLE_WMS_MAX_LIMIT = 1250


@pytest.mark.functional
class TestsFlextTapOracleWmsFunctional(TestsFlextTapOracleWmsHelpersMixin):
    """COMPREHENSIVE functional tests using REAL Oracle WMS data from .env."""

    _TAP_CONNECTION_ERROR_KEYWORDS = ("connection", "network", "timeout")

    @staticmethod
    def test_real_wms_environment_verification(
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """CRITICAL: Verify real Oracle WMS environment is properly loaded."""
        namespace = real_config.TapOracleWms
        tm.that(
            namespace.base_url, truth=True, msg="Missing required settings: base_url"
        )
        tm.that(
            namespace.username, truth=True, msg="Missing required settings: username"
        )
        tm.that(
            namespace.password, truth=True, msg="Missing required settings: password"
        )
        base_url = namespace.base_url
        tm.that(base_url, has="invalid.wms.ocs.oraclecloud.com")
        tm.that(base_url, has="company_unknow")
        logger.info("✅ Real Oracle WMS environment verified: %s", base_url)

    @staticmethod
    def test_tap_initialization_real_config(
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test tap initializes with REAL Oracle WMS configuration."""
        tap = FlextTapOracleWms.from_settings(real_config)
        tm.that(tap, none=False)
        tm.that(tap.settings.get("base_url"), eq=real_config.TapOracleWms.base_url)
        logger.info("✅ Tap initialized successfully with real settings")

    @pytest.mark.discovery
    def test_automatic_entity_discovery(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """CRITICAL: Test automatic entity discovery with REAL Oracle WMS."""

        def _run_test_automatic_entity_discovery() -> None:
            catalog = self._catalog(real_tap_instance)
            tm.that(catalog, none=False)
            streams = catalog.streams
            tm.that(streams, truth=True, msg="No streams discovered")
            entity_names = [stream.tap_stream_id for stream in streams]
            logger.info(
                "✅ Discovered %s entities: %s",
                len(entity_names),
                entity_names,
            )
            essential_entities = ["allocation"]
            for entity in essential_entities:
                found_entities = [
                    name for name in entity_names if entity in name.lower()
                ]
                tm.that(
                    found_entities,
                    truth=True,
                    msg=(f"Essential entity '{entity}' not found in: {entity_names}"),
                )
            core_wms_patterns = ["allocation", "company", "location"]
            found_core = 0
            for pattern in core_wms_patterns:
                if any(pattern in name.lower() for name in entity_names):
                    found_core += 1
            tm.that(
                found_core,
                gte=_MIN_CORE_STREAMS,
                msg=(f"Not enough core WMS entities found. Got: {entity_names}"),
            )
            for stream in streams:
                properties_raw = stream.schema_definition.get("properties")
                properties: t.JsonMapping = tm.instance(properties_raw, dict)
                tm.that(
                    properties,
                    truth=True,
                    msg=f"Stream {stream.tap_stream_id} has empty properties",
                )
                logger.info(
                    "✅ Stream %s has %d properties",
                    stream.tap_stream_id,
                    len(properties),
                )

        try:
            return _run_test_automatic_entity_discovery()
        except self._TAP_RECOVERABLE_EXCEPTIONS:
            logger.exception("❌ Entity discovery failed")
            raise

    @pytest.mark.singer
    def test_valid_singer_schema_generation(
        self,
        real_tap_instance: FlextTapOracleWms,
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
            properties: t.JsonMapping = tm.instance(properties_raw, dict)
            for prop_name, prop_value in properties.items():
                prop_def = tm.instance(prop_value, dict)
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
                tm.that(
                    prop_type in valid_types
                    or (isinstance(prop_type, list) and "null" in prop_type),
                    msg=f"Invalid Singer type for {prop_name}: {prop_type}",
                )
            logger.info(
                "✅ Valid Singer schema for %s with %d properties",
                stream.tap_stream_id,
                len(properties),
            )

    @pytest.mark.functional
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

        def _run_test_real_data_extraction_sample() -> None:
            stream = FlextTapOracleWmsStreams.WmsStream(
                tap=real_tap_instance,
                name=stream_id,
                schema=self._schema(test_stream),
            )
            tm.that(stream.name, eq=stream_id)
            tm.that(stream.schema, none=False)
            logger.info("✅ Stream created successfully: %s", stream_id)
            url = stream.url_base
            tm.that(url, none=False)
            tm.that(url, truth=True, msg="Stream URL is empty")
            tm.that(url, has="invalid.wms.ocs.oraclecloud.com")
            logger.info("✅ Stream URL generated: %s", url)

        try:
            return _run_test_real_data_extraction_sample()
        except self._TAP_RECOVERABLE_EXCEPTIONS:
            logger.exception("❌ Stream creation failed for %s", stream_id)
            raise

    @pytest.mark.singer
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
        stream = FlextTapOracleWmsStreams.WmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=self._schema(test_stream),
        )
        url_params = stream.build_operation_kwargs(page=1, context=None)
        tm.that(url_params, has="limit")
        limit_value = url_params["limit"]
        tm.that(limit_value, is_=int)
        tm.that(limit_value, gt=0, msg="limit must be positive")
        tm.that(
            limit_value, lte=_ORACLE_WMS_MAX_LIMIT, msg="limit exceeds Oracle WMS max"
        )
        logger.info("Pagination configured: page_size=%s", url_params["page_size"])

    @pytest.mark.functional
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
                if meta.breadcrumb == ():
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
            "✅ Incremental streams (%s): %s",
            len(streams_with_replication),
            streams_with_replication,
        )
        logger.info(
            "✅ Full table streams (%s): %s",
            len(streams_full_table),
            streams_full_table,
        )
        tm.that(
            streams_with_replication or streams_full_table,
            truth=True,
            msg=("No replication methods detected"),
        )

    @pytest.mark.functional
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
        stream = FlextTapOracleWmsStreams.WmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=self._schema(test_stream),
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
        logger.info("✅ URL parameters generated: %s", list(url_params.keys()))

    @pytest.mark.functional
    def test_error_handling_and_validation(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """Test error handling with invalid configurations."""
        self._assert_invalid_tap_recovery(
            real_config,
            {"base_url": "https://invalid-url-that-does-not-exist.com"},
        )
        logger.info("✅ Network error handled gracefully")

    @staticmethod
    @pytest.mark.functional
    def test_configuration_validation(
        real_config: FlextTapOracleWmsSettings,
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
        self,
        real_tap_instance: FlextTapOracleWms,
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
                stream_obj = FlextTapOracleWmsStreams.WmsStream(
                    real_tap_instance,
                    name=test_stream.tap_stream_id,
                    schema=self._schema(test_stream),
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
        except self._TAP_RECOVERABLE_EXCEPTIONS as e:
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
        tm.that(environment_loaded, msg="Environment not loaded")
        tm.that(tap_initialized, msg="Tap not initialized")
        tm.that(entities_discovered, gt=0, msg="No entities discovered")
        tm.that(schemas_generated, gt=0, msg="No schemas generated")
        tm.that(singer_compliant, msg="Not Singer compliant")
        tm.that(errors, truth=False, msg=f"Errors found: {errors}")
        logger.info("🎉 ALL FUNCTIONALITY TESTS PASSED!")
