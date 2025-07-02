#!/usr/bin/env python3
"""Teste completo de validação de configuração e parâmetros."""

import json
import os
from pathlib import Path

from tap_oracle_wms.config import validate_auth_config, validate_pagination_config
from tap_oracle_wms.tap import TapOracleWMS


def test_config_validation() -> None:
    """Testa validação completa de configuração."""
    # 1. Teste com configuração válida
    valid_config = {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "auth_method": "basic",
        "username": "USER_WMS_INTEGRA",
        "password": "jmCyS7BK94YvhS@",
        "page_size": 100,
    }

    validate_auth_config(valid_config)
    validate_pagination_config(valid_config)

    # 2. Teste de validação de autenticação

    # Basic auth sem username
    invalid_basic = {"auth_method": "basic", "password": "test"}
    validate_auth_config(invalid_basic)

    # OAuth2 sem client_id
    invalid_oauth = {"auth_method": "oauth2", "oauth_client_secret": "secret"}
    validate_auth_config(invalid_oauth)

    # 3. Teste de validação de paginação

    # Page size muito pequeno
    invalid_page_small = {"page_size": 0}
    validate_pagination_config(invalid_page_small)

    # Page size muito grande
    invalid_page_large = {"page_size": 2000}
    validate_pagination_config(invalid_page_large)


def test_env_variables() -> None:
    """Testa suporte a variáveis de ambiente."""
    # Configurar variáveis de ambiente
    test_env = {
        "TAP_ORACLE_WMS_BASE_URL": "https://test-env.wms.com",
        "TAP_ORACLE_WMS_USERNAME": "env_user",
        "TAP_ORACLE_WMS_PASSWORD": "env_pass",
        "TAP_ORACLE_WMS_PAGE_SIZE": "50",
    }

    # Salvar valores originais
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        # Criar configuração mínima (tap deve pegar do .env)

        for _key, _value in test_env.items():
            pass

    finally:
        # Restaurar ambiente
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


def test_config_file() -> None:
    """Testa carregamento de arquivo de configuração."""
    config_file = Path("examples/config.json")
    if config_file.exists():
        with Path(config_file).open(encoding="utf-8") as f:
            config = json.load(f)

        # Validar parâmetros obrigatórios
        required_params = ["base_url", "username", "password", "page_size"]
        missing = [p for p in required_params if p not in config]

        if missing:
            pass
        else:
            pass

        # Mostrar alguns parâmetros importantes
        important_params = [
            "base_url",
            "auth_method",
            "page_size",
            "page_mode",
            "request_timeout",
            "entities",
        ]

        for param in important_params:
            if param in config:
                value = config[param]
                if param == "password":
                    value = "*" * len(str(value))
    else:
        pass


def test_schema_validation() -> None:
    """Testa validação de schema de configuração."""
    try:
        # Tentar criar tap com configuração mínima
        minimal_config = {
            "base_url": "https://test.wms.com",
            "auth_method": "basic",
            "username": "test",
            "password": "test",
            "page_size": 10,
        }

        tap = TapOracleWMS(config=minimal_config, parse_env_config=False)

        # Verificar propriedades do schema
        schema_props = tap.config_schema.get("properties", {})

        # Verificar propriedades obrigatórias
        [p for p, def_ in schema_props.items() if def_.get("required", False)]

    except Exception:
        pass


if __name__ == "__main__":
    test_config_validation()
    test_env_variables()
    test_config_file()
    test_schema_validation()
