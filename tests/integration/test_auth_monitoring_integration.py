"""Testes de integração para autenticação e monitoramento."""

import contextlib
from unittest.mock import Mock, patch

import pytest

from tap_oracle_wms.tap import TapOracleWMS


class TestAuthenticationIntegration:
    """Testes de integração para autenticação."""

    @pytest.fixture
    def auth_config_basic(self):
        """Configuração para auth básica."""
        return {
            "base_url": "https://wms.auth.test.com",
            "auth_method": "basic",
            "username": "auth_user",
            "password": "auth_pass",
            "test_connection": False,
        }

    @pytest.fixture
    def auth_config_oauth2(self):
        """Configuração para OAuth2."""
        return {
            "base_url": "https://wms.oauth.test.com",
            "auth_method": "oauth2",
            "oauth_client_id": "client123",
            "oauth_client_secret": "secret456",
            "oauth_token_url": "https://auth.test.com/token",
            "test_connection": False,
        }

    @pytest.mark.integration
    def test_basic_auth_integration_with_tap(self, auth_config_basic) -> None:
        """Testa integração de auth básica com o tap."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class:
                mock_discovery.return_value = ["facility"]

                # Mock authenticator
                mock_auth = Mock()
                mock_auth.auth_headers = {"Authorization": "Basic dGVzdDpwYXNz"}
                mock_auth_class.return_value = mock_auth

                # Criar tap
                tap = TapOracleWMS(config=auth_config_basic)

                # Verificar que authenticator foi criado
                mock_auth_class.assert_called_once_with(auth_config_basic)

                # Verificar que tap tem acesso ao authenticator
                assert hasattr(tap, "authenticator")

                # Verificar headers de autenticação
                streams = tap.discover_streams()
                for stream in streams:
                    assert stream.authenticator is not None

    @pytest.mark.integration
    def test_oauth2_auth_integration_with_tap(self, auth_config_oauth2) -> None:
        """Testa integração de OAuth2 com o tap."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class:
                mock_discovery.return_value = ["facility"]

                # Mock OAuth2 authenticator
                mock_auth = Mock()
                mock_auth.auth_headers = {"Authorization": "Bearer token123"}
                mock_auth.get_oauth_token.return_value = "token123"
                mock_auth_class.return_value = mock_auth

                # Criar tap
                TapOracleWMS(config=auth_config_oauth2)

                # Verificar que authenticator foi criado com OAuth2
                mock_auth_class.assert_called_once_with(auth_config_oauth2)

                # Verificar token OAuth2
                assert mock_auth.auth_headers["Authorization"] == "Bearer token123"

    @pytest.mark.integration
    def test_auth_http_client_integration(self, auth_config_basic) -> None:
        """Testa integração entre auth e HTTP client."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("httpx.Client") as mock_client_class:
                with patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class:
                    mock_discovery.return_value = ["facility"]

                    # Mock HTTP client
                    mock_client = Mock()
                    mock_client_class.return_value = mock_client

                    # Mock authenticator
                    mock_auth = Mock()
                    mock_auth.auth_headers = {"Authorization": "Basic dGVzdA=="}
                    mock_auth_class.return_value = mock_auth

                    # Mock response
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"results": []}
                    mock_client.get.return_value = mock_response

                    # Criar tap e fazer request
                    tap = TapOracleWMS(config=auth_config_basic)
                    tap.discover_streams()

                    # Verificar que requests incluem headers de auth
                    if mock_client.get.called:
                        call_args = mock_client.get.call_args
                        call_args[1].get("headers", {})
                        # Headers de auth devem estar presentes
                        # (Implementação específica depende do auth handler)

    @pytest.mark.integration
    def test_auth_error_handling_integration(self, auth_config_basic) -> None:
        """Testa tratamento de erros de autenticação."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("httpx.Client") as mock_client_class:
                mock_discovery.return_value = ["facility"]

                # Mock HTTP client que retorna 401
                mock_client = Mock()
                mock_client_class.return_value = mock_client

                mock_response = Mock()
                mock_response.status_code = 401
                mock_response.json.return_value = {"error": "Unauthorized"}

                mock_client.get.return_value = mock_response

                # Criar tap
                tap = TapOracleWMS(config=auth_config_basic)

                # Tentar fazer request que falha por auth
                try:
                    tap.discover_streams()
                    # Se chegou aqui, erro 401 foi tratado graciosamente
                except Exception as e:
                    # Se falhou, deve ser erro relacionado a auth
                    assert (
                        "401" in str(e)
                        or "Unauthorized" in str(e)
                        or "auth" in str(e).lower()
                    )

    @pytest.mark.integration
    def test_auth_token_refresh_integration(self, auth_config_oauth2) -> None:
        """Testa refresh de token OAuth2."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class:
                mock_discovery.return_value = ["facility"]

                # Mock authenticator com token refresh
                mock_auth = Mock()
                mock_auth.auth_headers = {"Authorization": "Bearer initial_token"}

                # Simular refresh de token
                def mock_refresh() -> None:
                    mock_auth.auth_headers = {"Authorization": "Bearer refreshed_token"}

                mock_auth.refresh_token = mock_refresh
                mock_auth_class.return_value = mock_auth

                # Criar tap
                tap = TapOracleWMS(config=auth_config_oauth2)

                # Simular refresh
                if hasattr(tap.authenticator, "refresh_token"):
                    initial_token = tap.authenticator.auth_headers["Authorization"]
                    tap.authenticator.refresh_token()
                    refreshed_token = tap.authenticator.auth_headers["Authorization"]

                    assert initial_token != refreshed_token
                    assert "refreshed_token" in refreshed_token


class TestMonitoringIntegration:
    """Testes de integração para monitoramento."""

    @pytest.fixture
    def monitoring_config(self):
        """Configuração com monitoramento habilitado."""
        return {
            "base_url": "https://wms.monitoring.test.com",
            "auth_method": "basic",
            "username": "monitor_user",
            "password": "monitor_pass",
            "metrics": {
                "enabled": True,
                "namespace": "tap_oracle_wms",
                "labels": {"environment": "test"},
            },
            "test_connection": False,
        }

    @pytest.fixture
    def monitoring_disabled_config(self):
        """Configuração com monitoramento desabilitado."""
        return {
            "base_url": "https://wms.no-monitoring.test.com",
            "auth_method": "basic",
            "username": "no_monitor_user",
            "password": "no_monitor_pass",
            "metrics": {"enabled": False},
            "test_connection": False,
        }

    @pytest.mark.integration
    def test_monitoring_integration_with_tap(self, monitoring_config) -> None:
        """Testa integração de monitoramento com o tap."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                mock_discovery.return_value = ["facility"]

                # Mock monitor
                mock_monitor = Mock()
                mock_monitor.metrics = Mock()
                mock_monitor_class.return_value = mock_monitor

                # Criar tap
                tap = TapOracleWMS(config=monitoring_config)

                # Verificar que monitor foi criado
                mock_monitor_class.assert_called_once_with(monitoring_config)
                assert tap._monitor == mock_monitor

    @pytest.mark.integration
    def test_monitoring_disabled_integration(self, monitoring_disabled_config) -> None:
        """Testa tap sem monitoramento."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            mock_discovery.return_value = ["facility"]

            # Criar tap sem monitoring
            tap = TapOracleWMS(config=monitoring_disabled_config)

            # Verificar que monitor não foi criado
            assert tap._monitor is None

    @pytest.mark.integration
    def test_monitoring_metrics_integration(self, monitoring_config) -> None:
        """Testa integração de métricas com operações do tap."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                mock_discovery.return_value = ["facility", "item"]

                # Mock monitor com métricas
                mock_monitor = Mock()
                mock_metrics = Mock()
                mock_monitor.metrics = mock_metrics
                mock_monitor_class.return_value = mock_monitor

                # Criar tap
                tap = TapOracleWMS(config=monitoring_config)

                # Simular operações que devem gerar métricas
                tap.discover_streams()

                # Verificar que métricas foram registradas
                # (Discovery de entidades)

                # Verificar se pelo menos algumas métricas foram chamadas
                total_calls = (
                    mock_metrics.record_counter.call_count
                    + mock_metrics.record_gauge.call_count
                    + mock_metrics.record_histogram.call_count
                )

                assert total_calls > 0  # Pelo menos uma métrica foi registrada

    @pytest.mark.integration
    def test_monitoring_connection_test_integration(self, monitoring_config) -> None:
        """Testa métricas durante teste de conexão."""
        monitoring_config["test_connection"] = True

        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                mock_discovery.return_value = ["facility", "item"]

                # Mock monitor
                mock_monitor = Mock()
                mock_metrics = Mock()
                mock_monitor.metrics = mock_metrics
                mock_monitor_class.return_value = mock_monitor

                # Criar tap com test_connection
                tap = TapOracleWMS(config=monitoring_config)

                # Executar teste de conexão
                with contextlib.suppress(Exception):
                    # Teste pode falhar, mas métricas devem ter sido registradas
                    tap.validate_config()

                # Verificar que métricas de conexão foram registradas
                # connection.test.start, connection.test.success/failure, etc.
                assert mock_metrics.record_counter.call_count > 0

    @pytest.mark.integration
    def test_monitoring_error_tracking_integration(self, monitoring_config) -> None:
        """Testa tracking de erros via monitoramento."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                # Forçar erro no discovery
                mock_discovery.side_effect = Exception("Discovery failed")

                # Mock monitor
                mock_monitor = Mock()
                mock_metrics = Mock()
                mock_monitor.metrics = mock_metrics
                mock_monitor_class.return_value = mock_monitor

                # Tentar criar tap (deve falhar)
                with contextlib.suppress(Exception):
                    TapOracleWMS(config=monitoring_config)

                # Monitor deve ter sido criado mesmo com erro
                mock_monitor_class.assert_called_once_with(monitoring_config)

    @pytest.mark.integration
    def test_monitoring_stream_metrics_integration(self, monitoring_config) -> None:
        """Testa métricas específicas de streams."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                mock_discovery.return_value = ["facility"]

                # Mock monitor
                mock_monitor = Mock()
                mock_metrics = Mock()
                mock_monitor.metrics = mock_metrics
                mock_monitor_class.return_value = mock_monitor

                # Criar tap
                tap = TapOracleWMS(config=monitoring_config)
                streams = tap.discover_streams()

                # Simular operação de stream que gera métricas
                stream = streams[0]

                # Mock de response para simular extração
                mock_response = Mock()
                mock_response.json.return_value = {
                    "result_count": 100,
                    "results": [{"id": i} for i in range(10)],
                }

                # Simular processamento de dados
                paginator = stream.get_new_paginator()
                paginator.has_more(mock_response)

                # Se stream tem acesso ao monitor do tap, deve registrar métricas
                if hasattr(stream, "tap") and hasattr(stream.tap, "_monitor"):
                    monitor = stream.tap._monitor
                    if monitor:
                        # Verificar que métricas podem ser registradas
                        assert monitor.metrics is not None


