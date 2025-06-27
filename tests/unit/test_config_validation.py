"""Testes unitários para validação de configuração."""


import pytest

from tap_oracle_wms.config import (
    WMS_MAX_PAGE_SIZE,
    config_schema,
    validate_auth_config,
    validate_pagination_config,
)


class TestConfigValidation:
    """Testes para validação de configuração."""

    @pytest.mark.unit
    def test_validate_auth_config_basic_valid(self) -> None:
        """Testa validação de auth básica válida."""
        config = {
            "auth_method": "basic",
            "username": "test_user",
            "password": "test_password"
        }

        result = validate_auth_config(config)
        assert result is None

    @pytest.mark.unit
    def test_validate_auth_config_basic_missing_username(self) -> None:
        """Testa validação de auth básica sem username."""
        config = {
            "auth_method": "basic",
            "password": "test_password"
        }

        result = validate_auth_config(config)
        assert result == "Basic authentication requires username and password"

    @pytest.mark.unit
    def test_validate_auth_config_basic_missing_password(self) -> None:
        """Testa validação de auth básica sem password."""
        config = {
            "auth_method": "basic",
            "username": "test_user"
        }

        result = validate_auth_config(config)
        assert result == "Basic authentication requires username and password"

    @pytest.mark.unit
    def test_validate_auth_config_oauth2_valid(self) -> None:
        """Testa validação de OAuth2 válida."""
        config = {
            "auth_method": "oauth2",
            "oauth_client_id": "client123",
            "oauth_client_secret": "secret456",
            "oauth_token_url": "https://auth.example.com/token"
        }

        result = validate_auth_config(config)
        assert result is None

    @pytest.mark.unit
    def test_validate_auth_config_oauth2_missing_fields(self) -> None:
        """Testa validação de OAuth2 com campos faltando."""
        config = {
            "auth_method": "oauth2",
            "oauth_client_id": "client123"
        }

        result = validate_auth_config(config)
        assert "OAuth2 authentication requires" in result
        assert "oauth_client_secret" in result
        assert "oauth_token_url" in result

    @pytest.mark.unit
    def test_validate_auth_config_unknown_method(self) -> None:
        """Testa validação com método de auth desconhecido."""
        config = {
            "auth_method": "unknown_method"
        }

        result = validate_auth_config(config)
        assert result == "Unknown authentication method: unknown_method"

    @pytest.mark.unit
    def test_validate_pagination_config_valid(self) -> None:
        """Testa validação de paginação válida."""
        config = {
            "page_size": 1000
        }

        result = validate_pagination_config(config)
        assert result is None

    @pytest.mark.unit
    def test_validate_pagination_config_min_boundary(self) -> None:
        """Testa validação de paginação no limite mínimo."""
        config = {
            "page_size": 1
        }

        result = validate_pagination_config(config)
        assert result is None

    @pytest.mark.unit
    def test_validate_pagination_config_max_boundary(self) -> None:
        """Testa validação de paginação no limite máximo."""
        config = {
            "page_size": WMS_MAX_PAGE_SIZE
        }

        result = validate_pagination_config(config)
        assert result is None

    @pytest.mark.unit
    def test_validate_pagination_config_too_small(self) -> None:
        """Testa validação com page_size muito pequeno."""
        config = {
            "page_size": 0
        }

        result = validate_pagination_config(config)
        assert result == "Page size must be at least 1"

    @pytest.mark.unit
    def test_validate_pagination_config_too_large(self) -> None:
        """Testa validação com page_size muito grande."""
        config = {
            "page_size": WMS_MAX_PAGE_SIZE + 1
        }

        result = validate_pagination_config(config)
        assert result == "Page size cannot exceed 1250 (Oracle WMS limit)"

    @pytest.mark.unit
    def test_validate_pagination_config_negative(self) -> None:
        """Testa validação com page_size negativo."""
        config = {
            "page_size": -10
        }

        result = validate_pagination_config(config)
        assert result == "Page size must be at least 1"


