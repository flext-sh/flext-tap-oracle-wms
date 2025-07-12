"""Dynamic entity discovery for Oracle WMS - SOLID Refactored.

import asyncio  # TODO:
            Move import to module level
This module provides a high-level facade for entity discovery operations,
orchestrating the various components following SOLID principles.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import asyncio
from typing import Any

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

from flext_tap_oracle_wms.auth import get_wms_headers
from flext_tap_oracle_wms.cache_manager import CacheManager
from flext_tap_oracle_wms.entity_discovery import EntityDiscovery as EntityDiscoveryCore
from flext_tap_oracle_wms.schema_generator import SchemaGenerator as SchemaGeneratorCore

logger = get_logger(__name__)


# Re-export exceptions for backward compatibility
class WMSDiscoveryError(Exception):
    """Base exception for WMS discovery errors."""


class EntityDiscoveryError(WMSDiscoveryError):
    """Exception raised when entity discovery fails."""


class EntityDescriptionError(WMSDiscoveryError):
    """Exception raised when entity description fails."""


class SchemaGenerationError(WMSDiscoveryError):
    """Exception raised when schema generation fails."""


class DataTypeConversionError(WMSDiscoveryError):
    """Exception raised when data type conversion fails."""


class NetworkError(WMSDiscoveryError):
    """Exception raised for network-related errors."""


class AuthenticationError(WMSDiscoveryError):
    """Exception raised for authentication errors."""


class EntityDiscovery:
    """Facade for WMS entity discovery operations following SOLID principles.

    This class orchestrates entity discovery, caching, and schema generation
    while delegating specific responsibilities to specialized components.
    Follows the Facade pattern and Dependency Inversion Principle.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize entity discovery facade.

        Args:
            config: Configuration dictionary for entity discovery.

        """
        logger.debug("Initializing SOLID-compliant entity discovery system")
        logger.debug("Config keys: %s", list(config.keys()))

        self.config = config
        self.headers = get_wms_headers(config)

        # Dependency injection - create specialized components
        self._cache_manager = CacheManager(config)
        self._entity_discovery = EntityDiscoveryCore(
            config,
            self._cache_manager,
            self.headers,
        )
        self._schema_generator = SchemaGeneratorCore(config)

        # Legacy compatibility properties
        self.base_url = config["base_url"].rstrip("/")
        self.api_version = config.get("wms_api_version", "v10")

    @property
    def entity_endpoint(self) -> str:
        """Get the Oracle WMS entity endpoint URL.

        Returns:
            Complete URL for entity API endpoint.

        """
        return f"{self.base_url}/wms/lgfapi/{self.api_version}/entity/"

    async def discover_entities(self) -> dict[str, str]:
        """Discover available entities from Oracle WMS API.

        Returns:
            Dictionary mapping entity names to their API endpoints.

        """
        return await self._entity_discovery.discover_entities()

    def discover_entities_sync(self) -> dict[str, str]:
        """Discover entities using synchronous wrapper.

        Returns:
            Dictionary mapping entity names to their API endpoints.

        """
        # Use asyncio.run to execute async method in sync context
        return asyncio.run(self._entity_discovery.discover_entities())

    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration criteria.

        Args:
            entities: Dictionary of entity names to endpoints.

        Returns:
            Filtered dictionary of entities.

        """
        return self._entity_discovery.filter_entities(entities)

    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get metadata description for a specific entity.

        Args:
            entity_name: Name of the entity to describe.

        Returns:
            Entity metadata dictionary or None if not found.

        Raises:
            EntityDescriptionError: If entity description fails.

        """
        try:
            return await self._entity_discovery.describe_entity(entity_name)
        except Exception as e:
            logger.exception("Entity description failed for %s", entity_name)
            msg = f"Entity description failed for {entity_name}: {e}"
            raise EntityDescriptionError(msg) from e

    def describe_entity_sync(self, entity_name: str) -> dict[str, Any] | None:
        """Describe entity using synchronous wrapper.

        Args:
            entity_name: Name of the entity to describe.

        Returns:
            Entity metadata dictionary or None if not found.

        Raises:
            EntityDescriptionError: If entity description fails.

        """
        try:
            # Use asyncio.run to execute async method in sync context
            return asyncio.run(self._entity_discovery.describe_entity(entity_name))
        except Exception as e:
            logger.exception("Entity description failed for %s", entity_name)
            msg = f"Entity description failed for {entity_name}: {e}"
            raise EntityDescriptionError(msg) from e

    # 🚨 METHOD PERMANENTLY DELETED: get_entity_sample
    # This method is FORBIDDEN - schema discovery uses ONLY API metadata describe

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cache entries by type.

        Args:
            cache_type: Type of cache to clear, defaults to "all".

        """
        self._cache_manager.clear_cache(cache_type)
        logger.info("Cleared %s cache", cache_type)

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache statistics.

        """
        return self._cache_manager.get_cache_stats()


class SchemaGenerator:
    """Schema generator facade for backward compatibility.

    Delegates to the specialized schema generator component while maintaining
    the original interface for existing code.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize schema generator facade.

        Args:
            config: Configuration dictionary for schema generation.

        """
        self.config = config
        self._schema_generator = SchemaGeneratorCore(config)

        # Backward compatibility attributes
        self.enable_flattening = config.get("flattening_enabled", True)
        self.flatten_id_objects = True  # Default behavior
        self.max_flatten_depth = config.get("flattening_max_depth", 3)

    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate JSON schema from Oracle WMS API metadata.

        Args:
            metadata: API metadata describing entity structure.

        Returns:
            JSON schema dictionary for Singer protocol.

        Raises:
            SchemaGenerationError: If schema generation fails.

        """
        # 🚨 CRITICAL MANDATORY VALIDATION: Enforce metadata-only mode
        # Schema generation uses EXCLUSIVELY API metadata - no configuration needed
        logger.info("Generating schema using ONLY API metadata describe")

        try:
            return self._schema_generator.generate_from_metadata(metadata)
        except Exception as e:
            logger.exception("Schema generation from metadata failed")
            msg = f"Schema generation from metadata failed: {e}"
            raise SchemaGenerationError(msg) from e

    # 🚨 METHODS PERMANENTLY DELETED: generate_from_sample and generate_hybrid_schema
    # These methods are FORBIDDEN - schema generation uses ONLY API metadata describe

    def generate_metadata_schema_with_flattening(
        self, metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate flattened JSON schema from Oracle WMS API metadata.

        Args:
            metadata: API metadata describing entity structure.

        Returns:
            Flattened JSON schema dictionary for Singer protocol.

        Raises:
            SchemaGenerationError: If schema generation fails.

        """
        # Schema generation uses EXCLUSIVELY API metadata describe
        logger.info("Generating schema with flattening using ONLY API metadata")

        try:
            return self._schema_generator.generate_metadata_schema_with_flattening(
                metadata,
            )
        except Exception as e:
            logger.exception("Schema generation with flattening failed")
            msg = f"Schema generation with flattening failed: {e}"
            raise SchemaGenerationError(msg) from e

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
        try:
            return self._schema_generator.flatten_complex_objects(
                data,
                prefix,
                separator,
            )
        except Exception:
            logger.exception("Object flattening failed")
            # Return original data if flattening fails
            return data

    def _flatten_complex_objects(
        self, data: dict[str, Any], prefix: str = "", separator: str = "_",
    ) -> dict[str, Any]:
        return self.flatten_complex_objects(data, prefix, separator)

    @staticmethod
    def _infer_type(value: object) -> dict[str, Any]:
        # Handle None separately
        if value is None:
            return {"type": "null"}

        # Type mapping for different Python types
        type_mapping = [
            (bool, "boolean"),
            (int, "integer"),
            (float, "number"),
            (str, "string"),
            (list, "array"),
            (dict, "object"),
        ]

        # Check value against type mapping
        for python_type, schema_type in type_mapping:
            if isinstance(value, python_type):
                return {"type": schema_type}

        # Default fallback
        return {"type": "string"}

    @staticmethod
    def _merge_types(
        type1: dict[str, Any], type2: dict[str, Any],
    ) -> dict[str, Any]:
        # If same type, return it
        if type1.get("type") == type2.get("type"):
            return type1
        # Different types - use anyOf structure
        return {"anyOf": [type1, type2]}

    @staticmethod
    def _create_property_from_field(field_info: dict[str, Any]) -> dict[str, Any]:
        field_type = field_info.get("type", "string")
        required = field_info.get("required", True)

        if not required:
            return {"type": [field_type, "null"]}
        return {"type": field_type}
