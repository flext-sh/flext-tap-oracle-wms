"""Schema flattener functionality for Oracle WMS tap."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

# Removed circular dependency - use DI pattern
import logging
from typing import Any

logger = logging.getLogger(__name__)


class SchemaFlattener:
    """Flatten nested JSON schemas for Oracle WMS integration.

    Follows SRP by focusing solely on schema flattening operations.
    """

    def __init__(
        self,
        *,  # Force keyword-only arguments
        enabled: bool = True,
        max_depth: int = 5,
        separator: str = "_",
        flatten_arrays: bool = False,
    ) -> None:
        """Initialize schema flattener.

        Args:
            enabled: Whether flattening is enabled
            max_depth: Maximum depth for flattening
            separator: Separator for flattened field names
            flatten_arrays: Whether to flatten array types

        """
        self.enabled = enabled
        self.max_depth = max_depth
        self.separator = separator
        self.flatten_arrays = flatten_arrays

        if not enabled:
            logger.warning("Schema flattening is DISABLED")

    def flatten_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Flatten a JSON schema.

        Args:
            schema: The schema to flatten

        Returns:
            Flattened schema

        """
        if not self.enabled:
            return schema

        if "properties" not in schema:
            return schema

        flattened_properties = self._flatten_properties(schema["properties"], depth=0)

        return {
            **schema,
            "properties": flattened_properties,
        }

    def flatten_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Flatten a data record.

        Args:
            record: The record to flatten

        Returns:
            Flattened record

        """
        if not self.enabled:
            return record

        return self._flatten_data(record, depth=0)

    def deflate_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Deflate (unflatten) a flattened data record.

        Args:
            record: The flattened record to deflate

        Returns:
            Deflated (nested) record

        Raises:
            ValueError: If there are conflicting keys during deflation

        """
        if not self.enabled:
            return record

        return self._deflate_data(record)

    def get_flattening_config(self) -> dict[str, Any]:
        """Get current flattening configuration.

        Returns:
            Configuration dictionary

        """
        return {
            "enabled": self.enabled,
            "max_depth": self.max_depth,
            "separator": self.separator,
            "flatten_arrays": self.flatten_arrays,
        }

    def validate_schema_compatibility(self, schema: dict[str, Any]) -> list[str]:
        """Validate schema compatibility with flattening.

        Args:
            schema: Schema to validate

        Returns:
            List of warning messages

        """
        if not self.enabled:
            return []

        warnings: list[str] = []

        if "properties" not in schema:
            return warnings

        self._check_properties_warnings(
            schema["properties"],
            warnings,
            depth=0,
            path="",
        )

        return warnings

    def _flatten_properties(
        self,
        properties: dict[str, Any],
        depth: int = 0,
        prefix: str = "",
    ) -> dict[str, Any]:
        """Flatten properties recursively."""
        if depth >= self.max_depth:
            logger.warning(
                "Maximum flattening depth (%d) reached for properties",
                self.max_depth,
            )
            return properties

        flattened = {}

        for key, value in properties.items():
            new_key = f"{prefix}{self.separator}{key}" if prefix else key

            if isinstance(value, dict) and value.get("type") == "object":
                if "properties" in value:
                    # Recursively flatten nested object
                    nested = self._flatten_properties(
                        value["properties"],
                        depth + 1,
                        new_key,
                    )
                    flattened.update(nested)
                else:
                    flattened[new_key] = value
            elif (
                isinstance(value, dict)
                and value.get("type") == "array"
                and self.flatten_arrays
            ):
                # Handle array flattening if enabled
                if "items" in value and isinstance(value["items"], dict):
                    items_type = value["items"].get("type")
                    if items_type == "object" and "properties" in value["items"]:
                        # Flatten array of objects
                        nested = self._flatten_properties(
                            value["items"]["properties"],
                            depth + 1,
                            f"{new_key}{self.separator}items",
                        )
                        flattened.update(nested)
                    else:
                        flattened[new_key] = value
                else:
                    flattened[new_key] = value
            else:
                flattened[new_key] = value

        return flattened

    def _flatten_data(
        self,
        data: dict[str, Any],
        depth: int = 0,
        prefix: str = "",
    ) -> dict[str, Any]:
        """Flatten data record recursively."""
        if depth >= self.max_depth:
            logger.warning(
                "Maximum flattening depth (%d) reached for data",
                self.max_depth,
            )
            return data

        flattened = {}

        for key, value in data.items():
            new_key = f"{prefix}{self.separator}{key}" if prefix else key

            if isinstance(value, dict):
                # Recursively flatten nested dict
                nested = self._flatten_data(value, depth + 1, new_key)
                flattened.update(nested)
            elif isinstance(value, list) and self.flatten_arrays:
                # Handle array flattening if enabled
                if not value:
                    # Empty array should be kept as-is
                    flattened[new_key] = value
                else:
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            nested = self._flatten_data(
                                item,
                                depth + 1,
                                f"{new_key}{self.separator}items{self.separator}{i}",
                            )
                            flattened.update(nested)
                        else:
                            flattened[
                                f"{new_key}{self.separator}items{self.separator}{i}"
                            ] = item
            else:
                flattened[new_key] = value

        return flattened

    def _deflate_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Deflate (unflatten) a flattened data record."""
        if not data:
            return data

        deflated: dict[str, Any] = {}

        for key, value in data.items():
            # Split the key by separator to rebuild nested structure
            parts = key.split(self.separator)

            # Navigate/create nested structure
            current = deflated
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Conflict: trying to make a non-dict into a dict
                    msg = (
                        f"Key conflict while deflating: key '{part}' already exists "
                        f"as non-dict value"
                    )
                    logger.warning(msg)
                    # Skip this key to avoid the conflict
                    continue
                current = current[part]

            # Set the final value
            final_key = parts[-1]
            if final_key in current and isinstance(current[final_key], dict):
                # Conflict: trying to overwrite a dict with a value
                msg = (
                    f"Key conflict while deflating: key '{final_key}' already exists "
                    f"as dict"
                )
                logger.warning(msg)
                # Skip this assignment to avoid the conflict
                continue
            current[final_key] = value

        return deflated

    def _check_properties_warnings(
        self,
        properties: dict[str, Any],
        warnings: list[str],
        depth: int,
        path: str,
    ) -> None:
        """Check for warnings in properties."""
        for key, value in properties.items():
            current_path = f"{path}.{key}" if path else key

            # Check for separator conflicts
            if self.separator in key:
                warnings.append(
                    f"Property '{current_path}' contains separator '{self.separator}'",
                )

            # Check depth
            if depth >= self.max_depth:
                warnings.append(
                    f"Property '{current_path}' exceeds max_depth ({self.max_depth})",
                )
                continue

            # Recursively check nested objects
            if (
                isinstance(value, dict)
                and value.get("type") == "object"
                and "properties" in value
            ):
                self._check_properties_warnings(
                    value["properties"],
                    warnings,
                    depth + 1,
                    current_path,
                )
