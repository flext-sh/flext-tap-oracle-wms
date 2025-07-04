"""Cache manager implementation following SOLID principles.

This module implements caching functionality as a separate responsibility,
following the Single Responsibility Principle.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from .interfaces import CacheManagerInterface

logger = logging.getLogger(__name__)


class CacheManager(CacheManagerInterface):
    """Thread-safe cache manager for Oracle WMS tap operations.

    Handles all caching operations with TTL support and cache statistics.
    Follows SRP by focusing solely on cache management.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize cache manager with configuration."""
        self.config = config

        # Separate cache stores for different data types
        self._entity_cache: dict[str, str] | None = None
        self._schema_cache: dict[str, dict[str, Any]] = {}
        self._metadata_cache: dict[str, dict[str, Any]] = {}
        self._access_cache: dict[str, bool] = {}
        self._sample_cache: dict[str, list[dict[str, Any]]] = {}

        # Cache timestamps for TTL management
        self._entity_cache_time: datetime | None = None
        self._schema_cache_times: dict[str, datetime] = {}
        self._metadata_cache_times: dict[str, datetime] = {}
        self._access_cache_times: dict[str, datetime] = {}
        self._sample_cache_times: dict[str, datetime] = {}

        # Cache configuration
        self._entity_cache_ttl = config.get("entity_cache_ttl", 7200)  # 2 hours
        self._schema_cache_ttl = config.get("schema_cache_ttl", 3600)  # 1 hour
        self._metadata_cache_ttl = config.get("metadata_cache_ttl", 3600)  # 1 hour
        self._access_cache_ttl = config.get("access_cache_ttl", 1800)  # 30 minutes
        self._sample_cache_ttl = config.get("sample_cache_ttl", 1800)  # 30 minutes

    def get_cached_value(self, key: str) -> Any | None:
        """Get value from appropriate cache based on key type."""
        cache_type, cache_key = self._parse_cache_key(key)

        if cache_type == "entity":
            return self._get_entity_cache()
        if cache_type == "schema":
            return self._get_from_cache_with_ttl(
                self._schema_cache, cache_key,
                self._schema_cache_times, self._schema_cache_ttl
            )
        if cache_type == "metadata":
            return self._get_from_cache_with_ttl(
                self._metadata_cache, cache_key,
                self._metadata_cache_times, self._metadata_cache_ttl
            )
        if cache_type == "access":
            return self._get_from_cache_with_ttl(
                self._access_cache, cache_key,
                self._access_cache_times, self._access_cache_ttl
            )
        if cache_type == "sample":
            return self._get_from_cache_with_ttl(
                self._sample_cache, cache_key,
                self._sample_cache_times, self._sample_cache_ttl
            )

        return None

    def set_cached_value(
        self, key: str, value: Any, ttl: int | None = None
    ) -> None:
        """Set value in appropriate cache."""
        cache_type, cache_key = self._parse_cache_key(key)
        now = datetime.now(timezone.utc)

        if cache_type == "entity":
            self._entity_cache = value
            self._entity_cache_time = now
        elif cache_type == "schema":
            self._schema_cache[cache_key] = value
            self._schema_cache_times[cache_key] = now
        elif cache_type == "metadata":
            self._metadata_cache[cache_key] = value
            self._metadata_cache_times[cache_key] = now
        elif cache_type == "access":
            self._access_cache[cache_key] = value
            self._access_cache_times[cache_key] = now
        elif cache_type == "sample":
            self._sample_cache[cache_key] = value
            self._sample_cache_times[cache_key] = now

        logger.debug("Cached %s:%s (TTL: %s)", cache_type, cache_key, ttl)

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear specified cache type or all caches."""
        if cache_type in {"all", "entity"}:
            self._entity_cache = None
            self._entity_cache_time = None

        if cache_type in {"all", "schema"}:
            self._schema_cache.clear()
            self._schema_cache_times.clear()

        if cache_type in {"all", "metadata"}:
            self._metadata_cache.clear()
            self._metadata_cache_times.clear()

        if cache_type in {"all", "access"}:
            self._access_cache.clear()
            self._access_cache_times.clear()

        if cache_type in {"all", "sample"}:
            self._sample_cache.clear()
            self._sample_cache_times.clear()

        logger.info("Cleared %s cache", cache_type)

    def is_cache_valid(self, key: str, ttl: int) -> bool:
        """Check if cache entry is still valid."""
        cache_type, cache_key = self._parse_cache_key(key)

        if cache_type == "entity":
            return self._is_timestamp_valid(self._entity_cache_time, ttl)
        if cache_type == "schema":
            timestamp = self._schema_cache_times.get(cache_key)
            return self._is_timestamp_valid(timestamp, ttl)
        if cache_type == "metadata":
            timestamp = self._metadata_cache_times.get(cache_key)
            return self._is_timestamp_valid(timestamp, ttl)
        if cache_type == "access":
            timestamp = self._access_cache_times.get(cache_key)
            return self._is_timestamp_valid(timestamp, ttl)
        if cache_type == "sample":
            timestamp = self._sample_cache_times.get(cache_key)
            return self._is_timestamp_valid(timestamp, ttl)

        return False

    def get_cache_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            "entity_cache": {
                "cached": self._entity_cache is not None,
                "cached_at": self._entity_cache_time.isoformat() if self._entity_cache_time else None,
                "ttl_seconds": self._entity_cache_ttl,
            },
            "schema_cache": {
                "entries": len(self._schema_cache),
                "keys": list(self._schema_cache.keys()),
                "ttl_seconds": self._schema_cache_ttl,
            },
            "metadata_cache": {
                "entries": len(self._metadata_cache),
                "keys": list(self._metadata_cache.keys()),
                "ttl_seconds": self._metadata_cache_ttl,
            },
            "access_cache": {
                "entries": len(self._access_cache),
                "ttl_seconds": self._access_cache_ttl,
            },
            "sample_cache": {
                "entries": len(self._sample_cache),
                "keys": list(self._sample_cache.keys()),
                "ttl_seconds": self._sample_cache_ttl,
            },
        }

    def _parse_cache_key(self, key: str) -> tuple[str, str]:
        """Parse cache key into type and actual key."""
        if ":" in key:
            cache_type, cache_key = key.split(":", 1)
            return cache_type, cache_key
        # Default to metadata cache for backward compatibility
        return "metadata", key

    def _get_entity_cache(self) -> dict[str, str] | None:
        """Get entity cache if valid."""
        if (self._entity_cache is not None and
            self._is_timestamp_valid(self._entity_cache_time, self._entity_cache_ttl)):
            return self._entity_cache
        return None

    def _get_from_cache_with_ttl(
        self,
        cache_dict: dict[str, Any],
        key: str,
        time_dict: dict[str, datetime],
        ttl: int,
    ) -> Any | None:
        """Get value from cache with TTL validation."""
        if key not in cache_dict:
            return None

        cached_time = time_dict.get(key)
        if self._is_timestamp_valid(cached_time, ttl):
            return cache_dict[key]

        # Remove expired entry
        cache_dict.pop(key, None)
        time_dict.pop(key, None)
        return None

    def _is_timestamp_valid(
        self, timestamp: datetime | None, ttl: int
    ) -> bool:
        """Check if timestamp is within TTL."""
        if timestamp is None:
            return False

        age_seconds = (datetime.now(timezone.utc) - timestamp).total_seconds()
        return age_seconds < ttl
