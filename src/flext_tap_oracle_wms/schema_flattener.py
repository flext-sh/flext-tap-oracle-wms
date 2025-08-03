"""Schema flattener functionality for Oracle WMS tap."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

# Removed circular dependency - use DI pattern
from flext_core import TAnyDict, get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


# SOLID REFACTORING: Parameter Object Pattern to reduce method parameter count
@dataclass
class SchemaFlattenerConfig:
    """Configuration for schema flattening operations.

    SOLID REFACTORING: Reduces parameter count in __init__ method
    using Parameter Object Pattern.
    """

    enabled: bool = True
    max_depth: int = 5
    separator: str = "_"
    flatten_arrays: bool = False


class SchemaFlattener:
    """Flatten nested JSON schemas for Oracle WMS integration.

    Follows SRP by focusing solely on schema flattening operations.
    """

    def __init__(self, config: SchemaFlattenerConfig | None = None) -> None:
        """Initialize schema flattener.

        SOLID REFACTORING: Reduced parameter count from 6 to 1 using
        Parameter Object Pattern.

        Args:
            config: Configuration object for schema flattening

        """
        config = config or SchemaFlattenerConfig()

        self.enabled = config.enabled
        self.max_depth = config.max_depth
        self.separator = config.separator
        self.flatten_arrays = config.flatten_arrays

        if not self.enabled:
            logger.warning("Schema flattening is DISABLED")

    def flatten_schema(self, schema: TAnyDict) -> TAnyDict:
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

        properties = schema.get("properties")
        if not isinstance(properties, dict):
            return schema
        flattened_properties = self._flatten_properties(properties, depth=0)

        return {
            **schema,
            "properties": flattened_properties,
        }

    def flatten_record(self, record: TAnyDict) -> TAnyDict:
        """Flatten a data record.

        Args:
            record: The record to flatten

        Returns:
            Flattened record

        """
        if not self.enabled:
            return record

        return self._flatten_data(record, depth=0)

    def deflate_record(self, record: TAnyDict) -> TAnyDict:
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

    def get_flattening_config(self) -> TAnyDict:
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

    def validate_schema_compatibility(self, schema: TAnyDict) -> list[str]:
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

        properties = schema.get("properties")
        if isinstance(properties, dict):
            self._check_properties_warnings(
                properties,
                warnings,
                depth=0,
                path="",
            )

        return warnings

    def _flatten_properties(
        self,
        properties: TAnyDict,
        depth: int = 0,
        prefix: str = "",
    ) -> TAnyDict:
        """Flatten properties recursively.

        SOLID REFACTORING: Uses Template Method Pattern to eliminate duplication.
        """
        return self._flatten_generic(
            properties,
            depth,
            prefix,
            "properties",
            self._process_single_property,
        )

    def _flatten_generic(
        self,
        data_dict: TAnyDict,
        depth: int,
        prefix: str,
        data_type: str,
        processor_func: Callable[..., Any],
    ) -> TAnyDict:
        """Template Method Pattern: Generic flattening algorithm.

        SOLID REFACTORING: Eliminates 28 lines of duplication between
        _flatten_properties and _flatten_data using Template Method Pattern.
        """
        # Guard Clause: Early return for max depth
        if depth >= self.max_depth:
            logger.warning(
                "Maximum flattening depth (%d) reached for %s",
                self.max_depth,
                data_type,
            )
            return data_dict

        flattened: TAnyDict = {}

        for key, value in data_dict.items():
            new_key = f"{prefix}{self.separator}{key}" if prefix else key

            # Template Method Pattern: Delegate processing to specific function
            processor_func(flattened, key, value, new_key, depth)

        return flattened

    def _process_single_property(
        self,
        flattened: dict[str, object],
        key: str,
        value: object,
        new_key: str,
        depth: int,
    ) -> None:
        """Process a single property using Guard Clauses.

        SOLID REFACTORING: Extracted method to reduce nesting and complexity.
        """
        # Guard Clause: Handle object type
        if self._is_nested_object_property(value) and isinstance(value, dict):
            self._handle_nested_object_property(flattened, value, new_key, depth)
            return

        # Guard Clause: Handle array type
        if self._is_flattened_array_property(value) and isinstance(value, dict):
            self._handle_array_property(flattened, value, new_key, depth)
            return

        # Default case: simple property
        flattened[new_key] = value

    def _is_nested_object_property(self, value: object) -> bool:
        """Check if property is a nested object."""
        return (
            isinstance(value, dict)
            and value.get("type") == "object"
            and "properties" in value
        )

    def _is_flattened_array_property(self, value: object) -> bool:
        """Check if property is a flattened array."""
        return (
            isinstance(value, dict)
            and value.get("type") == "array"
            and self.flatten_arrays
        )

    def _handle_nested_object_property(
        self,
        flattened: TAnyDict,
        value: TAnyDict,
        new_key: str,
        depth: int,
    ) -> None:
        """Handle nested object property."""
        properties = value.get("properties")
        if isinstance(properties, dict):
            nested = self._flatten_properties(
                properties,
                depth + 1,
                new_key,
            )
            flattened.update(nested)

    def _handle_array_property(
        self,
        flattened: TAnyDict,
        value: TAnyDict,
        new_key: str,
        depth: int,
    ) -> None:
        """Handle array property using Guard Clauses."""
        # Guard Clause: No items
        if "items" not in value or not isinstance(value["items"], dict):
            flattened[new_key] = value
            return

        items_type = value["items"].get("type")

        # Guard Clause: Not object array
        if items_type != "object" or "properties" not in value["items"]:
            flattened[new_key] = value
            return

        # Flatten array of objects
        nested = self._flatten_properties(
            value["items"]["properties"],
            depth + 1,
            f"{new_key}{self.separator}items",
        )
        flattened.update(nested)

    def _flatten_data(
        self,
        data: TAnyDict,
        depth: int = 0,
        prefix: str = "",
    ) -> TAnyDict:
        """Flatten data record recursively.

        SOLID REFACTORING: Uses Template Method Pattern to eliminate duplication.
        """
        return self._flatten_generic(
            data,
            depth,
            prefix,
            "data",
            self._process_single_data_item,
        )

    def _process_single_data_item(
        self,
        flattened: dict[str, object],
        key: str,
        value: object,
        new_key: str,
        depth: int,
    ) -> None:
        """Process a single data item using Guard Clauses.

        SOLID REFACTORING: Extracted method to eliminate level-5 deep nesting.
        """
        # Guard Clause: Handle nested dict
        if isinstance(value, dict):
            nested = self._flatten_data(value, depth + 1, new_key)
            flattened.update(nested)
            return

        # Guard Clause: Handle list array
        if isinstance(value, list) and self.flatten_arrays:
            self._handle_data_array(flattened, value, new_key, depth)
            return

        # Default case: simple value
        flattened[new_key] = value

    def _handle_data_array(
        self,
        flattened: TAnyDict,
        value: list[Any],
        new_key: str,
        depth: int,
    ) -> None:
        """Handle array data using Guard Clauses.

        SOLID REFACTORING: Extracted method eliminates level-5 nesting.
        """
        # Guard Clause: Empty array
        if not value:
            flattened[new_key] = value
            return

        # Process each array item
        for i, item in enumerate(value):
            item_key = f"{new_key}{self.separator}items{self.separator}{i}"

            # Guard Clause: Nested dict item
            if isinstance(item, dict):
                nested = self._flatten_data(item, depth + 1, item_key)
                flattened.update(nested)
            else:
                # Simple array item
                flattened[item_key] = item

    def _deflate_data(self, data: TAnyDict) -> TAnyDict:
        """Deflate (unflatten) a flattened data record.

        SOLID REFACTORING: Reduced complexity using Extract Method Pattern.
        """
        if not data:
            return data

        deflated: TAnyDict = {}

        for key, value in data.items():
            parts = key.split(self.separator)

            # Extract Method: Handle nested structure creation
            target_dict = self._create_nested_structure(deflated, parts[:-1])
            if target_dict is None:
                continue  # Skip due to conflict

            # Extract Method: Handle final value assignment
            if not self._assign_final_value(target_dict, parts[-1], value):
                continue  # Skip due to conflict

        return deflated

    def _create_nested_structure(
        self,
        root: TAnyDict,
        parts: list[str],
    ) -> TAnyDict | None:
        """Extract Method: Create nested dictionary structure.

        SOLID REFACTORING: Reduces cyclomatic complexity of _deflate_data.

        Returns:
            Target dictionary for final assignment or None if conflict

        """
        current = root

        for part in parts:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Conflict: trying to make a non-dict into a dict
                logger.warning(
                    f"Key conflict while deflating: key '{part}' already exists "
                    f"as non-dict value",
                )
                return None

            current_part = current[part]
            if isinstance(current_part, dict):
                current = current_part
            else:
                # Safety check - shouldn't happen due to earlier validation
                return None

        return current

    def _assign_final_value(self, target_dict: TAnyDict, key: str, value: Any) -> bool:
        """Extract Method: Assign final value with conflict detection.

        SOLID REFACTORING: Separates final assignment logic.

        Returns:
            True if assignment successful, False if conflict

        """
        if key in target_dict and isinstance(target_dict[key], dict):
            # Conflict: trying to overwrite a dict with a value
            logger.warning(
                f"Key conflict while deflating: key '{key}' already exists as dict",
            )
            return False

        target_dict[key] = value
        return True

    def _check_properties_warnings(
        self,
        properties: dict[str, object],
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
