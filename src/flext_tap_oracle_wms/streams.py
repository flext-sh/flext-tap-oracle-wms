"""Oracle WMS Stream implementations for Singer protocol.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import ClassVar, override

from flext_core import FlextLogger, r
from flext_oracle_wms import FlextOracleWmsClient
from pydantic import BaseModel, TypeAdapter, ValidationError
from singer_sdk.streams import Stream
from singer_sdk.tap_base import Tap

from flext_tap_oracle_wms import p, t, u

logger = FlextLogger(__name__)
_CONTAINER_VALUE_MAP_ADAPTER: TypeAdapter[t.ContainerValueMapping] = TypeAdapter(
    t.ContainerValueMapping,
)
_CONTAINER_VALUE_LIST_ADAPTER: TypeAdapter[t.ContainerValueList] = TypeAdapter(
    t.ContainerValueList,
)


def _as_map(value: t.NormalizedValue) -> Mapping[str, t.ContainerValue] | None:
    if not isinstance(value, Mapping):
        return None
    try:
        validated_map = _CONTAINER_VALUE_MAP_ADAPTER.validate_python(value)
    except ValidationError:
        return None
    return {
        str(key): FlextTapOracleWmsStream.normalize_json_value(item)
        for key, item in validated_map.items()
    }


def _as_list(value: t.NormalizedValue) -> Sequence[t.ContainerValue] | None:
    if not isinstance(value, list):
        return None
    try:
        validated_list = _CONTAINER_VALUE_LIST_ADAPTER.validate_python(value)
    except ValidationError:
        return None
    return [
        FlextTapOracleWmsStream.normalize_json_value(item) for item in validated_list
    ]


class FlextTapOracleWmsStream(Stream):
    """Dynamic stream for Oracle WMS entities.

    Uses flext-oracle-wms client for all data operations.
    This is a generic stream class that adapts to any Oracle WMS entity dynamically.
    """

    stream_primary_keys: ClassVar[t.StrSequence] = []
    stream_replication_key: str | None = None
    url_base: str = ""
    # Singer SDK attributes exposed for type narrowing in tests/consumers
    tap: Tap
    http_headers: MutableMapping[str, str]
    authenticator: None = None

    @override
    def __init__(
        self,
        tap: Tap,
        name: str | None = None,
        schema: Mapping[str, t.ContainerValue] | None = None,
        _path: str | None = None,
    ) -> None:
        """Initialize stream."""
        schema_dict: dict[str, t.ContainerValue] | None = (
            dict(schema) if schema is not None else None
        )
        Stream.__init__(self, tap=tap, name=name or self.name, schema=schema_dict)
        self._client: FlextOracleWmsClient | None = None
        page_size = int(self.config.get("page_size", 100))
        self._page_size = (
            page_size
            if u.TapOracleWms.ConfigurationProcessing.validate_stream_page_size(
                page_size,
            )
            else 100
        )

    @property
    @override
    def schema(self) -> dict[str, t.ContainerValue]:
        """Return typed stream schema (overrides Singer SDK's bare dict)."""
        raw: dict[str, t.ContainerValue] = Stream.schema.__get__(self)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        return raw

    @property
    def client(self) -> FlextOracleWmsClient:
        """Get WMS client from tap."""
        if self._client is not None:
            return self._client
        tap_instance = self._tap
        if not isinstance(
            tap_instance,
            p.TapOracleWms.OracleWms.TapWithWmsClient,
        ):
            msg = "WMS client not available - tap must be FlextTapOracleWms"
            raise TypeError(msg)
        client: FlextOracleWmsClient = tap_instance.wms_client
        self._client = client
        return client

    @staticmethod
    def normalize_json_value(value: t.NormalizedValue) -> t.Scalar:
        """Normalize arbitrary values into Singer-compatible JSON values."""
        if isinstance(value, t.SCALAR_TYPES):
            return value
        if value is None:
            return ""
        list_value = _as_list(value)
        if list_value is not None:
            return str([
                FlextTapOracleWmsStream.normalize_json_value(item)
                for item in list_value
            ])
        map_value = _as_map(value)
        if map_value is not None:
            return str({
                key: FlextTapOracleWmsStream.normalize_json_value(item)
                for key, item in map_value.items()
            })
        if isinstance(value, BaseModel | Path):
            return str(value)
        return str(value)

    def get_primary_keys(self) -> t.StrSequence:
        """Get primary keys for this stream."""
        return list(self.stream_primary_keys)

    @override
    def get_records(
        self,
        context: Mapping[str, t.Scalar] | None,
    ) -> Iterable[dict[str, t.Scalar]]:
        """Get records from Oracle WMS."""
        page = 1
        has_more = True
        while has_more:
            try:
                page_result = self._fetch_page_data(page, context)
                if page_result.is_failure:
                    logger.error(
                        "Failed to fetch page %s for %s: %s",
                        page,
                        self.name,
                        page_result.error or "",
                    )
                    break
                records, has_more = page_result.value
                yield from self._process_page_records(records, context)
                page += 1
                if not records:
                    break
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ):
                logger.exception("Error getting records for %s", self.name)
                break

    def get_replication_key(self) -> str | None:
        """Get replication key for this stream."""
        return self.stream_replication_key

    def get_url_params(
        self,
        _context: Mapping[str, t.Scalar] | None,
        next_page_token: t.Scalar | None,
    ) -> Mapping[str, t.Scalar]:
        """Return URL params for REST-style pagination (stub for API compatibility)."""
        params: MutableMapping[str, t.Scalar] = {"page_size": self._page_size}
        if next_page_token is not None:
            params["page"] = next_page_token
        return params

    def parse_response(
        self,
        response: t.ContainerValue,
    ) -> Iterable[Mapping[str, t.ContainerValue]]:
        """Parse response data (stub for API compatibility)."""
        if isinstance(response, Mapping):
            data = response.get("data", [])
            if isinstance(data, Sequence):
                for item in data:
                    if isinstance(item, Mapping):
                        yield {str(k): v for k, v in item.items()}

    def _extract_records_from_response(
        self,
        response: t.ContainerValue,
    ) -> Iterable[Mapping[str, t.ContainerValue]]:
        """Extract records from a raw response (stub for API compatibility)."""
        yield from self.parse_response(response)

    @override
    def post_process(
        self,
        row: dict[str, t.Scalar],
        context: Mapping[str, t.Scalar] | None = None,
    ) -> dict[str, t.Scalar]:
        """Post-process a record."""
        config_map: t.ContainerMapping = self.config
        column_mappings_raw = config_map.get("column_mappings")
        column_mappings = _as_map(column_mappings_raw) if column_mappings_raw else None
        if column_mappings is not None:
            mapping_raw = column_mappings.get(self.name)
            mapping = _as_map(mapping_raw) if mapping_raw is not None else None
            if mapping is not None:
                for old_name, new_name in mapping.items():
                    new_name_str = str(new_name)
                    if old_name in row:
                        row[new_name_str] = row.pop(old_name)
        ignored_columns_raw = config_map.get("ignored_columns")
        ignored_columns = _as_list(ignored_columns_raw) if ignored_columns_raw else None
        if ignored_columns is not None:
            for column_name in ignored_columns:
                if isinstance(column_name, str):
                    row.pop(column_name, None)
        if context:
            row["_context"] = str({k: str(v) for k, v in context.items()})
        return row

    def _build_operation_kwargs(
        self,
        page: int,
        context: Mapping[str, t.Scalar] | None,
    ) -> MutableMapping[str, t.Scalar]:
        """Build kwargs for the operation call."""
        result_kwargs: MutableMapping[str, t.Scalar] = {}
        result_kwargs["page"] = page
        result_kwargs["limit"] = self._page_size
        if self.stream_replication_key:
            starting_timestamp = self.get_starting_timestamp(context)
            if starting_timestamp:
                kwargs_filter = (
                    f"{self.stream_replication_key}>={starting_timestamp.isoformat()}"
                )
                result_kwargs["filter"] = kwargs_filter
        return result_kwargs

    def _fetch_page_data(
        self,
        page: int,
        context: Mapping[str, t.Scalar] | None,
    ) -> r[tuple[Sequence[t.ScalarMapping], bool]]:
        """Fetch data for a specific page."""
        kwargs = self._build_operation_kwargs(page, context)
        limit_raw = kwargs.get("limit")
        limit = int(limit_raw) if isinstance(limit_raw, int) else self._page_size
        filters: MutableMapping[str, t.Scalar] = {}
        filter_raw = kwargs.get("filter")
        if isinstance(filter_raw, str) and self.stream_replication_key:
            filters[self.stream_replication_key] = filter_raw
        result = self.client.get_entity_data(
            entity_name=self.name,
            limit=limit,
            filters=filters or None,
        )
        if result.is_failure:
            return r[tuple[Sequence[t.ScalarMapping], bool]].fail(
                f"Failed to get records for {self.name}: {result.error}",
            )
        normalized: Sequence[t.ScalarMapping] = [
            {
                str(key): self.normalize_json_value(value)
                for key, value in record.items()
            }
            for record in result.value
        ]
        has_more = len(normalized) == self._page_size
        return r[tuple[Sequence[t.ScalarMapping], bool]].ok((
            normalized,
            has_more,
        ))

    def _process_page_records(
        self,
        records: Sequence[t.ScalarMapping],
        context: Mapping[str, t.Scalar] | None,
    ) -> Iterable[dict[str, t.Scalar]]:
        """Process and yield records from a page."""
        for record in records:
            record_dict: Mapping[str, t.ContainerValue] = dict(record)
            processed_record: Mapping[str, t.ContainerValue] = (
                u.TapOracleWms.DataProcessing.process_wms_record(
                    record=record_dict,
                )
            )
            processed_map = _as_map(processed_record)
            if processed_map is None:
                continue
            json_row: dict[str, t.Scalar] = {
                str(k): self.normalize_json_value(v) for k, v in processed_map.items()
            }
            yield self.post_process(json_row, context)

    def _run(self, value: t.Scalar) -> t.Scalar:
        return value
