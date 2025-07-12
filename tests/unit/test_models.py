"""Unit tests for models module."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from datetime import UTC
from datetime import datetime

import pytest
from pydantic import HttpUrl
from pydantic import ValidationError

from flext_tap_oracle_wms.models import FlextConstants
from flext_tap_oracle_wms.models import TapMetrics
from flext_tap_oracle_wms.models import WMSConfig
from flext_tap_oracle_wms.models import WMSDiscoveryResult
from flext_tap_oracle_wms.models import WMSEntity
from flext_tap_oracle_wms.models import WMSError
from flext_tap_oracle_wms.models import WMSRecord
from flext_tap_oracle_wms.models import WMSStreamMetadata

# Rebuild models to handle forward references
WMSConfig.model_rebuild()
WMSEntity.model_rebuild()
WMSStreamMetadata.model_rebuild()
WMSError.model_rebuild()
WMSRecord.model_rebuild()
WMSDiscoveryResult.model_rebuild()
TapMetrics.model_rebuild()


class TestFlextConstants:
    """Test FlextConstants."""

    def test_constants_values(self) -> None:
        """Test constant values are properly defined."""
        assert FlextConstants.MAX_ENTITY_NAME_LENGTH == 255
        assert FlextConstants.MAX_ERROR_MESSAGE_LENGTH == 1000
        assert FlextConstants.DEFAULT_TIMEOUT == 30
        assert FlextConstants.FRAMEWORK_VERSION == "0.7.0"


class TestWMSConfig:
    """Test WMSConfig model."""

    def test_minimal_config(self) -> None:
        """Test minimal valid configuration."""
        config = WMSConfig(
            base_url=HttpUrl("https://wms.example.com"),
            username="test_user",
            password="test_pass",
        )

        assert str(config.base_url) == "https://wms.example.com/"
        assert config.username == "test_user"
        assert config.password == "test_pass"
        assert config.company_code == "*"
        assert config.facility_code == "*"
        assert config.page_size == 500
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.auto_discover is True
        assert config.include_metadata is True

    def test_full_config(self) -> None:
        """Test full configuration with all fields."""
        config = WMSConfig(
            base_url=HttpUrl("https://wms.enterprise.com"),
            username="admin_user",
            password="secure_pass",
            company_code="COMP1",
            facility_code="FAC1",
            page_size=1000,
            timeout=60,
            max_retries=5,
            auto_discover=False,
            include_metadata=False,
        )

        assert str(config.base_url) == "https://wms.enterprise.com/"
        assert config.username == "admin_user"
        assert config.company_code == "COMP1"
        assert config.facility_code == "FAC1"
        assert config.page_size == 1000
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.auto_discover is False
        assert config.include_metadata is False

    def test_base_url_validation(self) -> None:
        """Test base URL validation."""
        # Valid URLs
        for url in ["https://test.com", "http://test.com"]:
            config = WMSConfig(
                base_url=HttpUrl(url),
                username="user",
                password="pass",
            )
            assert url in str(config.base_url)

        # Invalid URL should fail
        with pytest.raises(ValidationError):
            WMSConfig(
                base_url=HttpUrl("invalid-url"),
                username="user",
                password="pass",
            )

    def test_page_size_validation(self) -> None:
        """Test page size validation."""
        # Valid page size
        config = WMSConfig(
            base_url=HttpUrl("https://test.com"),
            username="user",
            password="pass",
            page_size=100,
        )
        assert config.page_size == 100

        # Invalid page sizes
        with pytest.raises(ValidationError):
            WMSConfig(
                base_url=HttpUrl("https://test.com"),
                username="user",
                password="pass",
                page_size=0,
            )

        with pytest.raises(ValidationError):
            WMSConfig(
                base_url=HttpUrl("https://test.com"),
                username="user",
                password="pass",
                page_size=20000,
            )

    def test_timeout_validation(self) -> None:
        """Test timeout validation."""
        # Valid timeout
        config = WMSConfig(
            base_url=HttpUrl("https://test.com"),
            username="user",
            password="pass",
            timeout=60,
        )
        assert config.timeout == 60

        # Invalid timeouts
        with pytest.raises(ValidationError):
            WMSConfig(
                base_url=HttpUrl("https://test.com"),
                username="user",
                password="pass",
                timeout=0,
            )

        with pytest.raises(ValidationError):
            WMSConfig(
                base_url=HttpUrl("https://test.com"),
                username="user",
                password="pass",
                timeout=400,
            )

    def test_required_fields(self) -> None:
        """Test required field validation."""
        # Missing base_url
        with pytest.raises(ValidationError):
            WMSConfig(username="user", password="pass")  # type: ignore[call-arg]

        # Missing username
        with pytest.raises(ValidationError):
            WMSConfig(base_url=HttpUrl("https://test.com"), password="pass")  # type: ignore[call-arg]

        # Missing password
        with pytest.raises(ValidationError):
            WMSConfig(base_url=HttpUrl("https://test.com"), username="user")  # type: ignore[call-arg]


class TestWMSEntity:
    """Test WMSEntity model."""

    def test_minimal_entity(self) -> None:
        """Test minimal entity creation."""
        entity = WMSEntity(
            name="item",
            description=None,
            endpoint="/entity/item",
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )

        assert entity.name == "item"
        assert entity.endpoint == "/entity/item"
        assert entity.description is None
        assert entity.supports_incremental is False
        assert entity.primary_key is None
        assert entity.timestamp_field is None
        assert entity.fields == []
        assert entity.total_records is None

    def test_full_entity(self) -> None:
        """Test full entity with all fields."""
        entity = WMSEntity(
            name="allocation",
            description="Allocation master data",
            endpoint="/entity/allocation",
            supports_incremental=True,
            primary_key="alloc_id",
            timestamp_field="mod_ts",
            fields=["alloc_id", "item_id", "location", "mod_ts"],
            total_records=1500,
        )

        assert entity.name == "allocation"
        assert entity.endpoint == "/entity/allocation"
        assert entity.description == "Allocation master data"
        assert entity.supports_incremental is True
        assert entity.primary_key == "alloc_id"
        assert entity.timestamp_field == "mod_ts"
        assert entity.fields == ["alloc_id", "item_id", "location", "mod_ts"]
        assert entity.total_records == 1500

    def test_name_validation(self) -> None:
        """Test entity name validation."""
        # Valid name
        entity = WMSEntity(
            name="item",
            description=None,
            endpoint="/test",
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )
        assert entity.name == "item"

        # Invalid names
        with pytest.raises(ValidationError):
            WMSEntity(
                name="",
                description=None,
                endpoint="/test",
                primary_key=None,
                timestamp_field=None,
                total_records=None,
            )

        # Name too long
        with pytest.raises(ValidationError):
            WMSEntity(
                name="x" * 300,
                description=None,
                endpoint="/test",
                primary_key=None,
                timestamp_field=None,
                total_records=None,
            )

    def test_total_records_validation(self) -> None:
        """Test total records validation."""
        # Valid record count
        entity = WMSEntity(
            name="test",
            description=None,
            endpoint="/test",
            primary_key=None,
            timestamp_field=None,
            total_records=100,
        )
        assert entity.total_records == 100

        # Invalid record count
        with pytest.raises(ValidationError):
            WMSEntity(
                name="test",
                description=None,
                endpoint="/test",
                primary_key=None,
                timestamp_field=None,
                total_records=-1,
            )


class TestWMSStreamMetadata:
    """Test WMSStreamMetadata model."""

    def test_default_metadata(self) -> None:
        """Test default stream metadata."""
        metadata = WMSStreamMetadata(stream_name="item", replication_key=None)

        assert metadata.stream_name == "item"
        assert metadata.key_properties == []
        assert metadata.replication_method == "FULL_TABLE"
        assert metadata.replication_key is None
        assert metadata.json_schema == {}
        assert metadata.metadata == {}

    def test_full_metadata(self) -> None:
        """Test full stream metadata."""
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "code": {"type": "string"},
            },
        }
        meta = {"inclusion": "available"}

        metadata = WMSStreamMetadata(
            stream_name="allocation",
            key_properties=["alloc_id", "facility_code"],
            replication_method="INCREMENTAL",
            replication_key="mod_ts",
            json_schema=schema,
            metadata=meta,
        )

        assert metadata.stream_name == "allocation"
        assert metadata.key_properties == ["alloc_id", "facility_code"]
        assert metadata.replication_method == "INCREMENTAL"
        assert metadata.replication_key == "mod_ts"
        assert metadata.json_schema == schema
        assert metadata.metadata == meta

    def test_stream_name_validation(self) -> None:
        """Test stream name validation."""
        # Valid name
        metadata = WMSStreamMetadata(stream_name="item", replication_key=None)
        assert metadata.stream_name == "item"

        # Invalid names
        with pytest.raises(ValidationError):
            WMSStreamMetadata(stream_name="", replication_key=None)

        with pytest.raises(ValidationError):
            WMSStreamMetadata(stream_name="x" * 300, replication_key=None)


class TestWMSRecord:
    """Test WMSRecord model."""

    def test_basic_record(self) -> None:
        """Test basic record creation."""
        now = datetime.now(UTC)
        record = WMSRecord(
            stream_name="item",
            record_data={"id": 1, "code": "ITEM001"},
            extracted_at=now,
            source_endpoint="/entity/item",
            record_id=None,
            page_number=None,
        )

        assert record.stream_name == "item"
        assert record.record_data == {"id": 1, "code": "ITEM001"}
        assert record.extracted_at == now
        assert record.source_endpoint == "/entity/item"
        assert record.record_id is None
        assert record.page_number is None

    def test_full_record(self) -> None:
        """Test full record with all fields."""
        now = datetime.now(UTC)
        record = WMSRecord(
            stream_name="allocation",
            record_data={"alloc_id": "A001", "item_id": "ITEM001"},
            extracted_at=now,
            source_endpoint="/entity/allocation",
            record_id="A001",
            page_number=2,
        )

        assert record.stream_name == "allocation"
        assert record.record_data == {"alloc_id": "A001", "item_id": "ITEM001"}
        assert record.record_id == "A001"
        assert record.page_number == 2

    def test_record_data_validation(self) -> None:
        """Test record data validation."""
        now = datetime.now(UTC)

        # Valid record data
        record = WMSRecord(
            stream_name="item",
            record_data={"id": 1},
            extracted_at=now,
            source_endpoint="/test",
            record_id=None,
            page_number=None,
        )
        assert record.record_data == {"id": 1}

        # Empty record data should fail
        with pytest.raises(ValidationError):
            WMSRecord(
                stream_name="item",
                record_data={},
                extracted_at=now,
                source_endpoint="/test",
                record_id=None,
                page_number=None,
            )

    def test_page_number_validation(self) -> None:
        """Test page number validation."""
        now = datetime.now(UTC)

        # Valid page number
        record = WMSRecord(
            stream_name="item",
            record_data={"id": 1},
            extracted_at=now,
            source_endpoint="/test",
            record_id=None,
            page_number=1,
        )
        assert record.page_number == 1

        # Invalid page number
        with pytest.raises(ValidationError):
            WMSRecord(
                stream_name="item",
                record_data={"id": 1},
                extracted_at=now,
                source_endpoint="/test",
                record_id=None,
                page_number=0,
            )


class TestWMSError:
    """Test WMSError model."""

    def test_basic_error(self) -> None:
        """Test basic error creation."""
        now = datetime.now(UTC)
        error = WMSError(
            error_type="authentication",
            message="Invalid credentials",
            timestamp=now,
            endpoint=None,
            status_code=None,
            request_id=None,
        )

        assert error.error_type == "authentication"
        assert error.message == "Invalid credentials"
        assert error.timestamp == now
        assert error.endpoint is None
        assert error.status_code is None
        assert error.retryable is False
        assert error.request_id is None
        assert error.details == {}

    def test_full_error(self) -> None:
        """Test full error with all fields."""
        now = datetime.now(UTC)
        details = {"auth_method": "basic", "retry_count": 3}

        error = WMSError(
            error_type="network",
            message="Connection timeout",
            timestamp=now,
            endpoint="/entity/item",
            status_code=500,
            retryable=True,
            request_id="req-123",
            details=details,
        )

        assert error.error_type == "network"
        assert error.message == "Connection timeout"
        assert error.endpoint == "/entity/item"
        assert error.status_code == 500
        assert error.retryable is True
        assert error.request_id == "req-123"
        assert error.details == details

    def test_status_code_validation(self) -> None:
        """Test status code validation."""
        now = datetime.now(UTC)

        # Valid status codes
        for status in [200, 404, 500]:
            error = WMSError(
                error_type="http",
                message="Test error",
                timestamp=now,
                endpoint=None,
                status_code=status,
                request_id=None,
            )
            assert error.status_code == status

        # Invalid status codes
        for invalid_status in [99, 600]:
            with pytest.raises(ValidationError):
                WMSError(
                    error_type="http",
                    message="Test error",
                    timestamp=now,
                    endpoint=None,
                    status_code=invalid_status,
                    request_id=None,
                )

    def test_message_length_validation(self) -> None:
        """Test message length validation."""
        now = datetime.now(UTC)

        # Valid message
        error = WMSError(
            error_type="test",
            message="Valid message",
            timestamp=now,
            endpoint=None,
            status_code=None,
            request_id=None,
        )
        assert error.message == "Valid message"

        # Message too long
        with pytest.raises(ValidationError):
            WMSError(
                error_type="test",
                message="x" * 1500,
                timestamp=now,
                endpoint=None,
                status_code=None,
                request_id=None,
            )


class TestWMSDiscoveryResult:
    """Test WMSDiscoveryResult model."""

    def test_empty_discovery(self) -> None:
        """Test empty discovery result."""
        now = datetime.now(UTC)
        result = WMSDiscoveryResult(
            discovered_at=now,
            base_url="https://wms.example.com",
            duration_seconds=None,
        )

        assert result.discovered_at == now
        assert result.base_url == "https://wms.example.com"
        assert result.total_entities == 0
        assert result.entities == []
        assert result.errors == []
        assert result.success is True
        assert result.duration_seconds is None

    def test_discovery_with_entities(self) -> None:
        """Test discovery result with entities."""
        now = datetime.now(UTC)

        entity1 = WMSEntity(
            name="item",
            description=None,
            endpoint="/entity/item",
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )
        entity2 = WMSEntity(
            name="location",
            description=None,
            endpoint="/entity/location",
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )

        result = WMSDiscoveryResult(
            discovered_at=now,
            base_url="https://wms.example.com",
            total_entities=2,
            entities=[entity1, entity2],
            duration_seconds=1.5,
        )

        assert result.total_entities == 2
        assert len(result.entities) == 2
        assert result.entities[0].name == "item"
        assert result.entities[1].name == "location"
        assert result.duration_seconds == 1.5

    def test_discovery_with_errors(self) -> None:
        """Test discovery result with errors."""
        now = datetime.now(UTC)

        error = WMSError(
            error_type="network",
            message="Connection failed",
            timestamp=now,
            endpoint=None,
            status_code=None,
            request_id=None,
        )

        result = WMSDiscoveryResult(
            discovered_at=now,
            base_url="https://wms.example.com",
            errors=[error],
            duration_seconds=None,
        )

        assert len(result.errors) == 1
        assert result.errors[0].error_type == "network"

    def test_successful_entities_property(self) -> None:
        """Test successful_entities property."""
        now = datetime.now(UTC)

        entity1 = WMSEntity(
            name="item",
            description=None,
            endpoint="/entity/item",
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )
        entity2 = WMSEntity(
            name="location",
            description=None,
            endpoint="/entity/location",
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )

        result = WMSDiscoveryResult(
            discovered_at=now,
            base_url="https://wms.example.com",
            entities=[entity1, entity2],
            duration_seconds=None,
        )

        successful = result.successful_entities
        assert len(successful) == 2
        assert all(entity.name for entity in successful)

    def test_failed_count_property(self) -> None:
        """Test failed_count property."""
        now = datetime.now(UTC)

        error1 = WMSError(
            error_type="auth",
            message="Failed",
            timestamp=now,
            endpoint=None,
            status_code=None,
            request_id=None,
        )
        error2 = WMSError(
            error_type="network",
            message="Failed",
            timestamp=now,
            endpoint=None,
            status_code=None,
            request_id=None,
        )

        result = WMSDiscoveryResult(
            discovered_at=now,
            base_url="https://wms.example.com",
            errors=[error1, error2],
            duration_seconds=None,
        )

        assert result.failed_count == 2

    def test_add_entity_method(self) -> None:
        """Test add_entity method."""
        now = datetime.now(UTC)

        result = WMSDiscoveryResult(
            discovered_at=now,
            base_url="https://wms.example.com",
            duration_seconds=None,
        )

        entity = WMSEntity(
            name="item",
            description=None,
            endpoint="/entity/item",
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )
        result.add_entity(entity)

        assert result.total_entities == 1
        assert len(result.entities) == 1
        assert result.entities[0] == entity

    def test_add_error_method(self) -> None:
        """Test add_error method."""
        now = datetime.now(UTC)

        result = WMSDiscoveryResult(
            discovered_at=now,
            base_url="https://wms.example.com",
            duration_seconds=None,
        )

        # Add non-critical error
        error1 = WMSError(
            error_type="warning",
            message="Warning",
            timestamp=now,
            endpoint=None,
            status_code=None,
            request_id=None,
        )
        result.add_error(error1)

        assert len(result.errors) == 1
        assert result.success is True  # Still successful

        # Add critical error
        error2 = WMSError(
            error_type="authentication",
            message="Auth failed",
            timestamp=now,
            endpoint=None,
            status_code=None,
            request_id=None,
        )
        result.add_error(error2)

        assert len(result.errors) == 2
        assert result.success is False  # Now failed


class TestTapMetrics:
    """Test TapMetrics model."""

    def test_default_metrics(self) -> None:
        """Test default metrics initialization."""
        metrics = TapMetrics(start_time=None)

        assert metrics.api_calls == 0
        assert metrics.records_processed == 0
        assert metrics.errors_encountered == 0
        assert metrics.start_time is None

    def test_metrics_with_data(self) -> None:
        """Test metrics with initial data."""
        now = datetime.now(UTC)

        metrics = TapMetrics(
            api_calls=10,
            records_processed=1000,
            errors_encountered=2,
            start_time=now,
        )

        assert metrics.api_calls == 10
        assert metrics.records_processed == 1000
        assert metrics.errors_encountered == 2
        assert metrics.start_time == now

    def test_add_api_call_method(self) -> None:
        """Test add_api_call method."""
        metrics = TapMetrics(start_time=None)

        assert metrics.api_calls == 0

        metrics.add_api_call()
        assert metrics.api_calls == 1

        metrics.add_api_call()
        assert metrics.api_calls == 2

    def test_add_record_method(self) -> None:
        """Test add_record method."""
        metrics = TapMetrics(start_time=None)

        assert metrics.records_processed == 0

        metrics.add_record()
        assert metrics.records_processed == 1

        metrics.add_record()
        assert metrics.records_processed == 2

    def test_add_error_method(self) -> None:
        """Test add_error method."""
        metrics = TapMetrics(start_time=None)

        assert metrics.errors_encountered == 0

        metrics.add_error()
        assert metrics.errors_encountered == 1

        metrics.add_error()
        assert metrics.errors_encountered == 2

    def test_metrics_validation(self) -> None:
        """Test metrics validation."""
        # Negative values should fail
        with pytest.raises(ValidationError):
            TapMetrics(api_calls=-1, start_time=None)

        with pytest.raises(ValidationError):
            TapMetrics(records_processed=-1, start_time=None)

        with pytest.raises(ValidationError):
            TapMetrics(errors_encountered=-1, start_time=None)


class TestModelIntegration:
    """Test model integration scenarios."""

    def test_complete_discovery_flow(self) -> None:
        """Test complete discovery flow with all models."""
        now = datetime.now(UTC)

        # Create config
        config = WMSConfig(
            base_url=HttpUrl("https://wms.example.com"),
            username="test_user",
            password="test_pass",
        )

        # Create entities
        item_entity = WMSEntity(
            name="item",
            description=None,
            endpoint="/entity/item",
            supports_incremental=True,
            primary_key=None,
            timestamp_field="mod_ts",
            total_records=None,
        )

        location_entity = WMSEntity(
            name="location",
            description=None,
            endpoint="/entity/location",
            supports_incremental=False,
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )

        # Create discovery result
        discovery = WMSDiscoveryResult(
            discovered_at=now,
            base_url=str(config.base_url),
            duration_seconds=None,
        )

        discovery.add_entity(item_entity)
        discovery.add_entity(location_entity)

        # Create stream metadata
        item_metadata = WMSStreamMetadata(
            stream_name=item_entity.name,
            replication_method="INCREMENTAL",
            replication_key=item_entity.timestamp_field,
        )

        # Create records
        item_record = WMSRecord(
            stream_name=item_entity.name,
            record_data={"id": 1, "code": "ITEM001", "mod_ts": "2024-01-01T10:00:00Z"},
            extracted_at=now,
            source_endpoint=item_entity.endpoint,
            record_id=None,
            page_number=None,
        )

        # Create metrics
        metrics = TapMetrics(start_time=now)
        metrics.add_api_call()
        metrics.add_record()

        # Verify integration
        assert discovery.total_entities == 2
        assert item_metadata.stream_name == item_entity.name
        assert item_record.stream_name == item_entity.name
        assert metrics.api_calls == 1
        assert metrics.records_processed == 1

    def test_error_handling_flow(self) -> None:
        """Test error handling integration."""
        now = datetime.now(UTC)

        # Create discovery with error
        discovery = WMSDiscoveryResult(
            discovered_at=now,
            base_url="https://wms.example.com",
            duration_seconds=None,
        )

        auth_error = WMSError(
            error_type="authentication",
            message="Invalid credentials provided",
            timestamp=now,
            endpoint=None,
            status_code=401,
            retryable=False,
            request_id=None,
        )

        discovery.add_error(auth_error)

        # Create metrics with error
        metrics = TapMetrics(start_time=now)
        metrics.add_error()

        # Verify error handling
        assert discovery.success is False
        assert discovery.failed_count == 1
        assert metrics.errors_encountered == 1

    def test_serialization_integration(self) -> None:
        """Test model serialization works correctly."""
        now = datetime.now(UTC)

        # Create and serialize config
        config = WMSConfig(
            base_url=HttpUrl("https://wms.example.com"),
            username="test_user",
            password="test_pass",
        )

        config_data = config.model_dump()
        assert "base_url" in config_data
        assert "username" in config_data

        # Create and serialize entity
        entity = WMSEntity(
            name="item",
            description=None,
            endpoint="/entity/item",
            primary_key=None,
            timestamp_field=None,
            total_records=None,
        )

        entity_data = entity.model_dump()
        assert entity_data["name"] == "item"
        assert entity_data["endpoint"] == "/entity/item"

        # Create and serialize record
        record = WMSRecord(
            stream_name="item",
            record_data={"id": 1},
            extracted_at=now,
            source_endpoint="/entity/item",
            record_id=None,
            page_number=None,
        )

        record_data = record.model_dump()
        assert record_data["stream_name"] == "item"
        assert "record_data" in record_data
