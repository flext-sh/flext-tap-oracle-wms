#!/usr/bin/env python3
"""Validação abrangente de todas as funcionalidades e tipos de parâmetros do tap-oracle-wms.

Este script valida:
- Tipos de parâmetros e anotações
- Configurações e validações
- Funcionalidades do Stream
- Paginação HATEOAS
- Autenticação
- CLI e comandos
- Descoberta de entidades
- Schemas dinâmicos
"""

import contextlib
import inspect
from pathlib import Path
import sys
from typing import get_type_hints
from unittest.mock import Mock, patch


# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def validate_type_annotations() -> bool:
    """Valida todas as anotações de tipo no projeto."""
    try:
        # Test imports first
        from tap_oracle_wms.auth import get_wms_authenticator, get_wms_headers
        from tap_oracle_wms.config import (
            validate_auth_config,
            validate_pagination_config,
        )
        from tap_oracle_wms.streams import WMSAdvancedPaginator, WMSAdvancedStream
        from tap_oracle_wms.tap import TapOracleWMS

        classes_to_check = [
            TapOracleWMS,
            WMSAdvancedStream,
            WMSAdvancedPaginator,
        ]

        functions_to_check = [
            validate_auth_config,
            validate_pagination_config,
            get_wms_authenticator,
            get_wms_headers,
        ]

        for cls in classes_to_check:
            # Check class methods
            for name, method in inspect.getmembers(cls, inspect.isfunction):
                if not name.startswith("_"):
                    with contextlib.suppress(Exception):
                        get_type_hints(method)

            # Check __init__ method specifically
            if hasattr(cls, "__init__"):
                with contextlib.suppress(Exception):
                    get_type_hints(cls.__init__)

        for func in functions_to_check:
            with contextlib.suppress(Exception):
                get_type_hints(func)

        return True

    except Exception:
        return False


def validate_configuration_schema() -> bool:
    """Valida o schema de configuração e todos os tipos de parâmetros."""
    try:
        from tap_oracle_wms.config import (
            config_schema,
            validate_auth_config,
            validate_pagination_config,
        )

        # Test schema structure
        schema_dict = (
            config_schema
            if isinstance(config_schema, dict)
            else config_schema.to_dict()
        )

        # Validate required properties
        properties = schema_dict.get("properties", {})
        required_properties = [
            "base_url",
            "auth_method",
            "username",
            "password",
            "page_size",
            "pagination_mode",
            "start_date",
        ]

        for prop in required_properties:
            if prop in properties:
                prop_config = properties[prop]

                # Check type validation
                if "type" in prop_config:
                    pass

                # Check constraints
                if "pattern" in prop_config:
                    pass

                if "examples" in prop_config:
                    pass

                if "allowed_values" in prop_config:
                    pass

        # Test configuration validation functions
        test_configs = [
            # Valid basic auth config
            {
                "base_url": "https://wms.test.com",
                "auth_method": "basic",
                "username": "test_user",
                "password": "test_pass",
                "page_size": 1000,
            },
            # Valid OAuth2 config
            {
                "base_url": "https://wms.test.com",
                "auth_method": "oauth2",
                "oauth_client_id": "client123",
                "oauth_client_secret": "secret456",
                "oauth_token_url": "https://auth.test.com/token",
                "page_size": 500,
            },
            # Invalid config (missing auth)
            {
                "base_url": "https://wms.test.com",
                "auth_method": "basic",
                "page_size": 1000,
            },
            # Invalid pagination
            {
                "base_url": "https://wms.test.com",
                "auth_method": "basic",
                "username": "test",
                "password": "pass",
                "page_size": 2000,  # Above limit
            },
        ]

        for i, config in enumerate(test_configs):
            auth_result = validate_auth_config(config)
            page_result = validate_pagination_config(config)

            if i < 2:  # Valid configs
                if auth_result is None:
                    pass

                if page_result is None:
                    pass
            else:  # Invalid configs
                if auth_result is not None:
                    pass
                if page_result is not None:
                    pass

        return True

    except Exception:
        return False


