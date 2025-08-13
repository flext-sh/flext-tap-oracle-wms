# End-to-End Tests

## Overview

This directory contains end-to-end (E2E) tests for FLEXT Tap Oracle WMS, focusing on complete user workflows and system behavior from CLI execution to data output.

## Current Status

❌ **CRITICAL ISSUE**: All E2E tests are currently disabled due to external WMS dependencies.

**Status Summary**:

- **E2E Tests**: Completely disabled (0% coverage)
- **User Workflows**: Not validated end-to-end
- **Priority**: High - Required for production confidence

## Test Structure

### **Disabled E2E Tests**

#### **[test_wms_e2e.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup](test_wms_e2e.py.DISABLED_USES_FORBIDDEN_SAMPLES.backup)**

**Purpose**: Complete end-to-end workflow testing
**Current State**: Disabled due to live Oracle WMS instance requirements
**Scope**:

- CLI command execution (discovery, extraction)
- Complete Singer protocol compliance
- Real-world data extraction scenarios
- Error handling in production-like conditions
- Performance validation with actual WMS data

**Remediation Required**:

- Implement comprehensive E2E mock environment
- Create realistic WMS simulation for testing
- Add CLI execution testing framework
- Implement output validation systems

## E2E Testing Strategy

### **Complete User Workflows**

#### **Discovery Workflow**

```bash
# Planned E2E test scenarios
tap-oracle-wms --config config.json --discover > catalog.json
```

**Test Coverage**:

- CLI argument parsing and validation
- Configuration loading and validation
- WMS connection establishment
- Entity discovery execution
- Schema generation and output
- Catalog JSON format compliance

#### **Extraction Workflow**

```bash
# Complete extraction pipeline
tap-oracle-wms --config config.json --catalog catalog.json > output.jsonl
```

**Test Coverage**:

- Catalog loading and stream selection
- Authentication flow execution
- Data extraction with pagination
- Singer message format compliance
- Error handling and recovery
- Performance characteristics

#### **Configuration Validation Workflow**

```bash
# Configuration validation testing
tap-oracle-wms --config invalid_config.json --discover
```

**Test Coverage**:

- Invalid configuration handling
- Clear error messaging
- Exit code compliance
- Help message accuracy

### **Singer Protocol Compliance**

#### **Message Format Validation**

```python
def test_singer_message_compliance():
    """Test complete Singer message format compliance."""
    # Execute tap and capture output
    result = run_tap_command(["--config", "test_config.json", "--discover"])

    # Parse and validate Singer messages
    messages = parse_singer_output(result.stdout)

    # Validate message types and structure
    assert any(msg.type == "SCHEMA" for msg in messages)
    assert any(msg.type == "RECORD" for msg in messages)
    assert any(msg.type == "STATE" for msg in messages)

    # Validate message content
    for schema_msg in filter(lambda m: m.type == "SCHEMA", messages):
        validate_json_schema(schema_msg.schema)
```

#### **State Management Testing**

```python
def test_incremental_state_management():
    """Test incremental extraction with state management."""
    # First extraction
    result1 = run_tap_extraction(config, catalog)
    state1 = extract_final_state(result1)

    # Second extraction with state
    result2 = run_tap_extraction(config, catalog, state1)
    state2 = extract_final_state(result2)

    # Validate incremental behavior
    assert state2.bookmarks != state1.bookmarks
    validate_incremental_records(result2.records)
```

## Mock Environment Architecture

### **E2E Mock Infrastructure**

```python
class E2EMockWMSEnvironment:
    """Complete mock WMS environment for E2E testing."""

    def __init__(self):
        self.mock_server = MockWMSServer()
        self.test_data = TestDataManager()
        self.config_generator = ConfigGenerator()

    def setup_complete_environment(self):
        """Setup complete mock environment for E2E testing."""
        # Mock WMS API server
        self.mock_server.start()

        # Generate test configurations
        self.configs = self.config_generator.generate_test_configs()

        # Load test data sets
        self.test_data.load_datasets()

    def teardown(self):
        """Clean up mock environment."""
        self.mock_server.stop()
        self.test_data.cleanup()
```

