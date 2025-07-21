"""Cache Manager for Oracle WMS Tap.

This module provides caching functionality for Oracle WMS API operations
using flext-core patterns and thread-safe operations.
"""

import logging
import threading
import time
from typing import Any

try:
    from flext_observability.logging import get_logger
except ImportError:
    # Fallback to standard logging if flext_observability is not available
    def get_logger(name: str) -> logging.Logger:  # type: ignore[misc]
        """Fallback logger function.

        Args:
            name: Logger name

        Returns:
            Configured logger instance

        """
        return logging.getLogger(name)


from flext_tap_oracle_wms.interfaces import CacheManagerInterface

CacheValueType = str | dict[str, Any] | bool

logger = get_logger(__name__)


class CacheManager(CacheManagerInterface):
    """Thread-safe cache manager for Oracle WMS tap operations.

    Handles all caching operations with TTL support and cache statistics.
    Follows SRP by focusing solely on cache management.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize cache manager.

        Args:
            config: Configuration dictionary

        """
        self.config = config

        # Initialize caches
        self._entity_cache: dict[str, Any] = {}
        self._schema_cache: dict[str, Any] = {}
        self._metadata_cache: dict[str, Any] = {}

        # Cache expiration tracking
        self._entity_cache_expires: dict[str, float] = {}
        self._schema_cache_expires: dict[str, float] = {}
        self._metadata_cache_expires: dict[str, float] = {}

        # Thread safety
        self._cache_lock = threading.RLock()

        # Configuration
        self._default_ttl = config.get("cache_ttl_seconds", 3600)
        self._max_cache_size = config.get("max_cache_size", 1000)

        # Statistics
        self._cache_hits = 0
        self._cache_misses = 0

        logger.debug(
            "Cache manager initialized with TTL: %d seconds",
            self._default_ttl,
        )

    def get_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get cached entity data.

        Args:
            entity_name: Name of the entity to retrieve

        Returns:
            Cached entity data if valid, None if not found or expired

        """
        with self._cache_lock:
            if self._is_cache_valid(entity_name, self._entity_cache_expires):
                self._cache_hits += 1
                logger.debug("Cache hit for entity: %s", entity_name)
                return self._entity_cache.get(entity_name)

            self._cache_misses += 1
            logger.debug("Cache miss for entity: %s", entity_name)
            return None

    def set_entity(
        self,
        entity_name: str,
        data: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Cache entity data with TTL.

        Args:
            entity_name: Name of the entity to cache
            data: Entity data to cache
            ttl: Time to live in seconds (optional)

        """
        with self._cache_lock:
            self._cleanup_expired_cache()

            cache_ttl = ttl or self._default_ttl
            expiry_time = time.time() + cache_ttl

            self._entity_cache[entity_name] = data
            self._entity_cache_expires[entity_name] = expiry_time

            logger.debug("Cached entity: %s (TTL: %d seconds)", entity_name, cache_ttl)

    def get_schema(self, entity_name: str) -> dict[str, Any] | None:
        """Get cached schema data.

        Args:
            entity_name: Name of the entity schema to retrieve

        Returns:
            Cached schema data if valid, None if not found or expired

        """
        with self._cache_lock:
            if self._is_cache_valid(entity_name, self._schema_cache_expires):
                self._cache_hits += 1
                logger.debug("Cache hit for schema: %s", entity_name)
                return self._schema_cache.get(entity_name)

            self._cache_misses += 1
            logger.debug("Cache miss for schema: %s", entity_name)
            return None

    def set_schema(
        self,
        entity_name: str,
        schema: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Cache schema data with TTL.

        Args:
            entity_name: Name of the entity schema to cache
            schema: Schema data to cache
            ttl: Time to live in seconds (optional)

        """
        with self._cache_lock:
            self._cleanup_expired_cache()

            cache_ttl = ttl or self._default_ttl
            expiry_time = time.time() + cache_ttl

            self._schema_cache[entity_name] = schema
            self._schema_cache_expires[entity_name] = expiry_time

            logger.debug("Cached schema: %s (TTL: %d seconds)", entity_name, cache_ttl)

    def get_metadata(self, entity_name: str) -> dict[str, Any] | None:
        """Get cached metadata.

        Args:
            entity_name: Name of the entity metadata to retrieve

        Returns:
            Cached metadata if valid, None if not found or expired

        """
        with self._cache_lock:
            if self._is_cache_valid(entity_name, self._metadata_cache_expires):
                self._cache_hits += 1
                logger.debug("Cache hit for metadata: %s", entity_name)
                return self._metadata_cache.get(entity_name)

            self._cache_misses += 1
            logger.debug("Cache miss for metadata: %s", entity_name)
            return None

    def set_metadata(
        self,
        entity_name: str,
        metadata: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Cache metadata with TTL.

        Args:
            entity_name: Name of the entity metadata to cache
            metadata: Metadata to cache
            ttl: Time to live in seconds (optional)

        """
        with self._cache_lock:
            self._cleanup_expired_cache()

            cache_ttl = ttl or self._default_ttl
            expiry_time = time.time() + cache_ttl

            self._metadata_cache[entity_name] = metadata
            self._metadata_cache_expires[entity_name] = expiry_time

            logger.debug(
                "Cached metadata: %s (TTL: %d seconds)",
                entity_name,
                cache_ttl,
            )

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cache by type.

        Args:
            cache_type: Type of cache to clear ('all', 'entity', 'schema', 'metadata')

        """
        with self._cache_lock:
            if cache_type in {"all", "entity"}:
                self._entity_cache.clear()
                self._entity_cache_expires.clear()
                logger.debug("Cleared entity cache")

            if cache_type in {"all", "schema"}:
                self._schema_cache.clear()
                self._schema_cache_expires.clear()
                logger.debug("Cleared schema cache")

            if cache_type in {"all", "metadata"}:
                self._metadata_cache.clear()
                self._metadata_cache_expires.clear()
                logger.debug("Cleared metadata cache")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache hit/miss statistics and sizes

        """
        with self._cache_lock:
            total_requests = self._cache_hits + self._cache_misses
            hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0.0

            return {
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "hit_rate": hit_rate,
                "entity_cache_size": len(self._entity_cache),
                "schema_cache_size": len(self._schema_cache),
                "metadata_cache_size": len(self._metadata_cache),
            }

    @staticmethod
    def _is_cache_valid(key: str, expires_dict: dict[str, float]) -> bool:
        """Check if cache entry is still valid.

        Args:
            key: Cache key to check
            expires_dict: Dictionary of expiration times

        Returns:
            True if cache entry exists and is not expired

        """
        if key not in expires_dict:
            return False
        return time.time() < expires_dict[key]

    def _cleanup_expired_cache(self) -> None:
        """Remove expired cache entries from all caches."""
        current_time = time.time()

        # Clean entity cache
        expired_entities = [
            key
            for key, expiry in self._entity_cache_expires.items()
            if current_time >= expiry
        ]
        for key in expired_entities:
            self._entity_cache.pop(key, None)
            self._entity_cache_expires.pop(key, None)

        # Clean schema cache
        expired_schemas = [
            key
            for key, expiry in self._schema_cache_expires.items()
            if current_time >= expiry
        ]
        for key in expired_schemas:
            self._schema_cache.pop(key, None)
            self._schema_cache_expires.pop(key, None)

        # Clean metadata cache
        expired_metadata = [
            key
            for key, expiry in self._metadata_cache_expires.items()
            if current_time >= expiry
        ]
        for key in expired_metadata:
            self._metadata_cache.pop(key, None)
            self._metadata_cache_expires.pop(key, None)

        if expired_entities or expired_schemas or expired_metadata:
            total_expired = (
                len(expired_entities) + len(expired_schemas) + len(expired_metadata)
            )
            logger.debug("Cleaned up %d expired cache entries", total_expired)

    def get_cached_value(self, key: str) -> object | None:
        """Retrieve a cached value by key.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found or expired.

        """
        # Handle typed cache keys
        if key.startswith(("entity:", "schema:", "metadata:")):
            return self._get_typed_cache_value(key)

        # Generic cache lookup - check all caches
        return self._get_generic_cache_value(key)

    def _get_typed_cache_value(self, key: str) -> object | None:
        """Get value from typed cache based on key prefix.

        Args:
            key: Prefixed cache key

        Returns:
            Cached value or None if not found

        """
        if key.startswith("entity:"):
            entity_name = key[7:]  # Remove "entity:" prefix
            return self.get_entity(entity_name)
        if key.startswith("schema:"):
            entity_name = key[7:]  # Remove "schema:" prefix
            return self.get_schema(entity_name)
        if key.startswith("metadata:"):
            entity_name = key[9:]  # Remove "metadata:" prefix
            return self.get_metadata(entity_name)
        return None

    def _get_generic_cache_value(self, key: str) -> object | None:
        """Get value from generic cache lookup.

        Args:
            key: Generic cache key

        Returns:
            Cached value or None if not found

        """
        with self._cache_lock:
            # Check caches in order of priority
            cache_checks = [
                (self._entity_cache_expires, self._entity_cache),
                (self._schema_cache_expires, self._schema_cache),
                (self._metadata_cache_expires, self._metadata_cache),
            ]

            for expires_dict, cache_dict in cache_checks:
                if self._is_cache_valid(key, expires_dict):
                    return cache_dict.get(key)

            return None

    def set_cached_value(self, key: str, value: object, ttl: int | None = None) -> None:
        """Store a value in cache with optional TTL.

        Args:
            key: Cache key to store.
            value: Value to cache.
            ttl: Optional time-to-live in seconds.

        """
        # Parse key to determine cache type
        if key.startswith("entity:"):
            entity_name = key[7:]  # Remove "entity:" prefix
            if isinstance(value, dict):
                self.set_entity(entity_name, value, ttl)
        elif key.startswith("schema:"):
            entity_name = key[7:]  # Remove "schema:" prefix
            if isinstance(value, dict):
                self.set_schema(entity_name, value, ttl)
        elif key.startswith("metadata:"):
            entity_name = key[9:]  # Remove "metadata:" prefix
            if isinstance(value, dict):
                self.set_metadata(entity_name, value, ttl)
        else:
            # Generic cache storage - use entity cache as default
            with self._cache_lock:
                self._cleanup_expired_cache()

                cache_ttl = ttl or self._default_ttl
                expiry_time = time.time() + cache_ttl

                self._entity_cache[key] = value
                self._entity_cache_expires[key] = expiry_time

                logger.debug(
                    "Cached generic value: %s (TTL: %d seconds)",
                    key,
                    cache_ttl,
                )

    def is_cache_valid(self, key: str, ttl: int) -> bool:
        """Check if a cache entry is valid (not expired).

        Args:
            key: Cache key to check.
            ttl: Time-to-live threshold in seconds.

        Returns:
            True if cache entry exists and is not expired.

        """
        # Parse key to determine cache type and get the appropriate expires dict
        actual_key, expires_dict = self._parse_cache_key(key)

        # Return False if no valid cache found or key doesn't exist
        if not expires_dict or actual_key not in expires_dict:
            return False

        # Check if TTL is within threshold
        time_remaining = expires_dict[actual_key] - time.time()
        return time_remaining >= ttl

    def _parse_cache_key(self, key: str) -> tuple[str, dict[str, float] | None]:
        """Parse cache key and return actual key and appropriate expires dictionary.

        Args:
            key: Cache key to parse

        Returns:
            Tuple of (actual_key, expires_dict) or (key, None) if not found

        """
        if key.startswith("entity:"):
            return key[7:], self._entity_cache_expires
        if key.startswith("schema:"):
            return key[7:], self._schema_cache_expires
        if key.startswith("metadata:"):
            return key[9:], self._metadata_cache_expires

        # Check all caches for generic key
        if (
            key in self._entity_cache_expires
            or key in self._schema_cache_expires
            or key in self._metadata_cache_expires
        ):
            # Default to entity cache for generic keys
            return key, self._entity_cache_expires

        return key, None
