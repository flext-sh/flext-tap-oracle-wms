"""Unit tests for TapOracleWMS."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from tap_oracle_wms.streams import WMSStream
from tap_oracle_wms.tap import TapOracleWMS


class TestTapOracleWMS:
    """Test Oracle WMS Tap functionality."""

    @pytest.fixture
    def minimal_config(self):
        """Minimal valid configuration."""
        return {
            "base_url": "https://wms.example.com",
            "username": "test_user",
            "password": "test_pass",
            "wms_api_version": "v10",
        }

    @pytest.fixture
    def full_config(self):
        """Full configuration with all options."""
        return {
            "base_url": "https://wms.example.com",
            "username": "test_user",
            "password": "test_pass",
            "wms_api_version": "v10",
            "company_code": "ACME",
            "facility_code": "DC01",
            "entities": ["customer", "order", "inventory"],
            "page_size": 1000,
            "start_date": "2024-01-01T00:00:00Z",
            "enable_incremental": True,
            "flattening_enabled": True,
            "flattening_max_depth": 3,
        }

    def test_tap_initialization(self, minimal_config):
        """Test tap initializes correctly."""
        tap = TapOracleWMS(config=minimal_config)

        assert tap.name == "tap-oracle-wms"
        assert tap.config["base_url"] == "https://wms.example.com"
        assert tap._entity_cache is None
        assert tap._schema_cache == {}

    def test_discovery_property(self, minimal_config):
        """Test discovery property lazy loading."""
        tap = TapOracleWMS(config=minimal_config)

        assert tap._discovery is None
        discovery = tap.discovery
        assert discovery is not None
        assert tap._discovery is discovery  # Same instance

    def test_schema_generator_property(self, minimal_config):
        """Test schema generator property lazy loading."""
        tap = TapOracleWMS(config=minimal_config)

        assert tap._schema_generator is None
        generator = tap.schema_generator
        assert generator is not None
        assert tap._schema_generator is generator  # Same instance

    @patch("tap_oracle_wms.tap.asyncio.run")
    def test_discover_streams_sync_mode(self, mock_asyncio_run, full_config):
        """Test stream discovery in sync mode (configured entities)."""
        tap = TapOracleWMS(config=full_config)

        # Mock schema generation
        mock_asyncio_run.return_value = {
            "type": "object",
            "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
        }

        streams = tap.discover_streams()

        assert len(streams) == 3  # customer, order, inventory
        assert all(isinstance(s, WMSStream) for s in streams)
        assert [s.name for s in streams] == ["customer", "order", "inventory"]

    @patch("tap_oracle_wms.tap.asyncio.run")
    def test_discover_streams_discovery_mode(self, mock_asyncio_run, minimal_config):
        """Test stream discovery in discovery mode (API discovery)."""
        tap = TapOracleWMS(config=minimal_config)
        tap.set_discovery_mode(enabled=True)

        # Mock entity discovery
        mock_asyncio_run.side_effect = [
            {"customer": "/customers", "order": "/orders"},  # discover_entities
            {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
            },  # schema for customer
            {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
            },  # schema for order
        ]

        streams = tap.discover_streams()

        assert len(streams) == 2
        assert [s.name for s in streams] == ["customer", "order"]

    def test_discover_streams_no_entities(self, minimal_config):
        """Test discovery with no configured entities."""
        tap = TapOracleWMS(config=minimal_config)

        with patch.object(tap.logger, "warning") as mock_warning:
            streams = tap.discover_streams()

            assert streams == []
            mock_warning.assert_called_once()

    @patch("tap_oracle_wms.tap.asyncio.run")
    def test_create_stream_safe_success(self, mock_asyncio_run, minimal_config):
        """Test safe stream creation with schema generation."""
        tap = TapOracleWMS(config=minimal_config)

        mock_asyncio_run.return_value = {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
        }

        stream = tap._create_stream_safe("test_entity")

        assert stream is not None
        assert stream.name == "test_entity"
        assert isinstance(stream, WMSStream)

    @patch("tap_oracle_wms.tap.asyncio.run")
    def test_create_stream_safe_fallback(self, mock_asyncio_run, minimal_config):
        """Test stream creation with fallback schema."""
        tap = TapOracleWMS(config=minimal_config)

        # Make schema generation fail
        mock_asyncio_run.side_effect = Exception("API error")

        stream = tap._create_stream_safe("test_entity")

        assert stream is not None
        assert stream.name == "test_entity"
        # Should use predefined schema
        assert "id" in stream.schema["properties"]

    def test_get_predefined_schema(self, minimal_config):
        """Test predefined schema generation."""
        tap = TapOracleWMS(config=minimal_config)

        schema = tap._get_predefined_schema("any_entity")

        assert schema["type"] == "object"
        assert "id" in schema["properties"]
        assert "mod_ts" in schema["properties"]
        assert "create_ts" in schema["properties"]
        assert schema["additionalProperties"] is True

    @patch("tap_oracle_wms.tap.EntityDiscovery")
    async def test_discover_entities_async(self, mock_discovery_class, minimal_config):
        """Test async entity discovery."""
        tap = TapOracleWMS(config=minimal_config)

        # Mock discovery instance
        mock_discovery = AsyncMock()
        mock_discovery.discover_entities.return_value = {
            "customer": "/customers",
            "order": "/orders",
        }
        # filter_entities is synchronous
        mock_discovery.filter_entities = Mock(return_value={"customer": "/customers"})
        mock_discovery_class.return_value = mock_discovery

        # Force recreation of discovery
        tap._discovery = None

        entities = await tap._discover_entities_async()

        assert entities == {"customer": "/customers"}
        assert tap._entity_cache == entities  # Cached

    @patch("tap_oracle_wms.tap.EntityDiscovery")
    @patch("tap_oracle_wms.tap.SchemaGenerator")
    async def test_generate_schema_async_with_flattening(
        self, mock_schema_gen_class, mock_discovery_class, full_config
    ):
        """Test async schema generation with flattening enabled."""
        tap = TapOracleWMS(config=full_config)

        # Mock discovery
        mock_discovery = AsyncMock()
        mock_discovery.describe_entity.return_value = {
            "fields": [{"name": "id", "type": "pk"}]
        }
        mock_discovery.get_entity_sample.return_value = [
            {"id": 1, "complex": {"nested": "value"}}
        ]
        mock_discovery_class.return_value = mock_discovery

        # Mock schema generator
        mock_schema_gen = Mock()
        mock_schema_gen.generate_hybrid_schema.return_value = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "complex_nested": {"type": "string"},
            },
        }
        mock_schema_gen_class.return_value = mock_schema_gen

        # Force recreation
        tap._discovery = None
        tap._schema_generator = None

        schema = await tap._generate_schema_async("customer")

        assert schema is not None
        assert "complex_nested" in schema["properties"]  # Flattened
        mock_discovery.get_entity_sample.assert_called_with("customer", limit=50)

    def test_post_process(self, minimal_config):
        """Test record post-processing."""
        tap = TapOracleWMS(config=minimal_config)

        row = {"id": 1, "name": "Test"}
        processed = tap.post_process(row, None)

        assert processed is not None
        assert "_extracted_at" in processed
        assert processed["id"] == 1
        assert processed["name"] == "Test"

    def test_catalog_dict_property(self, minimal_config):
        """Test catalog dict property."""
        tap = TapOracleWMS(config=minimal_config)

        # No catalog
        assert tap.catalog_dict == {}

        # With catalog
        tap._catalog = Mock()
        tap._catalog.to_dict.return_value = {"streams": []}
        assert tap.catalog_dict == {"streams": []}

    def test_state_dict_property(self, minimal_config):
        """Test state dict property."""
        tap = TapOracleWMS(config=minimal_config)

        # Test reading state (Singer SDK doesn't have state setter)
        state = tap.state_dict
        assert isinstance(state, dict)

        # For Singer SDK, state is managed internally through bookmarks
        # We can't directly set tap.state, but we can verify state_dict works
        assert state is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