### **Test Data Management**

```
tests/fixtures/e2e/
├── datasets/
│   ├── small_dataset/              # Quick E2E validation
│   │   ├── items.json              # 100 items
│   │   ├── inventory.json          # 500 inventory records
│   │   └── orders.json             # 50 orders
│   ├── medium_dataset/             # Performance testing
│   │   ├── items.json              # 10,000 items
│   │   ├── inventory.json          # 50,000 inventory records
│   │   └── orders.json             # 5,000 orders
│   └── large_dataset/              # Stress testing
│       ├── items.json              # 100,000 items
│       ├── inventory.json          # 1,000,000 inventory records
│       └── orders.json             # 100,000 orders
├── configurations/
│   ├── basic_e2e.json              # Basic E2E configuration
│   ├── production_like.json        # Production-like settings
│   ├── error_scenarios.json        # Error condition testing
│   └── performance_test.json       # Performance benchmarking
└── expected_outputs/
    ├── discovery_output.json       # Expected discovery results
    ├── extraction_samples.jsonl    # Sample extraction output
    └── error_messages.json         # Expected error formats
```

## CLI Testing Framework

### **Command Execution Testing**

```python
import asyncio
import json
from pathlib import Path

async def run_tap_command(args: list[str], input_data: str | None = None, timeout: int = 300):
    """Execute tap command and capture results using asyncio."""
    cmd = ["tap-oracle-wms", *args]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE if input_data else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=input_data.encode() if input_data else None),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        raise
    return CLIResult(
        returncode=process.returncode,
        stdout=stdout.decode(),
        stderr=stderr.decode(),
        command=cmd,
    )

def test_cli_discovery_execution():
    """Test CLI discovery command execution."""
    with e2e_mock_environment():
        result = await run_tap_command([
            "--config", "tests/fixtures/e2e/basic_e2e.json",
            "--discover"
        ])

        # Validate command success
        assert result.returncode == 0
        assert result.stderr == ""

        # Validate output format
        catalog = json.loads(result.stdout)
        assert "streams" in catalog
        assert len(catalog["streams"]) > 0
```

### **Output Validation Framework**

```python
def validate_singer_output(output_text):
    """Validate Singer-compliant output format."""
    messages = []

    for line in output_text.strip().split('\n'):
        if not line:
            continue

        try:
            msg = json.loads(line)
            messages.append(SingerMessage(**msg))
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON line: {line}")

    # Validate message sequence
    validate_message_sequence(messages)
    return messages

def validate_message_sequence(messages):
    """Validate proper Singer message sequence."""
    msg_types = [msg.type for msg in messages]

    # Must start with SCHEMA messages
    assert msg_types[0] == "SCHEMA"

    # RECORD messages must follow corresponding SCHEMA
    schema_streams = set()
    for msg in messages:
        if msg.type == "SCHEMA":
            schema_streams.add(msg.stream)
        elif msg.type == "RECORD":
            assert msg.stream in schema_streams, f"Record for undeclared stream: {msg.stream}"
```

## Performance E2E Testing

### **Performance Benchmarks**

```python
def test_e2e_performance_benchmarks():
    """Test E2E performance meets requirements."""
    with e2e_performance_environment():
        start_time = time.time()

        # Execute complete workflow
        discovery = run_tap_command(["--config", "perf_config.json", "--discover"])
        extraction = run_tap_command([
            "--config", "perf_config.json",
            "--catalog", "perf_catalog.json"
        ])

        total_time = time.time() - start_time

        # Validate performance requirements
        assert discovery.returncode == 0
        assert extraction.returncode == 0
        assert total_time < 600  # 10 minutes max

        # Validate throughput
        record_count = count_records(extraction.stdout)
        throughput = record_count / total_time
        assert throughput > 100  # 100+ records/second
```

### **Resource Usage Testing**

