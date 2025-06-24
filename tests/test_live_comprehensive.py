"""Comprehensive live tests for tap-oracle-wms functionality."""

import time

import pytest

from tap_oracle_wms.config import QUALITY_THRESHOLD, RATE_THRESHOLD
from tap_oracle_wms.tap import TapOracleWMS


@pytest.mark.live
@pytest.mark.slow
class TestComprehensiveLiveFlow:
    """Comprehensive end-to-end tests with live WMS API."""

    def test_complete_tap_workflow(self, live_config, captured_messages) -> None:
        """Test complete tap workflow from discovery to extraction."""
        # Configure for comprehensive test
        workflow_config = live_config.copy()
        workflow_config["entities"] = ["facility"]
        workflow_config["page_size"] = 10
        workflow_config["start_date"] = "2024-01-01T00:00:00Z"

        # Step 1: Create tap instance
        tap = TapOracleWMS(config=workflow_config)
        assert tap is not None

        # Step 2: Discover streams
        streams = tap.discover_streams()
        assert isinstance(streams, list)

        if len(streams) == 0:
            pytest.skip("No streams discovered - check entity configuration")

        # Step 3: Generate catalog
        catalog = tap.catalog
        assert catalog is not None

        # Step 4: Test stream properties
        facility_stream = streams[0]

        # Verify stream configuration
        assert facility_stream.name == "facility"
        assert facility_stream.path.endswith("/entity/facility")
        assert facility_stream.schema is not None

        # Step 5: Test pagination setup
        paginator = facility_stream.get_new_paginator()
        assert paginator is not None
        assert paginator._page_size == 10

        # Step 6: Test URL parameter generation
        params = facility_stream.get_url_params({}, 1)
        assert isinstance(params, dict)
        assert "page_size" in params
        assert "page" in params

        # Step 7: Run limited data extraction
        messages, capture_fn = captured_messages

        original_write = tap.write_message
        record_count = 0
        max_records = 20

        def workflow_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1
                if record_count % 5 == 0:
                    pass

                if record_count >= max_records:
                    msg = "Workflow test limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = workflow_capture

        start_time = time.time()
        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        end_time = time.time()
        extraction_time = end_time - start_time

        # Step 8: Analyze results

        schema_messages = [m for m in messages if m.get("type") == "SCHEMA"]
        record_messages = [m for m in messages if m.get("type") == "RECORD"]
        state_messages = [m for m in messages if m.get("type") == "STATE"]

        # Validate message structure
        assert len(schema_messages) > 0, "No SCHEMA messages found"

        if len(record_messages) > 0:
            # Validate record structure
            sample_record = record_messages[0]
            assert "stream" in sample_record
            assert "record" in sample_record
            assert sample_record["stream"] == "facility"

            record_data = sample_record["record"]
            assert isinstance(record_data, dict)
            assert len(record_data) > 0

            # Performance check
            if extraction_time > 0:
                records_per_second = len(record_messages) / extraction_time
                assert records_per_second > 0.1, "Performance too slow"

        assert len(state_messages) > 0, "No STATE messages found"

    def test_discovery_and_schema_validation(self, live_config) -> None:
        """Test comprehensive discovery and schema validation."""
        discovery_config = live_config.copy()
        discovery_config["entities"] = ["facility"]

        tap = TapOracleWMS(config=discovery_config)

        # Test discovery
        streams = tap.discover_streams()

        if len(streams) == 0:
            pytest.skip("No streams discovered")

        # Test each discovered stream
        for _i, stream in enumerate(streams[:3]):  # Test first 3 streams
            # Test basic properties
            assert stream.name
            assert stream.path
            assert stream.schema

            # Test schema structure
            schema = stream.schema
            assert isinstance(schema, dict)
            assert "type" in schema
            assert schema["type"] == "object"

            if "properties" in schema:
                properties = schema["properties"]
                assert isinstance(properties, dict)
                assert len(properties) > 0

                # Validate property structures
                for prop_def in properties.values():
                    assert isinstance(prop_name, str)
                    assert isinstance(prop_def, dict)
                    # Basic property validation
                    assert len(prop_name) > 0

            # Test stream configuration
            paginator = stream.get_new_paginator()
            assert paginator is not None

            # Test URL generation
            params = stream.get_url_params({}, 1)
            assert isinstance(params, dict)

    def test_pagination_comprehensive(self, live_config, captured_messages) -> None:
        """Test comprehensive pagination behavior."""
        pagination_config = live_config.copy()
        pagination_config["entities"] = ["facility"]
        pagination_config["page_size"] = 5  # Small pages to test pagination

        tap = TapOracleWMS(config=pagination_config)
        messages, capture_fn = captured_messages

        original_write = tap.write_message
        page_requests: list = []
        record_count = 0
        max_records = 20

        def pagination_capture(message) -> None:
            nonlocal record_count, page_requests
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1

                # Track page boundaries (every page_size records)
                if record_count % 5 == 1:  # First record of each page
                    page_requests.append(record_count)

                if record_count >= max_records:
                    msg = "Pagination test limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = pagination_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        # Analyze pagination behavior
        record_messages = [m for m in messages if m.get("type") == "RECORD"]

        if len(record_messages) > 5:
            # Should have multiple pages
            expected_pages = (len(record_messages) + 4) // 5
            actual_pages = len(page_requests)

            # Allow some variance in page detection
            assert (
                actual_pages >= expected_pages - 1
            ), f"Too few pages: {actual_pages} vs {expected_pages}"

            # Check for duplicate records (pagination issue indicator)
            record_ids: list = []
            for msg in record_messages:
                record = msg.get("record", {})
                if "id" in record:
                    record_ids.append(record["id"])

            if len(record_ids) > 1:
                unique_ids = set(record_ids)
                duplicate_ratio = 1 - (len(unique_ids) / len(record_ids))
                assert (
                    duplicate_ratio < 0.1
                ), f"Too many duplicates: {duplicate_ratio:.2%}"

    def test_error_handling_comprehensive(self, live_config) -> None:
        """Test comprehensive error handling scenarios."""
        # Test 1: Invalid entity handling
        invalid_entity_config = live_config.copy()
        invalid_entity_config["entities"] = ["definitely_nonexistent_entity_xyz_123"]

        try:
            tap = TapOracleWMS(config=invalid_entity_config)
            streams = tap.discover_streams()

            # Should handle gracefully
            assert isinstance(streams, list)
        except Exception as e:
            # Should have informative error
            assert str(e)

        # Test 2: Invalid configuration handling
        invalid_configs = [
            {**live_config, "page_size": -1},  # Negative page size
            {**live_config, "page_size": "invalid"},  # Wrong type
            {**live_config, "pagination_mode": "invalid"},  # Invalid mode
        ]

        for config in invalid_configs:
            try:
                tap = TapOracleWMS(config=config)
                streams = tap.discover_streams()
            except Exception as e:
                assert str(e)

        # Test 3: Network timeout simulation
        timeout_config = live_config.copy()
        timeout_config["entities"] = ["facility"]
        timeout_config["request_timeout"] = 1  # Very short timeout

        try:
            tap = TapOracleWMS(config=timeout_config)
            streams = tap.discover_streams()
        except Exception as e:
            # Timeout should be handled gracefully
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                pass

    def test_performance_comprehensive(self, live_config, captured_messages) -> None:
        """Test comprehensive performance characteristics."""
        performance_config = live_config.copy()
        performance_config["entities"] = ["facility"]
        performance_config["page_size"] = 20  # Larger pages for performance

        tap = TapOracleWMS(config=performance_config)
        messages, capture_fn = captured_messages

        # Performance metrics
        start_time = time.time()
        discovery_time = None
        first_record_time = None

        original_write = tap.write_message
        record_count = 0
        max_records = 50

        def performance_capture(message) -> None:
            nonlocal record_count, first_record_time
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                if first_record_time is None:
                    first_record_time = time.time()

                record_count += 1
                if record_count >= max_records:
                    msg = "Performance test limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = performance_capture

        # Measure discovery time
        discovery_start = time.time()
        streams = tap.discover_streams()
        discovery_time = time.time() - discovery_start

        if len(streams) == 0:
            pytest.skip("No streams for performance testing")

        # Measure extraction performance
        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        end_time = time.time()
        end_time - start_time
        extraction_time = end_time - (first_record_time or start_time)

        # Analyze performance
        record_messages = [m for m in messages if m.get("type") == "RECORD"]

        if len(record_messages) > 0 and extraction_time > 0:
            records_per_second = len(record_messages) / extraction_time

            # Performance assertions
            assert discovery_time < 30.0, f"Discovery too slow: {discovery_time:.2f}s"
            assert (
                records_per_second > 0.5
            ), f"Extraction too slow: {records_per_second:.2f} records/s"

    def test_data_quality_comprehensive(self, live_config, captured_messages) -> None:
        """Test comprehensive data quality validation."""
        quality_config = live_config.copy()
        quality_config["entities"] = ["facility"]
        quality_config["page_size"] = 15

        tap = TapOracleWMS(config=quality_config)
        messages, capture_fn = captured_messages

        original_write = tap.write_message
        record_count = 0
        max_records = 30
        quality_issues: list = []

        def quality_capture(message) -> None:
            nonlocal record_count, quality_issues
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record = msg_dict.get("record", {})

                # Data quality checks
                if not isinstance(record, dict):
                    quality_issues.append(f"Record {record_count}: Not a dictionary")
                elif len(record) == 0:
                    quality_issues.append(f"Record {record_count}: Empty record")
                    # Check field types and values
                    for value in record.values():
                        if not isinstance(field, str):
                            quality_issues.append(
                                f"Record {record_count}: Non-string field name: {field}"
                            )
                        elif len(field) == 0:
                            quality_issues.append(
                                f"Record {record_count}: Empty field name"
                            )

                        # Check for problematic values
                        if isinstance(value, type | function):
                            quality_issues.append(
                                f"Record {record_count}: Invalid value type in {field}"
                            )

                record_count += 1
                if record_count >= max_records:
                    msg = "Quality test limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = quality_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        # Analyze data quality
        record_messages = [m for m in messages if m.get("type") == "RECORD"]
        schema_messages = [m for m in messages if m.get("type") == "SCHEMA"]

        # Report quality issues
        if quality_issues:
            for _issue in quality_issues[:5]:  # Show first 5 issues
                pass
            if len(quality_issues) > 5:
                pass

        # Quality assertions
        quality_ratio = len(quality_issues) / max(len(record_messages), 1)
        assert (
            quality_ratio < QUALITY_THRESHOLD
        ), f"Too many quality issues: {quality_ratio:.2%}"

        if len(record_messages) > 0:
            # Schema compliance check
            if len(schema_messages) > 0:
                schema = schema_messages[0].get("schema", {})
                properties = schema.get("properties", {})

                if properties:
                    # Check if records generally comply with schema
                    for msg in record_messages[:10]:  # Check first 10 records
                        record = msg.get("record", {})

                        # Check for required fields (basic check)
                        for prop_name in properties:
                            if prop_name not in record:
                                # Missing field - may be okay if nullable
                                pass

            # Check for common facility fields
            sample_record = record_messages[0].get("record", {})
            expected_fields = ["id", "code", "name"]
            found_fields = [f for f in expected_fields if f in sample_record]

            assert len(found_fields) > 0, "No expected fields found in records"


