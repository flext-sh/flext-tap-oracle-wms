"""Dynamic entity discovery for Oracle WMS - SOLID Refactored.

This module provides a high-level facade for entity discovery operations,
orchestrating the various components following SOLID principles.
"""

from __future__ import annotations

import logging
from typing import Any

from .auth import get_wms_headers
from .cache_manager import CacheManager
from .entity_discovery import EntityDiscovery as EntityDiscoveryCore
from .schema_generator import SchemaGenerator as SchemaGeneratorCore

logger = logging.getLogger(__name__)


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
        """Initialize entity discovery facade with dependency injection.

        Args:
        ----
            config: Configuration dictionary

        """
        logger.debug("Initializing SOLID-compliant entity discovery system")
        logger.debug("Config keys: %s", list(config.keys()))

        self.config = config
        self.headers = get_wms_headers(config)

        # Dependency injection - create specialized components
        self._cache_manager = CacheManager(config)
        self._entity_discovery = EntityDiscoveryCore(
            config, self._cache_manager, self.headers
        )
        self._schema_generator = SchemaGeneratorCore(config)

        # Legacy compatibility properties
        self.base_url = config["base_url"].rstrip("/")
        self.api_version = config.get("wms_api_version", "v10")

    @property
    def entity_endpoint(self) -> str:
        """Get the entity discovery endpoint for backward compatibility."""
        return f"{self.base_url}/wms/lgfapi/{self.api_version}/entity/"

    async def discover_entities(self) -> dict[str, str]:
        """Discover all available entities from WMS API.

        Delegates to the specialized entity discovery component.

        Returns
        -------
            Dictionary mapping entity names to their API URLs

        """
        return await self._entity_discovery.discover_entities()

    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration.

        Delegates to the specialized entity discovery component.

        Args:
        ----
            entities: Dictionary of discovered entities

        Returns:
        -------
            Filtered dictionary of entities

        """
        return self._entity_discovery.filter_entities(entities)

    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get metadata description for a specific entity.

        Delegates to the specialized entity discovery component.

        Args:
        ----
            entity_name: Name of the entity to describe

        Returns:
        -------
            Entity metadata dictionary or None if not found

        """
        try:
            return await self._entity_discovery.describe_entity(entity_name)
        except Exception as e:
            logger.exception("Entity description failed for %s", entity_name)
            msg = f"Entity description failed for {entity_name}: {e}"
            raise EntityDescriptionError(msg) from e

    # 🚨 METHOD PERMANENTLY DELETED: get_entity_sample
    # This method is FORBIDDEN - schema discovery uses ONLY API metadata describe

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cached data.

        Delegates to the cache manager.

        Args:
        ----
            cache_type: Type of cache to clear ('all', 'entity', 'schema', 'metadata')

        """
        self._cache_manager.clear_cache(cache_type)
        logger.info("Cleared %s cache", cache_type)

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Delegates to the cache manager.

        Returns
        -------
            Dictionary with cache statistics

        """
        return self._cache_manager.get_cache_stats()


class SchemaGenerator:
    """Schema generator facade for backward compatibility.

    Delegates to the specialized schema generator component while maintaining
    the original interface for existing code.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize schema generator facade."""
        self.config = config
        self._schema_generator = SchemaGeneratorCore(config)

        # Backward compatibility attributes
        self.enable_flattening = config.get("flattening_enabled", True)
        self.flatten_id_objects = True  # Default behavior
        self.max_flatten_depth = config.get("flattening_max_depth", 3)

    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate schema from API metadata ONLY - NEVER uses samples."""
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
        self, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate schema from API metadata ONLY with flattening support.

        🚨 CRITICAL ENFORCEMENT: Uses ONLY API describe metadata
        NEVER, NEVER, NEVER uses any sample data - that is FORBIDDEN
        """
        # Schema generation uses EXCLUSIVELY API metadata describe
        logger.info("Generating schema with flattening using ONLY API metadata")

        try:
            return self._schema_generator.generate_metadata_schema_with_flattening(
                metadata
            )
        except Exception as e:
            logger.exception("Schema generation with flattening failed")
            msg = f"Schema generation with flattening failed: {e}"
            raise SchemaGenerationError(msg) from e

    def flatten_complex_objects(
        self, data: dict[str, Any], prefix: str = "", separator: str = "_"
    ) -> dict[str, Any]:
        """Flatten nested objects for schema consistency."""
        try:
            return self._schema_generator.flatten_complex_objects(
                data, prefix, separator
            )
        except Exception:
            logger.exception("Object flattening failed")
            # Return original data if flattening fails
            return data

    def _flatten_complex_objects(
        self, data: dict[str, Any], prefix: str = "", separator: str = "_"
    ) -> dict[str, Any]:
        """Legacy private method for backward compatibility."""
        return self.flatten_complex_objects(data, prefix, separator)

    def _infer_type(self, value: object) -> dict[str, Any]:
        """Legacy private method for type inference - backward compatibility."""
        # Simple type inference for backward compatibility
        if value is None:
            return {"type": "null"}
        if isinstance(value, bool):
            return {"type": "boolean"}
        if isinstance(value, int):
            return {"type": "integer"}
        if isinstance(value, float):
            return {"type": "number"}
        if isinstance(value, str):
            return {"type": "string"}
        if isinstance(value, list):
            return {"type": "array"}
        if isinstance(value, dict):
            return {"type": "object"}
        return {"type": "string"}

    def _merge_types(
        self, type1: dict[str, Any], type2: dict[str, Any]
    ) -> dict[str, Any]:
        """Legacy private method for type merging - backward compatibility."""
        # If same type, return it
        if type1.get("type") == type2.get("type"):
            return type1
        # Different types - use anyOf structure
        return {"anyOf": [type1, type2]}

    def _create_property_from_field(
        self, field_name: str, field_info: dict[str, Any]
    ) -> dict[str, Any]:
        """Legacy private method for property creation - backward compatibility."""
        field_type = field_info.get("type", "string")
        required = field_info.get("required", True)

        if not required:
            return {"type": [field_type, "null"]}
        return {"type": field_type}
