"""Interface definitions for Oracle WMS Tap following SOLID principles.

This module defines the contracts (interfaces) that components must implement,
promoting loose coupling and high cohesion.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EntityDiscoveryInterface(ABC):
    """Interface for entity discovery operations."""

    @abstractmethod
    async def discover_entities(self) -> dict[str, str]:
        """Discover available entities from the API."""

    @abstractmethod
    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get metadata description for a specific entity."""

    @abstractmethod
    async def get_entity_sample(
        self, entity_name: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get sample records from an entity."""

    @abstractmethod
    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration."""


class SchemaGeneratorInterface(ABC):
    """Interface for schema generation operations."""

    @abstractmethod
    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate schema from API metadata."""

    @abstractmethod
    def generate_from_sample(self, samples: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate schema from sample data."""

    @abstractmethod
    def generate_hybrid_schema(
        self, metadata: dict[str, Any], samples: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Generate schema using both metadata and samples."""

    @abstractmethod
    def flatten_complex_objects(self, data: dict[str, Any]) -> dict[str, Any]:
        """Flatten nested objects for schema consistency."""


class CacheManagerInterface(ABC):
    """Interface for cache management operations."""

    @abstractmethod
    def get_cached_value(self, key: str) -> Any | None:
        """Get value from cache."""

    @abstractmethod
    def set_cached_value(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL."""

    @abstractmethod
    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cache entries."""

    @abstractmethod
    def is_cache_valid(self, key: str, ttl: int) -> bool:
        """Check if cache entry is still valid."""


class TypeMapperInterface(ABC):
    """Interface for type mapping operations."""

    @abstractmethod
    def convert_metadata_type_to_singer(
        self,
        metadata_type: str | None,
        column_name: str = "",
        max_length: int | None = None,
        sample_value: object = None,
    ) -> dict[str, Any]:
        """Convert WMS metadata type to Singer schema format."""

    @abstractmethod
    def infer_type_from_sample(self, sample_value: object) -> dict[str, Any]:
        """Infer type from sample value."""


class AuthenticatorInterface(ABC):
    """Interface for authentication operations."""

    @abstractmethod
    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""

    @abstractmethod
    def refresh_credentials(self) -> bool:
        """Refresh authentication credentials if needed."""


class StreamFactoryInterface(ABC):
    """Interface for stream creation operations."""

    @abstractmethod
    def create_stream(
        self, entity_name: str, schema: dict[str, Any], tap_instance: Any
    ) -> Any:
        """Create a stream instance for the given entity."""

    @abstractmethod
    def validate_stream_config(self, config: dict[str, Any]) -> bool:
        """Validate stream configuration."""


class MetricsCollectorInterface(ABC):
    """Interface for metrics collection operations."""

    @abstractmethod
    def record_request_time(self, entity: str, duration: float) -> None:
        """Record request timing metrics."""

    @abstractmethod
    def record_record_count(self, entity: str, count: int) -> None:
        """Record extracted record count."""

    @abstractmethod
    def get_metrics_summary(self) -> dict[str, Any]:
        """Get metrics summary."""
