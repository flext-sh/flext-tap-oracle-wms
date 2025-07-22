"""Unit tests for config module."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_tap_oracle_wms.config import (
    TapOracleWMSConfig,
    WMSAuthConfig,
    WMSConnectionConfig,
    WMSDiscoveryConfig,
    WMSExtractionConfig,
)


class TestWMSAuthConfig:
    """Test WMSAuthConfig model."""

    def test_basic_auth_config(self) -> None:
        """Test basic authentication configuration."""
        auth = WMSAuthConfig(
            username="test_user",
            password="test_pass",
            auth_method="basic",
        )
        assert auth.username == "test_user"
        assert auth.password == "test_pass"
        assert auth.auth_method == "basic"

    def test_auth_method_validation(self) -> None:
        """Test authentication method validation."""
        # Valid methods
        auth_basic = WMSAuthConfig(
            username="user",
            password="pass",
            auth_method="basic",
        )
        assert auth_basic.auth_method == "basic"
        auth_token = WMSAuthConfig(
            username="user",
            password="pass",
            auth_method="token",
        )
        assert auth_token.auth_method == "token"
        auth_oauth = WMSAuthConfig(
            username="user",
            password="pass",
            auth_method="oauth",
        )
        assert auth_oauth.auth_method == "oauth"
        # Invalid method should fail
        with pytest.raises(ValidationError):
            WMSAuthConfig(username="user", password="pass", auth_method="invalid")

    def test_required_fields(self) -> None:
        """Test required field validation."""
        # Missing username should fail
        with pytest.raises(ValidationError):
            WMSAuthConfig(password="pass", auth_method="basic")
        # Missing password should fail
        with pytest.raises(ValidationError):
            WMSAuthConfig(username="user", auth_method="basic")


class TestWMSConnectionConfig:
    """Test WMSConnectionConfig model."""

    def test_minimal_connection_config(self) -> None:
        """Test minimal connection configuration."""
        conn = WMSConnectionConfig(base_url="https://wms.example.com")
        assert conn.base_url == "https://wms.example.com"
        assert conn.timeout == 30
        assert conn.max_retries == 3
        assert conn.verify_ssl is True

    def test_full_connection_config(self) -> None:
        """Test full connection configuration."""
        conn = WMSConnectionConfig(
            base_url="https://wms.example.com",
            timeout=60,
            max_retries=5,
            verify_ssl=False,
        )
        assert conn.base_url == "https://wms.example.com"
        assert conn.timeout == 60
        assert conn.max_retries == 5
        assert conn.verify_ssl is False

    def test_base_url_validation(self) -> None:
        """Test base URL validation."""
        # Valid URLs
        conn_https = WMSConnectionConfig(base_url="https://test.com")
        assert conn_https.base_url == "https://test.com"
        conn_http = WMSConnectionConfig(base_url="http://test.com")
        assert conn_http.base_url == "http://test.com"
        # URL with trailing slash should be stripped
        conn_slash = WMSConnectionConfig(base_url="https://test.com/")
        assert conn_slash.base_url == "https://test.com"
        # Invalid URL should fail
        with pytest.raises(ValidationError):
            WMSConnectionConfig(base_url="invalid-url")

    def test_timeout_validation(self) -> None:
        """Test timeout validation."""
        # Valid timeout
        conn = WMSConnectionConfig(base_url="https://test.com", timeout=30)
        assert conn.timeout == 30
        # Invalid timeout should fail
        with pytest.raises(ValidationError):
            WMSConnectionConfig(base_url="https://test.com", timeout=0)
        with pytest.raises(ValidationError):
            WMSConnectionConfig(base_url="https://test.com", timeout=301)

    def test_max_retries_validation(self) -> None:
        """Test max retries validation."""
        # Valid retries
        conn = WMSConnectionConfig(base_url="https://test.com", max_retries=5)
        assert conn.max_retries == 5
        # Invalid retries should fail
        with pytest.raises(ValidationError):
            WMSConnectionConfig(base_url="https://test.com", max_retries=-1)
        with pytest.raises(ValidationError):
            WMSConnectionConfig(base_url="https://test.com", max_retries=11)


class TestWMSDiscoveryConfig:
    """Test WMSDiscoveryConfig model."""

    def test_default_discovery_config(self) -> None:
        """Test default discovery configuration."""
        config = WMSDiscoveryConfig()
        assert config.auto_discover is True
        assert config.entity_filter == []
        assert config.exclude_entities == []
        assert config.include_metadata is True
        assert config.max_entities == 100

    def test_custom_discovery_config(self) -> None:
        """Test custom discovery configuration."""
        config = WMSDiscoveryConfig(
            auto_discover=False,
            entity_filter=["item", "location"],
            exclude_entities=["temp"],
            include_metadata=False,
            max_entities=50,
        )
        assert config.auto_discover is False
        assert config.entity_filter == ["item", "location"]
        assert config.exclude_entities == ["temp"]
        assert config.include_metadata is False
        assert config.max_entities == 50

    def test_max_entities_validation(self) -> None:
        """Test max entities validation."""
        # Valid max entities
        config = WMSDiscoveryConfig(max_entities=100)
        assert config.max_entities == 100
        # Invalid max entities should fail
        with pytest.raises(ValidationError):
            WMSDiscoveryConfig(max_entities=0)
        with pytest.raises(ValidationError):
            WMSDiscoveryConfig(max_entities=1001)


class TestWMSExtractionConfig:
    """Test WMSExtractionConfig model."""

    def test_default_extraction_config(self) -> None:
        """Test default extraction configuration."""
        config = WMSExtractionConfig(start_date=None)
        assert config.page_size == 500
        assert config.company_code == "*"
        assert config.facility_code == "*"
        assert config.start_date is None
        assert config.batch_size == 1000

    def test_custom_extraction_config(self) -> None:
        """Test custom extraction configuration."""
        config = WMSExtractionConfig(
            page_size=100,
            company_code="COMP1",
            facility_code="FAC1",
            start_date="2024-01-01T00:00:00Z",
            batch_size=500,
        )
        assert config.page_size == 100
        assert config.company_code == "COMP1"
        assert config.facility_code == "FAC1"
        assert config.start_date == "2024-01-01T00:00:00Z"
        assert config.batch_size == 500

    def test_page_size_validation(self) -> None:
        """Test page size validation."""
        # Valid page size
        config = WMSExtractionConfig(page_size=100, start_date=None)
        assert config.page_size == 100
        # Invalid page size should fail
        with pytest.raises(ValidationError):
            WMSExtractionConfig(page_size=0, start_date=None)
        with pytest.raises(ValidationError):
            WMSExtractionConfig(page_size=10001, start_date=None)

    def test_batch_size_validation(self) -> None:
        """Test batch size validation."""
        # Valid batch size
        config = WMSExtractionConfig(batch_size=1000, start_date=None)
        assert config.batch_size == 1000
        # Invalid batch size should fail
        with pytest.raises(ValidationError):
            WMSExtractionConfig(batch_size=0, start_date=None)
        with pytest.raises(ValidationError):
            WMSExtractionConfig(batch_size=50001, start_date=None)


class TestTapOracleWMSConfig:
    """Test TapOracleWMSConfig main configuration model."""

    def test_minimal_config_creation(self) -> None:
        """Test creating config with minimal required fields."""
        auth = WMSAuthConfig(username="user", password="pass", auth_method="basic")
        connection = WMSConnectionConfig(base_url="https://test.com")
        config = TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            state_file=None,
            catalog_file=None,
        )
        assert config.auth.username == "user"
        assert config.connection.base_url == "https://test.com"
        assert config.discovery.auto_discover is True
        assert config.extraction.page_size == 500
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_full_config_creation(self) -> None:
        """Test creating config with all fields."""
        auth = WMSAuthConfig(
            username="test_user",
            password="test_pass",
            auth_method="oauth",
        )
        connection = WMSConnectionConfig(
            base_url="https://wms.example.com",
            timeout=60,
            max_retries=5,
            verify_ssl=False,
        )
        discovery = WMSDiscoveryConfig(
            auto_discover=False,
            entity_filter=["item"],
            max_entities=50,
        )
        extraction = WMSExtractionConfig(
            page_size=100,
            company_code="COMP1",
            facility_code="FAC1",
            start_date=None,
        )
        config = TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            discovery=discovery,
            extraction=extraction,
            state_file="/path/to/state.json",
            catalog_file="/path/to/catalog.json",
            debug=True,
            log_level="DEBUG",
        )
        assert config.auth.username == "test_user"
        assert config.connection.base_url == "https://wms.example.com"
        assert config.discovery.auto_discover is False
        assert config.extraction.page_size == 100
        assert config.state_file == "/path/to/state.json"
        assert config.catalog_file == "/path/to/catalog.json"
        assert config.debug is True
        assert config.log_level == "DEBUG"

    def test_log_level_validation(self) -> None:
        """Test log level validation."""
        auth = WMSAuthConfig(username="user", password="pass", auth_method="basic")
        connection = WMSConnectionConfig(base_url="https://test.com")
        # Valid log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = TapOracleWMSConfig(
                auth=auth,
                connection=connection,
                log_level=level,
                state_file=None,
                catalog_file=None,
            )
            assert config.log_level == level
        # Lowercase should be converted to uppercase
        config = TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            log_level="debug",
            state_file=None,
            catalog_file=None,
        )
        assert config.log_level == "DEBUG"
        # Invalid log level should fail
        with pytest.raises(ValidationError):
            TapOracleWMSConfig(
                auth=auth,
                connection=connection,
                log_level="INVALID",
                state_file=None,
                catalog_file=None,
            )

    def test_config_defaults(self) -> None:
        """Test configuration defaults."""
        auth = WMSAuthConfig(username="user", password="pass", auth_method="basic")
        connection = WMSConnectionConfig(base_url="https://test.com")
        config = TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            state_file=None,
            catalog_file=None,
        )
        # Check discovery defaults
        assert config.discovery.auto_discover is True
        assert config.discovery.entity_filter == []
        assert config.discovery.include_metadata is True
        assert config.discovery.max_entities == 100
        # Check extraction defaults
        assert config.extraction.page_size == 500
        assert config.extraction.company_code == "*"
        assert config.extraction.facility_code == "*"
        assert config.extraction.start_date is None
        # Check main config defaults
        assert config.state_file is None
        assert config.catalog_file is None
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_required_fields(self) -> None:
        """Test that required fields are enforced."""
        # Missing auth should fail - pydantic should enforce this during creation
        with pytest.raises(ValidationError):
            TapOracleWMSConfig(
                connection=WMSConnectionConfig(base_url="https://test.com"),
            )
        # Missing connection should fail - pydantic should enforce this during creation
        with pytest.raises(ValidationError):
            TapOracleWMSConfig(
                auth=WMSAuthConfig(
                    username="user",
                    password="pass",
                    auth_method="basic",
                ),
            )

    def test_to_singer_config(self) -> None:
        """Test converting to Singer configuration format."""
        auth = WMSAuthConfig(username="user", password="pass", auth_method="basic")
        connection = WMSConnectionConfig(base_url="https://test.com", timeout=60)
        discovery = WMSDiscoveryConfig(entity_filter=["item"])
        extraction = WMSExtractionConfig(
            page_size=100,
            company_code="COMP1",
            start_date=None,
        )
        config = TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            discovery=discovery,
            extraction=extraction,
            debug=True,
            state_file=None,
            catalog_file=None,
        )
        singer_config = config.to_singer_config()
        assert singer_config["base_url"] == "https://test.com"
        assert singer_config["username"] == "user"
        assert singer_config["password"] == "pass"
        assert singer_config["auth_method"] == "basic"
        assert singer_config["timeout"] == 60
        assert singer_config["page_size"] == 100
        assert singer_config["company_code"] == "COMP1"
        assert singer_config["entity_filter"] == ["item"]
        assert singer_config["debug"] is True

    def test_from_singer_config(self) -> None:
        """Test creating from Singer configuration format."""
        singer_config = {
            "base_url": "https://wms.example.com",
            "username": "test_user",
            "password": "test_pass",
            "auth_method": "token",
            "timeout": 90,
            "max_retries": 4,
            "verify_ssl": False,
            "page_size": 200,
            "company_code": "COMP2",
            "facility_code": "FAC2",
            "auto_discover": False,
            "entity_filter": ["location"],
            "max_entities": 75,
            "start_date": "2024-01-01T00:00:00Z",
            "batch_size": 2000,
            "debug": True,
            "log_level": "WARNING",
        }
        config = TapOracleWMSConfig.from_singer_config(singer_config)
        assert config.auth.username == "test_user"
        assert config.auth.password == "test_pass"
        assert config.auth.auth_method == "token"
        assert config.connection.base_url == "https://wms.example.com"
        assert config.connection.timeout == 90
        assert config.connection.max_retries == 4
        assert config.connection.verify_ssl is False
        assert config.extraction.page_size == 200
        assert config.extraction.company_code == "COMP2"
        assert config.extraction.facility_code == "FAC2"
        assert config.discovery.auto_discover is False
        assert config.discovery.entity_filter == ["location"]
        assert config.discovery.max_entities == 75
        assert config.extraction.start_date == "2024-01-01T00:00:00Z"
        assert config.extraction.batch_size == 2000
        assert config.debug is True
        assert config.log_level == "WARNING"

    def test_config_serialization(self) -> None:
        """Test configuration serialization."""
        auth = WMSAuthConfig(username="user", password="pass", auth_method="basic")
        connection = WMSConnectionConfig(base_url="https://test.com")
        config = TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            state_file=None,
            catalog_file=None,
        )
        # Serialize to dict
        data = config.model_dump()
        # Verify structure
        assert "auth" in data
        assert "connection" in data
        assert "discovery" in data
        assert "extraction" in data
        assert data["auth"]["username"] == "user"
        assert data["connection"]["base_url"] == "https://test.com"

    def test_config_deserialization(self) -> None:
        """Test configuration deserialization."""
        data = {
            "auth": {
                "username": "user",
                "password": "pass",
                "auth_method": "basic",
            },
            "connection": {
                "base_url": "https://test.com",
                "timeout": 30,
                "max_retries": 3,
                "verify_ssl": True,
            },
            "discovery": {
                "auto_discover": True,
                "entity_filter": [],
                "exclude_entities": [],
                "include_metadata": True,
                "max_entities": 100,
            },
            "extraction": {
                "page_size": 500,
                "company_code": "*",
                "facility_code": "*",
                "start_date": None,
                "batch_size": 1000,
            },
            "debug": False,
            "log_level": "INFO",
        }
        config = TapOracleWMSConfig.model_validate(data)
        assert config.auth.username == "user"
        assert config.connection.base_url == "https://test.com"
        assert config.discovery.auto_discover is True
        assert config.extraction.page_size == 500


class TestConfigValidation:
    """Test configuration validation scenarios."""

    def test_nested_validation(self) -> None:
        """Test that nested validation works."""
        # Invalid auth method should fail at auth level
        with pytest.raises(ValidationError):
            self._create_invalid_wms_config()

    def _create_invalid_wms_config(self) -> TapOracleWMSConfig:
        """Helper function to create invalid WMS config for testing."""
        auth = WMSAuthConfig(
            username="user",
            password="pass",
            auth_method="invalid",
        )
        return TapOracleWMSConfig(
            auth=auth,
            connection=WMSConnectionConfig(base_url="https://test.com"),
            state_file=None,
            catalog_file=None,
        )

    def _create_invalid_url_config(self, auth: WMSAuthConfig) -> TapOracleWMSConfig:
        """Helper function to create WMS config with invalid URL for testing."""
        return TapOracleWMSConfig(
            auth=auth,
            connection=WMSConnectionConfig(base_url="invalid-url"),
            state_file=None,
            catalog_file=None,
        )

    def _create_invalid_page_size_config(
        self,
        auth: WMSAuthConfig,
        connection: WMSConnectionConfig,
    ) -> TapOracleWMSConfig:
        """Helper function to create WMS config with invalid page size for testing."""
        return TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            extraction=WMSExtractionConfig(page_size=0, start_date=None),
            state_file=None,
            catalog_file=None,
        )

    def test_connection_url_validation(self) -> None:
        """Test connection URL validation."""
        auth = WMSAuthConfig(username="user", password="pass", auth_method="basic")
        # Valid URLs should work
        config_https = TapOracleWMSConfig(
            auth=auth,
            connection=WMSConnectionConfig(base_url="https://test.com"),
            state_file=None,
            catalog_file=None,
        )
        assert config_https.connection.base_url == "https://test.com"
        # Invalid URL should fail
        with pytest.raises(ValidationError):
            self._create_invalid_url_config(auth)

    def test_extraction_validation(self) -> None:
        """Test extraction configuration validation."""
        auth = WMSAuthConfig(username="user", password="pass", auth_method="basic")
        connection = WMSConnectionConfig(base_url="https://test.com")
        # Valid extraction config
        config = TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            extraction=WMSExtractionConfig(
                page_size=100,
                batch_size=500,
                start_date=None,
            ),
            state_file=None,
            catalog_file=None,
        )
        assert config.extraction.page_size == 100
        assert config.extraction.batch_size == 500
        # Invalid page size should fail
        with pytest.raises(ValidationError):
            self._create_invalid_page_size_config(auth, connection)
