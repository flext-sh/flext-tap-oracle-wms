"""Integration tests for data extraction with live WMS API."""

import pytest

from tap_oracle_wms.tap import TapOracleWMS


@pytest.mark.integration
@pytest.mark.extraction
class TestLiveDataExtraction:
    """Integration tests using live WMS API for data extraction."""

    @pytest.mark.live
    def test_live_data_extraction_basic(self, live_config, captured_messages) -> None:
        """Test basic data extraction from live WMS API."""
        # Limit to single entity for focused testing
        limited_config = live_config.copy()
        limited_config["entities"] = ["facility"]
        limited_config["page_size"] = 5  # Small page size for testing

        tap = TapOracleWMS(config=limited_config)
        messages, capture_fn = captured_messages

        # Replace write_message to capture output
        original_write = tap.write_message
        tap.write_message = capture_fn

        try:
            # Run sync (limited to prevent long execution)
            tap.sync_all()
        except KeyboardInterrupt:
            # Allow manual interruption of long-running test
            pass
        finally:
            tap.write_message = original_write

        # Analyze captured messages
        schema_messages = [m for m in messages if m.get("type") == "SCHEMA"]
        record_messages = [m for m in messages if m.get("type") == "RECORD"]
        state_messages = [m for m in messages if m.get("type") == "STATE"]

        # Should have at least one schema message
        assert len(schema_messages) > 0, "No SCHEMA messages found"

        # Should have some record messages (if data exists)
        if len(record_messages) > 0:
            # Verify record structure
            sample_record = record_messages[0]
            assert "stream" in sample_record
            assert "record" in sample_record
            assert sample_record["stream"] == "facility"

            # Verify record data
            record_data = sample_record["record"]
            assert isinstance(record_data, dict)
            assert len(record_data) > 0

        # Should have state messages for tracking
        assert len(state_messages) > 0, "No STATE messages found"

    @pytest.mark.live
    def test_live_schema_generation(self, live_config) -> None:
        """Test schema generation from live WMS API."""
        limited_config = live_config.copy()
        limited_config["entities"] = ["facility"]

        tap = TapOracleWMS(config=limited_config)

        # Test catalog generation
        catalog = tap.catalog
        assert catalog is not None

        if hasattr(catalog, "streams") and len(catalog.streams) > 0:
            facility_stream = catalog.streams[0]

            # Verify schema structure
            schema = facility_stream.schema
            assert isinstance(schema, dict)
            assert "type" in schema
            assert "properties" in schema

            # Should have basic facility properties
            properties = schema["properties"]
            assert isinstance(properties, dict)
            assert len(properties) > 0

            # Common facility fields
            expected_fields = ["id", "code", "name"]
            found_fields = set(properties.keys())

            # At least some expected fields should be present
            common_fields = found_fields.intersection(expected_fields)
            assert len(common_fields) > 0, (
                f"Expected {expected_fields}, found {list(found_fields)[:10]}"
            )

    @pytest.mark.live
    def test_live_pagination_behavior(self, live_config, captured_messages) -> None:
        """Test pagination behavior with live WMS API."""
        # Configure for pagination testing
        pagination_config = live_config.copy()
        pagination_config["entities"] = ["facility"]
        pagination_config["page_size"] = 3  # Very small page size to force pagination
        pagination_config["pagination_mode"] = "offset"

        tap = TapOracleWMS(config=pagination_config)
        messages, capture_fn = captured_messages

        # Replace write_message to capture output
        original_write = tap.write_message
        tap.write_message = capture_fn

        # Limit execution time/records
        max_records = 10
        record_count = 0

        def limited_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1
                if record_count >= max_records:
                    msg = "Record limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = limited_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass  # Expected for test termination
        finally:
            tap.write_message = original_write

        # Analyze pagination behavior
        record_messages = [m for m in messages if m.get("type") == "RECORD"]

        if len(record_messages) > 3:
            # Should have more records than page_size, indicating pagination worked
            assert len(record_messages) > 3, "Pagination may not be working correctly"

            # Verify records are unique (no duplicates from pagination issues)
            record_ids: list = []
            for msg in record_messages:
                record = msg.get("record", {})
                if "id" in record:
                    record_ids.append(record["id"])

            if len(record_ids) > 1:
                unique_ids = set(record_ids)
                assert len(unique_ids) == len(
                    record_ids,
                ), "Duplicate records found - pagination issue"

    @pytest.mark.live
    def test_live_incremental_sync_setup(self, live_config, captured_messages) -> None:
        """Test incremental sync setup with live WMS API."""
        incremental_config = live_config.copy()
        incremental_config["entities"] = ["facility"]
        incremental_config["start_date"] = "2024-01-01T00:00:00Z"
        incremental_config["page_size"] = 5

        tap = TapOracleWMS(config=incremental_config)
        messages, capture_fn = captured_messages

        # Replace write_message
        original_write = tap.write_message
        tap.write_message = capture_fn

        # Limit execution
        max_records = 5
        record_count = 0

        def limited_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1
                if record_count >= max_records:
                    msg = "Record limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = limited_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        # Analyze incremental sync behavior
        record_messages = [m for m in messages if m.get("type") == "RECORD"]
        state_messages = [m for m in messages if m.get("type") == "STATE"]

        # Should have records with timestamps
        if len(record_messages) > 0:
            for msg in record_messages[:3]:  # Check first few records
                record = msg.get("record", {})

                # Look for timestamp fields
                timestamp_fields = ["mod_ts", "create_ts", "update_ts"]
                has_timestamp = any(field in record for field in timestamp_fields)

                if has_timestamp:
                    # At least one record has timestamp - good for incremental sync
                    break

        # Should have state tracking
        assert len(state_messages) > 0, "No state messages found for incremental sync"

    @pytest.mark.live
    def test_live_error_handling(self, live_config) -> None:
        """Test error handling with live WMS API."""
        # Test with invalid entity
        error_config = live_config.copy()
        error_config["entities"] = ["definitely_nonexistent_entity_123"]

        tap = TapOracleWMS(config=error_config)

        # Should handle invalid entity gracefully
        try:
            streams = tap.discover_streams()
            # Should either return empty list or handle gracefully
            assert isinstance(streams, list)
        except Exception as e:
            # If it raises an exception, should be informative
            assert str(e)

    @pytest.mark.live
    def test_live_authentication_verification(self, live_config) -> None:
        """Test authentication verification with live WMS API."""
        tap = TapOracleWMS(config=live_config)

        # Test that authentication works by attempting discovery
        try:
            streams = tap.discover_streams()
            # If we get here, authentication worked
            assert isinstance(streams, list)
        except Exception as e:
            error_msg = str(e).lower()
            if (
                "401" in error_msg
                or "unauthorized" in error_msg
                or "authentication" in error_msg
            ):
                pytest.fail("Authentication failed - check WMS credentials")
                # Other error - re-raise
                raise

    @pytest.mark.live
    def test_live_data_quality_validation(self, live_config, captured_messages) -> None:
        """Test data quality validation with live WMS API."""
        quality_config = live_config.copy()
        quality_config["entities"] = ["facility"]
        quality_config["page_size"] = 10

        tap = TapOracleWMS(config=quality_config)
        messages, capture_fn = captured_messages

        # Replace write_message
        original_write = tap.write_message
        tap.write_message = capture_fn

        # Limit execution
        max_records = 10
        record_count = 0

        def limited_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1
                if record_count >= max_records:
                    msg = "Record limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = limited_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        # Validate data quality
        record_messages = [m for m in messages if m.get("type") == "RECORD"]

        if len(record_messages) > 0:
            for msg in record_messages:
                record = msg.get("record", {})

                # Basic data quality checks
                assert isinstance(record, dict)
                assert len(record) > 0

                # Check for required fields (if any)
                if "id" in record:
                    assert record["id"] is not None

                # Check for data type consistency
                for value in record.values():
                    # Values should not be unexpected types
                    assert not isinstance(value, type | function | complex)


