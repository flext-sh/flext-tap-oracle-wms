# internal.invalid.md - TAP-ORACLE-WMS PROJECT SPECIFICS

**Hierarchy**: PROJECT-SPECIFIC
**Project**: TAP Oracle WMS - Singer protocol data extraction from Oracle WMS systems
**Status**: PRODUCTION
**Last Updated**: 2025-06-25

**Reference**: `/home/marlonsc/CLAUDE.md` → Universal principles
**Reference**: `/home/marlonsc/internal.invalid.md` → Cross-workspace issues
**Reference**: `../CLAUDE.md` → PyAuto workspace patterns

---

## 🎯 PROJECT-SPECIFIC CONFIGURATION

### Virtual Environment Usage

```bash
# MANDATORY: Use workspace venv
source /home/marlonsc/pyauto/.venv/bin/activate
# Verify Singer: python -c "import singer; print('✅ Singer available')"
# Verify Oracle: python -c "import oracledb; print('✅ Oracle client available')"
```

### Agent Coordination

```bash
# Read workspace coordination first
cat /home/marlonsc/pyauto/.token | tail -5
# Project context
echo "PROJECT_CONTEXT=tap-oracle-wms" > .token
echo "STATUS=production-singer-tap" >> .token
echo "ORACLE_WMS_INTEGRATION=active" >> .token
```

---

## 🚨 CRITICAL PROJECT-SPECIFIC ISSUES

### **1. Singer Protocol Compliance Requirements**

**Critical**: This is a PRODUCTION Singer tap - must follow Singer spec exactly

**Singer Protocol Requirements**:

```bash
# MANDATORY: Singer spec compliance validation
python -m tap_oracle_wms --config config.json --discover    # Schema discovery
python -m tap_oracle_wms --config config.json --catalog catalog.json    # Data extraction

# Output MUST be valid Singer format
# {"type": "RECORD", "record": {...}, "stream": "stream_name", "time_extracted": "..."}
# {"type": "STATE", "value": {...}}
# {"type": "SCHEMA", "stream": "stream_name", "schema": {...}}
```

### **2. Oracle WMS-Specific Data Patterns**

**Complexity**: WMS data has specific Oracle patterns requiring careful handling

**Critical WMS Entities**:

```python
# Core WMS entities that require specific handling
WMS_ENTITIES = [
    "allocation",     # Inventory allocation - complex composite keys
    "order_hdr",      # Order headers - timestamp-based incremental
    "order_dtl",      # Order details - foreign key dependencies
    "item_master",    # Item master data - slowly changing dimensions
    "location",       # Warehouse locations - hierarchical structure
]

# Each entity has specific extraction patterns
ENTITY_PATTERNS = {
    "allocation": "batch_with_composite_keys",
    "order_hdr": "incremental_by_timestamp",
    "order_dtl": "dependent_on_order_hdr",
    "item_master": "full_refresh_daily",
    "location": "hierarchical_extraction"
}
```

### **3. Production Integration with client-b-poc-oic-wms**

**Critical Dependency**: This tap is actively used by client-b-poc-oic-wms project

**Integration Requirements**:

```bash
# MANDATORY: Test integration before ANY changes
cd ../client-b-poc-oic-wms
python -c "from tap_oracle_wms import TapOracleWMS; print('✅ Tap import works')"

# Verify extraction patterns still work
python scripts/test_tap_integration.py                      # Integration test
python scripts/validate_wms_entity_extraction.py           # Entity-specific validation
```

---

## 🔧 PROJECT-SPECIFIC TECHNICAL REQUIREMENTS

### **Oracle WMS Environment Variables**

```bash
# MANDATORY: Oracle WMS connection configuration
export TAP_ORACLE_WMS_HOST="wms-oracle-server"            # WMS Oracle host
export TAP_ORACLE_WMS_PORT="1521"                         # Oracle port
export TAP_ORACLE_WMS_SID="WMSPRD"                        # WMS database SID
export TAP_ORACLE_WMS_USER="wms_reader"                   # Read-only user
export TAP_ORACLE_WMS_PASSWORD="secure_wms_password"       # Secure password

# Singer protocol configuration
export TAP_ORACLE_WMS_BATCH_SIZE="5000"                   # Optimal batch size for WMS
export TAP_ORACLE_WMS_REQUEST_TIMEOUT="300"               # 5 minute timeout for large queries
export TAP_ORACLE_WMS_INCREMENTAL_REPLICATION="enabled"   # Incremental extraction

# WMS-specific optimizations
export TAP_ORACLE_WMS_USE_CURSOR_PAGINATION="true"        # Large dataset handling
export TAP_ORACLE_WMS_PARALLEL_EXTRACTION="false"         # Avoid WMS system overload
```

### **Singer TAP CLI Commands**

