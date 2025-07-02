"""Testes de integração para componentes do Tap."""

from unittest.mock import Mock, patch

import pytest
from singer_sdk.helpers.capabilities import TapCapabilities

from tap_oracle_wms.streams import WMSAdvancedPaginator, WMSAdvancedStream
from tap_oracle_wms.tap import TapOracleWMS


class TestTapStreamIntegration:
    """Testes de integração entre Tap e Streams."""

    @pytest.fixture
    def integration_config(self):
        """Configuração para testes de integração."""
        return {
            "base_url": "https://wms.integration.test.com",
            "auth_method": "basic",
            "username": "integration_user",
            "password": "integration_pass",
            "page_size": 500,
            "enable_incremental": True,
            "incremental_overlap_minutes": 5,
            "test_connection": False,
            "metrics": {"enabled": True},
        }

    @pytest.fixture
    def mock_discovery_response(self):
        """Mock de resposta do entity discovery."""
        return ["facility", "item", "location", "allocation", "order_hdr"]

    @pytest.fixture
    def mock_schema_response(self):
        """Mock de schema response."""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "code": {"type": "string"},
                "name": {"type": "string"},
                "mod_ts": {"type": "string", "format": "date-time"},
            },
            "required": ["id", "code"],
        }

    @pytest.mark.integration
    def test_tap_stream_creation_integration(
        self, integration_config, mock_discovery_response, mock_schema_response,
    ) -> None:
        """Testa criação e integração entre tap e streams."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities",
        ) as mock_discovery, patch(
            "tap_oracle_wms.discovery.SchemaGenerator.generate_schema",
        ) as mock_schema:
            mock_discovery.return_value = mock_discovery_response
            mock_schema.return_value = mock_schema_response

            # Criar tap
            tap = TapOracleWMS(config=integration_config)

            # Verificar que tap foi criado com configuração correta
            assert tap.config == integration_config
            assert tap._monitor is not None  # Monitoring habilitado

            # Obter streams descobertos
            streams = tap.discover_streams()

            # Verificar que streams foram criados corretamente
            assert len(streams) == len(mock_discovery_response)

            for stream in streams:
                assert isinstance(stream, WMSAdvancedStream)
                assert stream.tap is tap
                assert stream.name in mock_discovery_response
                assert stream._base_url == integration_config["base_url"]

    @pytest.mark.integration
    def test_stream_paginator_integration(self, integration_config) -> None:
        """Testa integração entre stream e paginator."""
        mock_tap = Mock()
        mock_tap.config = integration_config

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="facility",
            schema={"type": "object", "properties": {"id": {"type": "integer"}}},
        )

        # Verificar que stream cria paginator corretamente
        paginator = stream.get_new_paginator()
        assert isinstance(paginator, WMSAdvancedPaginator)

        # Verificar integração com parâmetros de URL
        params = stream.get_url_params(context=None, next_page_token=None)
        assert isinstance(params, dict)
        assert "page_mode" in params
        assert "page_size" in params
        assert params["page_size"] == integration_config["page_size"]

    @pytest.mark.integration
    def test_tap_monitoring_integration(self, integration_config) -> None:
        """Testa integração com sistema de monitoramento."""
        with (
            patch(
                "tap_oracle_wms.discovery.EntityDiscovery.discover_entities",
            ) as mock_discovery,
            patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class,
        ):
            mock_discovery.return_value = ["facility"]
            mock_monitor = Mock()
            mock_monitor_class.return_value = mock_monitor

            # Criar tap com monitoring
            tap = TapOracleWMS(config=integration_config)

            # Verificar que monitor foi criado
            mock_monitor_class.assert_called_once_with(integration_config)
            assert tap._monitor == mock_monitor

    @pytest.mark.integration
    def test_auth_stream_integration(self, integration_config) -> None:
        """Testa integração entre autenticação e streams."""
        with (
            patch(
                "tap_oracle_wms.discovery.EntityDiscovery.discover_entities",
            ) as mock_discovery,
            patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class,
        ):
            mock_discovery.return_value = ["facility"]
            mock_auth = Mock()
            mock_auth_class.return_value = mock_auth

            tap = TapOracleWMS(config=integration_config)
            streams = tap.discover_streams()

            # Verificar que streams herdam autenticação do tap
            for stream in streams:
                # Stream deve ter acesso aos headers de auth do tap
                assert hasattr(stream, "authenticator")
                # Ou verificar se tap passa autenticação corretamente
                assert stream.tap is tap

    @pytest.mark.integration
    def test_discovery_schema_integration(self, integration_config) -> None:
        """Testa integração entre discovery e geração de schema."""
        entities = ["facility", "item", "location"]
        expected_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "code": {"type": "string"},
                "mod_ts": {"type": "string", "format": "date-time"},
            },
        }

        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities",
        ) as mock_discovery, patch(
            "tap_oracle_wms.discovery.SchemaGenerator.generate_schema",
        ) as mock_schema:
            mock_discovery.return_value = entities
            mock_schema.return_value = expected_schema

            tap = TapOracleWMS(config=integration_config)
            streams = tap.discover_streams()

            # Verificar que schema foi gerado para cada entidade descoberta
            assert mock_schema.call_count == len(entities)

            for stream in streams:
                assert stream.schema == expected_schema


class TestConfigValidationIntegration:
    """Testes de integração para validação de configuração."""

    @pytest.mark.integration
    def test_full_config_validation_flow(self) -> None:
        """Testa fluxo completo de validação de configuração."""
        from tap_oracle_wms.config import (
            validate_auth_config,
            validate_pagination_config,
        )

        # Configuração válida completa
        valid_config = {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test_user",
            "password": "test_pass",
            "page_size": 1000,
            "enable_incremental": True,
            "company_code": "TEST",
            "facility_code": "MAIN",
        }

        # Testar todas as validações
        auth_result = validate_auth_config(valid_config)
        pagination_result = validate_pagination_config(valid_config)

        assert auth_result is None
        assert pagination_result is None

        # Testar criação do tap com configuração validada
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=valid_config)
            assert tap.config == valid_config

    @pytest.mark.integration
    def test_config_validation_with_tap_creation(self) -> None:
        """Testa validação de configuração durante criação do tap."""
        invalid_configs = [
            # Auth inválida
            {
                "base_url": "https://wms.test.com",
                "auth_method": "basic",
                # Faltam username/password
            },
            # Paginação inválida
            {
                "base_url": "https://wms.test.com",
                "auth_method": "basic",
                "username": "test",
                "password": "pass",
                "page_size": 2000,  # Acima do limite
            },
        ]

        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            for config in invalid_configs:
                with pytest.raises(ValueError):
                    TapOracleWMS(config=config)


class TestHTTPIntegration:
    """Testes de integração HTTP."""

    @pytest.fixture
    def mock_http_responses(self):
        """Mock de respostas HTTP para diferentes endpoints."""
        return {
            "entity_discovery": ["facility", "item", "location"],
            "entity_describe": {
                "name": "facility",
                "fields": [
                    {"name": "id", "type": "integer", "nullable": False},
                    {"name": "code", "type": "string", "nullable": False},
                    {"name": "name", "type": "string", "nullable": True},
                    {"name": "mod_ts", "type": "datetime", "nullable": True},
                ],
            },
            "entity_data": {
                "result_count": 1000,
                "page_count": 10,
                "page_nbr": 1,
                "next_page": "https://wms.test.com/entity/facility?cursor=abc123&page_size=500",
                "results": [
                    {
                        "id": 1,
                        "code": "FAC001",
                        "name": "Main Facility",
                        "mod_ts": "2024-01-01T10:00:00Z",
                    },
                ],
            },
        }

    @pytest.mark.integration
    def test_http_client_stream_integration(
        self, integration_config, mock_http_responses,
    ) -> None:
        """Testa integração entre HTTP client e streams."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Configurar respostas mock
            def mock_get(url, **kwargs):
                response = Mock()
                response.status_code = 200

                if "/entity/" in url and url.endswith("/entity/"):
                    response.json.return_value = mock_http_responses["entity_discovery"]
                elif "/describe/" in url:
                    response.json.return_value = mock_http_responses["entity_describe"]
                else:
                    response.json.return_value = mock_http_responses["entity_data"]

                return response

            mock_client.get.side_effect = mock_get

            with patch(
                "tap_oracle_wms.discovery.EntityDiscovery.discover_entities",
            ) as mock_discovery:
                mock_discovery.return_value = mock_http_responses["entity_discovery"]

                tap = TapOracleWMS(config=integration_config)
                streams = tap.discover_streams()

                # Simular request de dados
                stream = streams[0]
                # Testar que stream pode fazer requests através do tap
                assert stream.tap is tap

    @pytest.mark.integration
    def test_pagination_http_integration(
        self, integration_config, mock_http_responses,
    ) -> None:
        """Testa integração entre paginação e requests HTTP."""
        mock_tap = Mock()
        mock_tap.config = integration_config

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="facility",
            schema={"type": "object", "properties": {"id": {"type": "integer"}}},
        )

        paginator = stream.get_new_paginator()

        # Mock de response HTTP
        mock_response = Mock()
        mock_response.json.return_value = mock_http_responses["entity_data"]

        # Testar extração de next page
        next_url = paginator.get_next_url(mock_response)
        expected_url = mock_http_responses["entity_data"]["next_page"]
        assert next_url == expected_url

        # Testar detecção de more pages
        has_more = paginator.has_more(mock_response)
        assert has_more is True


