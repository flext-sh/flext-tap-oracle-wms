"""Oracle WMS Discovery Module.

This module provides entity discovery and schema generation capabilities
for Oracle WMS API integration using flext-core patterns.

REFACTORED: Uses centralized flext-oracle-wms discovery - NO DUPLICATION.
"""

import asyncio
from typing import Any

from flext_observability.structured_logging import get_logger
from flext_oracle_wms import (
    FlextOracleWmsEntityDiscovery,
    FlextOracleWmsEntityNotFoundError,
    FlextOracleWmsError,
)

from flext_tap_oracle_wms.infrastructure.schema_generator import (
    SchemaGenerator as SchemaGeneratorCore,
)
from flext_tap_oracle_wms.interfaces import (
    CacheManagerInterface,
    EntityDiscoveryInterface,
    SchemaGeneratorInterface,
)

logger = get_logger(__name__)

# Use centralized discovery and exceptions - NO DUPLICATION
EntityDiscoveryCore = FlextOracleWmsEntityDiscovery
WMSDiscoveryError = FlextOracleWmsError
EntityDiscoveryError = FlextOracleWmsEntityNotFoundError


class EntityDescriptionError(WMSDiscoveryError):
    """Exception raised when entity description fails."""


class SchemaGenerationError(WMSDiscoveryError):
    """Exception raised when schema generation fails."""


class DataTypeConversionError(WMSDiscoveryError):
    """Exception raised when data type conversion fails."""


class NetworkError(WMSDiscoveryError):
    """Exception raised when network operations fail."""


class AuthenticationError(WMSDiscoveryError):
    """Exception raised when authentication fails."""


class EntityDiscovery(EntityDiscoveryInterface):
    """Entity discovery implementation for Oracle WMS API."""

    def __init__(
        self,
        config: dict[str, Any],
        cache_manager: CacheManagerInterface,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize entity discovery.

        Args:
            config: Configuration dictionary
            cache_manager: Cache manager instance
            headers: Optional headers for API requests

        """
        self.config = config
        self._cache_manager = cache_manager
        self.headers = headers or {}
        self._entity_discovery = EntityDiscoveryCore(config, cache_manager, headers)

    @property
    def entity_endpoint(self) -> str:
        """Get entity endpoint URL."""
        return self._entity_discovery.entity_endpoint

    async def discover_entities(self) -> dict[str, str]:
        """Discover available entities from Oracle WMS API.

        Returns:
            Dictionary mapping entity names to their URLs

        """
        return await self._entity_discovery.discover_entities()

    def discover_entities_sync(self) -> dict[str, str]:
        """Discover entities using synchronous wrapper.

        Returns:
            Dictionary mapping entity names to their URLs

        """
        return asyncio.run(self.discover_entities())

    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration.

        Args:
            entities: Dictionary of all discovered entities

        Returns:
            Filtered dictionary of entities

        """
        return self._entity_discovery.filter_entities(entities)

    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get metadata description for a specific entity.

        Args:
            entity_name: Name of the entity to describe

        Returns:
            Entity metadata dictionary or None if not found

        Raises:
            EntityDescriptionError: If entity description fails

        """
        try:
            return await self._entity_discovery.describe_entity(entity_name)
        except Exception as e:
            logger.exception("Entity description failed for %s", entity_name)
            msg = f"Entity description failed: {e}"
            raise EntityDescriptionError(msg) from e

    def describe_entity_sync(self, entity_name: str) -> dict[str, Any] | None:
        """Describe entity using synchronous wrapper.

        Args:
            entity_name: Name of the entity to describe

        Returns:
            Entity metadata dictionary or None if not found

        """
        try:
            return asyncio.run(self.describe_entity(entity_name))
        except Exception as e:
            logger.exception("Entity description failed for %s", entity_name)
            msg = f"Entity description failed: {e}"
            raise EntityDescriptionError(msg) from e

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cache entries by type.

        Args:
            cache_type: Type of cache to clear, defaults to "all"

        """
        self._cache_manager.clear_cache(cache_type)
        logger.info("Cleared %s cache", cache_type)

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache statistics

        """
        return self._cache_manager.get_cache_stats()


class SchemaGenerator(SchemaGeneratorInterface):
    """Schema generator facade for backward compatibility.

    Delegates to the specialized schema generator component while maintaining
    the original interface for existing code.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize schema generator facade.

        Args:
            config: Configuration dictionary for schema generation

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
            metadata: API metadata describing entity structure

        Returns:
            JSON schema dictionary for Singer protocol

        Raises:
            SchemaGenerationError: If schema generation fails

        """
        # 🚨 CRITICAL MANDATORY VALIDATION: Enforce metadata-only mode
        # Schema generation uses EXCLUSIVELY API metadata - no configuration needed
        logger.info("Generating schema using ONLY API metadata describe")
        try:
            return self._schema_generator.generate_from_metadata(metadata)
        except Exception as e:
            logger.exception("Schema generation from metadata failed")
            msg = f"Schema generation failed: {e}"
            raise SchemaGenerationError(msg) from e

    def generate_metadata_schema_with_flattening(
        self,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate flattened JSON schema from Oracle WMS API metadata.

        Args:
            metadata: API metadata describing entity structure

        Returns:
            Flattened JSON schema dictionary for Singer protocol

        Raises:
            SchemaGenerationError: If schema generation fails

        """
        # Schema generation uses EXCLUSIVELY API metadata describe
        logger.info("Generating schema with flattening using ONLY API metadata")
        try:
            return self._schema_generator.generate_metadata_schema_with_flattening(
                metadata,
            )
        except Exception as e:
            logger.exception("Schema generation with flattening failed")
            msg = f"Schema generation failed: {e}"
            raise SchemaGenerationError(msg) from e

    def flatten_complex_objects(
        self,
        data: dict[str, Any],
        prefix: str = "",
        separator: str = "_",
    ) -> dict[str, Any]:
        """Flatten nested objects for schema processing.

        Args:
            data: Complex nested data structure
            prefix: Prefix for flattened field names
            separator: Separator for flattened field names

        Returns:
            Flattened data structure

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
        self,
        data: dict[str, Any],
        prefix: str = "",
        separator: str = "_",
    ) -> dict[str, Any]:
        """Internal method for flattening complex objects."""
        return self.flatten_complex_objects(data, prefix, separator)

    @staticmethod
    def _infer_type(value: object) -> dict[str, Any]:
        """Infer JSON schema type from Python value.

        Args:
            value: Python value to infer type from

        Returns:
            JSON schema type dictionary

        """
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
        type1: dict[str, Any],
        type2: dict[str, Any],
    ) -> dict[str, Any]:
        """Merge two JSON schema types.

        Args:
            type1: First type dictionary
            type2: Second type dictionary

        Returns:
            Merged type dictionary

        """
        # If same type, return it
        if type1.get("type") == type2.get("type"):
            return type1
        # Different types - use anyOf structure
        return {"anyOf": [type1, type2]}

    @staticmethod
    def _create_property_from_field(field_info: dict[str, Any]) -> dict[str, Any]:
        """Create JSON schema property from field info.

        Args:
            field_info: Field information dictionary

        Returns:
            JSON schema property dictionary

        """
        field_type = field_info.get("type", "string")
        required = field_info.get("required", True)

        if not required:
            return {"type": [field_type, "null"]}
        return {"type": field_type}
