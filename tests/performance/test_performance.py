"""Testes de performance para tap-oracle-wms."""

import os
import threading
import time
from unittest.mock import Mock, patch

import psutil
import pytest

from tap_oracle_wms.streams import WMSAdvancedPaginator, WMSAdvancedStream
from tap_oracle_wms.tap import TapOracleWMS


class TestPerformanceBasic:
    """Testes básicos de performance."""

    @pytest.fixture
    def perf_config(self):
        """Configuração para testes de performance."""
        return {
            "base_url": "https://wms.perf.test.com",
            "auth_method": "basic",
            "username": "perf_user",
            "password": "perf_pass",
            "page_size": 1000,
            "enable_incremental": True,
            "test_connection": False
        }

    @pytest.fixture
    def large_entity_list(self):
        """Lista grande de entidades para teste."""
        return [f"entity_{i:04d}" for i in range(100)]

    @pytest.fixture
    def large_schema(self):
        """Schema grande para teste."""
        properties = {}
        for i in range(50):
            properties[f"field_{i:02d}"] = {"type": "string"}

        return {
            "type": "object",
            "properties": properties,
            "required": [f"field_{i:02d}" for i in range(10)]
        }

    @pytest.mark.performance
    @pytest.mark.slow
    def test_tap_initialization_performance(self, perf_config, large_entity_list, large_schema) -> None:
        """Testa performance de inicialização do tap."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities") as mock_discovery:
            with patch("tap_oracle_wms.discovery.SchemaGenerator.generate_schema") as mock_schema:
                mock_discovery.return_value = large_entity_list
                mock_schema.return_value = large_schema

                # Medir tempo de inicialização
                start_time = time.time()

                tap = TapOracleWMS(config=perf_config)

                initialization_time = time.time() - start_time

                # Inicialização deve ser rápida mesmo com muitas entidades
                assert initialization_time < 5.0  # Menos de 5 segundos
                assert tap is not None

    @pytest.mark.performance
    @pytest.mark.slow
    def test_stream_discovery_performance(self, perf_config, large_entity_list, large_schema) -> None:
        """Testa performance do discovery de streams."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities") as mock_discovery:
            with patch("tap_oracle_wms.discovery.SchemaGenerator.generate_schema") as mock_schema:
                mock_discovery.return_value = large_entity_list
                mock_schema.return_value = large_schema

                tap = TapOracleWMS(config=perf_config)

                # Medir tempo de discovery
                start_time = time.time()

                streams = tap.discover_streams()

                discovery_time = time.time() - start_time

                # Discovery deve ser eficiente
                assert discovery_time < 10.0  # Menos de 10 segundos
                assert len(streams) == len(large_entity_list)

    @pytest.mark.performance
    def test_paginator_performance_large_response(self) -> None:
        """Testa performance do paginator com resposta grande."""
        # Criar resposta grande (10MB simulado)
        large_response_data = {
            "result_count": 10000,
            "page_count": 10,
            "page_nbr": 1,
            "next_page": "https://wms.test.com/next",
            "results": [
                {
                    "id": i,
                    "large_field": "A" * 1000,  # 1KB per record
                    "mod_ts": f"2024-01-01T10:{i % 60:02d}:00Z"
                }
                for i in range(1000)  # 1MB total
            ]
        }

        paginator = WMSAdvancedPaginator()

        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = large_response_data

        # Medir tempo de processamento
        start_time = time.time()

        has_more = paginator.has_more(mock_response)
        next_url = paginator.get_next_url(mock_response)

        processing_time = time.time() - start_time

        # Processamento deve ser rápido mesmo com resposta grande
        assert processing_time < 1.0  # Menos de 1 segundo
        assert has_more is True
        assert next_url is not None

    @pytest.mark.performance
    def test_stream_url_params_performance(self, perf_config) -> None:
        """Testa performance de geração de parâmetros de URL."""
        mock_tap = Mock()
        mock_tap.config = perf_config
        mock_tap.apply_entity_filters = Mock(return_value={})
        mock_tap.apply_incremental_filters = Mock(return_value={"mod_ts__gte": "2024-01-01T10:00:00Z"})

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="performance_entity",
            schema={"type": "object", "properties": {"id": {"type": "integer"}}}
        )

        # Medir tempo de geração de parâmetros (múltiplas vezes)
        num_iterations = 1000
        start_time = time.time()

        for _ in range(num_iterations):
            stream.get_url_params(context=None, next_page_token=None)

        total_time = time.time() - start_time
        avg_time = total_time / num_iterations

        # Geração deve ser muito rápida
        assert avg_time < 0.01  # Menos de 10ms por geração
        assert total_time < 10.0  # Total menos de 10 segundos


