"""Tap and plugin implementations for Oracle WMS extraction."""

from __future__ import annotations

import importlib.metadata
from collections.abc import (
    Callable,
    Mapping,
    MutableSequence,
    Sequence,
)
from pathlib import Path
from typing import ClassVar, override

from flext_oracle_wms import (
    FlextOracleWmsSettings,
    FlextOracleWmsUtilitiesClient,
)

from flext_tap_oracle_wms import (
    FlextTapOracleWmsConfigurationError,
    FlextTapOracleWmsSettings,
    FlextTapOracleWmsStream,
    c,
    m,
    p,
    r,
    t,
    u,
)

logger = u.fetch_logger(__name__)


def _build_config_jsonschema() -> dict[str, t.JsonValue]:
    properties: dict[str, t.JsonValue] = {
        "base_url": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
        "username": {"type": c.TapOracleWms.SCHEMA_TYPE_STRING},
        "password": {
            "type": c.TapOracleWms.SCHEMA_TYPE_STRING,
            "secret": True,
        },
        "api_version": {
            "type": c.TapOracleWms.SCHEMA_TYPE_STRING,
            "default": "v1",
        },
        "page_size": {
            "type": c.TapOracleWms.SCHEMA_TYPE_INTEGER,
            "default": 100,
        },
        "verify_ssl": {
            "type": c.TapOracleWms.SCHEMA_TYPE_BOOLEAN,
            "default": True,
        },
    }
    required: list[t.JsonValue] = [
        str(field) for field in c.TapOracleWms.REQUIRED_CONFIG_FIELDS
    ]
    return {
        "type": c.TapOracleWms.SCHEMA_TYPE_OBJECT,
        "properties": properties,
        "required": required,
    }


