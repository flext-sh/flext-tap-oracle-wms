"""Enterprise Pydantic models for Oracle WMS Tap - Python 3.13+ with modern typing.

MIGRATED TO FLEXT-CORE PATTERNS:
Uses flext-core base classes, types, and constants. Zero tolerance for code duplication.
"""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from datetime import datetime

from flext_core.domain.pydantic_base import DomainBaseModel
from flext_core.domain.pydantic_base import DomainValueObject
from pydantic import Field
from pydantic import HttpUrl
from pydantic import field_validator


# Simple constants for compatibility
class FlextConstants:
    """Enterprise constants for FLEXT Oracle WMS integration."""

    MAX_ENTITY_NAME_LENGTH = 255
    MAX_ERROR_MESSAGE_LENGTH = 1000
    DEFAULT_TIMEOUT = 30
    FRAMEWORK_VERSION = "0.7.0"


class WMSConfig(DomainBaseModel):
    """Simplified, enterprise-ready WMS configuration using flext-core patterns."""

    # Core connection settings
    base_url: HttpUrl = Field(..., description="Oracle WMS base URL")
    username: str = Field(..., min_length=1, description="Authentication username")
    password: str = Field(..., min_length=1, description="Authentication password")

    # WMS scoping (simplified from complex multi-layer system)
    company_code: str = Field(default="*", description="WMS company code")
    facility_code: str = Field(default="*", description="WMS facility code")

    # Performance settings (reduced from 50+ options)
    page_size: int = Field(default=500, ge=1, le=10000, description="Records per page")
    timeout: int = Field(
        default=FlextConstants.DEFAULT_TIMEOUT,
        ge=1,
        le=300,
        description="Request timeout",
    )
    max_retries: int = Field(
        default=3, ge=0, le=10, description="Maximum retry attempts",
    )

    # Discovery settings (simplified)
    auto_discover: bool = Field(
        default=True, description="Enable automatic entity discovery",
    )
    include_metadata: bool = Field(
        default=True, description="Include metadata in responses",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: HttpUrl) -> HttpUrl:
        """Validate base URL format for Oracle WMS.

        Args:
            v: HttpUrl to validate

        Returns:
            Validated HttpUrl instance

        Raises:
            ValueError: If URL format is invalid

        """
        url_str = str(v)
        if not url_str.startswith(("http://", "https://")):
            msg = "Base URL must start with http:// or https://"
            raise ValueError(msg)
        return v


class WMSEntity(DomainValueObject):
    """WMS entity metadata using flext-core value object patterns."""

    name: str = Field(
        ..., min_length=1, max_length=FlextConstants.MAX_ENTITY_NAME_LENGTH,
    )
    description: str | None = Field(
        None, max_length=FlextConstants.MAX_ERROR_MESSAGE_LENGTH,
    )
    endpoint: str = Field(..., min_length=1, description="API endpoint path")

    # Entity characteristics
    supports_incremental: bool = Field(
        default=False, description="Supports incremental sync",
    )
    primary_key: str | None = Field(None, description="Primary key field name")
    timestamp_field: str | None = Field(
        None, description="Timestamp field for incremental sync",
    )

    # Metadata
    fields: list[str] = Field(default_factory=list, description="Available field names")
    total_records: int | None = Field(
        None, ge=0, description="Total record count if known",
    )


class WMSStreamMetadata(DomainValueObject):
    """Stream metadata for Singer protocol compliance."""

    stream_name: str = Field(
        ..., min_length=1, max_length=FlextConstants.MAX_ENTITY_NAME_LENGTH,
    )
    key_properties: list[str] = Field(
        default_factory=list, description="Primary key fields",
    )
    replication_method: str = Field(
        default="FULL_TABLE", description="Replication method",
    )
    replication_key: str | None = Field(None, description="Incremental replication key")

    # Schema information
    json_schema: dict[str, Any] = Field(default_factory=dict, description="JSON schema")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Stream metadata",
    )


