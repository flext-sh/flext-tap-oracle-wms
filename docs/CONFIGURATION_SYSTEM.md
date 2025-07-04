# Oracle WMS Tap - Configuration System Documentation

## Overview

The Oracle WMS tap now uses a comprehensive **ConfigMapper system** that transforms all hardcoded specifications into configurable parameters. This system provides flexibility, company-specific configurations, and environment-based overrides.

## Configuration Hierarchy

The system follows a clear precedence order (highest to lowest):

1. **Environment Variables** (`WMS_*` variables)
2. **Configuration Profiles** (`WMS_PROFILE_NAME` setting)
3. **ConfigMapper Defaults** (sensible fallback values)

## Key Components

### 1. ConfigMapper (`config_mapper.py`)

Central component that externalizes all hardcoded values:

```python
from tap_oracle_wms.config_mapper import ConfigMapper

mapper = ConfigMapper()
api_version = mapper.get_api_version()  # Instead of hardcoded "v10"
page_size = mapper.get_page_size()      # Instead of hardcoded 100
oauth_scope = mapper.get_oauth_scope()  # Instead of hardcoded URL
```

#### Major Categories Externalized:

- **API Configuration**: versions, endpoints, authentication
- **Performance Settings**: page sizes, timeouts, retries
- **Business Logic**: replication keys, status mappings
- **Entity Configuration**: primary keys, enabled entities
- **Company Settings**: timezones, currencies, codes

### 2. Configuration Profiles (`config_profiles.py`)

Company-specific JSON configurations:

```json
{
  "company_name": "client-b",
  "company_code": "GNOS",
  "environment": "production",
  "domain": "client-b.com.br",
  "business_rules": {
    "company_timezone": "America/Sao_Paulo",
    "currency_code": "BRL",
    "allocation_status_mapping": {
      "ALLOCATED": "Active",
      "PICKED": "Fulfilled"
    }
  },
  "performance": {
    "page_size": 2000,
    "request_timeout": 180
  }
}
```

### 3. Configuration Validation (`config_validator.py`)

Validates all configuration values to ensure proper Oracle WMS integration:

```python
from tap_oracle_wms.config_validator import validate_config_with_mapper

# Automatically validates during tap initialization
validate_config_with_mapper(config_mapper)
```

#### Validation Categories:

- **Connection Settings**: URLs, authentication credentials
- **API Settings**: versions, endpoints, page modes
- **Performance Settings**: timeouts, page sizes, retries
- **Business Logic**: replication keys, entity configurations
- **Data Types**: ensures proper types and ranges

## Usage Examples

### Basic Setup

1. **Set Profile**:
   ```bash
   export WMS_PROFILE_NAME=client-b
   ```

2. **Core Connection**:
   ```bash
   export TAP_ORACLE_WMS_BASE_URL=https://wms.client-b.com
   export TAP_ORACLE_WMS_USERNAME=api_user
   export TAP_ORACLE_WMS_PASSWORD=secure_password
   ```

3. **Run Tap**:
   ```bash
   tap-oracle-wms --config config.json --discover
   ```

### Environment Overrides

Override profile settings with environment variables:

```bash
# Override page size from profile
export WMS_PAGE_SIZE=5000

# Override company timezone
export WMS_COMPANY_TIMEZONE=America/New_York

# Override API version
export WMS_API_VERSION=v11
```

### Meltano Integration

Simplified `meltano.yml` with ConfigMapper:

```yaml
plugins:
  extractors:
  - name: tap-oracle-wms-full
    config:
      # Only core connection settings needed
      base_url: $TAP_ORACLE_WMS_BASE_URL
      username: $TAP_ORACLE_WMS_USERNAME
      password: $TAP_ORACLE_WMS_PASSWORD
      entities: ["allocation", "order_hdr", "order_dtl"]
      force_full_table: true
    settings:
      # All other configs come from profile system
      WMS_PROFILE_NAME: $WMS_PROFILE_NAME
```

## Configuration Reference

### Environment Variables

