# TAP Oracle WMS

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Singer SDK](https://img.shields.io/badge/Singer%20SDK-0.46.4%2B-green)
![Oracle WMS](https://img.shields.io/badge/Oracle%20WMS-Cloud%20%7C%20On--Premise-orange)

A Singer tap for extracting data from Oracle WMS (Warehouse Management System) using the REST API.

## ⚡ Quick Start

```bash
# Install
pip install -e .

# Configure
cp examples/configs/basic.json config.json
# Edit config.json with your Oracle WMS credentials

# Discover schema
tap-oracle-wms --config config.json --discover > catalog.json

# Extract data
tap-oracle-wms --config config.json --catalog catalog.json
```

## 🎯 Features

- **Oracle WMS REST API Integration**: Native integration with Oracle WMS Cloud and On-Premise
- **Singer Protocol Compliance**: Full Singer specification compliance for data pipeline integration
- **Advanced Pagination**: HATEOAS cursor-based pagination for optimal performance
- **Schema Discovery**: Automatic schema generation for any Oracle WMS entity
- **Simple Date Expressions**: Intuitive date filters (`today-7d`, `yesterday`, etc.)
- **Circuit Breaker**: Resilient error handling for production environments
- **Record Limiting**: Configurable extraction limits for testing and development

## 📋 Requirements

- Python 3.9+
- Oracle WMS with REST API access
- Valid user credentials with read permissions

## 🔧 Installation

### Production Setup (Recommended)
```bash
./setup_production.sh
```

### Manual Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## ⚙️ Configuration

### Basic Configuration
```json
{
  "base_url": "https://your-wms.oracle.com",
  "username": "your_username",
  "password": "your_password",
  "auth_method": "basic",
  "page_size": 100,
  "entities": ["allocation", "order_hdr", "inventory"]
}
```

### Advanced Configuration
```json
{
  "base_url": "https://your-wms.oracle.com",
  "username": "your_username",
  "password": "your_password",
  "auth_method": "basic",
  "page_size": 100,
  "record_limit": 5000,
  "log_level": "INFO",
  "disable_trace_logs": true,
  "simple_date_expressions": {
    "allocation": {
      "mod_ts__gte": "today-7d",
      "create_ts__gte": "yesterday"
    }
  },
  "entity_filters": {
    "allocation": {"status_id": "ACTIVE"}
  },
  "circuit_breaker": {
    "enabled": true,
    "failure_threshold": 5,
    "recovery_timeout": 60
  },
  "entities": ["allocation", "order_hdr", "inventory"]
}
```

## 📅 Simple Date Expressions

Replace complex ISO timestamps with intuitive expressions:

| Expression | Result | Description |
|------------|--------|-------------|
| `today` | `2025-07-01T00:00:00Z` | Start of today UTC |
| `yesterday` | `2025-06-30T00:00:00Z` | Start of yesterday UTC |
| `now` | `2025-07-01T15:30:45Z` | Current timestamp |
| `today-7d` | `2025-06-24T00:00:00Z` | 7 days ago |
| `today+1w` | `2025-07-08T00:00:00Z` | 1 week from today |
| `today-3m` | `2025-04-01T00:00:00Z` | 3 months ago (precise) |

## 🚀 Usage Examples

### Discovery
```bash
tap-oracle-wms --config config.json --discover > catalog.json
```

### Full Extraction
```bash
tap-oracle-wms --config config.json --catalog catalog.json > data.jsonl
```

### Testing with Limited Records
```bash
# Extract only 100 records for testing
echo '{"record_limit": 100}' | jq -s add config.json - > test_config.json
tap-oracle-wms --config test_config.json --catalog catalog.json
```

## 📁 Project Structure

```
├── src/tap_oracle_wms/     # Main source code
├── tests/                  # Test utilities
├── examples/               # Configuration examples
├── docs/                   # Additional documentation
├── setup_production.sh     # Production setup script
└── DEPLOYMENT_GUIDE.md     # Detailed deployment guide
```

## 🧪 Testing

### Validate Configurations
```bash
python tests/validate_all_configs.py
```

### Test Connection
```bash
tap-oracle-wms --config config.json --discover | head -20
```

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Configuration Examples](examples/configs/)** - Sample configurations
- **[API Documentation](docs/)** - Detailed API reference

## 🔐 Security

- Store credentials in environment variables
- Use SSL/TLS for all connections
- Follow Oracle WMS security best practices
- Regular credential rotation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the [Deployment Guide](DEPLOYMENT_GUIDE.md)
2. Review [configuration examples](examples/configs/)
3. Open an issue on GitHub

---

**Built with ❤️ for Oracle WMS integration**