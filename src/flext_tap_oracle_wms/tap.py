"""FLEXT Tap Oracle WMS - Singer tap implementation.

Simple, clean implementation following FLEXT patterns.
Uses flext-oracle-wms for all Oracle WMS communication.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, ClassVar

from flext_core import FlextResult, get_logger
from singer_sdk import Tap

from flext_tap_oracle_wms.config import FlextTapOracleWMSConfig
from flext_tap_oracle_wms.exceptions import FlextTapOracleWMSConfigurationError
from flext_tap_oracle_wms.streams import FlextTapOracleWMSStream

if TYPE_CHECKING:
    from collections.abc import Sequence

    from flext_core.flext_types import TAnyDict, TAnyObject
    from singer_sdk import Stream

logger = get_logger(__name__)


class FlextTapOracleWMS(Tap):
    """Oracle WMS tap using FLEXT patterns.

    Implements Singer tap for Oracle Warehouse Management System with:
    - Automatic schema discovery using flext-oracle-wms
    - Incremental replication
    - Stream filtering and selection
    - Pagination and rate limiting
    - Error handling and retries
    """

    name = "flext-tap-oracle-wms"

    config_jsonschema: ClassVar[dict[str, object]] = {
        "type": "object",
        "properties": {
            "base_url": {
                "type": "string",
                "description": "Oracle WMS base URL",
            },
            "username": {
                "type": "string",
                "description": "Oracle WMS username",
            },
            "password": {
                "type": "string",
                "description": "Oracle WMS password",
                "secret": True,
            },
            "api_version": {
                "type": "string",
                "default": "v10",
                "description": "Oracle WMS API version",
            },
            "page_size": {
                "type": "integer",
                "default": 100,
                "description": "Number of records per page",
            },
            "verify_ssl": {
                "type": "boolean",
                "default": True,
                "description": "Verify SSL certificates",
            },
        },
        "required": ["base_url", "username", "password"],
    }

    def __init__(
        self,
        config: dict[str, object] | FlextTapOracleWMSConfig | None = None,
        catalog: dict[str, object] | None = None,
        state: dict[str, object] | None = None,
        parse_env_config: bool = True,
        validate_config: bool = True,
    ) -> None:
        """Initialize the Oracle WMS tap.

        Args:
            config: Configuration dict or FlextTapOracleWMSConfig instance
            catalog: Singer catalog
            state: Singer state
            parse_env_config: Whether to parse config from environment
            validate_config: Whether to validate configuration

        """
        # Convert config to FlextTapOracleWMSConfig if needed
        if config is not None and not isinstance(config, FlextTapOracleWMSConfig):
            try:
                # Convert dict[str, object] to proper types for Pydantic model
                # Pydantic will handle type conversion internally
                config_dict = dict(config) if hasattr(config, "items") else config
                config = FlextTapOracleWMSConfig.model_validate(config_dict)
            except Exception as e:
                msg = f"Invalid configuration: {e}"
                raise FlextTapOracleWMSConfigurationError(msg) from e

        # Store typed config
        self._flext_config = config

        # Initialize instance attributes before parent init
        self._wms_client: object | None = None
        self._discovery: object | None = None
        self._is_started = False

        # Initialize parent with dict config for Singer SDK compatibility
        config_dict = config.model_dump(exclude_unset=True) if config else {}

        super().__init__(
            config=config_dict,
            catalog=catalog,
            state=state,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

    @property
    def flext_config(self) -> FlextTapOracleWMSConfig:
        """Get typed configuration."""
        if self._flext_config is None:
            # Create from parent config
            self._flext_config = FlextTapOracleWMSConfig(**self.config)
        return self._flext_config

    def _run_async(self, coro: TAnyObject) -> TAnyObject:
        """Run async coroutine in sync context."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    @property
    def wms_client(self) -> TAnyObject:  # FlextOracleWmsClient at runtime
        """Get or create WMS client."""
        if self._wms_client is None:
            # Import dynamically to avoid import errors
            try:
                from flext_oracle_wms import (
                    FlextOracleWmsClient,
                    FlextOracleWmsClientConfig,
                )
                from flext_oracle_wms.api_catalog import FlextOracleWmsApiVersion
            except ImportError as e:
                msg = f"flext_oracle_wms not available: {e}"
                raise FlextTapOracleWMSConfigurationError(msg) from e

            # Create client config for flext-oracle-wms
            client_config = FlextOracleWmsClientConfig(
                base_url=self.flext_config.base_url,
                username=self.flext_config.username,
                password=self.flext_config.password.get_secret_value(),
                environment=self.flext_config.api_version.replace("v", "").replace(
                    "/",
                    "",
                ),
                timeout=self.flext_config.timeout,
                max_retries=self.flext_config.max_retries,
                api_version=FlextOracleWmsApiVersion(self.flext_config.api_version),
                verify_ssl=self.flext_config.verify_ssl,
                enable_logging=True,
            )

            # Create client
            self._wms_client = FlextOracleWmsClient(client_config)

            # Start client (async operation)
            if not self._is_started:
                start_result = self._run_async(self._wms_client.start())
                if hasattr(start_result, "is_failure") and start_result.is_failure:
                    error_msg = getattr(start_result, "error", "Unknown error")
                    msg = f"Failed to start Oracle WMS client: {error_msg}"
                    raise FlextTapOracleWMSConfigurationError(msg)
                self._is_started = True

        return self._wms_client

    @property
    def discovery(self) -> TAnyObject:  # Use WMS client directly for discovery
        """Get WMS client for discovery operations."""
        # Use the WMS client directly as it has discovery capabilities
        return self.wms_client

    def initialize(self) -> FlextResult[None]:
        """Initialize the tap."""
        logger.info("Initializing Oracle WMS tap")

        try:
            # Validate configuration
            if self.flext_config.validate_config:
                validation_result = self.validate_configuration()
                if validation_result.is_failure:
                    return FlextResult.fail(
                        validation_result.error or "Configuration validation failed",
                    )

            # Ensure client is created and started
            _ = self.wms_client

            logger.info("Oracle WMS tap initialized successfully")
            return FlextResult.ok(None)

        except Exception as e:
            logger.exception("Failed to initialize tap")
            return FlextResult.fail(str(e))

    def discover_catalog(self) -> FlextResult[dict[str, object]]:
        """Discover available streams and their schemas.

        Returns:
            FlextResult containing Singer catalog

        """
        logger.info("Discovering Oracle WMS catalog")

        try:
            # Initialize if needed
            if not self._is_started:
                init_result = self.initialize()
                if init_result.is_failure:
                    return FlextResult.fail(
                        init_result.error or "Initialization failed",
                    )

            # Use flext-oracle-wms discovery
            # The WMS client has discover_entities method
            discovery_result = self._run_async(
                self.discovery.discover_entities(),
            )

            if hasattr(discovery_result, "is_failure") and discovery_result.is_failure:
                error_msg = getattr(discovery_result, "error", "Discovery failed")
                return FlextResult.fail(error_msg)

            # Build Singer catalog from discovery result
            data = getattr(discovery_result, "data", discovery_result)
            catalog = self._build_singer_catalog(data)

            # Count streams safely
            stream_count = 0
            if isinstance(catalog, dict):
                streams = catalog.get("streams", [])
                if isinstance(streams, list):
                    stream_count = len(streams)
            logger.info(f"Discovered {stream_count} streams")
            return FlextResult.ok(catalog)

        except Exception as e:
            logger.exception("Failed to discover catalog")
            return FlextResult.fail(str(e))

    def _build_singer_catalog(self, discovery_result: object) -> dict[str, object]:
        """Build Singer catalog from Oracle WMS discovery result."""
        streams = []

        # discovery_result should be a list of entities
        entities = discovery_result if isinstance(discovery_result, list) else []

        for entity_name in entities:
            # For now, create a simple schema as the entities are just strings
            # In production, you'd need to query each entity to get its schema
            stream = {
                "tap_stream_id": entity_name,
                "stream": entity_name,
                "schema": {
                    "type": "object",
                    "properties": {
                        # Basic generic properties
                        "id": {"type": ["string", "null"]},
                        "name": {"type": ["string", "null"]},
                        "created_at": {
                            "type": ["string", "null"],
                            "format": "date-time",
                        },
                        "updated_at": {
                            "type": ["string", "null"],
                            "format": "date-time",
                        },
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "forced-replication-method": "FULL_TABLE",
                            "table-key-properties": ["id"],
                        },
                    },
                ],
            }

            # Add field metadata for each property
            for prop_name in stream["schema"]["properties"]:
                stream["metadata"].append(
                    {
                        "breadcrumb": ["properties", prop_name],
                        "metadata": {
                            "inclusion": "available",
                        },
                    },
                )

            streams.append(stream)

        return {
            "type": "CATALOG",
            "streams": streams,
        }

    def _convert_fields_to_properties(self, fields: TAnyObject) -> dict[str, object]:
        """Convert Oracle WMS fields to Singer properties."""
        properties: dict[str, object] = {}

        # Ensure fields is iterable
        if not hasattr(fields, "__iter__"):
            return properties

        for field in fields:
            # Map Oracle WMS types to Singer types
            singer_type = "string"  # Default

            if field.data_type in {"NUMBER", "INTEGER", "DECIMAL"}:
                singer_type = "number"
            elif field.data_type == "BOOLEAN":
                singer_type = "boolean"
            elif field.data_type in {"DATE", "TIMESTAMP"}:
                singer_type = "string"
                properties[field.name] = {
                    "type": singer_type,
                    "format": "date-time",
                }
                continue

            properties[field.name] = {"type": singer_type}

            if field.is_nullable:
                properties[field.name] = {
                    "anyOf": [
                        properties[field.name],
                        {"type": "null"},
                    ],
                }

        return properties

    def discover_streams(self) -> Sequence[Stream]:
        """Discover available streams dynamically from Oracle WMS.

        Returns:
            List of Stream instances

        """
        logger.info("Discovering streams dynamically")

        # Get stream definitions from catalog
        stream_definitions = self._get_stream_definitions_from_catalog()
        if not stream_definitions:
            return []

        # Create stream instances from definitions
        streams = self._create_streams_from_definitions(stream_definitions)

        logger.info(f"Discovered {len(streams)} dynamic streams")
        return streams

    def _get_stream_definitions_from_catalog(self) -> list[TAnyDict]:
        """Get stream definitions from discovered catalog.

        Returns:
            List of stream definition dictionaries

        """
        # Discover the catalog to get available entities
        catalog_result = self.discover_catalog()
        if catalog_result.is_failure:
            logger.error(f"Failed to discover catalog: {catalog_result.error}")
            return []

        catalog = catalog_result.data
        if not isinstance(catalog, dict):
            logger.error("Invalid catalog format")
            return []

        catalog_streams = catalog.get("streams", [])
        if not isinstance(catalog_streams, list):
            logger.error("Invalid catalog streams format")
            return []

        return catalog_streams

    def _create_streams_from_definitions(
        self, stream_definitions: list[TAnyDict],
    ) -> list[Stream]:
        """Create stream instances from stream definitions.

        Args:
            stream_definitions: List of stream definition dictionaries

        Returns:
            List of created Stream instances

        """
        streams = []

        for stream_def in stream_definitions:
            try:
                stream = self._create_single_stream(stream_def)
                if stream is not None:
                    streams.append(stream)
                    logger.debug(f"Created dynamic stream: {stream.name}")
            except Exception as e:
                logger.warning(f"Failed to create stream from catalog: {e}")

        return streams

    def _create_single_stream(self, stream_def: TAnyDict) -> Stream | None:
        """Create a single stream from definition.

        Args:
            stream_def: Stream definition dictionary

        Returns:
            Created Stream instance or None if invalid

        """
        # Extract stream information
        stream_name = stream_def.get("stream")
        stream_schema = stream_def.get("schema")

        if not stream_name:
            logger.warning("Stream missing name, skipping")
            return None

        # Create a dynamic stream instance
        stream = FlextTapOracleWMSStream(
            tap=self,
            name=stream_name,
            schema=stream_schema,
        )

        # Configure stream metadata
        self._configure_stream_metadata(stream, stream_def)

        return stream

    def _configure_stream_metadata(
        self, stream: Stream, stream_def: TAnyDict,
    ) -> None:
        """Configure stream metadata from definition.

        Args:
            stream: Stream instance to configure
            stream_def: Stream definition dictionary

        """
        # Set primary keys if available from metadata
        metadata_list = stream_def.get("metadata", [])
        for metadata in metadata_list:
            if metadata.get("breadcrumb") == []:
                table_metadata = metadata.get("metadata", {})
                pk_list = table_metadata.get("table-key-properties", [])
                if pk_list:
                    # Set primary keys dynamically using setattr for class variables
                    stream.primary_keys = pk_list
                break

    def execute(self, message: str | None = None) -> FlextResult[None]:
        """Execute tap in Singer mode.

        Args:
            message: Optional Singer message to process

        Returns:
            FlextResult indicating success or failure

        """
        try:
            # If message provided, process it
            if message:
                # This is target mode, not supported for tap
                return FlextResult.fail("Tap does not support message processing")

            # Run tap using sync_all from Singer SDK
            # Use sync_all method from Singer SDK
            self.sync_all()
            return FlextResult.ok(None)

        except Exception as e:
            logger.exception("Tap execution failed")
            return FlextResult.fail(str(e))

    def validate_configuration(self) -> FlextResult[dict[str, object]]:
        """Validate tap configuration.

        Returns:
            FlextResult with validation status

        """
        logger.info("Validating configuration")

        try:
            # Validate config model
            validation_result = self.flext_config.validate_oracle_wms_config()
            if validation_result.is_failure:
                return validation_result

            # Test connection using flext-oracle-wms health check
            health_result = self._run_async(self.wms_client.health_check())
            if hasattr(health_result, "is_failure") and health_result.is_failure:
                error_msg = getattr(
                    health_result, "error", "Unknown health check error",
                )
                return FlextResult.fail(f"Connection test failed: {error_msg}")

            validation_info = {
                "valid": True,
                "connection": "success",
                "base_url": self.flext_config.base_url,
                "api_version": self.flext_config.api_version,
                "health": getattr(health_result, "data", None),
            }

            logger.info("Configuration validated successfully")
            return FlextResult.ok(validation_info)

        except Exception as e:
            logger.exception("Configuration validation failed")
            return FlextResult.fail(str(e))

    def get_implementation_name(self) -> str:
        """Get implementation name."""
        return "FLEXT Oracle WMS Tap"

    def get_implementation_version(self) -> str:
        """Get implementation version."""
        try:
            import importlib.metadata

            return importlib.metadata.version("flext-tap-oracle-wms")
        except Exception:
            return "0.9.0"

    def get_implementation_metrics(self) -> FlextResult[dict[str, object]]:
        """Get implementation metrics.

        Returns:
            FlextResult containing metrics

        """
        metrics = {
            "tap_name": self.name,
            "version": self.get_implementation_version(),
            "streams_available": len(self.discover_streams()),
            "configuration": {
                "base_url": self.flext_config.base_url,
                "api_version": self.flext_config.api_version,
                "page_size": self.flext_config.page_size,
                "verify_ssl": self.flext_config.verify_ssl,
            },
        }

        # Add runtime metrics if available
        if hasattr(self, "metrics"):
            metrics["runtime"] = {
                "records_extracted": getattr(self.metrics, "records_extracted", 0),
                "streams_extracted": getattr(self.metrics, "streams_extracted", 0),
            }

        return FlextResult.ok(metrics)

    def __del__(self) -> None:
        """Cleanup when tap is destroyed."""
        if (
            hasattr(self, "_is_started")
            and self._is_started
            and hasattr(self, "_wms_client")
            and self._wms_client
        ):
            try:
                if hasattr(self._wms_client, "stop"):
                    self._run_async(self._wms_client.stop())
            except Exception as e:
                logger.debug(f"Error stopping WMS client: {e}")