class TestPerformanceMemory:
    """Testes de performance de memória."""

    @pytest.fixture
    def memory_config(self):
        """Configuração para testes de memória."""
        return {
            "base_url": "https://wms.memory.test.com",
            "auth_method": "basic",
            "username": "memory_user",
            "password": "memory_pass",
            "page_size": 1000,
            "test_connection": False
        }

    @pytest.mark.performance
    @pytest.mark.slow
    def test_memory_usage_large_dataset(self, memory_config) -> None:
        """Testa uso de memória com dataset grande."""
        # Criar dataset grande simulado
        large_entities = [f"entity_{i:04d}" for i in range(50)]

        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities") as mock_discovery:
            with patch("tap_oracle_wms.discovery.SchemaGenerator.generate_schema") as mock_schema:
                mock_discovery.return_value = large_entities
                mock_schema.return_value = {
                    "type": "object",
                    "properties": {f"field_{i}": {"type": "string"} for i in range(20)}
                }

                # Medir memória antes
                process = psutil.Process(os.getpid())
                memory_before = process.memory_info().rss / 1024 / 1024  # MB

                # Criar tap e streams
                tap = TapOracleWMS(config=memory_config)
                streams = tap.discover_streams()

                # Forçar criação de todas as estruturas
                for stream in streams:
                    stream.get_new_paginator()
                    stream.get_url_params(context=None, next_page_token=None)

                # Medir memória depois
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = memory_after - memory_before

                # Aumento de memória deve ser razoável
                assert memory_increase < 100  # Menos de 100MB para 50 entidades
                assert len(streams) == len(large_entities)

    @pytest.mark.performance
    def test_memory_leak_detection(self, memory_config) -> None:
        """Testa detecção de vazamentos de memória."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities") as mock_discovery:
            mock_discovery.return_value = ["test_entity"]

            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Criar e destruir taps múltiplas vezes
            for _i in range(10):
                tap = TapOracleWMS(config=memory_config)
                streams = tap.discover_streams()

                # Simular uso das streams
                for stream in streams:
                    stream.get_new_paginator()

                # Limpar referências
                del tap
                del streams

            # Medir memória final
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = final_memory - initial_memory

            # Crescimento deve ser mínimo (sem vazamentos significativos)
            assert memory_growth < 20  # Menos de 20MB de crescimento

    @pytest.mark.performance
    def test_paginator_memory_efficiency(self) -> None:
        """Testa eficiência de memória do paginator."""
        paginator = WMSAdvancedPaginator()

        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Processar múltiplas respostas grandes
        for _i in range(100):
            large_response = {
                "result_count": 1000,
                "results": [{"id": j, "data": f"data_{j}"} for j in range(100)]
            }

            mock_response = Mock()
            mock_response.json.return_value = large_response

            paginator.has_more(mock_response)
            paginator.get_next_url(mock_response)

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        # Paginator não deve acumular memória significativamente
        assert memory_increase < 50  # Menos de 50MB para 100 operações


class TestPerformanceConcurrency:
    """Testes de performance de concorrência."""

    @pytest.fixture
    def concurrency_config(self):
        """Configuração para testes de concorrência."""
        return {
            "base_url": "https://wms.concurrent.test.com",
            "auth_method": "basic",
            "username": "concurrent_user",
            "password": "concurrent_pass",
            "page_size": 500,
            "test_connection": False
        }

    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_tap_creation(self, concurrency_config) -> None:
        """Testa criação concorrente de taps."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities") as mock_discovery:
            mock_discovery.return_value = ["concurrent_entity"]

            results = []
            errors = []

            def create_tap(thread_id) -> None:
                try:
                    start_time = time.time()
                    tap = TapOracleWMS(config=concurrency_config)
                    streams = tap.discover_streams()
                    end_time = time.time()

                    results.append({
                        "thread_id": thread_id,
                        "time": end_time - start_time,
                        "streams_count": len(streams)
                    })
                except Exception as e:
                    errors.append({"thread_id": thread_id, "error": str(e)})

            # Criar múltiplas threads
            threads = []
            num_threads = 5

            for i in range(num_threads):
                thread = threading.Thread(target=create_tap, args=(i,))
                threads.append(thread)

            # Executar todas as threads
            start_time = time.time()
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            total_time = time.time() - start_time

            # Verificar resultados
            assert len(errors) == 0  # Nenhum erro deve ocorrer
            assert len(results) == num_threads  # TODOs devem completar
            assert total_time < 30.0  # Deve completar em tempo razoável

            # Verificar que todos criaram streams
            for result in results:
                assert result["streams_count"] > 0
                assert result["time"] < 10.0  # Cada thread deve ser rápida

    @pytest.mark.performance
    def test_concurrent_paginator_usage(self) -> None:
        """Testa uso concorrente de paginators."""
        results = []
        errors = []

        def use_paginator(thread_id) -> None:
            try:
                paginator = WMSAdvancedPaginator()

                for _i in range(10):
                    response_data = {
                        "result_count": 100,
                        "results": [{"id": j} for j in range(10)]
                    }

                    mock_response = Mock()
                    mock_response.json.return_value = response_data

                    paginator.has_more(mock_response)
                    paginator.get_next_url(mock_response)

                results.append({"thread_id": thread_id, "success": True})
            except Exception as e:
                errors.append({"thread_id": thread_id, "error": str(e)})

        # Executar múltiplas threads
        threads = []
        num_threads = 10

        for i in range(num_threads):
            thread = threading.Thread(target=use_paginator, args=(i,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Verificar que não houve erros
        assert len(errors) == 0
        assert len(results) == num_threads

    @pytest.mark.performance
    def test_stream_thread_safety(self, concurrency_config) -> None:
        """Testa thread safety dos streams."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities") as mock_discovery:
            mock_discovery.return_value = ["thread_safe_entity"]

            mock_tap = Mock()
            mock_tap.config = concurrency_config
            mock_tap.apply_entity_filters = Mock(return_value={})

            stream = WMSAdvancedStream(
                tap=mock_tap,
                entity_name="thread_safe_entity",
                schema={"type": "object", "properties": {"id": {"type": "integer"}}}
            )

            results = []
            errors = []

            def use_stream(thread_id) -> None:
                try:
                    for _i in range(5):
                        stream.get_url_params(context=None, next_page_token=None)
                        stream.get_new_paginator()

                    results.append({"thread_id": thread_id, "success": True})
                except Exception as e:
                    errors.append({"thread_id": thread_id, "error": str(e)})

            # Executar múltiplas threads
            threads = []
            num_threads = 5

            for i in range(num_threads):
                thread = threading.Thread(target=use_stream, args=(i,))
                threads.append(thread)

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            # Verificar que streams são thread-safe
            assert len(errors) == 0
            assert len(results) == num_threads


class TestPerformanceBenchmarks:
    """Benchmarks de performance específicos."""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_benchmark_discovery_scaling(self) -> None:
        """Benchmark de scaling do discovery com número crescente de entidades."""
        entity_counts = [10, 50, 100, 200]
        times = []

        for count in entity_counts:
            entities = [f"entity_{i:04d}" for i in range(count)]

            config = {
                "base_url": "https://wms.benchmark.test.com",
                "auth_method": "basic",
                "username": "bench_user",
                "password": "bench_pass",
                "test_connection": False
            }

            with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities") as mock_discovery:
                with patch("tap_oracle_wms.discovery.SchemaGenerator.generate_schema") as mock_schema:
                    mock_discovery.return_value = entities
                    mock_schema.return_value = {"type": "object", "properties": {"id": {"type": "integer"}}}

                    start_time = time.time()

                    tap = TapOracleWMS(config=config)
                    streams = tap.discover_streams()

                    end_time = time.time()

                    times.append({
                        "entity_count": count,
                        "time": end_time - start_time,
                        "streams_created": len(streams)
                    })

        # Verificar que scaling é razoável (não exponencial)
        for i in range(1, len(times)):
            prev_time = times[i - 1]["time"]
            curr_time = times[i]["time"]
            prev_count = times[i - 1]["entity_count"]
            curr_count = times[i]["entity_count"]

            # Ratio de tempo deve ser menor que ratio de entidades (sub-linear)
            time_ratio = curr_time / prev_time if prev_time > 0 else 1
            count_ratio = curr_count / prev_count

            assert time_ratio < count_ratio * 2  # Scaling não deve ser muito pior que linear

    @pytest.mark.performance
    def test_benchmark_paginator_throughput(self) -> None:
        """Benchmark de throughput do paginator."""
        paginator = WMSAdvancedPaginator()

        # Preparar múltiplas respostas
        responses = []
        for _i in range(1000):
            response_data = {
                "result_count": 100,
                "results": [{"id": j, "value": f"value_{j}"} for j in range(10)]
            }

            mock_response = Mock()
            mock_response.json.return_value = response_data
            responses.append(mock_response)

        # Medir throughput
        start_time = time.time()

        for response in responses:
            paginator.has_more(response)
            paginator.get_next_url(response)

        end_time = time.time()
        total_time = end_time - start_time

        throughput = len(responses) / total_time  # Responses per second

        # Throughput deve ser alto
        assert throughput > 100  # Pelo menos 100 responses/second
        assert total_time < 10.0  # Total menos de 10 segundos

    @pytest.mark.performance
    def test_benchmark_url_params_generation(self) -> None:
        """Benchmark de geração de parâmetros de URL."""
        config = {
            "base_url": "https://wms.benchmark.test.com",
            "auth_method": "basic",
            "username": "bench_user",
            "password": "bench_pass",
            "page_size": 1000,
            "enable_incremental": True
        }

        mock_tap = Mock()
        mock_tap.config = config
        mock_tap.apply_entity_filters = Mock(return_value={"facility_code": "MAIN"})
        mock_tap.apply_incremental_filters = Mock(return_value={"mod_ts__gte": "2024-01-01T10:00:00Z"})

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="benchmark_entity",
            schema={"type": "object", "properties": {"id": {"type": "integer"}}}
        )

        # Medir throughput de geração de parâmetros
        num_iterations = 10000
        start_time = time.time()

        for _i in range(num_iterations):
            stream.get_url_params(context=None, next_page_token=None)

        end_time = time.time()
        total_time = end_time - start_time

        throughput = num_iterations / total_time  # Generations per second
        avg_time = total_time / num_iterations  # Average time per generation

        # Performance deve ser excelente
        assert throughput > 1000  # Pelo menos 1000 generations/second
        assert avg_time < 0.001   # Menos de 1ms por geração

    @pytest.mark.performance
    def test_benchmark_memory_efficiency_scale(self) -> None:
        """Benchmark de eficiência de memória com scaling."""
        memory_measurements = []
        entity_counts = [10, 50, 100]

        for count in entity_counts:
            entities = [f"entity_{i:04d}" for i in range(count)]

            config = {
                "base_url": "https://wms.memory-benchmark.test.com",
                "auth_method": "basic",
                "username": "memory_user",
                "password": "memory_pass",
                "test_connection": False
            }

            with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities") as mock_discovery:
                mock_discovery.return_value = entities

                process = psutil.Process(os.getpid())
                memory_before = process.memory_info().rss / 1024 / 1024  # MB

                tap = TapOracleWMS(config=config)
                streams = tap.discover_streams()

                # Forçar criação de estruturas
                for stream in streams:
                    stream.get_new_paginator()

                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = memory_after - memory_before

                memory_measurements.append({
                    "entity_count": count,
                    "memory_increase_mb": memory_increase,
                    "memory_per_entity_kb": (memory_increase * 1024) / count if count > 0 else 0
                })

                # Cleanup
                del tap
                del streams

        # Verificar que uso de memória é eficiente
        for measurement in memory_measurements:
            # Menos de 1MB por entidade
            assert measurement["memory_per_entity_kb"] < 1024
            # Aumento total razoável
            assert measurement["memory_increase_mb"] < 100