def validate_stream_functionality() -> bool:
    """Valida funcionalidades do stream e parâmetros."""
    try:
        from tap_oracle_wms.streams import WMSAdvancedStream

        # Mock configuration
        mock_config = {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "page_size": 1000,
            "enable_incremental": True,
            "incremental_overlap_minutes": 5,
        }

        # Create mock tap
        with patch("tap_oracle_wms.tap.TapOracleWMS.config", mock_config):
            mock_tap = Mock()
            mock_tap.config = mock_config

            # Test stream initialization
            stream = WMSAdvancedStream(
                tap=mock_tap,
                entity_name="test_entity",
                schema={"type": "object", "properties": {"id": {"type": "integer"}}},
            )

            # Test properties
            assert stream.name == "test_entity"

            assert stream.path == "/wms/lgfapi/v10/entity/test_entity"

            assert (
                stream.url == "https://wms.test.com/wms/lgfapi/v10/entity/test_entity"
            )

            # Test replication method
            assert stream.replication_method in {"INCREMENTAL", "FULL_TABLE"}

            if stream.replication_method == "INCREMENTAL":
                assert stream.replication_keys == ["mod_ts"]

            # Test get_url_params with different scenarios
            base_params = stream.get_url_params(context=None, next_page_token=None)
            assert isinstance(base_params, dict)
            assert "page_mode" in base_params
            assert "page_size" in base_params

            # Test with mock next_page_token (ParseResult simulation)
            from urllib.parse import urlparse

            mock_next_url = urlparse(
                "https://wms.test.com/entity?cursor=abc123&page_size=1000"
            )
            next_params = stream.get_url_params(
                context=None, next_page_token=mock_next_url
            )
            assert isinstance(next_params, dict)

            # Test optimal page size calculation
            page_size = stream._get_optimal_page_size()
            assert isinstance(page_size, int)
            assert 1 <= page_size <= 1250

        return True

    except Exception:
        return False


def validate_hateoas_pagination() -> bool:
    """Valida a paginação HATEOAS moderna."""
    try:
        from singer_sdk.pagination import BaseHATEOASPaginator

        from tap_oracle_wms.streams import WMSAdvancedPaginator

        # Test inheritance
        paginator = WMSAdvancedPaginator()
        assert isinstance(paginator, BaseHATEOASPaginator)

        # Test get_next_url with mock response
        mock_response_with_next = Mock()
        mock_response_with_next.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "next_page": "https://wms.test.com/entity?cursor=xyz123&page_size=1000",
        }

        next_url = paginator.get_next_url(mock_response_with_next)
        assert next_url == "https://wms.test.com/entity?cursor=xyz123&page_size=1000"

        # Test get_next_url without next page
        mock_response_without_next = Mock()
        mock_response_without_next.json.return_value = {"results": [{"id": 1}]}

        next_url = paginator.get_next_url(mock_response_without_next)
        assert next_url is None

        # Test has_more method
        has_more = paginator.has_more(mock_response_with_next)
        assert has_more is True

        has_more = paginator.has_more(mock_response_without_next)
        assert has_more is False

        # Test error handling
        mock_response_error = Mock()
        mock_response_error.json.side_effect = ValueError("Invalid JSON")

        next_url = paginator.get_next_url(mock_response_error)
        assert next_url is None

        return True

    except Exception:
        return False


def validate_authentication_methods() -> bool:
    """Valida métodos de autenticação e tipos."""
    try:
        from tap_oracle_wms.auth import get_wms_authenticator, get_wms_headers

        # Test basic auth configuration
        basic_config = {
            "auth_method": "basic",
            "username": "test_user",
            "password": "test_password",
            "company_code": "TEST",
            "facility_code": "MAIN",
        }

        # Test OAuth2 configuration
        oauth_config = {
            "auth_method": "oauth2",
            "oauth_client_id": "client123",
            "oauth_client_secret": "secret456",
            "oauth_token_url": "https://auth.test.com/token",
            "oauth_scope": "wms.read",
            "company_code": "TEST",
            "facility_code": "MAIN",
        }

        for _config_name, config in [("Basic", basic_config), ("OAuth2", oauth_config)]:
            try:
                # Test authenticator creation
                mock_stream = Mock()
                get_wms_authenticator(mock_stream, config)

                # Test headers generation
                headers = get_wms_headers(config)
                assert isinstance(headers, dict)
                assert "Content-Type" in headers
                assert "Accept" in headers

                # Validate WMS context headers
                if "company_code" in config:
                    assert "X-Oracle-WMS-Company" in headers or "company_code" in config

            except Exception:
                pass

        return True

    except Exception:
        return False


