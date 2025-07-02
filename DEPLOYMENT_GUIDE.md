# 🚀 TAP Oracle WMS - Production Deployment Guide

## 📋 Prerequisites

### System Requirements
- **Python**: 3.9+ (tested with 3.9, 3.10, 3.11, 3.12, 3.13)
- **Memory**: Minimum 512MB RAM, recommended 2GB+ for large datasets
- **Network**: HTTPS access to Oracle WMS API endpoints
- **OS**: Linux, macOS, or Windows with WSL2

### Oracle WMS Requirements
- Oracle WMS Cloud or On-Premise with REST API enabled
- Valid user credentials with read access to required entities
- Network connectivity to WMS API endpoints (typically port 443/HTTPS)

## 🔧 Installation

### Quick Start (Recommended)
```bash
git clone <repository-url>
cd flext-tap-oracle-wms
./setup_production.sh
```

### Manual Installation
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .

# Verify installation
tap-oracle-wms --help
```

## ⚙️ Configuration

### Basic Configuration
Create `config.production.json`:

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

### Production Configuration with Advanced Features
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
    },
    "order_hdr": {
      "mod_ts__gte": "today-1w"
    }
  },
  
  "entity_filters": {
    "allocation": {"status_id": "ACTIVE"},
    "order_hdr": {"facility_code": "MAIN"}
  },
  
  "circuit_breaker": {
    "enabled": true,
    "failure_threshold": 5,
    "recovery_timeout": 60
  },
  
  "entities": ["allocation", "order_hdr", "inventory"],
  "enable_incremental": true,
  "test_connection": true
}
```

## 🗓️ Simple Date Expressions

Replace complex ISO timestamps with intuitive expressions:

| Expression | Result | Description |
|------------|--------|-------------|
| `today` | `2025-07-01T00:00:00Z` | Start of today UTC |
| `yesterday` | `2025-06-30T00:00:00Z` | Start of yesterday UTC |
| `now` | `2025-07-01T15:30:45Z` | Current timestamp |
| `today-7d` | `2025-06-24T00:00:00Z` | 7 days ago |
| `today+1w` | `2025-07-08T00:00:00Z` | 1 week from today |
| `today-3m` | `2025-04-01T00:00:00Z` | 3 months ago (precise) |

### Examples
```json
{
  "simple_date_expressions": {
    "allocation": {
      "mod_ts__gte": "today-7d",
      "mod_ts__lte": "today"
    },
    "order_hdr": {
      "create_ts__gte": "yesterday",
      "mod_ts__lte": "now"
    }
  }
}
```

## 🚀 Running in Production

### Discovery Phase
```bash
# Discover available entities and generate catalog
tap-oracle-wms --config config.production.json --discover > catalog.json
```

### Data Extraction
```bash
# Extract data using catalog
tap-oracle-wms --config config.production.json --catalog catalog.json > data.jsonl
```

### Using Production Runner (Recommended)
```bash
# All-in-one execution
./run_production.sh config.production.json
```

## 📊 Performance Tuning

### Page Size Optimization
```json
{
  "page_size": 100,  // Small datasets: 50-100
  "page_size": 500,  // Medium datasets: 200-500  
  "page_size": 1000  // Large datasets: 500-1000 (max)
}
```

### Record Limiting
```json
{
  "record_limit": 1000,   // Development
  "record_limit": 10000,  // Testing
  "record_limit": null    // Production (no limit)
}
```

### Circuit Breaker
```json
{
  "circuit_breaker": {
    "enabled": true,
    "failure_threshold": 5,    // Failures before opening circuit
    "recovery_timeout": 60     // Seconds before retry
  }
}
```

## 🔍 Monitoring and Logging

### Log Levels
- **INFO**: Production (recommended)
- **DEBUG**: Development/troubleshooting
- **WARNING**: Errors only
- **ERROR**: Critical issues only

### Production Logging
```json
{
  "log_level": "INFO",
  "disable_trace_logs": true,
  "log_to_file": false
}
```

### Development Logging
```json
{
  "log_level": "DEBUG", 
  "disable_trace_logs": false,
  "log_to_file": true,
  "log_file_path": "tap-oracle-wms.log"
}
```

