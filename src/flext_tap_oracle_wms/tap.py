"""Tap and plugin implementations for Oracle WMS extraction."""

from __future__ import annotations

import importlib.metadata
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import ClassVar, TypedDict, override

from flext_core import FlextLogger, r
from flext_meltano.singer.sdk import FlextMeltanoSingerTapBase
from flext_oracle_wms import (
    FlextOracleWmsClient,
    FlextOracleWmsSettings,
)
from pydantic import SecretStr, TypeAdapter, ValidationError

from flext_tap_oracle_wms import c, m, t
from flext_tap_oracle_wms.exceptions import FlextTapOracleWmsConfigurationError
from flext_tap_oracle_wms.settings import FlextTapOracleWmsSettings
from flext_tap_oracle_wms.streams import FlextTapOracleWmsStream

logger = FlextLogger(__name__)
_CONTAINER_VALUE_MAP_ADAPTER: TypeAdapter[t.ContainerValueMapping] = TypeAdapter(
    t.ContainerValueMapping,
)


def _safe_str_mapping(
    raw: Mapping[str, t.ContainerValue],
) -> Mapping[str, t.ContainerValue]:
    """Return a Mapping with str keys from an untyped mapping source."""
    return {str(k): v for k, v in raw.items()}


def _safe_str_dict(
    raw: Mapping[str, t.ContainerValue],
) -> dict[str, t.ContainerValue]:
    """Return a dict with str keys from an untyped dict source."""
    return {str(k): v for k, v in raw.items()}


class SingerMetadataEntry(TypedDict):
    """Singer catalog metadata entry."""

    breadcrumb: list[str]
    metadata: dict[str, t.ContainerValue]


class SingerStreamEntry(TypedDict):
    """Singer catalog stream entry."""

    tap_stream_id: str
    stream: str
    schema: dict[str, t.ContainerValue]
    metadata: list[SingerMetadataEntry]


class SingerCatalogDict(TypedDict):
    """Singer catalog dict with typed streams."""

    streams: list[SingerStreamEntry]


