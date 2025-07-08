"""Enterprise Pydantic models for Oracle WMS Tap - Python 3.13+ with modern typing."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class WMSConfig(BaseModel):
    """Simplified, enterprise-ready WMS configuration using Pydantic V2."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        frozen=True,
    )

    # Core connection settings
    base_url: HttpUrl = Field(..., description="Oracle WMS base URL")
    username: str = Field(..., min_length=1, description="Authentication username")
    password: str = Field(..., min_length=1, description="Authentication password")

    # WMS scoping (simplified from complex multi-layer system)
    company_code: str = Field(default="*", description="WMS company code")
    facility_code: str = Field(default="*", description="WMS facility code")

    # Performance settings (reduced from 50+ options)
    page_size: int = Field(default=100, ge=1, le=1250, description="Records per page")
    request_timeout: int = Field(
        default=120,
        ge=1,
        le=300,
        description="Request timeout seconds",
    )

    # Security
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: HttpUrl) -> HttpUrl:
        """Ensure URL is HTTPS in production."""
        if str(v).startswith("http://"):
            msg = "HTTP URLs not allowed - use HTTPS"
            raise ValueError(msg)
        return v


class WMSEntity(BaseModel):
    """WMS entity representation with minimal required fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(..., min_length=1)
    endpoint: str = Field(..., min_length=1)
    has_mod_ts: bool = Field(default=False, description="Supports incremental sync")
    fields: list[str] = Field(default_factory=list)


class WMSRecord(BaseModel):
    """Generic WMS record structure."""

    model_config = ConfigDict(extra="allow")  # Allow extra fields from WMS

    # Common WMS fields
    mod_ts: datetime | None = Field(default=None, description="Modification timestamp")
    id: str | int | None = Field(default=None, description="Record identifier")

    # All other fields allowed via extra="allow"


class StreamState(BaseModel):
    """Singer stream state for incremental sync."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    stream_name: str = Field(..., min_length=1)
    last_mod_ts: datetime | None = Field(default=None)
    last_id: str | int | None = Field(default=None)


class TapMetrics(BaseModel):
    """Performance and monitoring metrics."""

    model_config = ConfigDict(extra="forbid")

    records_extracted: int = Field(default=0, ge=0)
    entities_discovered: int = Field(default=0, ge=0)
    api_calls_made: int = Field(default=0, ge=0)
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(UTC)

    def add_records(self, count: int) -> None:
        """Add to records count and update activity."""
        self.records_extracted += count
        self.update_activity()

    def add_api_call(self) -> None:
        """Increment API call count and update activity."""
        self.api_calls_made += 1
        self.update_activity()


# Type aliases for modern Python 3.13 typing
type EntityDict = dict[str, WMSEntity]
type RecordDict = dict[str, Any]
type StateDict = dict[str, StreamState]
