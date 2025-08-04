"""Unit tests for models module."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import HttpUrl, ValidationError

from flext_tap_oracle_wms.models import (
    FlextConstants,
    TapMetrics,
    WMSConfig,
    WMSDiscoveryResult,
    WMSEntity,
    WMSError,
    WMSRecord,
    WMSStreamMetadata,
)

# Constants
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3
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
        if FlextConstants.MAX_ENTITY_NAME_LENGTH != 255:
            msg: str = f"Expected {255}, got {FlextConstants.MAX_ENTITY_NAME_LENGTH}"
            raise AssertionError(
                msg,
            )
        assert FlextConstants.MAX_ERROR_MESSAGE_LENGTH == 1000
        if FlextConstants.DEFAULT_TIMEOUT != 30:
            msg: str = f"Expected {30}, got {FlextConstants.DEFAULT_TIMEOUT}"
            raise AssertionError(msg)
        assert FlextConstants.FRAMEWORK_VERSION == "0.9.0"


class TestWMSConfig:
    """Test WMSConfig model."""

    def test_minimal_config(self) -> None:
        """Test minimal valid configuration."""
        config = WMSConfig(
            base_url=HttpUrl("https://wms.example.com"),
            username="test_user",
            password="test_pass",
        )
        if str(config.base_url) != "https://wms.example.com/":
            msg: str = f"Expected {'https://wms.example.com/'}, got {config.base_url!s}"
            raise AssertionError(
                msg,
            )
        assert config.username == "test_user"
        if config.password != "test_pass":
            msg: str = f"Expected {'test_pass'}, got {config.password}"
            raise AssertionError(msg)
        assert config.company_code == "*"
        if config.facility_code != "*":
            msg: str = f"Expected {'*'}, got {config.facility_code}"
            raise AssertionError(msg)
        assert config.page_size == 500
        if config.timeout != 30:
            msg: str = f"Expected {30}, got {config.timeout}"
            raise AssertionError(msg)
        assert config.max_retries == EXPECTED_DATA_COUNT
        if not (config.auto_discover):
            msg: str = f"Expected True, got {config.auto_discover}"
            raise AssertionError(msg)
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
        if str(config.base_url) != "https://wms.enterprise.com/":
            msg: str = (
                f"Expected {'https://wms.enterprise.com/'}, got {config.base_url!s}"
            )
            raise AssertionError(
                msg,
            )
        assert config.username == "admin_user"
        if config.company_code != "COMP1":
            msg: str = f"Expected {'COMP1'}, got {config.company_code}"
            raise AssertionError(msg)
        assert config.facility_code == "FAC1"
        if config.page_size != 1000:
            msg: str = f"Expected {1000}, got {config.page_size}"
            raise AssertionError(msg)
        assert config.timeout == 60
        if config.max_retries != 5:
            msg: str = f"Expected {5}, got {config.max_retries}"
            raise AssertionError(msg)
        if config.auto_discover:
            msg: str = f"Expected False, got {config.auto_discover}"
            raise AssertionError(msg)
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
            if url not in str(config.base_url):
                msg: str = f"Expected {url} in {config.base_url!s}"
                raise AssertionError(msg)
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
        if config.page_size != 100:
            msg: str = f"Expected {100}, got {config.page_size}"
            raise AssertionError(msg)
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
        if config.timeout != 60:
            msg: str = f"Expected {60}, got {config.timeout}"
            raise AssertionError(msg)
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
            WMSConfig(username="user", password="pass")
        # Missing username
        with pytest.raises(ValidationError):
            WMSConfig(base_url=HttpUrl("https://test.com"), password="pass")
        # Missing password
        with pytest.raises(ValidationError):
            WMSConfig(base_url=HttpUrl("https://test.com"), username="user")


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
        if entity.name != "item":
            msg: str = f"Expected {'item'}, got {entity.name}"
            raise AssertionError(msg)
        assert entity.endpoint == "/entity/item"
        assert entity.description is None
        if entity.supports_incremental:
            msg: str = f"Expected False, got {entity.supports_incremental}"
            raise AssertionError(msg)
        assert entity.primary_key is None
        assert entity.timestamp_field is None
        if entity.fields != []:
            msg: str = f"Expected {[]}, got {entity.fields}"
            raise AssertionError(msg)
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
        if entity.name != "allocation":
            msg: str = f"Expected {'allocation'}, got {entity.name}"
            raise AssertionError(msg)
        assert entity.endpoint == "/entity/allocation"
        if entity.description != "Allocation master data":
            msg: str = f"Expected {'Allocation master data'}, got {entity.description}"
            raise AssertionError(
                msg,
            )
        if not (entity.supports_incremental):
            msg: str = f"Expected True, got {entity.supports_incremental}"
            raise AssertionError(msg)
        if entity.primary_key != "alloc_id":
            msg: str = f"Expected {'alloc_id'}, got {entity.primary_key}"
            raise AssertionError(msg)
        assert entity.timestamp_field == "mod_ts"
        if entity.fields != ["alloc_id", "item_id", "location", "mod_ts"]:
            msg: str = f"Expected {['alloc_id', 'item_id', 'location', 'mod_ts']}, got {entity.fields}"
            raise AssertionError(
                msg,
            )
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
        if entity.name != "item":
            msg: str = f"Expected {'item'}, got {entity.name}"
            raise AssertionError(msg)
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
        if entity.total_records != 100:
            msg: str = f"Expected {100}, got {entity.total_records}"
            raise AssertionError(msg)
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
        if metadata.stream_name != "item":
            msg: str = f"Expected {'item'}, got {metadata.stream_name}"
            raise AssertionError(msg)
        assert metadata.key_properties == []
        if metadata.replication_method != "FULL_TABLE":
            msg: str = f"Expected {'FULL_TABLE'}, got {metadata.replication_method}"
            raise AssertionError(
                msg,
            )
        assert metadata.replication_key is None
        if metadata.json_schema != {}:
            msg: str = f"Expected {{}}, got {metadata.json_schema}"
            raise AssertionError(msg)
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
        if metadata.stream_name != "allocation":
            msg: str = f"Expected {'allocation'}, got {metadata.stream_name}"
            raise AssertionError(msg)
        assert metadata.key_properties == ["alloc_id", "facility_code"]
        if metadata.replication_method != "INCREMENTAL":
            msg: str = f"Expected {'INCREMENTAL'}, got {metadata.replication_method}"
            raise AssertionError(
                msg,
            )
        assert metadata.replication_key == "mod_ts"
        if metadata.json_schema != schema:
            msg: str = f"Expected {schema}, got {metadata.json_schema}"
            raise AssertionError(msg)
        assert metadata.metadata == meta

    def test_stream_name_validation(self) -> None:
        """Test stream name validation."""
        # Valid name
        metadata = WMSStreamMetadata(stream_name="item", replication_key=None)
        if metadata.stream_name != "item":
            msg: str = f"Expected {'item'}, got {metadata.stream_name}"
            raise AssertionError(msg)
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
            id="record_1",
            stream_name="item",
            record_data={"id": 1, "code": "ITEM001"},
            extracted_at=now,
            source_endpoint="/entity/item",
            record_id=None,
            page_number=None,
        )
        if record.stream_name != "item":
            msg: str = f"Expected {'item'}, got {record.stream_name}"
            raise AssertionError(msg)
        assert record.record_data == {"id": 1, "code": "ITEM001"}
        if record.extracted_at != now:
            msg: str = f"Expected {now}, got {record.extracted_at}"
            raise AssertionError(msg)
        assert record.source_endpoint == "/entity/item"
        assert record.record_id is None
        assert record.page_number is None

    def test_full_record(self) -> None:
        """Test full record with all fields."""
        now = datetime.now(UTC)
        record = WMSRecord(
            id="record_2",
            stream_name="allocation",
            record_data={"alloc_id": "A001", "item_id": "ITEM001"},
            extracted_at=now,
            source_endpoint="/entity/allocation",
            record_id="A001",
            page_number=2,
        )
        if record.stream_name != "allocation":
            msg: str = f"Expected {'allocation'}, got {record.stream_name}"
            raise AssertionError(msg)
        assert record.record_data == {"alloc_id": "A001", "item_id": "ITEM001"}
        if record.record_id != "A001":
            msg: str = f"Expected {'A001'}, got {record.record_id}"
            raise AssertionError(msg)
        assert record.page_number == EXPECTED_BULK_SIZE

    def test_record_data_validation(self) -> None:
        """Test record data validation."""
        now = datetime.now(UTC)
        # Valid record data
        record = WMSRecord(
            id="record_3",
            stream_name="item",
            record_data={"id": 1},
            extracted_at=now,
            source_endpoint="/test",
            record_id=None,
            page_number=None,
        )
        if record.record_data != {"id": 1}:
            msg: str = f"Expected {{'id': 1}}, got {record.record_data}"
            raise AssertionError(msg)
        # Empty record data should fail
        with pytest.raises(ValidationError):
            WMSRecord(
                id="record_4",
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
            id="record_5",
            stream_name="item",
            record_data={"id": 1},
            extracted_at=now,
            source_endpoint="/test",
            record_id=None,
            page_number=1,
        )
        if record.page_number != 1:
            msg: str = f"Expected {1}, got {record.page_number}"
            raise AssertionError(msg)
        # Invalid page number
        with pytest.raises(ValidationError):
            WMSRecord(
                id="record_6",
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
        if error.error_type != "authentication":
            msg: str = f"Expected {'authentication'}, got {error.error_type}"
            raise AssertionError(msg)
        assert error.message == "Invalid credentials"
        if error.timestamp != now:
            msg: str = f"Expected {now}, got {error.timestamp}"
            raise AssertionError(msg)
        assert error.endpoint is None
        assert error.status_code is None
        if error.retryable:
            msg: str = f"Expected False, got {error.retryable}"
            raise AssertionError(msg)
        assert error.request_id is None
        if error.details != {}:
            msg: str = f"Expected {{}}, got {error.details}"
            raise AssertionError(msg)

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
        if error.error_type != "network":
            msg: str = f"Expected {'network'}, got {error.error_type}"
            raise AssertionError(msg)
        assert error.message == "Connection timeout"
        if error.endpoint != "/entity/item":
            msg: str = f"Expected {'/entity/item'}, got {error.endpoint}"
            raise AssertionError(msg)
        assert error.status_code == 500
        if not (error.retryable):
            msg: str = f"Expected True, got {error.retryable}"
            raise AssertionError(msg)
        if error.request_id != "req-123":
            msg: str = f"Expected {'req-123'}, got {error.request_id}"
            raise AssertionError(msg)
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
            if error.status_code != status:
                msg: str = f"Expected {status}, got {error.status_code}"
                raise AssertionError(msg)
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
        if error.message != "Valid message":
            msg: str = f"Expected {'Valid message'}, got {error.message}"
            raise AssertionError(msg)
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
            id="discovery_1",
            discovered_at=now,
            base_url="https://wms.example.com",
            duration_seconds=None,
        )
        if result.discovered_at != now:
            msg: str = f"Expected {now}, got {result.discovered_at}"
            raise AssertionError(msg)
        assert result.base_url == "https://wms.example.com"
        if result.total_entities != 0:
            msg: str = f"Expected {0}, got {result.total_entities}"
            raise AssertionError(msg)
        assert result.entities == []
        if result.errors != []:
            msg: str = f"Expected {[]}, got {result.errors}"
            raise AssertionError(msg)
        if not (result.success):
            msg: str = f"Expected True, got {result.success}"
            raise AssertionError(msg)
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
            id="discovery_auto",
            discovered_at=now,
            base_url="https://wms.example.com",
            total_entities=2,
            entities=[entity1, entity2],
            duration_seconds=1.5,
        )
        if result.total_entities != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {result.total_entities}"
            raise AssertionError(msg)
        assert len(result.entities) == EXPECTED_BULK_SIZE
        if result.entities[0].name != "item":
            msg: str = f"Expected {'item'}, got {result.entities[0].name}"
            raise AssertionError(msg)
        assert result.entities[1].name == "location"
        if result.duration_seconds != 1.5:
            msg: str = f"Expected {1.5}, got {result.duration_seconds}"
            raise AssertionError(msg)

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
            id="discovery_auto",
            discovered_at=now,
            base_url="https://wms.example.com",
            errors=[error],
            duration_seconds=None,
        )
        if len(result.errors) != 1:
            msg: str = f"Expected {1}, got {len(result.errors)}"
            raise AssertionError(msg)
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
            id="discovery_auto",
            discovered_at=now,
            base_url="https://wms.example.com",
            entities=[entity1, entity2],
            duration_seconds=None,
        )
        successful = result.successful_entities
        if len(successful) != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {len(successful)}"
            raise AssertionError(msg)
        if not all(entity.name for entity in successful):
            msg = (
                f"Expected {all(entity.name for entity in successful)} in {successful}"
            )
            raise AssertionError(
                msg,
            )

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
            id="discovery_auto",
            discovered_at=now,
            base_url="https://wms.example.com",
            errors=[error1, error2],
            duration_seconds=None,
        )
        if result.failed_count != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {result.failed_count}"
            raise AssertionError(msg)

    def test_add_entity_method(self) -> None:
        """Test add_entity method."""
        now = datetime.now(UTC)
        result = WMSDiscoveryResult(
            id="discovery_auto",
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
        if result.total_entities != 1:
            msg: str = f"Expected {1}, got {result.total_entities}"
            raise AssertionError(msg)
        assert len(result.entities) == 1
        if result.entities[0] != entity:
            msg: str = f"Expected {entity}, got {result.entities[0]}"
            raise AssertionError(msg)

    def test_add_error_method(self) -> None:
        """Test add_error method."""
        now = datetime.now(UTC)
        result = WMSDiscoveryResult(
            id="discovery_auto",
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
        if len(result.errors) != 1:
            msg: str = f"Expected {1}, got {len(result.errors)}"
            raise AssertionError(msg)
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
        if len(result.errors) != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {len(result.errors)}"
            raise AssertionError(msg)
        assert result.success is False  # Now failed


class TestTapMetrics:
    """Test TapMetrics model."""

    def test_default_metrics(self) -> None:
        """Test default metrics initialization."""
        metrics = TapMetrics(
            id="metrics_auto",
            start_time=None)
        if metrics.api_calls != 0:
            msg: str = f"Expected {0}, got {metrics.api_calls}"
            raise AssertionError(msg)
        assert metrics.records_processed == 0
        if metrics.errors_encountered != 0:
            msg: str = f"Expected {0}, got {metrics.errors_encountered}"
            raise AssertionError(msg)
        assert metrics.start_time is None

    def test_metrics_with_data(self) -> None:
        """Test metrics with initial data."""
        now = datetime.now(UTC)
        metrics = TapMetrics(
            id="metrics_auto",
            api_calls=10,
            records_processed=1000,
            errors_encountered=2,
            start_time=now,
        )
        if metrics.api_calls != 10:
            msg: str = f"Expected {10}, got {metrics.api_calls}"
            raise AssertionError(msg)
        assert metrics.records_processed == 1000
        if metrics.errors_encountered != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {metrics.errors_encountered}"
            raise AssertionError(msg)
        assert metrics.start_time == now

    def test_add_api_call_method(self) -> None:
        """Test add_api_call method."""
        metrics = TapMetrics(
            id="metrics_auto",
            start_time=None)
        if metrics.api_calls != 0:
            msg: str = f"Expected {0}, got {metrics.api_calls}"
            raise AssertionError(msg)
        metrics.add_api_call()
        if metrics.api_calls != 1:
            msg: str = f"Expected {1}, got {metrics.api_calls}"
            raise AssertionError(msg)
        metrics.add_api_call()
        if metrics.api_calls != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {metrics.api_calls}"
            raise AssertionError(msg)

    def test_add_record_method(self) -> None:
        """Test add_record method."""
        metrics = TapMetrics(
            id="metrics_auto",
            start_time=None)
        if metrics.records_processed != 0:
            msg: str = f"Expected {0}, got {metrics.records_processed}"
            raise AssertionError(msg)
        metrics.add_record()
        if metrics.records_processed != 1:
            msg: str = f"Expected {1}, got {metrics.records_processed}"
            raise AssertionError(msg)
        metrics.add_record()
        if metrics.records_processed != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {metrics.records_processed}"
            raise AssertionError(msg)

    def test_add_error_method(self) -> None:
        """Test add_error method."""
        metrics = TapMetrics(
            id="metrics_auto",
            start_time=None)
        if metrics.errors_encountered != 0:
            msg: str = f"Expected {0}, got {metrics.errors_encountered}"
            raise AssertionError(msg)
        metrics.add_error()
        if metrics.errors_encountered != 1:
            msg: str = f"Expected {1}, got {metrics.errors_encountered}"
            raise AssertionError(msg)
        metrics.add_error()
        if metrics.errors_encountered != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {metrics.errors_encountered}"
            raise AssertionError(msg)

    def test_metrics_validation(self) -> None:
        """Test metrics validation."""
        # Negative values should fail
        with pytest.raises(ValidationError):
            TapMetrics(
            id="metrics_auto",
            api_calls=-1, start_time=None)
        with pytest.raises(ValidationError):
            TapMetrics(
            id="metrics_auto",
            records_processed=-1, start_time=None)
        with pytest.raises(ValidationError):
            TapMetrics(
            id="metrics_auto",
            errors_encountered=-1, start_time=None)


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
            id="discovery_auto",
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
            id="record_7",
            stream_name=item_entity.name,
            record_data={"id": 1, "code": "ITEM001", "mod_ts": "2024-01-01T10:00:00Z"},
            extracted_at=now,
            source_endpoint=item_entity.endpoint,
            record_id=None,
            page_number=None,
        )
        # Create metrics
        metrics = TapMetrics(
            id="metrics_auto",
            start_time=now)
        metrics.add_api_call()
        metrics.add_record()
        # Verify integration
        if discovery.total_entities != EXPECTED_BULK_SIZE:
            msg: str = f"Expected {2}, got {discovery.total_entities}"
            raise AssertionError(msg)
        assert item_metadata.stream_name == item_entity.name
        if item_record.stream_name != item_entity.name:
            msg: str = f"Expected {item_entity.name}, got {item_record.stream_name}"
            raise AssertionError(
                msg,
            )
        assert metrics.api_calls == 1
        if metrics.records_processed != 1:
            msg: str = f"Expected {1}, got {metrics.records_processed}"
            raise AssertionError(msg)

    def test_error_handling_flow(self) -> None:
        """Test error handling integration."""
        now = datetime.now(UTC)
        # Create discovery with error
        discovery = WMSDiscoveryResult(
            id="discovery_auto",
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
        metrics = TapMetrics(
            id="metrics_auto",
            start_time=now)
        metrics.add_error()
        # Verify error handling
        if discovery.success:
            msg: str = f"Expected False, got {discovery.success}"
            raise AssertionError(msg)
        assert discovery.failed_count == 1
        if metrics.errors_encountered != 1:
            msg: str = f"Expected {1}, got {metrics.errors_encountered}"
            raise AssertionError(msg)

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
        if "base_url" not in config_data:
            msg: str = f"Expected {'base_url'} in {config_data}"
            raise AssertionError(msg)
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
        if entity_data["name"] != "item":
            msg: str = f"Expected {'item'}, got {entity_data['name']}"
            raise AssertionError(msg)
        assert entity_data["endpoint"] == "/entity/item"
        # Create and serialize record
        record = WMSRecord(
            id="record_8",
            stream_name="item",
            record_data={"id": 1},
            extracted_at=now,
            source_endpoint="/entity/item",
            record_id=None,
            page_number=None,
        )
        record_data = record.model_dump()
        if record_data["stream_name"] != "item":
            msg: str = f"Expected {'item'}, got {record_data['stream_name']}"
            raise AssertionError(msg)
        if "record_data" not in record_data:
            msg: str = f"Expected {'record_data'} in {record_data}"
            raise AssertionError(msg)
