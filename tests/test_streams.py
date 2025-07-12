"""Unit tests for WMSStream."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

import requests

import pytest
from flext_tap_oracle_wms.streams import WMSPaginator, WMSStream


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
        assert next_url == "/api/v1/customers?page=2"

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

        with pytest.raises(Exception) as exc_info:
            paginator.get_next_url(response)
        assert "Pagination JSON parsing failed" in str(exc_info.value)

    def test_has_more(self) -> None:
        paginator = WMSPaginator()

        # With next page
        response = Mock(spec=requests.Response)
        response.json.return_value = {"next_page": "/api/v1/customers?page=2"}
        assert paginator.has_more(response) is True

        # Without next page
        response.json.return_value = {"results": []}
        assert paginator.has_more(response) is False


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
    def mock_tap(self, minimal_config) -> Mock:
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

    def test_stream_initialization(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        assert stream._entity_name == "customer"
        assert stream._schema == basic_schema
        assert stream.primary_keys == ["id"]
        # Since mod_ts is in schema properties, should be INCREMENTAL
        assert stream.replication_method == "INCREMENTAL"
        assert stream.replication_key == "mod_ts"

    def test_stream_force_full_table(self, mock_tap, basic_schema) -> None:
        mock_tap.config["force_full_table"] = True

        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        assert stream.replication_method == "FULL_TABLE"
        assert stream.replication_key == "id"

    def test_url_base_property(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        assert stream.url_base == "https://wms.example.com"

        # Test with trailing slash
        mock_tap.config["base_url"] = "https://wms.example.com/"
        assert stream.url_base == "https://wms.example.com"

    def test_path_property(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Default path
        assert stream.path == "/customer"

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
        assert stream_with_prefix.path == "/api/v1/customer"

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
        assert stream_with_pattern.path == "/api/v1/entities/customer/data"

    def test_http_headers(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        headers = stream.http_headers

        assert headers["Content-Type"] == "application/json"
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
        assert headers_with_custom["X-API-Key"] == "secret"

    def test_get_url_params_initial_request(self, mock_tap, basic_schema) -> None:
        # Mock state properly for Singer SDK
        mock_tap.load_state = Mock(return_value={})
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Override tap_state property to return proper state
        stream._tap = mock_tap
        stream._tap_state = {"bookmarks": {}}

        params = stream.get_url_params(None, None)

        assert params["page_size"] == 100
        assert params["page_mode"] == "sequenced"
        assert params["ordering"] == "mod_ts"
        assert "mod_ts__gte" in params  # Should have timestamp filter

    def test_get_url_params_pagination(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Mock pagination token
        token = Mock()
        token.query = "page=2&limit=100"

        params = stream.get_url_params(None, token)

        assert params["page"] == "2"
        assert params["limit"] == "100"

    def test_parse_response_with_results(self, mock_tap, basic_schema) -> None:
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

        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[1]["id"] == 2

    def test_parse_response_direct_array(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        response = Mock(spec=requests.Response)
        response.json.return_value = [
            {"id": 1, "name": "Customer 1"},
            {"id": 2, "name": "Customer 2"},
        ]

        records = list(stream.parse_response(response))

        assert len(records) == 2
        assert records[0]["id"] == 1

    def test_parse_response_invalid_json(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        response = Mock(spec=requests.Response)
        response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)

        with pytest.raises(Exception) as exc_info:
            list(stream.parse_response(response))
        assert "Invalid JSON response" in str(exc_info.value)

    def test_validate_response_success(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        response = Mock(spec=requests.Response)
        response.status_code = 200

        # Should not raise
        stream.validate_response(response)

    def test_validate_response_errors(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # 401 Unauthorized
        response = Mock(spec=requests.Response)
        response.status_code = 401
        with pytest.raises(Exception) as exc_info:
            stream.validate_response(response)
        assert "Authentication failed" in str(exc_info.value)

        # 404 Not Found
        response.status_code = 404
        with pytest.raises(Exception) as exc_info:
            stream.validate_response(response)
        assert "not found" in str(exc_info.value)

        # 429 Rate Limited
        response.status_code = 429
        response.headers = {"Retry-After": "60"}
        with pytest.raises(Exception) as exc_info:
            stream.validate_response(response)
        assert "Rate limit" in str(exc_info.value)

    @patch("flext_tap_oracle_wms.streams.SchemaGenerator")
    def test_post_process_with_flattening(self,
        mock_schema_gen_class,
        mock_tap,
        basic_schema,
    ) -> None:
        mock_tap.config["flattening_enabled"] = True
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Mock schema generator
        mock_gen = Mock()
        mock_gen.flatten_complex_objects.return_value = {
            "id": 1,
            "name": "Test",
            "address_street": "123 Main St",
        }
        mock_schema_gen_class.return_value = mock_gen

        row = {"id": 1, "name": "Test", "address": {"street": "123 Main St"}}
        processed = stream.post_process(row, None)

        assert processed is not None
        assert "_sdc_extracted_at" in processed
        assert "_sdc_entity" in processed
        assert processed["_sdc_entity"] == "customer"
        assert "address_street" in processed

    def test_post_process_without_flattening(self, mock_tap, basic_schema) -> None:
        mock_tap.config["flattening_enabled"] = False
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        row = {"id": 1, "name": "Test", "address": {"street": "123 Main St"}}
        processed = stream.post_process(row, None)

        assert processed is not None
        assert "_sdc_extracted_at" in processed
        assert "address" in processed  # Not flattened
        # Complex objects are converted to JSON strings without flattening
        assert isinstance(processed["address"], str)
        assert "123 Main St" in processed["address"]

    def test_get_starting_timestamp_from_state(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # Mock state
        with patch.object(
            stream,
            "get_starting_replication_key_value",
        ) as mock_get_state:
            mock_get_state.return_value = "2024-01-01T00:00:00Z"

            timestamp = stream.get_starting_timestamp(None)

            assert timestamp is not None
            assert timestamp.year == 2024
            assert timestamp.month == 1
            assert timestamp.day == 1

    def test_get_starting_timestamp_from_config(self, mock_tap, basic_schema) -> None:
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
            assert timestamp.month == 2

    def test_normalize_timestamp(self, mock_tap, basic_schema) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        # String without timezone
        normalized = stream._normalize_timestamp("2024-01-01T12:00:00")
        assert normalized.endswith(("+00:00", "Z"))

        # String with Z
        normalized = stream._normalize_timestamp("2024-01-01T12:00:00Z")
        assert "2024-01-01" in normalized

        # Datetime object
        dt = datetime(2024, 1, 1, 12, 0, 0)
        normalized = stream._normalize_timestamp(dt)
        assert normalized.endswith("+00:00")

        # None
        assert stream._normalize_timestamp(None) is None

    @patch("flext_tap_oracle_wms.streams.get_wms_authenticator")
    def test_authenticator_property(self,
        mock_get_auth,
        mock_tap,
        basic_schema,
    ) -> None:
        stream = WMSStream(tap=mock_tap, name="customer", schema=basic_schema)

        mock_auth = Mock()
        mock_get_auth.return_value = mock_auth

        auth = stream.authenticator

        assert auth == mock_auth
        mock_get_auth.assert_called_once_with(stream, mock_tap.config)


if __name__ == "__main__":
            pytest.main([__file__, "-v"])
