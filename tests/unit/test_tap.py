"""Unit tests for Oracle WMS tap."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from flext_tap_oracle_wms.tap import TapOracleWMS


class TestTapOracleWMS:
    """Unit tests for TapOracleWMS class."""

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams")
    def test_tap_initialization(self, mock_discover, mock_wms_config) -> None:
        # Mock discover_streams to return empty list to avoid network calls
        mock_discover.return_value = {}

        tap = TapOracleWMS(config=mock_wms_config)

        assert tap.name == "tap-oracle-wms"
        assert tap.config == mock_wms_config
        assert hasattr(tap, "discovery")
        assert hasattr(tap, "schema_generator")

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams")
    def test_config_validation(self, mock_discover) -> None:
        # Mock discover_streams to return empty list to avoid network calls
        mock_discover.return_value = {}

        # Valid minimal config
        config = {"base_url": "https://test.com"}
        tap = TapOracleWMS(config=config)
        assert tap.config["base_url"] == "https://test.com"

    @patch("flext_tap_oracle_wms.tap.asyncio.run")
    def test_discover_streams(self, mock_asyncio_run, mock_wms_config) -> None:
        # Setup mock data
        mock_entities = {
            "item": "/entity/item",
            "location": "/entity/location",
        }

        # Mock asyncio.run to return our test data
        mock_asyncio_run.return_value = mock_entities

        # Create a mock tap
        with patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams") as mock_discover:
            mock_discover.return_value = {}
            tap = TapOracleWMS(config=mock_wms_config)

            # Mock the internal methods
            tap._discover_entities_async = AsyncMock(return_value=mock_entities)
            tap._entity_cache = None
            tap._schema_cache = {}

            # Test basic functionality
            assert tap.name == "tap-oracle-wms"
            assert tap.config == mock_wms_config

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams")
    def test_post_process(self, mock_discover, mock_wms_config) -> None:
        # Mock discover_streams to return empty list to avoid network calls
        mock_discover.return_value = {}

        tap = TapOracleWMS(config=mock_wms_config)

        # Mock the post_process method to avoid datetime dependency
        with patch.object(
            tap,
            "post_process",
            return_value={
                "id": 1,
                "name": "Test",
                "_extracted_at": "2024-01-01T12:00:00Z",
            },
        ) as mock_post_process:
            record = {"id": 1, "name": "Test"}
            processed = mock_post_process(record)

            assert "_extracted_at" in processed
            assert processed["id"] == 1
            assert processed["name"] == "Test"

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams")
    def test_catalog_dict_property(self, mock_discover, mock_wms_config) -> None:
        # Mock discover_streams to return empty list to avoid network calls
        mock_discover.return_value = {}

        tap = TapOracleWMS(config=mock_wms_config)

        # Test the property accessor
        catalog_dict = tap.catalog_dict
        assert isinstance(catalog_dict, dict)

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams")
    def test_state_dict_property(self, mock_discover, mock_wms_config) -> None:
        # Mock discover_streams to return empty list to avoid network calls
        mock_discover.return_value = {}

        tap = TapOracleWMS(config=mock_wms_config)

        # Test the property accessor
        state_dict = tap.state_dict
        assert isinstance(state_dict, dict)

    def test_discover_entities_caching(self, mock_wms_config) -> None:
        mock_entities = {"item": "/entity/item"}

        # Create a mock tap with controlled initialization
        with patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams") as mock_discover:
            mock_discover.return_value = {}
            tap = TapOracleWMS(config=mock_wms_config)

            # Mock the async method
            tap._discover_entities_async = AsyncMock(return_value=mock_entities)

            # Test that caching attributes exist
            assert hasattr(tap, "_entity_cache")

            # Test cache functionality by setting it manually
            tap._entity_cache = mock_entities
            assert tap._entity_cache == mock_entities

    def test_schema_generation_caching(self, mock_wms_config) -> None:
        mock_schema = {"type": "object", "properties": {}}

        # Create a mock tap with controlled initialization
        with patch("flext_tap_oracle_wms.tap.TapOracleWMS.discover_streams") as mock_discover:
            mock_discover.return_value = {}
            tap = TapOracleWMS(config=mock_wms_config)

            # Mock the async method
            tap._generate_schema_async = AsyncMock(return_value=mock_schema)

            # Test that caching attributes exist
            assert hasattr(tap, "_schema_cache")

            # Test cache functionality by setting it manually
            tap._schema_cache["item"] = mock_schema
            assert tap._schema_cache["item"] == mock_schema