```bash
# Singer protocol standard commands
python -m tap_oracle_wms --config config.json --discover > catalog.json
python -m tap_oracle_wms --config config.json --catalog catalog.json > data.jsonl

# WMS-specific operations
python -m tap_oracle_wms --config config.json --test-connection
python -m tap_oracle_wms --config config.json --validate-entities
python -m tap_oracle_wms --config config.json --performance-test

# Integration testing with Meltano
meltano extract tap-oracle-wms --dry-run                   # Meltano integration test
```

### **WMS-Specific Quality Gates**

```bash
# MANDATORY: Singer tap quality standards
ruff check --select ALL .                                 # Zero tolerance approach
mypy --strict .                                           # Strict typing required
pytest tests/ --cov=85                                    # High coverage for production

# Singer protocol validation
python scripts/validate_singer_compliance.py              # Singer spec compliance
python scripts/test_wms_entity_extraction.py             # WMS entity validation
python scripts/performance_benchmark.py                   # Extraction performance
```

---

## 📊 WMS-SPECIFIC PERFORMANCE CHARACTERISTICS

### **Oracle WMS Extraction Performance**

- **Connection Establishment**: ~800ms to WMS Oracle system
- **Schema Discovery**: ~2 seconds for all WMS entities
- **Allocation Entity**: ~15,000 records/minute (complex queries)
- **Order Headers**: ~25,000 records/minute (timestamp-based)
- **Order Details**: ~20,000 records/minute (foreign key dependent)
- **Item Master**: ~5,000 records/minute (full table scan)

### **WMS Performance Monitoring**

```python
# Built-in WMS performance monitoring
from tap_oracle_wms.monitoring import WMSPerformanceMonitor

with WMSPerformanceMonitor(entity="allocation") as monitor:
    records = extract_allocation_data()
# Automatically logs extraction rates and identifies slow queries
```

---

## 🚨 WMS-SPECIFIC INTEGRATION POINTS

### **Downstream Dependencies**

**Critical**: Changes affect these integrations:

- **client-b-poc-oic-wms**: Primary consumer of this tap
- **Meltano projects**: Used as Singer tap in Meltano pipelines
- **target-oracle-wms**: Paired target for WMS data replication

### **WMS Integration Testing Protocol**

```bash
# MANDATORY: After ANY WMS tap changes
python scripts/test_client-b_integration.py               # Test primary consumer
python scripts/validate_meltano_compatibility.py          # Meltano integration test
python scripts/run_wms_end_to_end_test.py                # Full pipeline test
```

---

## 🔄 WMS-SPECIFIC MAINTENANCE PROCEDURES

### **Daily WMS Health Monitoring**

```bash
# MANDATORY: Production WMS monitoring
python -m tap_oracle_wms --config config.json --health-check
python scripts/wms_connection_health.py                   # WMS system health
python scripts/wms_extraction_performance.py              # Performance monitoring
```

### **WMS Schema Evolution Handling**

```bash
# When WMS schema changes (common in WMS systems)
python -m tap_oracle_wms --config config.json --discover > new_catalog.json
python scripts/compare_wms_schemas.py old_catalog.json new_catalog.json
python scripts/update_extraction_logic.py                 # Update extraction if needed
```

---

## 📝 WMS PROJECT COORDINATION NOTES

### **WMS-Specific Agent Guidelines**

- **Schema Changes**: WMS schemas change frequently - always test discovery
- **Performance Changes**: WMS systems are sensitive to query load
- **Connection Changes**: Coordinate with WMS system REDACTED_LDAP_BIND_PASSWORDistrators
- **Entity Changes**: May affect downstream consumers immediately

### **WMS Emergency Procedures**

```bash
# If WMS extraction fails
echo "WMS_EXTRACTION_FAILURE_$(date)" >> .token
python scripts/wms_emergency_diagnostics.py               # Full WMS diagnostic
python scripts/fallback_to_cached_wms_data.py            # Use cached data
# Never proceed with incomplete WMS data extraction
```

---

## 🏆 WMS PROJECT SUCCESS PATTERNS

### **Production Singer Tap Best Practices**

This project demonstrates:

- ✅ **Singer Protocol Compliance**: Exact adherence to Singer specification
- ✅ **Oracle WMS Integration**: Production-grade WMS system integration
- ✅ **Performance Optimization**: Optimized for WMS-specific data patterns
- ✅ **Error Handling**: Robust error handling for WMS system variations

### **WMS Extraction Patterns for Replication**

```python
# WMS entity extraction pattern
class WMSEntityExtractor:
    def extract_with_pagination(self, entity: str, bookmark: Dict) -> Iterator[Dict]:
        """WMS-optimized extraction with proper pagination"""
        cursor = self.get_cursor_for_entity(entity, bookmark)

        while cursor.has_more():
            batch = cursor.fetch_batch(size=self.batch_size)
            for record in batch:
                yield self.transform_wms_record(record, entity)

            # Update bookmark for incremental extraction
            bookmark = self.update_bookmark(cursor.position)
```

---

**Authority**: This file defines WMS-specific Singer tap development standards
**Critical Note**: Production tap - changes require thorough testing with WMS systems
**Integration**: Primary dependency for client-b-poc-oic-wms project operations
