# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `flext-tap-oracle-wms`, a Singer tap for extracting data from Oracle Warehouse Management Systems (WMS). It uses the Singer SDK for data extraction and properly integrates with the FLEXT ecosystem.

**✅ REFACTORED STATUS**: This project has been successfully refactored from an over-engineered architecture to a clean, maintainable Singer tap implementation that properly leverages the FLEXT ecosystem.

## Current Simplified Architecture

### Clean Implementation Achieved

The project now contains **11 Python files with ~2,121 lines of code** - a properly sized Singer tap implementation:

**Core Files (clean structure)**:

- `tap_cli.py` - Main tap CLI entry point
- `tap_client.py` - Oracle WMS client integration (using flext-oracle-wms)
- `tap_config.py` - Configuration management 
- `tap_streams.py` - Singer stream implementations
- `tap_models.py` - Data models and schemas
- `utils.py` - Utility functions
- `typings.py` - Type definitions
- `tap_exceptions.py` - Project-specific exceptions

### FLEXT Ecosystem Integration

**Proper Use of FLEXT Libraries**:

- **flext-oracle-wms**: All Oracle WMS API communication via `FlextOracleWmsClient`
- **flext-core**: Base patterns, logging, result handling, domain models
- **Singer SDK**: Standard Singer protocol implementation
- **Clean Architecture**: Proper separation between Singer protocol and WMS integration

### Dependencies

The project depends on core dependencies:

- `pydantic>=2.11.7` - Data validation and settings management
- `pydantic-settings>=2.10.1` - Configuration management
- `requests>=2.31.0` - HTTP client functionality
- Plus development dependencies for testing, linting, and type checking

### Integration with FLEXT Ecosystem

This tap is designed to work within the larger FLEXT ecosystem:

- **flext-oracle-wms**: Oracle WMS API connectivity (used via client integration)
- **flext-core**: Base patterns and domain models (when available)
- **Meltano**: Data orchestration platform integration

## Development Commands

### Installation and Setup

```bash
make setup                   # Complete project setup with pre-commit hooks
make install                 # Install project dependencies only
make install-dev             # Install with development dependencies
```

### Quality Gates (Always run before committing)

```bash
make validate               # Complete validation (lint + type + security + test)
make check                  # Quick health check (lint + type-check)
make lint                   # Run ruff linting
make type-check             # Run mypy type checking with strict mode
make security               # Run bandit security scanning + pip-audit
make format                 # Auto-format code with ruff
make fix                    # Auto-fix linting issues + format
```

### Testing

```bash
make test                   # Run all tests with 90% coverage requirement
make test-unit              # Run unit tests only (exclude integration tests)
make test-integration       # Run integration tests only
make test-singer            # Run Singer-specific protocol tests
make test-fast              # Run tests without coverage (faster)
make coverage-html          # Generate HTML coverage report
```

### Singer Tap Operations

```bash
make discover               # Run tap discovery mode, generates catalog.json
make run                    # Run tap extraction with config.json and catalog.json
make validate-config        # Validate tap configuration file
make catalog                # Alias for discover
make sync                   # Alias for run
```

### Singer Tap Testing and Debugging

```bash
make wms-test               # Test Oracle WMS connectivity (via tap_client)
make diagnose               # Run project diagnostics and health checks
make doctor                 # Comprehensive health check + diagnostics
```

### Building and Distribution

```bash
make build                  # Build distribution packages
make build-clean            # Clean build artifacts and rebuild
make publish-test           # Publish to test PyPI
```

### Development Tools

```bash
make shell                  # Open Python shell with project loaded
make diagnose               # Run project diagnostics and health checks
make doctor                 # Comprehensive health check + diagnostics
make clean                  # Clean build artifacts and cache
make clean-all              # Deep clean including virtual environment
```

### Convenience Aliases

```bash
make t                      # test
make l                      # lint
make f                      # format
make tc                     # type-check
make v                      # validate
make d                      # discover
make r                      # run
make c                      # clean
```

## Configuration

### Basic Configuration Structure

The tap uses JSON configuration files. Key settings include:

**Connection Settings:**

- `base_url` - Oracle WMS instance URL
- `auth_method` - "basic" or "oauth2"
- `company_code` / `facility_code` - WMS organizational identifiers
- `username` / `password` or OAuth credentials

**Extraction Settings:**

- `entities` - List of WMS entities to extract (item, location, inventory, etc.)
- `page_size` - Records per page (max 1250)
- `start_date` - ISO8601 date for incremental extraction
- `entity_filters` - Entity-specific filtering criteria
- `field_selection` - Specific fields to extract per entity

**Examples:**

- `config.json.example` - Basic configuration template
- `examples/configs/` - Various configuration examples for different use cases

### Meltano Integration

The project includes `meltano.yml` with:

- Environment-specific configurations (dev, staging, prod)
- Comprehensive setting definitions with validation
- Example job and schedule definitions
- Metadata for replication methods (FULL_TABLE vs INCREMENTAL)

## Testing Strategy

### Test Organization

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests (some disabled in production)
- `tests/e2e/` - End-to-end tests (disabled in production)
- Test configuration in `tests/config.json`

### Test Markers

Use pytest markers to run specific test types:

```bash
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Exclude slow tests
pytest -m singer           # Singer protocol tests
```

### Coverage Requirements

- Minimum 90% code coverage enforced
- HTML reports generated in `reports/coverage/`
- XML reports for CI/CD in `reports/coverage.xml`

## Architecture Patterns

### Singer SDK Integration

