"""Modern unit tests for Pydantic models."""

from __future__ import annotations

from pydantic import ValidationError
import pytest

from tap_oracle_wms.models import TapMetrics, WMSConfig, WMSEntity


class TestWMSConfig:
    """Test WMS configuration model."""

    def test_valid_config(self) -> None:
        """Test valid configuration creation."""
        config = WMSConfig(
            base_url="https://wms.example.com",
            username="test_user",
            password="test_pass",
        )

        assert str(config.base_url) == "https://wms.example.com/"
        assert config.username == "test_user"
        assert config.password == "test_pass"
        assert config.company_code == "*"  # Default
        assert config.facility_code == "*"  # Default
        assert config.page_size == 100  # Default

    def test_http_url_rejected(self) -> None:
        """Test that HTTP URLs are rejected."""
        with pytest.raises(ValidationError, match="HTTP URLs not allowed"):
            WMSConfig(
                base_url="http://insecure.example.com",
                username="test",
                password="test",
            )

    def test_empty_credentials_rejected(self) -> None:
        """Test that empty credentials are rejected."""
        with pytest.raises(ValidationError):
            WMSConfig(
                base_url="https://wms.example.com",
                username="",
                password="test",
            )

    def test_invalid_page_size_rejected(self) -> None:
        """Test that invalid page sizes are rejected."""
        with pytest.raises(ValidationError):
            WMSConfig(
                base_url="https://wms.example.com",
                username="test",
                password="test",
                page_size=0,  # Invalid
            )

    def test_config_immutable(self) -> None:
        """Test that config is immutable after creation."""
        config = WMSConfig(
            base_url="https://wms.example.com",
            username="test",
            password="test",
        )

        with pytest.raises(ValidationError):
            config.username = "modified"  # Should fail - frozen=True


class TestWMSEntity:
    """Test WMS entity model."""

    def test_valid_entity(self) -> None:
        """Test valid entity creation."""
        entity = WMSEntity(
            name="item_master",
            endpoint="/api/item_master",
            has_mod_ts=True,
            fields=["id", "name", "mod_ts"],
        )

        assert entity.name == "item_master"
        assert entity.endpoint == "/api/item_master"
        assert entity.has_mod_ts is True
        assert "id" in entity.fields

    def test_entity_defaults(self) -> None:
        """Test entity with default values."""
        entity = WMSEntity(
            name="location",
            endpoint="/api/location",
        )

        assert entity.has_mod_ts is False  # Default
        assert entity.fields == []  # Default


class TestTapMetrics:
    """Test tap metrics model."""

    def test_metrics_initialization(self) -> None:
        """Test metrics initialization."""
        metrics = TapMetrics()

        assert metrics.records_extracted == 0
        assert metrics.entities_discovered == 0
        assert metrics.api_calls_made == 0
        assert metrics.start_time is not None
        assert metrics.last_activity is not None

    def test_add_records(self) -> None:
        """Test adding records updates counts and activity."""
        metrics = TapMetrics()
        original_activity = metrics.last_activity

        metrics.add_records(50)

        assert metrics.records_extracted == 50
        assert metrics.last_activity > original_activity

    def test_add_api_call(self) -> None:
        """Test adding API call updates counts and activity."""
        metrics = TapMetrics()
        original_activity = metrics.last_activity

        metrics.add_api_call()

        assert metrics.api_calls_made == 1
        assert metrics.last_activity > original_activity
