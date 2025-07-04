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
SIMPLE_OBJECT_MAX_FIELDS = 3


class SchemaGenerator(SchemaGeneratorInterface):
    """Generate Singer schemas from WMS entity metadata and samples.

    Focuses solely on schema generation logic, delegating type mapping
    to specialized components. Follows SRP and DIP principles.
    """

    def __init__(self, config: dict[str, Any], type_mapper: TypeMapperInterface | None = None) -> None:
        """Initialize schema generator with configuration and type mapper."""
        self.config = config
        # Dependency injection for type mapper (DIP)
        self.type_mapper = type_mapper or DefaultTypeMapper()

        # Schema generation settings
        self.flattening_enabled = config.get("flattening_enabled", True)
        self.max_sample_size = config.get("max_sample_size", 100)

    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate schema from API metadata only."""
        if not metadata or "fields" not in metadata:
            logger.warning("Empty or invalid metadata provided for schema generation")
            return self._get_default_schema()

        properties = {}
        required_fields = []
        fields = metadata["fields"]

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

    def generate_from_sample(self, samples: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate schema from sample data only."""
        if not samples:
            logger.warning("No samples provided for schema generation")
            return self._get_default_schema()

        # Process samples with flattening if enabled
        processed_samples = self._process_samples(samples)

        # Collect all unique fields
        all_fields: set[str] = set()
        for sample in processed_samples:
            all_fields.update(sample.keys())

        properties = {}
        for field_name in all_fields:
            # Find representative value
            field_value = self._find_representative_value(processed_samples, field_name)
            properties[field_name] = self.type_mapper.infer_type_from_sample(field_value)

        return {
            "type": "object",
            "properties": properties,
            "additionalProperties": True,  # Allow additional fields in sample-only mode
        }

    def generate_hybrid_schema(
        self, metadata: dict[str, Any], samples: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate schema using both metadata and samples for maximum accuracy."""
        if not metadata or "fields" not in metadata:
            logger.warning("Invalid metadata, falling back to sample-only schema")
            return self.generate_from_sample(samples)

        if not samples:
            logger.warning("No samples provided, falling back to metadata-only schema")
            return self.generate_from_metadata(metadata)

        # Start with metadata-based schema
        base_properties = self._generate_metadata_properties(metadata["fields"])

        # Process samples with flattening
        processed_samples = self._process_samples(samples)

        # Find additional fields from samples (flattened FK fields)
        sample_fields: set[str] = set()
        for sample in processed_samples:
            sample_fields.update(sample.keys())

        metadata_fields = set(base_properties.keys())
        additional_fields = sample_fields - metadata_fields

        logger.info(
            "Hybrid schema generation: metadata=%d fields, samples=%d fields, additional=%d fields",
            len(metadata_fields),
            len(sample_fields),
            len(additional_fields),
        )

        # Add additional fields from samples
        for field_name in additional_fields:
            field_value = self._find_representative_value(processed_samples, field_name)
            base_properties[field_name] = self.type_mapper.infer_type_from_sample(field_value)

        return {
            "type": "object",
            "properties": base_properties,
            "additionalProperties": True,  # Allow discovery of new fields
        }

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

    def _process_samples(self, samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process samples with flattening if enabled."""
        if not self.flattening_enabled:
            return samples

        processed = []
        for sample in samples[:self.max_sample_size]:
            flattened = self.flatten_complex_objects(sample)
            processed.append(flattened)

        return processed

    def _find_representative_value(
        self, samples: list[dict[str, Any]], field_name: str
    ) -> Any:
        """Find a representative non-null value for the field."""
        for sample in samples:
            value = sample.get(field_name)
            if value is not None:
                return value
        return None

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

        # Flatten first few elements for schema discovery
        max_elements = min(len(value), 3)  # Limit to prevent explosion
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
        if not isinstance(obj, dict) or len(obj) > SIMPLE_OBJECT_MAX_FIELDS:
            return False

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
                base_name = base_name[:-len(suffix)]
                break

        return base_name

    def _get_default_schema(self) -> dict[str, Any]:
        """Get default schema for fallback cases."""
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": ["integer", "null"],
                    "description": "Primary key",
                },
                "mod_ts": {
                    "type": ["string", "null"],
                    "format": "date-time",
                    "description": "Modification timestamp",
                },
            },
            "additionalProperties": True,
        }


class DefaultTypeMapper(TypeMapperInterface):
    """Default type mapper implementation using existing type mapping logic."""

    def convert_metadata_type_to_singer(
        self,
        metadata_type: str | None,
        column_name: str = "",
        max_length: int | None = None,
        sample_value: object = None,
    ) -> dict[str, Any]:
        """Convert WMS metadata type to Singer schema format."""
        return convert_metadata_type_to_singer(
            metadata_type=metadata_type,
            column_name=column_name,
            max_length=max_length,
            sample_value=sample_value,
        )

    def infer_type_from_sample(self, sample_value: object) -> dict[str, Any]:
        """Infer type from sample value."""
        # Use existing type mapping logic
        return convert_metadata_type_to_singer(
            metadata_type=None,
            column_name="",
            sample_value=sample_value,
        )
