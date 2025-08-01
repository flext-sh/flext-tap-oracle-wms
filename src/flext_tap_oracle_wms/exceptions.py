"""Oracle WMS tap exception hierarchy using flext-core patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions for Oracle WMS tap operations inheriting from flext-core.
"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)

# =============================================================================
# SOLID REFACTORING: DRY Principle - Centralized context building pattern
# =============================================================================


def _build_exception_context(
    kwargs: dict[str, object],
    **additional_context: object,
) -> dict[str, object]:
    """Build exception context using DRY principle.

    SOLID REFACTORING: Eliminates 126 lines of duplicated context building code
    by centralizing the pattern in a single function.

    Args:
        kwargs: Keyword arguments from exception constructors
        **additional_context: Additional context fields to include

    Returns:
        Dictionary with properly formatted exception context

    """
    context = kwargs.copy()

    # Add additional context fields with None filtering
    for key, value in additional_context.items():
        if value is not None:
            context[key] = value

    return context


class FlextTapOracleWmsError(FlextError):
    """Base exception for Oracle WMS tap operations."""

    def __init__(
        self,
        message: str = "Oracle WMS tap error",
        warehouse_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap error with context."""
        context = kwargs.copy()
        if warehouse_name is not None:
            context["warehouse_name"] = warehouse_name

        super().__init__(message, error_code="ORACLE_WMS_TAP_ERROR", context=context)


class FlextTapOracleWmsConnectionError(FlextConnectionError):
    """Oracle WMS tap connection errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap connection failed",
        wms_endpoint: str | None = None,
        database_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap connection error with context."""
        # SOLID REFACTORING: Use DRY principle - centralized context building
        context = _build_exception_context(
            kwargs,
            wms_endpoint=wms_endpoint,
            database_name=database_name,
        )
        super().__init__(f"Oracle WMS tap connection: {message}", **context)


class FlextTapOracleWmsAuthenticationError(FlextAuthenticationError):
    """Oracle WMS tap authentication errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap authentication failed",
        username: str | None = None,
        warehouse_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap authentication error with context."""
        # SOLID REFACTORING: Use DRY principle - centralized context building
        context = _build_exception_context(
            kwargs,
            username=username,
            warehouse_name=warehouse_name,
        )
        super().__init__(f"Oracle WMS tap auth: {message}", **context)


class FlextTapOracleWmsValidationError(FlextValidationError):
    """Oracle WMS tap validation errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap validation failed",
        field: str | None = None,
        value: object = None,
        entity_type: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap validation error with context."""
        validation_details: dict[str, object] = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)[:100]  # Truncate long values

        context = kwargs.copy()
        if entity_type is not None:
            context["entity_type"] = entity_type

        super().__init__(
            f"Oracle WMS tap validation: {message}",
            validation_details=validation_details,
            context=context,
        )


class FlextTapOracleWmsConfigurationError(FlextConfigurationError):
    """Oracle WMS tap configuration errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap configuration error",
        config_key: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap configuration error with context."""
        # SOLID REFACTORING: Use DRY principle - centralized context building
        context = _build_exception_context(kwargs, config_key=config_key)
        super().__init__(f"Oracle WMS tap config: {message}", **context)


class FlextTapOracleWmsProcessingError(FlextProcessingError):
    """Oracle WMS tap processing errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap processing failed",
        entity_type: str | None = None,
        processing_stage: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap processing error with context."""
        # SOLID REFACTORING: Use DRY principle - centralized context building
        context = _build_exception_context(
            kwargs,
            entity_type=entity_type,
            processing_stage=processing_stage,
        )
        super().__init__(f"Oracle WMS tap processing: {message}", **context)


class FlextTapOracleWmsInventoryError(FlextTapOracleWmsError):
    """Oracle WMS tap inventory-specific errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap inventory error",
        item_code: str | None = None,
        location: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap inventory error with context."""
        # SOLID REFACTORING: Use DRY principle - centralized context building
        context = _build_exception_context(
            kwargs,
            item_code=item_code,
            location=location,
        )
        super().__init__(f"Oracle WMS tap inventory: {message}", **context)


class FlextTapOracleWmsShipmentError(FlextTapOracleWmsError):
    """Oracle WMS tap shipment-specific errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap shipment error",
        shipment_id: str | None = None,
        carrier: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap shipment error with context."""
        # SOLID REFACTORING: Use DRY principle - centralized context building
        context = _build_exception_context(
            kwargs,
            shipment_id=shipment_id,
            carrier=carrier,
        )
        super().__init__(f"Oracle WMS tap shipment: {message}", **context)


class FlextTapOracleWmsTimeoutError(FlextTimeoutError):
    """Oracle WMS tap timeout errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap operation timed out",
        operation: str | None = None,
        timeout_seconds: float | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap timeout error with context."""
        # SOLID REFACTORING: Use DRY principle - centralized context building
        context = _build_exception_context(
            kwargs,
            operation=operation,
            timeout_seconds=timeout_seconds,
        )
        super().__init__(f"Oracle WMS tap timeout: {message}", **context)


class FlextTapOracleWmsStreamError(FlextTapOracleWmsError):
    """Oracle WMS tap stream processing errors."""

    def __init__(
        self,
        message: str = "Oracle WMS tap stream error",
        stream_name: str | None = None,
        entity_type: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize Oracle WMS tap stream error with context."""
        # SOLID REFACTORING: Use DRY principle - centralized context building
        context = _build_exception_context(
            kwargs,
            stream_name=stream_name,
            entity_type=entity_type,
        )
        super().__init__(f"Oracle WMS tap stream: {message}", **context)


__all__ = [
    "FlextTapOracleWmsAuthenticationError",
    "FlextTapOracleWmsConfigurationError",
    "FlextTapOracleWmsConnectionError",
    "FlextTapOracleWmsError",
    "FlextTapOracleWmsInventoryError",
    "FlextTapOracleWmsProcessingError",
    "FlextTapOracleWmsShipmentError",
    "FlextTapOracleWmsStreamError",
    "FlextTapOracleWmsTimeoutError",
    "FlextTapOracleWmsValidationError",
]
