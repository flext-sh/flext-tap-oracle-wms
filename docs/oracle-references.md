# Oracle WMS Official References and Documentation Links

## Official Oracle WMS Documentation

### Primary Documentation Sources

#### Oracle WMS Cloud 25B (Latest)

- **Main Documentation Portal**: [Oracle Fusion Cloud Warehouse Management](https://docs.oracle.com/en/cloud/saas/warehouse-management/)
- **REST API Guide**: [Oracle WMS REST API Guide 25B](https://docs.oracle.com/en/cloud/saas/warehouse-management/25b/owmre/)
- **What's New**: [Oracle Fusion Cloud Warehouse Management 25B What's New](https://docs.oracle.com/en/cloud/saas/readiness/logistics/25b/wms25b/)
- **Integration API Guide**: [WMS Web Service APIs](https://docs.oracle.com/en/cloud/saas/warehouse-management/24a/owmap/)

#### Oracle WMS Cloud 24C

- **Documentation**: [Oracle WMS Cloud 24C Documentation](https://support.oracle.com/knowledge/Oracle%20Cloud/3033874_1.html)
- **Release Notes**: Available through My Oracle Support

#### Oracle Supply Chain & Manufacturing Documentation

- **Portal**: [Oracle Supply Chain & Manufacturing 24B](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/24b/)
- **Oracle Logistics**: [Oracle Logistics Get Started](https://docs.oracle.com/en/cloud/saas/logistics-cloud-suite/)

### API Documentation

#### REST API Reference

- **Current Version**: v10 (stable across WMS versions)
- **Base URL Pattern**: `https://{instance}.wms.ocs.oraclecloud.com/{tenant}/wms/lgfapi/v10/`
- **Entity Module**: Provides access to 300+ business entities
- **Operation Module**: Specialized operations for complex workflows

#### Authentication Methods

- **Basic Authentication**: Username/password for development
- **OAuth 2.0**: Token-based authentication for production
- **Required Permissions**: `lgfapi_read_access`, `lgfapi_create_access`, `lgfapi_update_access`, `lgfapi_delete_access`

### Key Oracle WMS Concepts

#### Entity Architecture

Oracle WMS uses an entity-based architecture with the following patterns:

```
/entity/{entity_name}/           # List/Create operations
/entity/{entity_name}/{id}/      # Retrieve/Update/Delete operations
/entity/{entity_name}/describe/  # Schema metadata
/entity/{entity_name}/{operation}/ # Specialized operations
```

#### Supported Entities (300+)

Core business entities include:

- **Facility Management**: facility, company, location
- **Inventory**: inventory, allocation, cycle_count
- **Inbound Operations**: receipt, iblpn, putaway
- **Outbound Operations**: order_hdr, order_dtl, oblpn, shipment
- **Configuration**: screen_config, rule, reason_code

## Cross-Reference with tap-oracle-wms Documentation

### Architecture Alignment

| tap-oracle-wms Document                            | Oracle Official Reference                                                                          | Key Alignment Points                               |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [wms-architecture.md](wms-architecture.md)         | [Oracle WMS REST API Guide](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/) | API layering, authentication, entity model         |
| [wms-api-reference.md](wms-api-reference.md)       | [WMS Web Service APIs](https://docs.oracle.com/en/cloud/saas/warehouse-management/24a/owmap/)      | Endpoint structure, HTTP methods, response formats |
| [wms-authentication.md](wms-authentication.md)     | Chapter 2: Authentication (REST API Guide)                                                         | Basic Auth, OAuth 2.0, required headers            |
| [wms-entity-discovery.md](wms-entity-discovery.md) | Chapter 4: Entity Module                                                                           | Entity metadata, schema discovery, field types     |
| [wms-data-extraction.md](wms-data-extraction.md)   | Chapter 3: HTTP Response & Pagination                                                              | Pagination modes, filtering, field selection       |

### Configuration Mapping

| tap-oracle-wms Config | Oracle WMS Requirement | Official Reference                  |
| --------------------- | ---------------------- | ----------------------------------- |
| `base_url`            | WMS Instance URL       | REST API Guide: URL Format          |
| `username`/`password` | Basic Authentication   | Chapter 2: Login and Authentication |
| `oauth_token`         | OAuth 2.0 Token        | Chapter 2: OAuth2 Authentication    |
| `company_code`        | X-WMS-Company Header   | Required for multi-tenant access    |
| `facility_code`       | X-WMS-Facility Header  | Required for facility context       |

### Entity Stream Mapping

| Singer Stream   | Oracle WMS Entity | API Endpoint         | Official Documentation                 |
| --------------- | ----------------- | -------------------- | -------------------------------------- |
| `items`         | `item`            | `/entity/item/`      | Chapter 5: Supported Entity Operations |
| `locations`     | `location`        | `/entity/location/`  | Chapter 5: Location                    |
| `inventory`     | `inventory`       | `/entity/inventory/` | Chapter 5: Inventory                   |
| `orders`        | `order_hdr`       | `/entity/order_hdr/` | Chapter 5: Sales Order Header          |
| `order_details` | `order_dtl`       | `/entity/order_dtl/` | Chapter 5: Order Detail                |
| `receipts`      | `receipt`         | `/entity/receipt/`   | Chapter 5: Receipt                     |
| `shipments`     | `shipment`        | `/entity/shipment/`  | Chapter 5: Shipment                    |

## Oracle WMS Version Compatibility

### API Version Support Matrix

| WMS Version | API Version | Support Status | Documentation Link                                                                             |
| ----------- | ----------- | -------------- | ---------------------------------------------------------------------------------------------- |
| 25B         | v10         | Current        | [25B Documentation](https://docs.oracle.com/en/cloud/saas/warehouse-management/25b/)           |
| 24C         | v10         | Supported      | [24C Documentation](https://support.oracle.com/knowledge/Oracle%20Cloud/3033874_1.html)        |
| 24B         | v10         | Supported      | [24B Documentation](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/24b/) |
| 24A         | v10         | Supported      | [24A Documentation](https://docs.oracle.com/en/cloud/saas/warehouse-management/24a/)           |

### Version Compatibility Notes

- API v10 is stable across all supported WMS versions
- Backward compatibility maintained within major versions
- New entities and operations added in minor versions
- Deprecation notices provided 12+ months in advance

### Oracle WMS 25B New Features

#### Data Extract for Cloud Object Store

- **Feature**: REST API for extracting data to cloud object stores
- **API Endpoint**: `POST /wms/lgfapi/v10/data_extract/push_to_object_store`
- **Formats**: CSV, JSON, Parquet (10MB to 1GB file sizes)
- **Providers**: OCI Object Storage, AWS S3, Google Cloud Storage, Azure Blob
- **Filters**: `create_ts__gt`, `mod_ts__gt`, `status_id__lt`
- **tap-oracle-wms Coverage**: [Data Extraction Patterns](wms-data-extraction.md)
- **Oracle Reference**: [Data Extract Guide](https://docs.oracle.com/en/cloud/saas/warehouse-management/25a/owmre/data-extract1.html)

#### Password Life for API Authentication

- **Feature**: Password expiration policies for API users
- **Configuration**: User-level async data extract flag
- **Security**: Enhanced API authentication lifecycle management
- **Oracle Reference**: [WMS 25B What's New](https://docs.oracle.com/en/cloud/saas/readiness/logistics/25b/wms25b/25B-wms-wn-f36630.htm)

#### Custom Attribute Fields

- **Feature**: Custom attributes for Inbound LPN, Outbound LPN, and Pallet entities
- **Configuration**: Setup required before use
- **Oracle Reference**: [WMS 25B What's New](https://docs.oracle.com/en/cloud/saas/readiness/logistics/25b/wms25b/25B-wms-wn-f36617.htm)

#### Enhanced Inbound Performance Metrics

- **Feature**: Dock to Stock time measurement APIs
- **APIs**: Average dock to stock time per day, per shipment
- **Oracle Reference**: [Performance Metrics](https://docs.oracle.com/en/cloud/saas/readiness/logistics/25b/wms25b/25B-wms-wn-f36620.htm)

#### Cloud Object Store for Output Interfaces

- **Feature**: Direct output to cloud storage providers
- **Integration**: Enhanced endpoint configuration
- **Oracle Reference**: [Output Interfaces](https://docs.oracle.com/en/cloud/saas/readiness/logistics/25b/wms25b/25B-wms-wn-f36619.htm)

## Performance Guidelines from Oracle

### Pagination Recommendations

- **Default Page Size**: 20 records (user configurable: 10-125)
- **Maximum Page Size**: 1,250 records for bulk operations
- **Pagination Modes**:
  - `paged`: Standard pagination with total counts
  - `sequenced`: Cursor-based for performance (recommended for large datasets)

### Rate Limiting Guidelines

- Per-tenant rate limits apply
- Burst capacity available for peak loads
- Use cursor-based pagination for large datasets
- Implement exponential backoff for retry logic

### Field Selection Optimization

```http
GET /entity/item?fields=id,code,description&page_size=1000
```

- Reduces payload size significantly
- Improves response times
- Recommended for integration scenarios

## Error Handling Reference

### Standard HTTP Status Codes

| Status Code | Description  | Oracle Documentation Reference |
| ----------- | ------------ | ------------------------------ |
| 200         | Success      | Chapter 3: Status Codes        |
| 201         | Created      | Chapter 3: Status Codes        |
| 400         | Bad Request  | Chapter 3: Status Codes        |
| 401         | Unauthorized | Chapter 3: Status Codes        |
| 403         | Forbidden    | Chapter 3: Status Codes        |
| 404         | Not Found    | Chapter 3: Status Codes        |
| 409         | Conflict     | Chapter 3: Status Codes        |
| 500         | Server Error | Chapter 3: Status Codes        |

### Error Response Format

```json
{
  "reference": "25b414f0-7a1d-4f35-ac3c-0ec9886cf37a",
  "code": "VALIDATION_ERROR",
  "message": "Invalid input.",
  "details": {
    "reason_code": "Invalid Reason code"
  }
}
```

## Additional Oracle Resources

### Support and Community

- **My Oracle Support**: [https://support.oracle.com](https://support.oracle.com)
- **Oracle Cloud Customer Connect**: Community forums and user groups
- **Oracle University**: Training and certification programs
- **Oracle Architecture Center**: Reference architectures and best practices

### Technical Resources

- **Oracle Developer Portal**: APIs and SDKs
- **Oracle Cloud Infrastructure**: Platform documentation
- **Oracle Integration**: OIC and other integration services
- **Oracle Analytics**: Reporting and business intelligence

### Compliance and Security

- **Oracle Cloud Security**: Security architecture and compliance
- **Data Privacy**: GDPR and other privacy regulations
- **Audit and Compliance**: Audit trails and compliance reporting

## Integration Best Practices from Oracle

### Authentication Best Practices

1. Use OAuth 2.0 for production environments
2. Implement token refresh mechanisms
3. Store credentials securely (never in code)
4. Use least-privilege access principles

### Performance Optimization

1. Use cursor-based pagination for large datasets
2. Implement field selection to reduce payload
3. Cache static data (entities that rarely change)
4. Use appropriate page sizes for your use case

### Error Handling

1. Implement exponential backoff for retries
2. Log error references for support cases
3. Handle rate limiting gracefully
4. Monitor API usage patterns

### Data Quality

1. Validate data before sending to WMS
2. Use entity describe operations to understand field requirements
3. Implement proper error handling for data validation failures
4. Monitor data consistency across systems

## Related Oracle Documentation

### Integration Patterns

- **Oracle Integration Cloud (OIC)**: Pre-built WMS adapters
- **Oracle Data Integrator (ODI)**: ETL patterns for WMS
- **Oracle Analytics Cloud**: Reporting on WMS data
- **Oracle Process Automation**: Workflow integration

### Industry-Specific Guides

- **Retail**: Omni-channel fulfillment patterns
- **Manufacturing**: Supply chain integration
- **3PL**: Multi-tenant operations
- **E-commerce**: Direct-to-consumer fulfillment

---

## Document Maintenance

**Last Updated**: 2025-06-15
**Oracle WMS Version**: 25B
**API Version**: v10
**Next Review**: 2025-09-15

**Maintenance Schedule**:

- Quarterly review of Oracle documentation updates
- Annual review of version compatibility matrix
- Immediate updates for breaking changes or deprecations