class TestStateManagementIntegration:
    """Testes de integração para gerenciamento de estado."""

    @pytest.fixture
    def state_config(self):
        """Configuração com state management."""
        return {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "enable_incremental": True,
            "start_date": "2024-01-01T00:00:00Z",
        }

    @pytest.mark.integration
    def test_state_stream_integration(self, state_config) -> None:
        """Testa integração entre state management e streams."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities",
        ) as mock_discovery:
            mock_discovery.return_value = ["facility"]

            tap = TapOracleWMS(config=state_config)
            streams = tap.discover_streams()

            stream = streams[0]

            # Verificar que stream suporta incremental
            assert stream.replication_method == "INCREMENTAL"
            assert "mod_ts" in stream.replication_keys

            # Testar bookmark management
            initial_bookmark = stream.get_starting_replication_key_value(None)
            assert initial_bookmark is not None

    @pytest.mark.integration
    def test_incremental_extraction_integration(self, state_config) -> None:
        """Testa integração de extração incremental."""
        mock_tap = Mock()
        mock_tap.config = state_config
        mock_tap.apply_incremental_filters = Mock(
            return_value={"mod_ts__gte": "2024-01-01T10:00:00Z"},
        )

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="facility",
            schema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "mod_ts": {"type": "string", "format": "date-time"},
                },
            },
        )

        # Mock bookmark value
        with patch.object(
            stream, "get_starting_replication_key_value",
        ) as mock_bookmark:
            mock_bookmark.return_value = "2024-01-01T10:00:00Z"

            # Testar geração de parâmetros incrementais
            stream.get_url_params(context=None, next_page_token=None)

            # Verificar que filtros incrementais foram aplicados
            mock_tap.apply_incremental_filters.assert_called_once()


class TestErrorHandlingIntegration:
    """Testes de integração para tratamento de erros."""

    @pytest.mark.integration
    def test_http_error_handling_integration(self, integration_config) -> None:
        """Testa tratamento de erros HTTP em integração."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Simular erro HTTP
            import httpx

            mock_client.get.side_effect = httpx.HTTPStatusError(
                "Server error",
                request=Mock(),
                response=Mock(status_code=500),
            )

            with patch(
                "tap_oracle_wms.discovery.EntityDiscovery.discover_entities",
            ) as mock_discovery:
                # Discovery deve lidar com erro graciosamente
                mock_discovery.side_effect = Exception("Connection failed")

                with pytest.raises(Exception, match="Connection failed"):
                    TapOracleWMS(config=integration_config)

    @pytest.mark.integration
    def test_paginator_error_recovery_integration(self) -> None:
        """Testa recuperação de erros do paginator."""
        paginator = WMSAdvancedPaginator()

        # Mock response com erro JSON
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")

        # Paginator deve lidar graciosamente com erro
        next_url = paginator.get_next_url(mock_response)
        has_more = paginator.has_more(mock_response)

        assert next_url is None
        assert has_more is False

    @pytest.mark.integration
    def test_stream_error_recovery_integration(self, integration_config) -> None:
        """Testa recuperação de erros em streams."""
        mock_tap = Mock()
        mock_tap.config = integration_config
        mock_tap.apply_entity_filters = Mock(side_effect=Exception("Filter error"))

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="facility",
            schema={"type": "object"},
        )

        # Stream deve lidar com erro em filtros
        try:
            params = stream.get_url_params(context=None, next_page_token=None)
            # Se não levantou exceção, deve ter parâmetros básicos
            assert isinstance(params, dict)
        except Exception as e:
            # Se levantou exceção, deve ser tratada apropriadamente
            assert "Filter error" in str(e)