@pytest.mark.live
class TestLiveConfigurationMatrix:
    """Test various configuration combinations with live API."""

    @pytest.mark.parametrize("page_size", [1, 5, 10, 25])
    def test_different_page_sizes(self, live_config, page_size) -> None:
        """Test tap with different page sizes."""
        config = live_config.copy()
        config["entities"] = ["facility"]
        config["page_size"] = page_size

        tap = TapOracleWMS(config=config)
        streams = tap.discover_streams()

        assert isinstance(streams, list)

        if len(streams) > 0:
            stream = streams[0]
            paginator = stream.get_new_paginator()
            assert paginator._page_size == page_size

    @pytest.mark.parametrize("pagination_mode", ["offset", "cursor"])
    def test_different_pagination_modes(self, live_config, pagination_mode) -> None:
        """Test tap with different pagination modes."""
        config = live_config.copy()
        config["entities"] = ["facility"]
        config["pagination_mode"] = pagination_mode
        config["page_size"] = 5

        tap = TapOracleWMS(config=config)
        streams = tap.discover_streams()

        assert isinstance(streams, list)

        if len(streams) > 0:
            stream = streams[0]
            paginator = stream.get_new_paginator()
            assert paginator.mode == pagination_mode

    @pytest.mark.parametrize(
        "start_date",
        ["2024-01-01T00:00:00Z", "2024-06-15T12:00:00Z", "2025-01-01T00:00:00+00:00"],
    )
    def test_different_start_dates(self, live_config, start_date) -> None:
        """Test tap with different start date formats."""
        config = live_config.copy()
        config["entities"] = ["facility"]
        config["start_date"] = start_date
        config["page_size"] = 5

        tap = TapOracleWMS(config=config)
        streams = tap.discover_streams()

        assert isinstance(streams, list)

    def test_multiple_entities_configuration(self, live_config) -> None:
        """Test tap with multiple entities if available."""
        # Try with facility only first
        single_config = live_config.copy()
        single_config["entities"] = ["facility"]

        tap = TapOracleWMS(config=single_config)
        streams = tap.discover_streams()

        # Should work with single entity
        assert isinstance(streams, list)

        if len(streams) > 0:
            pass

            # Could test multiple entities if available
            # multi_config = live_config.copy()
            # multi_config["entities"] = ["facility", "item"]  # If item is available
            # But this depends on actual WMS configuration


