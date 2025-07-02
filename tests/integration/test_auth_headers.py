#!/usr/bin/env python3
"""Teste completo de autenticação e headers HTTP."""

import base64
import json
import time
from pathlib import Path

import httpx


def test_authentication_methods() -> None:
    """Testa diferentes métodos de autenticação."""
    # Configuração base
    config = {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "username": "USER_WMS_INTEGRA",
        "password": "jmCyS7BK94YvhS@",
    }

    base_url = f"{config['base_url']}/wms/lgfapi/v10/entity"
    test_url = f"{base_url}/allocation"
    params = {"page_size": 1, "page_mode": "sequenced"}

    # 1. Teste Basic Authentication (método atual)

    auth_string = f"{config['username']}:{config['password']}"
    auth_bytes = auth_string.encode("ascii")
    auth_header = base64.b64encode(auth_bytes).decode("ascii")

    basic_headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    test_auth_method("Basic Auth", test_url, basic_headers, params)

    # 2. Teste sem autenticação (deve falhar)

    no_auth_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    test_auth_method("Sem Auth", test_url, no_auth_headers, params)

    # 3. Teste com credenciais inválidas

    invalid_auth = base64.b64encode(b"invalid:credentials").decode("ascii")
    invalid_headers = {
        "Authorization": f"Basic {invalid_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    test_auth_method("Credenciais Inválidas", test_url, invalid_headers, params)


def test_auth_method(method_name: str, url: str, headers: dict, params: dict) -> str:
    """Testa um método de autenticação específico."""
    try:
        start_time = time.time()

        with httpx.Client(timeout=10) as client:
            response = client.get(url, headers=headers, params=params)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "results" in data:
                    count = len(data["results"])
                    return f"✅ Sucesso - {count} registros em {duration:.2f}s"
                return f"✅ Sucesso - formato: {type(data)} em {duration:.2f}s"
            if response.status_code == 401:
                return f"❌ Unauthorized (401) - esperado para {method_name}"
            if response.status_code == 403:
                return "❌ Forbidden (403) - sem permissão"
            return f"❌ HTTP {response.status_code} em {duration:.2f}s"

    except Exception as e:
        return f"❌ Erro: {str(e)[:50]}"


def test_http_headers() -> None:
    """Testa diferentes configurações de headers HTTP."""
    # Configuração base
    config = {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "username": "USER_WMS_INTEGRA",
        "password": "jmCyS7BK94YvhS@",
    }

    # Base auth header
    auth_string = f"{config['username']}:{config['password']}"
    auth_bytes = auth_string.encode("ascii")
    auth_header = base64.b64encode(auth_bytes).decode("ascii")

    base_url = f"{config['base_url']}/wms/lgfapi/v10/entity"
    test_url = f"{base_url}/allocation"
    params = {"page_size": 3, "page_mode": "sequenced"}

    # 1. Headers básicos
    basic_headers = {
        "Authorization": f"Basic {auth_header}",
    }
    test_headers_config("Básico", test_url, basic_headers, params)

    # 2. Headers com Content-Type
    content_headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
    }
    test_headers_config("Content-Type", test_url, content_headers, params)

    # 3. Headers completos (recomendado)
    full_headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "tap-oracle-wms/1.0.0",
    }
    test_headers_config("Completo", test_url, full_headers, params)

    # 4. Headers com compressão
    compression_headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "tap-oracle-wms/1.0.0",
    }
    test_headers_config("Compressão", test_url, compression_headers, params)

    # 5. Headers com cache control
    cache_headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": "tap-oracle-wms/1.0.0",
    }
    test_headers_config("Cache Control", test_url, cache_headers, params)


def test_headers_config(config_name: str, url: str, headers: dict, params: dict) -> str:
    """Testa uma configuração específica de headers."""
    try:
        start_time = time.time()

        with httpx.Client(timeout=10) as client:
            response = client.get(url, headers=headers, params=params)
            duration = time.time() - start_time

            # Analisar resposta
            response_size = len(response.content)
            compression_info = ""

            # Verificar se houve compressão
            content_encoding = response.headers.get("content-encoding", "")
            if content_encoding:
                compression_info = f", compressão: {content_encoding}"

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "results" in data:
                    count = len(data["results"])
                    return (
                        f"✅ {count} regs, {duration:.2f}s, "
                        f"{response_size} bytes{compression_info}"
                    )
                return f"✅ {duration:.2f}s, {response_size} bytes{compression_info}"
            return f"❌ HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Erro: {str(e)[:50]}"


