"""FLEXT Tap Oracle WMS Utilities - Domain-specific utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    Sequence,
)

from flext_meltano import u
from flext_oracle_wms import FlextOracleWmsUtilities
from flext_tap_oracle_wms import c, t


class FlextTapOracleWmsUtilities(u, FlextOracleWmsUtilities):
    """Domain-specific Oracle WMS tap utilities.

    Inherits from u to avoid duplication.
    """

    class TapOracleWms:
        """Oracle WMS tap utilities namespace."""

        class ConfigurationProcessing:
            """Configuration processing utilities for Oracle WMS."""

            @staticmethod
            def validate_stream_page_size(page_size: int) -> bool:
                """Validate stream page size.

                Args:
                    page_size: Page size to validate.

                Returns:
                    True if valid, False otherwise.

                """
                return page_size > 0

        class DataProcessing:
            """Data processing utilities for Oracle WMS records."""

            @staticmethod
            def process_wms_record(
                record: t.ContainerValueMapping,
            ) -> t.ContainerValueMapping:
                """Process WMS record for output.

                Args:
                    record: Raw WMS record.

                Returns:
                    Processed record.

                """
                return record

        class MappingConversion:
            """Mapping and sequence conversion utilities for Singer protocol."""

            @staticmethod
            def safe_str_mapping(
                raw: t.ContainerValueMapping,
            ) -> t.ContainerValueMapping:
                """Return a Mapping with str keys from an untyped mapping source.

                Args:
                    raw: Raw mapping to convert.

                Returns:
                    Mapping with string keys.

                """
                return {str(k): v for k, v in raw.items()}

            @staticmethod
            def safe_str_dict(
                raw: t.ContainerValueMapping,
            ) -> dict[str, t.Container]:
                """Return a dict with str keys from an untyped dict source.

                Args:
                    raw: Raw mapping to convert.

                Returns:
                    Dict with string keys.

                """
                return {str(k): v for k, v in raw.items()}

            @staticmethod
            def as_map(
                value: t.Container,
                *,
                normalizer: t.ScalarNormalizer | None = None,
                map_adapter: t.ContainerValueMapAdapter | None = None,
                error_cls: type[Exception] | None = None,
            ) -> t.ContainerValueMapping | None:
                """Convert a NormalizedValue into a Mapping if possible.

                Args:
                    value: Value to convert.
                    normalizer: Callable that normalizes JSON values.
                    map_adapter: TypeAdapter for validating mappings.
                    error_cls: Exception class to raise on validation failure.

                Returns:
                    Mapping with string keys, or None if not a mapping.

                """
                if not isinstance(value, Mapping):
                    return None
                if map_adapter is not None:
                    try:
                        validated_map = map_adapter.validate_python(value)
                    except c.ValidationError as exc:
                        if error_cls is not None:
                            msg = f"Validation failed for mapping: {exc}"
                            raise error_cls(msg) from exc
                        return None
                    if normalizer is not None:
                        return {
                            str(key): normalizer(item)
                            for key, item in validated_map.items()
                        }
                    return {str(key): item for key, item in validated_map.items()}
                if normalizer is not None:
                    return {
                        str(key): normalizer(str(item)) for key, item in value.items()
                    }
                coerced: dict[str, t.Container] = {
                    str(key): str(item) for key, item in value.items()
                }
                return coerced

            @staticmethod
            def as_list(
                value: t.Container,
                *,
                normalizer: t.ScalarNormalizer | None = None,
                list_adapter: t.ContainerValueListAdapter | None = None,
                error_cls: type[Exception] | None = None,
            ) -> Sequence[t.Container] | None:
                """Convert a NormalizedValue into a Sequence if possible.

                Args:
                    value: Value to convert.
                    normalizer: Callable that normalizes JSON values.
                    list_adapter: TypeAdapter for validating lists.
                    error_cls: Exception class to raise on validation failure.

                Returns:
                    Sequence of container values, or None if not a list.

                """
                if not isinstance(value, list):
                    return None
                if list_adapter is not None:
                    try:
                        validated_seq = list_adapter.validate_python(value)
                    except c.ValidationError as exc:
                        if error_cls is not None:
                            msg = f"Validation failed for list: {exc}"
                            raise error_cls(msg) from exc
                        return None
                    if normalizer is not None:
                        return [normalizer(item) for item in validated_seq]
                    return list(validated_seq)
                if normalizer is not None:
                    return [normalizer(str(item)) for item in value]
                coerced_list: list[t.Container] = [str(item) for item in value]
                return coerced_list


u = FlextTapOracleWmsUtilities
"""Facade assignment for module-level utility access."""

__all__: list[str] = [
    "FlextTapOracleWmsUtilities",
    "u",
]