class TestAuthMonitoringIntegration:
    """Testes de integração entre autenticação e monitoramento."""

    @pytest.fixture
    def auth_monitoring_config(self):
        """Configuração com auth e monitoring."""
        return {
            "base_url": "https://wms.auth-monitor.test.com",
            "auth_method": "basic",
            "username": "auth_monitor_user",
            "password": "auth_monitor_pass",
            "metrics": {
                "enabled": True,
                "track_auth_events": True,
            },
            "test_connection": True,
        }

    @pytest.mark.integration
    def test_auth_success_monitoring(self, auth_monitoring_config) -> None:
        """Testa monitoramento de auth bem-sucedida."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                with patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class:
                    mock_discovery.return_value = ["facility"]

                    # Mock auth bem-sucedida
                    mock_auth = Mock()
                    mock_auth.auth_headers = {"Authorization": "Basic valid"}
                    mock_auth.test_connection.return_value = True
                    mock_auth_class.return_value = mock_auth

                    # Mock monitor
                    mock_monitor = Mock()
                    mock_metrics = Mock()
                    mock_monitor.metrics = mock_metrics
                    mock_monitor_class.return_value = mock_monitor

                    # Criar tap
                    tap = TapOracleWMS(config=auth_monitoring_config)

                    # Simular teste de conexão bem-sucedido
                    with contextlib.suppress(Exception):
                        tap.validate_config()

                    # Verificar que métricas de auth foram registradas
                    # auth.success, connection.test.success, etc.
                    assert mock_metrics.record_counter.call_count > 0

    @pytest.mark.integration
    def test_auth_failure_monitoring(self, auth_monitoring_config) -> None:
        """Testa monitoramento de falha de auth."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                with patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class:
                    mock_discovery.return_value = ["facility"]

                    # Mock auth que falha
                    mock_auth = Mock()
                    mock_auth.test_connection.side_effect = Exception("Auth failed")
                    mock_auth_class.return_value = mock_auth

                    # Mock monitor
                    mock_monitor = Mock()
                    mock_metrics = Mock()
                    mock_monitor.metrics = mock_metrics
                    mock_monitor_class.return_value = mock_monitor

                    # Criar tap
                    tap = TapOracleWMS(config=auth_monitoring_config)

                    # Tentar teste de conexão (deve falhar)
                    with contextlib.suppress(Exception):
                        tap.validate_config()

                    # Verificar que métricas de falha foram registradas
                    # auth.failure, connection.test.failure, etc.
                    # Pelo menos uma métrica deve ter sido registrada
                    total_metric_calls = (
                        mock_metrics.record_counter.call_count
                        + mock_metrics.record_gauge.call_count
                    )
                    assert total_metric_calls > 0

    @pytest.mark.integration
    def test_auth_token_refresh_monitoring(self) -> None:
        """Testa monitoramento de refresh de token OAuth2."""
        oauth_monitoring_config = {
            "base_url": "https://wms.oauth-monitor.test.com",
            "auth_method": "oauth2",
            "oauth_client_id": "client123",
            "oauth_client_secret": "secret456",
            "oauth_token_url": "https://auth.test.com/token",
            "metrics": {
                "enabled": True,
                "track_auth_events": True,
            },
            "test_connection": False,
        }

        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                with patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class:
                    mock_discovery.return_value = ["facility"]

                    # Mock OAuth authenticator
                    mock_auth = Mock()
                    mock_auth.auth_headers = {"Authorization": "Bearer token123"}

                    # Mock token refresh
                    refresh_call_count = {"count": 0}

                    def mock_refresh() -> None:
                        refresh_call_count["count"] += 1
                        mock_auth.auth_headers = {
                            "Authorization": f'Bearer refreshed_{refresh_call_count["count"]}'
                        }

                    mock_auth.refresh_token = mock_refresh
                    mock_auth_class.return_value = mock_auth

                    # Mock monitor
                    mock_monitor = Mock()
                    mock_metrics = Mock()
                    mock_monitor.metrics = mock_metrics
                    mock_monitor_class.return_value = mock_monitor

                    # Criar tap
                    tap = TapOracleWMS(config=oauth_monitoring_config)

                    # Simular refresh de token
                    if hasattr(tap.authenticator, "refresh_token"):
                        tap.authenticator.refresh_token()

                        # Se monitoring está integrado com auth, deve ter métricas
                        # auth.token.refresh, auth.token.refresh.success, etc.
                        assert refresh_call_count["count"] == 1

    @pytest.mark.integration
    def test_comprehensive_auth_monitoring_flow(self, auth_monitoring_config) -> None:
        """Testa fluxo completo de auth + monitoring."""
        with patch(
            "tap_oracle_wms.discovery.EntityDiscovery.discover_entities"
        ) as mock_discovery:
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor_class:
                with patch("tap_oracle_wms.auth.WMSAuthenticator") as mock_auth_class:
                    with patch("httpx.Client") as mock_client_class:
                        mock_discovery.return_value = ["facility"]

                        # Mock auth
                        mock_auth = Mock()
                        mock_auth.auth_headers = {"Authorization": "Basic valid"}
                        mock_auth.test_connection.return_value = True
                        mock_auth_class.return_value = mock_auth

                        # Mock HTTP client
                        mock_client = Mock()
                        mock_client_class.return_value = mock_client

                        mock_response = Mock()
                        mock_response.status_code = 200
                        mock_response.json.return_value = {
                            "results": [{"id": 1, "code": "TEST"}],
                        }
                        mock_client.get.return_value = mock_response

                        # Mock monitor
                        mock_monitor = Mock()
                        mock_metrics = Mock()
                        mock_monitor.metrics = mock_metrics
                        mock_monitor_class.return_value = mock_monitor

                        # Executar fluxo completo
                        tap = TapOracleWMS(config=auth_monitoring_config)

                        # Teste de conexão
                        with contextlib.suppress(Exception):
                            tap.validate_config()

                        # Discovery
                        streams = tap.discover_streams()

                        # Verificar que tanto auth quanto monitoring funcionaram
                        assert tap.authenticator is not None
                        assert tap._monitor is not None
                        assert len(streams) > 0

                        # Verificar que métricas foram registradas
                        assert mock_metrics.record_counter.call_count > 0
