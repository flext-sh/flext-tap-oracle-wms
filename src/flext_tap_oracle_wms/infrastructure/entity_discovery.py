"""Entity discovery implementation following SOLID principles.

This module focuses solely on discovering entities from Oracle WMS API,
following the Single Responsibility Principle.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import base64

# Removed circular dependency - use DI pattern
import re
from typing import TYPE_CHECKING, Any

import httpx
from flext_core import get_logger

from flext_tap_oracle_wms.config_mapper import ConfigMapper
from flext_tap_oracle_wms.interfaces import EntityDiscoveryInterface

if TYPE_CHECKING:
    from flext_tap_oracle_wms.interfaces import CacheManagerInterface

logger = get_logger(__name__)

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
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize EntityDiscovery with dependency injection.

        Args:
            config: Configuration dictionary
            cache_manager: Cache manager interface instance
            headers: Optional HTTP headers dictionary

        """
        self.config = config
        self.cache_manager = cache_manager  # Dependency injection (DIP)
        self.headers = headers or {}

        # Use ConfigMapper for flexible configuration
        self.config_mapper = ConfigMapper(config)

        # Build API endpoints using configuration
        self.base_url = config["base_url"].rstrip("/")
        self.api_version = self.config_mapper.get_api_version()
        endpoint_prefix = self.config_mapper.get_endpoint_prefix()
        self.entity_endpoint = (
            f"{self.base_url}{endpoint_prefix}/{self.api_version}/entity/"
        )

    async def discover_entities(self) -> dict[str, str]:
        """Discover available entities from Oracle WMS API.

        Returns:
            Dictionary mapping entity names to their API endpoints.

        """
        # Check cache first
        cached_entities = self.cache_manager.get_cached_value("entity:all")
        if cached_entities is not None and isinstance(cached_entities, dict):
            logger.debug("Using cached entity list (%d entities)", len(cached_entities))
            return cached_entities

        # Discover from API
        discovered_entities = await self._fetch_entities_from_api()

        # Cache the results
        self.cache_manager.set_cached_value("entity:all", discovered_entities)

        logger.info("Discovered %d entities from WMS API", len(discovered_entities))
        return discovered_entities

    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get metadata description for a specific entity.

        Args:
            entity_name: Name of the entity to describe.

        Returns:
            Entity metadata dictionary or None if not found.

        """
        # Check cache first
        cache_key = f"metadata:{entity_name}"
        cached_metadata = self.cache_manager.get_cached_value(cache_key)
        if cached_metadata is not None and isinstance(cached_metadata, dict):
            logger.debug("Using cached metadata for entity: %s", entity_name)
            return cached_metadata

        # Fetch from API
        metadata = await self._fetch_entity_metadata(entity_name)

        if metadata:
            # Cache the results
            self.cache_manager.set_cached_value(cache_key, metadata)
            logger.debug("Cached metadata for entity: %s", entity_name)

        return metadata

    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration criteria.

        Args:
            entities: Dictionary of entity names to endpoints

        Returns:
            Filtered dictionary of entities

        """
        # Check if specific entities are configured
        configured_entities = self.config.get("entities")
        if configured_entities:
            filtered = {
                name: url
                for name, url in entities.items()
                if name in configured_entities
            }
            logger.info(
                "Filtered to configured entities: %d/%d",
                len(filtered),
                len(entities),
            )
            return filtered

        # Apply pattern-based filtering
        entity_patterns = self.config.get("entity_patterns", {})
        include_patterns = entity_patterns.get("include", [])
        exclude_patterns = entity_patterns.get("exclude", [])

        # If no patterns, return all entities
        if not include_patterns and not exclude_patterns:
            return entities

        filtered = {}
        for entity_name, entity_url in entities.items():
            # Check include patterns
            if include_patterns and not self._matches_patterns(
                entity_name,
                include_patterns,
            ):
                continue

            # Check exclude patterns
            if exclude_patterns and self._matches_patterns(
                entity_name,
                exclude_patterns,
            ):
                continue

            filtered[entity_name] = entity_url

        logger.info(
            "Pattern filtering: %d/%d entities (include: %s, exclude: %s)",
            len(filtered),
            len(entities),
            len(include_patterns),
            len(exclude_patterns),
        )
        return filtered

    async def _fetch_entities_from_api(self) -> dict[str, str]:
        """Fetch entity list from Oracle WMS API.

        Returns:
            Dictionary mapping entity names to their API endpoints

        Raises:
            EntityDiscoveryError: If entity discovery fails

        """
        entities = {}
        try:
            auth_headers = self._prepare_auth_headers()

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(
                    self.entity_endpoint,
                    headers=auth_headers,
                )
                response.raise_for_status()
                data = response.json()

                # Delegate complex processing to existing helper method
                entities = self._process_api_response(data)

        except httpx.HTTPError as e:
            logger.exception("Failed to fetch entities from API")
            msg = f"HTTP error during entity discovery: {e}"
            raise EntityDiscoveryError(
                msg,
            ) from e
        except Exception as e:
            logger.exception("Unexpected error during entity discovery")
            msg = f"Entity discovery failed: {e}"
            raise EntityDiscoveryError(msg) from e

        return entities

    def _prepare_auth_headers(self) -> dict[str, str]:
        """Prepare authentication headers for API requests.

        Returns:
            Dictionary of authentication headers

        """
        auth_headers = self.headers.copy()

        # Add basic auth if configured
        if self.config.get("auth_method") == "basic":
            username = self.config.get("username")
            password = self.config.get("password")
            if username and password:
                credentials = f"{username}:{password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                auth_headers["Authorization"] = f"Basic {encoded}"

        return auth_headers

    def _process_api_response(
        self,
        data: dict[str, object] | list[object] | object,
    ) -> dict[str, str]:
        """Process Oracle WMS API response and extract entity mapping.

        Args:
            data: Raw API response data

        Returns:
            Dictionary mapping entity names to their URLs

        """
        entities: dict[str, str] = {}

        if isinstance(data, dict):
            entities = self._process_dict_response(data)
        elif isinstance(data, list):
            entities = self._process_list_response(data)
        else:
            logger.warning("Unexpected response type: %s", type(data))

        return entities

    def _process_dict_response(self, data: dict[str, object]) -> dict[str, str]:
        """Process dictionary format API response.

        Args:
            data: Raw dictionary response from API

        Returns:
            Dictionary mapping entity names to URLs

        """
        entities: dict[str, str] = {}

        # Check if it's a direct entity mapping (Oracle WMS format)
        if all(isinstance(v, str) for v in data.values()):
            # Direct mapping format - use as-is
            entities = {k: str(v) for k, v in data.items()}  # Type-safe copy
            logger.info(
                "Using direct entity mapping format (%d entities)",
                len(entities),
            )
        elif "entities" in data:
            # Nested entities format
            entities = self._process_nested_entities(data["entities"])
            logger.info(
                "Using nested entities format (%d entities)",
                len(entities),
            )
        else:
            logger.warning(
                "Unexpected dictionary response format for entities",
            )

        return entities

    def _process_nested_entities(self, entity_list: object) -> dict[str, str]:
        """Process nested entities from API response.

        Args:
            entity_list: Nested entity data from response

        Returns:
            Dictionary mapping entity names to URLs

        """
        entities: dict[str, str] = {}

        if isinstance(entity_list, dict):
            entities = {k: str(v) for k, v in entity_list.items()}  # Type-safe copy
        elif isinstance(entity_list, list):
            # Build entity mapping from list
            for entity_info in entity_list:
                if isinstance(entity_info, dict):
                    name = entity_info.get("name")
                    url = entity_info.get("url") or entity_info.get("href")
                    if name and url and isinstance(name, str) and isinstance(url, str):
                        entities[name] = url
                elif isinstance(entity_info, str):
                    # Simple entity name - construct URL
                    entities[entity_info] = f"{self.entity_endpoint}/{entity_info}"

        return entities

    def _process_list_response(self, data: list[object]) -> dict[str, str]:
        """Process list format API response.

        Args:
            data: List response from API

        Returns:
            Dictionary mapping entity names to URLs

        """
        entities: dict[str, str] = {}

        # List format - build entity mapping
        for entity_info in data:
            if isinstance(entity_info, dict):
                name = entity_info.get("name")
                url = entity_info.get("url") or entity_info.get("href")
                if name and url and isinstance(name, str) and isinstance(url, str):
                    entities[name] = url
            elif isinstance(entity_info, str):
                # Simple entity name - construct URL
                entities[entity_info] = f"{self.entity_endpoint}/{entity_info}"

        logger.info("Using list format (%d entities)", len(entities))
        return entities

    async def _fetch_entity_metadata(self, entity_name: str) -> dict[str, Any] | None:
        """Fetch metadata for a specific entity.

        Args:
            entity_name: Name of the entity to fetch metadata for

        Returns:
            Entity metadata dictionary or None if not found

        Raises:
            EntityDescriptionError: If metadata fetching fails

        """
        metadata_url = f"{self.entity_endpoint}{entity_name}/describe"
        try:
            auth_headers = self._prepare_auth_headers()

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(
                    metadata_url,
                    headers=auth_headers,
                )

                if response.status_code == HTTP_NOT_FOUND:
                    logger.warning("Entity metadata not found: %s", entity_name)
                    return None

                response.raise_for_status()
                metadata_result = response.json()
                return dict(metadata_result) if metadata_result else None

        except httpx.HTTPError as e:
            logger.exception(
                "Failed to fetch metadata for entity %s",
                entity_name,
            )
            msg = f"HTTP error during entity metadata fetch: {e}"
            raise EntityDescriptionError(
                msg,
            ) from e
        except Exception as e:
            logger.exception("Unexpected error during entity metadata fetch")
            msg = f"Entity metadata fetch failed: {e}"
            raise EntityDescriptionError(msg) from e

    @staticmethod
    def _matches_patterns(entity_name: str, patterns: list[str]) -> bool:
        """Check if entity name matches any of the given patterns.

        Args:
            entity_name: Name of the entity to check
            patterns: List of regex patterns to match against

        Returns:
            True if entity name matches any pattern, False otherwise

        """
        for pattern in patterns:
            try:
                if re.search(pattern, entity_name, re.IGNORECASE):
                    return True
            except re.error:
                # Treat invalid regex as literal string match
                if pattern.lower() in entity_name.lower():
                    return True
        return False
