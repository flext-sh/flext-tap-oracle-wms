"""Oracle WMS Models using standardized [Project]Models pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, SecretStr

from flext_core import FlextModels, FlextTypes


class FlextTapOracleWmsModels(FlextModels):
    """Oracle WMS tap models extending flext-core FlextModels.

    Provides comprehensive models for Oracle WMS entity extraction, authentication,
    stream configuration, and Singer protocol compliance following standardized patterns.
    """

    class WmsAuthenticationConfig(FlextModels.BaseConfig):
        """Oracle WMS authentication configuration."""

        base_url: str = Field(..., description="Oracle WMS instance URL")
        username: str = Field(..., description="WMS username")
        password: SecretStr = Field(..., description="WMS password")
        auth_method: Literal["basic", "oauth2"] = Field(
            default="basic", description="Authentication method"
        )

        # Organizational configuration
        company_code: str = Field(..., description="Company code identifier")
        facility_code: str = Field(
            ..., description="Facility/warehouse code identifier"
        )

        # Optional authentication settings
        request_timeout: int = Field(
            default=120, ge=30, le=600, description="Request timeout in seconds"
        )
        max_retries: int = Field(
            default=3, ge=1, le=10, description="Maximum retry attempts"
        )
        concurrent_requests: int = Field(
            default=3, ge=1, le=5, description="Concurrent requests limit"
        )

    class WmsEntityBase(FlextModels.Entity):
        """Base model for Oracle WMS entities."""

        entity_id: str = Field(..., description="Unique entity identifier")
        entity_name: str | None = Field(None, description="Entity display name")
        date_time_stamp: datetime | None = Field(
            None, description="WMS timestamp for replication"
        )
        company_code: str | None = Field(None, description="Associated company code")
        facility_code: str | None = Field(None, description="Associated facility code")

    class WmsItemEntity(WmsEntityBase):
        """Oracle WMS Item master entity."""

        item_id: str = Field(..., description="Unique item identifier")
        item_desc: str | None = Field(None, description="Item description")
        item_category: str | None = Field(
            None, description="Item category classification"
        )
        item_type: str | None = Field(None, description="Item type")
        item_status: str | None = Field(
            None, description="Item status (Active/Inactive)"
        )

        # Physical attributes
        weight: float | None = Field(None, description="Item weight")
        volume: float | None = Field(None, description="Item volume")
        length: float | None = Field(None, description="Item length")
        width: float | None = Field(None, description="Item width")
        height: float | None = Field(None, description="Item height")

        # Business attributes
        unit_of_measure: str | None = Field(None, description="Primary unit of measure")
        lot_control: str | None = Field(None, description="Lot control flag")
        expiry_date_tracking: str | None = Field(
            None, description="Expiry date tracking flag"
        )
        serial_number_tracking: str | None = Field(
            None, description="Serial number tracking flag"
        )

    class WmsLocationEntity(WmsEntityBase):
        """Oracle WMS Location entity."""

        location_id: str = Field(..., description="Unique location identifier")
        location_type: str | None = Field(
            None, description="Location type (Pick, Reserve, etc.)"
        )
        location_status: str | None = Field(None, description="Location status")
        zone_id: str | None = Field(None, description="Zone identifier")
        area_id: str | None = Field(None, description="Area identifier")

        # Physical attributes
        aisle: str | None = Field(None, description="Aisle identifier")
        bay: str | None = Field(None, description="Bay identifier")
        tier: str | None = Field(None, description="Tier level")
        position: str | None = Field(None, description="Position identifier")

        # Capacity attributes
        max_weight: float | None = Field(None, description="Maximum weight capacity")
        max_volume: float | None = Field(None, description="Maximum volume capacity")
        location_capacity: int | None = Field(
            None, description="Location unit capacity"
        )

    class WmsInventoryEntity(WmsEntityBase):
        """Oracle WMS Inventory entity with current stock levels."""

        item_id: str = Field(..., description="Item identifier")
        location_id: str = Field(..., description="Location identifier")
        lot_number: str | None = Field(None, description="Lot number")
        lot_expiry_date: datetime | None = Field(None, description="Lot expiry date")

        # Quantity information
        quantity_on_hand: float | None = Field(None, description="Quantity on hand")
        quantity_allocated: float | None = Field(None, description="Quantity allocated")
        quantity_available: float | None = Field(None, description="Quantity available")
        quantity_reserved: float | None = Field(None, description="Quantity reserved")
        quantity_damaged: float | None = Field(None, description="Quantity damaged")

        # Status information
        inventory_status: str | None = Field(None, description="Inventory status")
        lock_code: str | None = Field(None, description="Lock code if locked")
        unit_of_measure: str | None = Field(None, description="Unit of measure")

    class WmsOrderEntity(WmsEntityBase):
        """Oracle WMS Order entity for warehouse orders."""

        order_id: str = Field(..., description="Unique order identifier")
        order_type: str | None = Field(
            None, description="Order type (Outbound, Inbound, etc.)"
        )
        order_status: str | None = Field(None, description="Order status")
        priority: int | None = Field(None, description="Order priority")

        # Customer/supplier information
        customer_id: str | None = Field(None, description="Customer identifier")
        supplier_id: str | None = Field(None, description="Supplier identifier")
        carrier_id: str | None = Field(None, description="Carrier identifier")

        # Temporal information
        order_date: datetime | None = Field(None, description="Order creation date")
        requested_date: datetime | None = Field(
            None, description="Requested delivery date"
        )
        shipped_date: datetime | None = Field(None, description="Actual ship date")

        # Order details
        total_lines: int | None = Field(None, description="Total order lines")
        total_quantity: float | None = Field(None, description="Total order quantity")
        total_weight: float | None = Field(None, description="Total order weight")
        total_volume: float | None = Field(None, description="Total order volume")

    class WmsShipmentEntity(WmsEntityBase):
        """Oracle WMS Shipment entity for shipment tracking."""

        shipment_id: str = Field(..., description="Unique shipment identifier")
        shipment_status: str | None = Field(None, description="Shipment status")
        shipment_type: str | None = Field(None, description="Shipment type")
        carrier_id: str | None = Field(None, description="Carrier identifier")
        tracking_number: str | None = Field(None, description="Carrier tracking number")

        # Shipment details
        total_weight: float | None = Field(None, description="Total shipment weight")
        total_volume: float | None = Field(None, description="Total shipment volume")
        total_orders: int | None = Field(None, description="Total orders in shipment")

        # Temporal information
        ship_date: datetime | None = Field(None, description="Ship date")
        estimated_delivery: datetime | None = Field(
            None, description="Estimated delivery date"
        )
        actual_delivery: datetime | None = Field(
            None, description="Actual delivery date"
        )

    class WmsUserEntity(WmsEntityBase):
        """Oracle WMS User entity for user management."""

        user_id: str = Field(..., description="Unique user identifier")
        user_name: str = Field(..., description="User login name")
        user_type: str | None = Field(
            None, description="User type (Employee, Admin, etc.)"
        )
        user_status: str | None = Field(
            None, description="User status (Active/Inactive)"
        )

        # User details
        first_name: str | None = Field(None, description="User first name")
        last_name: str | None = Field(None, description="User last name")
        email_address: str | None = Field(None, description="User email address")
        phone_number: str | None = Field(None, description="User phone number")

        # Role and permissions
        role_id: str | None = Field(None, description="Assigned role identifier")
        permission_level: str | None = Field(None, description="Permission level")
        default_facility: str | None = Field(
            None, description="Default facility assignment"
        )

        # Activity tracking
        last_login_date: datetime | None = Field(
            None, description="Last login timestamp"
        )
        login_count: int | None = Field(None, description="Total login count")

    class WmsStreamMetadata(FlextModels.BaseConfig):
        """Stream metadata for Oracle WMS streams."""

        stream_name: str = Field(..., description="Singer stream name")
        primary_keys: list[str] = Field(..., description="Primary key field names")
        replication_method: Literal["FULL_TABLE", "INCREMENTAL"] = Field(
            default="FULL_TABLE", description="Replication method"
        )
        replication_key: str | None = Field(
            None, description="Replication key field name"
        )
        inclusion: Literal["available", "automatic", "unsupported"] = Field(
            default="available", description="Stream inclusion setting"
        )

        def to_singer_metadata(self) -> list[dict[str, Any]]:
            """Convert to Singer metadata format."""
            metadata = [
                {
                    "breadcrumb": [],
                    "metadata": {
                        "inclusion": self.inclusion,
                        "forced-replication-method": self.replication_method,
                        "table-key-properties": self.primary_keys,
                    },
                },
            ]

            if self.replication_key:
                metadata[0]["metadata"]["replication-key"] = self.replication_key

            return metadata

    class WmsStreamSchema(FlextModels.BaseConfig):
        """Schema definition for Oracle WMS streams."""

        stream_name: str = Field(..., description="Stream name")
        properties: dict[str, FlextTypes.Core.Dict] = Field(
            ..., description="Schema properties"
        )

        def to_singer_schema(self) -> dict[str, Any]:
            """Convert to Singer schema format."""
            return {
                "type": "object",
                "properties": self.properties,
            }

    class WmsCatalogStream(FlextModels.BaseConfig):
        """Complete catalog stream definition for Oracle WMS."""

        tap_stream_id: str = Field(..., description="Unique tap stream identifier")
        stream_name: str = Field(..., description="Stream name")
        stream_schema: FlextTapOracleWmsModels.WmsStreamSchema = Field(
            ..., description="Stream schema definition"
        )
        metadata: FlextTapOracleWmsModels.WmsStreamMetadata = Field(
            ..., description="Stream metadata"
        )

        def to_singer_catalog_entry(self) -> dict[str, Any]:
            """Convert to Singer catalog entry format."""
            return {
                "tap_stream_id": self.tap_stream_id,
                "stream": self.stream_name,
                "schema": self.stream_schema.to_singer_schema(),
                "metadata": self.metadata.to_singer_metadata(),
            }

    class WmsExtractionConfig(FlextModels.BaseConfig):
        """Configuration for WMS data extraction."""

        entities: list[str] = Field(
            default_factory=list, description="WMS entities to extract"
        )
        page_size: int = Field(
            default=1000,
            ge=1,
            le=1250,
            description="Records per page (Oracle WMS limit: 1250)",
        )
        start_date: str | None = Field(
            None, description="Start date for incremental extraction (ISO format)"
        )

        # Filtering configuration
        entity_filters: dict[str, dict[str, Any]] = Field(
            default_factory=dict, description="Entity-specific filters"
        )
        field_selection: dict[str, list[str]] = Field(
            default_factory=dict, description="Field selection by entity"
        )

        # Performance configuration
        concurrent_requests: int = Field(
            default=3, ge=1, le=5, description="Concurrent request limit"
        )
        batch_processing: bool = Field(
            default=True, description="Enable batch processing"
        )

    class WmsApiResponse(FlextModels.BaseModel):
        """Standardized Oracle WMS API response wrapper."""

        success: bool = Field(..., description="Response success indicator")
        data: Any | None = Field(None, description="Response data payload")
        total_count: int | None = Field(
            None, description="Total entity count (for pagination)"
        )
        page_size: int | None = Field(None, description="Current page size")
        page_number: int | None = Field(None, description="Current page number")
        has_more: bool | None = Field(None, description="More pages available")

        # Error information
        error_code: str | None = Field(None, description="Error code if failed")
        error_message: str | None = Field(None, description="Error message if failed")
        error_details: dict[str, Any] | None = Field(
            None, description="Detailed error information"
        )

        # Metadata
        timestamp: datetime = Field(
            default_factory=datetime.utcnow, description="Response timestamp"
        )
        api_version: str | None = Field(None, description="WMS API version")
        request_id: str | None = Field(None, description="Request correlation ID")
        processing_time_ms: int | None = Field(
            None, description="Server processing time"
        )

    class WmsErrorContext(FlextModels.BaseModel):
        """Error context for Oracle WMS API error handling."""

        error_type: Literal[
            "AUTHENTICATION",
            "AUTHORIZATION",
            "RATE_LIMIT",
            "TIMEOUT",
            "SERVER_ERROR",
            "NETWORK",
            "VALIDATION",
        ] = Field(..., description="Error category")
        http_status_code: int | None = Field(None, description="HTTP status code")
        retry_after_seconds: int | None = Field(
            None, description="Retry after duration"
        )

        # Context information
        endpoint: str | None = Field(None, description="WMS API endpoint that failed")
        entity_type: str | None = Field(
            None, description="WMS entity type being processed"
        )
        request_method: str | None = Field(None, description="HTTP method used")
        request_params: dict[str, Any] | None = Field(
            None, description="Request parameters"
        )

        # Recovery information
        is_retryable: bool = Field(
            default=False, description="Whether error is retryable"
        )
        suggested_action: str | None = Field(
            None, description="Suggested recovery action"
        )
        max_retry_attempts: int | None = Field(
            None, description="Maximum retry attempts for this error"
        )
        backoff_strategy: Literal["linear", "exponential", "fixed"] | None = Field(
            None, description="Recommended backoff strategy"
        )


__all__ = [
    "FlextTapOracleWmsModels",
]