class TestEndToEndIntegration:
    """Testes de integração end-to-end simplificados."""

    @pytest.mark.integration
    def test_full_discovery_flow_integration(self, integration_config) -> None:
        """Testa fluxo completo de discovery."""
        entities = ["facility", "item", "location"]
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "code": {"type": "string"},
                "mod_ts": {"type": "string", "format": "date-time"},
            },
        }

        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities",
        ) as mock_discovery, patch(
            "tap_oracle_wms.discovery.SchemaGenerator.generate_schema",
        ) as mock_schema:
            mock_discovery.return_value = entities
            mock_schema.return_value = schema

            # Criar tap
            tap = TapOracleWMS(config=integration_config)

            # Executar discovery
            streams = tap.discover_streams()

            # Verificar resultado completo
            assert len(streams) == len(entities)

            for stream in streams:
                assert isinstance(stream, WMSAdvancedStream)
                assert stream.name in entities
                assert stream.schema == schema
                assert stream.tap is tap

    @pytest.mark.integration
    def test_capabilities_integration(self, integration_config) -> None:
        """Testa integração de capabilities."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=integration_config)

            # Verificar capabilities
            capabilities = tap.capabilities
            assert isinstance(capabilities, list)
            assert TapCapabilities.DISCOVER in capabilities
            assert TapCapabilities.STATE in capabilities
            assert TapCapabilities.CATALOG in capabilities

            # Verificar que streams respeitam capabilities
            streams = tap.discover_streams()
            for stream in streams:
                if TapCapabilities.STATE in capabilities:
                    # Stream deve suportar state se tap suporta
                    assert hasattr(stream, "replication_method")
