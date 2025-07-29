"""Comprehensive tests for cache manager functionality."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import threading
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from flext_tap_oracle_wms.infrastructure.cache import CacheManager


# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3

class TestCacheManagerComprehensive:
    """Comprehensive tests for cache manager functionality."""

    def test_cache_manager_initialization(self) -> None:
        """Test cache manager initialization."""
        config = {
            "cache_ttl_seconds": 1800,
            "max_cache_size": 500,
        }

        cache_manager = CacheManager(config)

        if cache_manager.config != config:

            raise AssertionError(f"Expected {config}, got {cache_manager.config}")
        assert cache_manager._default_ttl == 1800
        if cache_manager._max_cache_size != 500:
            raise AssertionError(f"Expected {500}, got {cache_manager._max_cache_size}")
        assert cache_manager._cache_hits == 0
        if cache_manager._cache_misses != 0:
            raise AssertionError(f"Expected {0}, got {cache_manager._cache_misses}")

    def test_cache_manager_default_settings(self) -> None:
        """Test cache manager with default settings."""
        cache_manager = CacheManager({})

        if cache_manager._default_ttl != 3600  # Default 1 hour:

            raise AssertionError(f"Expected {3600  # Default 1 hour}, got {cache_manager._default_ttl}")
        assert cache_manager._max_cache_size == 1000  # Default size

    def test_entity_cache_operations(self) -> None:
        """Test entity cache operations."""
        cache_manager = CacheManager({})
        entity_data = {"id": 1, "name": "test_entity"}

        # Test cache miss
        result = cache_manager.get_entity("test_entity")
        assert result is None
        if cache_manager._cache_misses != 1:
            raise AssertionError(f"Expected {1}, got {cache_manager._cache_misses}")

        # Set entity in cache
        cache_manager.set_entity("test_entity", entity_data)

        # Test cache hit
        result = cache_manager.get_entity("test_entity")
        if result != entity_data:
            raise AssertionError(f"Expected {entity_data}, got {result}")
        assert cache_manager._cache_hits == 1

    def test_entity_cache_with_custom_ttl(self) -> None:
        """Test entity cache with custom TTL."""
        cache_manager = CacheManager({})
        entity_data = {"id": 1, "name": "test_entity"}

        # Set with custom TTL
        cache_manager.set_entity("test_entity", entity_data, ttl=1)

        # Should be cached immediately
        result = cache_manager.get_entity("test_entity")
        if result != entity_data:
            raise AssertionError(f"Expected {entity_data}, got {result}")

        # Wait for TTL to expire
        time.sleep(1.1)

        # Should be expired
        result = cache_manager.get_entity("test_entity")
        assert result is None

    def test_schema_cache_operations(self) -> None:
        """Test schema cache operations."""
        cache_manager = CacheManager({})
        schema_data = {"type": "object", "properties": {"id": {"type": "integer"}}}

        # Test cache miss
        result = cache_manager.get_schema("test_schema")
        assert result is None

        # Set schema in cache
        cache_manager.set_schema("test_schema", schema_data)

        # Test cache hit
        result = cache_manager.get_schema("test_schema")
        if result != schema_data:
            raise AssertionError(f"Expected {schema_data}, got {result}")

    def test_schema_cache_with_custom_ttl(self) -> None:
        """Test schema cache with custom TTL."""
        cache_manager = CacheManager({})
        schema_data = {"type": "object"}

        # Set with custom TTL
        cache_manager.set_schema("test_schema", schema_data, ttl=1)

        # Should be cached immediately
        result = cache_manager.get_schema("test_schema")
        if result != schema_data:
            raise AssertionError(f"Expected {schema_data}, got {result}")

        # Wait for TTL to expire
        time.sleep(1.1)

        # Should be expired
        result = cache_manager.get_schema("test_schema")
        assert result is None

    def test_metadata_cache_operations(self) -> None:
        """Test metadata cache operations."""
        cache_manager = CacheManager({})
        metadata = {"last_updated": "2024-01-01", "version": "1.0"}

        # Test cache miss
        result = cache_manager.get_metadata("test_metadata")
        assert result is None

        # Set metadata in cache
        cache_manager.set_metadata("test_metadata", metadata)

        # Test cache hit
        result = cache_manager.get_metadata("test_metadata")
        if result != metadata:
            raise AssertionError(f"Expected {metadata}, got {result}")

    def test_metadata_cache_with_custom_ttl(self) -> None:
        """Test metadata cache with custom TTL."""
        cache_manager = CacheManager({})
        metadata = {"version": "1.0"}

        # Set with custom TTL
        cache_manager.set_metadata("test_metadata", metadata, ttl=1)

        # Should be cached immediately
        result = cache_manager.get_metadata("test_metadata")
        if result != metadata:
            raise AssertionError(f"Expected {metadata}, got {result}")

        # Wait for TTL to expire
        time.sleep(1.1)

        # Should be expired
        result = cache_manager.get_metadata("test_metadata")
        assert result is None

    def test_clear_cache_all(self) -> None:
        """Test clearing all caches."""
        cache_manager = CacheManager({})

        # Populate all caches
        cache_manager.set_entity("entity1", {"data": "entity"})
        cache_manager.set_schema("schema1", {"data": "schema"})
        cache_manager.set_metadata("metadata1", {"data": "metadata"})

        # Clear all caches
        cache_manager.clear_cache("all")

        # All should be empty
        assert cache_manager.get_entity("entity1") is None
        assert cache_manager.get_schema("schema1") is None
        assert cache_manager.get_metadata("metadata1") is None

    def test_clear_cache_entity_only(self) -> None:
        """Test clearing entity cache only."""
        cache_manager = CacheManager({})

        # Populate all caches
        cache_manager.set_entity("entity1", {"data": "entity"})
        cache_manager.set_schema("schema1", {"data": "schema"})
        cache_manager.set_metadata("metadata1", {"data": "metadata"})

        # Clear entity cache only
        cache_manager.clear_cache("entity")

        # Only entity should be cleared
        assert cache_manager.get_entity("entity1") is None
        assert cache_manager.get_schema("schema1") is not None
        assert cache_manager.get_metadata("metadata1") is not None

    def test_clear_cache_schema_only(self) -> None:
        """Test clearing schema cache only."""
        cache_manager = CacheManager({})

        # Populate all caches
        cache_manager.set_entity("entity1", {"data": "entity"})
        cache_manager.set_schema("schema1", {"data": "schema"})
        cache_manager.set_metadata("metadata1", {"data": "metadata"})

        # Clear schema cache only
        cache_manager.clear_cache("schema")

        # Only schema should be cleared
        assert cache_manager.get_entity("entity1") is not None
        assert cache_manager.get_schema("schema1") is None
        assert cache_manager.get_metadata("metadata1") is not None

    def test_clear_cache_metadata_only(self) -> None:
        """Test clearing metadata cache only."""
        cache_manager = CacheManager({})

        # Populate all caches
        cache_manager.set_entity("entity1", {"data": "entity"})
        cache_manager.set_schema("schema1", {"data": "schema"})
        cache_manager.set_metadata("metadata1", {"data": "metadata"})

        # Clear metadata cache only
        cache_manager.clear_cache("metadata")

        # Only metadata should be cleared
        assert cache_manager.get_entity("entity1") is not None
        assert cache_manager.get_schema("schema1") is not None
        assert cache_manager.get_metadata("metadata1") is None

    def test_cache_stats(self) -> None:
        """Test cache statistics."""
        cache_manager = CacheManager({})

        # Populate caches
        cache_manager.set_entity("entity1", {"data": "entity"})
        cache_manager.set_schema("schema1", {"data": "schema"})
        cache_manager.set_metadata("metadata1", {"data": "metadata"})

        # Generate some hits and misses
        cache_manager.get_entity("entity1")  # hit
        cache_manager.get_entity("entity2")  # miss
        cache_manager.get_schema("schema1")  # hit
        cache_manager.get_metadata("metadata2")  # miss

        stats = cache_manager.get_cache_stats()

        if stats["cache_hits"] != EXPECTED_BULK_SIZE:

            raise AssertionError(f"Expected {2}, got {stats["cache_hits"]}")
        assert stats["cache_misses"] == EXPECTED_BULK_SIZE
        if stats["hit_rate"] != 0.5:
            raise AssertionError(f"Expected {0.5}, got {stats["hit_rate"]}")
        assert stats["entity_cache_size"] == 1
        if stats["schema_cache_size"] != 1:
            raise AssertionError(f"Expected {1}, got {stats["schema_cache_size"]}")
        assert stats["metadata_cache_size"] == 1

    def test_cache_stats_empty(self) -> None:
        """Test cache statistics when empty."""
        cache_manager = CacheManager({})

        stats = cache_manager.get_cache_stats()

        if stats["cache_hits"] != 0:

            raise AssertionError(f"Expected {0}, got {stats["cache_hits"]}")
        assert stats["cache_misses"] == 0
        if stats["hit_rate"] != 0.0:
            raise AssertionError(f"Expected {0.0}, got {stats["hit_rate"]}")
        assert stats["entity_cache_size"] == 0
        if stats["schema_cache_size"] != 0:
            raise AssertionError(f"Expected {0}, got {stats["schema_cache_size"]}")
        assert stats["metadata_cache_size"] == 0

    def test_cache_expiry_cleanup(self) -> None:
        """Test cache expiry cleanup."""
        cache_manager = CacheManager({})

        # Set items with short TTL
        cache_manager.set_entity("entity1", {"data": "entity1"}, ttl=1)
        cache_manager.set_entity("entity2", {"data": "entity2"}, ttl=2)
        cache_manager.set_schema("schema1", {"data": "schema1"}, ttl=1)
        cache_manager.set_metadata("metadata1", {"data": "metadata1"}, ttl=1)

        # Wait for some to expire
        time.sleep(1.1)

        # Force cleanup by setting new item
        cache_manager.set_entity("entity3", {"data": "entity3"})

        # Check what's still cached
        assert cache_manager.get_entity("entity1") is None  # Expired
        assert cache_manager.get_entity("entity2") is not None  # Still valid
        assert cache_manager.get_schema("schema1") is None  # Expired
        assert cache_manager.get_metadata("metadata1") is None  # Expired

    def test_generic_cache_operations(self) -> None:
        """Test generic cache operations."""
        cache_manager = CacheManager({})

        # Test typed cache keys
        cache_manager.set_cached_value("entity:test", {"type": "entity"})
        cache_manager.set_cached_value("schema:test", {"type": "schema"})
        cache_manager.set_cached_value("metadata:test", {"type": "metadata"})

        # Test retrieval
        if cache_manager.get_cached_value("entity:test") != {"type": "entity"}:
            raise AssertionError(f"Expected {{"type": "entity"}}, got {cache_manager.get_cached_value("entity:test")}")
        assert cache_manager.get_cached_value("schema:test") == {"type": "schema"}
        if cache_manager.get_cached_value("metadata:test") != {"type": "metadata"}:
            raise AssertionError(f"Expected {{"type": "metadata"}}, got {cache_manager.get_cached_value("metadata:test")}")

    def test_generic_cache_fallback(self) -> None:
        """Test generic cache fallback."""
        cache_manager = CacheManager({})

        # Set generic value
        cache_manager.set_cached_value("generic_key", {"data": "generic"})

        # Should be retrievable via generic lookup
        result = cache_manager.get_cached_value("generic_key")
        if result != {"data": "generic"}:
            raise AssertionError(f"Expected {{"data": "generic"}}, got {result}")

    def test_cache_validation_methods(self) -> None:
        """Test cache validation methods."""
        cache_manager = CacheManager({})

        # Set item with known TTL
        cache_manager.set_entity("test_entity", {"data": "test"}, ttl=10)

        # Test validation
        if not (cache_manager.is_cache_valid("entity:test_entity", 5)):
            raise AssertionError(f"Expected True, got {cache_manager.is_cache_valid("entity:test_entity", 5)}")
        if cache_manager.is_cache_valid("entity:test_entity", 15):
            raise AssertionError(f"Expected False, got {cache_manager.is_cache_valid("entity:test_entity", 15)}")\ n        assert cache_manager.is_cache_valid("entity:nonexistent", 5) is False

    def test_cache_validation_parse_key(self) -> None:
        """Test cache key parsing."""
        cache_manager = CacheManager({})

        # Test various key formats
        key, expires_dict = cache_manager._parse_cache_key("entity:test")
        if key != "test":
            raise AssertionError(f"Expected {"test"}, got {key}")
        assert expires_dict is cache_manager._entity_cache_expires

        key, expires_dict = cache_manager._parse_cache_key("schema:test")
        if key != "test":
            raise AssertionError(f"Expected {"test"}, got {key}")
        assert expires_dict is cache_manager._schema_cache_expires

        key, expires_dict = cache_manager._parse_cache_key("metadata:test")
        if key != "test":
            raise AssertionError(f"Expected {"test"}, got {key}")
        assert expires_dict is cache_manager._metadata_cache_expires

        key, expires_dict = cache_manager._parse_cache_key("unknown:test")
        if key != "unknown:test":
            raise AssertionError(f"Expected {"unknown:test"}, got {key}")
        assert expires_dict is None

    def test_thread_safety(self) -> None:
        """Test thread safety of cache operations."""
        cache_manager = CacheManager({})
        results: list[Any] = []
        errors: list[Exception] = []

        def cache_worker(worker_id: int) -> None:
            try:
                # Each worker sets and gets its own data
                cache_manager.set_entity(f"entity_{worker_id}", {"worker": worker_id})
                result = cache_manager.get_entity(f"entity_{worker_id}")
                results.append(result)
            except (RuntimeError, ValueError, TypeError) as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        if len(errors) != 0, f"Thread safety errors: {errors}":
            raise AssertionError(f"Expected {0, f"Thread safety errors: {errors}"}, got {len(errors)}")
        assert len(results) == 10

        # Verify each worker's data is correct
        for i, result in enumerate(results):
            if result is not None:  # Some might be None due to timing
                if result["worker"] != i:
                    raise AssertionError(f"Expected {i}, got {result["worker"]}")

    def test_cache_invalid_key_types(self) -> None:
        """Test cache with invalid key types."""
        cache_manager = CacheManager({})

        # Test setting with non-dict values for typed caches
        cache_manager.set_cached_value("entity:test", "string_value")
        cache_manager.set_cached_value("schema:test", 123)
        cache_manager.set_cached_value("metadata:test", ["list", "value"])

        # These should not be set in typed caches (only dict values)
        assert cache_manager.get_cached_value("entity:test") is None
        assert cache_manager.get_cached_value("schema:test") is None
        assert cache_manager.get_cached_value("metadata:test") is None

    def test_cache_conflict_resolution(self) -> None:
        """Test cache conflict resolution."""
        cache_manager = CacheManager({})

        # Set the same key in multiple caches
        cache_manager.set_entity("conflict_key", {"type": "entity"})
        cache_manager.set_schema("conflict_key", {"type": "schema"})
        cache_manager.set_metadata("conflict_key", {"type": "metadata"})

        # Generic lookup should return from entity cache (priority order)
        result = cache_manager.get_cached_value("conflict_key")
        if result != {"type": "entity"}:
            raise AssertionError(f"Expected {{"type": "entity"}}, got {result}")

    def test_cache_ttl_edge_cases(self) -> None:
        """Test cache TTL edge cases."""
        cache_manager = CacheManager({})

        # Test with very short TTL
        cache_manager.set_entity("short_ttl", {"data": "test"}, ttl=1)

        # Should be cached immediately
        result = cache_manager.get_entity("short_ttl")
        assert result is not None

        # Wait for TTL to expire
        time.sleep(1.1)

        # Should be expired now
        result = cache_manager.get_entity("short_ttl")
        assert result is None

    @patch("flext_tap_oracle_wms.infrastructure.cache.logger")
    def test_cache_logging(self, mock_logger: MagicMock) -> None:
        """Test cache logging functionality."""
        cache_manager = CacheManager({"cache_ttl_seconds": 3600})

        # Verify initialization logging
        mock_logger.debug.assert_called_with(
            "Cache manager initialized with TTL: %d seconds",
            3600,
        )

        # Reset mock
        mock_logger.reset_mock()

        # Test cache operations logging
        cache_manager.set_entity("test_entity", {"data": "test"})
        cache_manager.get_entity("test_entity")  # hit
        cache_manager.get_entity("nonexistent")  # miss

        # Verify debug logs were called
        if mock_logger.debug.call_count < 3  # At least set, hit, miss logs:
            raise AssertionError(f"Expected {mock_logger.debug.call_count} >= {3  # At least set, hit, miss logs}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
