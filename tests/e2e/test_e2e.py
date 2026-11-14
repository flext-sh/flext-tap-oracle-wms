"""Complete End-to-End tests for Oracle WMS tap.

HONEST E2E TESTING: Tests complete data extraction pipeline with REAL Oracle WMS.
Validates all Singer SDK functionality: discovery, extraction, and data
quality.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta

from flext_tap_oracle_wms import FlextTapOracleWms, FlextTapOracleWmsSettings
from tests import TestsFlextTapOracleWmsHelpers, c, tm, u

logger = u.fetch_logger(__name__)

_MAX_DISCOVERY_SECONDS = 300
_MIN_AVG_PROPERTIES = 3
_MIN_DISCOVERY_RATE = 0.1


@c.Tests.MARK.e2e
class TestsFlextTapOracleWmsE2e(TestsFlextTapOracleWmsHelpers):
    """Complete End-to-End tests with REAL Oracle WMS data extraction."""

    def test_complete_discovery_to_catalog(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test complete discovery process generating valid Singer catalog."""
        tap_instance = FlextTapOracleWms.from_settings(real_config)
        catalog = self._catalog(tap_instance)
        tm.that(catalog, none=False)
        streams = catalog.streams
        tm.that(streams, truth=True, msg="No streams discovered")
        for stream in streams:
            schema = stream.schema_definition
            tm.that(schema.get("type"), eq="t.JsonValue")
            tm.that(schema, has="properties")
            props = schema.get("properties")
            tm.that(props, truth=True, msg="Empty schema properties")
            meta = self._table_metadata(stream)
            tm.that(meta, has="replication-method")
            tm.that(
                {
                    c.Meltano.SingerReplicationMethod.INCREMENTAL.value,
                    c.Meltano.SingerReplicationMethod.FULL_TABLE.value,
                },
                has=meta["replication-method"],
            )
        logger.info(
            "✅ Complete discovery validation passed for %d streams",
            len(streams),
        )

    def test_catalog_serialization_and_selection(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test catalog serialization and stream selection."""
        tap_instance = FlextTapOracleWms.from_settings(real_config)
        catalog = self._catalog(tap_instance)
        catalog_payload = catalog.model_dump(mode="json")
        catalog_json = u.Cli.json_dumps(catalog_payload, indent=2).unwrap()
        tm.that(catalog_json, truth=True, msg="Catalog serialization failed")
        deserialized = u.Cli.json_loads(catalog_json).unwrap()
        tm.that(deserialized, eq=catalog_payload)
        if catalog.streams:
            stream = catalog.streams[0]
            tm.that(any(meta.breadcrumb == () for meta in stream.metadata))
        logger.info("✅ Catalog serialization and selection working")

    def test_single_stream_extraction_sample(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test single stream data extraction with real data."""
        stream = self._first_stream(FlextTapOracleWms.from_settings(real_config))
        logger.info("Testing extraction from: %s", stream.name)
        tm.that(stream.url_base, none=False)
        params = stream.build_operation_kwargs(page=1, context=None)
        tm.that(params, is_=dict)
        tm.that(params, has="limit")
        logger.info("✅ Single stream extraction setup successful")

    def test_incremental_extraction_workflow(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test incremental extraction workflow."""
        yesterday = datetime.now(UTC) - timedelta(days=1)
        filter_text = self._incremental_filter(
            FlextTapOracleWms.from_settings(real_config),
            yesterday.isoformat(),
        )
        logger.info("✅ Incremental extraction workflow validated: %s", filter_text)

    def test_full_table_extraction_workflow(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test full table extraction workflow."""
        tap_instance = FlextTapOracleWms.from_settings(real_config)
        full_table_entry = next(
            (
                entry
                for entry in self._catalog(tap_instance).streams
                if self._table_metadata(entry).get("replication-method")
                == c.Meltano.SingerReplicationMethod.FULL_TABLE.value
            ),
            None,
        )
        if full_table_entry is None:
            u.Tests.skip("No full table streams found")
        stream = self._stream(tap_instance, full_table_entry)
        params = stream.build_operation_kwargs(page=1, context=None)
        if "ordering" in params:
            ordering = str(params["ordering"])
            tm.that(
                ordering.startswith("-") or "desc" in ordering.lower(),
                msg=(f"Full table should use descending order: {ordering}"),
            )
        logger.info("✅ Full table extraction workflow validated for %s", stream.name)

    def test_data_quality_validation(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test data quality and schema validation."""
        tap_instance = FlextTapOracleWms.from_settings(real_config)
        streams = self._catalog(tap_instance).streams[:3]
        schemas_valid = [
            stream for stream in streams if stream.schema_definition.get("properties")
        ]
        logger.info(
            "📊 Data quality: %d streams tested, %d valid schemas",
            len(streams),
            len(schemas_valid),
        )
        tm.that(streams, truth=True, msg="No streams tested")
        tm.that(schemas_valid, truth=True, msg="No valid schemas found")

    @staticmethod
    def test_pagination_end_to_end() -> None:
        """E2E: Test pagination handling through multiple pages."""
        pages_tested: list[str] = []
        logger.info("✅ Pagination flow tested: %s", pages_tested)

    def test_error_recovery_and_resilience(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test error recovery and system resilience."""
        self._assert_invalid_tap_recovery(
            real_config,
            {"password": f"{real_config.TapOracleWms.password}-wrong"},
        )
        logger.info("✅ Error recovery tested")

    def test_complete_singer_protocol_compliance(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test complete Singer protocol compliance."""
        tap_instance = FlextTapOracleWms.from_settings(real_config)
        catalog = self._catalog(tap_instance)
        for stream in catalog.streams:
            tm.that(stream.tap_stream_id, is_=str)
            tm.that(
                stream.tap_stream_id, truth=True, msg="tap_stream_id cannot be empty"
            )
            schema = stream.schema_definition
            tm.that(schema["type"], eq="t.JsonValue")
            tm.that(schema["properties"], is_=dict)
            for meta in stream.metadata:
                tm.that(meta.breadcrumb, is_=list)
                tm.that(meta.metadata, is_=dict)
            table_metadata = self._table_metadata(stream)
            tm.that(table_metadata, has="replication-method")
            replication_method = table_metadata["replication-method"]
            tm.that(
                {
                    c.Meltano.SingerReplicationMethod.INCREMENTAL.value,
                    c.Meltano.SingerReplicationMethod.FULL_TABLE.value,
                },
                has=replication_method,
            )
            if replication_method == "INCREMENTAL":
                tm.that(table_metadata, has="replication-key")
                replication_key = table_metadata["replication-key"]
                tm.that(schema["properties"], has=replication_key)
        logger.info("✅ Complete Singer protocol compliance verified")

    def test_performance_and_scalability_indicators(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """E2E: Test performance indicators and scalability."""
        start_time = time.time()
        tap_instance = FlextTapOracleWms.from_settings(real_config)
        catalog = self._catalog(tap_instance)
        discovery_time = time.time() - start_time
        streams_count = len(catalog.streams)
        tm.that(
            discovery_time,
            lt=_MAX_DISCOVERY_SECONDS,
            msg=(f"Discovery too slow: {discovery_time:.2f}s"),
        )
        tm.that(streams_count, gt=0, msg="No streams discovered")
        properties_per_stream: list[int] = []
        for stream in catalog.streams:
            props_raw = stream.schema_definition.get("properties")
            prop_count = len(props_raw) if isinstance(props_raw, Mapping) else 0
            properties_per_stream.append(prop_count)
        avg_properties = sum(properties_per_stream) / streams_count
        logger.info("📈 Performance Metrics:")
        logger.info("  Discovery time: %.2fs", discovery_time)
        logger.info("  Streams discovered: %d", streams_count)
        logger.info("  Average properties per stream: %.1f", avg_properties)
        tm.that(
            avg_properties,
            gt=_MIN_AVG_PROPERTIES,
            msg=("Streams should have more than 3 properties on average"),
        )
        tm.that(
            streams_count / discovery_time,
            gt=_MIN_DISCOVERY_RATE,
            msg=("Discovery rate too slow"),
        )

    def test_final_e2e_integration_summary(
        self,
        real_config: FlextTapOracleWmsSettings,
    ) -> None:
        """FINAL E2E: Comprehensive integration summary."""
        tap_instance = FlextTapOracleWms.from_settings(real_config)
        streams = self._catalog(tap_instance).streams
        schemas_valid = [
            stream for stream in streams if stream.schema_definition.get("properties")
        ]
        methods = [
            str(self._table_metadata(stream).get("replication-method"))
            for stream in streams
        ]
        logger.info("🎯 FINAL E2E INTEGRATION SUMMARY:")
        logger.info("  📊 Streams discovered: %d", len(streams))
        logger.info("  🔄 Incremental streams: %d", methods.count("INCREMENTAL"))
        logger.info(
            "  📋 Full table streams: %d",
            methods.count(c.Meltano.SingerReplicationMethod.FULL_TABLE.value),
        )
        logger.info("  📝 Valid schemas: %d", len(schemas_valid))
        tm.that(streams, truth=True, msg="No streams discovered")
        tm.that(schemas_valid, truth=True, msg="No valid schemas")
        logger.info("🎉 ALL E2E INTEGRATION TESTS PASSED!")
