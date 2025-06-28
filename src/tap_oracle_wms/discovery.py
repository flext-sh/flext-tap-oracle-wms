"""Dynamic entity discovery for Oracle WMS."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import fnmatch
import logging
from typing import Any

import httpx

from .auth import get_wms_authenticator, get_wms_headers
from .config import HTTP_FORBIDDEN, HTTP_NOT_FOUND, HTTP_OK
from .logging_config import (
    get_logger,
    log_exception_context,
    log_function_entry_exit,
    performance_monitor,
)


# Use enhanced logger with TRACE support
logger = get_logger(__name__)


class EntityDiscovery:
    """Handle dynamic entity discovery from Oracle WMS API."""

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize entity discovery.

        Args:
        ----
            config: Configuration dictionary

        """
        logger.info("Initializing Oracle WMS Entity Discovery")
        logger.debug("Discovery config: base_url=%s", config.get("base_url", "None"))
        logger.trace("Starting entity discovery setup")

        self.config = config
        self.base_url = config["base_url"].rstrip("/")
        self.api_version = "v10"  # Current stable version

        logger.debug("Entity discovery URL: %s/wms/lgfapi/%s",
                     self.base_url, self.api_version)
        logger.trace("Setting up WMS headers")

        self.headers = get_wms_headers(config)
        logger.debug("WMS headers configured: %d items", len(self.headers))

        # Add authentication
        logger.trace("Setting up authentication for discovery")
        self._authenticator = None
        self._setup_authentication()

        # Enhanced cache for discovered entities with comprehensive caching
        logger.trace("Initializing discovery caches")
        self._entity_cache: dict[str, str] | None = None
        self._schema_cache: dict[str, dict[str, Any]] = {}
        self._access_cache: dict[str, bool] = {}
        self._sample_cache: dict[str, list[dict[str, Any]]] = {}
        self._metadata_cache: dict[str, dict[str, Any]] = {}

        # Cache configuration
        self._cache_ttl = config.get("schema_cache_ttl", 3600)
        self._entity_cache_ttl = config.get(
            "entity_cache_ttl",
            7200,
        )  # 2 hours for entity discovery

        logger.debug("Cache configuration: schema_ttl=%ds, entity_ttl=%ds",
                    self._cache_ttl, self._entity_cache_ttl)
        logger.trace("Discovery caches initialized")

        logger.info("Oracle WMS Entity Discovery initialized successfully")
        self._access_cache_ttl = config.get(
            "access_cache_ttl",
            1800,
        )  # 30 minutes for access checks

        # Cache timestamps
        self._last_cache_time: datetime | None = None
        self._last_entity_cache_time: datetime | None = None
        self._access_cache_times: dict[str, datetime] = {}
        self._sample_cache_times: dict[str, datetime] = {}
        self._metadata_cache_times: dict[str, datetime] = {}

    @log_exception_context(reraise=True)
    @performance_monitor("discovery_auth_setup")
    def _setup_authentication(self) -> None:
        """Set up authentication headers."""
        logger.debug("Setting up authentication for entity discovery")
        logger.trace("Creating stream context for authenticator")

        try:
            # Create a minimal stream context for authenticator
            logger.trace("Building minimal stream context")
            stream_context = type(
                "StreamContext",
                (),
                {
                    "config": self.config,
                    "tap_name": "tap-oracle-wms",
                    "logger": logger,
                },
            )()

            logger.debug("Getting WMS authenticator")
            logger.trace("Requesting authenticator with discovery context")

            auth = get_wms_authenticator(stream_context, self.config)
            if auth:
                logger.debug("Authenticator created, extracting headers")
                logger.trace("Getting auth_headers from authenticator")

                auth_headers = getattr(auth, "auth_headers", {})
                if auth_headers:
                    logger.debug("Auth headers obtained: %d items", len(auth_headers))
                    logger.trace("Auth header keys: %s", list(auth_headers.keys()))
                    self.headers.update(auth_headers)
                    logger.debug("Authentication headers updated successfully")
                else:
                    logger.debug("No auth headers returned from authenticator")
                    logger.trace("Authenticator exists but returned empty headers")
            else:
                logger.debug("No authenticator configured")
                logger.trace("Proceeding without authentication")

        except (ImportError, AttributeError, ValueError, TypeError) as e:
            logger.warning("Failed to setup authentication: %s", str(e))
            logger.trace("Authentication setup failed, continuing without auth")
            logger.exception("Full authentication setup error details")
            # Continue without auth - basic auth will be used via headers

    @property
    @log_exception_context(reraise=True)
    def entity_endpoint(self) -> str:
        """Get the entity discovery endpoint.

        Returns:
        -------
            Full URL for entity endpoint

        """
        logger.trace("Building entity discovery endpoint")
        endpoint = f"{self.base_url}/wms/lgfapi/{self.api_version}/entity/"
        logger.trace("Entity endpoint: %s", endpoint)
        return endpoint

    @log_function_entry_exit(log_args=False, log_result=True, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("discover_entities")
    async def discover_entities(self) -> dict[str, str]:
        """Discover all available entities from WMS API.

        Returns:
        -------
            Dictionary mapping entity names to their URLs

        Raises:
        ------
            HTTPError: If API request fails

        """
        logger.info("Starting Oracle WMS entity discovery")
        logger.trace("Checking entity cache validity")

        # Check enhanced entity cache
        if (
            self._entity_cache
            and self._last_entity_cache_time
            and datetime.now(timezone.utc) - self._last_entity_cache_time
            < timedelta(seconds=self._entity_cache_ttl)
        ):
            cache_age = datetime.now(timezone.utc) - self._last_entity_cache_time
            logger.debug("Using cached entity list (age: %s seconds)",
                         cache_age.total_seconds())
            logger.trace("Cached entities: %d items", len(self._entity_cache))
            return self._entity_cache

        logger.info("Cache miss or expired, discovering entities from Oracle WMS API")
        logger.debug("Entity discovery endpoint: %s", self.entity_endpoint)
        logger.trace("Setting up HTTP client configuration")

        # Setup timeouts
        logger.debug("Configuring HTTP timeouts for entity discovery")
        timeout = httpx.Timeout(
            connect=self.config.get("connect_timeout", 30),
            read=self.config.get("read_timeout", 120),
            write=self.config.get("write_timeout", 30),
            pool=self.config.get("pool_timeout", 10),
        )
        logger.trace("Timeouts: connect=%ds, read=%ds, write=%ds, pool=%ds",
                    timeout.connect, timeout.read, timeout.write, timeout.pool)

        # SSL configuration
        logger.debug("Configuring SSL verification")
        verify_ssl = self.config.get("verify_ssl", True)
        if not verify_ssl:
            logger.warning("SSL verification disabled")
            verify_ssl = False
        elif self.config.get("ssl_ca_file"):
            logger.debug("Using custom SSL CA file: %s", self.config["ssl_ca_file"])
            logger.trace("Creating SSL context with custom CA")
            import ssl

            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(self.config["ssl_ca_file"])
            verify_ssl = ssl_context
            logger.trace("SSL context configured successfully")
        else:
            logger.trace("Using default SSL verification")

        logger.debug("Creating HTTP client for entity discovery")
        logger.trace("Client config: SSL=%s, User-Agent=%s",
                    bool(verify_ssl),
                    self.config.get("user_agent", "tap-oracle-wms/1.0"))

        async with httpx.AsyncClient(
            timeout=timeout,
            verify=verify_ssl,
            headers={"User-Agent": self.config.get("user_agent", "tap-oracle-wms/1.0")},
        ) as client:
            try:
                logger.debug("Making GET request to entity discovery endpoint")
                logger.trace("Request headers: %d items", len(self.headers))

                response = await client.get(
                    self.entity_endpoint,
                    headers=self.headers,
                )

                logger.debug("Entity discovery response: %d %s",
                            response.status_code, response.reason_phrase)
                logger.trace("Response headers: %d items", len(response.headers))

                response.raise_for_status()

                logger.trace("Parsing entity discovery response JSON")
                entity_list = response.json()
                logger.debug("Entity list type: %s", type(entity_list).__name__)

                # Convert list of entity names to dictionary mapping names to URLs
                logger.trace("Converting entity list to URL mapping")
                entities: dict[str, str] = {}

                if isinstance(entity_list, list):
                    logger.debug("Processing entity list with %d items",
                                len(entity_list))
                    base_url = f"{self.base_url}/wms/lgfapi/{self.api_version}/entity"
                    logger.trace("Base entity URL: %s", base_url)

                    for entity_name in entity_list:
                        if isinstance(entity_name, str):
                            entities[entity_name] = f"{base_url}/{entity_name}"
                            logger.trace("Mapped entity: %s", entity_name)
                        else:
                            logger.warning("Skipping non-string entity: %s",
                                           entity_name)

                elif isinstance(entity_list, dict):
                    logger.debug("Using entity dict directly with %d items",
                                len(entity_list))
                    # If API returns dict directly, use it
                    entities = entity_list
                else:
                    logger.error("Unexpected entity list type: %s",
                                type(entity_list).__name__)
                    logger.trace("Entity list content: %s", str(entity_list)[:200])

                # Cache the results with enhanced caching
                logger.debug("Caching entity discovery results")
                self._entity_cache = entities
                self._last_entity_cache_time = datetime.now(timezone.utc)
                logger.trace("Cache updated at: %s", self._last_entity_cache_time)

                logger.info("Successfully discovered %d entities from Oracle WMS",
                            len(entities))
                logger.debug("Entities discovered: %s",
                            list(entities.keys())[:10])  # First 10
                return entities

            except httpx.HTTPStatusError as e:
                logger.exception("HTTP error during entity discovery: %d %s",
                            e.response.status_code, e.response.reason_phrase)
                logger.debug("Failed endpoint: %s", self.entity_endpoint)
                logger.trace("Response content: %s", e.response.text[:500])
                logger.exception("Full HTTP error details")
                raise
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ) as e:
                logger.exception("Network error during entity discovery: %s", str(e))
                logger.debug("Failed endpoint: %s", self.entity_endpoint)
                logger.exception("Full network error details")
                raise
            except (ValueError, KeyError, TypeError) as e:
                logger.exception("Data parsing error during entity discovery: %s", str(e))
                logger.debug("Response parsing failed for entity list")
                logger.exception("Full parsing error details")
                raise

    @log_function_entry_exit(log_args=True, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("describe_entity")
    async def describe_entity(self, entity_name: str) -> dict[str, Any] | None:
        """Get entity metadata from describe endpoint.

        Args:
        ----
            entity_name: Name of the entity

        Returns:
        -------
            Entity metadata including field definitions

        """
        logger.info("Starting entity metadata description for: %s", entity_name)
        logger.debug("Describe entity: checking metadata cache")
        logger.trace("Entity describe entry point reached")
        logger.trace("Metadata cache size: %d entries", len(self._metadata_cache))

        # Check enhanced metadata cache
        logger.trace("Checking if entity exists in metadata cache")
        if entity_name in self._metadata_cache:
            logger.trace("Entity found in cache, checking timestamp")
            cache_time = self._metadata_cache_times.get(entity_name)
            logger.trace("Cache time for entity: %s", cache_time)

            if cache_time and datetime.now(timezone.utc) - cache_time < timedelta(
                seconds=self._cache_ttl,
            ):
                cache_age = datetime.now(timezone.utc) - cache_time
                logger.debug("Using cached metadata for entity: %s (age: %ss)",
                           entity_name, cache_age.total_seconds())
                logger.trace("Returning cached metadata for entity: %s", entity_name)
                return self._metadata_cache[entity_name]
            logger.trace("Cached metadata expired for entity: %s", entity_name)
        else:
            logger.trace("Entity not found in metadata cache: %s", entity_name)

        logger.debug("Making API request to describe entity: %s", entity_name)
        url = f"{self.entity_endpoint}/{entity_name}/describe/"
        logger.trace("Describe endpoint URL: %s", url)

        logger.trace("Creating HTTP client for describe request")
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.trace("Sending GET request to describe endpoint")
                logger.trace("Request headers count: %d", len(self.headers))

                response = await client.get(url, headers=self.headers)
                logger.debug("Describe response status: %d", response.status_code)
                logger.trace("Response headers count: %d", len(response.headers))

                response.raise_for_status()

                logger.trace("Parsing describe response JSON")
                metadata: dict[str, Any] = response.json()
                logger.debug("Metadata retrieved for entity: %s", entity_name)
                logger.trace("Metadata keys: %s", list(metadata.keys()) if metadata else [])

                # Cache the result with enhanced caching
                logger.trace("Caching metadata for entity: %s", entity_name)
                self._metadata_cache[entity_name] = metadata
                self._metadata_cache_times[entity_name] = datetime.now(timezone.utc)
                logger.trace("Metadata cached successfully")

                logger.info("Entity metadata description completed for: %s", entity_name)
                return metadata

            except httpx.HTTPStatusError as e:
                logger.exception("HTTP error describing entity %s: %d %s",
                           entity_name, e.response.status_code, e.response.reason_phrase)
                logger.warning("Failed to describe entity %s: %s", entity_name, e)
                logger.trace("HTTP status error details: %s", str(e))
                return None
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ) as e:
                logger.exception("Network error describing entity %s: %s", entity_name, str(e))
                logger.exception("Network error describing entity")
                logger.trace("Network error type: %s", type(e).__name__)
                return None
            except (ValueError, KeyError, TypeError) as e:
                logger.exception("Data parsing error describing entity %s: %s", entity_name, str(e))
                logger.exception("Data parsing error describing entity")
                logger.trace("Parsing error type: %s", type(e).__name__)
                return None

    @log_function_entry_exit(log_args=True, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("get_entity_sample")
    async def get_entity_sample(
        self,
        entity_name: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Get sample records from entity for schema inference with caching.

        Args:
        ----
            entity_name: Name of the entity
            limit: Number of sample records to fetch

        Returns:
        -------
            List of sample records

        """
        logger.info("Starting entity sample retrieval for: %s (limit: %d)", entity_name, limit)
        logger.debug("Get entity sample: checking sample cache")
        logger.trace("Entity sample entry point reached")
        logger.trace("Sample cache size: %d entries", len(self._sample_cache))

        # Check enhanced sample cache
        cache_key = "%s_%d" % (entity_name, limit)
        logger.trace("Sample cache key: %s", cache_key)

        if cache_key in self._sample_cache:
            logger.trace("Sample found in cache, checking timestamp")
            cache_time = self._sample_cache_times.get(cache_key)
            logger.trace("Sample cache time: %s", cache_time)

            if cache_time and datetime.now(timezone.utc) - cache_time < timedelta(
                seconds=self._cache_ttl,
            ):
                cache_age = datetime.now(timezone.utc) - cache_time
                logger.debug("Using cached sample data for entity: %s (age: %ss)",
                           entity_name, cache_age.total_seconds())
                logger.trace("Returning cached sample for entity: %s", entity_name)
                return self._sample_cache[cache_key]
            logger.trace("Cached sample expired for entity: %s", entity_name)
        else:
            logger.trace("Entity not found in sample cache: %s", entity_name)

        logger.debug("Making API request to get sample for entity: %s", entity_name)
        url = f"{self.entity_endpoint}/{entity_name}"
        params = {"page_size": limit, "page": 1}
        logger.trace("Sample endpoint URL: %s", url)
        logger.trace("Sample request params: %s", params)

        logger.trace("Creating HTTP client for sample request")
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.trace("Sending GET request to sample endpoint")
                logger.trace("Request headers count: %d", len(self.headers))

                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                )
                logger.debug("Sample response status: %d", response.status_code)
                logger.trace("Response headers count: %d", len(response.headers))

                response.raise_for_status()

                logger.trace("Parsing sample response JSON")
                data = response.json()
                logger.trace("Sample data type: %s", type(data).__name__)

                # Handle different response formats
                sample_data: list[dict[str, Any]]
                logger.trace("Processing sample data format")

                if isinstance(data, dict) and "results" in data:
                    logger.trace("Sample data format: dict with results key")
                    sample_data = data["results"]
                    logger.trace("Extracted %d records from results", len(sample_data))
                elif isinstance(data, list):
                    logger.trace("Sample data format: direct list")
                    sample_data = data[:limit]
                    logger.trace("Using first %d records from list", len(sample_data))
                else:
                    logger.trace("Sample data format: unknown, returning empty list")
                    sample_data = []

                logger.debug("Sample retrieved for entity %s: %d records", entity_name, len(sample_data))

                # Cache the sample data
                logger.trace("Caching sample data for entity: %s", entity_name)
                self._sample_cache[cache_key] = sample_data
                self._sample_cache_times[cache_key] = datetime.now(timezone.utc)
                logger.trace("Sample data cached successfully")

                logger.info("Entity sample retrieval completed for: %s (%d records)",
                          entity_name, len(sample_data))
                return sample_data

            except httpx.HTTPStatusError as e:
                if e.response.status_code == HTTP_NOT_FOUND:
                    logger.warning("Entity %s not found for sampling", entity_name)
                    logger.debug("Entity %s not found for sampling", entity_name)
                    logger.trace("404 Not Found for entity: %s", entity_name)
                else:
                    logger.exception("HTTP error getting sample for %s: %d %s",
                               entity_name, e.response.status_code, e.response.reason_phrase)
                    logger.warning(
                        "HTTP error getting sample for %s: %s",
                        entity_name,
                        e,
                    )
                    logger.trace("HTTP error details: %s", str(e))
                return []
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ) as e:
                logger.exception("Network error getting sample for entity %s: %s", entity_name, str(e))
                logger.warning(
                    "Network error getting sample for entity %s: %s",
                    entity_name,
                    e,
                )
                logger.trace("Network error type: %s", type(e).__name__)
                return []
            except (ValueError, KeyError, TypeError) as e:
                logger.exception("Data parsing error getting sample for entity %s: %s", entity_name, str(e))
                logger.warning(
                    "Data parsing error getting sample for entity %s: %s",
                    entity_name,
                    e,
                )
                logger.trace("Parsing error type: %s", type(e).__name__)
                return []

    @log_function_entry_exit(log_args=True, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    @performance_monitor("filter_entities")
    def filter_entities(self, entities: dict[str, str]) -> dict[str, str]:
        """Filter entities based on configuration.

        Args:
        ----
            entities: Dictionary of discovered entities

        Returns:
        -------
            Filtered dictionary of entities

        """
        logger.info("Starting entity filtering process")
        logger.debug("Filter entities: input count=%d", len(entities))
        logger.trace("Entity filtering entry point reached")
        logger.trace("Input entities: %s", list(entities.keys())[:10])  # First 10

        # If specific entities are configured, use only those
        logger.trace("Checking for specific configured entities")
        if self.config.get("entities"):
            configured_entities = self.config["entities"]
            logger.debug("Applying specific entity filter: %d configured", len(configured_entities))
            logger.trace("Configured entities: %s", configured_entities)

            filtered_result = {
                name: url
                for name, url in entities.items()
                if name in configured_entities
            }
            logger.info("Entity filtering completed: %d -> %d (specific entities)",
                       len(entities), len(filtered_result))
            logger.trace("Filtered entities (specific): %s", list(filtered_result.keys()))
            return filtered_result
        logger.trace("No specific entities configured, proceeding with pattern filtering")

        # Apply pattern-based filtering
        logger.debug("Applying pattern-based entity filtering")
        logger.trace("Starting with all entities for pattern filtering")
        filtered = dict(entities)

        patterns = self.config.get("entity_patterns", {})
        logger.trace("Entity patterns config: %s", patterns)

        # Apply include patterns
        logger.trace("Checking for include patterns")
        if patterns.get("include"):
            include_patterns = patterns["include"]
            logger.debug("Applying include patterns: %s", include_patterns)
            logger.trace("Include patterns count: %d", len(include_patterns))

            filtered = {
                name: url
                for name, url in filtered.items()
                if any(
                    fnmatch.fnmatch(name, pattern) for pattern in include_patterns
                )
            }
            logger.debug("After include patterns: %d entities remain", len(filtered))
            logger.trace("Entities after include: %s", list(filtered.keys())[:10])
        else:
            logger.trace("No include patterns configured")

        # Apply exclude patterns
        logger.trace("Checking for exclude patterns")
        if patterns.get("exclude"):
            exclude_patterns = patterns["exclude"]
            logger.debug("Applying exclude patterns: %s", exclude_patterns)
            logger.trace("Exclude patterns count: %d", len(exclude_patterns))

            pre_exclude_count = len(filtered)
            filtered = {
                name: url
                for name, url in filtered.items()
                if not any(
                    fnmatch.fnmatch(name, pattern) for pattern in exclude_patterns
                )
            }
            logger.debug("After exclude patterns: %d -> %d entities", pre_exclude_count, len(filtered))
            logger.trace("Entities after exclude: %s", list(filtered.keys())[:10])
        else:
            logger.trace("No exclude patterns configured")

        # Always exclude system/internal entities
        logger.debug("Applying system entity exclusion")
        system_prefixes = ["_", "sys_", "internal_"]
        logger.trace("System prefixes to exclude: %s", system_prefixes)

        pre_system_count = len(filtered)
        filtered_result = {
            name: url
            for name, url in filtered.items()
            if not any(name.startswith(prefix) for prefix in system_prefixes)
        }
        logger.debug("After system exclusion: %d -> %d entities", pre_system_count, len(filtered_result))
        logger.trace("Final filtered entities: %s", list(filtered_result.keys())[:10])

        logger.info("Entity filtering completed: %d -> %d entities", len(entities), len(filtered_result))
        return filtered_result

    async def check_entity_access(self, entity_name: str) -> bool:
        """Check if user has access to entity with caching.

        Args:
        ----
            entity_name: Name of the entity

        Returns:
        -------
            True if entity is accessible

        """
        # Check enhanced access cache
        if entity_name in self._access_cache:
            cache_time = self._access_cache_times.get(entity_name)
            if cache_time and datetime.now(timezone.utc) - cache_time < timedelta(
                seconds=self._access_cache_ttl,
            ):
                logger.debug("Using cached access result for entity: %s", entity_name)
                return self._access_cache[entity_name]
        url = f"{self.entity_endpoint}/{entity_name}"
        params = {"page_size": 1, "page": 1}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                )
                access_result = response.status_code == HTTP_OK

                # Cache the access result
                self._access_cache[entity_name] = access_result
                self._access_cache_times[entity_name] = datetime.now(timezone.utc)

                return access_result

            except httpx.HTTPStatusError as e:
                if e.response.status_code == HTTP_FORBIDDEN:
                    logger.warning("No access to entity %s", entity_name)
                    access_result = False
                else:
                    access_result = False

                # Cache negative results too
                self._access_cache[entity_name] = access_result
                self._access_cache_times[entity_name] = datetime.now(timezone.utc)

                return access_result
            except Exception:
                # Don't cache exceptions, allow retry
                return False

    async def estimate_entity_size(self, entity_name: str) -> int | None:
        """Estimate the number of records in an entity.

        Args:
        ----
            entity_name: Name of the entity

        Returns:
        -------
            Estimated record count or None

        """
        url = f"{self.entity_endpoint}/{entity_name}"
        params = {"page_size": 1, "page": 1}

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                )
                response.raise_for_status()

                data = response.json()

                # Look for count in response
                if isinstance(data, dict):
                    return (
                        data.get("result_count")
                        or data.get("count")
                        or data.get("total")
                    )

                return None

            except httpx.HTTPStatusError as e:
                if e.response.status_code == HTTP_NOT_FOUND:
                    logger.debug("Entity %s size estimation not supported", entity_name)
                else:
                    logger.warning(
                        "HTTP error estimating size for entity %s: %s",
                        entity_name,
                        e,
                    )
                return None
            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.RequestError,
            ) as e:
                logger.warning(
                    "Network error estimating size for entity %s: %s",
                    entity_name,
                    e,
                )
                return None
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(
                    "Data parsing error estimating size for entity %s: %s",
                    entity_name,
                    e,
                )
                return None

    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear cached data.

        Args:
        ----
            cache_type: Type of cache to clear
                ("all", "entities", "metadata", "samples", "access")

        """
        if cache_type in {"all", "entities"}:
            self._entity_cache = None
            self._last_entity_cache_time = None
            logger.info("Cleared entity cache")

        if cache_type in {"all", "metadata"}:
            self._metadata_cache.clear()
            self._metadata_cache_times.clear()
            logger.info("Cleared metadata cache")

        if cache_type in {"all", "samples"}:
            self._sample_cache.clear()
            self._sample_cache_times.clear()
            logger.info("Cleared sample cache")

        if cache_type in {"all", "access"}:
            self._access_cache.clear()
            self._access_cache_times.clear()
            logger.info("Cleared access cache")

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
        -------
            Dictionary with cache statistics

        """
        current_time = datetime.now(timezone.utc)

        # Calculate cache hit ratios and sizes
        return {
            "entity_cache": {
                "cached": self._entity_cache is not None,
                "last_updated": (
                    self._last_entity_cache_time.isoformat()
                    if self._last_entity_cache_time
                    else None
                ),
                "ttl_seconds": self._entity_cache_ttl,
                "valid": bool(
                    self._entity_cache
                    and self._last_entity_cache_time
                    and current_time - self._last_entity_cache_time
                    < timedelta(seconds=self._entity_cache_ttl),
                ),
            },
            "metadata_cache": {
                "entries": len(self._metadata_cache),
                "ttl_seconds": self._cache_ttl,
                "valid_entries": sum(
                    1
                    for entity_name, cache_time in self._metadata_cache_times.items()
                    if current_time - cache_time < timedelta(seconds=self._cache_ttl)
                ),
            },
            "sample_cache": {
                "entries": len(self._sample_cache),
                "ttl_seconds": self._cache_ttl,
                "valid_entries": sum(
                    1
                    for cache_key, cache_time in self._sample_cache_times.items()
                    if current_time - cache_time < timedelta(seconds=self._cache_ttl)
                ),
            },
            "access_cache": {
                "entries": len(self._access_cache),
                "ttl_seconds": self._access_cache_ttl,
                "valid_entries": sum(
                    1
                    for entity_name, cache_time in self._access_cache_times.items()
                    if current_time - cache_time
                    < timedelta(seconds=self._access_cache_ttl)
                ),
            },
        }

    def cleanup_expired_cache(self) -> None:
        """Clean up expired cache entries to prevent memory bloat."""
        current_time = datetime.now(timezone.utc)

        # Clean expired metadata cache
        expired_metadata = [
            entity_name
            for entity_name, cache_time in self._metadata_cache_times.items()
            if current_time - cache_time >= timedelta(seconds=self._cache_ttl)
        ]
        for entity_name in expired_metadata:
            self._metadata_cache.pop(entity_name, None)
            self._metadata_cache_times.pop(entity_name, None)

        # Clean expired sample cache
        expired_samples = [
            cache_key
            for cache_key, cache_time in self._sample_cache_times.items()
            if current_time - cache_time >= timedelta(seconds=self._cache_ttl)
        ]
        for cache_key in expired_samples:
            self._sample_cache.pop(cache_key, None)
            self._sample_cache_times.pop(cache_key, None)

        # Clean expired access cache
        expired_access = [
            entity_name
            for entity_name, cache_time in self._access_cache_times.items()
            if current_time - cache_time >= timedelta(seconds=self._access_cache_ttl)
        ]
        for entity_name in expired_access:
            self._access_cache.pop(entity_name, None)
            self._access_cache_times.pop(entity_name, None)

        if expired_metadata or expired_samples or expired_access:
            logger.debug(
                "Cleaned up %d metadata, %d sample, %d access entries",
                len(expired_metadata),
                len(expired_samples),
                len(expired_access),
            )


class SchemaGenerator:
    """Generate Singer schemas from WMS entity metadata."""

    # Map WMS types to Singer/JSON Schema types
    TYPE_MAPPING = {
        "integer": "integer",
        "string": "string",
        "number": "number",
        "decimal": "number",
        "float": "number",
        "boolean": "boolean",
        "datetime": "string",  # with format
        "date": "string",  # with format
        "time": "string",  # with format
        "array": "array",
        "object": "object",
        "text": "string",
        "char": "string",
        "varchar": "string",
    }

    def generate_from_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Generate schema from entity describe metadata.

        Args:
        ----
            metadata: Entity metadata from describe endpoint

        Returns:
        -------
            Singer-compatible schema

        """
        properties: dict[str, Any] = {}
        required_fields: list[str] = []

        # The describe endpoint returns field names in "parameters"
        # and definitions in "fields"
        field_names = metadata.get("parameters", [])
        field_definitions = metadata.get("fields", {})

        for field_name in field_names:
            if field_name in field_definitions:
                field_def = field_definitions[field_name]
                # Create property definition
                prop = self._create_property_from_field(field_name, field_def)
                properties[field_name] = prop

                # Track required fields
                if field_def.get("required", False):
                    required_fields.append(field_name)
            else:
                # Default property for fields without definition
                properties[field_name] = {"type": ["string", "null"]}

        # Build schema
        schema = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }

        if required_fields:
            schema["required"] = required_fields

        return schema

    def generate_from_sample(self, samples: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate schema by inferring from sample data.

        Args:
        ----
            samples: List of sample records

        Returns:
        -------
            Singer-compatible schema

        """
        if not samples:
            return {"type": "object", "properties": {}}

        # Analyze all samples to build complete schema
        properties: dict[str, Any] = {}

        for sample in samples:
            for field_name, value in sample.items():
                if field_name not in properties:
                    properties[field_name] = self._infer_type(value)
                else:
                    # Update type if needed (handle nulls, mixed types)
                    current_type = properties[field_name]
                    new_type = self._infer_type(value)
                    properties[field_name] = self._merge_types(current_type, new_type)

        return {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }

    def _create_property_from_field(
        self,
        field_name: str,
        field_def: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a property definition from field definition.

        Args:
        ----
            field_name: Field name
            field_def: Field definition from describe endpoint

        Returns:
        -------
            Property definition

        """
        field_type = field_def.get("type", "string").lower()
        base_type = self.TYPE_MAPPING.get(field_type, "string")

        base_prop = {"type": base_type}

        # Add description if available
        if field_def.get("description"):
            base_prop["description"] = field_def["description"]

        # Add constraints for base type
        if base_type == "string":
            if field_def.get("max_length"):
                base_prop["maxLength"] = field_def["max_length"]

            # Add format for date/time types
            if field_type in {"datetime", "timestamp"}:
                base_prop["format"] = "date-time"
            elif field_type == "date":
                base_prop["format"] = "date"
            elif field_type == "time":
                base_prop["format"] = "time"

        elif base_type in {"number", "integer"}:
            if field_def.get("min_value") is not None:
                base_prop["minimum"] = field_def["min_value"]
            if field_def.get("max_value") is not None:
                base_prop["maximum"] = field_def["max_value"]

        # Handle enums
        if field_def.get("choices"):
            base_prop["enum"] = field_def["choices"]

        # Handle default values
        if field_def.get("default") is not None:
            base_prop["default"] = field_def["default"]

        # Handle nullable fields by wrapping in anyOf
        if not field_def.get("required", True):
            return {"anyOf": [base_prop, {"type": "null"}]}

        return base_prop

    def _create_property(self, param: dict[str, Any]) -> dict[str, Any]:
        """Create a property definition from parameter metadata.

        Args:
        ----
            param: Parameter metadata

        Returns:
        -------
            Property definition

        """
        field_type = param.get("type", "string").lower()
        base_type = self.TYPE_MAPPING.get(field_type, "string")

        base_prop = {"type": base_type}

        # Add description if available
        if param.get("help_text"):
            base_prop["description"] = param["help_text"]
        elif param.get("description"):
            base_prop["description"] = param["description"]

        # Add constraints
        if base_type == "string":
            if param.get("max_length"):
                base_prop["maxLength"] = param["max_length"]

            # Add format for date/time types
            if field_type in {"datetime", "timestamp"}:
                base_prop["format"] = "date-time"
            elif field_type == "date":
                base_prop["format"] = "date"
            elif field_type == "time":
                base_prop["format"] = "time"

        elif base_type in {"number", "integer"}:
            if param.get("min_value") is not None:
                base_prop["minimum"] = param["min_value"]
            if param.get("max_value") is not None:
                base_prop["maximum"] = param["max_value"]

        # Handle enums
        if param.get("choices"):
            base_prop["enum"] = param["choices"]

        # Handle default values
        if param.get("default") is not None:
            base_prop["default"] = param["default"]

        # Handle nullable fields by wrapping in anyOf
        if param.get("allow_blank") or param.get("required") == "N":
            return {"anyOf": [base_prop, {"type": "null"}]}

        return base_prop

    def _infer_type(self, value: Any) -> dict[str, Any]:
        """Infer JSON schema type from a value.

        Args:
        ----
            value: Sample value

        Returns:
        -------
            Type definition

        """
        if value is None:
            return {"type": "null"}

        if isinstance(value, bool):
            return {"type": "boolean"}

        if isinstance(value, int):
            return {"type": "integer"}

        if isinstance(value, float):
            return {"type": "number"}

        if isinstance(value, str):
            # Try to detect date/time formats
            if self._is_datetime(value):
                return {"type": "string", "format": "date-time"}
            if self._is_date(value):
                return {"type": "string", "format": "date"}
            return {"type": "string"}

        if isinstance(value, list):
            if value:
                # Infer array item type from first element
                item_type = self._infer_type(value[0])
                return {"type": "array", "items": item_type}
            return {"type": "array"}

        if isinstance(value, dict):
            return {"type": "object"}

        # Default to string for unknown types
        return {"type": "string"}

    def _merge_types(
        self,
        type1: dict[str, Any],
        type2: dict[str, Any],
    ) -> dict[str, Any]:
        """Merge two type definitions.

        Args:
        ----
            type1: First type definition
            type2: Second type definition

        Returns:
        -------
            Merged type definition

        """
        # If types are identical, return as-is
        if type1 == type2:
            return type1

        # Handle null types
        if type1.get("type") == "null":
            return {"anyOf": [type2, {"type": "null"}]}
        if type2.get("type") == "null":
            return {"anyOf": [type1, {"type": "null"}]}

        # If types differ, create a union
        return {"anyOf": [type1, type2]}

    def _is_datetime(self, value: str) -> bool:
        """Check if string value is a datetime."""
        try:
            # Common datetime formats
            for fmt in [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
            ]:
                dt = datetime.strptime(value, fmt)
                if dt.tzinfo is None:
                    # If no timezone info, assume UTC
                    dt = dt.replace(tzinfo=timezone.utc)
                return True
        except ValueError:
            pass
        return False

    def _is_date(self, value: str) -> bool:
        """Check if string value is a date."""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False