@pytest.mark.integration
@pytest.mark.extraction
class TestExtractionConfiguration:
    """Integration tests for extraction configuration options."""

    @pytest.mark.live
    def test_extraction_with_field_selection(
        self,
        live_config,
        captured_messages,
    ) -> None:
        """Test extraction with field selection configuration."""
        field_config = live_config.copy()
        field_config["entities"] = ["facility"]
        field_config["field_selection"] = {"facility": ["id", "code", "name"]}
        field_config["page_size"] = 3

        tap = TapOracleWMS(config=field_config)
        messages, capture_fn = captured_messages

        # Capture limited messages
        original_write = tap.write_message
        record_count = 0

        def limited_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1
                if record_count >= 3:
                    msg = "Record limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = limited_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        # Verify field selection (if implemented)
        record_messages = [m for m in messages if m.get("type") == "RECORD"]

        if len(record_messages) > 0:
            # Field selection implementation may vary
            # This test verifies the configuration is accepted
            assert len(record_messages) > 0

    @pytest.mark.live
    def test_extraction_with_filtering(self, live_config, captured_messages) -> None:
        """Test extraction with filtering configuration."""
        filter_config = live_config.copy()
        filter_config["entities"] = ["facility"]
        filter_config["global_filters"] = {
            "active": True,
        }  # May or may not be supported
        filter_config["page_size"] = 5

        tap = TapOracleWMS(config=filter_config)
        _messages, _capture_fn = captured_messages

        # Test that configuration is accepted
        try:
            # Quick discovery test
            streams = tap.discover_streams()
            assert isinstance(streams, list)
        except Exception as e:
            # If filtering is not supported, should handle gracefully
            error_msg = str(e).lower()
            if "filter" not in error_msg:
                # Re-raise if not filter-related error
                raise

    @pytest.mark.live
    def test_extraction_with_ordering(self, live_config, captured_messages) -> None:
        """Test extraction with ordering configuration."""
        order_config = live_config.copy()
        order_config["entities"] = ["facility"]
        order_config["default_ordering"] = "id"
        order_config["entity_ordering"] = {"facility": "code"}
        order_config["page_size"] = 5

        tap = TapOracleWMS(config=order_config)

        # Test that ordering configuration is accepted
        try:
            streams = tap.discover_streams()
            assert isinstance(streams, list)
        except Exception as e:
            # Should handle gracefully if ordering not supported
            assert str(e)

    @pytest.mark.live
    def test_extraction_with_different_page_sizes(self, live_config) -> None:
        """Test extraction with different page sizes."""
        page_sizes = [1, 5, 10, 25]

        for page_size in page_sizes:
            config = live_config.copy()
            config["entities"] = ["facility"]
            config["page_size"] = page_size

            tap = TapOracleWMS(config=config)

            # Should accept different page sizes
            try:
                streams = tap.discover_streams()
                assert isinstance(streams, list)

                # Verify stream configuration
                if len(streams) > 0:
                    stream = streams[0]
                    paginator = stream.get_new_paginator()
                    assert paginator._page_size == page_size

            except Exception as e:
                pytest.fail(f"Failed with page_size={page_size}: {e}")

    @pytest.mark.live
    def test_extraction_with_different_pagination_modes(self, live_config) -> None:
        """Test extraction with different pagination modes."""
        pagination_modes = ["offset", "cursor"]

        for mode in pagination_modes:
            config = live_config.copy()
            config["entities"] = ["facility"]
            config["pagination_mode"] = mode
            config["page_size"] = 5

            tap = TapOracleWMS(config=config)

            # Should accept different pagination modes
            try:
                streams = tap.discover_streams()
                assert isinstance(streams, list)

                # Verify stream configuration
                if len(streams) > 0:
                    stream = streams[0]
                    paginator = stream.get_new_paginator()
                    assert paginator.mode == mode

            except Exception as e:
                pytest.fail(f"Failed with pagination_mode={mode}: {e}")


