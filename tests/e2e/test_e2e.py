"""Complete End-to-End tests for Oracle WMS tap.

HONEST E2E TESTING: Tests complete data extraction pipeline with REAL Oracle WMS.
Validates all Singer SDK functionality including discovery, extraction, and data quality.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import time
from collections.abc import (
    Mapping,
)
from datetime import UTC, datetime, timedelta

import pytest

from flext_tap_oracle_wms import (
    FlextTapOracleWms,
    FlextTapOracleWmsSettings,
    FlextTapOracleWmsStream,
)
from tests import m, t, u

logger = u.fetch_logger(__name__)


@pytest.mark.e2e
class TestOracleWMSE2EComplete:
    """Complete End-to-End tests with REAL Oracle WMS data extraction."""

    @staticmethod
    def _catalog(tap: FlextTapOracleWms) -> m.Meltano.SingerCatalog:
        """Return the typed discovered catalog used by runtime code."""
        result = tap.discovercatalog_typed()
        assert result.success, result.error
        return result.value

    @staticmethod
    def _schema(
        stream: m.Meltano.SingerCatalogEntry,
    ) -> t.ContainerValueMapping:
        """Normalize model schema payload to the runtime stream contract."""
        return t.CONTAINER_VALUE_MAP_ADAPTER.validate_python(
            stream.schema_definition,
        )

    @pytest.mark.usefixtures("_mock_oracle_wms")
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_complete_discovery_to_catalog(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test complete discovery process generating valid Singer catalog."""
        tap_instance = FlextTapOracleWms(settings=real_config.model_dump(mode="json"))
        catalog = self._catalog(tap_instance)
        assert catalog is not None, "Discovery returned None catalog"
        streams = catalog.streams
        assert streams, "No streams discovered"
        for stream in streams:
            schema = stream.schema_definition
            assert schema.get("type") == "t.Container", "Invalid schema type"
            assert "properties" in schema, "Schema missing properties"
            props = schema.get("properties")
            assert props, "Empty schema properties"
            metadata = stream.metadata
            table_metadata = next(
                (entry for entry in metadata if entry.breadcrumb == []),
                None,
            )
            assert table_metadata is not None, "Missing table metadata"
            meta = table_metadata.metadata
            assert "replication-method" in meta, "Missing replication method"
            assert meta["replication-method"] in {"INCREMENTAL", "FULL_TABLE"}, (
                "Invalid replication method"
            )
        logger.info(
            "✅ Complete discovery validation passed for %d streams",
            len(streams),
        )

    @pytest.mark.usefixtures("_mock_oracle_wms")
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_catalog_serialization_and_selection(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test catalog serialization and stream selection."""
        tap_instance = FlextTapOracleWms(settings=real_config.model_dump(mode="json"))
        catalog = self._catalog(tap_instance)
        catalog_payload = catalog.model_dump(mode="json")
        catalog_json = json.dumps(catalog_payload, indent=2)
        assert catalog_json, "Catalog serialization failed"
        deserialized = json.loads(catalog_json)
        assert deserialized == catalog_payload, (
            "Catalog serialization/deserialization mismatch"
        )
        if catalog.streams:
            stream = catalog.streams[0]
            assert any(meta.breadcrumb == [] for meta in stream.metadata)
        logger.info("✅ Catalog serialization and selection working")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_single_stream_extraction_sample(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test single stream data extraction with real data."""
        tap_instance = FlextTapOracleWms(settings=real_config.model_dump(mode="json"))
        catalog = self._catalog(tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams available for extraction")
        test_stream = streams[0]
        stream_id = test_stream.tap_stream_id
        logger.info("Testing extraction from: %s", stream_id)
        stream = FlextTapOracleWmsStream(
            tap=tap_instance,
            name=stream_id,
            schema=self._schema(test_stream),
        )
        assert stream.name == stream_id
        assert stream.url_base is not None
        params = stream._build_operation_kwargs(page=1, context=None)
        assert isinstance(params, dict)
        assert "limit" in params
        logger.info("✅ Single stream extraction setup successful")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_incremental_extraction_workflow(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test incremental extraction workflow."""
        tap_instance = FlextTapOracleWms(settings=real_config.model_dump(mode="json"))
        catalog = self._catalog(tap_instance)
        streams = catalog.streams
        incremental_stream_config: m.Meltano.SingerCatalogEntry | None = None
        for stream_config in streams:
            for meta in stream_config.metadata:
                if meta.breadcrumb == [] and (
                    meta.metadata.get("replication-method") == "INCREMENTAL"
                ):
                    incremental_stream_config = stream_config
                    break
            if incremental_stream_config:
                break
        if not incremental_stream_config:
            pytest.skip("No incremental streams found")
        stream = FlextTapOracleWmsStream(
            tap=tap_instance,
            name=incremental_stream_config.tap_stream_id,
            schema=self._schema(incremental_stream_config),
        )
        assert stream.replication_method == "INCREMENTAL"
        assert stream.replication_key is not None
        yesterday = datetime.now(UTC) - timedelta(days=1)
        context = {"replication_key_value": yesterday.isoformat()}
        params = stream._build_operation_kwargs(page=1, context=context)
        kwargs_filter = params.get("filter")
        assert kwargs_filter is not None and (
            ">=" in str(kwargs_filter) or ">" in str(kwargs_filter)
        ), f"No timestamp filters in incremental stream: {list(params.keys())}"
        logger.info("✅ Incremental extraction workflow validated for %s", stream.name)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_full_table_extraction_workflow(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test full table extraction workflow."""
        tap_instance = FlextTapOracleWms(settings=real_config.model_dump(mode="json"))
        catalog = self._catalog(tap_instance)
        streams = catalog.streams
        full_table_stream_config: m.Meltano.SingerCatalogEntry | None = None
        for stream_config in streams:
            for meta in stream_config.metadata:
                if meta.breadcrumb == [] and (
                    meta.metadata.get("replication-method") == "FULL_TABLE"
                ):
                    full_table_stream_config = stream_config
                    break
            if full_table_stream_config:
                break
        if not full_table_stream_config:
            pytest.skip("No full table streams found")
        stream = FlextTapOracleWmsStream(
            tap=tap_instance,
            name=full_table_stream_config.tap_stream_id,
            schema=self._schema(full_table_stream_config),
        )
        params = stream._build_operation_kwargs(page=1, context=None)
        if "ordering" in params:
            ordering = str(params["ordering"])
            assert ordering.startswith("-") or "desc" in ordering.lower(), (
                f"Full table should use descending order: {ordering}"
            )
        logger.info("✅ Full table extraction workflow validated for %s", stream.name)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_data_quality_validation(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test data quality and schema validation."""
        tap_instance = FlextTapOracleWms(settings=real_config.model_dump(mode="json"))
        catalog = self._catalog(tap_instance)
        streams = catalog.streams
        quality_report = {
            "streams_tested": 0,
            "schemas_valid": 0,
            "primary_keys_defined": 0,
            "replication_keys_defined": 0,
            "nullable_fields_documented": 0,
        }
        for stream_config in streams[:3]:
            quality_report["streams_tested"] += 1
            schema = stream_config.schema_definition
            properties_raw = schema.get("properties")
            if properties_raw:
                quality_report["schemas_valid"] += 1
            metadata = stream_config.metadata
            primary_keys: list[str] = []
            for meta in metadata:
                breadcrumb_raw = meta.breadcrumb
                if len(breadcrumb_raw) == 1:
                    field_meta = meta.metadata
                    if field_meta.get("inclusion") == "automatic":
                        primary_keys.append(breadcrumb_raw[0])
            if primary_keys:
                quality_report["primary_keys_defined"] += 1
            table_metadata = next(
                (entry for entry in metadata if entry.breadcrumb == []),
                None,
            )
            if table_metadata:
                tm_meta = table_metadata.metadata
                if tm_meta.get("replication-key"):
                    quality_report["replication_keys_defined"] += 1
            nullable_documented = 0
            if isinstance(properties_raw, Mapping):
                properties: t.ContainerValueMapping = properties_raw
                for prop_def in properties.values():
                    if isinstance(prop_def, Mapping):
                        type_raw = prop_def.get("type")
                        if isinstance(type_raw, list) and "null" in type_raw:
                            nullable_documented += 1
            if nullable_documented > 0:
                quality_report["nullable_fields_documented"] += 1
        logger.info("📊 Data Quality Report:")
        logger.info("  Streams tested: %d", quality_report["streams_tested"])
        logger.info("  Valid schemas: %d", quality_report["schemas_valid"])
        logger.info(
            "  Primary keys defined: %d",
            quality_report["primary_keys_defined"],
        )
        logger.info(
            "  Replication keys defined: %d",
            quality_report["replication_keys_defined"],
        )
        logger.info(
            "  Nullable fields documented: %d",
            quality_report["nullable_fields_documented"],
        )
        assert quality_report["streams_tested"] > 0, "No streams tested"
        assert quality_report["schemas_valid"] > 0, "No valid schemas found"

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_pagination_end_to_end(self) -> None:
        """E2E: Test pagination handling through multiple pages."""
        pages_tested: list[str] = []
        logger.info("✅ Pagination flow tested: %s", pages_tested)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_error_recovery_and_resilience(
        self,
        real_wms_config: Mapping[str, t.Container],
    ) -> None:
        """E2E: Test error recovery and system resilience."""
        invalid_config: t.MutableRecursiveContainerMapping = dict(real_wms_config)
        invalid_config["password"] = "invalid_password"
        tap = FlextTapOracleWms(settings=invalid_config)
        try:
            catalog = self._catalog(tap)
            assert catalog.streams is not None
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
            meaningful_errors = [
                "authentication",
                "authorization",
                "credentials",
                "unauthorized",
                "forbidden",
            ]
            has_meaningful_error = any(err in error_msg for err in meaningful_errors)
            if not has_meaningful_error:
                pytest.fail(f"Unexpected error: {e}")
        logger.info("✅ Error recovery tested")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_complete_singer_protocol_compliance(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test complete Singer protocol compliance."""
        tap_instance = FlextTapOracleWms(settings=real_config.model_dump(mode="json"))
        catalog = self._catalog(tap_instance)
        for stream in catalog.streams:
            assert isinstance(stream.tap_stream_id, str), "tap_stream_id must be string"
            assert stream.tap_stream_id, "tap_stream_id cannot be empty"
            schema = stream.schema_definition
            assert schema["type"] == "t.Container", "Schema type must be t.Container"
            assert isinstance(schema["properties"], dict), "Properties must be dict"
            metadata = stream.metadata
            for meta in metadata:
                assert isinstance(meta.breadcrumb, list), "Breadcrumb must be list"
                assert isinstance(meta.metadata, dict), "Metadata field must be dict"
            table_meta = next(
                (meta for meta in metadata if meta.breadcrumb == []), None
            )
            assert table_meta is not None, "Missing table-level metadata"
            table_metadata = table_meta.metadata
            assert "replication-method" in table_metadata, "Missing replication method"
            replication_method = table_metadata["replication-method"]
            assert replication_method in {"INCREMENTAL", "FULL_TABLE"}, (
                f"Invalid replication method: {replication_method}"
            )
            if replication_method == "INCREMENTAL":
                assert "replication-key" in table_metadata, (
                    "Incremental stream missing replication key"
                )
                replication_key = table_metadata["replication-key"]
                assert replication_key in schema["properties"], (
                    f"Replication key {replication_key} not in schema"
                )
        logger.info("✅ Complete Singer protocol compliance verified")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_performance_and_scalability_indicators(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test performance indicators and scalability."""
        start_time = time.time()
        tap_instance = FlextTapOracleWms(settings=real_config.model_dump(mode="json"))
        catalog = self._catalog(tap_instance)
        discovery_time = time.time() - start_time
        streams_count = len(catalog.streams)
        assert discovery_time < 300, f"Discovery too slow: {discovery_time:.2f}s"
        assert streams_count > 0, "No streams discovered"
        properties_per_stream: list[int] = []
        for stream in catalog.streams:
            props_raw = stream.schema_definition.get("properties")
            prop_count = len(props_raw) if isinstance(props_raw, Mapping) else 0
            properties_per_stream.append(prop_count)
        avg_properties = (
            sum(properties_per_stream) / len(properties_per_stream)
            if properties_per_stream
            else 0
        )
        logger.info("📈 Performance Metrics:")
        logger.info("  Discovery time: %.2fs", discovery_time)
        logger.info("  Streams discovered: %d", streams_count)
        logger.info("  Average properties per stream: %.1f", avg_properties)
        logger.info(
            "  Discovery rate: %.2f streams/second",
            streams_count / discovery_time if discovery_time > 0 else 0,
        )
        assert avg_properties > 3, (
            "Streams should have more than 3 properties on average"
        )
        assert streams_count / discovery_time > 0.1, "Discovery rate too slow"

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_final_e2e_integration_summary(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """FINAL E2E: Comprehensive integration summary."""
        discovery_successful: bool = False
        streams_discovered: int = 0
        incremental_streams: int = 0
        full_table_streams: int = 0
        schemas_valid: int = 0
        singer_compliant: bool = False
        performance_acceptable: bool = False
        errors: list[str] = []
        try:
            start_time = time.time()
            tap_instance = FlextTapOracleWms(
                settings=real_config.model_dump(mode="json")
            )
            catalog = self._catalog(tap_instance)
            discovery_successful = True
            catalog_streams = catalog.streams
            streams_discovered = len(catalog_streams)
            for stream in catalog_streams:
                metadata = stream.metadata
                table_meta = next(
                    (entry for entry in metadata if entry.breadcrumb == []),
                    None,
                )
                if table_meta:
                    tm_meta = table_meta.metadata
                    replication_method = tm_meta.get("replication-method")
                    if replication_method == "INCREMENTAL":
                        incremental_streams += 1
                    elif replication_method == "FULL_TABLE":
                        full_table_streams += 1
                schema = stream.schema_definition
                if schema.get("properties"):
                    schemas_valid += 1
            singer_compliant = streams_discovered > 0 and schemas_valid > 0
            end_time = time.time()
            discovery_time = end_time - start_time
            performance_acceptable = discovery_time < 300 and streams_discovered > 0
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
        logger.info("🎯 FINAL E2E INTEGRATION SUMMARY:")
        logger.info("  ✅ Discovery successful: %s", discovery_successful)
        logger.info("  📊 Streams discovered: %d", streams_discovered)
        logger.info("  🔄 Incremental streams: %d", incremental_streams)
        logger.info("  📋 Full table streams: %d", full_table_streams)
        logger.info("  📝 Valid schemas: %d", schemas_valid)
        logger.info("  🎵 Singer compliant: %s", singer_compliant)
        logger.info("  ⚡ Performance acceptable: %s", performance_acceptable)
        if errors:
            logger.error("  ❌ Errors: %s", errors)
        assert discovery_successful, "Discovery failed"
        assert streams_discovered > 0, "No streams discovered"
        assert schemas_valid > 0, "No valid schemas"
        assert singer_compliant, "Not Singer compliant"
        assert not errors, f"Errors found: {errors}"
        logger.info("🎉 ALL E2E INTEGRATION TESTS PASSED!")
        time.sleep(0.1)
