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
        context = kwargs.copy()
        if wms_endpoint is not None:
            context["wms_endpoint"] = wms_endpoint
        if database_name is not None:
            context["database_name"] = database_name

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
        context = kwargs.copy()
        if username is not None:
            context["username"] = username
        if warehouse_name is not None:
            context["warehouse_name"] = warehouse_name

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
        validation_details = {}
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
        context = kwargs.copy()
        if config_key is not None:
            context["config_key"] = config_key

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
        context = kwargs.copy()
        if entity_type is not None:
            context["entity_type"] = entity_type
        if processing_stage is not None:
            context["processing_stage"] = processing_stage

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
        context = kwargs.copy()
        if item_code is not None:
            context["item_code"] = item_code
        if location is not None:
            context["location"] = location

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
        context = kwargs.copy()
        if shipment_id is not None:
            context["shipment_id"] = shipment_id
        if carrier is not None:
            context["carrier"] = carrier

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
        context = kwargs.copy()
        if operation is not None:
            context["operation"] = operation
        if timeout_seconds is not None:
            context["timeout_seconds"] = timeout_seconds

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
        context = kwargs.copy()
        if stream_name is not None:
            context["stream_name"] = stream_name
        if entity_type is not None:
            context["entity_type"] = entity_type

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
