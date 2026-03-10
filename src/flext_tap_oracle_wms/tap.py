"""Tap and plugin implementations for Oracle WMS extraction."""

from __future__ import annotations

import importlib.metadata
from collections.abc import Mapping, Sequence
from typing import ClassVar

from flext_core import FlextLogger, FlextResult, t
from flext_oracle_wms import FlextOracleWmsClient, FlextOracleWmsSettings
from singer_sdk.tap_base import Tap

from .constants import c
from .exceptions import FlextTapOracleWmsConfigurationError
from .models import m
from .settings import FlextTapOracleWmsSettings
from .streams import FlextTapOracleWmsStream

logger = FlextLogger(__name__)


class FlextTapOracleWms(Tap):
    """Singer-compatible tap implementation backed by flext_oracle_wms."""

    name = "flext-tap-oracle-wms"
    config_jsonschema: ClassVar[dict[str, t.ContainerValue]] = {
        "type": c.TapOracleWms.SCHEMA_TYPE_OBJECT,
        "properties": {
            "base_url": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
            "username": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
            "password": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING, "secret": True},
            "api_version": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING, "default": "v1"},
            "page_size": {"type": c.TapOracleWms.SCHEMA_TYPE_INTEGER, "default": 100},
            "verify_ssl": {"type": c.TapOracleWms.SCHEMA_TYPE_BOOLEAN, "default": True},
        },
        "required": list(c.TapOracleWms.REQUIRED_CONFIG_FIELDS),
    }

    _wms_client: FlextOracleWmsClient | None = None
    _discovery: t.ContainerValue | None = None
    _schema_generator: t.ContainerValue | None = None
    _discovery_mode: bool = False

    @property
    def flext_config(self) -> FlextTapOracleWmsSettings:
        """Return validated tap settings."""
        config_map = dict(self.config)
        try:
            return FlextTapOracleWmsSettings.model_validate(config_map)
        except Exception as exc:
            msg = f"Invalid configuration: {exc}"
            raise FlextTapOracleWmsConfigurationError(msg) from exc

    @property
    def wms_client(self) -> FlextOracleWmsClient:
        """Return a started WMS client instance."""
        if self._wms_client is None:
            wms_settings = FlextOracleWmsSettings(
                base_url=str(self.flext_config.base_url),
                username=self.flext_config.username,
                password=self.flext_config.password.get_secret_value(),
                api_version=self.flext_config.api_version,
                timeout=self.flext_config.timeout,
                retry_attempts=self.flext_config.max_retries,
                enable_ssl_verification=self.flext_config.verify_ssl,
            )
            client = FlextOracleWmsClient(config=wms_settings)
            start_result = client.start()
            if start_result.is_failure:
                msg = start_result.error or "Failed to start Oracle WMS client"
                raise FlextTapOracleWmsConfigurationError(msg)
            self._wms_client = client
        return self._wms_client

    @staticmethod
    def _schema_for_entity() -> Mapping[str, t.JsonValue]:
        """Return a default Singer JSON schema for discovered entities."""
        return {
            "type": c.TapOracleWms.SCHEMA_TYPE_OBJECT,
            "properties": {
                "id": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING_OR_NULL},
                "name": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING_OR_NULL},
                "created_at": {
                    "type": c.TapOracleWms.SCHEMA_TYPE_STRING_OR_NULL,
                    "format": c.TapOracleWms.SCHEMA_FORMAT_DATETIME,
                },
                "updated_at": {
                    "type": c.TapOracleWms.SCHEMA_TYPE_STRING_OR_NULL,
                    "format": c.TapOracleWms.SCHEMA_FORMAT_DATETIME,
                },
            },
        }

    def discover_catalog(self) -> FlextResult[m.Meltano.SingerCatalog]:
        """Discover source entities and convert them into Singer catalog streams."""
        discovery_result = self.wms_client.discover_entities()
        if discovery_result.is_failure:
            return FlextResult[m.Meltano.SingerCatalog].fail(
                discovery_result.error or "Discovery failed"
            )
        entities: list[str] = list(discovery_result.value)
        streams = [
            m.Meltano.SingerCatalogEntry(
                tap_stream_id=entity,
                stream=entity,
                schema=dict(self._schema_for_entity()),
                metadata=[
                    m.Meltano.SingerCatalogMetadata(
                        breadcrumb=[],
                        metadata={
                            "inclusion": "available",
                            "forced-replication-method": "FULL_TABLE",
                            "table-key-properties": ["id"],
                        },
                    )
                ],
            )
            for entity in entities
        ]
        return FlextResult[m.Meltano.SingerCatalog].ok(
            m.Meltano.SingerCatalog(streams=streams)
        )

    def discover_streams(self) -> Sequence[FlextTapOracleWmsStream]:
        """Build stream objects from the discovered catalog."""
        catalog_result = self.discover_catalog()
        if catalog_result.is_failure:
            logger.warning("Catalog discovery failed: %s", catalog_result.error or "")
            return []
        streams_raw = catalog_result.value.streams
        if not streams_raw:
            return []
        streams: list[FlextTapOracleWmsStream] = []
        for stream_raw in streams_raw:
            stream_name = stream_raw.stream
            stream_schema = stream_raw.schema_definition
            stream = FlextTapOracleWmsStream(
                tap=self, name=stream_name, schema=stream_schema
            )
            streams.append(stream)
        return streams

    def execute(self, message: str | None = None) -> FlextResult[bool]:
        """Run a full tap sync when no custom message is provided."""
        if message:
            return FlextResult[bool].fail("Tap does not support message execution")
        self.sync_all()
        return FlextResult[bool].ok(True)

    def get_implementation_metrics(self) -> FlextResult[t.ConfigurationMapping]:
        """Return basic runtime metrics for observability."""
        return FlextResult[t.ConfigurationMapping].ok({
            "tap_name": self.name,
            "version": self.get_implementation_version(),
            "streams_available": len(self.discover_streams()),
        })

    def get_implementation_name(self) -> str:
        """Return the human-readable implementation name."""
        return "FLEXT Oracle WMS Tap"

    def get_implementation_version(self) -> str:
        """Return installed package version or project fallback."""
        try:
            return importlib.metadata.version("flext-tap-oracle-wms")
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ):
            return "0.9.0"

    def validate_configuration(self) -> FlextResult[t.ConfigurationMapping]:
        """Expose non-secret validated configuration fields."""
        return FlextResult[t.ConfigurationMapping].ok({
            "base_url": str(self.flext_config.base_url),
            "api_version": self.flext_config.api_version,
            "page_size": self.flext_config.page_size,
        })


