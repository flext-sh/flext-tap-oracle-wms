"""Unit tests for WMSStream."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import json
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests

from flext_tap_oracle_wms.streams import WMSPaginator, WMSStream


# Constants
EXPECTED_BULK_SIZE = 2

class TestWMSPaginator:
    """Test WMS HATEOAS paginator."""

    def test_get_next_url_with_next_page(self) -> None:
        paginator = WMSPaginator()

        # Mock response with next_page
        response = Mock(spec=requests.Response)
        response.json.return_value = {
            "results": [],
            "next_page": "/api/v1/customers?page=2",
        }

        next_url = paginator.get_next_url(response)
        if next_url != "/api/v1/customers?page=2":
            raise AssertionError(f"Expected {"/api/v1/customers?page=2"}, got {next_url}")

    def test_get_next_url_no_next_page(self) -> None:
        paginator = WMSPaginator()

        response = Mock(spec=requests.Response)
        response.json.return_value = {"results": []}

        next_url = paginator.get_next_url(response)
        assert next_url is None

    def test_get_next_url_json_error(self) -> None:
        paginator = WMSPaginator()

        response = Mock(spec=requests.Response)
        response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        response.status_code = 200
        response.headers = {"Content-Type": "application/json"}

        with pytest.raises(ValueError, match="Critical pagination failure"):
            paginator.get_next_url(response)

    def test_has_more(self) -> None:
        paginator = WMSPaginator()

        # With next page
        response = Mock(spec=requests.Response)
        response.json.return_value = {"next_page": "/api/v1/customers?page=2"}
        if not (paginator.has_more(response)):
            raise AssertionError(f"Expected True, got {paginator.has_more(response)}")

        # Without next page
        response.json.return_value = {"results": []}
        if paginator.has_more(response):
            raise AssertionError(f"Expected False, got {paginator.has_more(response)}")\ n

class TestWMSStream:
    """Test WMS stream functionality."""

    @pytest.fixture
    def minimal_config(self) -> dict[str, Any]:
        return {
            "base_url": "https://wms.example.com",
            "username": "test",
            "password": "pass",
            "page_size": 100,
        }

    @pytest.fixture
    def mock_tap(self, minimal_config: dict[str, Any]) -> Mock:
        tap = Mock()
        tap.config = minimal_config
        tap.logger = Mock()
        # Mock Singer SDK state management
        tap.load_state = Mock(return_value={"bookmarks": {}})
        tap.tap_state = {"bookmarks": {}}
        return tap

    @pytest.fixture
    def basic_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "mod_ts": {"type": "string", "format": "date-time"},
            },
        }

    def test_stream_initialization(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        if stream._entity_name != "customer":

            raise AssertionError(f"Expected {"customer"}, got {stream._entity_name}")
        assert stream._schema == basic_schema
        if stream.primary_keys != ["id"]:
            raise AssertionError(f"Expected {["id"]}, got {stream.primary_keys}")
        # Since mod_ts is in schema properties, should be INCREMENTAL
        if stream.replication_method != "INCREMENTAL":
            raise AssertionError(f"Expected {"INCREMENTAL"}, got {stream.replication_method}")
        assert stream.replication_key == "mod_ts"

    def test_stream_force_full_table(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        mock_tap.config["force_full_table"] = True

        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        if stream.replication_method != "FULL_TABLE":

            raise AssertionError(f"Expected {"FULL_TABLE"}, got {stream.replication_method}")
        assert stream.replication_key is None  # FULL_TABLE doesn't use replication keys

    def test_url_base_property(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        if stream.url_base != "https://wms.example.com":

            raise AssertionError(f"Expected {"https://wms.example.com"}, got {stream.url_base}")

        # Test with trailing slash
        mock_tap.config["base_url"] = "https://wms.example.com/"
        if stream.url_base != "https://wms.example.com":
            raise AssertionError(f"Expected {"https://wms.example.com"}, got {stream.url_base}")

    def test_path_property(self, mock_tap: Mock, basic_schema: dict[str, Any]) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Oracle WMS path pattern
        if stream.path != "//wms/lgfapi/v10/entity/customer":
            raise AssertionError(f"Expected {"//wms/lgfapi/v10/entity/customer"}, got {stream.path}")

        # With prefix - create new tap with updated config
        mock_tap_with_prefix = Mock()
        mock_tap_with_prefix.config = {
            **mock_tap.config,
            "api_endpoint_prefix": "api/v1",
        }
        stream_with_prefix = WMSStream(
            tap=mock_tap_with_prefix,
            name="customer",
            schema=basic_schema,
        )
        # The path is generated using WMS patterns, not a simple prefix
        if "customer" not in stream_with_prefix.path:
            raise AssertionError(f"Expected {"customer"} in {stream_with_prefix.path}")

        # With custom pattern - create new tap with updated config
        mock_tap_with_pattern = Mock()
        mock_tap_with_pattern.config = {
            **mock_tap.config,
            "api_endpoint_prefix": "api/v1",
            "path_pattern": "/entities/{entity}/data",
        }
        stream_with_pattern = WMSStream(
            tap=mock_tap_with_pattern,
            name="customer",
            schema=basic_schema,
        )
        # The path is generated using WMS patterns from ConfigMapper
        if "customer" not in stream_with_pattern.path:
            raise AssertionError(f"Expected {"customer"} in {stream_with_pattern.path}")

    def test_http_headers(self, mock_tap: Mock, basic_schema: dict[str, Any]) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        headers = stream.http_headers

        if headers["Content-Type"] != "application/json":

            raise AssertionError(f"Expected {"application/json"}, got {headers["Content-Type"]}")
        assert headers["Accept"] == "application/json"

        # With custom headers - create new tap with updated config
        mock_tap_with_headers = Mock()
        mock_tap_with_headers.config = {
            **mock_tap.config,
            "custom_headers": {"X-API-Key": "secret"},
        }
        stream_with_headers = WMSStream(
            tap=mock_tap_with_headers,
            name="customer",
            schema=basic_schema,
        )
        headers_with_custom = stream_with_headers.http_headers
        if headers_with_custom["X-API-Key"] != "secret":
            raise AssertionError(f"Expected {"secret"}, got {headers_with_custom["X-API-Key"]}")

    def test_get_url_params_initial_request(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        # Mock state properly for Singer SDK
        mock_tap.load_state = Mock(return_value={})
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Override tap_state property to return proper state
        stream._tap = mock_tap
        stream._tap_state = {"bookmarks": {}}

        params = stream.get_url_params(None, None)

        if params["page_size"] != 100:

            raise AssertionError(f"Expected {100}, got {params["page_size"]}")
        assert params["page_mode"] == "sequenced"
        if params["ordering"] != "mod_ts":
            raise AssertionError(f"Expected {"mod_ts"}, got {params["ordering"]}")
        if "mod_ts__gte" not in params  # Should have timestamp filter:
            raise AssertionError(f"Expected {"mod_ts__gte"} in {params  # Should have timestamp filter}")

    def test_get_url_params_pagination(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Mock pagination token
        token = Mock()
        token.query = "page=2&limit=100"

        params = stream.get_url_params(None, token)

        if params["page"] != "2":

            raise AssertionError(f"Expected {"2"}, got {params["page"]}")
        assert params["limit"] == "100"

    def test_parse_response_with_results(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        response = Mock(spec=requests.Response)
        response.json.return_value = {
            "results": [
                {"id": 1, "name": "Customer 1"},
                {"id": 2, "name": "Customer 2"},
            ],
            "next_page": "/api/v1/customers?page=2",
        }

        records = list(stream.parse_response(response))

        if len(records) != EXPECTED_BULK_SIZE:

            raise AssertionError(f"Expected {2}, got {len(records)}")
        assert records[0]["id"] == 1
        if records[1]["id"] != EXPECTED_BULK_SIZE:
            raise AssertionError(f"Expected {2}, got {records[1]["id"]}")

    def test_parse_response_direct_array(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        response = Mock(spec=requests.Response)
        response.json.return_value = [
            {"id": 1, "name": "Customer 1"},
            {"id": 2, "name": "Customer 2"},
        ]

        records = list(stream.parse_response(response))

        if len(records) != EXPECTED_BULK_SIZE:

            raise AssertionError(f"Expected {2}, got {len(records)}")
        assert records[0]["id"] == 1

    def test_parse_response_invalid_json(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        response = Mock(spec=requests.Response)
        response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)

        with pytest.raises(ValueError, match="Invalid JSON response from API"):
            list(stream.parse_response(response))

    def test_validate_response_success(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        response = Mock(spec=requests.Response)
        response.status_code = 200

        # Should not raise
        stream.validate_response(response)

    def test_validate_response_errors(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # 401 Unauthorized
        response = Mock(spec=requests.Response)
        response.status_code = 401
        with pytest.raises(ValueError, match="Unauthorized access to Oracle WMS API"):
            stream.validate_response(response)

        # 404 Not Found
        response.status_code = 404
        with pytest.raises(ValueError, match="Resource not found in Oracle WMS API"):
            stream.validate_response(response)

        # 429 Rate Limited
        response.status_code = 429
        response.headers = {"Retry-After": "60"}
        with pytest.raises(ValueError, match="Too many requests to Oracle WMS API"):
            stream.validate_response(response)

    def test_get_starting_timestamp_from_state(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Mock state
        with patch.object(
            stream,
            "get_starting_replication_key_value",
        ) as mock_get_state:
            mock_get_state.return_value = "2024-01-01T00:00:00Z"

            timestamp = stream.get_starting_timestamp(None)

            assert timestamp is not None
            if timestamp.year != 2024:
                raise AssertionError(f"Expected {2024}, got {timestamp.year}")
            assert timestamp.month == 1
            if timestamp.day != 1:
                raise AssertionError(f"Expected {1}, got {timestamp.day}")

    def test_get_starting_timestamp_from_config(
        self,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        mock_tap.config["start_date"] = "2024-02-01T00:00:00Z"
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Mock no state
        with patch.object(
            stream,
            "get_starting_replication_key_value",
        ) as mock_get_state:
            mock_get_state.return_value = None

            timestamp = stream.get_starting_timestamp(None)

            assert timestamp is not None
            if timestamp.month != EXPECTED_BULK_SIZE:
                raise AssertionError(f"Expected {2}, got {timestamp.month}")

    @patch("flext_tap_oracle_wms.streams.get_wms_authenticator")
    def test_authenticator_property(
        self,
        mock_get_auth: Mock,
        mock_tap: Mock,
        basic_schema: dict[str, Any],
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        mock_auth = Mock()
        mock_get_auth.return_value = mock_auth

        auth = stream.authenticator

        if auth != mock_auth:

            raise AssertionError(f"Expected {mock_auth}, got {auth}")
        mock_get_auth.assert_called_once_with(stream, mock_tap.config)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
