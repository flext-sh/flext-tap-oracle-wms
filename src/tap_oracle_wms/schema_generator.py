"""Schema generator implementation following SOLID principles.

This module focuses solely on schema generation operations,
following the Single Responsibility Principle.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Union

from .interfaces import SchemaGeneratorInterface, TypeMapperInterface
from .type_mapping import convert_metadata_type_to_singer

logger = logging.getLogger(__name__)

# Type alias for values that can be of various types to avoid FBT001
ValueType = Union[float, str, int, bool, dict[str, Any], list[Any], None]

# Flattening thresholds
FK_INDICATOR_THRESHOLD = 0.5
# REMOVED ARTIFICIAL LIMITATION: SIMPLE_OBJECT_MAX_FIELDS completely
# Accept unlimited fields in objects as the WMS API provides


class SchemaGenerator(SchemaGeneratorInterface):
    """Generate Singer schemas from WMS entity metadata ONLY.

    Focuses solely on schema generation logic, delegating type mapping
    to specialized components. Follows SRP and DIP principles.
    """

    def __init__(
        self, config: dict[str, Any], type_mapper: TypeMapperInterface | None = None
    ) -> None:
        """Initialize schema generator with configuration and type mapper."""
        self.config = config
        # Dependency injection for type mapper (DIP)
        self.type_mapper = type_mapper or DefaultTypeMapper()

        # Schema generation settings
        self.flattening_enabled = config.get("flattening_enabled", True)
        # REMOVED: max_sample_size - samples are FORBIDDEN

    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate schema from API metadata only."""
        if not metadata or "fields" not in metadata:
            error_msg = "🚨 ABORT: Empty or invalid metadata provided for schema generation - NO fallback allowed!"
            logger.error(error_msg)
            raise SystemExit(error_msg)

        properties = {}
        required_fields = []
        fields = metadata["fields"]

        # Handle both dictionary and list formats for fields
        if isinstance(fields, list):
            # Convert list format to dictionary format
            fields_dict = {}
            for field_item in fields:
                if isinstance(field_item, dict) and "name" in field_item:
                    field_name = field_item["name"]
                    field_info = {k: v for k, v in field_item.items() if k != "name"}
                    fields_dict[field_name] = field_info
            fields = fields_dict

        for field_name, field_info in fields.items():
            field_type = field_info.get("type", "string")
            max_length = field_info.get("max_length")
            required = field_info.get("required", False)

            properties[field_name] = self.type_mapper.convert_metadata_type_to_singer(
                metadata_type=field_type,
                column_name=field_name,
                max_length=max_length,
            )

            # Add to required if explicitly marked as required
            if required:
                required_fields.append(field_name)

        schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }

        if required_fields:
            schema["required"] = required_fields

        return schema

    def generate_metadata_schema_with_flattening(
        self, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate schema from API metadata only, with predictable flattening support.

        This method uses ONLY the API describe metadata to generate the schema,
        and anticipates flattening fields based on metadata patterns.
        """
        # Generate base schema from metadata
        base_schema = self.generate_from_metadata(metadata)

        # If flattening is enabled, add anticipated flattening fields
        if self.flattening_enabled:
            base_schema = self._add_anticipated_flattening_fields(base_schema, metadata)

        return base_schema

    # REMOVED: generate_from_sample - FORBIDDEN METHOD
    # NEVER, NEVER, NEVER use samples for schema generation
    # This method has been PERMANENTLY DELETED to prevent any possibility of sample usage

    # REMOVED: generate_hybrid_schema - FORBIDDEN METHOD
    # NEVER, NEVER, NEVER use samples for schema generation
    # This method has been PERMANENTLY DELETED to prevent any possibility of sample usage
    # Any attempt to use samples is a FATAL ERROR and will cause immediate abortion

    def flatten_complex_objects(
        self, data: dict[str, Any], prefix: str = "", separator: str = "_"
    ) -> dict[str, Any]:
        """Flatten nested objects for schema consistency."""
        if not self.flattening_enabled:
            return data

        flattened: dict[str, Any] = {}

        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key

            if isinstance(value, dict):
                self._flatten_dict_value(flattened, key, value, new_key, separator)
            elif isinstance(value, list):
                self._flatten_list_value(flattened, key, value, new_key, separator)
            else:
                flattened[new_key] = value

        return flattened

    def _generate_metadata_properties(self, fields: dict[str, Any]) -> dict[str, Any]:
        """Generate properties from metadata fields."""
        properties = {}

        for field_name, field_info in fields.items():
            field_type = field_info.get("type", "string")
            max_length = field_info.get("max_length")

            properties[field_name] = self.type_mapper.convert_metadata_type_to_singer(
                metadata_type=field_type,
                column_name=field_name,
                max_length=max_length,
            )

        return properties

    # 🚨 METHOD PERMANENTLY DELETED: _process_samples
    # This method is FORBIDDEN - schema generation uses ONLY API metadata describe

    # 🚨 METHOD PERMANENTLY DELETED: _find_representative_value
    # This method is FORBIDDEN - schema generation uses ONLY API metadata describe

    def _flatten_dict_value(
        self,
        flattened: dict[str, Any],
        key: str,
        value: dict[str, Any],
        new_key: str,
        separator: str,
    ) -> None:
        """Flatten dictionary values with appropriate strategy."""
        if self._is_foreign_key_object(value):
            self._flatten_fk_object(flattened, key, value)
        elif self._is_set_object(value):
            self._flatten_set_object(flattened, value, new_key)
        else:
            # Regular nested object
            nested_flattened = self.flatten_complex_objects(value, new_key, separator)
            flattened.update(nested_flattened)

    def _flatten_list_value(
        self,
        flattened: dict[str, Any],
        key: str,
        value: list[Any],
        new_key: str,
        separator: str,
    ) -> None:
        """Flatten list values based on content type."""
        if not value:
            flattened[f"{new_key}_count"] = 0
            return

        # Check if this is a special list type
        if (
            "set" in key.lower()
            or "instruction" in key.lower()
            or "serial" in key.lower()
        ):
            self._flatten_special_list(flattened, value, new_key)
        else:
            self._flatten_regular_list(flattened, value, new_key, separator)

    def _flatten_special_list(
        self, flattened: dict[str, Any], value: list[Any], new_key: str
    ) -> None:
        """Flatten special lists (sets, instructions, etc.)."""
        flattened[f"{new_key}_count"] = len(value)
        if value:  # Only store non-empty lists
            flattened[f"{new_key}_data"] = json.dumps(value, default=str)

    def _flatten_regular_list(
        self,
        flattened: dict[str, Any],
        value: list[Any],
        new_key: str,
        separator: str,
    ) -> None:
        """Flatten regular lists by indexing elements."""
        flattened[f"{new_key}_count"] = len(value)

        # Flatten all elements - no artificial limitations
        max_elements = len(value)  # Accept unlimited elements as WMS provides
        for i, item in enumerate(value[:max_elements]):
            if isinstance(item, dict):
                item_flattened = self.flatten_complex_objects(
                    item, f"{new_key}_{i}", separator
                )
                flattened.update(item_flattened)
            else:
                flattened[f"{new_key}_{i}"] = item

    def _flatten_fk_object(
        self, flattened: dict[str, Any], key: str, value: dict[str, Any]
    ) -> None:
        """Flatten foreign key object."""
        base_name = self._get_fk_base_name(key)

        # Add ID field (primary for joins)
        if "id" in value:
            flattened[f"{base_name}_id"] = value["id"]

        # Add key field if different from ID
        for field in ["key", "code", "name"]:
            if field in value and field != "id":
                flattened[f"{base_name}_{field}"] = value[field]

    def _flatten_set_object(
        self, flattened: dict[str, Any], value: dict[str, Any], new_key: str
    ) -> None:
        """Flatten SET object data."""
        set_data = {
            "count": value.get("result_count", 0),
            "total": value.get("total_count", value.get("result_count", 0)),
        }

        # Extract filter parameters if present
        if "next_page" in value:
            try:
                from urllib.parse import parse_qs, urlparse

                parsed = urlparse(value["next_page"])
                params = parse_qs(parsed.query)
                if params:
                    set_data["filter_params"] = json.dumps(params)
            except Exception:
                pass  # Ignore parsing errors

        # Flatten the set data
        for set_key, set_value in set_data.items():
            flattened[f"{new_key}_{set_key}"] = set_value

    def _is_foreign_key_object(self, obj: dict[str, Any]) -> bool:
        """Check if object represents a foreign key reference."""
        if not isinstance(obj, dict):
            return False
        
        # REMOVED ARTIFICIAL LIMITATION: Accept any number of fields as WMS provides
        # No maximum field count restrictions - process all data as provided by API

        # Check for FK indicators
        fk_indicators = {"id", "key", "code", "name", "url"}
        obj_keys = set(obj.keys())

        # Must have ID and at least one other identifier
        has_id = "id" in obj_keys
        has_identifier = bool(obj_keys & (fk_indicators - {"id"}))

        return has_id and has_identifier

    def _is_set_object(self, obj: dict[str, Any]) -> bool:
        """Check if object represents a SET (collection) reference."""
        if not isinstance(obj, dict):
            return False

        set_indicators = {"result_count", "total_count", "next_page", "previous_page"}
        return bool(set(obj.keys()) & set_indicators)

    def _get_fk_base_name(self, key: str) -> str:
        """Get base name for FK field from original key."""
        # Remove common suffixes to get base name
        suffixes = ["_set", "_object", "_ref", "_fk"]
        base_name = key.lower()

        for suffix in suffixes:
            if base_name.endswith(suffix):
                base_name = base_name[: -len(suffix)]
                break

        return base_name

    # 🚨 CRITICAL: _get_default_schema METHOD PERMANENTLY DELETED
    # NO fallback schemas allowed - schema MUST come from API metadata describe only!


class DefaultTypeMapper(TypeMapperInterface):
    """Default type mapper implementation using existing type mapping logic."""

    def convert_metadata_type_to_singer(
        self,
        metadata_type: str | None,
        column_name: str = "",
        max_length: int | None = None,
        # 🚨 REMOVED: sample_value parameter - FORBIDDEN
    ) -> dict[str, Any]:
        """Convert WMS metadata type to Singer schema format.

        🚨 CRITICAL: Schema generation uses ONLY metadata - no other parameters accepted
        Type conversion MUST use ONLY metadata_type and max_length from API describe
        """

        return convert_metadata_type_to_singer(
            metadata_type=metadata_type,
            column_name=column_name,
            max_length=max_length,
            # 🚨 CRITICAL: Uses ONLY metadata
        )

    # REMOVED: infer_type_from_sample - FORBIDDEN METHOD
    # NEVER, NEVER, NEVER infer types from samples - this method is PERMANENTLY DELETED

    def _add_anticipated_flattening_fields(
        self, base_schema: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Add anticipated flattening fields based on metadata patterns.

        This method predicts which fields will be created by flattening
        based on known WMS API patterns, without needing data samples.
        """
        properties = base_schema.get("properties", {}).copy()

        # Known WMS object types that get flattened
        object_field_patterns = {
            "facility": ["id", "code", "name", "key"],
            "company": ["id", "code", "name", "key"],
            "user": ["id", "code", "name", "key"],
            "location": ["id", "code", "name", "key", "zone_key"],
            "item": ["id", "code", "name", "key", "desc"],
            "task": ["id", "key", "type"],
            "wave": ["id", "key", "number"],
            "order": ["id", "key", "number"],
            "allocation": ["id", "key", "number"],
            "status": ["id", "code", "name"],
            "configuration": ["id", "code", "name"],
        }

        # List field patterns that get flattened
        list_field_patterns = {
            "serial": ["count", "data"],
            "instruction": ["count", "data"],
            "set": ["count", "total", "filter_params"],
        }

        # Scan existing fields for flattening patterns
        for field_name, field_schema in properties.items():
            # Check for object fields (ending with common WMS object names)
            for obj_type, sub_fields in object_field_patterns.items():
                if field_name.endswith(f"_{obj_type}") or field_name == obj_type:
                    self._add_object_flattening_fields(
                        properties, field_name, sub_fields
                    )

            # Check for list fields
            for list_type, sub_fields in list_field_patterns.items():
                if list_type in field_name.lower():
                    self._add_list_flattening_fields(properties, field_name, sub_fields)

        # Return updated schema
        updated_schema = base_schema.copy()
        updated_schema["properties"] = properties
        return updated_schema

    def _add_object_flattening_fields(
        self, properties: dict[str, Any], base_field: str, sub_fields: list[str]
    ) -> None:
        """Add object flattening fields to properties."""
        for sub_field in sub_fields:
            flattened_field = f"{base_field}_{sub_field}"
            if flattened_field not in properties:
                # Add the flattened field with appropriate type
                if sub_field == "id":
                    field_type = {"type": ["integer", "null"]}
                else:
                    field_type = {"type": ["string", "null"]}

                field_type["x-wms-metadata"] = {
                    "original_metadata_type": "flattened_fk",
                    "flattened_from": base_field,
                    "column_name": flattened_field,
                    "anticipated": True,
                }
                properties[flattened_field] = field_type

    def _add_list_flattening_fields(
        self, properties: dict[str, Any], base_field: str, sub_fields: list[str]
    ) -> None:
        """Add list flattening fields to properties."""
        for sub_field in sub_fields:
            flattened_field = f"{base_field}_{sub_field}"
            if flattened_field not in properties:
                # Add the flattened field with appropriate type
                if sub_field == "count" or sub_field in ["total"]:
                    field_type = {"type": ["integer", "null"]}
                else:
                    field_type = {"type": ["string", "null"]}

                field_type["x-wms-metadata"] = {
                    "original_metadata_type": "flattened_list",
                    "flattened_from": base_field,
                    "column_name": flattened_field,
                    "anticipated": True,
                }
                properties[flattened_field] = field_type
