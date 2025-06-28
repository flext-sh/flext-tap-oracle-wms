"""Testes unitários para capabilities do Tap."""

from unittest.mock import Mock, patch

import pytest
from singer_sdk.helpers.capabilities import TapCapabilities

from tap_oracle_wms.tap import TapOracleWMS


class TestTapCapabilities:
    """Testes para capabilities do TapOracleWMS."""

    @pytest.mark.unit
    def test_tap_has_capabilities_attribute(self) -> None:
        """Testa se o tap tem atributo capabilities."""
        assert hasattr(TapOracleWMS, "capabilities")

    @pytest.mark.unit
    def test_tap_capabilities_type(self) -> None:
        """Testa se capabilities é uma lista."""
        capabilities = TapOracleWMS.capabilities
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0

    @pytest.mark.unit
    def test_tap_capabilities_content(self) -> None:
        """Testa conteúdo das capabilities."""
        capabilities = TapOracleWMS.capabilities

        # Capabilities obrigatórias
        required_capabilities = [
            TapCapabilities.DISCOVER,
            TapCapabilities.STATE,
            TapCapabilities.CATALOG,
            TapCapabilities.PROPERTIES,
        ]

        for capability in required_capabilities:
            assert capability in capabilities, f"Missing capability: {capability}"

    @pytest.mark.unit
    def test_tap_capabilities_discover(self) -> None:
        """Testa capability DISCOVER."""
        capabilities = TapOracleWMS.capabilities
        assert TapCapabilities.DISCOVER in capabilities

    @pytest.mark.unit
    def test_tap_capabilities_state(self) -> None:
        """Testa capability STATE."""
        capabilities = TapOracleWMS.capabilities
        assert TapCapabilities.STATE in capabilities

    @pytest.mark.unit
    def test_tap_capabilities_catalog(self) -> None:
        """Testa capability CATALOG."""
        capabilities = TapOracleWMS.capabilities
        assert TapCapabilities.CATALOG in capabilities

    @pytest.mark.unit
    def test_tap_capabilities_properties(self) -> None:
        """Testa capability PROPERTIES."""
        capabilities = TapOracleWMS.capabilities
        assert TapCapabilities.PROPERTIES in capabilities

    @pytest.mark.unit
    def test_tap_capabilities_no_duplicates(self) -> None:
        """Testa se não há capabilities duplicadas."""
        capabilities = TapOracleWMS.capabilities
        assert len(capabilities) == len(set(capabilities))

    @pytest.mark.unit
    def test_tap_capabilities_enum_values(self) -> None:
        """Testa se todas as capabilities são enum válidos."""
        capabilities = TapOracleWMS.capabilities

        for capability in capabilities:
            assert isinstance(capability, TapCapabilities)
            assert hasattr(capability, "value")


class TestTapBasicProperties:
    """Testes para propriedades básicas do Tap."""

    @pytest.mark.unit
    def test_tap_name(self) -> None:
        """Testa nome do tap."""
        assert TapOracleWMS.name == "tap-oracle-wms"

    @pytest.mark.unit
    def test_tap_has_config_schema(self) -> None:
        """Testa se tem schema de configuração."""
        assert hasattr(TapOracleWMS, "config_jsonschema")
        assert TapOracleWMS.config_jsonschema is not None

    @pytest.mark.unit
    def test_tap_config_schema_structure(self) -> None:
        """Testa estrutura do schema de configuração."""
        schema = TapOracleWMS.config_jsonschema

        # Converte para dict se necessário
        schema_dict = schema.to_dict() if hasattr(schema, "to_dict") else schema

        assert isinstance(schema_dict, dict)
        assert "properties" in schema_dict


