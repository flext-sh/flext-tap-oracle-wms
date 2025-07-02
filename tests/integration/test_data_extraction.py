#!/usr/bin/env python3
"""Teste completo de extração de dados com diferentes page_size."""

import operator
import time

import httpx


def test_data_extraction_sizes() -> None:
    """Testa extração com diferentes tamanhos de página."""
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

    # Tamanhos de página para teste
    page_sizes = [1, 10, 50, 100, 250, 500, 1000]
    entity = "allocation"

    results = []

    for page_size in page_sizes:
        result = test_extraction_performance(
            entity,
            page_size,
            headers,
            base_url,
        )
        results.append((page_size, result))

    # Análise de performance

    # Extrair dados válidos
    valid_results = []
    for page_size, result in results:
        if result.startswith("✅"):
            # Parse do resultado
            parts = result.split(", ")
            if len(parts) >= 3:
                records_str = parts[0].split(" ")[1]
                time_str = parts[1].replace("s", "")
                bytes_str = parts[2].split(" ")[0]

                try:
                    records = int(records_str)
                    duration = float(time_str)
                    size_bytes = int(bytes_str)

                    valid_results.append(
                        {
                            "page_size": page_size,
                            "records": records,
                            "duration": duration,
                            "size_bytes": size_bytes,
                            "records_per_sec": records / duration
                            if duration > 0
                            else 0,
                            "bytes_per_record": size_bytes / records
                            if records > 0
                            else 0,
                        },
                    )
                except (ValueError, ZeroDivisionError):
                    pass

    if valid_results:
        for _r in valid_results:
            pass

        # Recomendações

        # Melhor rate
        max(valid_results, key=operator.itemgetter("records_per_sec"))

        # Menor overhead
        min(valid_results, key=operator.itemgetter("bytes_per_record"))

        # Balanced approach
        balanced = [r for r in valid_results if 100 <= r["page_size"] <= 500]
        if balanced:
            max(balanced, key=operator.itemgetter("records_per_sec"))


def test_extraction_performance(
    entity: str,
    page_size: int,
    headers: dict,
    base_url: str,
) -> str:
    """Testa performance de extração para um page_size específico."""
    try:
        start_time = time.time()

        url = f"{base_url}/{entity}"
        params = {
            "page_size": page_size,
            "page_mode": "sequenced",
        }

        with httpx.Client(timeout=60) as client:
            response = client.get(url, headers=headers, params=params)

            end_time = time.time()
            duration = end_time - start_time

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, dict) and "results" in data:
                    results_count = len(data["results"])
                    response_size = len(response.content)

                    # Verificar dados válidos
                    if results_count > 0:
                        first_record = data["results"][0]
                        has_id = (
                            "id" in first_record
                            if isinstance(first_record, dict)
                            else False
                        )

                        return (
                            f"✅ {results_count} regs, {duration:.2f}s, {response_size} bytes, "
                            f"ID={'✅' if has_id else '❌'}"
                        )
                    return "⚠️ 0 registros retornados"
                return f"❌ Formato inválido: {type(data)}"
            return f"❌ HTTP {response.status_code}"

    except Exception as e:
        return f"❌ {str(e)[:50]}"


def test_data_quality() -> None:
    """Testa qualidade dos dados extraídos."""
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
    entities = ["allocation", "order_hdr", "order_dtl"]

    for entity in entities:
        analyze_entity_data(entity, headers, base_url)


def analyze_entity_data(entity: str, headers: dict, base_url: str) -> str:
    """Analisa qualidade dos dados de uma entidade."""
    try:
        url = f"{base_url}/{entity}"
        params = {
            "page_size": 5,
            "page_mode": "sequenced",
        }

        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, dict) and "results" in data:
                    results = data["results"]

                    if not results:
                        return "❌ Nenhum registro encontrado"

                    # Análise do primeiro registro
                    first_record = results[0]

                    if not isinstance(first_record, dict):
                        return f"❌ Tipo inválido: {type(first_record)}"

                    # Contadores de qualidade
                    field_count = len(first_record)
                    has_id = "id" in first_record
                    has_timestamps = any(
                        field.endswith(("_ts", "_date")) for field in first_record
                    )
                    null_fields = sum(1 for v in first_record.values() if v is None)

                    # Verificar tipos de dados
                    type_variety = len(
                        {type(v).__name__ for v in first_record.values()},
                    )

                    quality_score = 0
                    if has_id:
                        quality_score += 2
                    if has_timestamps:
                        quality_score += 2
                    if null_fields < field_count * 0.3:  # < 30% null
                        quality_score += 2
                    if type_variety >= 3:  # Variety of data types
                        quality_score += 1
                    if field_count >= 10:  # Rich data structure
                        quality_score += 1

                    quality_level = (
                        "EXCELENTE"
                        if quality_score >= 7
                        else "BOA"
                        if quality_score >= 5
                        else "REGULAR"
                        if quality_score >= 3
                        else "BAIXA"
                    )

                    return (
                        f"✅ {len(results)} regs, {field_count} campos, "
                        f"ID={'✅' if has_id else '❌'}, "
                        f"TS={'✅' if has_timestamps else '❌'}, "
                        f"Qualidade={quality_level}"
                    )

                return f"❌ Formato inválido: {type(data)}"
            return f"❌ HTTP {response.status_code}"

    except Exception as e:
        return f"❌ Erro: {str(e)[:50]}"


def test_concurrent_extraction() -> None:
    """Testa extração concorrente de múltiplas entidades."""
    import asyncio

    import httpx

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
    entities = ["allocation", "order_hdr", "order_dtl"]

    async def extract_entity(entity: str) -> str:
        """Extrai dados de uma entidade específica."""
        try:
            start_time = time.time()

            async with httpx.AsyncClient(timeout=30) as client:
                url = f"{base_url}/{entity}"
                params = {"page_size": 10, "page_mode": "sequenced"}

                response = await client.get(url, headers=headers, params=params)
                duration = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "results" in data:
                        count = len(data["results"])
                        return f"✅ {entity}: {count} regs em {duration:.2f}s"
                    return f"❌ {entity}: formato inválido"
                return f"❌ {entity}: HTTP {response.status_code}"

        except Exception as e:
            return f"❌ {entity}: {str(e)[:30]}"

    async def run_concurrent():
        """Executa extrações concorrentes."""
        start_time = time.time()
        tasks = [extract_entity(entity) for entity in entities]
        results = await asyncio.gather(*tasks)
        total_duration = time.time() - start_time

        for _result in results:
            pass

        return total_duration

    # Executar teste concorrente
    try:
        total_time = asyncio.run(run_concurrent())

        # Comparar com extração sequencial

        sequential_start = time.time()
        for entity in entities:
            analyze_entity_data(entity, headers, base_url)
        sequential_time = time.time() - sequential_start

        (sequential_time - total_time) / sequential_time * 100

    except Exception:
        pass


if __name__ == "__main__":
    test_data_extraction_sizes()
    test_data_quality()
    test_concurrent_extraction()