def test_tap_authentication() -> None:
    """Testa autenticação através do tap."""
    try:
        # Importar tap
        from tap_oracle_wms.auth import get_wms_headers
        from tap_oracle_wms.tap import TapOracleWMS

        # Configuração do tap
        config = {
            "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
            "auth_method": "basic",
            "username": "USER_WMS_INTEGRA",
            "password": "jmCyS7BK94YvhS@",
            "page_size": 5,
        }

        TapOracleWMS(config=config, parse_env_config=False)

        wms_headers = get_wms_headers(config)

        # Listar headers importantes
        important_headers = ["Content-Type", "Accept", "User-Agent"]
        for header in important_headers:
            if header in wms_headers:
                pass
            else:
                pass

        # Verificar se config tem tudo necessário
        required_auth_fields = ["auth_method", "username", "password"]
        missing_fields = [
            field for field in required_auth_fields if not config.get(field)
        ]

        if missing_fields:
            pass
        else:
            pass

    except ImportError:
        pass
    except Exception:
        pass


def test_auth_config_file() -> None:
    """Testa configuração de autenticação via arquivo."""
    config_file = Path("examples/config.json")
    if config_file.exists():
        with Path(config_file).open() as f:
            config = json.load(f)

        # Verificar campos de autenticação
        auth_fields = ["auth_method", "username", "password"]

        for field in auth_fields:
            if field in config:
                if field == "password":
                    pass
                else:
                    pass
            else:
                pass

        # Testar se autenticação funciona
        if all(field in config for field in auth_fields):
            # Construir headers do arquivo
            auth_string = f"{config['username']}:{config['password']}"
            auth_bytes = auth_string.encode("ascii")
            auth_header = base64.b64encode(auth_bytes).decode("ascii")

            headers = {
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            # Testar API
            base_url = f"{config['base_url']}/wms/lgfapi/v10/entity"
            test_url = f"{base_url}/allocation"
            params = {"page_size": 1, "page_mode": "sequenced"}

            test_auth_method("Config File", test_url, headers, params)
        else:
            pass

    else:
        pass


def test_connection_security() -> None:
    """Testa aspectos de segurança da conexão."""
    # Configuração
    config = {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "username": "USER_WMS_INTEGRA",
        "password": "jmCyS7BK94YvhS@",
    }

    # Headers básicos
    auth_string = f"{config['username']}:{config['password']}"
    auth_bytes = auth_string.encode("ascii")
    auth_header = base64.b64encode(auth_bytes).decode("ascii")

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    base_url = f"{config['base_url']}/wms/lgfapi/v10/entity"
    test_url = f"{base_url}/allocation"
    params = {"page_size": 1}

    if config["base_url"].startswith("https://"):
        pass
    else:
        pass

    try:
        with httpx.Client(timeout=10, verify=True) as client:
            response = client.get(test_url, headers=headers, params=params)

            if response.status_code == 200:
                # Verificar headers de segurança
                security_headers = [
                    "strict-transport-security",
                    "x-content-type-options",
                    "x-frame-options",
                    "x-xss-protection",
                ]

                for header in security_headers:
                    response.headers.get(header, "Não presente")

            else:
                pass

    except Exception as e:
        if "ssl" in str(e).lower():
            pass
        else:
            pass

    try:
        start_time = time.time()
        with httpx.Client(timeout=5) as client:
            response = client.get(test_url, headers=headers, params=params)
            time.time() - start_time

            if response.status_code == 200:
                pass
            else:
                pass

    except httpx.TimeoutException:
        pass
    except Exception:
        pass


if __name__ == "__main__":
    test_authentication_methods()
    test_http_headers()
    test_tap_authentication()
    test_auth_config_file()
    test_connection_security()
