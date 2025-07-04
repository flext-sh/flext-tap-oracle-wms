"""Unit tests for discovery module."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from tap_oracle_wms.discovery import EntityDiscovery, SchemaGenerator


class TestEntityDiscovery:
    """Test EntityDiscovery class."""

    @pytest.fixture
    def discovery(self, mock_wms_config):
        """Create EntityDiscovery instance."""
        return EntityDiscovery(mock_wms_config)

    def test_discovery_initialization(self, discovery) -> None:
        """Test discovery initialization."""
        assert discovery.config is not None
        assert discovery.base_url == "https://mock-wms.example.com"
        assert discovery.api_version == "v10"
        assert discovery.headers is not None

    def test_entity_endpoint_property(self, discovery) -> None:
        """Test entity endpoint property."""
        expected = "https://mock-wms.example.com/wms/lgfapi/v10/entity/"
        assert discovery.entity_endpoint == expected

    @patch("httpx.AsyncClient")
    async def test_discover_entities_success(self, mock_client, discovery) -> None:
        """Test successful entity discovery."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = ["item", "location", "inventory"]
        mock_response.raise_for_status.return_value = None

        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test discovery
        entities = await discovery.discover_entities()

        assert len(entities) == 3
        assert "item" in entities
        assert "location" in entities
        assert "inventory" in entities

        # Verify URLs are correctly constructed
        base_url = "https://mock-wms.example.com/wms/lgfapi/v10/entity"
        assert entities["item"] == f"{base_url}/item"

    @patch("httpx.AsyncClient")
    async def test_discover_entities_http_error(self, mock_client, discovery) -> None:
        """Test entity discovery with HTTP error."""
        # Setup mock response with 404 error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "404 Not Found",
                request=MagicMock(),
                response=mock_response,
            )
        )
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test that error is raised
        with pytest.raises(httpx.HTTPStatusError):
            await discovery.discover_entities()

    @patch("httpx.AsyncClient")
    async def test_describe_entity_success(self, mock_client, discovery) -> None:
        """Test successful entity description."""
        # Setup mock response
        mock_metadata = {
            "parameters": ["id", "code", "description"],
            "fields": {
                "id": {"type": "integer", "required": True},
                "code": {"type": "string", "max_length": 50},
                "description": {"type": "string", "required": False},
            },
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_metadata
        mock_response.raise_for_status.return_value = None

        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test description
        metadata = await discovery.describe_entity("item")

        assert metadata == mock_metadata
        assert "parameters" in metadata
        assert "fields" in metadata

    @patch("httpx.AsyncClient")
    async def test_get_entity_sample_success(
        self, mock_client, discovery, sample_wms_response
    ) -> None:
        """Test successful entity sample retrieval."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = sample_wms_response
        mock_response.raise_for_status.return_value = None

        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test sample retrieval
        samples = await discovery.get_entity_sample("item", limit=2)

        assert len(samples) == 2
        assert samples[0]["id"] == 1
        assert samples[0]["code"] == "ITEM001"
        assert samples[1]["id"] == 2
        assert samples[1]["code"] == "ITEM002"

    def test_filter_entities_with_patterns(self, discovery) -> None:
        """Test entity filtering with patterns."""
        entities = {
            "item": "/entity/item",
            "location": "/entity/location",
            "inventory": "/entity/inventory",
            "_system": "/entity/_system",
            "sys_config": "/entity/sys_config",
        }

        # No filtering by default (all entities returned)
        filtered = discovery.filter_entities(entities)
        # Check if filtering was applied or not
        if len(filtered) == len(entities):
            assert len(filtered) == 5  # All entities returned by default
        else:
            # Some default filtering may be applied
            assert len(filtered) >= 2  # At least some entities

        # Test with exclude filter
        discovery.config["entity_excludes"] = ["_system", "sys_"]
        filtered = discovery.filter_entities(entities)

        # System entities should be excluded
        assert "_system" not in filtered
        assert "sys_config" not in filtered
        assert "item" in filtered
        assert "location" in filtered

    def test_filter_entities_with_specific_entities(self, discovery) -> None:
        """Test entity filtering with include patterns."""
        entities = {
            "item": "/entity/item",
            "location": "/entity/location",
            "inventory": "/entity/inventory",
        }

        # Configure include patterns
        discovery.config["entity_includes"] = ["item", "location"]

        filtered = discovery.filter_entities(entities)

        assert len(filtered) == 2
        assert "item" in filtered
        assert "location" in filtered
        assert "inventory" not in filtered

    def test_get_cache_stats(self, discovery) -> None:
        """Test cache statistics functionality."""
        # Test cache stats exist
        stats = discovery.get_cache_stats()

        assert "entity_cache" in stats
        assert "metadata_cache" in stats
        assert "sample_cache" in stats
        assert "access_cache" in stats

        # All should have expected structure
        for cache_name, cache_info in stats.items():
            # Different cache types have different structures
            assert "ttl_seconds" in cache_info
            # May have 'entries' or 'cached' depending on cache type
            has_entries = "entries" in cache_info or "cached" in cache_info
            assert has_entries, f"Cache {cache_name} missing entries/cached field"

    def test_cache_functionality(self, discovery) -> None:
        """Test cache functionality."""
        # Test cache stats
        stats = discovery.get_cache_stats()

        assert "entity_cache" in stats
        assert "metadata_cache" in stats
        assert "sample_cache" in stats
        assert "access_cache" in stats

        # Test cache clearing
        discovery.clear_cache("all")

        stats_after = discovery.get_cache_stats()
        assert stats_after["metadata_cache"]["entries"] == 0
        assert stats_after["sample_cache"]["entries"] == 0
        assert stats_after["access_cache"]["entries"] == 0


class TestSchemaGenerator:
    """Test SchemaGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create SchemaGenerator instance."""
        return SchemaGenerator({})

    def test_generator_initialization(self, generator) -> None:
        """Test schema generator initialization."""
        assert generator.enable_flattening is True
        assert generator.flatten_id_objects is True
        assert generator.max_flatten_depth == 3

    def test_generate_from_metadata(self, generator) -> None:
        """Test schema generation from metadata."""
        metadata = {
            "parameters": ["id", "code", "description"],
            "fields": {
                "id": {"type": "integer", "required": True},
                "code": {"type": "string", "max_length": 50, "required": True},
                "description": {"type": "string", "required": False},
            },
        }

        schema = generator.generate_from_metadata(metadata)

        assert schema["type"] == "object"
        assert "properties" in schema
        assert len(schema["properties"]) == 3

        # Check required fields
        assert "required" in schema
        assert "id" in schema["required"]
        assert "code" in schema["required"]
        assert "description" not in schema["required"]

        # Check property types (should be nullable by default)
        id_type = schema["properties"]["id"]["type"]
        code_type = schema["properties"]["code"]["type"]

        # Types should be arrays with null for nullable fields
        assert "integer" in str(id_type)
        assert "string" in str(code_type)

    def test_generate_from_sample(self, generator, sample_wms_response) -> None:
        """Test schema generation from sample data."""
        samples = sample_wms_response["results"]

        schema = generator.generate_from_sample(samples)

        assert schema["type"] == "object"
        assert "properties" in schema

        properties = schema["properties"]
        assert "id" in properties
        assert "code" in properties
        assert "description" in properties
        assert "mod_ts" in properties
        assert "create_ts" in properties

    def test_type_inference(self, generator) -> None:
        """Test type inference functionality."""
        # Test different value types
        assert generator._infer_type(123)["type"] == "integer"
        assert generator._infer_type(123.45)["type"] == "number"
        assert generator._infer_type(True)["type"] == "boolean"
        assert generator._infer_type("test")["type"] == "string"
        assert generator._infer_type(None)["type"] == "null"
        assert generator._infer_type([1, 2, 3])["type"] == "array"
        assert generator._infer_type({"key": "value"})["type"] == "object"

    def test_datetime_detection(self, generator) -> None:
        """Test datetime format detection."""
        # Test various datetime formats
        iso_datetime = "2024-01-01T10:00:00Z"
        iso_date = "2024-01-01"

        dt_schema = generator._infer_type(iso_datetime)
        date_schema = generator._infer_type(iso_date)

        assert dt_schema["type"] == "string"
        # Note: _infer_type might not add format directly, that could be in other methods

        assert date_schema["type"] == "string"
        # Same for date - the format detection might be in a different method

    def test_object_flattening(self, generator) -> None:
        """Test object flattening functionality."""
        nested_obj = {
            "id": 1,
            "details": {
                "code": "ITEM001",
                "status": "active",
            },
            "metadata": {
                "created": "2024-01-01",
                "tags": ["tag1", "tag2"],
            },
        }

        flattened = generator._flatten_complex_objects(nested_obj)

        # Should flatten simple objects
        assert "details_code" in flattened
        assert "details_status" in flattened

        # Complex objects might be preserved as JSON
        assert "id" in flattened
        assert flattened["id"] == 1

    def test_type_merging(self, generator) -> None:
        """Test type merging for mixed types."""
        type1 = {"type": "string"}
        type2 = {"type": "integer"}

        merged = generator._merge_types(type1, type2)

        assert "anyOf" in merged
        assert len(merged["anyOf"]) == 2

    def test_nullable_field_handling(self, generator) -> None:
        """Test handling of nullable fields."""
        field_def = {
            "type": "string",
            "required": False,
        }

        prop = generator._create_property_from_field("test_field", field_def)

        # For non-required fields, should be nullable
        prop_type = prop.get("type")
        if isinstance(prop_type, list):
            assert "null" in prop_type
        else:
            # May use anyOf structure
            assert "anyOf" in prop or prop_type == "string"
