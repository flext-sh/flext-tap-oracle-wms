# flext-tap-oracle-wms

**Type**: Singer Tap | **Status**: 1.0.0 Release Preparation | **Dependencies**: flext-core, flext-oracle-wms

Singer-compliant tap for extracting data from Oracle Warehouse Management Systems.

> ⚠️ Development Status: 10 streams working; 37 MyPy errors (regression); architecture simplification planned.

## Quick Start

```bash
# Install dependencies
poetry install

# Test basic functionality
python -c "from flext_tap_oracle_wms import FlextMeltanoTapOracleWms; tap = FlextMeltanoTapOracleWms(); print('✅ Working')"

# Development setup
make setup

# Run tap discovery
make discover
```

## Current Reality

**What Actually Works:**

- 10 functional streams with proper replication key detection
- Singer SDK compliance with catalog discovery
- Oracle WMS API integration via flext-oracle-wms
- SOLID principles with Strategy/Factory patterns

**What Needs Work:**

- 37 MyPy type errors (regression during refactoring)
- Over-engineered architecture (26 files, 8,179 lines for a tap)
- 27% of tests disabled due to external dependencies
- No test coverage implemented

## Architecture Role in FLEXT Ecosystem

### **Singer Ecosystem Component**

FLEXT Tap Oracle WMS extracts data from Oracle WMS for data pipelines:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: FlexCore(Go) | FLEXT Service(Go/Python) | Clients     │
├─────────────────────────────────────────────────────────────────┤
│ Applications: API | Auth | Web | CLI | Quality | Observability  │
├─────────────────────────────────────────────────────────────────┤
│ Infrastructure: Oracle | LDAP | LDIF | gRPC | Plugin | WMS      │
├═════════════════════════════════════════════════════════════════┤
│ Singer Ecosystem: [TAP-ORACLE-WMS] | Targets(5) | DBT(4) | Ext  │
├─────────────────────────────────────────────────────────────────┤
│ Foundation: FLEXT-CORE (FlextResult | DI | Domain Patterns)     │
└─────────────────────────────────────────────────────────────────┘
```

### **Core Responsibilities**

1. **Data Extraction**: Oracle WMS data extraction using Singer protocol
2. **Schema Discovery**: Automatic catalog generation for WMS entities
3. **Pipeline Integration**: Singer-compliant for Meltano orchestration

## Key Features

### **Current Capabilities**

- **Singer SDK Integration**: Full Singer specification compliance
- **10 Working Streams**: Inventory, orders, shipments, locations, etc.
- **Authentication Support**: Basic Auth and OAuth2 methods
- **FLEXT Integration**: Built on flext-core and flext-oracle-wms patterns

### **Supported WMS Entities**

- Inventory management and tracking
- Order processing and fulfillment
- Shipment creation and tracking
- Location and facility management
- User and permission management

## Installation & Usage

### Installation

```bash
# Clone and install
cd /path/to/flext-tap-oracle-wms
poetry install

# Development setup
make setup
```

### Basic Usage

```bash
# Copy configuration template
cp config.json.example config.json

# Edit config.json with your WMS credentials
# {
#   "base_url": "https://your-wms.oraclecloud.com",
#   "username": "your_username",
#   "password": "your_password",
#   "auth_method": "basic"
# }

# Discover catalog
make discover

# Extract data
make run
```

### Meltano Integration

```yaml
# meltano.yml
extractors:
  - name: tap-oracle-wms
    namespace: tap_oracle_wms
    pip_url: flext-tap-oracle-wms
    config:
      base_url: ${WMS_BASE_URL}
      username: ${WMS_USERNAME}
      password: ${WMS_PASSWORD}
```

## Development Commands

### Quality Gates (Zero Tolerance)

```bash
# Complete validation pipeline (run before commits)
make validate              # Full validation (lint + type + security + test)
make check                 # Quick lint + type check + test
make test                  # Run all tests (90% coverage requirement)
make lint                  # Code linting
make type-check
make format                # Code formatting
make security              # Security scanning
```

### Singer Operations

```bash
# Tap operations
make discover              # Run tap discovery mode
make run                   # Run tap extraction
make validate-config       # Validate configuration
make wms-test             # Test WMS connectivity
```

### Testing

```bash
# Test categories
make test-unit             # Unit tests only
make test-integration      # Integration tests only
make test-singer           # Singer protocol tests
make coverage-html         # Generate HTML coverage report
```

## Configuration

### Environment Variables

```bash
# WMS connection settings
export TAP_ORACLE_WMS_BASE_URL="https://your-wms.oraclecloud.com"
export TAP_ORACLE_WMS_USERNAME="api_user"
export TAP_ORACLE_WMS_PASSWORD="secure_password"
export TAP_ORACLE_WMS_AUTH_METHOD="basic"

# Extraction settings
export TAP_ORACLE_WMS_PAGE_SIZE="1000"
export TAP_ORACLE_WMS_START_DATE="2024-01-01T00:00:00Z"
```

### Configuration Examples

```json
{
  "base_url": "https://your-wms.oraclecloud.com",
  "username": "api_user",
  "password": "secure_password",
  "auth_method": "basic",
  "entities": ["inventory", "orders", "shipments"],
  "page_size": 1000,
  "start_date": "2024-01-01T00:00:00Z"
}
```

## Quality Standards

### **Quality Targets**

- **Coverage**: 90% target
- **Type Safety**: MyPy strict mode planned (currently ~37 errors)
- **Linting**: Ruff with rules
- **Security**: Bandit + pip-audit scanning

## Integration with FLEXT Ecosystem

### **FLEXT Core Patterns**

```python
# Singer tap using FLEXT patterns
from flext_tap_oracle_wms import FlextMeltanoTapOracleWms
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

tap = FlextMeltanoTapOracleWms()
streams = tap.discover_streams()
```

### **Service Integration**

- **flext-oracle-wms**: Oracle WMS API client integration
- **flext-meltano**: Meltano orchestration platform
- **Singer Targets**: Integration with flext-target-\* projects
- **DBT Models**: Integration with flext-dbt-oracle-wms

## Current Status

**Version**: 0.9.9 RC (Development)

**Completed**:

- ✅ 10 functional streams with Singer compliance
- ✅ Oracle WMS API integration
- ✅ SOLID architecture patterns
- ✅ Ruff linting compliance (0 errors)

**Critical Issues**:

- ❌ 37 MyPy type errors (regression needs immediate fix)
- ❌ Over-engineered architecture (needs simplification)
- ❌ Test coverage incomplete

**Planned**:

- 📋 Architecture simplification (26 files → 6-8 files)
- 📋 Comprehensive test coverage
- 📋 Production deployment patterns

## Contributing

### Development Standards

- **Singer Compliance**: Follow Singer SDK patterns
- **Type Safety**: All code must pass MyPy (fix 37 current errors)
- **Testing**: Maintain 90% coverage
- **Architecture**: Simplify over-engineered patterns

### Development Workflow

```bash
# Setup and validate
make setup
make validate
make test
make discover
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Links

For verified project capabilities and accurate status information, see [ACTUAL_CAPABILITIES.md](../ACTUAL_CAPABILITIES.md).

- **[flext-core](../flext-core)**: Foundation library
- **[flext-oracle-wms](../flext-oracle-wms)**: Oracle WMS integration
- **[CLAUDE.md](CLAUDE.md)**: Development guidance

---
