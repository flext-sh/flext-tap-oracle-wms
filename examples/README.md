# Configuration Examples

<!-- TOC START -->

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
  - [Basic Configuration Format](#basic-configuration-format)
- [Available Configuration Examples](#available-configuration-examples)
  - [Basic Configurations](#basic-configurations)
  - [Authentication Examples](#authentication-examples)
  - [Entity Configuration Examples](#entity-configuration-examples)
- [Specialized Configuration Examples](#specialized-configuration-examples)
  - [Performance-Oriented Configuration](#performance-oriented-configuration)
  - [Filtering and Selection Examples](#filtering-and-selection-examples)
  - [Date-Based Configuration Examples](#date-based-configuration-examples)
- [Environment-Specific Configurations](#environment-specific-configurations)
  - [Development Environment](#development-environment)
  - [Staging Environment](#staging-environment)
  - [Production Environment](#production-environment)
- [Configuration Usage Patterns](#configuration-usage-patterns)
  - [Local Development](#local-development)
  - [Meltano Integration](#meltano-integration)
  - [Environment Variables](#environment-variables)
- [Configuration Validation](#configuration-validation)
  - [Required Fields](#required-fields)
  - [Authentication Requirements](#authentication-requirements)
  - [Optional Settings](#optional-settings)
- [Troubleshooting Configurations](#troubleshooting-configurations)
  - [Common Configuration Issues](#common-configuration-issues)
  - [Debug Configuration](#debug-configuration)
- [Best Practices](#best-practices)
  - [Configuration Security](#configuration-security)
  - [Performance Optimization](#performance-optimization)
  - [Monitoring and Logging](#monitoring-and-logging)
- [Configuration Examples by Use Case](#configuration-examples-by-use-case)
  - [Data Warehouse Integration](#data-warehouse-integration)
  - [Real-time Inventory Monitoring](#real-time-inventory-monitoring)
  - [Compliance Reporting](#compliance-reporting)

<!-- TOC END -->

## Overview

This directory contains comprehensive configuration examples for FLEXT Tap Oracle WMS, demonstrating various use cases from basic setups to complex production environments.

## Configuration Structure

All configuration examples follow the JSON format required by Singer taps and include validation for Oracle WMS-specific settings.

### Basic Configuration Format

```json
{
  "base_url": "https://your-wms-instance.com",
  "auth_method": "basic|oauth2",
  "company_code": "YOUR_COMPANY",
  "facility_code": "YOUR_FACILITY",
  "entities": ["item", "location", "inventory"],
  "page_size": 1000,
  "start_date": "2024-01-01T00:00:00Z"
}
```

## Available Configuration Examples

### Basic Configurations

#### [basic.JSON](configs/basic.json)

**Use Case**: Getting started with minimal configuration
**Features**:

- Basic authentication
- Core entities only (item, inventory)
- Small page size for testing
- Full table replication

```bash
# Test basic configuration
tap-oracle-wms --config examples/configs/basic.json --discover
```

#### [production.JSON](configs/production.json)

**Use Case**: Production environment setup
**Features**:

- OAuth2 authentication
- Complete entity set
- Optimized page sizes
- Incremental replication
- Performance optimizations

```bash
# Production discovery
tap-oracle-wms --config examples/configs/production.json --discover > catalog.json
```

### Authentication Examples

#### Basic Authentication

```json
{
  "base_url": "https://wms.company.com",
  "auth_method": "basic",
  "username": "${WMS_USERNAME}",
  "password": "${WMS_PASSWORD}",
  "company_code": "ACME",
  "facility_code": "DC01"
}
```

#### OAuth2 Authentication

```json
{
  "base_url": "https://wms.company.com",
  "auth_method": "oauth2",
  "oauth_client_id": "${WMS_CLIENT_ID}",
  "oauth_client_secret": "${WMS_CLIENT_SECRET}",
  "oauth_token_url": "https://auth.company.com/oauth2/token",
  "company_code": "ACME",
  "facility_code": "DC01"
}
```

### Entity Configuration Examples

#### Core Entities (Minimal)

```json
{
  "entities": ["item", "location", "inventory"]
}
```

#### Complete Entity Set (Full WMS)

```json
{
  "entities": [
    "item",
    "location",
    "inventory",
    "order",
    "shipment",
    "receipt",
    "pick",
    "replenishment",
    "cycle_count"
  ]
}
```

#### Filtered Entities (Specific Use Case)

```json
{
  "entities": ["inventory", "order", "shipment"],
  "entity_filters": {
    "inventory": {
      "status": "active",
      "quantity__gt": 0
    },
    "order": {
      "order_status__in": ["allocated", "picked", "shipped"]
    }
  }
}
```

## Specialized Configuration Examples

### Performance-Oriented Configuration

#### [test_config_performance.JSON](configs/test_config_performance.json)

**Use Case**: High-volume data extraction
**Features**:

- Maximum page size (1250)
- Multiple entities
- Optimized request settings
- Connection pooling configuration

```json
{
  "page_size": 1250,
  "request_timeout": 300,
  "max_retries": 5,
  "enable_caching": true,
  "cache_ttl": 300,
  "request_concurrency": 3
}
```

### Filtering and Selection Examples

#### [test_config_filters_advanced.JSON](configs/test_config_filters_advanced.json)

**Use Case**: Complex data filtering scenarios
**Features**:

- Advanced entity filtering
- Field selection
- Date range filtering
- Status-based filtering

```json
{
  "entity_filters": {
    "item": {
      "item_status": "ACTIVE",
      "category__in": ["FINISHED_GOOD", "RAW_MATERIAL"]
    },
    "inventory": {
      "quantity__gt": 0,
      "last_updated__gte": "2024-01-01T00:00:00Z"
    }
  },
  "field_selection": {
    "item": ["item_id", "item_desc", "category", "status"],
    "inventory": ["item_id", "location_id", "quantity", "last_updated"]
  }
}
```

### Date-Based Configuration Examples

#### [test_config_simple_dates_yesterday.JSON](configs/test_config_simple_dates_yesterday.json)

**Use Case**: Daily incremental extraction

```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "entities": ["inventory", "order", "shipment"],
  "replication_method": "INCREMENTAL"
}
```

#### [test_config_simple_dates_today_7d.JSON](configs/test_config_simple_dates_today_7d.json)

**Use Case**: Weekly incremental extraction

```json
{
  "start_date": "2024-01-01T00:00:00Z",
  "entities": ["order", "shipment", "receipt"],
  "incremental_window_days": 7
}
```

## Environment-Specific Configurations

### Development Environment

```json
{
  "base_url": "https://dev-wms.company.com",
  "log_level": "DEBUG",
  "page_size": 100,
  "max_pages_per_stream": 10,
  "enable_request_logging": true,
  "cache_debug": true
}
```

### Staging Environment

```json
{
  "base_url": "https://staging-wms.company.com",
  "log_level": "INFO",
  "page_size": 500,
  "retry_limit": 5,
  "request_timeout": 180
}
```

### Production Environment

```json
{
  "base_url": "https://prod-wms.company.com",
  "log_level": "WARNING",
  "page_size": 1250,
  "pagination_mode": "cursor",
  "retry_limit": 10,
  "request_concurrency": 5,
  "enable_metrics": true
}
```

## Configuration Usage Patterns

### Local Development

```bash
# Copy example configuration
cp examples/configs/basic.json config.json

# Edit with your WMS details
vim config.json

# Test configuration
make validate-config

# Run discovery
make discover

# Extract data
make run
```

### Meltano Integration

```yaml
# meltano.yml
extractors:
  - name: tap-oracle-wms
    variant: flext
    config:
      base_url: $WMS_BASE_URL
      auth_method: oauth2
      oauth_client_id: $WMS_CLIENT_ID
      oauth_client_secret: $WMS_CLIENT_SECRET
      company_code: $WMS_COMPANY_CODE
      facility_code: $WMS_FACILITY_CODE
    select:
      - "item.*"
      - "inventory.item_id"
      - "inventory.location_id"
      - "inventory.quantity"
```

### Environment Variables

```bash
# Set environment variables for sensitive data
export TAP_ORACLE_WMS_BASE_URL="https://wms.company.com"
export TAP_ORACLE_WMS_USERNAME="integration_user"
export TAP_ORACLE_WMS_PASSWORD="secure_password"
export TAP_ORACLE_WMS_COMPANY_CODE="ACME"
export TAP_ORACLE_WMS_FACILITY_CODE="DC01"

# Use in configuration
{
  "base_url": "${TAP_ORACLE_WMS_BASE_URL}",
  "username": "${TAP_ORACLE_WMS_USERNAME}",
  "password": "${TAP_ORACLE_WMS_PASSWORD}"
}
```

## Configuration Validation

### Required Fields

All configurations must include:

- `base_url`: Oracle WMS instance URL
- `auth_method`: Authentication method ("basic" or "oauth2")
- `company_code`: WMS company identifier
- `facility_code`: WMS facility identifier

### Authentication Requirements

**Basic Auth**:

- `username`: WMS username
- `password`: WMS password

**OAuth2**:

- `oauth_client_id`: OAuth2 client ID
- `oauth_client_secret`: OAuth2 client secret
- `oauth_token_url`: Token endpoint URL (optional, will be derived)

### Optional Settings

| Setting           | Default                 | Description                           |
| ----------------- | ----------------------- | ------------------------------------- |
| `entities`        | `["item", "inventory"]` | List of entities to extract           |
| `page_size`       | `1000`                  | Records per page (max 1250)           |
| `start_date`      | `null`                  | Start date for incremental extraction |
| `request_timeout` | `120`                   | Request timeout in seconds            |
| `max_retries`     | `3`                     | Maximum retry attempts                |
| `log_level`       | `"INFO"`                | Logging level                         |

## Troubleshooting Configurations

### Common Configuration Issues

#### Authentication Failures

```json
// Problem: Invalid credentials
{
  "auth_method": "basic",
  "username": "wrong_user",
  "password": "wrong_pass"
}

// Solution: Verify credentials with WMS REDACTED_LDAP_BIND_PASSWORDistrator
{
  "auth_method": "basic",
  "username": "correct_user",
  "password": "correct_pass"
}
```

#### Entity Access Errors

```json
// Problem: Requesting unavailable entities
{
  "entities": ["nonexistent_entity"]
}

// Solution: Use discovery to check available entities
tap-oracle-wms --config config.json --discover
```

#### Page Size Issues

```json
// Problem: Page size too large
{
  "page_size": 5000  // Oracle WMS max is 1250
}

// Solution: Use maximum allowed page size
{
  "page_size": 1250
}
```

### Debug Configuration

```json
{
  "log_level": "DEBUG",
  "enable_request_logging": true,
  "enable_response_logging": true,
  "request_timeout": 300,
  "max_retries": 1
}
```

## Best Practices

### Configuration Security

- **Never commit credentials** to version control
- **Use environment variables** for sensitive data
- **Use OAuth2** when available for better security
- **Rotate credentials** regularly

### Performance Optimization

- **Start with smaller page sizes** for testing
- **Increase page size gradually** up to 1250 maximum
- **Use incremental replication** for large datasets
- **Filter entities** to reduce unnecessary data transfer

### Monitoring and Logging

- **Use appropriate log levels** for each environment
- **Enable metrics** in production
- **Monitor extraction performance** and adjust page sizes
- **Set reasonable timeouts** based on network conditions

## Configuration Examples by Use Case

### Data Warehouse Integration

```json
{
  "entities": ["item", "location", "inventory", "order", "shipment"],
  "start_date": "2024-01-01T00:00:00Z",
  "page_size": 1250,
  "enable_caching": false,
  "replication_method": "INCREMENTAL"
}
```

### Real-time Inventory Monitoring

```json
{
  "entities": ["inventory"],
  "page_size": 1000,
  "polling_interval": 300,
  "entity_filters": {
    "inventory": {
      "last_updated__gte": "NOW - INTERVAL 1 HOUR"
    }
  }
}
```

### Compliance Reporting

```json
{
  "entities": ["order", "shipment", "receipt", "cycle_count"],
  "start_date": "2024-01-01T00:00:00Z",
  "page_size": 500,
  "field_selection": {
    "order": ["order_id", "customer_id", "order_date", "status"],
    "shipment": ["shipment_id", "order_id", "ship_date", "tracking_number"]
  }
}
```

---

**Updated**: 2025-08-13
**Status**: Configuration examples available for all common use cases · 1.0.0 Release Preparation
**Next**: Review and test configurations with actual WMS instances