class WMSRecord(DomainBaseModel):
    """WMS record with tracking and validation using flext-core patterns."""

    # Core data
    stream_name: str = Field(..., min_length=1, description="Source stream name")
    record_data: dict[str, Any] = Field(..., description="Record payload")

    # Tracking information
    extracted_at: datetime = Field(..., description="Extraction timestamp")
    record_id: str | None = Field(None, description="Record identifier if available")

    # Processing metadata
    source_endpoint: str = Field(..., description="Source API endpoint")
    page_number: int | None = Field(None, ge=1, description="Source page number")

    @field_validator("record_data")
    @classmethod
    def validate_record_data(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate record data is not empty.

        Args:
            v: Record data dictionary to validate

        Returns:
            Validated record data dictionary

        Raises:
            ValueError: If record data is empty

        """
        if not v:
            msg = "Record data cannot be empty"
            raise ValueError(msg)
        return v


class WMSError(DomainValueObject):
    """WMS error information using flext-core value object patterns."""

    error_type: str = Field(..., min_length=1, description="Error type classification")
    message: str = Field(
        ..., min_length=1, max_length=FlextConstants.MAX_ERROR_MESSAGE_LENGTH,
    )
    endpoint: str | None = Field(None, description="Related API endpoint")

    # Error context
    status_code: int | None = Field(
        None, ge=100, le=599, description="HTTP status code",
    )
    timestamp: datetime = Field(..., description="Error occurrence time")
    retryable: bool = Field(default=False, description="Whether error is retryable")

    # Additional context
    request_id: str | None = Field(None, description="Request identifier")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Additional error details",
    )


class WMSDiscoveryResult(DomainBaseModel):
    """Discovery operation result using flext-core patterns."""

    # Discovery metadata
    discovered_at: datetime = Field(..., description="Discovery timestamp")
    base_url: str = Field(..., description="WMS base URL")
    total_entities: int = Field(
        default=0, ge=0, description="Number of entities discovered",
    )

    # Discovered entities
    entities: list[WMSEntity] = Field(
        default_factory=list, description="Discovered entities",
    )
    errors: list[WMSError] = Field(default_factory=list, description="Discovery errors")

    # Operation summary
    success: bool = Field(default=True, description="Overall discovery success")
    duration_seconds: float | None = Field(None, ge=0, description="Discovery duration")

    @property
    def successful_entities(self) -> list[WMSEntity]:
        """Get entities that were successfully discovered."""
        return [entity for entity in self.entities if entity.name]

    @property
    def failed_count(self) -> int:
        """Get count of failed discoveries."""
        return len(self.errors)

    def add_entity(self, entity: WMSEntity) -> None:
        """Add a discovered entity."""
        self.entities.append(entity)
        self.total_entities = len(self.entities)

    def add_error(self, error: WMSError) -> None:
        """Add a discovery error."""
        self.errors.append(error)
        if error.error_type in {"authentication", "network"}:
            self.success = False


class TapMetrics(DomainBaseModel):
    """Metrics tracking for the tap operations."""

    api_calls: int = Field(
        default=0, ge=0, description="Number of API calls made",
    )
    records_processed: int = Field(
        default=0, ge=0, description="Number of records processed",
    )
    errors_encountered: int = Field(
        default=0, ge=0, description="Number of errors encountered",
    )
    start_time: datetime | None = Field(None, description="Tap start time")

    def add_api_call(self) -> None:
        """Increment API call counter."""
        self.api_calls += 1

    def add_record(self) -> None:
        """Increment record counter."""
        self.records_processed += 1

    def add_error(self) -> None:
        """Increment error counter."""
        self.errors_encountered += 1


# Export main models
__all__ = [
    "FlextConstants",
    "TapMetrics",
    "WMSConfig",
    "WMSDiscoveryResult",
    "WMSEntity",
    "WMSError",
    "WMSRecord",
    "WMSStreamMetadata",
]
