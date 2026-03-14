"""Oracle WMS Stream implementations for Singer protocol.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
from typing import ClassVar, override

from flext_core import FlextLogger, r, t
from flext_oracle_wms import FlextOracleWmsClient
from pydantic import BaseModel, TypeAdapter, ValidationError
from singer_sdk.streams import Stream
from singer_sdk.tap_base import Tap

from flext_tap_oracle_wms.protocols import p
from flext_tap_oracle_wms.utilities import FlextTapOracleWmsUtilities

logger = FlextLogger(__name__)


def _as_map(value: object) -> Mapping[str, t.ContainerValue] | None:
    if not isinstance(value, Mapping):
        return None
    try:
        validated_map = TypeAdapter(dict[str, object]).validate_python(value)
    except ValidationError:
        return None
    return {
        str(key): FlextTapOracleWmsStream.normalize_json_value(item)
        for key, item in validated_map.items()
    }


def _as_list(value: object) -> list[t.ContainerValue] | None:
    if not isinstance(value, list):
        return None
    try:
        validated_list = TypeAdapter(list[object]).validate_python(value)
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

    stream_primary_keys: ClassVar[list[str]] = []
    stream_replication_key: str | None = None

    @override
    def __init__(
        self,
        tap: Tap,
        name: str | None = None,
        schema: dict[str, t.Container] | None = None,
        _path: str | None = None,
    ) -> None:
        """Initialize stream."""
        Stream.__init__(self, tap=tap, name=name or self.name, schema=schema)
        self._utilities = FlextTapOracleWmsUtilities()
        self._client: FlextOracleWmsClient | None = None
        page_size = int(self.config.get("page_size", 100))
        self._page_size = (
            page_size
            if self._utilities.ConfigurationProcessing.validate_stream_page_size(
                page_size
            )
            else 100
        )

    @property
    def client(self) -> FlextOracleWmsClient:
        """Get WMS client from tap."""
        if self._client is None:
            tap_instance = self._tap
            if tap_instance and isinstance(
                tap_instance, p.TapOracleWms.OracleWms.TapWithWmsClient
            ):
                wms_tap: p.TapOracleWms.OracleWms.TapWithWmsClient = tap_instance
                self._client = wms_tap.wms_client
            else:
                msg = "WMS client not available - tap must be FlextTapOracleWms"
                raise RuntimeError(msg)
        return self._client

    @staticmethod
    def normalize_json_value(value: object) -> t.Scalar:
        """Normalize arbitrary values into Singer-compatible JSON values."""
        if isinstance(value, str | int | float | bool | datetime):
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

    def get_primary_keys(self) -> list[str]:
        """Get primary keys for this stream."""
        return list(self.stream_primary_keys)

    @override
    def get_records(
        self, context: Mapping[str, t.Scalar] | None
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

    @override
    def post_process(
        self,
        row: dict[str, t.Scalar],
        context: Mapping[str, t.Scalar] | None = None,
    ) -> dict[str, t.Scalar]:
        """Post-process a record."""
        config_map: Mapping[str, object] = self.config
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
        self, page: int, context: Mapping[str, t.Scalar] | None
    ) -> Mapping[str, t.Scalar]:
        """Build kwargs for the operation call."""
        kwargs: dict[str, t.Scalar] = {"page": page, "limit": self._page_size}
        if self.stream_replication_key:
            starting_timestamp = self.get_starting_timestamp(context)
            if starting_timestamp:
                kwargs_filter = (
                    f"{self.stream_replication_key}>={starting_timestamp.isoformat()}"
                )
                kwargs["filter"] = kwargs_filter
        return kwargs

    def _fetch_page_data(
        self, page: int, context: Mapping[str, t.Scalar] | None
    ) -> r[tuple[list[dict[str, t.Scalar]], bool]]:
        """Fetch data for a specific page."""
        kwargs = self._build_operation_kwargs(page, context)
        limit_raw = kwargs.get("limit")
        limit = int(limit_raw) if isinstance(limit_raw, int) else self._page_size
        filters: dict[str, t.Scalar] = {}
        filter_raw = kwargs.get("filter")
        if isinstance(filter_raw, str) and self.stream_replication_key:
            filters[self.stream_replication_key] = filter_raw
        result = self.client.get_entity_data(
            entity_name=self.name, limit=limit, filters=filters or None
        )
        if result.is_failure:
            return r[tuple[list[dict[str, t.Scalar]], bool]].fail(
                f"Failed to get records for {self.name}: {result.error}"
            )
        normalized: list[dict[str, t.Scalar]] = [
            {
                str(key): self.normalize_json_value(value)
                for key, value in record.items()
            }
            for record in result.value
        ]
        has_more = len(normalized) == self._page_size
        return r[tuple[list[dict[str, t.Scalar]], bool]].ok((
            normalized,
            has_more,
        ))

    def _process_page_records(
        self,
        records: list[dict[str, t.Scalar]],
        context: Mapping[str, t.Scalar] | None,
    ) -> Iterable[dict[str, t.Scalar]]:
        """Process and yield records from a page."""
        for record in records:
            record_dict: dict[str, t.Scalar] = dict(record)
            processed_record = self._utilities.DataProcessing.process_wms_record(
                record=record_dict
            )
            processed_map = _as_map(processed_record)
            if processed_map is None:
                continue
            json_row: dict[str, t.Scalar] = {
                str(k): self.normalize_json_value(v) for k, v in processed_map.items()
            }
            yield self.post_process(json_row, context)

    def _run(self, value: object) -> object:
        return value
