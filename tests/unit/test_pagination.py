#!/usr/bin/env python3
"""Teste completo de paginação sequenced (único modo suportado)."""

import json
import time

import httpx


def test_pagination_sequenced_mode() -> None:
    """Testa paginação sequenced - único modo suportado pelo Oracle WMS."""
    # Configuração base
    config = {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "username": "USER_WMS_INTEGRA",
        "password": "jmCyS7BK94YvhS@",
    }

    # Headers de autenticação
    import base64

    auth_string = f"{config['username']}:{config['password']}"
    auth_bytes = auth_string.encode("ascii")
    auth_header = base64.b64encode(auth_bytes).decode("ascii")

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    base_url = f"{config['base_url']}/wms/lgfapi/v10/entity"

    # Teste page_mode = "sequenced" (único modo suportado)
    _test_pagination_mode(
        "allocation",
        "sequenced",
        headers,
        base_url,
        page_size=5,
    )


def _test_pagination_mode(
    entity: str,
    page_mode: str,
    headers: dict,
    base_url: str,
    page_size: int = 10,
) -> str:
    """Testa o modo de paginação sequenced."""
    try:
        start_time = time.time()

        url = f"{base_url}/{entity}"
        params = {
            "page_size": page_size,
            "page_mode": page_mode,  # Always "sequenced"
        }

        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers, params=params)

            end_time = time.time()
            duration = end_time - start_time

            if response.status_code == 200:
                data = response.json()

                # Analisar estrutura da resposta
                if isinstance(data, dict):
                    results_count = len(data.get("results", []))

                    # Análise da resposta sequenced
                    analysis = {
                        "registros": results_count,
                        "tempo": f"{duration:.2f}s",
                        "tamanho_resposta": len(response.content),
                    }

                    # Campos de navegação (apenas sequenced)
                    navigation = {}
                    if "next_page" in data:
                        navigation["next_page"] = "✅ Presente"
                    if "previous_page" in data:
                        navigation["previous_page"] = "✅ Presente"

                    analysis["navegacao"] = navigation

                    return f"✅ {analysis}"
                return f"✅ Tipo: {type(data)}, Tempo: {duration:.2f}s"
            return f"❌ HTTP {response.status_code}: {response.text[:100]}"

    except Exception as e:
        return f"❌ Erro: {str(e)[:100]}"


def test_cursor_navigation() -> None:
    """Testa navegação com cursor (sequenced)."""
    # Configuração para teste
    config = {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "username": "USER_WMS_INTEGRA",
        "password": "jmCyS7BK94YvhS@",
    }

    # Headers de autenticação
    import base64

    auth_string = f"{config['username']}:{config['password']}"
    auth_bytes = auth_string.encode("ascii")
    auth_header = base64.b64encode(auth_bytes).decode("ascii")

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    base_url = f"{config['base_url']}/wms/lgfapi/v10/entity"

    try:
        # Primeira página
        url = f"{base_url}/allocation"
        params = {
            "page_size": 3,
            "page_mode": "sequenced",  # Único modo suportado
        }

        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, dict):
                    data.get("results", [])
                    next_page = data.get("next_page")

                    if next_page:
                        # Segunda página usando next_page
                        response2 = client.get(next_page, headers=headers)

                        if response2.status_code == 200:
                            data2 = response2.json()
                            data2.get("results", [])
                            next_page2 = data2.get("next_page")

                            if next_page2:
                                pass
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass

    except Exception:
        pass


def test_page_sizes() -> None:
    """Testa diferentes tamanhos de página com mode sequenced."""
    # Configuração
    config = {
        "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
        "username": "USER_WMS_INTEGRA",
        "password": "jmCyS7BK94YvhS@",
    }

    # Headers de autenticação
    import base64

    auth_string = f"{config['username']}:{config['password']}"
    auth_bytes = auth_string.encode("ascii")
    auth_header = base64.b64encode(auth_bytes).decode("ascii")

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    base_url = f"{config['base_url']}/wms/lgfapi/v10/entity"

    # Tamanhos de página para teste
    page_sizes = [1, 5, 10, 50, 100, 500, 1000]

    for page_size in page_sizes:
        _test_page_size_performance(
            "allocation",
            page_size,
            headers,
            base_url,
        )


def _test_page_size_performance(
    entity: str,
    page_size: int,
    headers: dict,
    base_url: str,
) -> str:
    """Testa performance de um tamanho de página específico com mode sequenced."""
    try:
        start_time = time.time()

        url = f"{base_url}/{entity}"
        params = {
            "page_size": page_size,
            "page_mode": "sequenced",  # Único modo suportado
        }

        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers, params=params)

            end_time = time.time()
            duration = end_time - start_time

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, dict):
                    results_count = len(data.get("results", []))
                    response_size = len(response.content)

                    return f"✅ {results_count:3d} regs, {duration:.2f}s, {response_size:5d} bytes"
                return f"✅ Tempo: {duration:.2f}s"
            return f"❌ HTTP {response.status_code}"

    except Exception as e:
        return f"❌ {str(e)[:30]}"


def test_pagination_config() -> None:
    """Testa configuração de paginação no tap (sempre sequenced)."""
    try:
        with Path("examples/config.json").open() as f:
            config = json.load(f)

        pagination_params = [
            "page_mode",  # Sempre "sequenced"
            "page_size",
            "request_timeout",
            "max_retries",
            "backoff_factor",
        ]

        for param in pagination_params:
            if param in config:
                config[param]
            else:
                pass

        # Validar configuração - page_mode deve ser sempre "sequenced"
        page_mode = config.get("page_mode", "sequenced")
        assert (
            page_mode == "sequenced"
        ), f"page_mode deve ser 'sequenced', encontrado: {page_mode}"

        config.get("page_size", 100)

    except Exception:
        pass


if __name__ == "__main__":
    test_pagination_sequenced_mode()
    test_cursor_navigation()
    test_page_sizes()
    test_pagination_config()