class TestConfigSchema:
    """Testes para o schema de configuração."""

    @pytest.mark.unit
    def test_config_schema_exists(self) -> None:
        """Testa se o schema de configuração existe."""
        assert config_schema is not None

    @pytest.mark.unit
    def test_config_schema_structure(self) -> None:
        """Testa a estrutura do schema de configuração."""
        schema_dict = config_schema if isinstance(config_schema, dict) else config_schema.to_dict()

        assert isinstance(schema_dict, dict)
        assert "properties" in schema_dict

    @pytest.mark.unit
    def test_config_schema_required_properties(self) -> None:
        """Testa se propriedades obrigatórias estão presentes."""
        schema_dict = config_schema if isinstance(config_schema, dict) else config_schema.to_dict()
        properties = schema_dict.get("properties", {})

        required_props = ["base_url", "auth_method"]

        for prop in required_props:
            assert prop in properties, f"Property '{prop}' not found in schema"

    @pytest.mark.unit
    def test_config_schema_base_url_validation(self) -> None:
        """Testa validação de base_url no schema."""
        schema_dict = config_schema if isinstance(config_schema, dict) else config_schema.to_dict()
        properties = schema_dict.get("properties", {})

        base_url_prop = properties.get("base_url", {})

        # Verifica se tem pattern validation
        assert "pattern" in base_url_prop or "type" in base_url_prop

        # Verifica se tem examples
        if "examples" in base_url_prop:
            assert isinstance(base_url_prop["examples"], list)
            assert len(base_url_prop["examples"]) > 0

    @pytest.mark.unit
    def test_config_schema_auth_method_values(self) -> None:
        """Testa valores permitidos para auth_method."""
        schema_dict = config_schema if isinstance(config_schema, dict) else config_schema.to_dict()
        properties = schema_dict.get("properties", {})

        auth_method_prop = properties.get("auth_method", {})

        # Verifica se tem valores permitidos ou default
        has_validation = (
            "allowed_values" in auth_method_prop or
            "enum" in auth_method_prop or
            "default" in auth_method_prop
        )
        assert has_validation, "auth_method should have validation or default value"

    @pytest.mark.unit
    @pytest.mark.parametrize(("property_name", "expected_type"), [
        ("base_url", ["string"]),
        ("page_size", ["integer", "null"]),
        ("start_date", ["string", "null"]),
        ("entities", ["array", "null"]),
    ])
    def test_config_schema_property_types(self, property_name: str, expected_type: list) -> None:
        """Testa tipos de propriedades específicas."""
        schema_dict = config_schema if isinstance(config_schema, dict) else config_schema.to_dict()
        properties = schema_dict.get("properties", {})

        if property_name in properties:
            prop_config = properties[property_name]
            prop_type = prop_config.get("type", [])

            # Normaliza para lista se for string
            if isinstance(prop_type, str):
                prop_type = [prop_type]

            # Verifica se pelo menos um tipo esperado está presente
            type_match = any(t in prop_type for t in expected_type)
            assert type_match, f"Property '{property_name}' type {prop_type} not in expected {expected_type}"


class TestConfigValidationIntegration:
    """Testes de integração para validação de configuração."""

    @pytest.mark.unit
    def test_full_config_validation_basic_auth(self) -> None:
        """Testa validação completa com auth básica."""
        config = {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test_user",
            "password": "test_password",
            "page_size": 1000,
            "company_code": "TEST",
            "facility_code": "MAIN"
        }

        auth_result = validate_auth_config(config)
        page_result = validate_pagination_config(config)

        assert auth_result is None
        assert page_result is None

    @pytest.mark.unit
    def test_full_config_validation_oauth2(self) -> None:
        """Testa validação completa com OAuth2."""
        config = {
            "base_url": "https://wms.test.com",
            "auth_method": "oauth2",
            "oauth_client_id": "client123",
            "oauth_client_secret": "secret456",
            "oauth_token_url": "https://auth.test.com/token",
            "page_size": 500
        }

        auth_result = validate_auth_config(config)
        page_result = validate_pagination_config(config)

        assert auth_result is None
        assert page_result is None

    @pytest.mark.unit
    def test_config_validation_multiple_errors(self) -> None:
        """Testa configuração com múltiplos erros."""
        config = {
            "auth_method": "basic",  # Faltam username/password
            "page_size": 2000        # Acima do limite
        }

        auth_result = validate_auth_config(config)
        page_result = validate_pagination_config(config)

        assert auth_result is not None
        assert page_result is not None
        assert "username and password" in auth_result
        assert "1250" in page_result

    @pytest.mark.unit
    def test_config_validation_edge_cases(self) -> None:
        """Testa casos extremos de configuração."""
        # Configuração vazia
        empty_config = {}

        auth_result = validate_auth_config(empty_config)
        page_result = validate_pagination_config(empty_config)

        # Com configuração vazia, validation deve usar defaults ou detectar problemas
        # O comportamento específico depende da implementação, mas não deve quebrar
        assert isinstance(auth_result, (str, type(None)))
        assert isinstance(page_result, (str, type(None)))

    @pytest.mark.unit
    def test_config_validation_with_extra_fields(self) -> None:
        """Testa validação com campos extras não definidos."""
        config = {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test_user",
            "password": "test_password",
            "page_size": 1000,
            "extra_field": "should_be_ignored",
            "another_extra": 12345
        }

        auth_result = validate_auth_config(config)
        page_result = validate_pagination_config(config)

        # Campos extras não devem afetar validação dos campos obrigatórios
        assert auth_result is None
        assert page_result is None
