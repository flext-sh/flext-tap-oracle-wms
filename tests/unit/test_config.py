"""Unit tests for config module."""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_tap_oracle_wms.config import (
# Constants
HTTP_OK = 200
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3

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
        if auth.username != "test_user":
            raise AssertionError(f"Expected {"test_user"}, got {auth.username}")
        assert auth.password == "test_pass"
        if auth.auth_method != "basic":
            raise AssertionError(f"Expected {"basic"}, got {auth.auth_method}")

    def test_auth_method_validation(self) -> None:
        """Test authentication method validation."""
        # Valid methods
        auth_basic = WMSAuthConfig(
            username="user",
            password="pass",
            auth_method="basic",
        )
        if auth_basic.auth_method != "basic":
            raise AssertionError(f"Expected {"basic"}, got {auth_basic.auth_method}")
        auth_token = WMSAuthConfig(
            username="user",
            password="pass",
            auth_method="token",
        )
        if auth_token.auth_method != "token":
            raise AssertionError(f"Expected {"token"}, got {auth_token.auth_method}")
        auth_oauth = WMSAuthConfig(
            username="user",
            password="pass",
            auth_method="oauth",
        )
        if auth_oauth.auth_method != "oauth":
            raise AssertionError(f"Expected {"oauth"}, got {auth_oauth.auth_method}")
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
        if conn.base_url != "https://wms.example.com":
            raise AssertionError(f"Expected {"https://wms.example.com"}, got {conn.base_url}")
        assert conn.timeout == 30
        if conn.max_retries != EXPECTED_DATA_COUNT:
            raise AssertionError(f"Expected {3}, got {conn.max_retries}")
        if not (conn.verify_ssl):
            raise AssertionError(f"Expected True, got {conn.verify_ssl}")

    def test_full_connection_config(self) -> None:
        """Test full connection configuration."""
        conn = WMSConnectionConfig(
            base_url="https://wms.example.com",
            timeout=60,
            max_retries=5,
            verify_ssl=False,
        )
        if conn.base_url != "https://wms.example.com":
            raise AssertionError(f"Expected {"https://wms.example.com"}, got {conn.base_url}")
        assert conn.timeout == 60
        if conn.max_retries != 5:
            raise AssertionError(f"Expected {5}, got {conn.max_retries}")
        if conn.verify_ssl:
            raise AssertionError(f"Expected False, got {conn.verify_ssl}")\ n
    def test_base_url_validation(self) -> None:
        """Test base URL validation."""
        # Valid URLs
        conn_https = WMSConnectionConfig(base_url="https://test.com")
        if conn_https.base_url != "https://test.com":
            raise AssertionError(f"Expected {"https://test.com"}, got {conn_https.base_url}")
        conn_http = WMSConnectionConfig(base_url="http://test.com")
        if conn_http.base_url != "http://test.com":
            raise AssertionError(f"Expected {"http://test.com"}, got {conn_http.base_url}")
        # URL with trailing slash should be stripped
        conn_slash = WMSConnectionConfig(base_url="https://test.com/")
        if conn_slash.base_url != "https://test.com":
            raise AssertionError(f"Expected {"https://test.com"}, got {conn_slash.base_url}")
        # Invalid URL should fail
        with pytest.raises(ValidationError):
            WMSConnectionConfig(base_url="invalid-url")

    def test_timeout_validation(self) -> None:
        """Test timeout validation."""
        # Valid timeout
        conn = WMSConnectionConfig(base_url="https://test.com", timeout=30)
        if conn.timeout != 30:
            raise AssertionError(f"Expected {30}, got {conn.timeout}")
        # Invalid timeout should fail
        with pytest.raises(ValidationError):
            WMSConnectionConfig(base_url="https://test.com", timeout=0)
        with pytest.raises(ValidationError):
            WMSConnectionConfig(base_url="https://test.com", timeout=301)

    def test_max_retries_validation(self) -> None:
        """Test max retries validation."""
        # Valid retries
        conn = WMSConnectionConfig(base_url="https://test.com", max_retries=5)
        if conn.max_retries != 5:
            raise AssertionError(f"Expected {5}, got {conn.max_retries}")
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
        if not (config.auto_discover):
            raise AssertionError(f"Expected True, got {config.auto_discover}")
        if config.entity_filter != []:
            raise AssertionError(f"Expected {[]}, got {config.entity_filter}")
        assert config.exclude_entities == []
        if not (config.include_metadata):
            raise AssertionError(f"Expected True, got {config.include_metadata}")
        if config.max_entities != 100:
            raise AssertionError(f"Expected {100}, got {config.max_entities}")

    def test_custom_discovery_config(self) -> None:
        """Test custom discovery configuration."""
        config = WMSDiscoveryConfig(
            auto_discover=False,
            entity_filter=["item", "location"],
            exclude_entities=["temp"],
            include_metadata=False,
            max_entities=50,
        )
        if config.auto_discover:
            raise AssertionError(f"Expected False, got {config.auto_discover}")\ n        assert config.entity_filter == ["item", "location"]
        if config.exclude_entities != ["temp"]:
            raise AssertionError(f"Expected {["temp"]}, got {config.exclude_entities}")
        if config.include_metadata:
            raise AssertionError(f"Expected False, got {config.include_metadata}")\ n        assert config.max_entities == 50

    def test_max_entities_validation(self) -> None:
        """Test max entities validation."""
        # Valid max entities
        config = WMSDiscoveryConfig(max_entities=100)
        if config.max_entities != 100:
            raise AssertionError(f"Expected {100}, got {config.max_entities}")
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
        if config.page_size != 500:
            raise AssertionError(f"Expected {500}, got {config.page_size}")
        assert config.company_code == "*"
        if config.facility_code != "*":
            raise AssertionError(f"Expected {"*"}, got {config.facility_code}")
        assert config.start_date is None
        if config.batch_size != 1000:
            raise AssertionError(f"Expected {1000}, got {config.batch_size}")

    def test_custom_extraction_config(self) -> None:
        """Test custom extraction configuration."""
        config = WMSExtractionConfig(
            page_size=100,
            company_code="COMP1",
            facility_code="FAC1",
            start_date="2024-01-01T00:00:00Z",
            batch_size=500,
        )
        if config.page_size != 100:
            raise AssertionError(f"Expected {100}, got {config.page_size}")
        assert config.company_code == "COMP1"
        if config.facility_code != "FAC1":
            raise AssertionError(f"Expected {"FAC1"}, got {config.facility_code}")
        assert config.start_date == "2024-01-01T00:00:00Z"
        if config.batch_size != 500:
            raise AssertionError(f"Expected {500}, got {config.batch_size}")

    def test_page_size_validation(self) -> None:
        """Test page size validation."""
        # Valid page size
        config = WMSExtractionConfig(page_size=100, start_date=None)
        if config.page_size != 100:
            raise AssertionError(f"Expected {100}, got {config.page_size}")
        # Invalid page size should fail
        with pytest.raises(ValidationError):
            WMSExtractionConfig(page_size=0, start_date=None)
        with pytest.raises(ValidationError):
            WMSExtractionConfig(page_size=10001, start_date=None)

    def test_batch_size_validation(self) -> None:
        """Test batch size validation."""
        # Valid batch size
        config = WMSExtractionConfig(batch_size=1000, start_date=None)
        if config.batch_size != 1000:
            raise AssertionError(f"Expected {1000}, got {config.batch_size}")
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
        if config.auth.username != "user":
            raise AssertionError(f"Expected {"user"}, got {config.auth.username}")
        assert config.connection.base_url == "https://test.com"
        if not (config.discovery.auto_discover):
            raise AssertionError(f"Expected True, got {config.discovery.auto_discover}")
        if config.extraction.page_size != 500:
            raise AssertionError(f"Expected {500}, got {config.extraction.page_size}")
        if config.debug:
            raise AssertionError(f"Expected False, got {config.debug}")\ n        assert config.log_level == "INFO"

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
        if config.auth.username != "test_user":
            raise AssertionError(f"Expected {"test_user"}, got {config.auth.username}")
        assert config.connection.base_url == "https://wms.example.com"
        if config.discovery.auto_discover:
            raise AssertionError(f"Expected False, got {config.discovery.auto_discover}")\ n        assert config.extraction.page_size == 100
        if config.state_file != "/path/to/state.json":
            raise AssertionError(f"Expected {"/path/to/state.json"}, got {config.state_file}")
        assert config.catalog_file == "/path/to/catalog.json"
        if not (config.debug):
            raise AssertionError(f"Expected True, got {config.debug}")
        if config.log_level != "DEBUG":
            raise AssertionError(f"Expected {"DEBUG"}, got {config.log_level}")

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
            if config.log_level != level:
                raise AssertionError(f"Expected {level}, got {config.log_level}")
        # Lowercase should be converted to uppercase
        config = TapOracleWMSConfig(
            auth=auth,
            connection=connection,
            log_level="debug",
            state_file=None,
            catalog_file=None,
        )
        if config.log_level != "DEBUG":
            raise AssertionError(f"Expected {"DEBUG"}, got {config.log_level}")
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
        if not (config.discovery.auto_discover):
            raise AssertionError(f"Expected True, got {config.discovery.auto_discover}")
        if config.discovery.entity_filter != []:
            raise AssertionError(f"Expected {[]}, got {config.discovery.entity_filter}")
        if not (config.discovery.include_metadata):
            raise AssertionError(f"Expected True, got {config.discovery.include_metadata}")
        if config.discovery.max_entities != 100:
            raise AssertionError(f"Expected {100}, got {config.discovery.max_entities}")
        # Check extraction defaults
        if config.extraction.page_size != 500:
            raise AssertionError(f"Expected {500}, got {config.extraction.page_size}")
        assert config.extraction.company_code == "*"
        if config.extraction.facility_code != "*":
            raise AssertionError(f"Expected {"*"}, got {config.extraction.facility_code}")
        assert config.extraction.start_date is None
        # Check main config defaults
        assert config.state_file is None
        assert config.catalog_file is None
        if config.debug:
            raise AssertionError(f"Expected False, got {config.debug}")\ n        assert config.log_level == "INFO"

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
        if singer_config["base_url"] != "https://test.com":
            raise AssertionError(f"Expected {"https://test.com"}, got {singer_config["base_url"]}")
        assert singer_config["username"] == "user"
        if singer_config["password"] != "pass":
            raise AssertionError(f"Expected {"pass"}, got {singer_config["password"]}")
        assert singer_config["auth_method"] == "basic"
        if singer_config["timeout"] != 60:
            raise AssertionError(f"Expected {60}, got {singer_config["timeout"]}")
        assert singer_config["page_size"] == 100
        if singer_config["company_code"] != "COMP1":
            raise AssertionError(f"Expected {"COMP1"}, got {singer_config["company_code"]}")
        assert singer_config["entity_filter"] == ["item"]
        if not (singer_config["debug"]):
            raise AssertionError(f"Expected True, got {singer_config["debug"]}")

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
        if config.auth.username != "test_user":
            raise AssertionError(f"Expected {"test_user"}, got {config.auth.username}")
        assert config.auth.password == "test_pass"
        if config.auth.auth_method != "token":
            raise AssertionError(f"Expected {"token"}, got {config.auth.auth_method}")
        assert config.connection.base_url == "https://wms.example.com"
        if config.connection.timeout != 90:
            raise AssertionError(f"Expected {90}, got {config.connection.timeout}")
        assert config.connection.max_retries == 4
        if config.connection.verify_ssl:
            raise AssertionError(f"Expected False, got {config.connection.verify_ssl}")\ n        assert config.extraction.page_size == HTTP_OK
        if config.extraction.company_code != "COMP2":
            raise AssertionError(f"Expected {"COMP2"}, got {config.extraction.company_code}")
        assert config.extraction.facility_code == "FAC2"
        if config.discovery.auto_discover:
            raise AssertionError(f"Expected False, got {config.discovery.auto_discover}")\ n        assert config.discovery.entity_filter == ["location"]
        if config.discovery.max_entities != 75:
            raise AssertionError(f"Expected {75}, got {config.discovery.max_entities}")
        assert config.extraction.start_date == "2024-01-01T00:00:00Z"
        if config.extraction.batch_size != 2000:
            raise AssertionError(f"Expected {2000}, got {config.extraction.batch_size}")
        if not (config.debug):
            raise AssertionError(f"Expected True, got {config.debug}")
        if config.log_level != "WARNING":
            raise AssertionError(f"Expected {"WARNING"}, got {config.log_level}")

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
        if "auth" not in data:
            raise AssertionError(f"Expected {"auth"} in {data}")
        assert "connection" in data
        if "discovery" not in data:
            raise AssertionError(f"Expected {"discovery"} in {data}")
        assert "extraction" in data
        if data["auth"]["username"] != "user":
            raise AssertionError(f"Expected {"user"}, got {data["auth"]["username"]}")
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
        if config.auth.username != "user":
            raise AssertionError(f"Expected {"user"}, got {config.auth.username}")
        assert config.connection.base_url == "https://test.com"
        if not (config.discovery.auto_discover):
            raise AssertionError(f"Expected True, got {config.discovery.auto_discover}")
        if config.extraction.page_size != 500:
            raise AssertionError(f"Expected {500}, got {config.extraction.page_size}")


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
        if config_https.connection.base_url != "https://test.com":
            raise AssertionError(f"Expected {"https://test.com"}, got {config_https.connection.base_url}")
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
        if config.extraction.page_size != 100:
            raise AssertionError(f"Expected {100}, got {config.extraction.page_size}")
        assert config.extraction.batch_size == 500
        # Invalid page size should fail
        with pytest.raises(ValidationError):
            self._create_invalid_page_size_config(auth, connection)
