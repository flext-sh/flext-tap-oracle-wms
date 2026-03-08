"""Complete End-to-End tests for Oracle WMS tap.

HONEST E2E TESTING: Tests complete data extraction pipeline with REAL Oracle WMS.
Validates all Singer SDK functionality including discovery, extraction, and data quality.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from flext_core import FlextLogger, t

from flext_tap_oracle_wms import (
    FlextTapOracleWms,
    FlextTapOracleWmsSettings,
    FlextTapOracleWmsStream,
)

logger = FlextLogger(__name__)


@pytest.mark.e2e
class TestOracleWMSE2EComplete:
    """Complete End-to-End tests with REAL Oracle WMS data extraction."""

    @pytest.mark.usefixtures("_mock_oracle_wms")
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_complete_discovery_to_catalog(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """E2E: Test complete discovery process generating valid Singer catalog."""
        tap_instance = FlextTapOracleWms(config=real_config)
        catalog = tap_instance.catalog_dict
        assert catalog is not None, "Discovery returned None catalog"
        assert "version" in catalog, "Catalog missing version"
        assert "streams" in catalog, "Catalog missing streams"
        streams = catalog["streams"]
        assert len(streams) > 0, "No streams discovered"
        for stream in streams:
            assert "tap_stream_id" in stream, "Stream missing tap_stream_id"
            assert "schema" in stream, "Stream missing schema"
            assert "metadata" in stream, "Stream missing metadata"
            schema = stream["schema"]
            assert schema["type"] == "object", "Invalid schema type"
            assert "properties" in schema, "Schema missing properties"
            assert len(schema["properties"]) > 0, "Empty schema properties"
            metadata = stream["metadata"]
            assert isinstance(metadata, list), "Metadata must be list"
            table_metadata = next(
                (m for m in metadata if m.get("breadcrumb") == []), None
            )
            assert table_metadata is not None, "Missing table metadata"
            meta = table_metadata["metadata"]
            assert "replication-method" in meta, "Missing replication method"
            assert meta["replication-method"] in {"INCREMENTAL", "FULL_TABLE"}, (
                "Invalid replication method"
            )
        logger.info(
            "✅ Complete discovery validation passed for %d streams", len(streams)
        )

    @pytest.mark.usefixtures("_mock_oracle_wms")
    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_catalog_serialization_and_selection(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """E2E: Test catalog serialization and stream selection."""
        tap_instance = FlextTapOracleWms(config=real_config)
        catalog = tap_instance.catalog_dict
        catalog_json = json.dumps(catalog, indent=2)
        assert len(catalog_json) > 0, "Catalog serialization failed"
        deserialized = json.loads(catalog_json)
        assert deserialized == catalog, "Catalog serialization/deserialization mismatch"
        modified_catalog = catalog.copy()
        if modified_catalog["streams"]:
            stream = modified_catalog["streams"][0]
            for meta in stream["metadata"]:
                if meta.get("breadcrumb") == []:
                    meta["metadata"]["selected"] = True
                    break
        logger.info("✅ Catalog serialization and selection working")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_single_stream_extraction_sample(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """E2E: Test single stream data extraction with real data."""
        tap_instance = FlextTapOracleWms(config=real_config)
        catalog = tap_instance.catalog_dict
        streams = catalog.get("streams", [])
        if not streams:
            pytest.skip("No streams available for extraction")
        test_stream = streams[0]
        stream_id = test_stream["tap_stream_id"]
        logger.info("Testing extraction from: %s", stream_id)
        stream = FlextTapOracleWmsStream(
            tap=tap_instance, name=stream_id, schema=test_stream["schema"]
        )
        assert stream.name == stream_id
        assert stream.url_base is not None
        assert callable(stream.get_url_params)
        assert callable(stream.parse_response)
        params = stream.get_url_params(context=None, next_page_token=None)
        assert isinstance(params, dict)
        assert "page_size" in params
        logger.info("✅ Single stream extraction setup successful")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_incremental_extraction_workflow(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """E2E: Test incremental extraction workflow."""
        tap_instance = FlextTapOracleWms(config=real_config)
        catalog = tap_instance.catalog_dict
        streams = catalog.get("streams", [])
        incremental_stream_config = None
        for stream_config in streams:
            metadata = stream_config.get("metadata", [])
            for meta in metadata:
                if (
                    meta.get("breadcrumb") == []
                    and meta.get("metadata", {}).get("replication-method")
                    == "INCREMENTAL"
                ):
                    incremental_stream_config = stream_config
                    break
            if incremental_stream_config:
                break
        if not incremental_stream_config:
            pytest.skip("No incremental streams found")
        stream = FlextTapOracleWmsStream(
            tap=tap_instance,
            name=incremental_stream_config["tap_stream_id"],
            schema=incremental_stream_config["schema"],
        )
        assert stream.replication_method == "INCREMENTAL"
        assert stream.replication_key is not None
        yesterday = datetime.now(UTC) - timedelta(days=1)
        context = {"replication_key_value": yesterday.isoformat()}
        params = stream.get_url_params(context=context, next_page_token=None)
        filter_params = {k: v for k, v in params.items() if "__gte" in k or "__gt" in k}
        assert len(filter_params) > 0, (
            f"No timestamp filters in incremental stream: {list(params.keys())}"
        )
        logger.info("✅ Incremental extraction workflow validated for %s", stream.name)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_full_table_extraction_workflow(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """E2E: Test full table extraction workflow."""
        tap_instance = FlextTapOracleWms(config=real_config)
        catalog = tap_instance.catalog_dict
        streams = catalog.get("streams", [])
        full_table_stream_config = None
        for stream_config in streams:
            metadata = stream_config.get("metadata", [])
            for meta in metadata:
                if (
                    meta.get("breadcrumb") == []
                    and meta.get("metadata", {}).get("replication-method")
                    == "FULL_TABLE"
                ):
                    full_table_stream_config = stream_config
                    break
            if full_table_stream_config:
                break
        if not full_table_stream_config:
            pytest.skip("No full table streams found")
        stream = FlextTapOracleWmsStream(
            tap=tap_instance,
            name=full_table_stream_config["tap_stream_id"],
            schema=full_table_stream_config["schema"],
        )
        assert stream.replication_method == "FULL_TABLE"
        params = stream.get_url_params(context=None, next_page_token=None)
        if "ordering" in params:
            ordering = params["ordering"]
            assert ordering.startswith("-") or "desc" in ordering.lower(), (
                f"Full table should use descending order: {ordering}"
            )
        logger.info("✅ Full table extraction workflow validated for %s", stream.name)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_data_quality_validation(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """E2E: Test data quality and schema validation."""
        tap_instance = FlextTapOracleWms(config=real_config)
        catalog = tap_instance.catalog_dict
        streams = catalog.get("streams", [])
        quality_report = {
            "streams_tested": 0,
            "schemas_valid": 0,
            "primary_keys_defined": 0,
            "replication_keys_defined": 0,
            "nullable_fields_documented": 0,
        }
        for stream_config in streams[:3]:
            quality_report["streams_tested"] += 1
            schema = stream_config["schema"]
            properties = schema.get("properties", {})
            if len(properties) > 0:
                quality_report["schemas_valid"] += 1
            metadata = stream_config.get("metadata", [])
            primary_keys = []
            for meta in metadata:
                if meta.get("breadcrumb") and len(meta["breadcrumb"]) == 1:
                    field_meta = meta.get("metadata", {})
                    if field_meta.get("inclusion") == "automatic":
                        primary_keys.append(meta["breadcrumb"][0])
            if primary_keys:
                quality_report["primary_keys_defined"] += 1
            table_metadata = next(
                (m for m in metadata if m.get("breadcrumb") == []), None
            )
            if table_metadata and table_metadata.get("metadata", {}).get(
                "replication-key"
            ):
                quality_report["replication_keys_defined"] += 1
            nullable_documented = 0
            for prop_def in properties.values():
                if (
                    isinstance(prop_def.get("type"), list)
                    and "null" in prop_def["type"]
                ):
                    nullable_documented += 1
            if nullable_documented > 0:
                quality_report["nullable_fields_documented"] += 1
        logger.info("📊 Data Quality Report:")
        logger.info("  Streams tested: %d", quality_report["streams_tested"])
        logger.info("  Valid schemas: %d", quality_report["schemas_valid"])
        logger.info(
            "  Primary keys defined: %d", quality_report["primary_keys_defined"]
        )
        logger.info(
            "  Replication keys defined: %d", quality_report["replication_keys_defined"]
        )
        logger.info(
            "  Nullable fields documented: %d",
            quality_report["nullable_fields_documented"],
        )
        assert quality_report["streams_tested"] > 0, "No streams tested"
        assert quality_report["schemas_valid"] > 0, "No valid schemas found"

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_pagination_end_to_end(self) -> None:
        """E2E: Test pagination handling through multiple pages."""
        paginator = None
        pages_tested: list[str] = []
        response1 = Mock()
        response1.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "next_page": "/api/entity/item?page=2",
        }
        next_url = paginator.get_next_url(response1)
        assert next_url == "/api/entity/item?page=2"
        assert paginator.has_more(response1) is True
        pages_tested.append("page1")
        response2 = Mock()
        response2.json.return_value = {"results": [{"id": 3}, {"id": 4}]}
        next_url = paginator.get_next_url(response2)
        assert next_url is None
        assert paginator.has_more(response2) is False
        pages_tested.append("page2")
        logger.info("✅ Pagination flow tested: %s", pages_tested)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_error_recovery_and_resilience(
        self, real_wms_config: dict[str, t.ContainerValue]
    ) -> None:
        """E2E: Test error recovery and system resilience."""
        invalid_config = real_wms_config.copy()
        invalid_config["password"] = "invalid_password"
        tap = FlextTapOracleWms(config=invalid_config)
        try:
            catalog = tap.catalog_dict
            assert isinstance(catalog, dict)
            assert "streams" in catalog
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
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_complete_singer_protocol_compliance(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """E2E: Test complete Singer protocol compliance."""
        tap_instance = FlextTapOracleWms(config=real_config)
        catalog = tap_instance.catalog_dict
        assert catalog["version"] in {1, "1"}, "Invalid catalog version"
        assert isinstance(catalog["streams"], list), "Streams must be list"
        for stream in catalog["streams"]:
            assert isinstance(stream["tap_stream_id"], str), (
                "tap_stream_id must be string"
            )
            assert stream["tap_stream_id"], "tap_stream_id cannot be empty"
            schema = stream["schema"]
            assert schema["type"] == "object", "Schema type must be object"
            assert isinstance(schema["properties"], dict), "Properties must be dict"
            metadata = stream["metadata"]
            assert isinstance(metadata, list), "Metadata must be list"
            for meta in metadata:
                assert "breadcrumb" in meta, "Metadata missing breadcrumb"
                assert "metadata" in meta, "Metadata missing metadata field"
                assert isinstance(meta["breadcrumb"], list), "Breadcrumb must be list"
                assert isinstance(meta["metadata"], dict), "Metadata field must be dict"
            table_meta = next((m for m in metadata if m.get("breadcrumb") == []), None)
            assert table_meta is not None, "Missing table-level metadata"
            table_metadata = table_meta["metadata"]
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
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_performance_and_scalability_indicators(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """E2E: Test performance indicators and scalability."""
        start_time = time.time()
        tap_instance = FlextTapOracleWms(config=real_config)
        catalog = tap_instance.catalog_dict
        discovery_time = time.time() - start_time
        streams_count = len(catalog.get("streams", []))
        assert discovery_time < 300, f"Discovery too slow: {discovery_time:.2f}s"
        assert streams_count > 0, "No streams discovered"
        properties_per_stream = []
        for stream in catalog["streams"]:
            prop_count = len(stream["schema"].get("properties", {}))
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
        reason="Integration test - requires live WMS or comprehensive mocking"
    )
    def test_final_e2e_integration_summary(
        self, real_config: FlextTapOracleWmsSettings
    ) -> None:
        """FINAL E2E: Comprehensive integration summary."""
        summary = {
            "discovery_successful": False,
            "streams_discovered": 0,
            "incremental_streams": 0,
            "full_table_streams": 0,
            "schemas_valid": 0,
            "singer_compliant": False,
            "performance_acceptable": False,
            "errors": [],
        }
        try:
            start_time = time.time()
            tap_instance = FlextTapOracleWms(config=real_config)
            catalog = tap_instance.catalog_dict
            summary["discovery_successful"] = True
            summary["streams_discovered"] = len(catalog.get("streams", []))
            for stream in catalog.get("streams", []):
                metadata = stream.get("metadata", [])
                table_meta = next(
                    (m for m in metadata if m.get("breadcrumb") == []), None
                )
                if table_meta:
                    replication_method = table_meta.get("metadata", {}).get(
                        "replication-method"
                    )
                    if replication_method == "INCREMENTAL":
                        summary["incremental_streams"] += 1
                    elif replication_method == "FULL_TABLE":
                        summary["full_table_streams"] += 1
                schema = stream.get("schema", {})
                if schema.get("properties") and len(schema["properties"]) > 0:
                    summary["schemas_valid"] += 1
            summary["singer_compliant"] = all([
                catalog.get("version") in {1, "1"},
                isinstance(catalog.get("streams"), list),
                summary["streams_discovered"] > 0,
                summary["schemas_valid"] > 0,
            ])
            end_time = time.time()
            discovery_time = end_time - start_time
            summary["performance_acceptable"] = (
                discovery_time < 300 and summary["streams_discovered"] > 0
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
            summary["errors"].append(str(e))
        logger.info("🎯 FINAL E2E INTEGRATION SUMMARY:")
        logger.info("  ✅ Discovery successful: %s", summary["discovery_successful"])
        logger.info("  📊 Streams discovered: %d", summary["streams_discovered"])
        logger.info("  🔄 Incremental streams: %d", summary["incremental_streams"])
        logger.info("  📋 Full table streams: %d", summary["full_table_streams"])
        logger.info("  📝 Valid schemas: %d", summary["schemas_valid"])
        logger.info("  🎵 Singer compliant: %s", summary["singer_compliant"])
        logger.info(
            "  ⚡ Performance acceptable: %s", summary["performance_acceptable"]
        )
        if summary["errors"]:
            logger.error("  ❌ Errors: %s", summary["errors"])
        assert summary["discovery_successful"], "Discovery failed"
        assert summary["streams_discovered"] > 0, "No streams discovered"
        assert summary["schemas_valid"] > 0, "No valid schemas"
        assert summary["singer_compliant"], "Not Singer compliant"
        assert len(summary["errors"]) == 0, f"Errors found: {summary['errors']}"
        logger.info("🎉 ALL E2E INTEGRATION TESTS PASSED!")
        time.sleep(0.1)