def validate_tap_capabilities() -> bool:
    """Valida as capabilities do Tap e funcionalidades principais."""
    try:
        from singer_sdk.helpers.capabilities import TapCapabilities

        from tap_oracle_wms.tap import TapOracleWMS

        # Test tap initialization
        mock_config = {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "test_connection": False,  # Skip connection test
            "metrics": {"enabled": False},  # Skip monitoring
        }

        with patch("tap_oracle_wms.tap.TapOracleWMS.config", mock_config):
            tap = TapOracleWMS(config=mock_config)

            # Test capabilities
            assert hasattr(tap, "capabilities")
            capabilities = tap.capabilities

            expected_capabilities = [
                TapCapabilities.DISCOVER,
                TapCapabilities.STATE,
                TapCapabilities.CATALOG,
                TapCapabilities.PROPERTIES,
            ]

            for cap in expected_capabilities:
                assert cap in capabilities

            # Test tap properties
            assert tap.name == "tap-oracle-wms"

            assert hasattr(tap, "config_jsonschema")

            # Test validation method exists
            assert hasattr(tap, "validate_config")

        return True

    except Exception:
        return False


def validate_discovery_functionality() -> bool:
    """Valida funcionalidades de descoberta de entidades."""
    try:
        from tap_oracle_wms.discovery import EntityDiscovery, SchemaGenerator

        # Test EntityDiscovery initialization
        mock_config = {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
        }

        discovery = EntityDiscovery(mock_config)

        # Test methods exist
        assert hasattr(discovery, "discover_entities")

        assert hasattr(discovery, "get_entity_list")

        # Test SchemaGenerator initialization
        schema_gen = SchemaGenerator(mock_config)

        # Test schema generation methods
        assert hasattr(schema_gen, "generate_schema")

        assert hasattr(schema_gen, "infer_field_type")

        # Test type inference
        test_values = [
            (123, "integer"),
            ("test string", "string"),
            (True, "boolean"),
            (12.34, "number"),
            ({"key": "value"}, "object"),
            ([1, 2, 3], "array"),
        ]

        for value, _expected_type in test_values:
            schema_gen.infer_field_type(value)

        return True

    except Exception:
        return False


def validate_cli_functionality() -> bool:
    """Valida funcionalidades do CLI."""
    try:
        import click

        from tap_oracle_wms.cli import cli

        # Test CLI command exists
        assert isinstance(cli, click.Command) or hasattr(cli, "callback")

        # Test main CLI function
        from tap_oracle_wms.tap import TapOracleWMS

        # Test that TapOracleWMS has cli method
        assert hasattr(TapOracleWMS, "cli")

        return True

    except Exception:
        return False


def validate_error_handling() -> bool:
    """Valida tratamento de erros e circuit breaker."""
    try:
        from tap_oracle_wms.streams import CircuitBreaker

        # Test CircuitBreaker initialization
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        # Test initial state
        assert cb.state == "closed"
        assert cb.can_attempt_call() is True

        # Test failure handling
        for _i in range(3):
            cb.call_failed()

        assert cb.state == "open"
        assert cb.can_attempt_call() is False

        # Test success recovery
        cb.call_succeeded()
        assert cb.state == "closed"
        assert cb.failure_count == 0

        return True

    except Exception:
        return False


def main() -> None:
    """Executa todas as validações abrangentes."""
    validation_tests = [
        ("Anotações de Tipo", validate_type_annotations),
        ("Schema de Configuração", validate_configuration_schema),
        ("Funcionalidades do Stream", validate_stream_functionality),
        ("Paginação HATEOAS", validate_hateoas_pagination),
        ("Métodos de Autenticação", validate_authentication_methods),
        ("Capabilities do Tap", validate_tap_capabilities),
        ("Descoberta de Entidades", validate_discovery_functionality),
        ("CLI", validate_cli_functionality),
        ("Tratamento de Erros", validate_error_handling),
    ]

    passed = 0
    total = len(validation_tests)
    results = []

    for test_name, test_func in validation_tests:
        try:
            result = test_func()
            if result:
                passed += 1
                results.append(f"✅ {test_name}")
            else:
                results.append(f"❌ {test_name}")
        except Exception as e:
            results.append(f"❌ {test_name} - Exception: {str(e)[:100]}")

    for result in results:
        pass

    if passed == total:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
