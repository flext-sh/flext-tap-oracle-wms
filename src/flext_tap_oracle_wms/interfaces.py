"""Interface definitions for Oracle WMS Tap following SOLID principles.

This module defines the contracts (interfaces) that components must implement,
promoting loose coupling and high cohesion.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EntityDiscoveryInterface(ABC):
    """Interface for entity discovery operations."""

    @abstractmethod
    async def discover_entities(self) -> dict[str, str]:
        """Discover available entities from Oracle WMS API.

        Returns:
            Dictionary mapping entity names to their API endpoints.

        """
        raise NotImplementedError

    @abstractmethod
    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get metadata description for a specific entity.

        Args:
            entity_name: Name of the entity to describe.

        Returns:
            Entity metadata dictionary or None if not found.

        """
        raise NotImplementedError

    # 🚨 METHOD PERMANENTLY DELETED: get_entity_sample
    # This method is FORBIDDEN - schema discovery uses ONLY API metadata describe

    @abstractmethod
    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration criteria.

        Args:
            entities: Dictionary of entity names to endpoints.

        Returns:
            Filtered dictionary of entities.

        """
        raise NotImplementedError


class SchemaGeneratorInterface(ABC):
    """Interface for schema generation operations."""

    @abstractmethod
    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate JSON schema from API metadata.

        Args:
            metadata: API metadata describing entity structure.

        Returns:
            JSON schema dictionary for Singer protocol.

        """
        raise NotImplementedError

    # Note: Sample-based generation is forbidden for security
    # These methods are FORBIDDEN and have been permanently deleted
    # Any implementation attempting to use samples will fail

    @abstractmethod
    def flatten_complex_objects(self, data: dict[str, Any]) -> dict[str, Any]:
        """Flatten nested objects for schema generation.

        Args:
            data: Complex nested data structure.

        Returns:
            Flattened data structure.

        """
        raise NotImplementedError


class CacheManagerInterface(ABC):
    """Interface for cache management operations."""

    @abstractmethod
    def get_cached_value(self, key: str) -> object | None:
        """Retrieve a cached value by key.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found.

        """
        raise NotImplementedError

    @abstractmethod
    def set_cached_value(self, key: str, value: object, ttl: int | None = None) -> None:
        """Store a value in cache with optional TTL.

        Args:
            key: Cache key to store under.
            value: Value to cache.
            ttl: Optional time-to-live in seconds.

        """
        raise NotImplementedError

    @abstractmethod
    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cache entries.

        Args:
            cache_type: Type of cache to clear, defaults to "all".

        """
        raise NotImplementedError

    @abstractmethod
    def is_cache_valid(self, key: str, ttl: int) -> bool:
        """Check if a cache entry is still valid.

        Args:
            key: Cache key to check.
            ttl: Time-to-live threshold in seconds.

        Returns:
            True if cache entry is valid, False otherwise.

        """
        raise NotImplementedError

    @abstractmethod
    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache hit/miss statistics and sizes.

        """
        raise NotImplementedError


class TypeMapperInterface(ABC):
    """Interface for type mapping operations."""

    @abstractmethod
    def convert_metadata_type_to_singer(
        self,
        metadata_type: str | None,
        column_name: str = "",
        max_length: int | None = None,
    ) -> dict[str, Any]:
        """Convert Oracle WMS metadata type to Singer JSON schema type.

        Args:
            metadata_type: Type from Oracle WMS API metadata.
            column_name: Name of the column for context.
            max_length: Maximum length constraint if applicable.

        Returns:
            Singer-compatible type definition dictionary.

        """
        # REMOVED: infer_type_from_sample - FORBIDDEN METHOD
        # This method is FORBIDDEN and has been permanently deleted
        raise NotImplementedError


class AuthenticatorInterface(ABC):
    """Interface for authentication operations."""

    @abstractmethod
    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary of authentication headers.

        """
        raise NotImplementedError

    @abstractmethod
    def refresh_credentials(self) -> bool:
        """Refresh authentication credentials if needed.

        Returns:
            True if credentials were refreshed successfully.

        """
        raise NotImplementedError


class StreamFactoryInterface(ABC):
    """Interface for stream creation operations."""

    @abstractmethod
    def create_stream(
        self,
        entity_name: str,
        schema: dict[str, Any],
        tap_instance: object,
    ) -> object:
        """Create a stream instance for the given entity.

        Args:
            entity_name: Name of the Oracle WMS entity.
            schema: JSON schema for the entity.
            tap_instance: Parent tap instance.

        Returns:
            Stream object for data extraction.

        """
        # Abstract method - parameters intentionally unused in interface
        _ = entity_name, schema, tap_instance
        raise NotImplementedError

    @abstractmethod
    def validate_stream_config(self, config: dict[str, Any]) -> bool:
        """Validate stream configuration.

        Args:
            config: Stream configuration dictionary.

        Returns:
            True if configuration is valid.

        """
        raise NotImplementedError


class MetricsCollectorInterface(ABC):
    """Interface for metrics collection operations."""

    @abstractmethod
    def record_request_time(self, entity: str, duration: float) -> None:
        """Record API request duration for an entity.

        Args:
            entity: Entity name for the request.
            duration: Request duration in seconds.

        """
        # Abstract method - parameters intentionally unused in interface
        _ = entity, duration
        raise NotImplementedError

    @abstractmethod
    def record_record_count(self, entity: str, count: int) -> None:
        """Record number of records extracted for an entity.

        Args:
            entity: Entity name.
            count: Number of records extracted.

        """
        raise NotImplementedError

    @abstractmethod
    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics.

        Returns:
            Dictionary containing metrics summary data.

        """
        raise NotImplementedError
