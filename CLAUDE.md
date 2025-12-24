# flext-tap-oracle-wms - FLEXT Singer Ecosystem

**Hierarchy**: PROJECT
**Parent**: [../CLAUDE.md](../CLAUDE.md) - Workspace standards
**Last Update**: 2025-12-07

---

## Project Overview

**FLEXT-Tap-Oracle-WMS** is the Singer tap for Oracle Warehouse Management System extraction in the FLEXT ecosystem.

**Version**: 1.0.0  
**Status**: Production-ready  
**Python**: 3.13+

**CRITICAL INTEGRATION DEPENDENCIES**:

- **flext-meltano**: MANDATORY for ALL Singer operations (ZERO TOLERANCE for direct singer-sdk without flext-meltano)
- **flext-oracle-wms**: MANDATORY for ALL Oracle WMS operations (ZERO TOLERANCE for bypassing WMS domain)
- **flext-db-oracle**: MANDATORY for ALL Oracle Database operations (ZERO TOLERANCE for direct SQLAlchemy/oracledb imports)
- **flext-core**: Foundation patterns (FlextResult, FlextService, FlextContainer)

---

## Essential Commands

```bash
# Setup and validation
make setup                    # Complete development environment setup
make validate                 # Complete validation (lint + type + security + test)
make check                    # Quick check (lint + type)

# Quality gates
make lint                     # Ruff linting
make type-check               # Pyrefly type checking
make security                 # Bandit security scan
make test                     # Run tests
```

---

## Key Patterns

### Singer Tap Implementation

```python
from flext_core import FlextResult
from flext_tap_oracle_wms import FlextTapOracleWms

tap = FlextTapOracleWms()

# Discover catalog
result = tap.discover()
if result.is_success:
    catalog = result.unwrap()
```

---

## Critical Development Rules

### ZERO TOLERANCE Policies

**ABSOLUTELY FORBIDDEN**:

- ❌ Direct singer-sdk imports (use flext-meltano)
- ❌ Direct Oracle WMS operations (use flext-oracle-wms)
- ❌ Direct SQLAlchemy/oracledb imports (use flext-db-oracle)
- ❌ Exception-based error handling (use FlextResult)
- ❌ Type ignores or `Any` types

**MANDATORY**:

- ✅ Use `FlextResult[T]` for all operations
- ✅ Use flext-meltano for Singer operations
- ✅ Use flext-oracle-wms for WMS operations
- ✅ Use flext-db-oracle for Oracle operations
- ✅ Complete type annotations
- ✅ Zero Ruff violations

---

**See Also**:

- [Workspace Standards](../CLAUDE.md)
- [flext-core Patterns](../flext-core/CLAUDE.md)
- [flext-oracle-wms Patterns](../flext-oracle-wms/CLAUDE.md)
- [flext-meltano Patterns](../flext-meltano/CLAUDE.md)
