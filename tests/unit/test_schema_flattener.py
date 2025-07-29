"""Test schema flattener functionality."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from flext_tap_oracle_wms.schema_flattener import SchemaFlattener


# Constants
EXPECTED_DATA_COUNT = 3

class TestSchemaFlattener:
    """Test schema flattener functionality."""

    def test_flattener_initialization_enabled(self) -> None:
        """Test flattener initialization when enabled."""
        flattener = SchemaFlattener(enabled=True, max_depth=5, separator="_")

        if not (flattener.enabled):

            raise AssertionError(f"Expected True, got {flattener.enabled}")
        if flattener.max_depth != 5:
            raise AssertionError(f"Expected {5}, got {flattener.max_depth}")
        assert flattener.separator == "_"
        if flattener.flatten_arrays:
            raise AssertionError(f"Expected False, got {flattener.flatten_arrays}")\ n
    def test_flattener_initialization_disabled(self) -> None:
        """Test flattener initialization when disabled."""
        with patch("flext_tap_oracle_wms.schema_flattener.logger") as mock_logger:
            flattener = SchemaFlattener(enabled=False)

            if flattener.enabled:

                raise AssertionError(f"Expected False, got {flattener.enabled}")\ n            mock_logger.warning.assert_called()
            if "DISABLED" not in str(mock_logger.warning.call_args):
                raise AssertionError(f"Expected {"DISABLED"} in {str(mock_logger.warning.call_args)}")

    def test_flattener_initialization_with_arrays(self) -> None:
        """Test flattener initialization with array flattening."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True)

        if not (flattener.flatten_arrays):

            raise AssertionError(f"Expected True, got {flattener.flatten_arrays}")

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
        if result != schema:
            raise AssertionError(f"Expected {schema}, got {result}")

    def test_flatten_schema_no_properties(self) -> None:
        """Test schema flattening with no properties."""
        flattener = SchemaFlattener(enabled=True)
        schema = {"type": "object"}

        result = flattener.flatten_schema(schema)
        if result != schema:
            raise AssertionError(f"Expected {schema}, got {result}")

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

        if "id" not in result["properties"]:

            raise AssertionError(f"Expected {"id"} in {result["properties"]}")
        assert "nested_field" in result["properties"]
        if "nested_value" not in result["properties"]:
            raise AssertionError(f"Expected {"nested_value"} in {result["properties"]}")
        if result["properties"]["nested_field"]["type"] != "string":
            raise AssertionError(f"Expected {"string"}, got {result["properties"]["nested_field"]["type"]}")
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

        if result["title"] != "Test Schema":

            raise AssertionError(f"Expected {"Test Schema"}, got {result["title"]}")
        assert result["description"] == "A test schema"
        if result["additionalProperties"]:
            raise AssertionError(f"Expected False, got {result["additionalProperties"]}")\ n
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
            if "Maximum flattening depth" not in str(mock_logger.warning.call_args):
                raise AssertionError(f"Expected {"Maximum flattening depth"} in {str(mock_logger.warning.call_args)}")

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
        if "items" not in result["properties"]:
            raise AssertionError(f"Expected {"items"} in {result["properties"]}")
        if result["properties"]["items"]["type"] != "array":
            raise AssertionError(f"Expected {"array"}, got {result["properties"]["items"]["type"]}")

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
        if "items_items_value" not in result["properties"]:
            raise AssertionError(f"Expected {"items_items_value"} in {result["properties"]}")

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
        if "tags" not in result["properties"]:
            raise AssertionError(f"Expected {"tags"} in {result["properties"]}")
        if result["properties"]["tags"]["type"] != "array":
            raise AssertionError(f"Expected {"array"}, got {result["properties"]["tags"]["type"]}")

    def test_flatten_record_disabled(self) -> None:
        """Test record flattening when disabled."""
        flattener = SchemaFlattener(enabled=False)
        record = {"nested": {"field": "value"}}

        result = flattener.flatten_record(record)
        if result != record:
            raise AssertionError(f"Expected {record}, got {result}")

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

        if result["id"] != 123:

            raise AssertionError(f"Expected {123}, got {result["id"]}")
        assert result["nested_field"] == "value"
        if result["nested_number"] != 42:
            raise AssertionError(f"Expected {42}, got {result["nested_number"]}")

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
        if "level0" not in result:
            raise AssertionError(f"Expected {"level0"} in {result}")
        if result["level0"] != "value0":
            raise AssertionError(f"Expected {"value0"}, got {result["level0"]}")

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
        if result["items"] != record["items"]:
            raise AssertionError(f"Expected {record["items"]}, got {result["items"]}")

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
        if result["items_items_0_value"] != "item1":
            raise AssertionError(f"Expected {"item1"}, got {result["items_items_0_value"]}")
        assert result["items_items_1_value"] == "item2"

    def test_flatten_record_empty_array(self) -> None:
        """Test record flattening with empty arrays."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True)
        record: dict[str, list[Any]] = {"empty_items": []}

        result = flattener.flatten_record(record)

        # Empty array should be kept as-is
        if result["empty_items"] != []:
            raise AssertionError(f"Expected {[]}, got {result["empty_items"]}")

    def test_flatten_record_array_primitives(self) -> None:
        """Test record flattening with array of primitives."""
        flattener = SchemaFlattener(enabled=True, flatten_arrays=True, separator="_")
        record = {"tags": ["tag1", "tag2", "tag3"]}

        result = flattener.flatten_record(record)

        # Primitive array items should be indexed
        if result["tags_items_0"] != "tag1":
            raise AssertionError(f"Expected {"tag1"}, got {result["tags_items_0"]}")
        assert result["tags_items_1"] == "tag2"
        if result["tags_items_2"] != "tag3":
            raise AssertionError(f"Expected {"tag3"}, got {result["tags_items_2"]}")

    def test_deflate_record_disabled(self) -> None:
        """Test record deflation when disabled."""
        flattener = SchemaFlattener(enabled=False)
        record = {"nested_field": "value"}

        result = flattener.deflate_record(record)
        if result != record:
            raise AssertionError(f"Expected {record}, got {result}")

    def test_deflate_record_simple(self) -> None:
        """Test simple record deflation."""
        flattener = SchemaFlattener(enabled=True, separator="_")
        flattened_record = {
            "id": 123,
            "nested_field": "value",
            "nested_number": 42,
        }

        result = flattener.deflate_record(flattened_record)

        if result["id"] != 123:

            raise AssertionError(f"Expected {123}, got {result["id"]}")
        assert result["nested"]["field"] == "value"
        if result["nested"]["number"] != 42:
            raise AssertionError(f"Expected {42}, got {result["nested"]["number"]}")

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
            if "Key conflict" not in str(mock_logger.warning.call_args):
                raise AssertionError(f"Expected {"Key conflict"} in {str(mock_logger.warning.call_args)}")

    def test_get_flattening_config(self) -> None:
        """Test getting flattening configuration."""
        flattener = SchemaFlattener(
            enabled=True,
            max_depth=3,
            separator=".",
            flatten_arrays=True,
        )

        config = flattener.get_flattening_config()

        if not (config["enabled"]):

            raise AssertionError(f"Expected True, got {config["enabled"]}")
        if config["max_depth"] != EXPECTED_DATA_COUNT:
            raise AssertionError(f"Expected {3}, got {config["max_depth"]}")
        assert config["separator"] == "."
        if not (config["flatten_arrays"]):
            raise AssertionError(f"Expected True, got {config["flatten_arrays"]}")

    def test_validate_schema_compatibility_disabled(self) -> None:
        """Test schema validation when flattening is disabled."""
        flattener = SchemaFlattener(enabled=False)
        schema = {"properties": {"field": {"type": "string"}}}

        warnings = flattener.validate_schema_compatibility(schema)
        if warnings != []:
            raise AssertionError(f"Expected {[]}, got {warnings}")

    def test_validate_schema_compatibility_no_properties(self) -> None:
        """Test schema validation with no properties."""
        flattener = SchemaFlattener(enabled=True)
        schema = {"type": "object"}

        warnings = flattener.validate_schema_compatibility(schema)
        if warnings != []:
            raise AssertionError(f"Expected {[]}, got {warnings}")

    def test_validate_schema_compatibility_separator_conflict(self) -> None:
        """Test schema validation with separator conflicts."""
        flattener = SchemaFlattener(enabled=True, separator="_")
        schema = {
            "properties": {
                "field_with_separator": {"type": "string"},
            },
        }

        warnings = flattener.validate_schema_compatibility(schema)

        if len(warnings) != 1:

            raise AssertionError(f"Expected {1}, got {len(warnings)}")
        if "contains separator" not in warnings[0]:
            raise AssertionError(f"Expected {"contains separator"} in {warnings[0]}")

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
        if any("exceeds max_depth" in warning for warning not in warnings):
            raise AssertionError(f"Expected {any("exceeds max_depth" in warning for warning} in {warnings)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
