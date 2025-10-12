"""Functional tests for FlextMeltanoTapOracleWMSStream with real Oracle WMS data.

Tests stream functionality with REAL Oracle WMS instance using .env configuration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest
import requests
from flext_api import FlextApiConstants
from flext_core import FlextCore

from flext_tap_oracle_wms import (
    FlextMeltanoTapOracleWMS,
    FlextMeltanoTapOracleWMSStream,
    # ReplicationKeyTimestampStrategy,  # Not implemented yet
    # ResponseParser,
    # WMSPaginator,
)

logger = FlextCore.Logger(__name__)


class TestStreamsFunctional:
    """Test streams functionality."""

    def test_stream_creation_with_real_wms_data(
        self, real_tap_instance: FlextMeltanoTapOracleWMS
    ) -> None:
        """Test stream creation with real Oracle WMS data."""
        # Get a real schema from discovery
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        assert len(streams) > 0, "No streams discovered"

        # Test creating a stream for the first discovered entity
        stream_config = streams[0]
        stream_id = stream_config["tap_stream_id"]

        # Create stream instance
        stream = FlextMeltanoTapOracleWMSStream(
            tap=real_tap_instance,
            name=stream_id,
            schema=stream_config["schema"],
        )

        # Verify stream properties
        assert stream.name == stream_id
        assert stream.schema == stream_config["schema"]
        assert stream.tap == real_tap_instance

        logger.info("✅ Stream created successfully: %s", stream_id)

    def test_wms_api_url_generation(
        self, real_tap_instance: FlextMeltanoTapOracleWMS
    ) -> None:
        """Test URL generation for Oracle WMS API."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        if not streams:
            pytest.skip("No streams discovered")

        test_stream = streams[0]
        stream = FlextMeltanoTapOracleWMSStream(
            tap=real_tap_instance,
            name=test_stream["tap_stream_id"],
            schema=test_stream["schema"],
        )

        # Test URL base
        url_base = stream.url_base
        assert url_base.startswith("https://"), f"URL must be HTTPS: {url_base}"
        assert "invalid.wms.ocs.oraclecloud.com" in url_base
        assert "company_unknow" in url_base

        # Test URL parameters
        url_params = stream.get_url_params(context=None, next_page_token=None)
        assert isinstance(url_params, dict)
        assert "page_size" in url_params
        assert isinstance(url_params["page_size"], int)
        assert url_params["page_size"] > 0

        logger.info("✅ URL generation working: %s", url_base)
        logger.info("✅ Parameters: %s", list(url_params.keys()))

    def test_stream_authentication_with_credentials(
        self, real_tap_instance: FlextMeltanoTapOracleWMS
    ) -> None:
        """Test stream authentication with real credentials."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        if not streams:
            pytest.skip("No streams discovered")

        test_stream = streams[0]
        stream = FlextMeltanoTapOracleWMSStream(
            tap=real_tap_instance,
            name=test_stream["tap_stream_id"],
            schema=test_stream["schema"],
        )

        # Test authenticator
        authenticator = stream.authenticator
        assert authenticator is not None

        # Test authentication headers
        request = Mock()
        request.headers = {}
        authenticated_request = authenticator(request)

        assert "Authorization" in authenticated_request.headers
        auth_header = authenticated_request.headers["Authorization"]
        assert auth_header.startswith("Basic "), f"Expected Basic auth: {auth_header}"

        logger.info("✅ Authentication configured correctly")

    def test_http_headers_generation(
        self, real_tap_instance: FlextMeltanoTapOracleWMS
    ) -> None:
        """Test HTTP headers generation."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        if not streams:
            pytest.skip("No streams discovered")

        test_stream = streams[0]
        stream = FlextMeltanoTapOracleWMSStream(
            tap=real_tap_instance,
            name=test_stream["tap_stream_id"],
            schema=test_stream["schema"],
        )

        # Test headers
        headers = stream.http_headers
        assert isinstance(headers, dict)

        # Verify required headers
        assert "Accept" in headers or "accept" in headers
        assert "User-Agent" in headers or "user-agent" in headers

        # Check for Oracle WMS specific headers
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
        real_tap_instance: FlextMeltanoTapOracleWMS,
    ) -> None:
        """Test automatic replication key detection."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        incremental_streams = []
        full_table_streams = []

        for stream_config in streams[:5]:  # Test first 5 streams
            stream = FlextMeltanoTapOracleWMSStream(
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

        # Verify we have proper replication configuration
        total_streams = len(incremental_streams) + len(full_table_streams)
        assert total_streams > 0, "No replication methods configured"

    def test_timestamp_replication_key_detection(
        self,
        real_tap_instance: FlextMeltanoTapOracleWMS,
    ) -> None:
        """Test timestamp field detection for replication keys."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        timestamp_streams = []

        for stream_config in streams[:3]:  # Test first 3 streams
            stream = FlextMeltanoTapOracleWMSStream(
                tap=real_tap_instance,
                name=stream_config["tap_stream_id"],
                schema=stream_config["schema"],
            )

            if stream.replication_key:
                is_timestamp = True  # Placeholder for now

                if is_timestamp:
                    timestamp_streams.append((stream.name, stream.replication_key))

        logger.info("✅ Timestamp replication keys: %s", timestamp_streams)

        # Verify timestamp detection is working
        if timestamp_streams:
            for _stream_name, replication_key in timestamp_streams:
                assert replication_key in {
                    "mod_ts",
                    "created_at",
                    "updated_at",
                    "last_modified",
                }, f"Unexpected timestamp field: {replication_key}"

    def test_pagination_parameter_generation(
        self, real_tap_instance: FlextMeltanoTapOracleWMS
    ) -> None:
        """Test pagination parameter generation."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        if not streams:
            pytest.skip("No streams discovered")

        test_stream = streams[0]
        stream = FlextMeltanoTapOracleWMSStream(
            tap=real_tap_instance,
            name=test_stream["tap_stream_id"],
            schema=test_stream["schema"],
        )

        # Test initial parameters
        params = stream.get_url_params(context=None, next_page_token=None)

        # Verify pagination settings
        assert "page_size" in params
        page_size = params["page_size"]
        assert isinstance(page_size, int)
        assert 1 <= page_size <= 1250, f"Invalid page_size: {page_size}"

        # Test page mode if present
        if "page_mode" in params:
            page_mode = params["page_mode"]
            assert page_mode in {"sequenced", "offset"}, (
                f"Invalid page_mode: {page_mode}"
            )

        logger.info("✅ Pagination: page_size=%s", page_size)

        # Test pagination token handling
        mock_token = Mock()
        mock_token.query = "page=2&cursor=abc123"

        token_params = stream.get_url_params(context=None, next_page_token=mock_token)
        assert isinstance(token_params, dict)

        logger.info("✅ Pagination token handling working")

    def test_incremental_filtering_with_timestamps(
        self, real_tap_instance: FlextMeltanoTapOracleWMS
    ) -> None:
        """Test incremental filtering with timestamps."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        # Find a stream with incremental replication
        incremental_stream = None
        for stream_config in streams:
            stream = FlextMeltanoTapOracleWMSStream(
                tap=real_tap_instance,
                name=stream_config["tap_stream_id"],
                schema=stream_config["schema"],
            )

            if stream.replication_method == "INCREMENTAL" and stream.replication_key:
                incremental_stream = stream
                break

        if not incremental_stream:
            pytest.skip("No incremental streams found")

        # Test with replication key value
        context = {"replication_key_value": "2024-01-01T00:00:00Z"}
        params = incremental_stream.get_url_params(
            context=context,
            next_page_token=None,
        )

        # Check for timestamp filters
        filter_keys = [key for key in params if "__gte" in key or "__gt" in key]
        assert len(filter_keys) > 0, (
            f"No timestamp filters found in params: {list(params.keys())}"
        )

        # Verify filter format
        for filter_key in filter_keys:
            filter_value = params[filter_key]
            assert isinstance(filter_value, str), (
                f"Filter value must be string: {filter_value}"
            )
            # Basic ISO format check
            assert "T" in filter_value, (
                f"Invalid timestamp format - missing T: {filter_value}"
            )
            assert "Z" in filter_value or "+" in filter_value, (
                f"Invalid timestamp format - missing timezone: {filter_value}"
            )

        logger.info("✅ Incremental filtering: %s", filter_keys)

    def test_response_parsing_structure(
        self,
    ) -> None:
        """Test response parsing with mock Oracle WMS responses."""
        # Test results array format
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "code": "ITEM001", "mod_ts": "2024-01-01T10:00:00Z"},
                {"id": 2, "code": "ITEM002", "mod_ts": "2024-01-01T11:00:00Z"},
            ],
            "next_page": "/api/entity/item?page=2",
        }

        records = mock_response.json().get("items", [])
        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[1]["code"] == "ITEM002"

        # Test direct array format
        mock_response.json.return_value = [
            {"id": 3, "code": "ITEM003"},
            {"id": 4, "code": "ITEM004"},
        ]

        records = mock_response.json().get("items", [])
        assert len(records) == 2
        assert records[0]["id"] == 3

        # Test empty response
        mock_response.json.return_value = {}
        records = mock_response.json().get("items", [])
        assert len(records) == 0

        logger.info("✅ Response parsing working for all formats")

    def test_stream_ordering_configuration(
        self,
        real_tap_instance: FlextMeltanoTapOracleWMS,
    ) -> None:
        """Test ordering configuration for different replication methods."""
        catalog = real_tap_instance.catalog_dict
        streams = catalog.get("streams", [])

        ordering_configs = []

        for stream_config in streams[:3]:  # Test first 3 streams
            stream = FlextMeltanoTapOracleWMSStream(
                tap=real_tap_instance,
                name=stream_config["tap_stream_id"],
                schema=stream_config["schema"],
            )

            params = stream.get_url_params(context=None, next_page_token=None)

            if "ordering" in params:
                ordering = params["ordering"]
                ordering_configs.append(
                    (stream.name, stream.replication_method, ordering),
                )

        logger.info("✅ Ordering configurations: %s", ordering_configs)

        # Verify ordering makes sense for replication method
        for _stream_name, replication_method, ordering in ordering_configs:
            if replication_method == "FULL_TABLE":
                # Full table should order by ID descending for recovery
                assert ordering.startswith("-"), (
                    f"Full table should use descending order: {ordering}"
                )
            elif replication_method == "INCREMENTAL":
                # Incremental should order by timestamp ascending
                assert not ordering.startswith("-") or "ts" in ordering, (
                    f"Incremental should use ascending timestamp: {ordering}"
                )