## 🔐 Security Best Practices

### Credential Management
```bash
# Use environment variables (recommended)
export TAP_ORACLE_WMS_USERNAME="your_username"
export TAP_ORACLE_WMS_PASSWORD="your_password"
```

```json
{
  "username": "${TAP_ORACLE_WMS_USERNAME}",
  "password": "${TAP_ORACLE_WMS_PASSWORD}"
}
```

### SSL Configuration
```json
{
  "verify_ssl": true,           // Always verify in production
  "ssl_ca_file": "/path/to/ca.pem",
  "ssl_cert_file": "/path/to/cert.pem",
  "ssl_key_file": "/path/to/key.pem"
}
```

## 🔄 Incremental Sync

### Automatic Incremental
```json
{
  "enable_incremental": true,
  "incremental_lookback_hours": 24
}
```

### Manual Incremental with Dates
```json
{
  "simple_date_expressions": {
    "allocation": {
      "mod_ts__gte": "today-1d"  // Only last 24 hours
    }
  }
}
```

## 🛠️ Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Test connectivity
curl -u username:password https://your-wms.oracle.com/wms/lgfapi/v10/entity/
```

#### Schema Discovery Issues
```json
{
  "verify_entity_access": true,   // Enable entity validation
  "schema_discovery_method": "describe"  // More thorough discovery
}
```

#### Performance Issues
```json
{
  "page_size": 100,              // Reduce page size
  "request_timeout": 300,        // Increase timeout  
  "max_parallel_streams": 1      // Disable parallelism
}
```

### Debug Mode
```json
{
  "log_level": "DEBUG",
  "disable_trace_logs": false,
  "test_connection": true
}
```

## 📈 Scaling for Large Datasets

### High-Volume Configuration
```json
{
  "page_size": 1000,
  "request_timeout": 7200,       // 2 hours
  "max_parallel_streams": 5,
  "record_limit": null,          // No limits
  "circuit_breaker": {
    "enabled": true,
    "failure_threshold": 10,     // Higher tolerance
    "recovery_timeout": 120      // Longer recovery
  }
}
```

### Memory Optimization
```json
{
  "connection_pool_size": 20,
  "connection_pool_maxsize": 100,
  "compression_enabled": true
}
```

## 🔄 Automation and Scheduling

### Cron Example (Daily Incremental)
```bash
# Run daily at 2 AM
0 2 * * * /path/to/run_production.sh /path/to/config.production.json > /var/log/tap-oracle-wms.log 2>&1
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["tap-oracle-wms", "--config", "config.production.json"]
```

## ✅ Validation and Testing

### Pre-Production Checklist
- [ ] Configuration file validated
- [ ] Connectivity tested
- [ ] Sample extraction successful
- [ ] Log levels appropriate
- [ ] Security credentials secured
- [ ] Performance benchmarked

### Test Commands
```bash
# Validate configuration
python evidence_validation_tap_oracle_wms/validate_all_configs.py

# Run test suite
./evidence_validation_tap_oracle_wms/test_final_complete_system.sh

# Quick connectivity test
tap-oracle-wms --config config.production.json --discover | head -20
```

## 📞 Support and Maintenance

### Regular Maintenance
- Monitor log files for errors
- Update credentials as needed
- Review performance metrics
- Update configuration for new requirements

### Health Checks
```bash
# Basic health check
tap-oracle-wms --config config.production.json --discover >/dev/null && echo "OK" || echo "FAILED"
```

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Setup
./setup_production.sh

# Discovery
tap-oracle-wms --config config.json --discover > catalog.json

# Extraction  
tap-oracle-wms --config config.json --catalog catalog.json > data.jsonl

# Production run
./run_production.sh config.production.json
```

### Essential Configuration
```json
{
  "base_url": "https://your-wms.oracle.com",
  "username": "user", "password": "pass",
  "page_size": 100, "log_level": "INFO",
  "simple_date_expressions": {
    "allocation": {"mod_ts__gte": "today-7d"}
  },
  "entities": ["allocation"]
}
```

---

**🏆 Your TAP Oracle WMS is now ready for production deployment!**