- Inherits from `singer_sdk.Tap` and `singer_sdk.streams.RESTStream`
- Implements custom `WMSPaginator` for Oracle WMS HATEOAS pagination
- Uses Singer SDK typing (`singer_typing`) for schema definitions
- Supports both full table and incremental replication

### Error Handling and Validation

- Multi-layer validation: config validation, critical validation, business rules
- Custom exception hierarchy in `src/flext_tap_oracle_wms/exceptions.py`
- Comprehensive error handling for authentication, network, and API errors

### Performance Optimizations

- Response caching system with configurable TTL
- Configurable request concurrency and retry logic
- Circuit breaker patterns for resilient API interactions
- Schema flattening for complex nested WMS data structures

### Enterprise Features

- OAuth2 and Basic Authentication support
- Comprehensive configuration validation with business rules
- Environment variable loading with prefixes (`TAP_ORACLE_WMS_`)
- Structured logging with correlation IDs
- Security scanning with bandit and pip-audit

## Quality Standards

### CURRENT STATUS (2025-08-17) - COMPLETED REFACTORING

- **MyPy**: 0 errors ✅ (All type errors resolved)
- **Linting**: 0 errors ✅ (All ruff rules passing)
- **Functionality**: Working Singer tap with proper stream implementations
- **Architecture**: Clean Singer tap leveraging FLEXT ecosystem libraries

### Zero Tolerance Quality Gates ACHIEVED

- **Python 3.13** ✅ - Latest Python version with strict typing
- **MyPy Strict Mode** ✅ - 0 type errors (was 37, now completely resolved)
- **Ruff with ALL rules** ✅ - Comprehensive linting achieved
- **Clean Architecture** ✅ - Proper FLEXT ecosystem integration
- **Simplified Structure** ✅ - From 26 files to 11 clean files

### NEXT DEVELOPMENT PRIORITIES

1. **Implement comprehensive tests** - Coverage + functionality validation
2. **Add security scanning** - Complete quality pipeline with bandit + pip-audit
3. **Production validation** - Real Oracle WMS environment testing

### Code Standards

- All code uses type hints with strict mypy configuration
- Pydantic models for configuration and data validation
- Comprehensive docstrings following Google style
- Clean Architecture patterns with clear separation of concerns
- Domain-Driven Design principles for business logic organization

## Common Development Workflows

### Adding a New WMS Entity

1. Add entity configuration to `meltano.yml` settings
2. Define the entity in `tap_models.py` with proper schema
3. Add stream implementation in `tap_streams.py`
4. Update `tap_client.py` if new API endpoints are needed
5. Create comprehensive unit tests
6. Update example configurations

### Running the Tap Locally

1. Copy `config.json.example` to `config.json`
2. Configure WMS connection settings
3. Run `make discover` to generate catalog
4. Run `make sync` to extract data
5. Monitor logs for extraction progress

### Debugging Issues

1. Use `make diagnose` to check project health
2. Run `make wms-test` to verify WMS connectivity
3. Use `make test-unit` for isolated component testing
4. Check logs with increased verbosity (`log_level: DEBUG`)
5. Use configuration examples in `examples/configs/` for reference

## Integration with FLEXT Ecosystem

This tap integrates with other FLEXT components:

- **flext-core** - Provides logging, error handling, and base patterns
- **flext-observability** - Monitoring and health check capabilities
- **flext-oracle-wms** - Oracle WMS API client and data models
- **flext-meltano** - Singer/Meltano orchestration platform

The tap can be deployed as part of larger FLEXT data pipelines with corresponding targets and DBT transformations in the ecosystem.

## Key Architecture Insights

### Clean Singer Tap Implementation

This project represents a proper Singer tap implementation:

- **Singer Protocol**: Standard implementation using Singer SDK patterns
- **WMS Integration**: Uses `requests` for HTTP communication with Oracle WMS
- **Type Safety**: Comprehensive type hints with strict MyPy validation
- **Configuration**: Pydantic-based configuration management
- **Modular Design**: Clean separation of concerns across focused modules

### Testing Architecture

The project includes a comprehensive testing structure:

- **Unit Tests**: Located in `tests/unit/` for individual component testing
- **Integration Tests**: Located in `tests/integration/` for end-to-end functionality
- **E2E Tests**: Located in `tests/e2e/` for full workflow testing
- **Performance Tests**: Located in `tests/performance/` for load testing
- **Test Configuration**: Uses `tests/config.json` for test-specific settings

### Configuration Patterns

Multiple configuration approaches are supported:

- **Basic Configuration**: `config.json.example` for simple setups
- **Advanced Examples**: 20+ configuration examples in `examples/configs/` covering various scenarios
- **Meltano Integration**: Environment-specific configurations (dev, staging, prod) in `meltano.yml`
- **Environment Variables**: Supports `TAP_ORACLE_WMS_` prefixed environment variables

## Common Development Issues

### Test Configuration

When running tests, be aware that some integration and e2e tests are disabled:

- Look for files with `.DISABLED_USES_FORBIDDEN_SAMPLES.backup` extension
- These contain tests that require external WMS instances
- Use `make test-unit` for isolated testing without external dependencies

### Performance Considerations

- **Page Size Limits**: Oracle WMS has a maximum page size of 1250 records
- **Request Timeouts**: Default timeout is 120 seconds, configurable up to 600 seconds
- **Retry Logic**: Up to 10 retries with exponential backoff
- **Caching**: Response caching is available for performance optimization

### Development vs Production

The project includes different configurations for different environments:

- **Development**: Verbose logging, smaller page sizes, more retries
- **Staging**: Balanced configuration with moderate logging
- **Production**: Optimized for performance with minimal logging
