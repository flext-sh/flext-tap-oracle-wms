"""Unit tests for config module using refactored configuration classes.

Tests for Oracle WMS tap configuration that extends flext-core patterns
instead of the old duplicated configuration classes.
"""

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License
from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_tap_oracle_wms.config import (
    OracleWMSTapConfig,
    TapOracleWMSConfig,
    create_wms_tap_config,
    get_wms_config_schema,
)

# Constants
HTTP_OK = 200
EXPECTED_BULK_SIZE = 2
EXPECTED_DATA_COUNT = 3


class TestOracleWMSTapConfig:
    """Test OracleWMSTapConfig model - extends FlextDataIntegrationConfig."""

    def test_basic_wms_config(self) -> None:
        """Test basic WMS tap configuration."""
        config = OracleWMSTapConfig(
            company_code="TEST",
            facility_code="FAC01",
            wms_api_version="v10",
            page_mode="sequenced",
        )
        assert config.company_code == "TEST"
        assert config.facility_code == "FAC01"
        assert config.wms_api_version == "v10"
        assert config.page_mode == "sequenced"

    def test_default_values(self) -> None:
        """Test default values are properly set."""
        config = OracleWMSTapConfig()
        assert config.company_code == "*"
        assert config.facility_code == "*"
        assert config.wms_api_version == "v10"
        assert config.page_mode == "sequenced"
        assert config.entities == []
        assert config.entity_filters == {}

    def test_page_mode_validation(self) -> None:
        """Test page mode validation."""
        # Valid modes
        config1 = OracleWMSTapConfig(page_mode="sequenced")
        assert config1.page_mode == "sequenced"

        config2 = OracleWMSTapConfig(page_mode="paged")
        assert config2.page_mode == "paged"

        # Invalid mode should fail
        with pytest.raises(ValidationError):
            OracleWMSTapConfig(page_mode="invalid_mode")

    def test_api_version_validation(self) -> None:
        """Test WMS API version validation."""
        # Valid versions
        config1 = OracleWMSTapConfig(wms_api_version="v10")
        assert config1.wms_api_version == "v10"

        config2 = OracleWMSTapConfig(wms_api_version="v12")
        assert config2.wms_api_version == "v12"

        # Invalid versions should fail
        with pytest.raises(ValidationError):
            OracleWMSTapConfig(wms_api_version="10")  # Missing 'v' prefix

        with pytest.raises(ValidationError):
            OracleWMSTapConfig(wms_api_version="vabc")  # Non-numeric after 'v'


class TestTapOracleWMSConfig:
    """Test TapOracleWMSConfig model - main configuration class."""

    def test_basic_oracle_wms_config(self) -> None:
        """Test basic Oracle WMS configuration."""
        config = TapOracleWMSConfig(
            host="localhost",
            username="test_user",
            password="test_pass",
            service_name="XE",
            port=1521,
        )
        assert config.host == "localhost"
        assert config.username == "test_user"
        assert config.password == "test_pass"
        assert config.service_name == "XE"
        assert config.port == 1521

    def test_get_oracle_config(self) -> None:
        """Test Oracle configuration generation using flext-core patterns."""
        config = TapOracleWMSConfig(
            host="oracle.example.com",
            username="oracle_user",
            password="oracle_pass",
            service_name="PRODDB",
            port=1522,
        )

        oracle_config = config.get_oracle_config()

        # Verify Oracle configuration uses flext-core patterns
        assert oracle_config.host == "oracle.example.com"
        assert oracle_config.username == "oracle_user"
        assert oracle_config.password.get_secret_value() == "oracle_pass"  # SecretStr requires get_secret_value()
        assert oracle_config.service_name == "PRODDB"
        assert oracle_config.port == 1522

    def test_get_wms_specific_config(self) -> None:
        """Test WMS-specific configuration extraction."""
        config = TapOracleWMSConfig(
            host="localhost",
            username="user",
            password="pass",
            service_name="XE",
            company_code="COMP01",
            facility_code="FAC01",
            wms_api_version="v11",
            page_mode="paged",
            entities=["item", "location"],
        )

        wms_config = config.get_wms_specific_config()

        expected_config = {
            "company_code": "COMP01",
            "facility_code": "FAC01",
            "wms_api_version": "v11",
            "page_mode": "paged",
            "entities": ["item", "location"],
            "entity_filters": {},
        }

        assert wms_config == expected_config

    def test_to_singer_config(self) -> None:
        """Test conversion to Singer protocol format."""
        config = TapOracleWMSConfig(
            host="singer.test",
            username="singer_user",
            password="singer_pass",
            service_name="SINGER",
            port=1523,
            company_code="SINGER_COMP",
            facility_code="SINGER_FAC",
        )

        singer_config = config.to_singer_config()

        # Verify all required fields are present
        assert singer_config["host"] == "singer.test"
        assert singer_config["username"] == "singer_user"
        assert singer_config["password"] == "singer_pass"
        assert singer_config["service_name"] == "SINGER"
        assert singer_config["port"] == 1523
        assert singer_config["company_code"] == "SINGER_COMP"
        assert singer_config["facility_code"] == "SINGER_FAC"

        # Verify flext-core data integration fields
        assert "batch_size" in singer_config
        assert "parallel_workers" in singer_config

    def test_from_singer_config(self) -> None:
        """Test creation from Singer protocol format."""
        singer_config = {
            "base_url": "from_singer.test",
            "username": "from_singer_user",
            "password": "from_singer_pass",
            "port": 1524,
            "service_name": "FROM_SINGER",
        }

        config = TapOracleWMSConfig.from_singer_config(singer_config)

        assert config.host == "from_singer.test"
        assert config.username == "from_singer_user"
        assert config.password == "from_singer_pass"
        assert config.port == 1524
        assert config.service_name == "FROM_SINGER"

    def test_from_singer_config_with_defaults(self) -> None:
        """Test creation from minimal Singer config with defaults."""
        singer_config = {
            "base_url": "minimal.test",
            "username": "minimal_user",
            "password": "minimal_pass",
        }

        config = TapOracleWMSConfig.from_singer_config(singer_config)

        assert config.host == "minimal.test"
        assert config.username == "minimal_user"
        assert config.password == "minimal_pass"
        assert config.port == 1521  # Default port
        assert config.service_name == "XE"  # Default service name