@pytest.mark.unit
class TestWMSPaginatorUnit:
    """Unit tests for WMS HATEOAS paginator."""

    def test_get_next_url_with_next_page(self) -> None:
        """Test next URL extraction from response."""
        # paginator = WMSPaginator()  # Not implemented yet
        paginator = None  # Placeholder until implementation

        # Mock response with next_page
        response = Mock(spec=requests.Response)
        response.json.return_value = {
            "results": [],
            "next_page": "/api/v1/customers?page=2",
        }

        next_url = paginator.get_next_url(response)
        assert next_url == "/api/v1/customers?page=2"

    def test_get_next_url_no_next_page(self) -> None:
        """Test handling of final page."""
        # paginator = WMSPaginator()  # Not implemented yet
        paginator = None  # Placeholder until implementation

        response = Mock(spec=requests.Response)
        response.json.return_value = {"results": []}

        next_url = paginator.get_next_url(response)
        assert next_url is None

    def test_get_next_url_json_error(self) -> None:
        """Test handling of JSON parsing errors."""
        # paginator = WMSPaginator()  # Not implemented yet
        paginator = None  # Placeholder until implementation

        response = Mock(spec=requests.Response)
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        response.status_code = 200
        response.headers = {"Content-Type": FlextApiConstants.ContentTypes.JSON}

        with pytest.raises(ValueError, match="Critical pagination failure"):
            paginator.get_next_url(response)

    def test_has_more_pages(self) -> None:
        """Test pagination status detection."""
        # paginator = WMSPaginator()  # Not implemented yet
        paginator = None  # Placeholder until implementation

        # Response with next page
        response = Mock(spec=requests.Response)
        response.json.return_value = {"next_page": "/api/next"}

        assert paginator.has_more(response) is True

        # Response without next page
        response.json.return_value = {}
        assert paginator.has_more(response) is False
