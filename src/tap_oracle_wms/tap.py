"""Oracle WMS tap class."""

import asyncio
import logging
from typing import Any, Optional

from singer_sdk import Stream, Tap

from .config import config_schema, validate_auth_config, validate_pagination_config
from .discovery import EntityDiscovery, SchemaGenerator
from .monitoring import TAPMonitor
from .streams_advanced import WMSAdvancedStream


logger = logging.getLogger(__name__)


class TapOracleWMS(Tap):
    """Oracle WMS tap class."""

    name = "tap-oracle-wms"
    config_jsonschema = config_schema

    def __init__(self, *args, **kwargs) -> None:
        """Initialize tap."""
        # CRITICAL: Singer SDK requires tap_name BEFORE super().__init__
        self.tap_name = "tap-oracle-wms"  # Required by Singer SDK
        self._entity_discovery = None
        self._schema_generator = None
        self._discovered_entities = None
        self._entity_schemas = {}
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
                        "connection.entities_discovered", len(entities)
                    )
            else:
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
        if not self._entity_discovery:
            self._entity_discovery = EntityDiscovery(dict(self.config))
        return self._entity_discovery

    @property
    def schema_generator(self) -> SchemaGenerator:
        """Get schema generator instance."""
        if not self._schema_generator:
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
        self, entities: dict[str, str]
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
                        "Configuration error checking access to entity %s: %s", name, e
                    )
                    return name, url, False
                except Exception as e:
                    logger.warning(
                        "Unexpected error checking access to entity %s: %s", name, e
                    )
                    return name, url, False

        # Create tasks for all entities
        tasks = [check_single_entity(name, url) for name, url in entities.items()]

        # Execute with timeout
        timeout = self.config.get("entity_access_timeout", 300)  # 5 minutes default
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("Entity access check timed out after %s seconds", timeout)
            # Return all entities if timeout
            return entities

        # Filter accessible entities
        accessible_entities = {}
        for name, url, accessible in results:
            if accessible:
                accessible_entities[name] = url
            else:
                logger.warning("No access to entity: %s", name)

        logger.info(
            "Verified access to %d/%d entities", len(accessible_entities), len(entities)
        )
        return accessible_entities

    async def _generate_schemas_parallel(
        self, entities: dict[str, str]
    ) -> dict[str, dict[str, Any]]:
        """Generate schemas for entities in parallel.

        Args:
        ----
            entities: Dictionary of entities to generate schemas for

        Returns:
        -------
            Dictionary mapping entity names to their schemas

        """
        max_concurrent = self.config.get("max_concurrent_schema_gen", 20)
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_single_schema(
            entity_name: str,
        ) -> tuple[str, Optional[dict[str, Any]]]:
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
            "schema_generation_timeout", 600
        )  # 10 minutes default
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("Schema generation timed out after %s seconds", timeout)
            # Try to generate schemas sequentially for remaining entities
            results = []
            for entity_name in sorted(entities.keys()):
                try:
                    schema = await self._generate_schema_for_entity(entity_name)
                    results.append((entity_name, schema))
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(
                        "Configuration error generating schema for entity %s: %s",
                        entity_name,
                        e,
                    )
                    results.append((entity_name, None))
                except Exception as e:
                    logger.warning(
                        "Unexpected error generating schema for entity %s: %s",
                        entity_name,
                        e,
                    )
                    results.append((entity_name, None))

        # Filter successful schemas
        successful_schemas = {}
        for entity_name, schema in results:
            if schema:
                successful_schemas[entity_name] = schema
            else:
                logger.warning("Skipping entity %s: No schema generated", entity_name)

        logger.info(
            "Generated schemas for %d/%d entities",
            len(successful_schemas),
            len(entities),
        )
        return successful_schemas

    async def _generate_schema_for_entity(
        self, entity_name: str
    ) -> Optional[dict[str, Any]]:
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
        if method in ["auto", "describe"]:
            metadata = await self.entity_discovery.describe_entity(entity_name)
            if metadata:
                return self.schema_generator.generate_from_metadata(metadata)

        # Try sample data inference
        if method in ["auto", "sample"]:
            samples = await self.entity_discovery.get_entity_sample(
                entity_name, limit=self.config.get("schema_sample_size", 5)
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

        # Run async discovery
        entities = asyncio.run(self._discover_and_filter_entities())
        logger.info("Discovered %s accessible entities", len(entities))

        # Record discovery metrics
        if self._monitor:
            self._monitor.metrics.record_gauge(
                "discovery.entities_found", len(entities)
            )

        # Generate schemas for entities in parallel
        schemas = asyncio.run(self._generate_schemas_parallel(entities))

        # Record schema generation metrics
        if self._monitor:
            self._monitor.metrics.record_gauge(
                "discovery.schemas_generated", len(schemas)
            )

        # Create streams from successful schemas
        streams = []
        for schema in schemas.values():
            try:
                # Store schema for later use
                self._entity_schemas[entity_name] = schema

                # Create advanced stream with full functionality
                stream = WMSAdvancedStream(
                    tap=self, entity_name=entity_name, schema=schema
                )
                streams.append(stream)

                logger.debug("Created stream for entity: %s", entity_name)

                # Record stream creation metric
                if self._monitor:
                    self._monitor.metrics.record_counter(
                        "streams.created", tags={"entity": entity_name}
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
                    "Unexpected error creating stream for entity %s: %s", entity_name, e
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
                profile_id, record_count=len(streams)
            )
            logger.info("Stream discovery completed in %.2fms", duration_ms)

        logger.info("Created %s streams", len(streams))

        # Record final metrics
        if self._monitor:
            self._monitor.metrics.record_gauge("streams.total_created", len(streams))

        return streams

    def load_streams(self) -> list[Stream]:
        """Load streams (required by Singer SDK).

        Returns
        -------
            List of stream instances

        """
        # Discover streams if not already done
        if self._discovered_entities is None:
            return self.discover_streams()

        # Otherwise recreate streams from cached data
        streams = []
        for schema in self._entity_schemas.values():
            stream = WMSAdvancedStream(tap=self, entity_name=entity_name, schema=schema)
            streams.append(stream)

        return streams


# CLI entry point
if __name__ == "__main__":
    TapOracleWMS.cli()
