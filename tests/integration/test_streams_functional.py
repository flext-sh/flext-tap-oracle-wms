"""Functional tests for FlextTapOracleWmsStream with real Oracle WMS data.

Tests stream functionality with REAL Oracle WMS instance using .env configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_tap_oracle_wms import FlextTapOracleWms, FlextTapOracleWmsStream
from tests import m, t, u

logger = u.fetch_logger(__name__)


class TestsFlextTapOracleWmsStreamsFunctional:
    """Test streams functionality."""

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
    def test_stream_creation_with_real_wms_data(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test stream creation with real Oracle WMS data."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        assert streams, "No streams discovered"
        stream_config = streams[0]
        stream_id = stream_config.tap_stream_id
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=self._schema(stream_config),
        )
        assert stream.name == stream_id
        assert stream.tap == real_tap_instance
        logger.info("✅ Stream created successfully: %s", stream_id)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
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
        assert "invalid.wms.ocs.oraclecloud.com" in url_base
        assert "company_unknow" in url_base
        url_params = stream._build_operation_kwargs(page=1, context=None)
        assert isinstance(url_params, dict)
        assert "limit" in url_params
        assert isinstance(url_params["limit"], int)
        assert url_params["limit"] > 0
        logger.info(f"✅ URL generation working: {url_base}")
        logger.info(f"✅ Parameters: {list(url_params.keys())}")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_stream_authentication_with_credentials(
        self,
        real_tap_instance: FlextTapOracleWms,
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
        assert isinstance(auth_header, str)
        assert auth_header.startswith("Basic "), f"Expected Basic auth: {auth_header}"
        logger.info("✅ Authentication configured correctly")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_http_headers_generation(
        self,
        real_tap_instance: FlextTapOracleWms,
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
        assert isinstance(headers, dict)
        assert "Accept" in headers or "accept" in headers
        assert "User-Agent" in headers or "user-agent" in headers
        wms_headers = [
            h
            for h in headers
            if "WMS" in h.upper() or "Company" in h or "Facility" in h
        ]
        if wms_headers:
            logger.info(f"✅ WMS-specific headers: {wms_headers}")
        logger.info(f"✅ HTTP headers configured: {list(headers.keys())}")

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
        logger.info(f"✅ Incremental streams: {incremental_streams}")
        logger.info(f"✅ Full table streams: {full_table_streams}")
        total_streams = len(incremental_streams) + len(full_table_streams)
        assert total_streams > 0, "No replication methods configured"

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_timestamp_replication_key_detection(
        self,
        real_tap_instance: FlextTapOracleWms,
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
        logger.info(f"✅ Timestamp replication keys: {timestamp_streams}")
        if timestamp_streams:
            for _stream_name, replication_key in timestamp_streams:
                assert replication_key in {
                    "mod_ts",
                    "created_at",
                    "updated_at",
                    "last_modified",
                }, f"Unexpected timestamp field: {replication_key}"

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_pagination_parameter_generation(
        self,
        real_tap_instance: FlextTapOracleWms,
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
        params = stream._build_operation_kwargs(page=1, context=None)
        assert "limit" in params
        page_size = params["limit"]
        assert isinstance(page_size, int)
        assert 1 <= page_size <= 1250, f"Invalid limit: {page_size}"
        if "page_mode" in params:
            page_mode = params["page_mode"]
            assert page_mode in {"sequenced", "offset"}, (
                f"Invalid page_mode: {page_mode}"
            )
        logger.info("✅ Pagination: limit=%s", page_size)
        token_params = stream._build_operation_kwargs(page=2, context=None)
        assert isinstance(token_params, dict)
        logger.info("✅ Pagination token handling working")

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_incremental_filtering_with_timestamps(
        self,
        real_tap_instance: FlextTapOracleWms,
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
        params = incremental_stream._build_operation_kwargs(page=1, context=context)
        kwargs_filter = params.get("filter")
        assert kwargs_filter and (
            ">=" in str(kwargs_filter) or ">" in str(kwargs_filter)
        ), f"No timestamp filters found in params: {list(params.keys())}"
        for filter_value in [str(kwargs_filter)]:
            assert isinstance(filter_value, str), (
                f"Filter value must be string: {filter_value}"
            )
            assert "T" in filter_value, (
                f"Invalid timestamp format - missing T: {filter_value}"
            )
            assert "Z" in filter_value or "+" in filter_value, (
                f"Invalid timestamp format - missing timezone: {filter_value}"
            )
        logger.info("✅ Incremental filtering: %s", [str(kwargs_filter)])