#### Core Connection
- `TAP_ORACLE_WMS_BASE_URL` - WMS server URL
- `TAP_ORACLE_WMS_USERNAME` - API username
- `TAP_ORACLE_WMS_PASSWORD` - API password

#### Profile System
- `WMS_PROFILE_NAME` - Company profile to load

#### API Configuration
- `WMS_API_VERSION` - API version (default: "v10")
- `WMS_ENDPOINT_PREFIX` - API endpoint prefix (default: "/wms/lgfapi")
- `WMS_PAGE_MODE` - Pagination mode (default: "sequenced")
- `WMS_AUTH_METHOD` - Authentication method (default: "basic")

#### Performance Settings
- `WMS_PAGE_SIZE` - Records per page (default: 1000)
- `WMS_MAX_PAGE_SIZE` - Maximum page size (default: 5000)
- `WMS_REQUEST_TIMEOUT` - Request timeout seconds (default: 120)
- `WMS_MAX_RETRIES` - Maximum retry attempts (default: 3)
- `WMS_CACHE_TTL_SECONDS` - Cache TTL (default: 3600)

#### Business Logic
- `WMS_REPLICATION_KEY` - Default replication key (default: "mod_ts")
- `WMS_INCREMENTAL_OVERLAP_MINUTES` - Overlap for incremental sync (default: 5)
- `WMS_LOOKBACK_MINUTES` - Lookback for initial state (default: 5)
- `WMS_COMPANY_CODE` - WMS company code (default: "*")
- `WMS_FACILITY_CODE` - WMS facility code (default: "*")

#### Entity Configuration
- `WMS_ENTITIES` - Comma-separated entity list
- `WMS_ENTITY_{ENTITY}_PRIMARY_KEYS` - Primary keys for specific entity

#### Company Settings
- `WMS_COMPANY_TIMEZONE` - Company timezone (default: "UTC")
- `WMS_CURRENCY_CODE` - Currency code (default: "USD")
- `WMS_FISCAL_YEAR_START_MONTH` - Fiscal year start (default: 1)

#### Authentication (OAuth2)
- `WMS_OAUTH_SCOPE` - OAuth2 scope
- `WMS_OAUTH_CLIENT_ID` - OAuth2 client ID
- `WMS_OAUTH_CLIENT_SECRET` - OAuth2 client secret
- `WMS_OAUTH_TOKEN_URL` - OAuth2 token endpoint

#### Status Mappings (JSON format)
- `WMS_ALLOCATION_STATUS_MAPPING_JSON` - Allocation status mapping
- `WMS_ORDER_STATUS_MAPPING_JSON` - Order status mapping

#### Custom Headers
- `WMS_USER_AGENT` - Custom user agent
- `WMS_CUSTOM_HEADERS_JSON` - Additional headers (JSON format)

## Migration Guide

### From Hardcoded to ConfigMapper

**Before (Hardcoded)**:
```python
# streams.py
params = {
    "page_size": self.config.get("page_size", 100),  # Fixed default
    "page_mode": "sequenced",  # Always hardcoded
}

# auth.py
oauth_scope = "https://instance.wms.ocs.oraclecloud.com:443/..."  # Fixed
```

**After (ConfigMapper)**:
```python
# streams.py
params = {
    "page_size": self.config_mapper.get_page_size(),      # From profile/env/default
    "page_mode": self.config_mapper.get_pagination_mode(), # Configurable
}

# auth.py
oauth_scope = config_mapper.get_oauth_scope()  # Company-specific
```

### Meltano Configuration Migration

**Before (Explicit Configuration)**:
```yaml
config:
  base_url: $TAP_ORACLE_WMS_BASE_URL
  username: $TAP_ORACLE_WMS_USERNAME
  password: $TAP_ORACLE_WMS_PASSWORD
  wms_api_version: $WMS_API_VERSION
  page_mode: $WMS_PAGE_MODE
  page_size: $WMS_PAGE_SIZE
  request_timeout: $WMS_REQUEST_TIMEOUT
  # ... 20+ more explicit configurations
```