class TestFactoryFunctions:
    """Test factory functions for configuration creation."""

    def test_create_wms_tap_config(self) -> None:
        """Test WMS tap configuration factory function."""
        config_dict = {
            "base_url": "factory.test",
            "username": "factory_user",
            "password": "factory_pass",
            "port": 1525,
            "service_name": "FACTORY",
        }

        config = create_wms_tap_config(config_dict)

        assert isinstance(config, TapOracleWMSConfig)
        assert config.host == "factory.test"
        assert config.username == "factory_user"
        assert config.password == "factory_pass"
        assert config.port == 1525
        assert config.service_name == "FACTORY"

    def test_get_wms_config_schema(self) -> None:
        """Test WMS configuration schema generation."""
        schema = get_wms_config_schema()

        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "host" in schema["properties"]
        assert "username" in schema["properties"]
        assert "password" in schema["properties"]
        assert "service_name" in schema["properties"]
        assert "port" in schema["properties"]

        # Verify WMS-specific fields are in schema
        assert "company_code" in schema["properties"]
        assert "facility_code" in schema["properties"]
        assert "wms_api_version" in schema["properties"]
        assert "page_mode" in schema["properties"]


class TestConfigurationValidation:
    """Test configuration validation rules."""

    def test_required_fields_validation(self) -> None:
        """Test that required fields are enforced."""
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError):
            TapOracleWMSConfig()  # Missing required host, username, password, service_name

    def test_field_type_validation(self) -> None:
        """Test field type validation."""
        # Invalid port type
        with pytest.raises(ValidationError):
            TapOracleWMSConfig(
                host="test",
                username="user",
                password="pass",
                service_name="XE",
                port="invalid_port",  # Should be int
            )

    def test_entities_list_validation(self) -> None:
        """Test entities list validation."""
        config = TapOracleWMSConfig(
            host="test",
            username="user",
            password="pass",
            service_name="XE",
            entities=["item", "location", "inventory"],
        )

        assert config.entities == ["item", "location", "inventory"]
        assert isinstance(config.entities, list)
        assert all(isinstance(entity, str) for entity in config.entities)

    def test_entity_filters_dict_validation(self) -> None:
        """Test entity filters dictionary validation."""
        config = TapOracleWMSConfig(
            host="test",
            username="user",
            password="pass",
            service_name="XE",
            entity_filters={
                "item": {"status": "active"},
                "location": {"zone": "picking"},
            },
        )

        assert config.entity_filters == {
            "item": {"status": "active"},
            "location": {"zone": "picking"},
        }
        assert isinstance(config.entity_filters, dict)
