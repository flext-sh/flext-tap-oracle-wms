"""Schema generator implementation following SOLID principles.

This module focuses solely on schema generation operations,
following the Single Responsibility Principle.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import re
from typing import Any

from flext_observability.logging import get_logger

from flext_tap_oracle_wms.interfaces import SchemaGeneratorInterface
from flext_tap_oracle_wms.type_mapping import convert_metadata_type_to_singer

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

            # Build schema properties
            properties = {}
            required_fields = []

            # Oracle WMS metadata format: fields must be a dict
            if not isinstance(fields, dict):
                SchemaGenerator._raise_schema_error(
                    f"Fields must be a dict, got {type(fields).__name__}",
                )

            for field_name, field_info in fields.items():
                if not field_name:
                    continue

                field_schema = SchemaGenerator._create_field_schema(field_info)
                properties[field_name] = field_schema

                # Check if field is required
                if field_info.get("required", False):
                    required_fields.append(field_name)

            # Build complete schema
            schema = {
                "type": "object",
                "properties": properties,
                "additionalProperties": True,  # Allow extra fields like 'url'
            }

            if required_fields:
                schema["required"] = required_fields

            return schema  # noqa: TRY300

        except Exception as e:
            logger.exception("Schema generation from metadata failed")
            SchemaGenerator._raise_schema_error(f"Schema generation failed: {e}", e)
            return {}  # Unreachable but satisfies mypy

    def generate_metadata_schema_with_flattening(
        self, metadata: dict[str, Any],
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

            # Return flattened schema
            return {  # noqa: TRY300
                "type": "object",
                "properties": flattened_properties,
            }

        except Exception as e:
            logger.exception("Flattened schema generation failed")
            msg = f"Flattened schema generation failed: {e}"
            raise SchemaGenerationError(
                msg,
            ) from e

    def flatten_complex_objects(
        self, data: dict[str, Any], prefix: str = "", separator: str = "_",
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

    @staticmethod
    def _create_field_schema(field_info: dict[str, Any]) -> dict[str, Any]:
        """Create schema for a single field based on metadata.

        Args:
            field_info: Field metadata from Oracle WMS API.

        Returns:
            JSON schema definition for the field.

        """
        field_type = field_info.get("type", "string")
        field_format = field_info.get("format")
        nullable = field_info.get("nullable", True)

        # Convert WMS type to Singer schema type
        schema_type = convert_metadata_type_to_singer(field_type, field_format)

        # Build field schema
        field_schema: dict[str, Any] = {"type": schema_type}

        # Add format if specified
        if (
            field_format
            and schema_type == "string"
            and field_format in {"date-time", "date", "time"}
        ):
            field_schema["format"] = field_format

        # Handle nullable fields
        if nullable and schema_type != "null":
            field_schema["type"] = [schema_type, "null"]

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

    def infer_schema_from_sample(self, sample_data: dict[str, Any]) -> dict[str, Any]:
        """Infer JSON schema from sample data (fallback method).

        Args:
            sample_data: Sample data from WMS entity.

        Returns:
            Inferred JSON schema dictionary.

        """
        try:
            properties = {}

            for key, value in sample_data.items():
                properties[key] = self._infer_field_type(value)

            return {  # noqa: TRY300
                "type": "object",
                "properties": properties,
                "additionalProperties": True,
            }

        except Exception:
            logger.exception("Schema inference from sample failed")
            return SchemaGenerator._generate_empty_schema()

    def _infer_field_type(self, value: Any) -> dict[str, Any]:  # noqa: PLR0911
        """Infer field type from sample value.

        Args:
            value: Sample value to analyze for type inference

        Returns:
            Schema dictionary with inferred type information

        """
        if value is None:
            return {"type": "null"}
        if isinstance(value, bool):
            return {"type": "boolean"}
        if isinstance(value, int):
            return {"type": "integer"}
        if isinstance(value, float):
            return {"type": "number"}
        if isinstance(value, str):
            return self._infer_string_schema(value)
        if isinstance(value, list):
            return self._infer_array_schema(value)
        if isinstance(value, dict):
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
    def _raise_schema_error(message: str, cause: Exception | None = None) -> None:
        """Raise schema generation error with proper error handling.

        Args:
            message: Error message to include
            cause: Optional original exception that caused the error

        Raises:
            SchemaGenerationError: Always raises with the provided message

        """
        if cause:
            raise SchemaGenerationError(message) from cause
        raise SchemaGenerationError(message)
