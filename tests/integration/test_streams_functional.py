"""Functional tests for FlextTapOracleWmsStream with real Oracle WMS data.

Tests stream functionality with REAL Oracle WMS instance using .env configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream
from flext_tests import tm
from tests import t, u

if TYPE_CHECKING:
    from flext_tap_oracle_wms.tap import FlextTapOracleWms
    from tests import m

logger = u.fetch_logger(__name__)

_ORACLE_WMS_MAX_LIMIT = 1250


class TestsFlextTapOracleWmsStreamsFunctional:
    """Test streams functionality."""

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

    def test_stream_creation_with_real_wms_data(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test stream creation with real Oracle WMS data."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        assert streams, "No streams discovered"
        stream_config = streams[0]
        stream_id = stream_config.tap_stream_id
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance, name=stream_id, schema=self._schema(stream_config)
        )
        tm.that(stream.name, eq=stream_id)
        assert stream.tap is real_tap_instance
        logger.info("✅ Stream created successfully: %s", stream_id)

    def test_wms_api_url_generation(self, real_tap_instance: FlextTapOracleWms) -> None:
        """Test URL generation for Oracle WMS API."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams discovered")
        test_stream = streams[0]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=test_stream.tap_stream_id,
            schema=self._schema(test_stream),
        )
        url_base = stream.url_base
        assert url_base.startswith("https://"), f"URL must be HTTPS: {url_base}"
        tm.that(url_base, has="invalid.wms.ocs.oraclecloud.com")
        tm.that(url_base, has="company_unknow")
        url_params = stream.build_operation_kwargs(page=1, context=None)
        tm.that(url_params, is_=dict)
        tm.that(url_params, has="limit")
        limit_value = url_params["limit"]
        assert isinstance(limit_value, int)
        assert limit_value > 0
        logger.info("URL generation working: %s", url_base)
        logger.info(f"✅ Parameters: {list(url_params.keys())}")

    def test_stream_authentication_with_credentials(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test stream authentication with real credentials."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams discovered")
        test_stream = streams[0]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=test_stream.tap_stream_id,
            schema=self._schema(test_stream),
        )
        headers = stream.http_headers
        auth_header = headers.get("Authorization") or headers.get("authorization")
        assert auth_header is not None
        assert auth_header.startswith("Basic "), f"Expected Basic auth: {auth_header}"
        logger.info("Authentication configured correctly")

    def test_http_headers_generation(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test HTTP headers generation."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams discovered")
        test_stream = streams[0]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=test_stream.tap_stream_id,
            schema=self._schema(test_stream),
        )
        headers = stream.http_headers
        tm.that(headers, is_=dict)
        assert "Accept" in headers or "accept" in headers
        assert "User-Agent" in headers or "user-agent" in headers
        wms_headers = [
            h
            for h in headers
            if "WMS" in h.upper() or "Company" in h or "Facility" in h
        ]
        if wms_headers:
            logger.info("✅ WMS-specific headers: %s", wms_headers)
        logger.info(f"✅ HTTP headers configured: {list(headers.keys())}")

    def test_replication_key_detection(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test automatic replication key detection."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        incremental_streams: list[tuple[str, str | None]] = []
        full_table_streams: list[str] = []
        for stream_config in streams[:5]:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance,
                name=stream_config.tap_stream_id,
                schema=self._schema(stream_config),
            )
            if stream.replication_method == "INCREMENTAL":
                incremental_streams.append((stream.name, stream.replication_key))
            elif stream.replication_method == "FULL_TABLE":
                full_table_streams.append(stream.name)
        logger.info("✅ Incremental streams: %s", incremental_streams)
        logger.info("✅ Full table streams: %s", full_table_streams)
        total_streams = len(incremental_streams) + len(full_table_streams)
        assert total_streams > 0, "No replication methods configured"

    def test_timestamp_replication_key_detection(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test timestamp field detection for replication keys."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        timestamp_streams: list[tuple[str, str]] = []
        for stream_config in streams[:3]:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance,
                name=stream_config.tap_stream_id,
                schema=self._schema(stream_config),
            )
            if stream.replication_key:
                is_timestamp = True
                if is_timestamp:
                    timestamp_streams.append((stream.name, stream.replication_key))
        logger.info("✅ Timestamp replication keys: %s", timestamp_streams)
        if timestamp_streams:
            for _stream_name, replication_key in timestamp_streams:
                tm.that(
                    {"mod_ts", "created_at", "updated_at", "last_modified"},
                    has=replication_key,
                )

    def test_pagination_parameter_generation(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test pagination parameter generation."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        if not streams:
            pytest.skip("No streams discovered")
        test_stream = streams[0]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=test_stream.tap_stream_id,
            schema=self._schema(test_stream),
        )
        params = stream.build_operation_kwargs(page=1, context=None)
        tm.that(params, has="limit")
        page_size = params["limit"]
        assert isinstance(page_size, int)
        assert 1 <= page_size <= _ORACLE_WMS_MAX_LIMIT, f"Invalid limit: {page_size}"
        if "page_mode" in params:
            page_mode = params["page_mode"]
            tm.that({"sequenced", "offset"}, has=page_mode)
        logger.info("✅ Pagination: limit=%s", page_size)
        token_params = stream.build_operation_kwargs(page=2, context=None)
        tm.that(token_params, is_=dict)
        logger.info("✅ Pagination token handling working")

    def test_incremental_filtering_with_timestamps(
        self, real_tap_instance: FlextTapOracleWms
    ) -> None:
        """Test incremental filtering with timestamps."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        incremental_stream = None
        for stream_config in streams:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance,
                name=stream_config.tap_stream_id,
                schema=self._schema(stream_config),
            )
            if stream.replication_method == "INCREMENTAL" and stream.replication_key:
                incremental_stream = stream
                break
        if not incremental_stream:
            pytest.skip("No incremental streams found")
        context = {"replication_key_value": "2024-01-01T00:00:00Z"}
        params = incremental_stream.build_operation_kwargs(page=1, context=context)
        kwargs_filter = params.get("filter")
        assert kwargs_filter, f"No filter found in params: {list(params.keys())}"
        assert ">=" in str(kwargs_filter) or ">" in str(kwargs_filter), (
            f"No timestamp filters found in params: {list(params.keys())}"
        )
        for filter_value in [str(kwargs_filter)]:
            tm.that(filter_value, is_=str)
            tm.that(filter_value, has="T")
            assert "Z" in filter_value or "+" in filter_value, (
                f"Invalid timestamp format - missing timezone: {filter_value}"
            )
        logger.info("✅ Incremental filtering: %s", [str(kwargs_filter)])
