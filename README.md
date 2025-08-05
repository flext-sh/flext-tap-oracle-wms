# FLEXT Tap Oracle WMS

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Singer SDK](https://img.shields.io/badge/singer--sdk-compliant-brightgreen.svg)](https://sdk.meltano.com/)
[![FLEXT Ecosystem](https://img.shields.io/badge/FLEXT-Enterprise%20Data%20Platform-blue.svg)](https://github.com/flext-sh/flext)

Singer-compliant tap for extracting data from Oracle Warehouse Management Systems (WMS), built as part of the FLEXT enterprise data integration platform.

## Overview

FLEXT Tap Oracle WMS provides data extraction capabilities for Oracle Warehouse Management Systems using the Singer specification. The tap supports comprehensive WMS entity extraction with authentication, pagination, and error recovery mechanisms.

### Key Features

- **Oracle WMS Integration**: Data extraction from Oracle Warehouse Management Systems
- **Singer Protocol Compliance**: Full Singer SDK implementation with catalog discovery
- **FLEXT Ecosystem Integration**: Built on flext-core patterns and flext-oracle-wms library
- **Authentication Support**: Basic Auth and OAuth2 authentication methods
- **Entity Coverage**: 15+ WMS entities including inventory, orders, shipments, and locations
- **Development Status**: Functional with 10 working streams, 37 MyPy type errors need resolution

## Quick Start

### Installation

```bash
# Development installation
git clone https://github.com/flext-sh/flext-tap-oracle-wms
cd flext-tap-oracle-wms
make setup
```

### Basic Usage

```bash
# Discover available streams
make discover

# Extract data
make run

# Validate configuration
make validate-config
```

### Minimal Configuration

```json
{
  "base_url": "https://your-wms.oraclecloud.com",
  "auth_method": "basic",
  "username": "wms_user",
  "password": "secure_password",
  "company_code": "COMPANY",
  "facility_code": "FACILITY",
  "entities": ["item", "location", "inventory"]
}
```

## Current Development Status

This project is undergoing architectural refactoring to align with Singer SDK best practices and FLEXT ecosystem standards. While fully functional, the codebase will be simplified significantly in upcoming releases.

**Development Metrics**:
- **Current Architecture**: 26 Python files, 8,179 lines of code
- **Target Architecture**: 6-8 Python files, ~800 lines of code
- **Refactoring Goal**: 90% code reduction while maintaining all functionality
- **Timeline**: Refactoring planned for completion in 6 weeks

For detailed refactoring information, see [Refactoring Plan](docs/TODO.md).

## Configuration

### Connection Settings

| Setting         | Required | Description                                 |
| --------------- | -------- | ------------------------------------------- |
| `base_url`      | Yes      | Oracle WMS instance URL                     |
| `auth_method`   | Yes      | Authentication method ("basic" or "oauth2") |
| `company_code`  | Yes      | WMS company code                            |
| `facility_code` | Yes      | WMS facility code                           |
| `username`      | Yes*     | WMS username (basic auth)                   |
| `password`      | Yes*     | WMS password (basic auth)                   |

*Required for basic authentication

### Example Configurations

```bash
# Basic configuration
examples/configs/basic.json

# Production setup
examples/configs/production.json

# Performance optimized
examples/configs/test_config_performance.json
```

See [examples/README.md](examples/README.md) for comprehensive configuration documentation.

## Available WMS Entities

### Core Entities

| Entity      | Description                    | Replication |
| ----------- | ------------------------------ | ----------- |
| `item`      | Item master data               | FULL_TABLE  |
| `location`  | Warehouse locations and zones  | FULL_TABLE  |
| `inventory` | Current inventory levels       | INCREMENTAL |
| `order`     | Outbound orders and lines      | INCREMENTAL |
| `shipment`  | Shipment tracking information  | INCREMENTAL |
| `receipt`   | Inbound receipt information    | INCREMENTAL |

### Advanced Entities

| Entity          | Description                  | Replication |
| --------------- | ---------------------------- | ----------- |
| `pick`          | Pick tasks and execution     | INCREMENTAL |
| `replenishment` | Replenishment tasks          | INCREMENTAL |
| `cycle_count`   | Cycle count tasks and results| INCREMENTAL |

## Development Commands

### Quality Gates

```bash
make validate               # Complete validation (lint + type + security + test)
make check                  # Quick health check (lint + type-check)
make test                   # Run tests with coverage reporting
make lint                   # Ruff linting with comprehensive rules
make type-check             # MyPy strict mode type checking
make security               # Security scanning with Bandit + pip-audit
```

### Singer Operations

```bash
make discover               # Generate catalog.json from WMS discovery
make run                    # Extract data using config.json and catalog.json
make validate-config        # Validate tap configuration
```

### Development Tools

```bash
make diagnose               # Project diagnostics and health check
make clean                  # Clean build artifacts and cache
make format                 # Auto-format code with Ruff
```

## FLEXT Ecosystem Integration

### Dependencies

This tap integrates with the following FLEXT ecosystem components:

- **[flext-core](../flext-core/)**: Foundation library with base patterns, logging, and result handling
- **[flext-oracle-wms](../flext-oracle-wms/)**: Oracle WMS API client and data models
- **[flext-meltano](../flext-meltano/)**: Singer/Meltano integration and orchestration
- **[flext-observability](../flext-observability/)**: Monitoring, metrics, and health checks

### Integration Example

```python
from flext_core import get_logger, FlextResult
from flext_oracle_wms import FlextOracleWmsClient
from flext_tap_oracle_wms import FlextTapOracleWMS

# Initialize tap with FLEXT patterns
config = {
    "base_url": "https://wms.example.com",
    "auth_method": "basic",
    # ... other config
}

tap = FlextTapOracleWMS(config)
streams = tap.discover_streams()
```

### Related FLEXT Projects

- **[flext-target-oracle-wms](../flext-target-oracle-wms/)**: Singer target for loading data back to WMS
- **[flext-dbt-oracle-wms](../flext-dbt-oracle-wms/)**: DBT models for WMS data transformation
- **[FlexCore](../flexcore/)**: Go runtime container for FLEXT service orchestration

## Testing

### Test Architecture

The project includes comprehensive testing with some tests currently disabled pending refactoring:

```bash
# Working tests
make test-unit              # Unit tests (working)
pytest -m unit -v          # Verbose unit tests

# Test coverage
make test                   # Tests with coverage reporting
```

See [tests/README.md](tests/README.md) for complete testing documentation and re-enabling strategy for disabled tests.

## Meltano Integration

### Basic Meltano Configuration

```yaml
# meltano.yml
extractors:
  - name: tap-oracle-wms
    variant: flext
    pip_url: flext-tap-oracle-wms
    config:
      base_url: $WMS_BASE_URL
      auth_method: basic
      username: $WMS_USERNAME
      password: $WMS_PASSWORD
      company_code: $WMS_COMPANY_CODE
      facility_code: $WMS_FACILITY_CODE
    select:
      - "item.*"
      - "inventory.*"
      - "order.*"
```

## Troubleshooting

### Common Issues

**Authentication Failures**:
- Verify WMS credentials and API access permissions
- Check company/facility codes in WMS system

**Entity Access Errors**:
- Ensure user has permissions for requested entities
- Verify WMS license includes required modules

**Schema Discovery Issues**:
- Run `make discover` to refresh catalog with latest WMS schema
- Check WMS instance availability and configuration

### Diagnostic Commands

```bash
make diagnose               # Complete project diagnostics
make doctor                 # Health check + dependency verification
```

### Debug Configuration

```json
{
  "log_level": "DEBUG",
  "request_timeout": 180,
  "max_retries": 10,
  "enable_request_logging": true
}
```

## Architecture

### Current Architecture

The project currently uses a complex architecture with 26 Python components that will be simplified during refactoring. The current structure includes multiple discovery systems, configuration approaches, and abstraction layers.

### Target Architecture (Post-Refactoring)

The refactored architecture will follow Singer SDK best practices:
- **6-8 core modules** with clear responsibilities
- **Single configuration system** using FLEXT patterns
- **Unified discovery system** leveraging flext-oracle-wms
- **Simplified stream implementation** with standard Singer patterns

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architectural documentation.

## Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/improvement`
3. Run quality gates: `make validate`
4. Commit changes: `git commit -m 'Add improvement'`
5. Push branch: `git push origin feature/improvement`
6. Create Pull Request

### Code Standards

- **Python 3.13+** with strict type hints
- **Ruff linting** with comprehensive rules enabled
- **MyPy strict mode** type checking
- **90% test coverage** minimum
- **Singer SDK compliance** for all tap functionality
- **FLEXT ecosystem patterns** for configuration and error handling

## Documentation

### Project Documentation

- **[CLAUDE.md](CLAUDE.md)**: Development guidance for Claude Code with current project status
- **[docs/TODO.md](docs/TODO.md)**: Critical issues analysis and refactoring plan
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Comprehensive architectural documentation
- **[examples/README.md](examples/README.md)**: Configuration examples and usage patterns
- **[tests/README.md](tests/README.md)**: Testing strategy and disabled test analysis

### FLEXT Ecosystem Documentation

- **[FLEXT Platform Overview](../../README.md)**: Complete ecosystem documentation
- **[flext-core Documentation](../flext-core/README.md)**: Foundation library patterns
- **[Development Standards](../../docs/standards/)**: FLEXT development guidelines

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **GitHub Issues**: [Project Issues](https://github.com/flext-sh/flext-tap-oracle-wms/issues)
- **FLEXT Documentation**: [Platform Docs](https://github.com/flext-sh/flext)
- **Singer SDK**: [Singer Documentation](https://sdk.meltano.com/)

---

**Version**: 0.9.0 | **Status**: Active Development | **FLEXT Ecosystem**: Enterprise Data Platform | **Updated**: 2025-08-04