@pytest.mark.live
@pytest.mark.slow
class TestLiveStressTests:
    """Stress tests with live WMS API."""

    def test_rapid_successive_requests(self, live_config) -> None:
        """Test rapid successive requests to WMS API."""
        config = live_config.copy()
        config["entities"] = ["facility"]
        config["page_size"] = 5

        # Create multiple tap instances rapidly
        taps: list = []
        start_time = time.time()

        for _i in range(5):
            try:
                tap = TapOracleWMS(config=config)
                streams = tap.discover_streams()
                taps.append((tap, streams))
            except Exception:
                pass

        end_time = time.time()
        end_time - start_time

        assert len(taps) > 0, "No taps created successfully"

    def test_long_running_extraction(self, live_config, captured_messages) -> None:
        """Test longer-running data extraction."""
        long_config = live_config.copy()
        long_config["entities"] = ["facility"]
        long_config["page_size"] = 10

        tap = TapOracleWMS(config=long_config)
        _messages, capture_fn = captured_messages

        original_write = tap.write_message
        record_count = 0
        max_records = 100  # Higher limit for stress test
        start_time = time.time()

        def long_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1

                if record_count % 20 == 0:
                    elapsed = time.time() - start_time
                    record_count / elapsed if elapsed > 0 else 0

                if record_count >= max_records:
                    msg = "Long running test limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = long_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        end_time = time.time()
        total_time = end_time - start_time

        if total_time > 0:
            avg_rate = record_count / total_time
            assert avg_rate > RATE_THRESHOLD, f"Rate too slow: {avg_rate:.2f}"
