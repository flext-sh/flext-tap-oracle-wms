# Domain Components

## Overview

This directory contains domain-driven design (DDD) components for FLEXT Tap Oracle WMS, implementing core business logic and domain models separate from infrastructure concerns.

## Domain Architecture

### **Domain-Driven Design Principles**
- **Domain Models**: Core business entities and value objects
- **Domain Services**: Business logic not naturally belonging to entities
- **Domain Types**: Custom types representing business concepts
- **Ubiquitous Language**: Consistent terminology across business and technical domains

### **FLEXT Integration**
- Built on flext-core domain patterns
- Integrates with flext-oracle-wms domain models
- Uses FLEXT ecosystem ubiquitous language
- Follows Clean Architecture domain layer principles

## Components

### **[models.py](models.py)**
**Purpose**: Core domain models and business entities

**Key Components**:
- WMS business entities (Item, Location, Inventory, Order, etc.)
- Value objects for WMS concepts
- Domain aggregates with business invariants
- Entity relationships and domain rules

**Usage**:
```python
from flext_tap_oracle_wms.domain.models import WMSItem, InventoryLevel

item = WMSItem(
    item_id="ITEM001",
    description="Sample Item",
    category="FINISHED_GOOD"
)

inventory = InventoryLevel(
    item=item,
    location_id="LOC001", 
    quantity=100
)
```

### **[types.py](types.py)**
**Purpose**: Domain-specific types and type definitions

**Key Components**:
- WMS business concept types (CompanyCode, FacilityCode, etc.)
- Custom type aliases for domain clarity
- Type constraints and validation
- Business rule type definitions

**Usage**:
```python
from flext_tap_oracle_wms.domain.types import CompanyCode, FacilityCode, EntityName

company = CompanyCode("ACME")
facility = FacilityCode("DC01")
entity = EntityName("inventory")
```

## Domain Concepts

### **WMS Business Entities**

#### **Core Entities**
- **Item**: Product master data with SKU, description, and attributes
- **Location**: Warehouse locations, zones, and storage definitions
- **Inventory**: Current stock levels and availability
- **Order**: Outbound order management and fulfillment
- **Shipment**: Shipping and delivery tracking
- **Receipt**: Inbound receiving and putaway

#### **Operational Entities**
- **Pick**: Pick task execution and wave management
- **Replenishment**: Stock replenishment and optimization
- **CycleCount**: Inventory counting and accuracy management

### **Value Objects**
- **Quantity**: Inventory quantities with units of measure
- **Status**: Entity status with business rules
- **Timestamp**: WMS-specific datetime handling
- **Coordinates**: Warehouse location positioning

### **Business Rules**
- Inventory quantity cannot be negative
- Orders must have valid customer and facility
- Shipments require valid tracking information
- Locations must be within valid facility boundaries

## Architecture Integration

### **Clean Architecture Positioning**
```
┌─────────────────────────────────────┐
│           Presentation              │  <- CLI, Streams
├─────────────────────────────────────┤
│           Application               │  <- Tap, Discovery
├─────────────────────────────────────┤
│             Domain                  │  <- THIS MODULE
├─────────────────────────────────────┤
│          Infrastructure             │  <- Client, Auth
└─────────────────────────────────────┘
```

### **Dependency Direction**
- **Inward Dependencies Only**: Domain depends on nothing external
- **Interface Segregation**: Domain defines interfaces for external needs
- **Dependency Inversion**: Infrastructure implements domain interfaces

### **FLEXT Ecosystem Alignment**
- Uses flext-core domain patterns and base classes
- Integrates with flext-oracle-wms domain models
- Follows FLEXT ubiquitous language conventions
- Implements flext-observability domain events

## Development Guidelines

### **Domain Model Design**
- **Rich Domain Models**: Business logic in domain entities
- **Immutable Value Objects**: Immutable types for business concepts
- **Aggregate Boundaries**: Clear aggregate roots and consistency boundaries
- **Business Invariants**: Domain rules enforced within aggregates

### **Type Safety**
- **Strict Typing**: All domain types have comprehensive type hints
- **Custom Types**: Use domain-specific types instead of primitives
- **Type Validation**: Runtime validation of domain constraints
- **MyPy Compliance**: Full MyPy strict mode compatibility

### **Testing Strategy**
- **Domain Unit Tests**: Test business logic in isolation
- **Invariant Testing**: Verify business rules are enforced
- **Value Object Testing**: Test immutability and equality
- **Aggregate Testing**: Test aggregate consistency

## Business Logic Examples

### **Item Management**
```python
# Business rule: Items must have valid categories
item = WMSItem(
    item_id="ITEM001",
    description="Sample Item",
    category=ItemCategory.FINISHED_GOOD,  # Enforced enum
    status=ItemStatus.ACTIVE
)

# Business rule: Cannot change item ID after creation
# item.item_id = "DIFFERENT"  # Raises domain exception
```

### **Inventory Operations**
```python
# Business rule: Inventory cannot go negative
inventory = InventoryLevel(item_id="ITEM001", location_id="LOC001", quantity=100)

# This would raise a domain exception
# inventory.reduce_quantity(150)  # Cannot reduce below zero

# Valid operation
inventory.reduce_quantity(50)  # Results in quantity=50
```

### **Order Processing**
```python
# Business rule: Orders require valid company/facility
order = WMSOrder(
    order_id="ORD001",
    company_code=CompanyCode("ACME"),
    facility_code=FacilityCode("DC01"),
    customer_id="CUST001"
)

# Business rule: Cannot ship without allocation
# order.ship()  # Raises exception if not allocated
order.allocate()  # Allocate inventory first
order.ship()     # Now valid
```

## Performance Considerations

### **Domain Object Creation**
- Use factory methods for complex domain object creation
- Cache frequently used value objects
- Minimize object creation in hot paths
- Consider lazy loading for large aggregates

### **Business Rule Validation**
- Validate at aggregate boundaries
- Use fail-fast validation for critical rules
- Cache validation results when appropriate
- Batch validation for bulk operations

## Refactoring Notes

### **Current Issues**
- Some domain logic scattered across infrastructure layers
- Business rules not consistently enforced in domain
- Value objects could be more immutable
- Missing some aggregate boundaries

### **Improvement Opportunities**
- Consolidate business logic into domain layer
- Strengthen aggregate boundaries and invariants
- Implement domain events for business state changes
- Add more comprehensive business rule validation

---

**Status**: Core domain patterns established | **Priority**: Consolidate business logic | **Updated**: 2025-08-04