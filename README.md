# tap-oracle-wms

Singer tap for Oracle Warehouse Management System (WMS) built with the [Singer SDK](https://sdk.meltano.com) 0.47.4+.

This tap extracts data from Oracle WMS REST API with automatic entity discovery, dynamic schema generation, and full incremental sync support.

## Features

- 🔍 **Automatic Entity Discovery** - Discovers all available WMS entities dynamically
- 📊 **Dynamic Schema Generation** - Generates schemas from API metadata or sample data
- 🔄 **Incremental Sync** - Efficient data extraction using MOD_TS timestamps
- 📄 **HATEOAS Pagination** - Follows next_page URLs for efficient data retrieval
- 🛡️ **Resilient** - Built-in retry logic and error handling
- 🚀 **High Performance** - Optimized for large datasets with configurable page sizes
- 🔧 **Fully Configurable** - Extensive configuration options via Singer SDK
- 🐍 **Python 3.9+** - Compatible with Python 3.9, 3.10, 3.11, and 3.12

## Installation

```bash
pip install tap-oracle-wms
```

Or install from source:

```bash
git clone https://github.com/flext-sh/flext-tap-oracle-wms.git
cd flext-tap-oracle-wms
pip install -e .
```

## Configuration

### Using config.json

Create a `config.json` file with your Oracle WMS credentials:

```json
{
  "base_url": "https://your-wms-instance.com",
  "username": "your_username",
  "password": "your_password",
  "company_code": "*",
  "facility_code": "*",
  "page_size": 100
}
```

See [config.json.example](config.json.example) for all available options.

### Using Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your WMS credentials
```

## Usage

### Discover available entities

```bash
tap-oracle-wms --config config.json --discover > catalog.json
```

### Run a sync

```bash
tap-oracle-wms --config config.json --catalog catalog.json
```

### Incremental sync

The tap automatically performs incremental sync for entities with `mod_ts` field:

```bash
tap-oracle-wms --config config.json --catalog catalog.json --state state.json
```

### With Meltano

```yaml
# meltano.yml
plugins:
  extractors:
    - name: tap-oracle-wms
      namespace: tap_oracle_wms
      pip_url: tap-oracle-wms
      config:
        base_url: ${ORACLE_WMS_BASE_URL}
        username: ${ORACLE_WMS_USERNAME}
        password: ${ORACLE_WMS_PASSWORD}
```

## Key Configuration Options

### Core Settings
- `base_url` - Oracle WMS instance URL (required)
- `username` - Username for basic authentication (required)
- `password` - Password for basic authentication (required)
- `company_code` - WMS company code (default: "*" for all)
- `facility_code` - WMS facility code (default: "*" for all)

### Performance Settings
- `page_size` - Records per page, 1-1250 (default: 100)
- `request_timeout` - Request timeout in seconds (default: 120)
- `max_retries` - Maximum retry attempts (default: 3)

### Entity Selection
- `entities` - List of specific entities to extract
- `entity_patterns` - Include/exclude patterns for entity filtering
- `entity_filters` - Entity-specific filters

### Incremental Sync
- `enable_incremental` - Enable incremental sync (default: true)
- `start_date` - Initial extraction date for incremental sync
- `incremental_overlap_minutes` - Safety overlap for incremental sync (default: 5)

### Advanced Features
- `stream_maps` - Singer SDK stream maps for transformations
- `flattening_enabled` - Enable automatic schema flattening (default: true)
- `flattening_max_depth` - Maximum depth for flattening (default: 3)

## Incremental Sync Strategy

The tap implements intelligent incremental sync:

1. **Filter Rule**: `mod_ts > max(mod_ts from state) - 5 minutes`
2. **Ordering**: Records are processed in chronological order (`mod_ts ASC`)
3. **State Management**: Automatically tracks latest `mod_ts` for next sync
4. **Safety Overlap**: 5-minute overlap prevents missing records due to clock skew

## Testing

### Run unit tests

```bash
pytest tests/unit
```

### Run E2E tests (requires real WMS instance)

E2E tests require a `.env` file with valid WMS credentials. They are automatically skipped if the configuration is missing or invalid.

#### 1. Validate configuration

```bash
# Check if your environment is properly configured
python tests/e2e/validate_config.py
```

#### 2. Set up test environment

```bash
# Copy example configuration
cp .env.example .env

# Edit with your WMS credentials
# Required variables:
# - TAP_ORACLE_WMS_BASE_URL
# - TAP_ORACLE_WMS_USERNAME  
# - TAP_ORACLE_WMS_PASSWORD
```

#### 3. Run E2E tests

```bash
# Run all E2E tests (requires --run-e2e flag)
pytest tests/e2e --run-e2e

# Run with verbose output
pytest tests/e2e --run-e2e -v

# Run specific test
pytest tests/e2e/test_wms_e2e.py::test_tap_initialization --run-e2e

# Test specific entities
pytest tests/e2e/test_wms_e2e.py::test_specific_entity_extraction -k "item" --run-e2e
```

### Test behavior

- **No .env file**: All E2E tests are skipped with clear message
- **Missing credentials**: Tests are skipped with list of missing variables
- **Invalid URL**: Tests are skipped with validation error
- **Valid config**: Tests run against real WMS instance

## Development

### Prerequisites
- Python 3.9+
- Poetry or pip
- Access to Oracle WMS instance

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/flext-sh/flext-tap-oracle-wms.git
cd flext-tap-oracle-wms

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy .
```

### Architecture

The tap is built with Singer SDK 0.47.4+ for maximum simplicity and functionality:

- **tap.py** - Main tap class with automatic entity discovery
- **streams.py** - Dynamic REST stream using Singer SDK's RESTStream
- **config.py** - Comprehensive configuration schema
- **discovery.py** - Entity discovery and schema generation
- **auth.py** - Basic and OAuth2 authentication support

### Key Design Decisions

1. **Dynamic Discovery** - No hardcoded entities; discovers from API
2. **Schema Generation** - Creates schemas from API metadata or samples
3. **Singer SDK Features** - Leverages built-in retry, pagination, and state management
4. **Minimal Code** - Uses Singer SDK capabilities to reduce custom code

## Troubleshooting

### Common Issues

1. **No entities discovered**
   - Check base_url is correct
   - Verify credentials have read access
   - Check company/facility codes

2. **Incremental sync not working**
   - Ensure entity has `mod_ts` field
   - Check state file is being saved/loaded
   - Verify start_date is set correctly

3. **Performance issues**
   - Reduce page_size (try 500 or 250)
   - Enable request caching
   - Use entity_filters to limit data

### Debug Mode

Enable debug logging:

```bash
tap-oracle-wms --config config.json --discover --dev
```

Or set in config:

```json
{
  "log_level": "DEBUG",
  "dev_mode": true
}
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Documentation: [GitHub Wiki](https://github.com/flext-sh/flext-tap-oracle-wms/wiki)
- Issues: [GitHub Issues](https://github.com/flext-sh/flext-tap-oracle-wms/issues)
- Discussions: [GitHub Discussions](https://github.com/flext-sh/flext-tap-oracle-wms/discussions)

## Acknowledgments

Built with [Singer SDK](https://sdk.meltano.com) by [Meltano](https://meltano.com).