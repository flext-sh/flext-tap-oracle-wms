"""Mapping and sequence conversion utilities for the Singer protocol.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping

from flext_meltano import u

from flext_tap_oracle_wms import c, t


class FlextTapOracleWmsUtilitiesConversion:
    """Mapping and sequence conversion utilities composed into ``u.TapOracleWms``."""

    class MappingConversion:
        """Mapping and sequence conversion utilities for Singer protocol."""

        @staticmethod
        def as_map(
            value: t.JsonMapping | t.JsonValue,
            *,
            normalizer: t.TapOracleWms.ScalarNormalizer | None = None,
            map_adapter: t.TapOracleWms.ContainerValueMapAdapter | None = None,
            error_cls: type[Exception] | None = None,
        ) -> t.JsonMapping | None:
            """Convert a NormalizedValue into a Mapping if possible.

            Args:
                value: Value to convert.
                normalizer: Callable that normalizes JSON values.
                map_adapter: TypeAdapter for validating mappings.
                error_cls: Exception class to raise on validation failure.

            Returns:
                Mapping with string keys, or None if not a mapping or when
                adapter validation fails and ``error_cls`` is None.

            """
            if not isinstance(value, Mapping):
                return None
            source: t.JsonMapping = value
            if map_adapter is not None:
                try:
                    source = map_adapter.validate_python(value)
                except c.ValidationError as exc:
                    if error_cls is None:
                        return None
                    msg = f"Validation failed for mapping: {exc}"
                    raise error_cls(msg) from exc
            if normalizer is None:
                return u.json_dict_adapter().validate_python(source)
            return {key: normalizer(item) for key, item in source.items()}

        @staticmethod
        def as_list(
            value: t.JsonValue,
            *,
            normalizer: t.TapOracleWms.ScalarNormalizer | None = None,
            list_adapter: t.TapOracleWms.ContainerValueListAdapter | None = None,
            error_cls: type[Exception] | None = None,
        ) -> t.JsonList | None:
            """Convert a NormalizedValue into a Sequence if possible.

            Args:
                value: Value to convert.
                normalizer: Callable that normalizes JSON values.
                list_adapter: TypeAdapter for validating lists.
                error_cls: Exception class to raise on validation failure.

            Returns:
                Sequence of container values, or None if not a list or when
                adapter validation fails and ``error_cls`` is None.

            """
            if not isinstance(value, list):
                return None
            items: t.JsonList = [str(item) for item in value]
            if list_adapter is not None:
                try:
                    items = list(list_adapter.validate_python(value))
                except c.ValidationError as exc:
                    if error_cls is None:
                        return None
                    msg = f"Validation failed for list: {exc}"
                    raise error_cls(msg) from exc
            if normalizer is None:
                return items
            return [normalizer(item) for item in items]


__all__: list[str] = ["FlextTapOracleWmsUtilitiesConversion"]