class FlextTapOracleWms(FlextMeltanoSingerTapBase):
    """Singer-compatible tap implementation backed by flext_oracle_wms."""

    name = "flext-tap-oracle-wms"
    config_jsonschema: ClassVar[dict[str, t.NormalizedValue]] = {
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

    @override
    def __init__(
        self,
        config: t.ContainerMapping
        | Mapping[str, t.ContainerValue]
        | FlextTapOracleWmsSettings
        | None = None,
        catalog: dict[str, str] | None = None,
        state: dict[str, str] | None = None,
        parse_env_config: bool = False,
        validate_config: bool = True,
    ) -> None:
        """Initialize tap, accepting settings object or raw dict."""
        raw_config: Mapping[str, t.NormalizedValue]
        if isinstance(config, FlextTapOracleWmsSettings):
            raw_config = dict(config.model_dump(mode="json").items())
        else:
            raw_config = dict(config) if config else {}
        parent_init: Callable[..., None] = getattr(super(), "__init__")
        parent_init(
            config=raw_config,
            catalog=catalog,
            state=state,
            parse_env_config=parse_env_config,
            validate_config=validate_config,
        )

    @property
    def catalog_dict_typed(self) -> SingerCatalogDict:
        """Return catalog_dict with proper typing for pyright."""
        raw_catalog_dict: object = getattr(super(), "catalog_dict", {})
        try:
            validated_catalog = _CONTAINER_VALUE_MAP_ADAPTER.validate_python(
                raw_catalog_dict,
            )
        except ValidationError as exc:
            msg = f"Invalid catalog_dict format: {exc}"
            raise FlextTapOracleWmsConfigurationError(msg) from exc
        return self._to_typed_catalog(_safe_str_dict(validated_catalog))

    @staticmethod
    def _to_typed_catalog(raw: dict[str, t.ContainerValue]) -> SingerCatalogDict:
        """Convert raw catalog dict into a typed SingerCatalogDict."""
        raw_streams = raw.get("streams")
        raw_streams_seq: Sequence[t.ContainerValue] = (
            raw_streams
            if isinstance(raw_streams, Sequence)
            and not isinstance(raw_streams, (str, bytes))
            else []
        )
        streams: list[SingerStreamEntry] = []
        for s in raw_streams_seq:
            if not isinstance(s, Mapping):
                continue
            s_dict: Mapping[str, t.ContainerValue] = _safe_str_mapping(s)
            breadcrumb_raw: t.ContainerValue = s_dict.get("metadata", [])
            metadata_entries: list[SingerMetadataEntry] = []
            if isinstance(breadcrumb_raw, list) and not isinstance(
                breadcrumb_raw, (str, bytes)
            ):
                for entry in breadcrumb_raw:
                    if isinstance(entry, dict):
                        bc: t.ContainerValue = entry.get("breadcrumb", [])
                        md: t.ContainerValue = entry.get("metadata", {})
                        metadata_entries.append(
                            SingerMetadataEntry(
                                breadcrumb=[str(x) for x in bc]
                                if isinstance(bc, list)
                                else [],
                                metadata=_safe_str_dict(md)
                                if isinstance(md, dict)
                                else {},
                            )
                        )
            schema_raw: t.ContainerValue = s_dict.get("schema", {})
            streams.append(
                SingerStreamEntry(
                    tap_stream_id=str(s_dict.get("tap_stream_id", "")),
                    stream=str(s_dict.get("stream", "")),
                    schema=_safe_str_dict(schema_raw)
                    if isinstance(schema_raw, dict)
                    else {},
                    metadata=metadata_entries,
                )
            )
        return SingerCatalogDict(streams=streams)

    @property
    def flext_config(self) -> FlextTapOracleWmsSettings:
        """Return validated tap settings."""
        config_map = dict(self.config)
        try:
            return FlextTapOracleWmsSettings.model_validate(config_map)
        except (ValueError, TypeError, KeyError) as exc:
            msg = f"Invalid configuration: {exc}"
            raise FlextTapOracleWmsConfigurationError(msg) from exc

    @property
    def wms_client(self) -> FlextOracleWmsClient:
        """Return a started WMS client instance."""
        if self._wms_client is None:
            password = self.flext_config.password
            wms_settings = FlextOracleWmsSettings.model_validate({
                "base_url": str(self.flext_config.base_url),
                "username": str(self.flext_config.username),
                "password": (
                    password.get_secret_value()
                    if isinstance(password, SecretStr)
                    else str(password)
                ),
                "timeout": float(self.flext_config.timeout),
                "retry_attempts": self.flext_config.max_retries,
            })
            client = FlextOracleWmsClient(config=wms_settings)
            start_result = client.start()
            if start_result.is_failure:
                msg = start_result.error or "Failed to start Oracle WMS client"
                raise FlextTapOracleWmsConfigurationError(msg)
            self._wms_client = client
        return self._wms_client

    @staticmethod
    def _schema_for_entity() -> t.FlatContainerMapping:
        """Return a default Singer JSON schema for discovered entities."""
        return {"type": c.TapOracleWms.SCHEMA_TYPE_OBJECT}

    def discovercatalog_typed(self) -> r[m.Meltano.SingerCatalog]:
        """Discover source entities and convert them into Singer catalog streams."""
        discovery_result = self.wms_client.discover_entities()
        if discovery_result.is_failure:
            return r[m.Meltano.SingerCatalog].fail(
                discovery_result.error or "Discovery failed",
            )
        entities: t.StrSequence = list(discovery_result.value)
        streams = [
            m.Meltano.SingerCatalogEntry.model_validate({
                "tap_stream_id": entity,
                "stream": entity,
                "schema": dict(self._schema_for_entity()),
                "metadata": [
                    m.Meltano.SingerCatalogMetadata(
                        breadcrumb=[],
                        metadata={
                            "inclusion": "available",
                            "forced-replication-method": "FULL_TABLE",
                            "table-key-properties": ["id"],
                        },
                    ),
                ],
                "key_properties": ["id"],
                "replication_key": None,
                "replication_method": "FULL_TABLE",
                "is_view": None,
                "table_name": None,
                "database_name": None,
                "row_count": None,
            })
            for entity in entities
        ]
        return r[m.Meltano.SingerCatalog].ok(
            m.Meltano.SingerCatalog(type="CATALOG", streams=streams),
        )

    @override
    def discover_streams(self) -> Sequence[FlextTapOracleWmsStream]:
        """Build stream objects from the discovered catalog."""
        catalog_result = self.discovercatalog_typed()
        if catalog_result.is_failure:
            msg = f"Catalog discovery failed: {catalog_result.error or 'unknown error'}"
            raise FlextTapOracleWmsConfigurationError(msg)
        streams_raw = catalog_result.value.streams
        if not streams_raw:
            return []
        streams: Sequence[FlextTapOracleWmsStream] = [
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
        return streams

    def execute(self, message: str | None = None) -> r[bool]:
        """Run a full tap sync when no custom message is provided."""
        if message:
            return r[bool].fail("Tap does not support message execution")
        self.sync_all()
        return r[bool].ok(True)

    def get_implementation_metrics(self) -> r[t.ContainerValue]:
        """Return basic runtime metrics for observability."""
        return r[t.ContainerValue].ok({
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

    def validate_configuration(self) -> r[t.ContainerValue]:
        """Expose non-secret validated configuration fields."""
        return r[t.ContainerValue].ok({
            "base_url": str(self.flext_config.base_url),
            "api_version": self.flext_config.api_version,
            "page_size": self.flext_config.page_size,
        })

    def initialize(self) -> r[bool]:
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
        self,
        operation: str,
        _parameters: Mapping[str, t.ContainerValue] | None = None,
    ) -> r[t.ContainerValue]:
        """Execute supported plugin operations against the tap."""
        if self._tap is None:
            init_result = self.initialize(None)
            if init_result.is_failure:
                return r[t.ContainerValue].fail(
                    init_result.error or "Tap initialization failed",
                )
        tap = self._tap
        if tap is None:
            return r[t.ContainerValue].fail("Tap not initialized")
        if operation == "discover":
            catalog_result = tap.discovercatalog_typed()
            if catalog_result.is_failure:
                return r[t.ContainerValue].fail(
                    catalog_result.error or "Discovery failed",
                )
            return r[t.ContainerValue].ok(catalog_result.value.model_dump(mode="json"))
        if operation == "sync":
            execute_result = tap.execute()
            if execute_result.is_failure:
                return r[t.ContainerValue].fail(execute_result.error or "Sync failed")
            return r[t.ContainerValue].ok({"success": True})
        return r[t.ContainerValue].fail(f"Unsupported operation: {operation}")

    def get_info(self) -> Mapping[str, t.ContainerValue]:
        """Return plugin metadata for discovery and capabilities."""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Oracle WMS Singer Tap Plugin",
            "capabilities": ["discover", "sync"],
        }

    def initialize(self, _context: t.ContainerValue | None) -> r[bool]:
        """Instantiate the tap for subsequent operations."""
        self._tap = FlextTapOracleWms(config=dict(self._config))
        return r[bool].ok(True)

    def shutdown(self) -> r[bool]:
        """Release tap resources held by this plugin."""
        self._tap = None
        return r[bool].ok(True)
