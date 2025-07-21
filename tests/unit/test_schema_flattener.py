"""Test schema flattener functionality."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from flext_tap_oracle_wms.schema_flattener import SchemaFlattener


class TestSchemaFlattener:
    """Test schema flattener functionality."""

    def test_flattener_initialization_enabled(self) -> None:
        """Test flattener initialization when enabled."""
        flattener = SchemaFlattener(enabled=True, max_depth=5, separator="_")

        assert flattener.enabled is True
        assert flattener.max_depth == 5
        assert flattener.separator == "_"
        assert flattener.flatten_arrays is False

    def test_flattener_initialization_disabled(self) -> None:
        """Test flattener initialization when disabled."""
        with patch("flext_tap_oracle_wms.schema_flattener.logger") as mock_logger:
            flattener = SchemaFlattener(enabled=False)

            assert flattener.enabled is False
            mock_logger.warning.assert_called()
            assert "DISABLED" in str(mock_logger.warning.call_args)

    def test_flattener_initialization_with_arrays(self) -> None:
        """Test flattener initialization with array flattening."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True)

        assert flattener.flatten_arrays is True

    def test_flatten_schema_disabled(self) -> None:
        """Test schema flattening when disabled."""
        flattener = SchemaFlattener(enabled=False)
        schema = {
            "type": "object",
            "properties": {
                "nested": {
                    "type": "object",
                    "properties": {"field": {"type": "string"}},
                },
            },
        }

        result = flattener.flatten_schema(schema)
        assert result == schema

    def test_flatten_schema_no_properties(self) -> None:
        """Test schema flattening with no properties."""
        flattener = SchemaFlattener(enabled=True)
        schema = {"type": "object"}

        result = flattener.flatten_schema(schema)
        assert result == schema

    def test_flatten_schema_simple(self) -> None:
        """Test simple schema flattening."""
        flattener = SchemaFlattener(enabled=True, separator="_")
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "nested": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string"},
                        "value": {"type": "number"},
                    },
                },
            },
        }

        result = flattener.flatten_schema(schema)

        assert "id" in result["properties"]
        assert "nested_field" in result["properties"]
        assert "nested_value" in result["properties"]
        assert result["properties"]["nested_field"]["type"] == "string"
        assert result["properties"]["nested_value"]["type"] == "number"

    def test_flatten_schema_with_metadata(self) -> None:
        """Test schema flattening preserves metadata."""
        flattener = SchemaFlattener(enabled=True)
        schema = {
            "type": "object",
            "title": "Test Schema",
            "description": "A test schema",
            "additionalProperties": False,
            "properties": {
                "field": {"type": "string"},
            },
        }

        result = flattener.flatten_schema(schema)

        assert result["title"] == "Test Schema"
        assert result["description"] == "A test schema"
        assert result["additionalProperties"] is False

    def test_flatten_schema_max_depth(self) -> None:
        """Test schema flattening respects max depth."""
        flattener = SchemaFlattener(enabled=True, max_depth=1)
        schema = {
            "type": "object",
            "properties": {
                "level1": {
                    "type": "object",
                    "properties": {
                        "level2": {
                            "type": "object",
                            "properties": {
                                "level3": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }

        with patch("flext_tap_oracle_wms.schema_flattener.logger") as mock_logger:
            _ = flattener.flatten_schema(schema)

            # Should stop at max depth and log warning
            mock_logger.warning.assert_called()
            assert "Maximum flattening depth" in str(mock_logger.warning.call_args)

    def test_flatten_schema_arrays_disabled(self) -> None:
        """Test schema flattening with arrays when array flattening is disabled."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=False)
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"value": {"type": "string"}},
                    },
                },
            },
        }

        result = flattener.flatten_schema(schema)

        # Array should be kept as-is
        assert "items" in result["properties"]
        assert result["properties"]["items"]["type"] == "array"

    def test_flatten_schema_arrays_enabled(self) -> None:
        """Test schema flattening with arrays when array flattening is enabled."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True, separator="_")
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"value": {"type": "string"}},
                    },
                },
            },
        }

        result = flattener.flatten_schema(schema)

        # Array items should be flattened
        assert "items_items_value" in result["properties"]

    def test_flatten_schema_simple_array(self) -> None:
        """Test schema flattening with simple array items."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True)
        schema = {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
        }

        result = flattener.flatten_schema(schema)

        # Simple array should be kept as-is
        assert "tags" in result["properties"]
        assert result["properties"]["tags"]["type"] == "array"

    def test_flatten_record_disabled(self) -> None:
        """Test record flattening when disabled."""
        flattener = SchemaFlattener(enabled=False)
        record = {"nested": {"field": "value"}}

        result = flattener.flatten_record(record)
        assert result == record

    def test_flatten_record_simple(self) -> None:
        """Test simple record flattening."""
        flattener = SchemaFlattener(enabled=True, separator="_")
        record = {
            "id": 123,
            "nested": {
                "field": "value",
                "number": 42,
            },
        }

        result = flattener.flatten_record(record)

        assert result["id"] == 123
        assert result["nested_field"] == "value"
        assert result["nested_number"] == 42

    def test_flatten_record_max_depth(self) -> None:
        """Test record flattening respects max depth."""
        flattener = SchemaFlattener(enabled=True, max_depth=1)
        record = {
            "level0": "value0",
            "level1": {
                "level2": {
                    "level3": "deep_value",
                },
            },
        }

        result = flattener.flatten_record(record)

        # With max_depth=1, should process depth 0 only
        # So level0 should be there, but level1 won't be processed, so result might be empty
        # except for leaf values at depth 0
        assert "level0" in result
        assert result["level0"] == "value0"

    def test_flatten_record_arrays_disabled(self) -> None:
        """Test record flattening with arrays when disabled."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=False)
        record = {
            "items": [
                {"value": "item1"},
                {"value": "item2"},
            ],
        }

        result = flattener.flatten_record(record)

        # Array should be kept as-is
        assert result["items"] == record["items"]

    def test_flatten_record_arrays_enabled(self) -> None:
        """Test record flattening with arrays when enabled."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True, separator="_")
        record = {
            "items": [
                {"value": "item1"},
                {"value": "item2"},
            ],
        }

        result = flattener.flatten_record(record)

        # Array items should be flattened
        assert result["items_items_0_value"] == "item1"
        assert result["items_items_1_value"] == "item2"

    def test_flatten_record_empty_array(self) -> None:
        """Test record flattening with empty arrays."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True)
        record: dict[str, list[Any]] = {"empty_items": []}

        result = flattener.flatten_record(record)

        # Empty array should be kept as-is
        assert result["empty_items"] == []

    def test_flatten_record_array_primitives(self) -> None:
        """Test record flattening with array of primitives."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True, separator="_")
        record = {"tags": ["tag1", "tag2", "tag3"]}

        result = flattener.flatten_record(record)

        # Primitive array items should be indexed
        assert result["tags_items_0"] == "tag1"
        assert result["tags_items_1"] == "tag2"
        assert result["tags_items_2"] == "tag3"

    def test_deflate_record_disabled(self) -> None:
        """Test record deflation when disabled."""
        flattener = SchemaFlattener(enabled=False)
        record = {"nested_field": "value"}

        result = flattener.deflate_record(record)
        assert result == record

    def test_deflate_record_simple(self) -> None:
        """Test simple record deflation."""
        flattener = SchemaFlattener(enabled=True, separator="_")
        flattened_record = {
            "id": 123,
            "nested_field": "value",
            "nested_number": 42,
        }

        result = flattener.deflate_record(flattened_record)

        assert result["id"] == 123
        assert result["nested"]["field"] == "value"
        assert result["nested"]["number"] == 42

    def test_deflate_record_conflict(self) -> None:
        """Test record deflation with key conflicts."""
        flattener = SchemaFlattener(enabled=True, separator="_")
        flattened_record = {
            "field": "original",
            "field_subfield": "nested",
        }

        with patch("flext_tap_oracle_wms.schema_flattener.logger") as mock_logger:
            _ = flattener.deflate_record(flattened_record)

            # Should log warning about conflict
            mock_logger.warning.assert_called()
            assert "Key conflict" in str(mock_logger.warning.call_args)

    def test_get_flattening_config(self) -> None:
        """Test getting flattening configuration."""
        flattener = SchemaFlattener(
            enabled=True,
            max_depth=3,
            separator=".",
            flatten_arrays=True,
        )

        config = flattener.get_flattening_config()

        assert config["enabled"] is True
        assert config["max_depth"] == 3
        assert config["separator"] == "."
        assert config["flatten_arrays"] is True

    def test_validate_schema_compatibility_disabled(self) -> None:
        """Test schema validation when flattening is disabled."""
        flattener = SchemaFlattener(enabled=False)
        schema = {"properties": {"field": {"type": "string"}}}

        warnings = flattener.validate_schema_compatibility(schema)
        assert warnings == []

    def test_validate_schema_compatibility_no_properties(self) -> None:
        """Test schema validation with no properties."""
        flattener = SchemaFlattener(enabled=True)
        schema = {"type": "object"}

        warnings = flattener.validate_schema_compatibility(schema)
        assert warnings == []

    def test_validate_schema_compatibility_separator_conflict(self) -> None:
        """Test schema validation with separator conflicts."""
        flattener = SchemaFlattener(enabled=True, separator="_")
        schema = {
            "properties": {
                "field_with_separator": {"type": "string"},
            },
        }

        warnings = flattener.validate_schema_compatibility(schema)

        assert len(warnings) == 1
        assert "contains separator" in warnings[0]

    def test_validate_schema_compatibility_depth_warning(self) -> None:
        """Test schema validation with depth warnings."""
        flattener = SchemaFlattener(enabled=True, max_depth=1)
        schema = {
            "properties": {
                "level1": {
                    "type": "object",
                    "properties": {
                        "level2": {
                            "type": "object",
                            "properties": {
                                "level3": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }

        warnings = flattener.validate_schema_compatibility(schema)

        assert len(warnings) > 0
        assert any("exceeds max_depth" in warning for warning in warnings)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