class FlextTapOracleWmsPlugin:
    """Plugin wrapper exposing tap operations to the host runtime."""

    def __init__(self, config: Mapping[str, t.ContainerValue]) -> None:
        """Initialize plugin state and hold tap configuration."""
        self._config = config
        self._tap: FlextTapOracleWms | None = None
        self._name = "flext-tap-oracle-wms"
        self._version = "0.9.0"

    @property
    def name(self) -> str:
        """Return plugin identifier."""
        return self._name

    @property
    def version(self) -> str:
        """Return plugin version."""
        return self._version

    def execute(
        self, operation: str, _parameters: Mapping[str, t.ContainerValue] | None = None
    ) -> FlextResult[t.ConfigurationMapping]:
        """Execute supported plugin operations against the tap."""
        if self._tap is None:
            init_result = self.initialize(None)
            if init_result.is_failure:
                return FlextResult[t.ConfigurationMapping].fail(
                    init_result.error or "Tap initialization failed"
                )
        tap = self._tap
        if tap is None:
            return FlextResult[t.ConfigurationMapping].fail("Tap not initialized")
        if operation == "discover":
            catalog_result = tap.discover_catalog()
            if catalog_result.is_failure:
                return FlextResult[t.ConfigurationMapping].fail(
                    catalog_result.error or "Discovery failed"
                )
            return FlextResult[t.ConfigurationMapping].ok(
                catalog_result.value.model_dump(mode="json")
            )
        if operation == "sync":
            execute_result = tap.execute()
            if execute_result.is_failure:
                return FlextResult[t.ConfigurationMapping].fail(
                    execute_result.error or "Sync failed"
                )
            return FlextResult[t.ConfigurationMapping].ok({"success": True})
        return FlextResult[t.ConfigurationMapping].fail(
            f"Unsupported operation: {operation}"
        )

    def get_info(self) -> Mapping[str, t.ContainerValue]:
        """Return plugin metadata for discovery and capabilities."""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Oracle WMS Singer Tap Plugin",
            "capabilities": ["discover", "sync"],
        }

    def initialize(self, _context: t.ContainerValue) -> FlextResult[bool]:
        """Instantiate the tap for subsequent operations."""
        self._tap = FlextTapOracleWms(config=dict(self._config))
        return FlextResult[bool].ok(True)

    def shutdown(self) -> FlextResult[bool]:
        """Release tap resources held by this plugin."""
        self._tap = None
        return FlextResult[bool].ok(True)
