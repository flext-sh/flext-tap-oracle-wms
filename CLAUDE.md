# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `flext-tap-oracle-wms`, a Singer tap for extracting data from Oracle Warehouse Management Systems (WMS). It's part of the FLEXT ecosystem and uses the Singer SDK for data extraction. The project follows Clean Architecture principles and implements enterprise-grade patterns with zero tolerance quality standards.

## Architecture

### Core Components

**Singer Tap Implementation:**

- `src/flext_tap_oracle_wms/tap.py` - Main tap class inheriting from Singer SDK's `Tap`
- `src/flext_tap_oracle_wms/streams.py` - Stream definitions using `RESTStream` with WMS-specific pagination
- `src/flext_tap_oracle_wms/client.py` - HTTP client with Oracle WMS API integration
- `src/flext_tap_oracle_wms/auth.py` - Authentication handling (Basic Auth and OAuth2)

**Configuration and Discovery:**

- `src/flext_tap_oracle_wms/config.py` - Configuration models using Pydantic
- `src/flext_tap_oracle_wms/config_mapper.py` - Maps config to internal models
- `src/flext_tap_oracle_wms/config_validator.py` - Validates configuration with business rules
- `src/flext_tap_oracle_wms/discovery.py` - Entity discovery and schema generation
- `src/flext_tap_oracle_wms/entity_discovery.py` - WMS entity discovery logic

**Schema and Type Handling:**

- `src/flext_tap_oracle_wms/schema_generator.py` - Generates Singer schemas from WMS metadata
- `src/flext_tap_oracle_wms/schema_flattener.py` - Flattens nested WMS data structures
- `src/flext_tap_oracle_wms/type_mapping.py` - Maps WMS data types to Singer types

**Specialized Features:**

- `src/flext_tap_oracle_wms/cache.py` - Response caching for performance
- `src/flext_tap_oracle_wms/simple_api.py` - Simplified API interface
- `src/flext_tap_oracle_wms/critical_validation.py` - Validates critical environment variables

### Dependencies

The project depends on several FLEXT ecosystem libraries:

- `flext-core` - Base patterns, logging, result handling
- `flext-meltano` - Singer/Meltano integration and generic interfaces
- `flext-oracle-wms` - Oracle WMS API connectivity and data models
- `flext-observability` - Monitoring, metrics, health checks

## Development Commands

### Installation and Setup

```bash
make setup                   # Complete project setup with pre-commit hooks
make install                 # Install project dependencies only
make install-dev             # Install with development dependencies

## TODO: GAPS DE ARQUITETURA IDENTIFICADOS - PRIORIDADE ALTA

### 🚨 GAP 1: Oracle WMS Library Integration Duplication
**Status**: ALTO - Dependency em flext-oracle-wms mas components duplicated
**Problema**:
- client.py pode duplicar flext-oracle-wms API client functionality
- auth.py pode reimplementar authentication já available na WMS library
- Configuration patterns podem divergir entre tap e library

**TODO**:
- [ ] Eliminate duplication com flext-oracle-wms library
- [ ] Integrate WMS authentication patterns from library
- [ ] Consolidate configuration management
- [ ] Document WMS integration patterns

### 🚨 GAP 2: Complex Component Architecture
**Status**: ALTO - Muitos specialized components podem indicate over-engineering
**Problema**:
- 15+ specialized components (mapper, validator, discovery, schema generator, etc.)
- Component boundaries podem not be optimal
- Maintenance overhead pode be high

**TODO**:
- [ ] Review component architecture para simplification opportunities
- [ ] Consolidate related functionality onde appropriate
- [ ] Optimize component boundaries
- [ ] Document component responsibilities clearly

### 🚨 GAP 3: WMS Business Logic in Tap Layer
**Status**: ALTO - WMS-specific business logic pode belong in lower layer
**Problema**:
- Entity discovery e schema generation são WMS business concerns
- Type mapping e data transformation podem belong in flext-oracle-wms
- Tap layer pode be too thick com business logic

**TODO**:
- [ ] Move WMS business logic to appropriate layer (flext-oracle-wms)
- [ ] Keep tap layer focused em Singer protocol compliance
- [ ] Refactor to proper layered architecture
- [ ] Document layer responsibilities
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

### WMS-Specific Operations

```bash
make wms-test               # Test Oracle WMS connectivity
make wms-entities           # List available WMS entities for extraction
make wms-performance        # Run WMS performance benchmarks
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

### Zero Tolerance Quality Gates

- **Python 3.13** - Latest Python version with strict typing
- **MyPy Strict Mode** - All code must be fully typed
- **Ruff with ALL rules** - Comprehensive linting (specific ignores in pyproject.toml)
- **90% Test Coverage** - Enforced minimum coverage threshold
- **Security Scanning** - Bandit + pip-audit for vulnerability detection
- **Pre-commit Hooks** - Automated quality checks on every commit

### Code Standards

- All code uses type hints with strict mypy configuration
- Pydantic models for configuration and data validation
- Comprehensive docstrings following Google style
- Clean Architecture patterns with clear separation of concerns
- Domain-Driven Design principles for business logic organization

## Common Development Workflows

### Adding a New WMS Entity

1. Add entity configuration to `meltano.yml` settings
2. Implement entity discovery in `entity_discovery.py`
3. Define schema mapping in `schema_generator.py`
4. Add stream configuration in `streams.py`
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