class FlextTapOracleWms(m.Meltano.SingerTapBase):
    """Singer-compatible tap implementation backed by flext_oracle_wms."""

    name = "flext-tap-oracle-wms"
    config_jsonschema: ClassVar[dict[str, t.JsonValue]] = _build_config_jsonschema()

    _wms_client: FlextOracleWmsUtilitiesClient.Client | None = None
    _discovery: t.JsonValue | None = None
    _schema_generator: t.JsonValue | None = None
    _discovery_mode: bool = False

    @override
    def __init__(
        self,
        settings: t.JsonMapping | FlextTapOracleWmsSettings | None = None,
        config: t.JsonMapping | None = None,
        catalog: t.StrMapping | None = None,
        state: t.StrMapping | None = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
    ) -> None:
        """Initialize tap, accepting settings object or raw dict."""
        raw_config: t.JsonMapping
        effective_config = config if config is not None else settings
        if isinstance(effective_config, FlextTapOracleWmsSettings):
            raw_config = dict(effective_config.model_dump(mode="json").items())
        else:
            raw_config = dict(effective_config) if effective_config else {}
        parent_init: Callable[..., None] = getattr(super(), "__init__")
        parent_init(
            config=raw_config,
            catalog=catalog,
            state=state,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

    @property
    def settings(self) -> t.JsonMapping:
        """Expose tap configuration through legacy settings contract."""
        config = self.config
        return {str(key): value for key, value in config.items()}

    @property
    def catalog_dict_typed(self) -> t.MutableJsonMapping:
        """Return a validated Singer catalog mapping with recursive contracts."""
        raw_catalog_dict: t.JsonMapping = getattr(super(), "catalog_dict", {})
        try:
            validated_catalog = t.CONTAINER_VALUE_MAP_ADAPTER.validate_python(
                raw_catalog_dict,
            )
        except c.ValidationError as exc:
            msg = f"Invalid catalog_dict format: {exc}"
            raise FlextTapOracleWmsConfigurationError(msg) from exc
        return self._to_typed_catalog(
            u.TapOracleWms.MappingConversion.safe_str_dict(validated_catalog)
        )

    @staticmethod
    def _to_typed_catalog(
        raw: t.JsonMapping,
    ) -> t.MutableJsonMapping:
        """Convert a raw catalog mapping into a validated Singer catalog dict."""
        raw_streams = raw.get("streams")
        raw_streams_seq: t.JsonList = (
            raw_streams
            if isinstance(raw_streams, Sequence)
            and not isinstance(raw_streams, (str, bytes))
            else []
        )
        stream_entries: MutableSequence[m.Meltano.SingerCatalogEntry] = []
        for raw_stream in raw_streams_seq:
            if not isinstance(raw_stream, Mapping):
                continue
            s_dict: t.JsonMapping = u.TapOracleWms.MappingConversion.safe_str_mapping(
                raw_stream
            )
            metadata_raw: t.JsonValue = s_dict.get("metadata", [])
            metadata_entries: MutableSequence[m.Meltano.SingerCatalogMetadata] = []
            if isinstance(metadata_raw, Sequence) and not isinstance(
                metadata_raw, (str, bytes)
            ):
                for raw_entry in metadata_raw:
                    if not isinstance(raw_entry, Mapping):
                        continue
                    entry_dict = u.TapOracleWms.MappingConversion.safe_str_mapping(
                        raw_entry
                    )
                    breadcrumb_raw: t.JsonValue = entry_dict.get("breadcrumb", [])
                    metadata_map_raw: t.JsonValue = entry_dict.get("metadata", {})
                    metadata_entries.append(
                        m.Meltano.SingerCatalogMetadata(
                            breadcrumb=[str(item) for item in breadcrumb_raw]
                            if isinstance(breadcrumb_raw, Sequence)
                            and not isinstance(breadcrumb_raw, (str, bytes))
                            else [],
                            metadata=u.TapOracleWms.MappingConversion.safe_str_dict(
                                metadata_map_raw
                            )
                            if isinstance(metadata_map_raw, Mapping)
                            else {},
                        )
                    )
            schema_raw: t.JsonValue = s_dict.get("schema", {})
            stream_name = str(s_dict.get("stream", ""))
            entry_result = u.Meltano.build_catalog_entry(
                stream_name=stream_name,
                schema=(
                    u.TapOracleWms.MappingConversion.safe_str_dict(schema_raw)
                    if isinstance(schema_raw, Mapping)
                    else {}
                ),
                key_properties=(),
            )
            if entry_result.failure or entry_result.value is None:
                msg = (
                    entry_result.error
                    or f"Failed to build catalog entry for {stream_name}"
                )
                raise FlextTapOracleWmsConfigurationError(msg)
            stream_entries.append(
                entry_result.value.model_copy(
                    update={
                        "tap_stream_id": str(s_dict.get("tap_stream_id", "")),
                        "stream": stream_name,
                        "metadata": metadata_entries,
                    }
                )
            )
        catalog = m.Meltano.SingerCatalog(streams=stream_entries)
        dumped_catalog = catalog.model_dump(
            by_alias=True,
            exclude_none=True,
            mode="json",
        )
        validated_dump = t.CONTAINER_VALUE_MAP_ADAPTER.validate_python(dumped_catalog)
        return dict(validated_dump.items())

    @property
    def flext_config(self) -> FlextTapOracleWmsSettings:
        """Return validated tap settings."""
        config_map = dict(self.settings)
        try:
            return FlextTapOracleWmsSettings.model_validate(config_map)
        except c.Meltano.SINGER_SAFE_EXCEPTIONS as exc:
            msg = f"Invalid configuration: {exc}"
            raise FlextTapOracleWmsConfigurationError(msg) from exc

    @property
    def wms_client(self) -> FlextOracleWmsUtilitiesClient.Client:
        """Return a started WMS client instance."""
        if self._wms_client is None:
            password = self.flext_config.password
            wms_settings = FlextOracleWmsSettings.model_validate({
                "base_url": str(self.flext_config.base_url),
                "username": str(self.flext_config.username),
                "password": (
                    password.get_secret_value()
                    if isinstance(password, t.SecretStr)
                    else str(password)
                ),
                "timeout": float(self.flext_config.timeout),
                "retry_attempts": self.flext_config.max_retries,
            })
            client = FlextOracleWmsUtilitiesClient.Client(settings=wms_settings)
            start_result = client.start()
            if start_result.failure:
                msg = start_result.error or "Failed to start Oracle WMS client"
                raise FlextTapOracleWmsConfigurationError(msg)
            self._wms_client = client
        return self._wms_client

    @staticmethod
    def _schema_for_entity() -> t.JsonMapping:
        """Return a default Singer JSON schema for discovered entities."""
        return {"type": c.TapOracleWms.SCHEMA_TYPE_OBJECT}

    def discovercatalog_typed(self) -> p.Result[m.Meltano.SingerCatalog]:
        """Discover source entities and convert them into Singer catalog streams."""
        discovery_result = self.wms_client.discover_entities()
        if discovery_result.failure:
            return r[m.Meltano.SingerCatalog].fail(
                discovery_result.error or "Discovery failed",
            )
        entities: t.StrSequence = list(discovery_result.value)
        streams: list[m.Meltano.SingerCatalogEntry] = []
        for entity in entities:
            entry_result = u.Meltano.build_catalog_entry(
                stream_name=entity,
                schema=dict(self._schema_for_entity()),
                key_properties=("id",),
            )
            if entry_result.failure:
                return r[m.Meltano.SingerCatalog].fail(
                    entry_result.error
                    or f"Failed to build Singer catalog entry for {entity}",
                )
            if entry_result.value is not None:
                streams.append(
                    entry_result.value.model_copy(
                        update={
                            "metadata": [
                                m.Meltano.SingerCatalogMetadata(
                                    breadcrumb=[],
                                    metadata={
                                        "inclusion": "available",
                                        "forced-replication-method": "FULL_TABLE",
                                        "table-key-properties": ["id"],
                                    },
                                ),
                            ]
                        }
                    )
                )
        return r[m.Meltano.SingerCatalog].ok(
            m.Meltano.SingerCatalog(type="CATALOG", streams=streams),
        )

    @override
    def discover_streams(self) -> Sequence[FlextTapOracleWmsStream]:
        """Build stream objects from the discovered catalog."""
        catalog_result = self.discovercatalog_typed()
        if catalog_result.failure:
            msg = f"Catalog discovery failed: {catalog_result.error or 'unknown error'}"
            raise FlextTapOracleWmsConfigurationError(msg)
        streams_raw = catalog_result.value.streams
        if not streams_raw:
            return []
        return [
            FlextTapOracleWmsStream(
                tap=self,
                name=stream_raw.stream,
                schema={
                    k: v
                    for k, v in stream_raw.schema_definition.items()
                    if not isinstance(v, Path)
                },
            )
            for stream_raw in streams_raw
        ]

    def execute(self, message: str | None = None) -> p.Result[bool]:
        """Run a full tap sync when no custom message is provided."""
        if message:
            return r[bool].fail("Tap does not support message execution")
        self.sync_all()
        return r[bool].ok(True)

    def get_implementation_metrics(self) -> p.Result[t.JsonValue]:
        """Return basic runtime metrics for observability."""
        return r[t.JsonValue].ok({
            "tap_name": self.name,
            "version": self.get_implementation_version(),
            "streams_available": len(self.discover_streams()),
        })

    def get_implementation_name(self) -> str:
        """Return the human-readable implementation name."""
        return "FLEXT Oracle WMS Tap"

    def get_implementation_version(self) -> str:
        """Return installed package version."""
        return importlib.metadata.version("flext-tap-oracle-wms")

    def validate_configuration(self) -> p.Result[t.JsonValue]:
        """Expose non-secret validated configuration fields."""
        return r[t.JsonValue].ok({
            "base_url": str(self.flext_config.base_url),
            "api_version": self.flext_config.api_version,
            "page_size": self.flext_config.page_size,
        })

    def initialize(self) -> p.Result[bool]:
        """Initialize the tap and validate connectivity."""
        try:
            _ = self.flext_config
            return r[bool].ok(True)
        except (
            ValueError,
            TypeError,
            KeyError,
            FlextTapOracleWmsConfigurationError,
        ) as exc:
            return r[bool].fail(str(exc))


class FlextTapOracleWmsPlugin:
    """Plugin wrapper exposing tap operations to the host runtime."""

    def __init__(self, settings: t.JsonMapping) -> None:
        """Initialize plugin state and hold tap configuration."""
        self.config = settings
        self._tap: FlextTapOracleWms | None = None
        self.name = "flext-tap-oracle-wms"
        self._version = "0.9.0"

    @property
    def version(self) -> str:
        """Return plugin version."""
        return self._version

    def execute(
        self,
        operation: str,
        _parameters: t.JsonMapping | None = None,
    ) -> p.Result[t.JsonValue]:
        """Execute supported plugin operations against the tap."""
        if self._tap is None:
            init_result = self.initialize(None)
            if init_result.failure:
                return r[t.JsonValue].fail(
                    init_result.error or "Tap initialization failed",
                )
        tap = self._tap
        if tap is None:
            return r[t.JsonValue].fail("Tap not initialized")
        if operation == "discover":
            catalog_result = tap.discovercatalog_typed()
            if catalog_result.failure:
                return r[t.JsonValue].fail(
                    catalog_result.error or "Discovery failed",
                )
            return r[t.JsonValue].ok(catalog_result.value.model_dump(mode="json"))
        if operation == "sync":
            execute_result = tap.execute()
            if execute_result.failure:
                return r[t.JsonValue].fail(execute_result.error or "Sync failed")
            return r[t.JsonValue].ok({"success": True})
        return r[t.JsonValue].fail(f"Unsupported operation: {operation}")

    def get_info(self) -> t.JsonMapping:
        """Return plugin metadata for discovery and capabilities."""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Oracle WMS Singer Tap Plugin",
            "capabilities": ["discover", "sync"],
        }

    def initialize(self, context: t.JsonValue | None) -> p.Result[bool]:
        """Instantiate the tap for subsequent operations."""
        runtime_settings = dict(self.config)
        if isinstance(context, Mapping):
            runtime_settings.update({str(key): value for key, value in context.items()})
        elif context is not None:
            logger.debug("Ignoring non-mapping tap initialization context: %s", context)
        self._tap = FlextTapOracleWms(settings=runtime_settings)
        return r[bool].ok(True)

    def shutdown(self) -> p.Result[bool]:
        """Release tap resources held by this plugin."""
        self._tap = None
        return r[bool].ok(True)
