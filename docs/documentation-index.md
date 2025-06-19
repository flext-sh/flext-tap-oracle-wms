# Documentation Index

## Overview

This index provides comprehensive cross-references between tap-oracle-wms documentation and Oracle's official WMS documentation, ensuring complete coverage and alignment with Oracle standards.

## Core Documentation

### Foundation Documents

#### [README.md](README.md)

**Purpose**: Main entry point and project overview
**Oracle References**: [Oracle WMS Cloud Portal](https://docs.oracle.com/en/cloud/saas/warehouse-management/), [Oracle Logistics](https://docs.oracle.com/en/cloud/saas/logistics-cloud-suite/)

#### [Oracle WMS Official References](oracle-references.md)

**Purpose**: Complete mapping to Oracle's official documentation
**Key Features**: Version compatibility matrix, official API links, performance guidelines, integration best practices

### Technical Architecture

#### [WMS Architecture](wms-architecture.md)

**Purpose**: Oracle WMS Cloud architecture overview
**Oracle References**: [REST API Guide - Overview](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)
**Cross-references**: [API Reference](wms-api-reference.md), [Authentication Guide](wms-authentication.md), [Entity Discovery](wms-entity-discovery.md)

#### [WMS REST API Reference](wms-api-reference.md)

**Purpose**: Complete API endpoint documentation
**Oracle References**: [Entity Module](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/), [Web Service APIs](https://docs.oracle.com/en/cloud/saas/warehouse-management/24a/owmap/)

#### [Authentication Guide](wms-authentication.md)

**Purpose**: Authentication methods and security implementation
**Oracle References**: [REST API Guide - Authentication](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)

### Implementation Guides

#### [Quick Start Guide](quickstart.md)

**Purpose**: Getting started with tap-oracle-wms
**Dependencies**: [Configuration Guide](configuration.md), [Authentication Guide](wms-authentication.md)

#### [Configuration Reference](configuration.md)

**Purpose**: Complete configuration options and settings
**Oracle References**: [REST API Guide - URL Format](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)

### Data Integration

#### [Entity Discovery](wms-entity-discovery.md)

**Purpose**: Dynamic entity discovery and schema inference
**Oracle References**: [Chapter 4: Entity Module](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/), [Chapter 5: Supported Entities](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)

#### [Data Extraction Patterns](wms-data-extraction.md)

**Purpose**: Pagination, filtering, and extraction strategies including Oracle WMS 25A Data Extract for Cloud Object Store
**Oracle References**: [Chapter 3: HTTP Response](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/), [Data Extract Guide](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/data-extract1.html), [Resource Filtering](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)

#### [Performance Tuning](performance-tuning.md)

**Purpose**: Optimization strategies for large-scale data extraction
**Oracle References**: [Performance Guidelines](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)

#### [API Evolution & Versioning](wms-api-evolution.md)

**Purpose**: Oracle WMS API evolution and version compatibility
**Oracle References**: [Oracle WMS What's New](https://docs.oracle.com/en/cloud/saas/readiness/logistics/25a/wms25a/)

## Oracle Documentation Alignment

### Core Concepts Coverage

| Oracle Concept          | tap-oracle-wms Document                       | Oracle Reference                                                                                    |
| ----------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| RESTful Web Services    | [API Reference](wms-api-reference.md)         | [REST API Guide - Chapter 2](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/) |
| Entity Architecture     | [Entity Discovery](wms-entity-discovery.md)   | [Chapter 4: Entity Module](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)   |
| Authentication Methods  | [Authentication Guide](wms-authentication.md) | [Chapter 2: Authentication](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)  |
| HTTP Response Structure | [Data Extraction](wms-data-extraction.md)     | [Chapter 3: HTTP Response](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)   |
| Performance Guidelines  | [Performance Tuning](performance-tuning.md)   | [Performance Guidelines](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)     |

### Entity Coverage

| Oracle Entity Category | Documentation Coverage                      | Oracle Reference                                                                                       |
| ---------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Core Entities          | [Entity Discovery](wms-entity-discovery.md) | [Chapter 5: Supported Entities](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/) |
| Inventory Operations   | [Entity Discovery](wms-entity-discovery.md) | [Chapter 5: Inventory](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)          |
| Inbound Operations     | [Entity Discovery](wms-entity-discovery.md) | [Chapter 5: Inbound Entities](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)   |
| Outbound Operations    | [Entity Discovery](wms-entity-discovery.md) | [Chapter 5: Outbound Entities](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/)  |

## Navigation Paths by Role

### Developers

1. [README](README.md) → Overview
2. [Oracle References](oracle-references.md) → Official context
3. [Quick Start](quickstart.md) → Implementation
4. [API Reference](wms-api-reference.md) → Technical details

### System Integrators

1. [WMS Architecture](wms-architecture.md) → System design
2. [Authentication Guide](wms-authentication.md) → Security planning
3. [Configuration Guide](configuration.md) → Integration setup
4. [Oracle References](oracle-references.md) → Compliance requirements

### Data Engineers

1. [Entity Discovery](wms-entity-discovery.md) → Data model
2. [Data Extraction](wms-data-extraction.md) → Extraction patterns
3. [Performance Tuning](performance-tuning.md) → Optimization
4. [Oracle References](oracle-references.md) → Official definitions

## Maintenance Schedule

- **Monthly**: Oracle documentation link validation
- **Quarterly**: Cross-reference accuracy review
- **Per Oracle Release**: Version compatibility updates
- **As Needed**: Critical changes and updates

---

**Last Updated**: 2025-06-15
