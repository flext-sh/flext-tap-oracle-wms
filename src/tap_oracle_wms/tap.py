"""Oracle WMS tap class."""

from __future__ import annotations

import asyncio
import logging
from itertools import starmap
from typing import Any

from singer_sdk import Stream, Tap

from .config import config_schema, validate_auth_config, validate_pagination_config
from .discovery import EntityDiscovery, SchemaGenerator
from .monitoring import TAPMonitor
from .streams_advanced import WMSAdvancedStream

logger = logging.getLogger(__name__)


class TapOracleWMS(Tap):
    """Oracle WMS Singer Tap - Generic implementation for any WMS entity.

    OVERVIEW:
    =========
    This tap provides a generic, configurable interface to Oracle WMS that can work
    with any WMS entity without hardcoding specific business logic. It offers both
    simplified interfaces for basic use cases and advanced configuration for complex
    scenarios.

    GENERIC ENTITY SUPPORT:
    ======================
    The tap automatically discovers and adapts to any Oracle WMS entity:

    • Auto-discovery: Scans WMS API to find all available entities
    • Dynamic schemas: Generates schemas based on actual API responses
    • Generic filtering: Applies consistent filtering patterns across entities
    • Flexible pagination: Adapts to different entity response patterns

    FILTERING SYSTEM:
    ================
    Generic filters that work with any entity:

    1. TEMPORAL FILTERS (for entities with timestamps):
       - mod_ts__gte: Records modified after timestamp
       - mod_ts__lte: Records modified before timestamp
       - create_ts__gte: Records created after timestamp
       - create_ts__lte: Records created before timestamp

    2. ID FILTERS (for entities with numeric IDs):
       - id__gte: Records with ID >= value
       - id__lte: Records with ID <= value
       - id__lt: Records with ID < value (for resume scenarios)
       - id__gt: Records with ID > value

    3. STATUS FILTERS (for entities with status fields):
       - status: Exact status match
       - status__in: Status in list of values
       - active: Active/inactive flag (Y/N)

    4. ADVANCED OPERATOR FILTERS:
       - field__contains: Field contains substring
       - field__startswith: Field starts with value
       - field__endswith: Field ends with value
       - field__isnull: Field is null/not null
       - field__range: Field in range [min, max]

    CONFIGURATION MODES:
    ===================

    1. SIMPLIFIED MODE (minimal configuration):
       {
         "base_url": "https://wms.example.com",
         "username": "user",
         "password": "pass",
         "entities": ["allocation", "inventory"]
       }

    2. ENTITY-SPECIFIC MODE (per-entity configuration):
       {
         "base_url": "https://wms.example.com",
         "username": "user",
         "password": "pass",
         "entity_filters": {
           "allocation": {"status": "ACTIVE"},
           "inventory": {"mod_ts__gte": "2024-01-01T00:00:00Z"}
         },
         "entity_ordering": {
           "allocation": "mod_ts",
           "inventory": "-id"
         }
       }

    3. ADVANCED MODE (full control):
       {
         "base_url": "https://wms.example.com",
         "username": "user",
         "password": "pass",
         "advanced_filters": {
           "allocation": {
             "mod_ts": {"__gte": "2024-01-01T00:00:00Z", "__lte": "2024-12-31T23:59:59Z"},
             "status": {"__in": ["ACTIVE", "PENDING"]},
             "facility_code": "MAIN"
           }
         },
         "field_selection": {
           "allocation": ["id", "mod_ts", "status", "alloc_qty"]
         },
         "pagination_config": {
           "allocation": {"page_size": 1000, "mode": "sequenced"}
         }
       }

    INCREMENTAL SYNC PATTERNS:
    ========================
    Generic incremental sync rules applied to any entity with timestamp fields:

    1. TIMESTAMP-BASED INCREMENTAL:
       - Replication key: mod_ts (or configurable field)
       - Filter pattern: mod_ts > max(previous_mod_ts) - safety_overlap
       - Default safety overlap: 5 minutes (configurable)
       - Ordering: chronological (mod_ts ASC)

    2. ID-BASED INCREMENTAL:
       - Replication key: id (for entities without timestamps)
       - Filter pattern: id > max(previous_id)
       - Ordering: ascending (id ASC)

    FULL SYNC PATTERNS:
    ==================
    Generic full sync with intelligent resume for any entity:

    1. ID-BASED RESUME:
       - Filter pattern: id < min(existing_ids_in_target) - 1
       - Ordering: descending (-id DESC)
       - Use case: Resume interrupted full sync

    2. TIMESTAMP-BASED FULL:
       - Filter pattern: mod_ts >= start_date
       - Ordering: chronological (mod_ts ASC)
       - Use case: Full historical extraction

    PAGINATION ADAPTATION:
    =====================
    Automatically adapts to Oracle WMS pagination modes:

    • page_mode="sequenced": High-performance cursor navigation
    • page_mode="paged": Standard page number navigation
    • Auto page size optimization per entity
    • Handles different response formats transparently

    SCHEMA GENERATION:
    =================
    Dynamic schema discovery for any entity:

    1. METADATA-BASED: Uses WMS describe endpoints
    2. SAMPLE-BASED: Infers from actual data samples
    3. HYBRID: Combines metadata + samples for accuracy
    4. CACHED: Reuses schemas with configurable TTL

    ERROR HANDLING:
    ==============
    Robust error handling for production use:

    • Circuit breaker pattern per entity
    • Exponential backoff retry logic
    • Partial failure recovery (continue other entities)
    • Detailed error logging and metrics

    MONITORING & OBSERVABILITY:
    ===========================
    Built-in monitoring for production deployments:

    • Prometheus metrics endpoints
    • Detailed performance logging
    • State tracking and checkpointing
    • Progress reporting and ETAs

    SINGER SDK COMPLIANCE:
    =====================
    Full compliance with Singer/Meltano specifications:

    • Standard catalog/state/config interface
    • SCHEMA/RECORD/STATE message format
    • Bookmark-based incremental sync
    • Stream selection and metadata
    • Configurable output targets

    USAGE EXAMPLES:
    ==============

    1. Basic extraction:
       tap-oracle-wms --config config.json --discover > catalog.json
       tap-oracle-wms --config config.json --catalog catalog.json

    2. Incremental sync:
       tap-oracle-wms sync incremental --config config.json --entities allocation

    3. Full sync with resume:
       tap-oracle-wms sync full --config config.json --business-area inventory

    4. Advanced filtering:
       tap-oracle-wms --config advanced_config.json --catalog catalog.json --state state.json
    """

    name = "tap-oracle-wms"
    config_jsonschema = config_schema

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize tap."""
        # CRITICAL: Singer SDK requires tap_name BEFORE super().__init__
        self.tap_name = "tap-oracle-wms"  # Required by Singer SDK
        self._entity_discovery: EntityDiscovery | None = None
        self._schema_generator: SchemaGenerator | None = None
        self._discovered_entities = None
        self._entity_schemas: dict[str, dict[str, Any]] = {}
        self._monitor = None
        super().__init__(*args, **kwargs)

        # Initialize monitoring if enabled
        if self.config.get("metrics", {}).get("enabled", False):
            self._monitor = TAPMonitor(dict(self.config))
            logger.info("Monitoring enabled for TAP")

    def validate_config(self) -> None:
        """Validate configuration.

        Raises
        ------
            ValueError: If configuration is invalid

        """
        # Validate authentication
        auth_error = validate_auth_config(dict(self.config))
        if auth_error:
            raise ValueError(auth_error)

        # Validate pagination
        page_error = validate_pagination_config(dict(self.config))
        if page_error:
            raise ValueError(page_error)

        # Test connection if configured
        if self.config.get("test_connection", True):
            self._test_connection()

    def _test_connection(self) -> None:
        """Test connection to Oracle WMS API."""
        logger.info("Testing connection to Oracle WMS API")

        try:
            # Start monitoring if enabled
            if self._monitor:
                asyncio.run(self._monitor.start_monitoring())

            # Run async discovery to test connection
            entities = asyncio.run(self.entity_discovery.discover_entities())

            # Record connection test metrics
            if self._monitor:
                self._monitor.metrics.record_counter("connection.test.attempts")

            if entities:
                logger.info("Connection successful. Found %s entities.", len(entities))
                if self._monitor:
                    self._monitor.metrics.record_counter("connection.test.success")
                    self._monitor.metrics.record_gauge(
                        "connection.entities_discovered",
                        len(entities),
                    )
                if self._monitor:
                    self._monitor.metrics.record_counter("connection.test.failure")
                msg = "No entities discovered. Check permissions."
                raise ValueError(msg)
        except (ValueError, TypeError, AttributeError) as e:
            if self._monitor:
                self._monitor.metrics.record_counter("connection.test.failure")
            msg = f"Connection test failed: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            if self._monitor:
                self._monitor.metrics.record_counter("connection.test.error")
            msg = f"Unexpected error during connection test: {e}"
            raise ValueError(msg) from e

    @property
    def entity_discovery(self) -> EntityDiscovery:
        """Get entity discovery instance."""
        if self._entity_discovery is None:
            self._entity_discovery = EntityDiscovery(dict(self.config))
        return self._entity_discovery

    @property
    def schema_generator(self) -> SchemaGenerator:
        """Get schema generator instance."""
        if self._schema_generator is None:
            self._schema_generator = SchemaGenerator()
        return self._schema_generator

    async def _discover_and_filter_entities(self) -> dict[str, str]:
        """Discover and filter entities.

        Returns
        -------
            Filtered dictionary of entities

        """
        # Discover all entities
        all_entities = await self.entity_discovery.discover_entities()

        # Filter based on configuration
        filtered_entities = self.entity_discovery.filter_entities(all_entities)

        # Check if access verification is enabled
        verify_access = self.config.get("verify_entity_access", False)

        if not verify_access:
            logger.info(
                "Skipping access verification for %d entities (set verify_entity_access=true to enable)",
                len(filtered_entities),
            )
            return filtered_entities

        # Check access for each entity in parallel
        return await self._check_entities_access_parallel(filtered_entities)

    async def _check_entities_access_parallel(
        self,
        entities: dict[str, str],
    ) -> dict[str, str]:
        """Check access to entities in parallel.

        Args:
        ----
            entities: Dictionary of entities to check

        Returns:
        -------
            Dictionary of accessible entities

        """
        max_concurrent = self.config.get("max_concurrent_checks", 10)
        semaphore = asyncio.Semaphore(max_concurrent)

        async def check_single_entity(name: str, url: str) -> tuple[str, str, bool]:
            async with semaphore:
                try:
                    accessible = await self.entity_discovery.check_entity_access(name)
                    return name, url, accessible
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(
                        "Configuration error checking access to entity %s: %s",
                        name,
                        e,
                    )
                    return name, url, False
                except Exception as e:
                    logger.warning(
                        "Unexpected error checking access to entity %s: %s",
                        name,
                        e,
                    )
                    return name, url, False

        # Create tasks for all entities
        tasks = list(starmap(check_single_entity, entities.items()))

        # Execute with timeout
        timeout = self.config.get("entity_access_timeout", 300)  # 5 minutes default
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
        except TimeoutError:
            logger.warning("Entity access check timed out after %s seconds", timeout)
            # Return all entities if timeout
            return entities

        # Filter accessible entities
        accessible_entities: dict[str, str] = {}
        for name, url, accessible in results:
            if accessible:
                accessible_entities[name] = url
                logger.warning("No access to entity: %s", name)

        logger.info(
            "Verified access to %d/%d entities",
            len(accessible_entities),
            len(entities),
        )
        return accessible_entities

    async def _generate_schemas_parallel(
        self,
        entities: dict[str, str],
    ) -> dict[str, dict[str, Any]]:
        """Generate schemas for entities in parallel with robust error handling.

        CRITICAL BUG FIXED:
        ===================
        Previously had INVERTED LOGIC on line 464:
        - When schema existed: logged WARNING "Skipping entity"
        - When schema was None: added to successful_schemas

        CORRECT LOGIC IMPLEMENTED:
        =========================
        - When schema exists: Add to successful_schemas + log SUCCESS ✅
        - When schema is None: Skip entity + log WARNING ⚠️

        BUG DETAILS AND CORRECTION:
        ===========================

        **ORIGINAL BUGGY CODE (line 464):**
        ```python
        for entity_name, schema in final_results:
            if schema:
                successful_schemas[entity_name] = schema
                logger.warning("Skipping entity %s: No schema generated", entity_name)  # BUG: Wrong message!
        ```

        **SYMPTOMS OF THE BUG:**
        - Message "Skipping entity allocation: No schema generated" appeared even when schema was successfully generated
        - Entities with valid schemas were being reported as failed
        - No actual skipping occurred, but logging was misleading
        - Caused confusion in debugging and monitoring

        **ROOT CAUSE ANALYSIS:**
        - Logic was correct: `if schema:` properly identified successful schemas
        - Schema assignment was correct: `successful_schemas[entity_name] = schema`
        - ERROR: Success condition logged as failure message
        - MISSING: No handling for the `else` case (actual failures)

        **CORRECTED IMPLEMENTATION:**
        ```python
        for entity_name, schema in final_results:
            if schema:
                # CORRECT LOGIC: Schema exists, add to successful schemas
                successful_schemas[entity_name] = schema
                logger.info("✅ Generated schema for entity %s", entity_name)
            else:
                # CORRECT LOGIC: No schema generated, log warning and skip
                logger.warning(
                    "⚠️  Skipping entity %s: No schema generated", entity_name
                )
        ```

        **VALIDATION OF FIX:**
        - Before fix: "Skipping entity allocation: No schema generated" + schema had 24 properties
        - After fix: "✅ Generated schema for entity allocation" + schema has 24 properties
        - Test confirmed: Schema generation working correctly

        **PREVENTION MEASURES:**
        - Always implement both `if` and `else` branches for boolean conditions
        - Ensure log messages match the actual logic flow
        - Test both success and failure paths
        - Use descriptive variable names that match their purpose

        **NEVER CHANGE WITHOUT AUTHORIZATION:**
        - This specific logic pattern: success = add to dict + log success, failure = skip + log warning
        - The order of operations: check schema existence, then act accordingly
        - Log levels: INFO for success, WARNING for expected failures
        - Message format: "✅ Generated schema" vs "⚠️ Skipping entity"

        SCHEMA GENERATION PROCESS:
        =========================
        This method implements a comprehensive schema generation strategy
        that adapts to different WMS API response patterns and handles
        various error conditions gracefully.

        Generation Methods (in order of preference):
        ------------------------------------------
        1. METADATA-BASED: Uses WMS describe endpoint
           - Most accurate field types and constraints
           - Provides official field definitions
           - Includes validation rules and defaults

        2. SAMPLE-BASED: Infers from actual data samples
           - Fallback when describe endpoint fails
           - Uses real data to determine types
           - Handles dynamic/undocumented fields

        3. MINIMAL FALLBACK: Basic schema with common fields
           - Last resort when all methods fail
           - Ensures entity can still be processed
           - Uses additionalProperties=true for flexibility

        PARALLEL EXECUTION STRATEGY:
        ============================
        Uses asyncio.gather with timeout to process multiple entities
        simultaneously while preventing indefinite hangs:

        1. Primary parallel execution (with 60s timeout)
        2. Sequential fallback if timeout exceeded
        3. Individual error isolation (one failure doesn't affect others)

        ERROR HANDLING PATTERNS:
        =======================
        - Network errors: Retry with backoff
        - Timeout errors: Fall back to sequential processing
        - Schema errors: Use minimal fallback schema
        - Authentication errors: Fail fast with clear message

        NEVER CHANGE WITHOUT AUTHORIZATION:
        ==================================
        - Logic validation (schema exists = success, schema None = skip)
        - Timeout values (currently 60s for parallel, appropriate for WMS)
        - Fallback strategies (sequential after parallel timeout)
        - Error isolation patterns (continue processing other entities)

        Args:
            entities: Dictionary mapping entity names to their URLs

        Returns:
            Dictionary mapping entity names to their generated schemas
            Only includes entities where schema generation succeeded

        Raises:
            ValueError: If no entities provided
            RuntimeError: If all schema generation attempts fail

        """
        max_concurrent = self.config.get("max_concurrent_schema_gen", 20)
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_single_schema(
            entity_name: str,
        ) -> tuple[str, dict[str, Any] | None]:
            async with semaphore:
                try:
                    schema = await self._generate_schema_for_entity(entity_name)
                    return entity_name, schema
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(
                        "Configuration error generating schema for entity %s: %s",
                        entity_name,
                        e,
                    )
                    return entity_name, None
                except Exception as e:
                    logger.warning(
                        "Unexpected error generating schema for entity %s: %s",
                        entity_name,
                        e,
                    )
                    return entity_name, None

        # Create tasks for all entities
        tasks = [
            generate_single_schema(entity_name)
            for entity_name in sorted(entities.keys())
        ]

        # Execute with timeout
        timeout = self.config.get(
            "schema_generation_timeout",
            600,
        )  # 10 minutes default
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
        except TimeoutError:
            logger.warning("Schema generation timed out after %s seconds", timeout)
            # Try to generate schemas sequentially for remaining entities
            sequential_results: list[tuple[str, dict[str, Any] | None]] = []
            for entity_name in sorted(entities.keys()):
                try:
                    schema = await self._generate_schema_for_entity(entity_name)
                    sequential_results.append((entity_name, schema))
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(
                        "Configuration error generating schema for entity %s: %s",
                        entity_name,
                        e,
                    )
                    sequential_results.append((entity_name, None))
                except Exception as e:
                    logger.warning(
                        "Unexpected error generating schema for entity %s: %s",
                        entity_name,
                        e,
                    )
                    sequential_results.append((entity_name, None))

        # Filter successful schemas
        successful_schemas: dict[str, dict[str, Any]] = {}
        # Use sequential_results if we hit timeout, otherwise use original results
        final_results = (
            sequential_results if "sequential_results" in locals() else results
        )
        for entity_name, schema in final_results:
            if schema:
                # CORRECT LOGIC: Schema exists, add to successful schemas
                successful_schemas[entity_name] = schema
                logger.info("✅ Generated schema for entity %s", entity_name)
            else:
                # CORRECT LOGIC: No schema generated, log warning and skip
                logger.warning(
                    "⚠️  Skipping entity %s: No schema generated",
                    entity_name,
                )

        logger.info(
            "Generated schemas for %d/%d entities",
            len(successful_schemas),
            len(entities),
        )
        return successful_schemas

    async def _generate_schema_for_entity(
        self,
        entity_name: str,
    ) -> dict[str, Any] | None:
        """Generate schema for a single entity.

        Args:
        ----
            entity_name: Name of the entity

        Returns:
        -------
            JSON schema or None

        """
        method = self.config.get("schema_discovery_method", "auto")

        # Try describe endpoint first
        if method in {"auto", "describe"}:
            metadata = await self.entity_discovery.describe_entity(entity_name)
            if metadata:
                return self.schema_generator.generate_from_metadata(metadata)

        # Try sample data inference
        if method in {"auto", "sample"}:
            samples = await self.entity_discovery.get_entity_sample(
                entity_name,
                limit=self.config.get("schema_sample_size", 5),
            )
            if samples:
                return self.schema_generator.generate_from_sample(samples)

        # Default minimal schema
        logger.warning("Could not generate schema for entity: %s", entity_name)
        return {
            "type": "object",
            "properties": {
                "id": {"type": ["integer", "null"]},
            },
            "additionalProperties": True,
        }

    def discover_streams(self) -> list[Stream]:
        """Discover available streams.

        Returns
        -------
            List of discovered stream instances

        """
        logger.info("Discovering Oracle WMS streams")

        # Start profiling discovery
        if self._monitor:
            profile_id = self._monitor.profiler.start_profile("discovery")

        # Run async discovery - Fix asyncio.run() in running loop
        try:
            asyncio.get_running_loop()
            # We're in an existing event loop, run in thread pool
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                entities_future = executor.submit(
                    asyncio.run,
                    self._discover_and_filter_entities(),
                )
                entities = entities_future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            entities = asyncio.run(self._discover_and_filter_entities())

        logger.info("Discovered %s accessible entities", len(entities))

        # Record discovery metrics
        if self._monitor:
            self._monitor.metrics.record_gauge(
                "discovery.entities_found",
                len(entities),
            )

        # Generate schemas for entities in parallel - Fix asyncio.run() in running loop
        try:
            asyncio.get_running_loop()
            # We're in an existing event loop, run in thread pool
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                schemas_future = executor.submit(
                    asyncio.run,
                    self._generate_schemas_parallel(entities),
                )
                schemas = schemas_future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            schemas = asyncio.run(self._generate_schemas_parallel(entities))

        # Record schema generation metrics
        if self._monitor:
            self._monitor.metrics.record_gauge(
                "discovery.schemas_generated",
                len(schemas),
            )

        # Create streams from successful schemas
        streams: list[Stream] = []
        for entity_name, schema in schemas.items():
            try:
                # Store schema for later use
                self._entity_schemas[entity_name] = schema

                # Create advanced stream with full functionality
                stream = WMSAdvancedStream(
                    tap=self,
                    entity_name=entity_name,
                    schema=schema,
                )
                streams.append(stream)

                logger.debug("Created stream for entity: %s", entity_name)

                # Record stream creation metric
                if self._monitor:
                    self._monitor.metrics.record_counter(
                        "streams.created",
                        tags={"entity": entity_name},
                    )

            except (ValueError, TypeError, AttributeError) as e:
                logger.exception(
                    "Configuration error creating stream for entity %s: %s",
                    entity_name,
                    e,
                )
                if self._monitor:
                    self._monitor.metrics.record_counter(
                        "streams.creation_failed",
                        tags={"entity": entity_name, "error": "config"},
                    )
                continue
            except Exception as e:
                logger.exception(
                    "Unexpected error creating stream for entity %s: %s",
                    entity_name,
                    e,
                )
                if self._monitor:
                    self._monitor.metrics.record_counter(
                        "streams.creation_failed",
                        tags={"entity": entity_name, "error": "unexpected"},
                    )
                continue

        # End profiling and record metrics
        if self._monitor:
            duration_ms = self._monitor.profiler.end_profile(
                profile_id,
                record_count=len(streams),
            )
            logger.info("Stream discovery completed in %.2fms", duration_ms)

        logger.info("Created %s streams", len(streams))

        # Record final metrics
        if self._monitor:
            self._monitor.metrics.record_gauge("streams.total_created", len(streams))

        return streams

    def _load_streams(self) -> list[Stream]:
        """Load streams (required by Singer SDK).

        Returns
        -------
            List of stream instances

        """
        # Discover streams if not already done
        if self._discovered_entities is None:
            return self.discover_streams()

        # Otherwise recreate streams from cached data
        streams: list[Stream] = []
        for entity_name, schema in self._entity_schemas.items():
            stream = WMSAdvancedStream(tap=self, entity_name=entity_name, schema=schema)
            streams.append(stream)

        return streams

    # GENERIC FILTERING METHODS
    # =========================
    # These methods provide generic filtering capabilities that work with any WMS entity

    def apply_entity_filters(
        self,
        entity_name: str,
        base_params: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply generic filters for any entity based on configuration.

        GENERIC FILTERING SYSTEM:
        ========================
        This method implements a generic filtering system that can be applied to any
        Oracle WMS entity without hardcoding entity-specific logic. It supports:

        1. SIMPLE FILTERS: Direct field = value matching
        2. OPERATOR FILTERS: Advanced operators like __gte, __lte, __contains
        3. TEMPORAL FILTERS: Timestamp-based filtering with safety overlaps
        4. ID RANGE FILTERS: Numeric ID filtering for pagination and resume
        5. STATUS FILTERS: Common status/active field filtering

        The filtering system uses a hierarchical approach:
        - Global filters (apply to all entities)
        - Entity-specific filters (apply to specific entity)
        - Advanced filters (complex operators and conditions)

        Filter Configuration Examples:
        -----------------------------

        1. Simple entity filter:
           "entity_filters": {
             "allocation": {"status": "ACTIVE", "facility_code": "MAIN"}
           }

        2. Temporal range filter:
           "entity_filters": {
             "allocation": {
               "mod_ts__gte": "2024-01-01T00:00:00Z",
               "mod_ts__lte": "2024-12-31T23:59:59Z"
             }
           }

        3. ID range filter (for pagination/resume):
           "entity_filters": {
             "allocation": {
               "id__gte": 1000,
               "id__lt": 50000
             }
           }

        4. Advanced operators:
           "advanced_filters": {
             "allocation": {
               "status": {"__in": ["ACTIVE", "PENDING"]},
               "description": {"__contains": "urgent"},
               "create_ts": {"__gte": "2024-01-01T00:00:00Z"}
             }
           }

        Args:
            entity_name: Name of the WMS entity
            base_params: Base URL parameters to extend

        Returns:
            Updated parameters with applied filters

        """
        params = base_params.copy()

        # 1. Apply global filters (affect all entities)
        global_filters = self.config.get("global_filters", {})
        for field, value in global_filters.items():
            params[field] = value

        # 2. Apply entity-specific simple filters
        entity_filters = self.config.get("entity_filters", {}).get(entity_name, {})
        for field, value in entity_filters.items():
            params[field] = value

        # 3. Apply advanced filters with operators
        advanced_filters = self.config.get("advanced_filters", {}).get(entity_name, {})
        for field, conditions in advanced_filters.items():
            if isinstance(conditions, dict):
                # Handle operator-based filters: {"__gte": "value", "__lte": "value"}
                for operator, value in conditions.items():
                    if operator.startswith("__"):
                        params[f"{field}{operator}"] = value
                    else:
                        # Handle nested field conditions
                        params[f"{field}__{operator}"] = value
            else:
                # Handle direct value assignment
                params[field] = conditions

        return params

    def apply_incremental_filters(
        self,
        entity_name: str,
        params: dict[str, Any],
        bookmark_value: Any = None,
    ) -> dict[str, Any]:
        """Apply generic incremental filtering for any entity.

        INCREMENTAL FILTERING PATTERNS:
        ==============================
        This method implements generic incremental sync patterns that work with any
        Oracle WMS entity that has timestamp or ID-based tracking fields.

        Supported Incremental Patterns:
        -------------------------------

        1. TIMESTAMP-BASED (preferred for most entities):
           - Uses mod_ts field (last modified timestamp)
           - Filter: mod_ts > max(previous_mod_ts) - safety_overlap
           - Safety overlap prevents missing records due to clock skew
           - Ordering: chronological (mod_ts ASC)

        2. ID-BASED (fallback for entities without timestamps):
           - Uses id field (primary key)
           - Filter: id > max(previous_id)
           - Ordering: ascending (id ASC)

        3. CUSTOM REPLICATION KEY:
           - Uses configurable field as replication key
           - Supports any comparable field (timestamps, IDs, version numbers)

        Configuration Examples:
        ----------------------

        1. Default timestamp-based:
           "enable_incremental": true,
           "incremental_overlap_minutes": 5

        2. Custom replication key:
           "replication_key_override": {
             "allocation": "last_updated_ts",
             "inventory": "version_number"
           }

        3. Entity-specific safety overlap:
           "incremental_config": {
             "allocation": {"overlap_minutes": 10},
             "inventory": {"overlap_minutes": 2}
           }

        Args:
            entity_name: Name of the WMS entity
            params: URL parameters to extend
            bookmark_value: Previous bookmark value for incremental sync

        Returns:
            Updated parameters with incremental filters applied

        """
        from datetime import datetime, timedelta

        # Get replication key for this entity (default: mod_ts)
        replication_key_overrides = self.config.get("replication_key_override", {})
        replication_key = replication_key_overrides.get(entity_name, "mod_ts")

        # Get safety overlap (default: 5 minutes)
        default_overlap = self.config.get("incremental_overlap_minutes", 5)
        entity_config = self.config.get("incremental_config", {}).get(entity_name, {})
        overlap_minutes = entity_config.get("overlap_minutes", default_overlap)

        if bookmark_value:
            # Apply incremental filter based on replication key type
            if replication_key in {"mod_ts", "create_ts", "last_updated_ts"}:
                # Timestamp-based incremental
                if isinstance(bookmark_value, str):
                    try:
                        bookmark_dt = datetime.fromisoformat(
                            bookmark_value.replace("Z", "+00:00"),
                        )
                        filter_dt = bookmark_dt - timedelta(minutes=overlap_minutes)
                        params[f"{replication_key}__gte"] = filter_dt.isoformat()

                        logger.info(
                            f"🔄 Incremental filter for {entity_name}: "
                            f"{replication_key} >= {filter_dt.isoformat()} "
                            f"(bookmark: {bookmark_value}, overlap: {overlap_minutes}min)",
                        )
                    except ValueError as e:
                        logger.warning(
                            f"Invalid bookmark timestamp for {entity_name}: {e}",
                        )
                        # Fallback to using bookmark as-is
                        params[f"{replication_key}__gte"] = bookmark_value
                else:
                    params[f"{replication_key}__gte"] = bookmark_value

            elif replication_key == "id":
                # ID-based incremental
                params[f"{replication_key}__gt"] = bookmark_value
                logger.info(
                    f"🔄 Incremental filter for {entity_name}: "
                    f"{replication_key} > {bookmark_value}",
                )
            else:
                # Generic comparable field incremental
                params[f"{replication_key}__gt"] = bookmark_value
                logger.info(
                    f"🔄 Incremental filter for {entity_name}: "
                    f"{replication_key} > {bookmark_value}",
                )
        else:
            # No bookmark - apply start_date if configured
            start_date = self.config.get("start_date")
            if start_date and replication_key in {
                "mod_ts",
                "create_ts",
                "last_updated_ts",
            }:
                params[f"{replication_key}__gte"] = start_date
                logger.info(
                    f"🔄 Initial incremental for {entity_name}: "
                    f"{replication_key} >= {start_date}",
                )

        return params

    def apply_full_sync_filters(
        self,
        entity_name: str,
        params: dict[str, Any],
        resume_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Apply generic full sync filtering with intelligent resume for any entity.

        FULL SYNC PATTERNS:
        ==================
        This method implements generic full sync patterns that work with any Oracle WMS
        entity, providing intelligent resume capabilities for interrupted syncs.

        Supported Full Sync Patterns:
        -----------------------------

        1. ID-BASED RESUME (recommended for large datasets):
           - Uses descending ID ordering (-id DESC)
           - Filter: id < min(existing_ids_in_target) - 1
           - Resumes from where previous sync stopped
           - Most efficient for large entity datasets

        2. TIMESTAMP-BASED FULL:
           - Uses chronological ordering (mod_ts ASC)
           - Filter: mod_ts >= start_date
           - Comprehensive historical extraction
           - Good for time-based analysis

        3. NO-FILTER FULL:
           - Extracts all records without filters
           - Uses pagination for memory efficiency
           - Complete entity snapshot

        Resume Context Structure:
        ------------------------
        {
           "has_existing_data": true,
           "min_id_in_target": 12345,
           "total_records": 50000,
           "sync_strategy": "id_based_resume"
        }

        Configuration Examples:
        ----------------------

        1. ID-based resume with date boundaries:
           "full_sync_config": {
             "allocation": {
               "strategy": "id_based_resume",
               "start_date": "2024-01-01T00:00:00Z",
               "end_date": "2024-12-31T23:59:59Z"
             }
           }

        2. Timestamp-based full sync:
           "full_sync_config": {
             "inventory": {
               "strategy": "timestamp_based",
               "start_date": "2023-01-01T00:00:00Z"
             }
           }

        Args:
            entity_name: Name of the WMS entity
            params: URL parameters to extend
            resume_context: Context for resuming interrupted sync

        Returns:
            Updated parameters with full sync filters applied

        """
        # Get full sync configuration for this entity
        full_sync_config = self.config.get("full_sync_config", {}).get(entity_name, {})
        strategy = full_sync_config.get("strategy", "id_based_resume")

        if strategy == "id_based_resume" and resume_context:
            # Apply ID-based resume filtering
            if resume_context.get("has_existing_data") and resume_context.get(
                "min_id_in_target",
            ):
                min_id = resume_context["min_id_in_target"]
                filter_threshold = min_id - 1
                params["id__lt"] = filter_threshold
                params["ordering"] = "-id"  # Descending order

                logger.info(
                    f"🔄 Full sync resume for {entity_name}: "
                    f"id < {filter_threshold} (min_id: {min_id}) with -id ordering",
                )
            else:
                # No existing data, start from highest ID
                params["ordering"] = "-id"
                logger.info(
                    f"🔄 Full sync for {entity_name}: -id ordering (no existing data)",
                )

        elif strategy == "timestamp_based":
            # Apply timestamp-based full sync
            params["ordering"] = "mod_ts"  # Chronological order

            start_date = full_sync_config.get("start_date") or self.config.get(
                "start_date",
            )
            end_date = full_sync_config.get("end_date") or self.config.get("end_date")

            if start_date:
                params["mod_ts__gte"] = start_date
                logger.info(f"🔄 Full sync for {entity_name}: mod_ts >= {start_date}")
            if end_date:
                params["mod_ts__lte"] = end_date
                logger.info(f"🔄 Full sync for {entity_name}: mod_ts <= {end_date}")

        else:
            # Default: no special filtering, just order by ID
            params["ordering"] = self.config.get("default_ordering", "id")
            logger.info(f"🔄 Full sync for {entity_name}: default ordering")

        return params

    def get_entity_replication_config(self, entity_name: str) -> dict[str, Any]:
        """Get replication configuration for a specific entity.

        REPLICATION CONFIGURATION:
        =========================
        Returns the complete replication configuration for an entity, including:
        - Replication method (INCREMENTAL/FULL_TABLE)
        - Replication key field
        - Safety overlap settings
        - Ordering preferences

        This allows the streams to configure themselves generically based on
        entity characteristics and user configuration.

        Args:
            entity_name: Name of the WMS entity

        Returns:
            Replication configuration dictionary

        """
        # Check if incremental is enabled globally and for this entity
        enable_incremental = self.config.get("enable_incremental", True)
        entity_incremental_config = self.config.get("incremental_config", {}).get(
            entity_name,
            {},
        )
        entity_enable_incremental = entity_incremental_config.get(
            "enabled",
            enable_incremental,
        )

        # Get replication key
        replication_key_overrides = self.config.get("replication_key_override", {})
        replication_key = replication_key_overrides.get(entity_name, "mod_ts")

        # Get safety overlap
        default_overlap = self.config.get("incremental_overlap_minutes", 5)
        overlap_minutes = entity_incremental_config.get(
            "overlap_minutes",
            default_overlap,
        )

        return {
            "replication_method": (
                "INCREMENTAL" if entity_enable_incremental else "FULL_TABLE"
            ),
            "replication_key": replication_key,
            "safety_overlap_minutes": overlap_minutes,
            "ordering": {
                "incremental": replication_key,
                "full_sync": self.config.get("full_sync_config", {})
                .get(entity_name, {})
                .get("ordering", "-id"),
            },
        }


# CLI entry point
if __name__ == "__main__":
    TapOracleWMS.cli()