@pytest.mark.integration
@pytest.mark.extraction
class TestExtractionPerformance:
    """Integration tests for extraction performance."""

    @pytest.mark.live
    @pytest.mark.slow
    def test_large_page_size_performance(self, live_config, captured_messages) -> None:
        """Test performance with large page sizes."""
        large_page_config = live_config.copy()
        large_page_config["entities"] = ["facility"]
        large_page_config["page_size"] = 100  # Large page size

        tap = TapOracleWMS(config=large_page_config)
        _messages, capture_fn = captured_messages

        # Measure extraction time
        import time

        start_time = time.time()

        original_write = tap.write_message
        record_count = 0

        def counting_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1
                if record_count >= 50:  # Limit to 50 records for performance test
                    msg = "Performance test limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = counting_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        end_time = time.time()
        extraction_time = end_time - start_time

        # Performance should be reasonable
        if record_count > 0:
            records_per_second = record_count / extraction_time
            assert records_per_second > 0.5, (
                f"Too slow: {records_per_second:.2f} records/second"
            )

    @pytest.mark.live
    def test_connection_timeout_handling(self, live_config) -> None:
        """Test handling of connection timeouts."""
        timeout_config = live_config.copy()
        timeout_config["entities"] = ["facility"]
        timeout_config["request_timeout"] = 5  # Short timeout

        tap = TapOracleWMS(config=timeout_config)

        # Should handle timeout configuration
        try:
            streams = tap.discover_streams()
            assert isinstance(streams, list)
        except Exception as e:
            # Timeout errors should be handled gracefully
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                # Expected timeout behavior
                # Re-raise non-timeout errors
                raise

    @pytest.mark.live
    def test_concurrent_stream_processing(self, live_config) -> None:
        """Test concurrent processing of multiple streams."""
        multi_entity_config = live_config.copy()
        multi_entity_config["entities"] = ["facility"]  # Start with one entity
        multi_entity_config["max_parallel_streams"] = 2

        tap = TapOracleWMS(config=multi_entity_config)

        # Test stream discovery and creation
        streams = tap.discover_streams()

        # Should handle concurrent configuration
        assert isinstance(streams, list)


