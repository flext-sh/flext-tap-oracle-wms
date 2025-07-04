"""Entity discovery implementation following SOLID principles.

This module focuses solely on discovering entities from Oracle WMS API,
following the Single Responsibility Principle.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .interfaces import CacheManagerInterface, EntityDiscoveryInterface

logger = logging.getLogger(__name__)

# HTTP status codes
HTTP_NOT_FOUND = 404


class EntityDiscoveryError(Exception):
    """Exception raised when entity discovery fails."""


class EntityDescriptionError(Exception):
    """Exception raised when entity description fails."""


class NetworkError(Exception):
    """Exception raised for network-related errors."""


class EntityDiscovery(EntityDiscoveryInterface):
    """Handle dynamic entity discovery from Oracle WMS API.

    Focuses solely on entity discovery operations, delegating caching
    to a cache manager. Follows SRP and DIP principles.
    """

    def __init__(
        self,
        config: dict[str, Any],
        cache_manager: CacheManagerInterface,
        headers: dict[str, str] | None = None
    ) -> None:
        """Initialize entity discovery with configuration and dependencies."""
        self.config = config
        self.cache_manager = cache_manager  # Dependency injection (DIP)
        self.headers = headers or {}

        # Build API endpoints
        self.base_url = config["base_url"].rstrip("/")
        self.api_version = config.get("wms_api_version", "v10")
        self.entity_endpoint = f"{self.base_url}/wms/lgfapi/{self.api_version}/entity"

    async def discover_entities(self) -> dict[str, str]:
        """Discover available entities from WMS API."""
        # Check cache first
        cached_entities = self.cache_manager.get_cached_value("entity:all")
        if cached_entities is not None:
            logger.debug("Using cached entity list (%d entities)", len(cached_entities))
            return cached_entities

        # Discover from API
        discovered_entities = await self._fetch_entities_from_api()

        # Cache the results
        self.cache_manager.set_cached_value("entity:all", discovered_entities)

        logger.info("Discovered %d entities from WMS API", len(discovered_entities))
        return discovered_entities

    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get metadata description for a specific entity."""
        # Check cache first
        cache_key = f"metadata:{entity_name}"
        cached_metadata = self.cache_manager.get_cached_value(cache_key)
        if cached_metadata is not None:
            logger.debug("Using cached metadata for entity: %s", entity_name)
            return cached_metadata

        # Fetch from API
        metadata = await self._fetch_entity_metadata(entity_name)

        if metadata:
            # Cache the results
            self.cache_manager.set_cached_value(cache_key, metadata)
            logger.debug("Cached metadata for entity: %s", entity_name)

        return metadata

    async def get_entity_sample(
        self, entity_name: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get sample records from an entity for schema inference."""
        # Check cache first
        cache_key = f"sample:{entity_name}:{limit}"
        cached_samples = self.cache_manager.get_cached_value(cache_key)
        if cached_samples is not None:
            logger.debug("Using cached samples for entity: %s", entity_name)
            return cached_samples

        # Fetch from API
        samples = await self._fetch_entity_samples(entity_name, limit)

        # Cache the results
        self.cache_manager.set_cached_value(cache_key, samples)

        logger.debug("Fetched %d sample records for entity: %s", len(samples), entity_name)
        return samples

    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration patterns."""
        # Check if specific entities are configured
        configured_entities = self.config.get("entities")
        if configured_entities:
            filtered = {
                name: url for name, url in entities.items()
                if name in configured_entities
            }
            logger.info(
                "Filtered to configured entities: %d/%d",
                len(filtered), len(entities)
            )
            return filtered

        # Apply pattern-based filtering
        entity_patterns = self.config.get("entity_patterns", {})
        include_patterns = entity_patterns.get("include", [])
        exclude_patterns = entity_patterns.get("exclude", [])

        filtered = {}
        for entity_name, entity_url in entities.items():
            # Check include patterns
            if include_patterns and not self._matches_patterns(entity_name, include_patterns):
                continue

            # Check exclude patterns
            if exclude_patterns and self._matches_patterns(entity_name, exclude_patterns):
                continue

            filtered[entity_name] = entity_url

        logger.info(
            "Pattern filtering: %d/%d entities (include: %s, exclude: %s)",
            len(filtered), len(entities), include_patterns, exclude_patterns
        )
        return filtered

    async def _fetch_entities_from_api(self) -> dict[str, str]:
        """Fetch entity list from WMS API."""
        url = f"{self.entity_endpoint}/"

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                data = response.json()

                # Parse entity discovery response
                if isinstance(data, dict) and "results" in data:
                    results = data["results"]
                    if isinstance(results, list):
                        return self._parse_entity_results(results)
                elif isinstance(data, list):
                    return self._parse_entity_results(data)

                logger.warning("Unexpected entity discovery response format")
                return {}

            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP error discovering entities: {e.response.status_code}"
                logger.exception(error_msg)
                raise EntityDiscoveryError(error_msg) from e
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError) as e:
                error_msg = f"Network error discovering entities: {e}"
                logger.exception(error_msg)
                raise NetworkError(error_msg) from e
            except (ValueError, KeyError, TypeError) as e:
                error_msg = f"Data parsing error during entity discovery: {e}"
                logger.exception(error_msg)
                raise EntityDiscoveryError(error_msg) from e

    async def _fetch_entity_metadata(self, entity_name: str) -> dict[str, Any] | None:
        """Fetch metadata for a specific entity."""
        url = f"{self.entity_endpoint}/{entity_name}/describe/"

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                metadata: dict[str, Any] = response.json()
                return metadata

            except httpx.HTTPStatusError as e:
                if e.response.status_code == HTTP_NOT_FOUND:
                    logger.warning("Entity %s not found (404)", entity_name)
                    return None
                error_msg = f"HTTP error describing entity {entity_name}: {e.response.status_code}"
                logger.exception(error_msg)
                raise EntityDescriptionError(error_msg) from e
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError) as e:
                error_msg = f"Network error describing entity {entity_name}: {e}"
                logger.exception(error_msg)
                raise NetworkError(error_msg) from e
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(
                    "Data parsing error during metadata fetch for entity %s: %s",
                    entity_name, e
                )
                return None

    async def _fetch_entity_samples(
        self, entity_name: str, limit: int
    ) -> list[dict[str, Any]]:
        """Fetch sample records from an entity."""
        url = f"{self.entity_endpoint}/{entity_name}"
        params = {"page_size": limit, "page_mode": "sequenced"}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()

                # Parse sample data response
                if isinstance(data, dict) and "results" in data:
                    results = data["results"]
                    if isinstance(results, list):
                        return results[:limit]
                elif isinstance(data, list):
                    return data[:limit]

                return []

            except httpx.HTTPStatusError as e:
                if e.response.status_code == HTTP_NOT_FOUND:
                    logger.warning("Entity %s not found for sampling", entity_name)
                    return []
                error_msg = f"HTTP error getting samples for entity {entity_name}: {e}"
                logger.exception(error_msg)
                raise EntityDiscoveryError(error_msg) from e
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError) as e:
                error_msg = f"Network error getting samples for entity {entity_name}: {e}"
                logger.exception(error_msg)
                raise NetworkError(error_msg) from e
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(
                    "Data parsing error getting samples for entity %s: %s",
                    entity_name, e
                )
                return []

    def _parse_entity_results(self, results: list[Any]) -> dict[str, str]:
        """Parse entity results from API response."""
        entities = {}

        for item in results:
            if isinstance(item, dict):
                entity_name = item.get("name") or item.get("entity_name")
                entity_url = item.get("url") or item.get("entity_url")

                if entity_name and entity_url:
                    entities[entity_name] = entity_url
                elif entity_name:
                    # Construct URL if not provided
                    entities[entity_name] = f"{self.entity_endpoint}/{entity_name}"

        return entities

    def _matches_patterns(self, entity_name: str, patterns: list[str]) -> bool:
        """Check if entity name matches any of the patterns."""
        entity_lower = entity_name.lower()

        for pattern in patterns:
            pattern_lower = pattern.lower()

            # Support simple wildcard patterns
            if "*" in pattern_lower:
                pattern_clean = pattern_lower.replace("*", "")
                if pattern_lower.startswith("*") and entity_lower.endswith(pattern_clean):
                    return True
                if pattern_lower.endswith("*") and entity_lower.startswith(pattern_clean):
                    return True
                if pattern_clean in entity_lower:
                    return True
            elif pattern_lower == entity_lower:
                return True

        return False
