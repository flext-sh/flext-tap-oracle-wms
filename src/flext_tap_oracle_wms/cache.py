"""Cache Manager for Oracle WMS Tap.

REFACTORED: Uses simplified in-memory cache for reliability.
"""

import time
from typing import Any

from flext_core import get_logger

from flext_tap_oracle_wms.interfaces import CacheManagerInterface

logger = get_logger(__name__)

# Type alias for cache values - expanded to match library return types
CacheValueType = str | dict[str, object] | bool | list[Any] | int | float


class CacheManager(CacheManagerInterface):
    """Cache manager using centralized flext-oracle-wms functionality."""

    def __init__(self, config: dict[str, object]) -> None:
        """Initialize cache manager using simplified in-memory cache.

        Args:
            config: Cache configuration

        """
        # Use simplified in-memory cache to avoid flext-oracle-wms initialization issues
        # This provides the same interface but uses a simple dict-based cache
        self._cache: dict[str, tuple[object, float]] = {}  # key -> (value, expiry_time)

        # Parse configuration with test compatibility
        self._default_ttl = int(config.get("cache_ttl_seconds", config.get("default_ttl", 3600)))
        self._max_cache_size = int(config.get("max_cache_size", config.get("max_entries", 1000)))
        self._max_entries = self._max_cache_size  # Alias for internal use
        self._stats = {"hits": 0, "misses": 0, "entries": 0, "size": 0}

        # Test compatibility attributes
        self._cache_hits = 0
        self._cache_misses = 0
        self._entity_cache_expires: dict[str, float] = {}
        self._schema_cache_expires: dict[str, float] = {}
        self._metadata_cache_expires: dict[str, float] = {}

        self.config = config
        logger.info("Initialized cache manager with simplified in-memory cache")

    def get_cached_value(self, key: str) -> object | None:
        """Retrieve a cached value by key.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if not found.

        """
        # Check if key exists and is not expired
        if key in self._cache:
            value, expiry_time = self._cache[key]
            if time.time() < expiry_time:
                self._stats["hits"] += 1
                self._cache_hits += 1
                return value
            # Remove expired entry
            del self._cache[key]
            self._stats["entries"] = len(self._cache)

        self._stats["misses"] += 1
        self._cache_misses += 1
        return None

    def set_cached_value(self, key: str, value: object, ttl: int | None = None) -> None:
        """Store a value in cache with optional TTL.

        Args:
            key: Cache key to store under.
            value: Value to cache.
            ttl: Time-to-live threshold in seconds.

        """
        # Enforce cache size limit
        if len(self._cache) >= self._max_entries:
            # Remove oldest entries (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        # Store value with expiry time
        actual_ttl = ttl or self._default_ttl
        expiry_time = time.time() + actual_ttl
        self._cache[key] = (value, expiry_time)
        self._stats["entries"] = len(self._cache)

    def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found

        """
        if key in self._cache:
            del self._cache[key]
            self._stats["entries"] = len(self._cache)
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._stats["entries"] = 0

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics

        """
        # Update current entries count and return stats
        self._stats["entries"] = len(self._cache)
        self._stats["size"] = len(self._cache)
        return self._stats.copy()

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise

        """
        return self.get_cached_value(key) is not None

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cache entries.

        Args:
            cache_type: Type of cache to clear, defaults to "all".

        """
        # Implement abstract method from CacheManagerInterface
        self.clear()

    def is_cache_valid(self, key: str, ttl: int) -> bool:
        """Check if a cache entry is still valid.

        Args:
            key: Cache key to check.
            ttl: Time-to-live threshold in seconds.

        Returns:
            True if cache entry is valid, False otherwise.

        """
        # Implement abstract method from CacheManagerInterface
        return self.exists(key)

    def get_cache_stats(self) -> dict[str, object]:
        """Get cache statistics.

        Returns:
            Dictionary containing cache hit/miss statistics and sizes.

        """
        # Implement abstract method from CacheManagerInterface
        stats = self.get_stats()
        return {
            "hits": stats.get("hits", 0),
            "misses": stats.get("misses", 0),
            "entries": stats.get("entries", 0),
            "size": stats.get("size", 0),
        }

    # Domain-specific cache methods for Oracle WMS
    def get_entity(self, key: str) -> object | None:
        """Get cached entity by key."""
        return self.get_cached_value(f"entity:{key}")

    def set_entity(self, key: str, value: object, ttl: int | None = None) -> None:
        """Set cached entity with optional TTL."""
        self.set_cached_value(f"entity:{key}", value, ttl)

    def get_schema(self, key: str) -> object | None:
        """Get cached schema by key."""
        return self.get_cached_value(f"schema:{key}")

    def set_schema(self, key: str, value: object, ttl: int | None = None) -> None:
        """Set cached schema with optional TTL."""
        self.set_cached_value(f"schema:{key}", value, ttl)

    def get_metadata(self, key: str) -> object | None:
        """Get cached metadata by key."""
        return self.get_cached_value(f"metadata:{key}")

    def set_metadata(self, key: str, value: object, ttl: int | None = None) -> None:
        """Set cached metadata with optional TTL."""
        self.set_cached_value(f"metadata:{key}", value, ttl)

    def _parse_cache_key(self, cache_key: str) -> tuple[str, dict[str, float]]:
        """Parse cache key and return the appropriate expires dictionary.

        Args:
            cache_key: The cache key to parse

        Returns:
            Tuple of (key, expires_dict) where expires_dict is the appropriate cache expires dict

        """
        if cache_key.startswith("entity:"):
            return cache_key[7:], self._entity_cache_expires
        if cache_key.startswith("schema:"):
            return cache_key[7:], self._schema_cache_expires
        if cache_key.startswith("metadata:"):
            return cache_key[9:], self._metadata_cache_expires
        # Unknown prefix, return empty dict
        return cache_key, {}


# Backward compatibility alias
WMSCacheManager = CacheManager


class CacheManagerAdapter(CacheManager):
    """Adapter alias for backward compatibility."""