**After (Profile-Based)**:
```yaml
config:
  # Only core connection settings
  base_url: $TAP_ORACLE_WMS_BASE_URL
  username: $TAP_ORACLE_WMS_USERNAME
  password: $TAP_ORACLE_WMS_PASSWORD
  entities: ["allocation", "order_hdr", "order_dtl"]
  force_full_table: true
settings:
  # All other configs from profile system
  WMS_PROFILE_NAME: $WMS_PROFILE_NAME
```

## Benefits

### 1. **Elimination of Hardcoded Values**
- No more fixed API versions, endpoints, or timeouts in code
- All specifications now configurable

### 2. **Company-Specific Configurations**
- JSON profiles for different companies (client-b, Company A, etc.)
- Business rules specific to each organization

### 3. **Environment Flexibility**
- Development, staging, production configurations
- Easy overrides via environment variables

### 4. **Simplified Maintenance**
- Changes to configurations don't require code changes
- Simplified `meltano.yml` files

### 5. **Validation and Safety**
- Comprehensive configuration validation
- Clear error messages for invalid settings

## Troubleshooting

### Common Issues

1. **Profile Not Found**:
   ```
   Failed to load profile 'company_x': Profile file not found
   ```
   - Ensure profile exists in `config/profiles/company_x.json`
   - Check `WMS_PROFILE_NAME` environment variable

2. **Configuration Validation Errors**:
   ```
   Configuration validation failed: base_url is not a valid URL
   ```
   - Check environment variables for proper values
   - Refer to validation error messages for specific fixes

3. **Missing Environment Variables**:
   ```
   username is required for basic authentication
   ```
   - Ensure required variables are set in `.env` file
   - Check variable names match exactly

### Debug Mode

Enable debug logging to see configuration resolution:

```bash
export LOG_LEVEL=DEBUG
tap-oracle-wms --config config.json --discover
```

## Advanced Usage

### Custom Profiles

Create custom profiles for different environments:

```json
// config/profiles/development.json
{
  "company_name": "Development",
  "environment": "dev",
  "performance": {
    "page_size": 100,
    "request_timeout": 30
  },
  "business_rules": {
    "company_timezone": "UTC"
  }
}
```

### Profile Inheritance

Profiles can extend base configurations:

```json
// config/profiles/client-b-prod.json
{
  "extends": "client-b",
  "environment": "production",
  "performance": {
    "page_size": 5000,
    "request_timeout": 300
  }
}
```

### Dynamic Configuration

Generate configurations programmatically:

```python
from tap_oracle_wms.config_mapper import ConfigMapper
from tap_oracle_wms.config_profiles import ConfigProfileManager

# Load profile
manager = ConfigProfileManager()
profile = manager.load_profile("client-b")

# Create mapper with profile
mapper = ConfigMapper(profile.to_singer_config())

# Get all resolved configuration
config = mapper.get_all_config()
print(f"Resolved page size: {config['page_size']}")
```

## Files and Structure

```
flext-tap-oracle-wms/
├── src/tap_oracle_wms/
│   ├── config_mapper.py          # Core configuration mapping
│   ├── config_profiles.py        # Profile management
│   ├── config_validator.py       # Configuration validation
│   ├── tap.py                    # Main tap with validation
│   ├── streams.py                # Updated to use ConfigMapper
│   └── auth.py                   # Updated authentication
├── config/profiles/
│   ├── client-b.json             # client-b profile
│   └── company_a.json            # Template profile
├── templates/
│   ├── meltano.yml.template      # Generic meltano template
│   └── .env.template             # Environment variables template
└── docs/
    └── CONFIGURATION_SYSTEM.md   # This documentation
```

## Support

For issues with the configuration system:

1. Check this documentation first
2. Verify environment variables are properly set
3. Test with debug logging enabled
4. Review validation error messages
5. Check profile JSON syntax

The ConfigMapper system provides a robust, flexible foundation for Oracle WMS tap configuration that scales from development to enterprise production environments.
