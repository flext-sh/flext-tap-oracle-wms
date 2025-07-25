"""Cache Manager for Oracle WMS Tap.

REFACTORED: Uses centralized flext-oracle-wms cache - NO DUPLICATION.
"""

from typing import Any

from flext_core import get_logger
from flext_oracle_wms import (
    flext_oracle_wms_create_cache_manager,
)

from flext_tap_oracle_wms.interfaces import CacheManagerInterface

logger = get_logger(__name__)

# Type alias for cache values
CacheValueType = str | dict[str, Any] | bool


class CacheManager(CacheManagerInterface):
    """Cache manager using centralized flext-oracle-wms functionality."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize cache manager.

        Args:
            config: Cache configuration

        """
        # Use centralized cache manager
        self._cache_manager = flext_oracle_wms_create_cache_manager()
        self.config = config
        logger.info("Initialized cache manager with centralized implementation")

    def get(self, key: str) -> CacheValueType | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found

        """
        return self._cache_manager.flext_oracle_wms_get_entity_from_cache(key)

    def set(self, key: str, value: CacheValueType, ttl: int | None = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        """
        self._cache_manager.flext_oracle_wms_cache_entity(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found

        """
        return self._cache_manager.flext_oracle_wms_invalidate_cache(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache_manager.flext_oracle_wms_clear_cache()

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics

        """
        return self._cache_manager.flext_oracle_wms_get_cache_stats()

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise

        """
        return self.get(key) is not None


# Backward compatibility alias
WMSCacheManager = CacheManager