```python
def test_e2e_resource_usage():
    """Test E2E resource usage within limits."""
    import psutil

    with e2e_mock_environment():
        process = start_tap_process(["--config", "config.json", "--discover"])

        # Monitor resource usage
        max_memory = 0
        max_cpu = 0

        while process.poll() is None:
            proc = psutil.Process(process.pid)
            memory = proc.memory_info().rss / 1024 / 1024  # MB
            cpu = proc.cpu_percent()

            max_memory = max(max_memory, memory)
            max_cpu = max(max_cpu, cpu)

            time.sleep(1)

        # Validate resource limits
        assert max_memory < 512  # 512MB max memory
        assert max_cpu < 80      # 80% max CPU
```

## Error Scenario Testing

### **Network Failure Scenarios**

```python
def test_e2e_network_failures():
    """Test E2E behavior during network failures."""
    with e2e_mock_environment() as env:
        # Start extraction
        process = start_tap_process_async([
            "--config", "config.json",
            "--catalog", "catalog.json"
        ])

        # Simulate network failure mid-extraction
        time.sleep(5)
        env.simulate_network_failure()

        # Wait for completion
        result = process.wait(timeout=300)

        # Validate graceful failure handling
        assert result.returncode != 0
        assert "network" in result.stderr.lower()

        # Validate partial output is valid
        if result.stdout:
            validate_partial_singer_output(result.stdout)
```

### **Configuration Error Testing**

```python
def test_e2e_configuration_errors():
    """Test E2E handling of configuration errors."""
    error_configs = [
        "missing_url.json",
        "invalid_auth.json",
        "wrong_credentials.json",
        "malformed_json.json"
    ]

    for config_file in error_configs:
        result = run_tap_command(["--config", f"error_configs/{config_file}", "--discover"])

        # Validate error handling
        assert result.returncode != 0
        assert result.stderr != ""
        assert "error" in result.stderr.lower()
```

## E2E Re-enabling Plan

### **Phase 1: Mock Environment (Week 1-2)**

- [ ] Create comprehensive E2E mock WMS environment
- [ ] Implement realistic WMS simulation with full API coverage
- [ ] Set up test data management system
- [ ] Create CLI testing framework

### **Phase 2: Core E2E Tests (Week 3)**

- [ ] Re-enable `test_wms_e2e.py` with mock environment
- [ ] Implement discovery workflow E2E tests
- [ ] Add extraction workflow E2E tests
- [ ] Create configuration validation E2E tests

### **Phase 3: Advanced Scenarios (Week 4)**

- [ ] Add error scenario E2E testing
- [ ] Implement performance E2E benchmarks
- [ ] Create stress testing scenarios
- [ ] Add concurrent operation E2E tests

### **Phase 4: Production Validation (Week 5)**

- [ ] Add production-like scenario testing
- [ ] Implement monitoring and observability E2E tests
- [ ] Create deployment validation tests
- [ ] Add regression testing suite

## Quality Standards

### **E2E Test Requirements**

- **Complete Workflows**: Tests cover entire user journeys
- **Singer Compliance**: Full Singer protocol validation
- **Performance**: Tests validate performance requirements
- **Error Handling**: Comprehensive error scenario coverage
- **Reliability**: Tests pass consistently in CI/CD

### **Mock Environment Standards**

- **Realistic Behavior**: Mock environment behaves like real WMS
- **Data Consistency**: Test data represents real-world scenarios
- **Performance**: Mock responses have realistic timing
- **Error Simulation**: Comprehensive error condition simulation

## User Acceptance Scenarios

### **Business User Workflows**

```python
def test_business_user_daily_extraction():
    """Test complete daily extraction workflow for business users."""
    # Business scenario: Daily inventory extraction
    with e2e_business_environment():
        # 1. Discovery phase
        discovery = run_tap_command([
            "--config", "business_config.json",
            "--discover"
        ])
        assert discovery.returncode == 0

        # 2. Extraction phase
        extraction = run_tap_command([
            "--config", "business_config.json",
            "--catalog", "business_catalog.json"
        ])
        assert extraction.returncode == 0

        # 3. Validate business data requirements
        records = parse_singer_records(extraction.stdout)
        validate_business_data_quality(records)
```

---

**Status**: Completely disabled - Requires full reconstruction | **Priority**: High - Critical for user confidence | **Updated**: 2025-08-13