class TestTapInitialization:
    """Testes para inicialização do Tap."""

    @pytest.fixture
    def basic_config(self):
        """Configuração básica para testes."""
        return {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "test_connection": False,
            "metrics": {"enabled": False},
        }

    @pytest.mark.unit
    def test_tap_initialization_success(self, basic_config) -> None:
        """Testa inicialização bem-sucedida."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=basic_config)

            assert tap.name == "tap-oracle-wms"
            assert tap.tap_name == "tap-oracle-wms"
            assert tap.config == basic_config

    @pytest.mark.unit
    def test_tap_initialization_with_monitoring(self, basic_config) -> None:
        """Testa inicialização com monitoramento habilitado."""
        config_with_monitoring = basic_config.copy()
        config_with_monitoring["metrics"] = {"enabled": True}

        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            with patch("tap_oracle_wms.monitoring.TAPMonitor") as mock_monitor:
                tap = TapOracleWMS(config=config_with_monitoring)

                # Verifica se monitor foi criado
                mock_monitor.assert_called_once_with(config_with_monitoring)
                assert tap._monitor is not None

    @pytest.mark.unit
    def test_tap_initialization_without_monitoring(self, basic_config) -> None:
        """Testa inicialização sem monitoramento."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=basic_config)

            # Verifica se monitor não foi criado
            assert tap._monitor is None

    @pytest.mark.unit
    def test_tap_has_entity_discovery(self, basic_config) -> None:
        """Testa se tem entity discovery."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=basic_config)

            assert hasattr(tap, "_entity_discovery")
            assert hasattr(tap, "_schema_generator")

    @pytest.mark.unit
    def test_tap_initialization_sets_tap_name(self, basic_config) -> None:
        """Testa se tap_name é definido antes de super().__init__."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=basic_config)

            # Crítico: tap_name deve estar definido para Singer SDK
            assert tap.tap_name == "tap-oracle-wms"


class TestTapValidation:
    """Testes para validação do Tap."""

    @pytest.fixture
    def valid_config(self):
        """Configuração válida."""
        return {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "page_size": 1000,
            "test_connection": False,
        }

    @pytest.fixture
    def invalid_auth_config(self):
        """Configuração com auth inválida."""
        return {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            # Faltam username/password
            "test_connection": False,
        }

    @pytest.fixture
    def invalid_pagination_config(self):
        """Configuração com paginação inválida."""
        return {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "page_size": 2000,  # Acima do limite
            "test_connection": False,
        }

    @pytest.mark.unit
    def test_validate_config_success(self, valid_config) -> None:
        """Testa validação bem-sucedida."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=valid_config)

            # Não deve levantar exceção
            tap.validate_config()

    @pytest.mark.unit
    def test_validate_config_invalid_auth(self, invalid_auth_config) -> None:
        """Testa validação com auth inválida."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=invalid_auth_config)

            with pytest.raises(ValueError, match="username and password"):
                tap.validate_config()

    @pytest.mark.unit
    def test_validate_config_invalid_pagination(self, invalid_pagination_config) -> None:
        """Testa validação com paginação inválida."""
        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=invalid_pagination_config)

            with pytest.raises(ValueError, match="1250"):
                tap.validate_config()

    @pytest.mark.unit
    def test_validate_config_skip_connection_test(self, valid_config) -> None:
        """Testa validação pulando teste de conexão."""
        config = valid_config.copy()
        config["test_connection"] = False

        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=config)

            # Mock _test_connection para verificar se não é chamado
            with patch.object(tap, "_test_connection") as mock_test:
                tap.validate_config()

                mock_test.assert_not_called()

    @pytest.mark.unit
    def test_validate_config_with_connection_test(self, valid_config) -> None:
        """Testa validação com teste de conexão."""
        config = valid_config.copy()
        config["test_connection"] = True

        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            tap = TapOracleWMS(config=config)

            # Mock _test_connection para verificar se é chamado
            with patch.object(tap, "_test_connection") as mock_test:
                tap.validate_config()

                mock_test.assert_called_once()


