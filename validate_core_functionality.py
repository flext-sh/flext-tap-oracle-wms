#!/usr/bin/env python3
"""Validação de funcionalidades principais do tap-oracle-wms modernizado."""

from pathlib import Path
import sys


# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_imports() -> bool:
    """Testa se todos os imports principais funcionam."""
    try:
        # Core imports
        from singer_sdk.helpers.capabilities import TapCapabilities

        # Singer SDK imports
        from singer_sdk.pagination import BaseHATEOASPaginator

        from tap_oracle_wms.auth import get_wms_headers
        from tap_oracle_wms.config import config_schema, validate_auth_config
        from tap_oracle_wms.streams import WMSAdvancedPaginator, WMSAdvancedStream
        from tap_oracle_wms.tap import TapOracleWMS

        return True

    except ImportError:
        return False


def test_configuration_validation() -> bool:
    """Testa validação de configuração."""
    try:
        from tap_oracle_wms.config import (
            validate_auth_config,
            validate_pagination_config,
        )

        # Configuração válida básica
        valid_config = {
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "page_size": 1000,
        }

        auth_result = validate_auth_config(valid_config)
        page_result = validate_pagination_config(valid_config)

        if auth_result is None and page_result is None:
            pass

        # Configuração inválida
        invalid_config = {
            "auth_method": "basic",
            "page_size": 2000,  # Acima do limite
        }

        auth_result = validate_auth_config(invalid_config)
        page_result = validate_pagination_config(invalid_config)

        return bool(auth_result is not None or page_result is not None)

    except Exception:
        return False


def test_paginator() -> bool:
    """Testa o paginador HATEOAS."""
    try:
        from unittest.mock import Mock

        from singer_sdk.pagination import BaseHATEOASPaginator

        from tap_oracle_wms.streams import WMSAdvancedPaginator

        # Cria paginador
        paginator = WMSAdvancedPaginator()

        # Verifica herança
        if not isinstance(paginator, BaseHATEOASPaginator):
            return False

        # Testa resposta com next_page
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1}],
            "next_page": "https://test.com/next?cursor=abc",
        }

        next_url = paginator.get_next_url(mock_response)
        if next_url != "https://test.com/next?cursor=abc":
            return False

        has_more = paginator.has_more(mock_response)
        if not has_more:
            return False

        # Testa resposta sem next_page
        mock_response.json.return_value = {"results": []}

        next_url = paginator.get_next_url(mock_response)
        return not next_url is not None

    except Exception:
        return False


def test_stream_basic_functionality() -> bool:
    """Testa funcionalidades básicas do stream."""
    try:
        from unittest.mock import Mock

        from tap_oracle_wms.streams import WMSAdvancedStream

        # Mock tap simples
        mock_tap = Mock()
        mock_tap.config = {
            "base_url": "https://test.com",
            "enable_incremental": True,
        }

        # Cria stream
        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        # Testa propriedades básicas
        if stream.name != "test_entity":
            return False

        if not stream.path.endswith("test_entity"):
            return False

        if not stream.url.startswith("https://test.com"):
            return False

        # Testa método de replicação
        return not stream.replication_method not in {"INCREMENTAL", "FULL_TABLE"}

    except Exception:
        return False


def test_tap_capabilities() -> bool:
    """Testa as capabilities do tap."""
    try:
        from singer_sdk.helpers.capabilities import TapCapabilities

        from tap_oracle_wms.tap import TapOracleWMS

        # Verifica se capabilities existem
        if not hasattr(TapOracleWMS, "capabilities"):
            return False

        capabilities = TapOracleWMS.capabilities

        # Verifica capabilities essenciais
        required_caps = [
            TapCapabilities.DISCOVER,
            TapCapabilities.STATE,
            TapCapabilities.CATALOG,
        ]

        return all(cap in capabilities for cap in required_caps)

    except Exception:
        return False


def test_configuration_schema() -> bool:
    """Testa o schema de configuração."""
    try:
        from tap_oracle_wms.config import config_schema

        # Converte para dict se necessário
        if hasattr(config_schema, "to_dict"):
            schema_dict = config_schema.to_dict()
        else:
            schema_dict = config_schema

        # Verifica estrutura básica
        if not isinstance(schema_dict, dict):
            return False

        properties = schema_dict.get("properties", {})

        # Verifica propriedades essenciais
        required_props = ["base_url", "auth_method", "username", "password"]

        for prop in required_props:
            if prop not in properties:
                return False

        # Verifica se base_url tem validação de pattern
        base_url_prop = properties.get("base_url", {})
        if "pattern" in base_url_prop:
            pass

        return True

    except Exception:
        return False


def main() -> None:
    """Executa validações principais."""
    tests = [
        ("Imports", test_imports),
        ("Validação de Configuração", test_configuration_validation),
        ("Paginador HATEOAS", test_paginator),
        ("Stream Básico", test_stream_basic_functionality),
        ("Capabilities do Tap", test_tap_capabilities),
        ("Schema de Configuração", test_configuration_schema),
    ]

    passed = 0
    total = len(tests)

    for _test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception:
            pass

    if passed == total:

        # Resumo dos tipos de parâmetros validados

        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
