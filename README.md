# FLEXT Tap Oracle WMS

Enterprise Singer tap for Oracle Warehouse Management System (WMS) built with [Singer SDK](https://sdk.meltano.com) 0.47.4+ and FLEXT standards.

Extracts data from Oracle WMS REST APIs with automatic entity discovery, dynamic schema generation, and incremental sync support.

## Features

- 🔍 **Dynamic Entity Discovery** - Auto-discovers WMS entities from API
- 📊 **Schema Generation** - Creates schemas from API metadata  
- 🔄 **Incremental Sync** - Efficient extraction using `mod_ts` timestamps
- 📄 **HATEOAS Pagination** - Follows WMS API pagination patterns
- 🛡️ **Enterprise Ready** - Built-in retry, error handling, and observability
- 🏗️ **FLEXT Standards** - Clean Architecture with flext-core integration
- 🐍 **Python 3.13** - Modern Python with strict typing

## Installation

```bash
pip install flext-tap-oracle-wms
```

Or from source:

```bash
git clone https://github.com/flext-sh/flext-tap-oracle-wms.git
cd flext-tap-oracle-wms
pip install -e .
```

## Configuration

### Basic Configuration

Create a `config.json` file:

```json
{
  "base_url": "https://your-wms-instance.com",
  "username": "your_username", 
  "password": "your_password",
  "entities": ["allocation", "order_hdr", "order_dtl", "item_master"]
}
```

### Environment Variables

Set environment variables:

```bash
export TAP_ORACLE_WMS_BASE_URL="https://your-wms-instance.com"
export TAP_ORACLE_WMS_USERNAME="your_username"
export TAP_ORACLE_WMS_PASSWORD="your_password"
export TAP_ORACLE_WMS_ENTITIES="allocation,order_hdr,order_dtl,item_master"
```

## Usage

### Discovery

```bash
flext-tap-oracle-wms --config config.json --discover > catalog.json
```

### Extract Data

```bash
flext-tap-oracle-wms --config config.json --catalog catalog.json > data.jsonl
```

### Incremental Sync

```bash
flext-tap-oracle-wms --config config.json --catalog catalog.json --state state.json > data.jsonl
```

### With Meltano

Add to your `meltano.yml`:

```yaml
plugins:
  extractors:
    - name: flext-tap-oracle-wms
      namespace: tap_oracle_wms
      pip_url: flext-tap-oracle-wms
      config:
        base_url: ${TAP_ORACLE_WMS_BASE_URL}
        username: ${TAP_ORACLE_WMS_USERNAME}
        password: ${TAP_ORACLE_WMS_PASSWORD}
        entities: ["allocation", "order_hdr", "order_dtl"]
```

## Configuration Options

### Required Settings

- `base_url` - Oracle WMS REST API URL
- `username` - Authentication username
- `password` - Authentication password  
- `entities` - List of WMS entities to extract

### Optional Settings

- `company_code` - WMS company scope (default: "*")
- `facility_code` - WMS facility scope (default: "*") 
- `page_size` - Records per page (default: 500, max: 10000)
- `timeout` - Request timeout seconds (default: 30)
- `max_retries` - Retry attempts (default: 3)

### Incremental Sync

- `enable_incremental` - Enable incremental sync (default: true)
- `replication_key` - Timestamp field for incremental sync (default: "mod_ts")
- `start_date` - Initial extraction date (ISO format)

## Architecture

The tap follows FLEXT standards with clean architecture:

- **TapOracleWMS** - Main tap class using Singer SDK
- **WMSStream** - Dynamic REST stream with HATEOAS pagination  
- **WMSClient** - HTTP client with retry and error handling
- **ConfigMapper** - Configuration mapping and validation
- **EntityDiscovery** - Dynamic entity discovery from WMS API

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