class TestTapConnectionTest:
    """Testes para teste de conexão do Tap."""

    @pytest.fixture
    def tap_instance(self):
        """Instância do tap para testes."""
        config = {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "test_connection": False,
            "metrics": {"enabled": False},
        }

        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            return TapOracleWMS(config=config)

    @pytest.mark.unit
    def test_connection_test_success(self, tap_instance) -> None:
        """Testa teste de conexão bem-sucedido."""
        # Mock successful entity discovery
        mock_entities = ["facility", "item", "location"]

        with patch.object(tap_instance, "entity_discovery") as mock_discovery:
            mock_discovery.discover_entities.return_value = mock_entities

            # Não deve levantar exceção
            tap_instance._test_connection()

    @pytest.mark.unit
    def test_connection_test_no_entities(self, tap_instance) -> None:
        """Testa teste de conexão sem entidades descobertas."""
        # Mock empty entity discovery
        with patch.object(tap_instance, "entity_discovery") as mock_discovery:
            mock_discovery.discover_entities.return_value = []

            with pytest.raises(ValueError, match="No entities discovered"):
                tap_instance._test_connection()

    @pytest.mark.unit
    def test_connection_test_with_monitoring(self, tap_instance) -> None:
        """Testa teste de conexão com monitoramento."""
        # Enable monitoring
        tap_instance._monitor = Mock()

        mock_entities = ["facility", "item"]

        with patch.object(tap_instance, "entity_discovery") as mock_discovery:
            mock_discovery.discover_entities.return_value = mock_entities

            tap_instance._test_connection()

            # Verifica se métricas foram registradas
            monitor = tap_instance._monitor
            assert monitor.metrics.record_counter.call_count >= 2  # test.success + entities_discovered
            monitor.metrics.record_gauge.assert_called_with(
                "connection.entities_discovered", 2,
            )

    @pytest.mark.unit
    def test_connection_test_failure_with_monitoring(self, tap_instance) -> None:
        """Testa falha no teste de conexão com monitoramento."""
        # Enable monitoring
        tap_instance._monitor = Mock()

        with patch.object(tap_instance, "entity_discovery") as mock_discovery:
            mock_discovery.discover_entities.return_value = []

            with pytest.raises(ValueError):
                tap_instance._test_connection()

            # Verifica se métrica de falha foi registrada
            monitor = tap_instance._monitor
            monitor.metrics.record_counter.assert_any_call("connection.test.failure")


class TestTapDiscoveryMethods:
    """Testes para métodos de discovery do Tap."""

    @pytest.fixture
    def tap_instance(self):
        """Instância do tap para testes."""
        config = {
            "base_url": "https://wms.test.com",
            "auth_method": "basic",
            "username": "test",
            "password": "pass",
            "test_connection": False,
        }

        with patch("tap_oracle_wms.discovery.EntityDiscovery.discover_entities"):
            return TapOracleWMS(config=config)

    @pytest.mark.unit
    def test_tap_has_entity_discovery_property(self, tap_instance) -> None:
        """Testa se tem propriedade entity_discovery."""
        assert hasattr(tap_instance, "entity_discovery")

    @pytest.mark.unit
    def test_tap_has_schema_generator_property(self, tap_instance) -> None:
        """Testa se tem propriedade schema_generator."""
        assert hasattr(tap_instance, "schema_generator")

    @pytest.mark.unit
    def test_entity_discovery_lazy_initialization(self, tap_instance) -> None:
        """Testa inicialização lazy do entity discovery."""
        # Entity discovery deve ser criado sob demanda
        discovery = tap_instance.entity_discovery
        assert discovery is not None

        # Segunda chamada deve retornar a mesma instância
        discovery2 = tap_instance.entity_discovery
        assert discovery is discovery2

    @pytest.mark.unit
    def test_schema_generator_lazy_initialization(self, tap_instance) -> None:
        """Testa inicialização lazy do schema generator."""
        # Schema generator deve ser criado sob demanda
        generator = tap_instance.schema_generator
        assert generator is not None

        # Segunda chamada deve retornar a mesma instância
        generator2 = tap_instance.schema_generator
        assert generator is generator2