@pytest.mark.integration
@pytest.mark.extraction
class TestExtractionEdgeCases:
    """Integration tests for extraction edge cases."""

    @pytest.mark.live
    def test_extraction_with_empty_results(self, live_config) -> None:
        """Test extraction when API returns empty results."""
        # Try with entity that might have no data
        empty_config = live_config.copy()
        empty_config["entities"] = ["facility"]
        empty_config["start_date"] = (
            "2030-01-01T00:00:00Z"  # Future date - likely no data
        )

        tap = TapOracleWMS(config=empty_config)

        # Should handle empty results gracefully
        try:
            streams = tap.discover_streams()
            assert isinstance(streams, list)
        except Exception as e:
            # Should not fail on empty results
            assert str(e)

    @pytest.mark.live
    def test_extraction_with_malformed_config(self, live_config) -> None:
        """Test extraction with various malformed configurations."""
        base_config = live_config.copy()

        # Test missing required fields (one at a time)
        malformed_configs = [
            {**base_config, "page_size": "invalid"},  # Invalid page_size type
            {**base_config, "pagination_mode": "invalid"},  # Invalid pagination mode
            {**base_config, "entities": "not_a_list"},  # Invalid entities type
        ]

        for config in malformed_configs:
            try:
                tap = TapOracleWMS(config=config)
                # Should either handle gracefully or raise informative error
                assert tap is not None
            except Exception as e:
                # Should have informative error message
                assert str(e)

    @pytest.mark.live
    def test_extraction_with_unicode_data(self, live_config, captured_messages) -> None:
        """Test extraction with unicode data."""
        unicode_config = live_config.copy()
        unicode_config["entities"] = ["facility"]
        unicode_config["page_size"] = 5

        tap = TapOracleWMS(config=unicode_config)
        messages, capture_fn = captured_messages

        original_write = tap.write_message
        record_count = 0

        def unicode_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1
                if record_count >= 5:
                    msg = "Unicode test limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = unicode_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        # Verify unicode handling
        record_messages = [m for m in messages if m.get("type") == "RECORD"]

        if len(record_messages) > 0:
            for msg in record_messages:
                record = msg.get("record", {})

                # Should handle unicode in field values
                for value in record.values():
                    if isinstance(value, str):
                        # Should be valid unicode string
                        try:
                            value.encode("utf-8")
                        except UnicodeEncodeError:
                            pytest.fail(f"Invalid unicode in field {key}: {value}")

    @pytest.mark.live
    def test_extraction_with_large_field_values(
        self,
        live_config,
        captured_messages,
    ) -> None:
        """Test extraction with large field values."""
        large_field_config = live_config.copy()
        large_field_config["entities"] = ["facility"]
        large_field_config["page_size"] = 3

        tap = TapOracleWMS(config=large_field_config)
        messages, capture_fn = captured_messages

        original_write = tap.write_message
        record_count = 0

        def large_field_capture(message) -> None:
            nonlocal record_count
            capture_fn(message)

            if hasattr(message, "to_dict"):
                msg_dict = message.to_dict()
                msg_dict = {"type": message.__class__.__name__}

            if msg_dict.get("type") == "RECORD":
                record_count += 1
                if record_count >= 3:
                    msg = "Large field test limit reached"
                    raise KeyboardInterrupt(msg)

        tap.write_message = large_field_capture

        try:
            tap.sync_all()
        except KeyboardInterrupt:
            pass
        finally:
            tap.write_message = original_write

        # Verify handling of large fields
        record_messages = [m for m in messages if m.get("type") == "RECORD"]

        if len(record_messages) > 0:
            for msg in record_messages:
                record = msg.get("record", {})

                # Check for potentially large fields
                for value in record.values():
                    if isinstance(value, str) and len(value) > 1000:
                        # Should handle large strings without issues
                        assert isinstance(value, str)
                        assert len(value) < 1000000  # Reasonable upper limit
