"""Schema generator implementation following SOLID principles.

This module focuses solely on schema generation operations,
following the Single Responsibility Principle.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

# Removed circular dependency - use DI pattern
import re
from typing import Any

from flext_core import get_logger

from flext_tap_oracle_wms.interfaces import SchemaGeneratorInterface

logger = get_logger(__name__)


class SchemaGenerationError(Exception):
    """Exception raised when schema generation fails."""


class SchemaGenerator(SchemaGeneratorInterface):
    """Generate JSON schemas from Oracle WMS API metadata.

    Follows SRP by focusing solely on schema generation operations.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize schema generator with configuration.

        Args:
            config: Configuration dictionary for schema generation

        """
        self.config = config
        self.enable_flattening = config.get("flattening_enabled", True)
        self.max_flatten_depth = config.get("flattening_max_depth", 3)

    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate JSON schema from Oracle WMS API metadata.

        Args:
            metadata: API metadata describing entity structure.

        Returns:
            JSON schema dictionary for Singer protocol.

        """
        try:
            # Extract field definitions from metadata
            fields = metadata.get("fields", {})
            if not fields:
                logger.warning("No field definitions found in metadata")
                return SchemaGenerator._generate_empty_schema()

            # Normalize fields to dict format
            fields = self._normalize_fields_format(fields)

            # Build schema from fields
            properties, required_fields = self._build_schema_properties(fields)

            # Build complete schema
            return self._build_complete_schema(properties, required_fields)
        except (RuntimeError, ValueError, TypeError) as e:
            logger.exception("Schema generation from metadata failed")
            SchemaGenerator._raise_schema_error(f"Schema generation failed: {e}", e)
            return {}  # Unreachable but satisfies mypy

    def generate_metadata_schema_with_flattening(
        self,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate flattened JSON schema from Oracle WMS API metadata.

        Args:
            metadata: API metadata describing entity structure.

        Returns:
            Flattened JSON schema dictionary for Singer protocol.

        Raises:
            SchemaGenerationError: If schema generation fails

        """
        try:
            # Generate base schema
            base_schema = self.generate_from_metadata(metadata)

            if not self.enable_flattening:
                return base_schema

            # Apply flattening to properties
            flattened_properties = self.flatten_complex_objects(
                base_schema.get("properties", {}),
                separator="_",
            )
        except (RuntimeError, ValueError, TypeError) as e:
            logger.exception("Flattened schema generation failed")
            msg = f"Schema generation failed: {e}"
            raise SchemaGenerationError(
                msg,
            ) from e
        else:
            # Return flattened schema
            return {
                "type": "object",
                "properties": flattened_properties,
            }

    def flatten_complex_objects(
        self,
        data: dict[str, Any],
        prefix: str = "",
        separator: str = "_",
    ) -> dict[str, Any]:
        """Flatten nested objects for schema processing.

        Args:
            data: Complex nested data structure.
            prefix: Prefix for flattened field names.
            separator: Separator for flattened field names.

        Returns:
            Flattened data structure.

        """
        flattened = {}

        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key

            if isinstance(value, dict) and value.get("type") == "object":
                # Recursively flatten nested objects
                nested_properties = value.get("properties", {})
                if nested_properties:
                    flattened.update(
                        self.flatten_complex_objects(
                            nested_properties,
                            new_key,
                            separator,
                        ),
                    )
                else:
                    # Object without properties - keep as string
                    flattened[new_key] = {"type": "string"}
            else:
                # Keep primitive types as-is
                flattened[new_key] = value

        return flattened

    def _normalize_fields_format(self, fields: Any) -> dict[str, Any]:
        """Normalize fields format to dict format for processing.

        Args:
            fields: Fields from metadata (can be dict or list)

        Returns:
            Normalized fields as dict

        """
        if isinstance(fields, list):
            # Convert list format to dict format for processing
            fields_dict = {}
            for field_item in fields:
                if isinstance(field_item, dict) and "name" in field_item:
                    field_name = field_item["name"]
                    field_info = {k: v for k, v in field_item.items() if k != "name"}
                    fields_dict[field_name] = field_info
            return fields_dict
        if isinstance(fields, dict):
            return fields
        SchemaGenerator._raise_schema_error(
            f"Fields must be a dict or list, got {type(fields).__name__}",
        )
        return {}  # Unreachable but satisfies mypy

    def _build_schema_properties(
        self,
        fields: dict[str, Any],
    ) -> tuple[dict[str, Any], list[str]]:
        """Build schema properties and required fields list.

        Args:
            fields: Normalized fields dict

        Returns:
            Tuple of (properties, required_fields)

        """
        properties = {}
        required_fields = []

        for field_name, field_info in fields.items():
            if not field_name:
                continue

            field_schema = SchemaGenerator._create_field_schema(field_info)
            properties[field_name] = field_schema

            # Check if field is required
            if field_info.get("required", False):
                required_fields.append(field_name)

        return properties, required_fields

    @staticmethod
    def _build_complete_schema(
        properties: dict[str, Any],
        required_fields: list[str],
    ) -> dict[str, Any]:
        """Build complete schema from properties and required fields.

        Args:
            properties: Schema properties
            required_fields: List of required field names

        Returns:
            Complete schema dictionary

        """
        schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": True,  # Allow extra fields like 'url'
        }

        if required_fields:
            schema["required"] = required_fields

        return schema

    @staticmethod
    def _create_field_schema(field_info: dict[str, Any], field_name: str | None = None) -> dict[str, Any]:
        """Create schema for a single field based on metadata.

        Args:
            field_info: Field metadata from Oracle WMS API.
            field_name: Optional field name for type inference.

        Returns:
            JSON schema definition for the field.

        """
        field_type = field_info.get("type", "string")
        field_format = field_info.get("format")
        nullable = field_info.get("nullable", True)

        # Get complete Singer schema from type mapping (includes format)
        from flext_tap_oracle_wms.type_mapping import get_singer_type_with_metadata

        field_schema = get_singer_type_with_metadata(
            field_type,
            field_name=field_name,
            format_hint=field_format,
        )

        # Apply nullable constraint if needed
        if nullable and "type" in field_schema:
            current_type = field_schema["type"]
            if isinstance(current_type, str) and current_type != "null":
                field_schema["type"] = [current_type, "null"]
            elif isinstance(current_type, list) and "null" not in current_type:
                field_schema["type"] = [*current_type, "null"]

        # Add constraints if present
        if "maxLength" in field_info:
            field_schema["maxLength"] = field_info["maxLength"]
        if "minLength" in field_info:
            field_schema["minLength"] = field_info["minLength"]
        if "pattern" in field_info:
            field_schema["pattern"] = field_info["pattern"]

        return field_schema

    @staticmethod
    def _generate_empty_schema() -> dict[str, Any]:
        """Generate empty schema for entities without field metadata.

        Returns:
            Basic schema dictionary with minimal required fields

        """
        return {
            "type": "object",
            "properties": {
                "id": {"type": ["string", "null"]},
                "_sdc_extracted_at": {
                    "type": "string",
                    "format": "date-time",
                },
            },
            "additionalProperties": True,
        }

    def _infer_field_type(self, value: Any) -> dict[str, Any]:
        """Infer field type from sample value.

        Args:
            value: Sample value to analyze for type inference

        Returns:
            Schema dictionary with inferred type information

        """
        # Handle each type with proper type checking - reduces to 6 returns
        value_type = type(value)

        # Handle primitive types in single mapping
        simple_type_map = {
            type(None): "null",
            bool: "boolean",
            int: "integer",
            float: "number",
        }

        if value_type in simple_type_map:
            return {"type": simple_type_map[value_type]}
        if value_type is str:
            return self._infer_string_schema(value)
        if value_type is list:
            return self._infer_array_schema(value)
        if value_type is dict:
            return self._infer_object_schema(value)
        # Unknown type - default to string
        return {"type": "string"}

    @staticmethod
    def _infer_string_schema(value: str) -> dict[str, Any]:
        """Infer string type with format detection.

        Args:
            value: String value to analyze for format detection

        Returns:
            Schema dictionary with string type and optional format

        """
        if SchemaGenerator._looks_like_datetime(value):
            return {"type": "string", "format": "date-time"}
        if SchemaGenerator._looks_like_date(value):
            return {"type": "string", "format": "date"}
        return {"type": "string"}

    def _infer_array_schema(self, value: list[Any]) -> dict[str, Any]:
        """Infer array type schema.

        Args:
            value: Array value to analyze for schema inference

        Returns:
            Schema dictionary with array type and item type

        """
        if value:
            # Infer from first item
            item_type = self._infer_field_type(value[0])
            return {"type": "array", "items": item_type}
        return {"type": "array", "items": {"type": "string"}}

    def _infer_object_schema(self, value: dict[str, Any]) -> dict[str, Any]:
        """Infer object type schema.

        Args:
            value: Object value to analyze for schema inference

        Returns:
            Schema dictionary with object type and properties

        """
        properties = {k: self._infer_field_type(v) for k, v in value.items()}
        return {"type": "object", "properties": properties}

    @staticmethod
    def _looks_like_datetime(value: str) -> bool:
        """Check if string value looks like a datetime.

        Args:
            value: String value to check

        Returns:
            True if value matches datetime pattern, False otherwise

        """
        datetime_patterns = [
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        ]
        return any(re.search(pattern, value) for pattern in datetime_patterns)

    @staticmethod
    def _looks_like_date(value: str) -> bool:
        """Check if string value looks like a date.

        Args:
            value: String value to check

        Returns:
            True if value matches date pattern, False otherwise

        """
        date_pattern = r"\d{4}-\d{2}-\d{2}$"
        return bool(re.search(date_pattern, value))

    @staticmethod
    def _raise_schema_error(message: str, _cause: Exception | None = None) -> None:
        """Raise schema generation error with proper error handling.

        Args:
            message: Error message to include
            cause: Optional original exception that caused the error

        Raises:
            SchemaGenerationError: Always raises with the provided message

        """
        raise SchemaGenerationError(message)
