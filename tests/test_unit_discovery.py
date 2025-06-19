"""Unit tests for entity discovery functionality."""

from tap_oracle_wms.discovery import EntityDiscovery


class TestEntityDiscovery:
    """Test entity discovery functionality."""

    def test_discovery_client_initialization(self, sample_config) -> None:
        """Test that discovery client initializes properly."""
        discovery = EntityDiscovery(sample_config)

        assert discovery.config == sample_config
        assert discovery.base_url == sample_config["base_url"]
        assert hasattr(discovery, "_session")

    def test_entity_list_structure(self, sample_config) -> None:
        """Test that entity list has expected structure."""
        discovery = EntityDiscovery(sample_config)

        # Get the entity types that should be available
        entity_types = discovery.get_supported_entities()

        assert isinstance(entity_types, list)
        assert len(entity_types) > 0

        # Each entity should have required properties
        for entity in entity_types:
            assert isinstance(entity, dict)
            assert "name" in entity
            assert "endpoint" in entity

    def test_entity_schema_generation(self, sample_config) -> None:
        """Test that entity schemas are generated correctly."""
        discovery = EntityDiscovery(sample_config)

        # Test schema generation for a known entity
        test_entity = "facility"
        schema = discovery.get_entity_schema(test_entity)

        assert isinstance(schema, dict)
        assert "type" in schema
        assert "properties" in schema
        assert schema["type"] == "object"

        # Validate properties structure
        properties = schema["properties"]
        assert isinstance(properties, dict)
        assert len(properties) > 0

    def test_discover_entities_returns_catalog(self, sample_config) -> None:
        """Test that discover_entities returns proper catalog structure."""
        discovery = EntityDiscovery(sample_config)

        # Discover entities
        catalog = discovery.discover_entities()

        assert isinstance(catalog, list)
        assert len(catalog) > 0

        # Each catalog entry should have required fields
        for stream in catalog:
            assert isinstance(stream, dict)
            assert "tap_stream_id" in stream
            assert "schema" in stream
            assert "metadata" in stream

    def test_entity_field_types_validation(self, sample_config) -> None:
        """Test that entity field types are properly validated."""
        discovery = EntityDiscovery(sample_config)

        # Test field type mapping
        test_cases = [
            ("string", str),
            ("integer", int),
            ("number", float),
            ("boolean", bool),
            ("date-time", str),  # ISO format string
        ]

        for json_type, _python_type in test_cases:
            mapped_type = discovery._map_field_type(json_type)
            assert mapped_type is not None

    def test_entity_metadata_generation(self, sample_config) -> None:
        """Test that entity metadata is generated correctly."""
        discovery = EntityDiscovery(sample_config)

        test_entity = "facility"
        metadata = discovery.get_entity_metadata(test_entity)

        assert isinstance(metadata, list)
        assert len(metadata) > 0

        # Check for table-level metadata
        table_metadata = next((m for m in metadata if not m.get("breadcrumb")), None)
        assert table_metadata is not None
        assert "metadata" in table_metadata

    def test_supported_entities_not_empty(self, sample_config) -> None:
        """Test that supported entities list is not empty."""
        discovery = EntityDiscovery(sample_config)

        entities = discovery.get_supported_entities()
        assert len(entities) > 0

        # Should include common WMS entities
        entity_names = [e["name"] for e in entities]
        common_entities = ["facility", "item", "company"]

        for entity in common_entities:
            assert entity in entity_names, (
                f"Common entity '{entity}' should be supported"
            )
