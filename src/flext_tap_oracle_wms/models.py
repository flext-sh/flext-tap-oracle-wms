"""Oracle WMS Models using standardized [Project]Models pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal, Self

from pydantic import (
    ConfigDict,
    Field,
    SecretStr,
    computed_field,
    field_serializer,
    model_validator,
)

from flext_core import FlextModels, FlextTypes


class FlextTapOracleWmsModels(FlextModels):
    """Oracle WMS tap models extending flext-core FlextModels.

    Provides comprehensive models for Oracle WMS entity extraction, authentication,
    stream configuration, and Singer protocol compliance following standardized patterns.
    """

    # Pydantic 2.11 Configuration - Enterprise Singer Oracle WMS Tap Features
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=False,
        validate_return=True,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        hide_input_in_errors=True,
        json_schema_extra={
            "title": "FLEXT Singer Oracle WMS Tap Models",
            "description": "Enterprise Oracle Warehouse Management System API extraction models with Singer protocol compliance",
            "examples": [
                {
                    "tap_name": "tap-oracle-wms",
                    "extraction_mode": "warehouse_incremental_replication",
                    "wms_instance": "https://mycompany-wms.oracle.com",
                }
            ],
            "tags": [
                "singer",
                "oracle-wms",
                "tap",
                "extraction",
                "warehouse-management",
            ],
            "version": "2.11.0",
        },
    )

    # Advanced Pydantic 2.11 Features - Singer Oracle WMS Tap Domain

    @computed_field
    @property
    def active_wms_tap_models_count(self) -> int:
        """Count of active Oracle WMS tap models with warehouse extraction capabilities."""
        count = 0
        # Count core Singer Oracle WMS tap models
        if hasattr(self, "WmsAuthenticationConfig"):
            count += 1
        if hasattr(self, "WmsItemEntity"):
            count += 1
        if hasattr(self, "WmsLocationEntity"):
            count += 1
        if hasattr(self, "WmsInventoryEntity"):
            count += 1
        if hasattr(self, "WmsOrderEntity"):
            count += 1
        if hasattr(self, "WmsShipmentEntity"):
            count += 1
        if hasattr(self, "WmsUserEntity"):
            count += 1
        if hasattr(self, "WmsStreamMetadata"):
            count += 1
        if hasattr(self, "WmsExtractionConfig"):
            count += 1
        if hasattr(self, "WmsApiResponse"):
            count += 1
        return count

    @computed_field
    @property
    def wms_tap_system_summary(self) -> dict[str, Any]:
        """Comprehensive Singer Oracle WMS tap system summary with warehouse extraction capabilities."""
        return {
            "total_models": self.active_wms_tap_models_count,
            "tap_type": "singer_oracle_wms_warehouse_extractor",
            "extraction_features": [
                "wms_item_master_extraction",
                "location_hierarchy_mapping",
                "inventory_level_tracking",
                "order_lifecycle_monitoring",
                "shipment_status_tracking",
                "user_activity_auditing",
            ],
            "singer_compliance": {
                "protocol_version": "singer_v1",
                "stream_discovery": True,
                "catalog_generation": True,
                "state_management": True,
                "incremental_bookmarking": True,
            },
            "wms_capabilities": {
                "warehouse_operations": True,
                "inventory_management": True,
                "order_processing": True,
                "location_tracking": True,
                "shipment_monitoring": True,
            },
        }

    @model_validator(mode="after")
    def validate_wms_tap_system_consistency(self) -> Self:
        """Validate Singer Oracle WMS tap system consistency and configuration."""
        # Singer WMS tap authentication validation
        if hasattr(self, "_wms_authentication") and self._wms_authentication:
            if not hasattr(self, "WmsAuthenticationConfig"):
                msg = "WmsAuthenticationConfig required when WMS authentication configured"
                raise ValueError(msg)

        # Stream configuration validation
        if hasattr(self, "_stream_configurations") and self._stream_configurations:
            if not hasattr(self, "WmsStreamMetadata"):
                msg = "WmsStreamMetadata required for stream configurations"
                raise ValueError(msg)

        # Singer protocol compliance validation
        if hasattr(self, "_singer_mode") and self._singer_mode:
            required_models = ["WmsApiResponse", "WmsErrorContext"]
            for model in required_models:
                if not hasattr(self, model):
                    msg = f"{model} required for Singer protocol compliance"
                    raise ValueError(msg)

        return self

    @field_serializer("*", when_used="json")
    def serialize_with_wms_metadata(
        self, value: Any, _info: FieldSerializationInfo
    ) -> Any:
        """Add Singer Oracle WMS tap metadata to all serialized fields."""
        if isinstance(value, dict):
            return {
                **value,
                "_wms_tap_metadata": {
                    "extraction_timestamp": datetime.now(UTC).isoformat(),
                    "tap_type": "oracle_wms_warehouse_extractor",
                    "singer_protocol": "v1.0",
                    "data_source": "oracle_warehouse_management",
                },
            }
        if isinstance(value, (str, int, float, bool)) and hasattr(
            self, "_include_wms_metadata"
        ):
            return {
                "value": value,
                "_wms_context": {
                    "extracted_at": datetime.now(UTC).isoformat(),
                    "tap_name": "flext-tap-oracle-wms",
                },
            }
        return value

    class WmsAuthenticationConfig(FlextModels.BaseConfig):
        """Oracle WMS authentication configuration."""

        # Pydantic 2.11 Configuration - Authentication Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS authentication with facility context",
                "examples": [
                    {
                        "base_url": "https://mycompany-wms.oracle.com",
                        "username": "wms_user",
                        "company_code": "COMP01",
                        "facility_code": "WH001",
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def wms_auth_summary(self) -> dict[str, Any]:
            """Oracle WMS authentication configuration summary."""
            return {
                "wms_instance": {
                    "base_url": self.base_url,
                    "domain": self.base_url.split("//")[-1].split("/")[0]
                    if "//" in self.base_url
                    else self.base_url,
                    "auth_method": self.auth_method,
                },
                "organizational_context": {
                    "company_code": self.company_code,
                    "facility_code": self.facility_code,
                    "username": self.username[:3] + "..."
                    if len(self.username) > 3
                    else self.username,
                },
                "performance_settings": {
                    "request_timeout": self.request_timeout,
                    "max_retries": self.max_retries,
                    "concurrent_requests": self.concurrent_requests,
                },
            }

        @model_validator(mode="after")
        def validate_wms_auth_config(self) -> Self:
            """Validate Oracle WMS authentication configuration."""
            if not self.base_url.startswith(("http://", "https://")):
                msg = "WMS base URL must include protocol"
                raise ValueError(msg)
            if not self.company_code:
                msg = "Company code is required"
                raise ValueError(msg)
            if not self.facility_code:
                msg = "Facility code is required"
                raise ValueError(msg)
            return self

    class WmsEntityBase(FlextModels.Entity):
        """Base model for Oracle WMS entities."""

        # Pydantic 2.11 Configuration - Entity Base Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Base Oracle WMS entity with organizational context",
                "examples": [
                    {
                        "entity_id": "ENTITY_001",
                        "company_code": "COMP01",
                        "facility_code": "WH001",
                    }
                ],
            },
        )

        entity_id: str = Field(..., description="Unique entity identifier")
        entity_name: str | None = Field(None, description="Entity display name")
        date_time_stamp: datetime | None = Field(
            None, description="WMS timestamp for replication"
        )
        company_code: str | None = Field(None, description="Associated company code")
        facility_code: str | None = Field(None, description="Associated facility code")

        @computed_field
        @property
        def wms_entity_context(self) -> dict[str, Any]:
            """Oracle WMS entity organizational context."""
            return {
                "entity_identity": {
                    "id": self.entity_id,
                    "name": self.entity_name,
                    "timestamp": self.date_time_stamp.isoformat()
                    if self.date_time_stamp
                    else None,
                },
                "organizational_context": {
                    "company_code": self.company_code,
                    "facility_code": self.facility_code,
                    "full_context": f"{self.company_code}.{self.facility_code}"
                    if self.company_code and self.facility_code
                    else None,
                },
            }

        @model_validator(mode="after")
        def validate_wms_entity_base(self) -> Self:
            """Validate Oracle WMS entity base."""
            if not self.entity_id:
                msg = "Entity ID is required"
                raise ValueError(msg)
            return self

    class WmsItemEntity(WmsEntityBase):
        """Oracle WMS Item master entity."""

        # Pydantic 2.11 Configuration - Item Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS item master with physical attributes",
                "examples": [
                    {
                        "item_id": "ITEM_001",
                        "item_desc": "Widget A",
                        "item_category": "WIDGETS",
                        "weight": 1.5,
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def item_characteristics_summary(self) -> dict[str, Any]:
            """Oracle WMS item characteristics summary."""
            return {
                "item_identity": {
                    "id": self.item_id,
                    "description": self.item_desc,
                    "category": self.item_category,
                    "type": self.item_type,
                    "status": self.item_status,
                },
                "physical_attributes": {
                    "weight": self.weight,
                    "volume": self.volume,
                    "dimensions": {
                        "length": self.length,
                        "width": self.width,
                        "height": self.height,
                    },
                    "has_dimensions": any([self.length, self.width, self.height]),
                },
                "tracking_capabilities": {
                    "lot_control": bool(self.lot_control),
                    "expiry_tracking": bool(self.expiry_date_tracking),
                    "serial_tracking": bool(self.serial_number_tracking),
                    "unit_of_measure": self.unit_of_measure,
                },
            }

        @model_validator(mode="after")
        def validate_wms_item(self) -> Self:
            """Validate Oracle WMS item entity."""
            if not self.item_id:
                msg = "Item ID is required"
                raise ValueError(msg)
            if self.weight is not None and self.weight < 0:
                msg = "Weight cannot be negative"
                raise ValueError(msg)
            return self

    class WmsLocationEntity(WmsEntityBase):
        """Oracle WMS Location entity."""

        # Pydantic 2.11 Configuration - Location Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS location with capacity and hierarchy",
                "examples": [
                    {
                        "location_id": "A01-B02-T03-P01",
                        "location_type": "PICK",
                        "zone_id": "ZONE_A",
                        "max_weight": 500.0,
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def location_hierarchy_summary(self) -> dict[str, Any]:
            """Oracle WMS location hierarchy and capacity summary."""
            return {
                "location_identity": {
                    "id": self.location_id,
                    "type": self.location_type,
                    "status": self.location_status,
                },
                "warehouse_hierarchy": {
                    "zone_id": self.zone_id,
                    "area_id": self.area_id,
                    "coordinates": {
                        "aisle": self.aisle,
                        "bay": self.bay,
                        "tier": self.tier,
                        "position": self.position,
                    },
                    "full_address": f"{self.aisle}-{self.bay}-{self.tier}-{self.position}"
                    if all([self.aisle, self.bay, self.tier, self.position])
                    else None,
                },
                "capacity_limits": {
                    "max_weight": self.max_weight,
                    "max_volume": self.max_volume,
                    "unit_capacity": self.location_capacity,
                    "has_weight_limit": bool(self.max_weight),
                    "has_volume_limit": bool(self.max_volume),
                },
            }

        @model_validator(mode="after")
        def validate_wms_location(self) -> Self:
            """Validate Oracle WMS location entity."""
            if not self.location_id:
                msg = "Location ID is required"
                raise ValueError(msg)
            if self.max_weight is not None and self.max_weight < 0:
                msg = "Max weight cannot be negative"
                raise ValueError(msg)
            return self

    class WmsInventoryEntity(WmsEntityBase):
        """Oracle WMS Inventory entity with current stock levels."""

        # Pydantic 2.11 Configuration - Inventory Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS inventory with quantity tracking",
                "examples": [
                    {
                        "item_id": "ITEM_001",
                        "location_id": "A01-B02-T03-P01",
                        "quantity_on_hand": 100.0,
                        "quantity_available": 75.0,
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def inventory_allocation_summary(self) -> dict[str, Any]:
            """Oracle WMS inventory allocation and availability summary."""
            total_qty = self.quantity_on_hand or 0.0
            allocated_qty = self.quantity_allocated or 0.0
            available_qty = self.quantity_available or 0.0

            allocation_rate = allocated_qty / total_qty if total_qty > 0 else 0.0
            availability_rate = available_qty / total_qty if total_qty > 0 else 0.0

            return {
                "inventory_identity": {
                    "item_id": self.item_id,
                    "location_id": self.location_id,
                    "lot_number": self.lot_number,
                    "lot_expiry": self.lot_expiry_date.isoformat()
                    if self.lot_expiry_date
                    else None,
                },
                "quantity_breakdown": {
                    "on_hand": self.quantity_on_hand or 0.0,
                    "allocated": self.quantity_allocated or 0.0,
                    "available": self.quantity_available or 0.0,
                    "reserved": self.quantity_reserved or 0.0,
                    "damaged": self.quantity_damaged or 0.0,
                },
                "allocation_metrics": {
                    "allocation_rate": allocation_rate,
                    "availability_rate": availability_rate,
                    "utilization_status": "high"
                    if allocation_rate > 0.8
                    else "medium"
                    if allocation_rate > 0.5
                    else "low",
                },
                "status_info": {
                    "inventory_status": self.inventory_status,
                    "is_locked": bool(self.lock_code),
                    "lock_code": self.lock_code,
                    "unit_of_measure": self.unit_of_measure,
                },
            }

        @model_validator(mode="after")
        def validate_wms_inventory(self) -> Self:
            """Validate Oracle WMS inventory entity."""
            if not self.item_id:
                msg = "Item ID is required"
                raise ValueError(msg)
            if not self.location_id:
                msg = "Location ID is required"
                raise ValueError(msg)
            if self.quantity_on_hand is not None and self.quantity_on_hand < 0:
                msg = "Quantity on hand cannot be negative"
                raise ValueError(msg)
            return self

    class WmsOrderEntity(WmsEntityBase):
        """Oracle WMS Order entity for warehouse orders."""

        # Pydantic 2.11 Configuration - Order Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS order with lifecycle tracking",
                "examples": [
                    {
                        "order_id": "ORD_001",
                        "order_type": "OUTBOUND",
                        "order_status": "RELEASED",
                        "total_lines": 5,
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def order_lifecycle_summary(self) -> dict[str, Any]:
            """Oracle WMS order lifecycle and progress summary."""
            fulfillment_progress = "unknown"
            if self.order_status:
                status_mapping = {
                    "CREATED": "0%",
                    "RELEASED": "25%",
                    "PICKING": "50%",
                    "PACKED": "75%",
                    "SHIPPED": "100%",
                }
                fulfillment_progress = status_mapping.get(self.order_status, "unknown")

            return {
                "order_identity": {
                    "id": self.order_id,
                    "type": self.order_type,
                    "status": self.order_status,
                    "priority": self.priority,
                },
                "parties": {
                    "customer_id": self.customer_id,
                    "supplier_id": self.supplier_id,
                    "carrier_id": self.carrier_id,
                    "is_outbound": self.order_type == "OUTBOUND"
                    if self.order_type
                    else None,
                },
                "timeline": {
                    "order_date": self.order_date.isoformat()
                    if self.order_date
                    else None,
                    "requested_date": self.requested_date.isoformat()
                    if self.requested_date
                    else None,
                    "shipped_date": self.shipped_date.isoformat()
                    if self.shipped_date
                    else None,
                    "fulfillment_progress": fulfillment_progress,
                },
                "volume_metrics": {
                    "total_lines": self.total_lines or 0,
                    "total_quantity": self.total_quantity or 0.0,
                    "total_weight": self.total_weight or 0.0,
                    "total_volume": self.total_volume or 0.0,
                },
            }

        @model_validator(mode="after")
        def validate_wms_order(self) -> Self:
            """Validate Oracle WMS order entity."""
            if not self.order_id:
                msg = "Order ID is required"
                raise ValueError(msg)
            if self.total_lines is not None and self.total_lines < 0:
                msg = "Total lines cannot be negative"
                raise ValueError(msg)
            return self

    class WmsShipmentEntity(WmsEntityBase):
        """Oracle WMS Shipment entity for shipment tracking."""

        # Pydantic 2.11 Configuration - Shipment Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS shipment with delivery tracking",
                "examples": [
                    {
                        "shipment_id": "SHIP_001",
                        "shipment_status": "IN_TRANSIT",
                        "carrier_id": "CARRIER_001",
                        "tracking_number": "1Z999AA1234567890",
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def shipment_tracking_summary(self) -> dict[str, Any]:
            """Oracle WMS shipment tracking and delivery summary."""
            delivery_status = "unknown"
            if self.actual_delivery:
                delivery_status = "delivered"
            elif self.shipment_status == "IN_TRANSIT":
                delivery_status = "in_transit"
            elif self.ship_date:
                delivery_status = "shipped"
            else:
                delivery_status = "preparing"

            return {
                "shipment_identity": {
                    "id": self.shipment_id,
                    "type": self.shipment_type,
                    "status": self.shipment_status,
                    "tracking_number": self.tracking_number,
                },
                "carrier_info": {
                    "carrier_id": self.carrier_id,
                    "has_tracking": bool(self.tracking_number),
                },
                "shipment_volume": {
                    "total_weight": self.total_weight or 0.0,
                    "total_volume": self.total_volume or 0.0,
                    "total_orders": self.total_orders or 0,
                },
                "delivery_timeline": {
                    "ship_date": self.ship_date.isoformat() if self.ship_date else None,
                    "estimated_delivery": self.estimated_delivery.isoformat()
                    if self.estimated_delivery
                    else None,
                    "actual_delivery": self.actual_delivery.isoformat()
                    if self.actual_delivery
                    else None,
                    "delivery_status": delivery_status,
                },
            }

        @model_validator(mode="after")
        def validate_wms_shipment(self) -> Self:
            """Validate Oracle WMS shipment entity."""
            if not self.shipment_id:
                msg = "Shipment ID is required"
                raise ValueError(msg)
            if self.total_orders is not None and self.total_orders < 0:
                msg = "Total orders cannot be negative"
                raise ValueError(msg)
            return self

    class WmsUserEntity(WmsEntityBase):
        """Oracle WMS User entity for user management."""

        # Pydantic 2.11 Configuration - User Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS user with role and activity tracking",
                "examples": [
                    {
                        "user_id": "USER_001",
                        "user_name": "warehouse_operator",
                        "user_type": "EMPLOYEE",
                        "role_id": "PICKER",
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def user_access_summary(self) -> dict[str, Any]:
            """Oracle WMS user access and activity summary."""
            full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()

            return {
                "user_identity": {
                    "id": self.user_id,
                    "username": self.user_name,
                    "full_name": full_name or None,
                    "type": self.user_type,
                    "status": self.user_status,
                },
                "contact_info": {
                    "email": self.email_address,
                    "phone": self.phone_number,
                    "has_contact_info": bool(self.email_address or self.phone_number),
                },
                "access_control": {
                    "role_id": self.role_id,
                    "permission_level": self.permission_level,
                    "default_facility": self.default_facility,
                    "has_role_assignment": bool(self.role_id),
                },
                "activity_metrics": {
                    "last_login": self.last_login_date.isoformat()
                    if self.last_login_date
                    else None,
                    "login_count": self.login_count or 0,
                    "is_active_user": bool(
                        self.last_login_date
                        and self.login_count
                        and self.login_count > 0
                    ),
                },
            }

        @model_validator(mode="after")
        def validate_wms_user(self) -> Self:
            """Validate Oracle WMS user entity."""
            if not self.user_id:
                msg = "User ID is required"
                raise ValueError(msg)
            if not self.user_name:
                msg = "User name is required"
                raise ValueError(msg)
            if self.login_count is not None and self.login_count < 0:
                msg = "Login count cannot be negative"
                raise ValueError(msg)
            return self

    class WmsStreamMetadata(FlextModels.BaseConfig):
        """Stream metadata for Oracle WMS streams."""

        # Pydantic 2.11 Configuration - Stream Metadata Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS stream metadata with Singer compliance",
                "examples": [
                    {
                        "stream_name": "items",
                        "primary_keys": ["item_id"],
                        "replication_method": "INCREMENTAL",
                        "replication_key": "date_time_stamp",
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def stream_metadata_summary(self) -> dict[str, Any]:
            """Oracle WMS stream metadata summary."""
            return {
                "stream_identity": {
                    "name": self.stream_name,
                    "primary_keys": self.primary_keys,
                    "key_count": len(self.primary_keys),
                },
                "replication_config": {
                    "method": self.replication_method,
                    "replication_key": self.replication_key,
                    "is_incremental": self.replication_method == "INCREMENTAL",
                    "inclusion": self.inclusion,
                },
            }

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

        # Pydantic 2.11 Configuration - Stream Schema Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS stream schema definition",
                "examples": [
                    {
                        "stream_name": "items",
                        "properties": {
                            "item_id": {"type": "string"},
                            "item_desc": {"type": "string"},
                        },
                    }
                ],
            },
        )

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

        # Pydantic 2.11 Configuration - Catalog Stream Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS complete catalog stream definition",
                "examples": [
                    {
                        "tap_stream_id": "items",
                        "stream_name": "items",
                        "stream_schema": {"stream_name": "items", "properties": {}},
                        "metadata": {
                            "stream_name": "items",
                            "primary_keys": ["item_id"],
                        },
                    }
                ],
            },
        )

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

        # Pydantic 2.11 Configuration - Extraction Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS extraction configuration with filtering",
                "examples": [
                    {
                        "entities": ["items", "locations", "inventory"],
                        "page_size": 1000,
                        "concurrent_requests": 3,
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def extraction_config_summary(self) -> dict[str, Any]:
            """Oracle WMS extraction configuration summary."""
            return {
                "extraction_scope": {
                    "entity_count": len(self.entities),
                    "entities": self.entities,
                    "start_date": self.start_date,
                },
                "performance_settings": {
                    "page_size": self.page_size,
                    "concurrent_requests": self.concurrent_requests,
                    "batch_processing": self.batch_processing,
                },
                "filtering": {
                    "entity_filters": len(self.entity_filters),
                    "field_selections": len(self.field_selection),
                    "has_filters": bool(self.entity_filters or self.field_selection),
                },
            }

        @model_validator(mode="after")
        def validate_extraction_config(self) -> Self:
            """Validate Oracle WMS extraction configuration."""
            if not self.entities:
                msg = "At least one entity must be specified"
                raise ValueError(msg)
            if self.page_size <= 0 or self.page_size > 1250:
                msg = "Page size must be between 1 and 1250"
                raise ValueError(msg)
            return self

    class WmsApiResponse(FlextModels.BaseModel):
        """Standardized Oracle WMS API response wrapper."""

        # Pydantic 2.11 Configuration - API Response Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS API response with pagination and performance tracking",
                "examples": [
                    {
                        "success": True,
                        "total_count": 1500,
                        "page_size": 100,
                        "page_number": 1,
                        "has_more": True,
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def wms_api_response_summary(self) -> dict[str, Any]:
            """Oracle WMS API response summary."""
            return {
                "response_status": {
                    "success": self.success,
                    "timestamp": self.timestamp.isoformat(),
                    "api_version": self.api_version,
                    "request_id": self.request_id,
                    "processing_time_ms": self.processing_time_ms,
                },
                "pagination_info": {
                    "total_count": self.total_count,
                    "page_size": self.page_size,
                    "page_number": self.page_number,
                    "has_more": self.has_more,
                    "completion_rate": (
                        (self.page_number or 1)
                        * (self.page_size or 0)
                        / (self.total_count or 1)
                        if self.total_count and self.page_size
                        else 0.0
                    ),
                },
                "error_context": {
                    "has_error": not self.success,
                    "error_code": self.error_code,
                    "error_message": self.error_message,
                    "has_details": bool(self.error_details),
                },
                "data_metrics": {
                    "has_data": self.data is not None,
                    "data_type": type(self.data).__name__
                    if self.data is not None
                    else None,
                },
            }

        @model_validator(mode="after")
        def validate_wms_api_response(self) -> Self:
            """Validate Oracle WMS API response."""
            if not self.success and not self.error_message:
                msg = "Failed responses must have an error message"
                raise ValueError(msg)
            if self.page_number is not None and self.page_number < 1:
                msg = "Page number must be positive"
                raise ValueError(msg)
            return self

    class WmsErrorContext(FlextModels.BaseModel):
        """Error context for Oracle WMS API error handling."""

        # Pydantic 2.11 Configuration - Error Context Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Oracle WMS API error context with recovery strategies",
                "examples": [
                    {
                        "error_type": "TIMEOUT",
                        "http_status_code": 408,
                        "entity_type": "items",
                        "is_retryable": True,
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def wms_error_context_summary(self) -> dict[str, Any]:
            """Oracle WMS error context summary."""
            return {
                "error_classification": {
                    "type": self.error_type,
                    "http_status": self.http_status_code,
                    "severity": self._determine_error_severity(),
                    "is_retryable": self.is_retryable,
                },
                "request_context": {
                    "endpoint": self.endpoint,
                    "entity_type": self.entity_type,
                    "method": self.request_method,
                    "has_params": bool(self.request_params),
                },
                "recovery_strategy": {
                    "suggested_action": self.suggested_action,
                    "retry_after_seconds": self.retry_after_seconds,
                    "max_retry_attempts": self.max_retry_attempts,
                    "backoff_strategy": self.backoff_strategy,
                    "auto_recoverable": self.is_retryable
                    and bool(self.retry_after_seconds),
                },
            }

        def _determine_error_severity(self) -> str:
            """Determine error severity based on type and status code."""
            if self.error_type in {"AUTHENTICATION", "AUTHORIZATION"}:
                return "critical"
            if self.error_type in {"TIMEOUT", "RATE_LIMIT"}:
                return "warning"
            if self.error_type == "SERVER_ERROR":
                return "error"
            if self.error_type in {"NETWORK", "VALIDATION"}:
                return "warning"
            return "unknown"

        @model_validator(mode="after")
        def validate_wms_error_context(self) -> Self:
            """Validate Oracle WMS error context."""
            if self.http_status_code is not None and not (
                100 <= self.http_status_code <= 599
            ):
                msg = "HTTP status code must be between 100 and 599"
                raise ValueError(msg)
            if self.retry_after_seconds is not None and self.retry_after_seconds < 0:
                msg = "Retry after seconds cannot be negative"
                raise ValueError(msg)
            return self


__all__ = [
    "FlextTapOracleWmsModels",
]
