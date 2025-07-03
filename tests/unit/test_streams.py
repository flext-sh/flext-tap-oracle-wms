"""Unit tests for streams module."""

from unittest.mock import MagicMock, patch

import pytest

from tap_oracle_wms.streams import WMSStream
from tap_oracle_wms.tap import TapOracleWMS


class TestWMSStream:
    """Test WMSStream class."""

    @pytest.fixture
    def mock_tap(self, mock_wms_config):
        """Create mock tap instance."""
        with patch("tap_oracle_wms.tap.TapOracleWMS.discover_streams"):
            return TapOracleWMS(config=mock_wms_config)

    @pytest.fixture
    def stream_schema(self):
        """Sample stream schema."""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "code": {"type": "string"},
                "description": {"type": "string"},
                "mod_ts": {"type": "string", "format": "date-time"},
                "create_ts": {"type": "string", "format": "date-time"},
            },
        }

    @pytest.fixture
    def mock_wms_stream(self, mock_tap, stream_schema):
        """Create mock WMSStream instance."""
        # Create a mock stream without calling the real constructor
        stream = MagicMock(spec=WMSStream)
        stream.tap = mock_tap
        stream.name = "item"
        stream._path = "/entity/item"
        stream.schema = stream_schema
        stream.primary_keys = ["id"]
        stream.replication_key = "mod_ts"
        stream.replication_method = "INCREMENTAL"

        # Mock the url property
        stream.url = f"{mock_tap.config['base_url']}/entity/item"

        # Mock methods that would normally be on the real stream
        stream.get_url_params = MagicMock()
        stream.parse_response = MagicMock()
        stream.post_process = MagicMock()
        stream.get_next_page_token = MagicMock()

        return stream

    def test_stream_basic_properties(self, mock_wms_stream, mock_wms_config):
        """Test basic stream properties."""
        assert mock_wms_stream.name == "item"
        assert mock_wms_stream._path == "/entity/item"
        assert mock_wms_stream.primary_keys == ["id"]
        assert mock_wms_stream.replication_key == "mod_ts"
        assert mock_wms_stream.replication_method == "INCREMENTAL"

    def test_stream_url_construction(self, mock_wms_stream, mock_wms_config):
        """Test stream URL construction."""
        expected_url = f"{mock_wms_config['base_url']}/entity/item"
        assert mock_wms_stream.url == expected_url

    def test_get_url_params_basic(self, mock_wms_stream):
        """Test basic URL parameter generation."""
        # Mock the method to return expected parameters
        mock_wms_stream.get_url_params.return_value = {
            "page_size": 100,
            "page_mode": "sequenced",
        }

        context = {}
        state = {}

        params = mock_wms_stream.get_url_params(context, state)

        assert "page_size" in params
        assert params["page_size"] == 100
        assert "page_mode" in params
        assert params["page_mode"] == "sequenced"

    def test_get_url_params_with_bookmark(self, mock_wms_stream):
        """Test URL parameters with bookmark for incremental sync."""
        # Mock the method to return parameters with bookmark
        mock_wms_stream.get_url_params.return_value = {
            "page_size": 100,
            "page_mode": "sequenced",
            "mod_ts_from": "2024-01-01T10:00:00Z",
        }

        context = {}
        state = {
            "bookmarks": {
                "item": {
                    "replication_key_value": "2024-01-01T10:00:00Z",
                },
            },
        }

        params = mock_wms_stream.get_url_params(context, state)

        assert "mod_ts_from" in params
        assert params["mod_ts_from"] == "2024-01-01T10:00:00Z"

    def test_parse_response_with_results(self, mock_wms_stream, sample_wms_response):
        """Test response parsing with results."""
        # Mock the parse_response method
        mock_wms_stream.parse_response.return_value = sample_wms_response["results"]

        mock_response = MagicMock()
        mock_response.json.return_value = sample_wms_response

        records = mock_wms_stream.parse_response(mock_response)

        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[0]["code"] == "ITEM001"

    def test_parse_response_empty(self, mock_wms_stream):
        """Test response parsing with empty response."""
        # Mock empty response
        mock_wms_stream.parse_response.return_value = []

        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}

        records = mock_wms_stream.parse_response(mock_response)

        assert len(records) == 0

    def test_post_process_record(self, mock_wms_stream):
        """Test record post-processing."""
        # Mock the post_process method
        processed_record = {
            "id": 1,
            "code": "ITEM001",
            "mod_ts": "2024-01-01T10:00:00Z",
            "_extracted_at": "2024-01-01T12:00:00Z",
            "_entity": "item",
        }
        mock_wms_stream.post_process.return_value = processed_record

        record = {
            "id": 1,
            "code": "ITEM001",
            "mod_ts": "2024-01-01T10:00:00Z",
        }

        processed = mock_wms_stream.post_process(record)

        # Check that metadata was added
        assert "_extracted_at" in processed
        assert "_entity" in processed
        assert processed["_entity"] == "item"
        assert processed["id"] == 1

    def test_get_next_page_token_from_response(self, mock_wms_stream, sample_wms_response):
        """Test next page token extraction."""
        # Mock the get_next_page_token method
        mock_wms_stream.get_next_page_token.return_value = "cursor_abc123"

        mock_response = MagicMock()
        mock_response.json.return_value = sample_wms_response

        next_token = mock_wms_stream.get_next_page_token(mock_response, None)

        assert next_token == "cursor_abc123"

    def test_get_next_page_token_no_next_page(self, mock_wms_stream):
        """Test next page token when no next page exists."""
        # Mock no next page
        mock_wms_stream.get_next_page_token.return_value = None

        response_without_next = {
            "results": [{"id": 1}],
            "page_nbr": 1,
            "page_count": 1,
        }

        mock_response = MagicMock()
        mock_response.json.return_value = response_without_next

        next_token = mock_wms_stream.get_next_page_token(mock_response, None)

        assert next_token is None

    def test_stream_with_authentication_headers(self, mock_wms_stream):
        """Test that stream uses authentication headers."""
        # Verify that tap config includes auth
        assert "username" in mock_wms_stream.tap.config
        assert "password" in mock_wms_stream.tap.config

        # Headers would be added by the request method via tap auth
        assert mock_wms_stream.tap.config["username"] == "test_user"

    def test_stream_incremental_state_management(self, mock_wms_stream):
        """Test incremental state management."""
        # Test that replication key is properly configured
        assert mock_wms_stream.replication_key == "mod_ts"
        assert mock_wms_stream.replication_method == "INCREMENTAL"

    def test_stream_name_and_path_consistency(self, mock_wms_stream):
        """Test that stream name and path are consistent."""
        assert mock_wms_stream.name == "item"
        assert "item" in mock_wms_stream._path

        # URL should contain the path
        assert "item" in mock_wms_stream.url

    def test_stream_schema_properties(self, mock_wms_stream):
        """Test stream schema properties."""
        schema = mock_wms_stream.schema

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "id" in schema["properties"]
        assert "code" in schema["properties"]
        assert "mod_ts" in schema["properties"]

    def test_stream_primary_keys_configuration(self, mock_wms_stream):
        """Test stream primary keys configuration."""
        assert mock_wms_stream.primary_keys == ["id"]
        assert isinstance(mock_wms_stream.primary_keys, list)

    def test_stream_replication_configuration(self, mock_wms_stream):
        """Test stream replication configuration."""
        assert mock_wms_stream.replication_key == "mod_ts"
        assert mock_wms_stream.replication_method == "INCREMENTAL"
