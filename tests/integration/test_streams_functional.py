"""Functional tests for FlextTapOracleWmsStream with real Oracle WMS data.

Tests stream functionality with REAL Oracle WMS instance using .env configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from flext_core import FlextLogger
from flext_tap_oracle_wms import FlextTapOracleWms, FlextTapOracleWmsStream

logger = FlextLogger(__name__)


class TestStreamsFunctional:
    """Test streams functionality."""

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_stream_creation_with_real_wms_data(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test stream creation with real Oracle WMS data."""
        catalog = real_tap_instance.catalog_dict_typed
        streams = catalog.get("streams", [])
        assert streams, "No streams discovered"
        stream_config = streams[0]
        stream_id = stream_config["tap_stream_id"]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=stream_config["schema"],
        )
        assert stream.name == stream_id
        assert stream.tap == real_tap_instance
        logger.info("✅ Stream created successfully: %s", stream_id)

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_wms_api_url_generation(self, real_tap_instance: FlextTapOracleWms) -> None:
        """Test URL generation for Oracle WMS API."""
        catalog = real_tap_instance.catalog_dict_typed
        streams = catalog.get("streams", [])
        if not streams:
            pytest.skip("No streams discovered")
        test_stream = streams[0]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=test_stream["tap_stream_id"],
            schema=test_stream["schema"],
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
        logger.info("✅ URL generation working: %s", url_base)
        logger.info("✅ Parameters: %s", list(url_params.keys()))

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_stream_authentication_with_credentials(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test stream authentication with real credentials."""
        catalog = real_tap_instance.catalog_dict_typed
        streams = catalog.get("streams", [])
        if not streams:
            pytest.skip("No streams discovered")
        test_stream = streams[0]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=test_stream["tap_stream_id"],
            schema=test_stream["schema"],
        )
        authenticator = stream.authenticator
        assert authenticator is not None
        request = Mock()
        request.headers = dict[str, str]()
        authenticated_request = authenticator(request)
        assert "Authorization" in authenticated_request.headers
        auth_header = authenticated_request.headers["Authorization"]
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
        catalog = real_tap_instance.catalog_dict_typed
        streams = catalog.get("streams", [])
        if not streams:
            pytest.skip("No streams discovered")
        test_stream = streams[0]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=test_stream["tap_stream_id"],
            schema=test_stream["schema"],
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
            logger.info("✅ WMS-specific headers: %s", wms_headers)
        logger.info("✅ HTTP headers configured: %s", list(headers.keys()))

    @pytest.mark.skip(
        reason="Integration test - requires live WMS or comprehensive mocking",
    )
    def test_replication_key_detection(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test automatic replication key detection."""
        catalog = real_tap_instance.catalog_dict_typed
        streams = catalog.get("streams", [])
        incremental_streams: list[tuple[str, str | None]] = []
        full_table_streams: list[str] = []
        for stream_config in streams[:5]:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance,
                name=stream_config["tap_stream_id"],
                schema=stream_config["schema"],
            )
            if stream.replication_method == "INCREMENTAL":
                incremental_streams.append((stream.name, stream.replication_key))
            elif stream.replication_method == "FULL_TABLE":
                full_table_streams.append(stream.name)
        logger.info("✅ Incremental streams: %s", incremental_streams)
        logger.info("✅ Full table streams: %s", full_table_streams)
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
        catalog = real_tap_instance.catalog_dict_typed
        streams = catalog.get("streams", [])
        timestamp_streams: list[tuple[str, str]] = []
        for stream_config in streams[:3]:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance,
                name=stream_config["tap_stream_id"],
                schema=stream_config["schema"],
            )
            if stream.replication_key:
                is_timestamp = True
                if is_timestamp:
                    timestamp_streams.append((stream.name, stream.replication_key))
        logger.info("✅ Timestamp replication keys: %s", timestamp_streams)
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
        catalog = real_tap_instance.catalog_dict_typed
        streams = catalog.get("streams", [])
        if not streams:
            pytest.skip("No streams discovered")
        test_stream = streams[0]
        stream = FlextTapOracleWmsStream(
            tap=real_tap_instance,
            name=test_stream["tap_stream_id"],
            schema=test_stream["schema"],
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
        catalog = real_tap_instance.catalog_dict_typed
        streams = catalog.get("streams", [])
        incremental_stream = None
        for stream_config in streams:
            stream = FlextTapOracleWmsStream(
                tap=real_tap_instance,
                name=stream_config["tap_stream_id"],
                schema=stream_config["schema"],
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
