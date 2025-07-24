"""🚨 ARCHITECTURAL COMPLIANCE: DI Container for flext-tap-oracle-wms."""

from __future__ import annotations

from typing import Any


def get_service_result() -> Any:
    try:
        from flext_core import ServiceResult

        return ServiceResult
    except ImportError as e:
        raise ImportError(f"Failed to load FlextResult: {e}") from e


def get_domain_entity() -> Any:
    try:
        from flext_core import FlextEntity

        return FlextEntity
    except ImportError as e:
        raise ImportError(f"Failed to load FlextEntity: {e}") from e


def get_field() -> Any:
    try:
        from flext_core import FlextField

        return FlextField
    except ImportError as e:
        raise ImportError(f"Failed to load FlextField: {e}") from e


def get_domain_value_object() -> Any:
    try:
        from flext_core import FlextValueObject

        return FlextValueObject
    except ImportError as e:
        raise ImportError(f"Failed to load FlextValueObject: {e}") from e


def get_base_config() -> Any:
    try:
        from flext_core import FlextCoreSettings

        return FlextCoreSettings
    except ImportError as e:
        raise ImportError(f"Failed to load FlextCoreSettings: {e}") from e
