"""Functional tests for FlextTapOracleWmsStreams.WmsStream with real Oracle WMS data.

Tests stream functionality with REAL Oracle WMS instance using .env configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_tap_oracle_wms import FlextTapOracleWmsStreams
from tests import TestsFlextTapOracleWmsHelpersMixin, tm, u

if TYPE_CHECKING:
    from flext_tap_oracle_wms import FlextTapOracleWms

logger = u.fetch_logger(__name__)

_ORACLE_WMS_MAX_LIMIT = 1250


class TestsFlextTapOracleWmsStreamsFunctional(TestsFlextTapOracleWmsHelpersMixin):
    """Test streams functionality."""

    def test_stream_creation_with_real_wms_data(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test stream creation with real Oracle WMS data."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        tm.that(streams, truth=True, msg="No streams discovered")
        stream_config = streams[0]
        stream_id = stream_config.tap_stream_id
        stream = FlextTapOracleWmsStreams.WmsStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=self._schema(stream_config),
        )
        tm.that(stream.name, eq=stream_id)
        tm.that(stream.tap is real_tap_instance)
        logger.info("✅ Stream created successfully: %s", stream_id)

    def test_wms_api_url_generation(self, real_tap_instance: FlextTapOracleWms) -> None:
        """Test URL generation for Oracle WMS API."""
        stream = self._first_stream(real_tap_instance)
        url_base = stream.url_base
        tm.that(url_base.startswith("https://"), msg=f"URL must be HTTPS: {url_base}")
        tm.that(url_base, has="invalid.wms.ocs.oraclecloud.com")
        tm.that(url_base, has="company_unknow")
        url_params = stream.build_operation_kwargs(page=1, context=None)
        tm.that(url_params, is_=dict)
        tm.that(url_params, has="limit")
        limit_value = url_params["limit"]
        tm.that(limit_value, is_=int)
        tm.that(limit_value, gt=0)
        logger.info("URL generation working: %s", url_base)
        logger.info("✅ Parameters: %s", list(url_params.keys()))

    def test_stream_authentication_with_credentials(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test stream authentication with real credentials."""
        stream = self._first_stream(real_tap_instance)
        headers = stream.http_headers
        auth_header = tm.not_none(
            headers.get("Authorization") or headers.get("authorization"),
        )
        tm.that(
            auth_header.startswith("Basic "), msg=f"Expected Basic auth: {auth_header}"
        )
        logger.info("Authentication configured correctly")

    def test_http_headers_generation(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test HTTP headers generation."""
        stream = self._first_stream(real_tap_instance)
        headers = stream.http_headers
        tm.that(headers, is_=dict)
        tm.that("Accept" in headers or "accept" in headers)
        tm.that("User-Agent" in headers or "user-agent" in headers)
        wms_headers = [
            h
            for h in headers
            if "WMS" in h.upper() or "Company" in h or "Facility" in h
        ]
        if wms_headers:
            logger.info("✅ WMS-specific headers: %s", wms_headers)
        logger.info("✅ HTTP headers configured: %s", list(headers.keys()))

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
            stream = FlextTapOracleWmsStreams.WmsStream(
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
        tm.that(total_streams, gt=0, msg="No replication methods configured")

    def test_timestamp_replication_key_detection(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test timestamp field detection for replication keys."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        timestamp_streams: list[tuple[str, str]] = []
        for stream_config in streams[:3]:
            stream = FlextTapOracleWmsStreams.WmsStream(
                tap=real_tap_instance,
                name=stream_config.tap_stream_id,
                schema=self._schema(stream_config),
            )
            if stream.replication_key:
                timestamp_streams.append((stream.name, stream.replication_key))
        logger.info("✅ Timestamp replication keys: %s", timestamp_streams)
        if timestamp_streams:
            for _stream_name, replication_key in timestamp_streams:
                tm.that(
                    {"mod_ts", "created_at", "updated_at", "last_modified"},
                    has=replication_key,
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
        stream = FlextTapOracleWmsStreams.WmsStream(
            tap=real_tap_instance,
            name=test_stream.tap_stream_id,
            schema=self._schema(test_stream),
        )
        params = stream.build_operation_kwargs(page=1, context=None)
        tm.that(params, has="limit")
        page_size = params["limit"]
        tm.that(page_size, is_=int)
        tm.that(
            page_size,
            gte=1,
            lte=_ORACLE_WMS_MAX_LIMIT,
            msg=f"Invalid limit: {page_size}",
        )
        if "page_mode" in params:
            page_mode = params["page_mode"]
            tm.that({"sequenced", "offset"}, has=page_mode)
        logger.info("✅ Pagination: limit=%s", page_size)
        token_params = stream.build_operation_kwargs(page=2, context=None)
        tm.that(token_params, is_=dict)
        logger.info("✅ Pagination token handling working")

    def test_incremental_filtering_with_timestamps(
        self,
        real_tap_instance: FlextTapOracleWms,
    ) -> None:
        """Test incremental filtering with timestamps."""
        catalog = self._catalog(real_tap_instance)
        streams = catalog.streams
        incremental_stream = None
        for stream_config in streams:
            stream = FlextTapOracleWmsStreams.WmsStream(
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
        tm.that(
            kwargs_filter,
            truth=True,
            msg=f"No filter found in params: {list(params.keys())}",
        )
        tm.that(
            ">=" in str(kwargs_filter) or ">" in str(kwargs_filter),
            msg=(f"No timestamp filters found in params: {list(params.keys())}"),
        )
        filter_text = str(kwargs_filter)
        tm.that(filter_text, has="T")
        tm.that(
            "Z" in filter_text or "+" in filter_text,
            msg=(f"Invalid timestamp format - missing timezone: {filter_text}"),
        )
        logger.info("✅ Incremental filtering: %s", filter_text)
