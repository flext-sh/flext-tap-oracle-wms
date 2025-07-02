"""Testes unitários para streams avançados."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from singer_sdk.streams import RESTStream

from tap_oracle_wms.streams import WMSAdvancedPaginator, WMSAdvancedStream


class TestWMSAdvancedStream:
    """Testes para stream avançado do WMS."""

    @pytest.fixture
    def mock_tap(self):
        """Mock do tap para testes."""
        mock_tap = Mock()
        mock_tap.config = {
            "base_url": "https://wms.test.com",
            "enable_incremental": True,
            "incremental_overlap_minutes": 5,
            "page_size": 1000,
        }
        return mock_tap

    @pytest.fixture
    def stream_instance(self, mock_tap):
        """Instância do stream para testes."""
        return WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "mod_ts": {"type": "string", "format": "date-time"},
                },
            },
        )

    @pytest.mark.unit
    def test_stream_inheritance(self, stream_instance) -> None:
        """Testa se herda corretamente de RESTStream."""
        assert isinstance(stream_instance, RESTStream)

    @pytest.mark.unit
    def test_stream_initialization(self, stream_instance, mock_tap) -> None:
        """Testa inicialização do stream."""
        assert stream_instance.entity_name == "test_entity"
        assert stream_instance._base_url == "https://wms.test.com"
        assert stream_instance._enable_incremental is True

    @pytest.mark.unit
    def test_stream_name_property(self, stream_instance) -> None:
        """Testa propriedade name."""
        assert stream_instance.name == "test_entity"

    @pytest.mark.unit
    def test_stream_path_property(self, stream_instance) -> None:
        """Testa propriedade path."""
        expected_path = "/wms/lgfapi/v10/entity/test_entity"
        assert stream_instance.path == expected_path

    @pytest.mark.unit
    def test_stream_url_property(self, stream_instance) -> None:
        """Testa propriedade url."""
        expected_url = "https://wms.test.com/wms/lgfapi/v10/entity/test_entity"
        assert stream_instance.url == expected_url

    @pytest.mark.unit
    def test_stream_url_property_trailing_slash(self, mock_tap) -> None:
        """Testa URL com trailing slash na base_url."""
        mock_tap.config["base_url"] = "https://wms.test.com/"

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        expected_url = "https://wms.test.com/wms/lgfapi/v10/entity/test_entity"
        assert stream.url == expected_url

    @pytest.mark.unit
    def test_stream_replication_method_incremental(self, stream_instance) -> None:
        """Testa método de replicação incremental."""
        assert stream_instance.replication_method == "INCREMENTAL"
        assert stream_instance.replication_keys == ["mod_ts"]

    @pytest.mark.unit
    def test_stream_replication_method_full_table(self, mock_tap) -> None:
        """Testa método de replicação full table."""
        mock_tap.config["enable_incremental"] = False

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        assert stream.replication_method == "FULL_TABLE"
        assert stream.replication_keys == []

    @pytest.mark.unit
    def test_get_new_paginator(self, stream_instance) -> None:
        """Testa criação de novo paginador."""
        paginator = stream_instance.get_new_paginator()

        assert isinstance(paginator, WMSAdvancedPaginator)

    @pytest.mark.unit
    def test_get_optimal_page_size_default(self, stream_instance) -> None:
        """Testa cálculo de page size padrão."""
        page_size = stream_instance._get_optimal_page_size()

        assert page_size == 1000  # Default from config
        assert page_size <= stream_instance.MAX_PAGE_SIZE

    @pytest.mark.unit
    def test_get_optimal_page_size_entity_specific(self, mock_tap) -> None:
        """Testa page size específico para entidade."""
        mock_tap.config["pagination_config"] = {
            "allocation_dtl": {"page_size": 500},
        }

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="allocation_dtl",
            schema={"type": "object"},
        )

        page_size = stream._get_optimal_page_size()
        assert page_size == 500

    @pytest.mark.unit
    def test_get_optimal_page_size_large_entity_optimization(self, mock_tap) -> None:
        """Testa otimização para entidades grandes."""
        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="allocation_dtl",  # Entidade grande
            schema={"type": "object"},
        )

        page_size = stream._get_optimal_page_size()
        # allocation_dtl deve ter page size menor por ser detalhada
        assert page_size <= 500

    @pytest.mark.unit
    def test_get_optimal_page_size_lookup_entity_optimization(self, mock_tap) -> None:
        """Testa otimização para entidades de lookup."""
        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="facility",  # Entidade de lookup
            schema={"type": "object"},
        )

        page_size = stream._get_optimal_page_size()
        # facility pode ter page size maior por ser simples
        assert page_size >= 1000

    @pytest.mark.unit
    def test_get_optimal_page_size_max_limit(self, mock_tap) -> None:
        """Testa limite máximo de page size."""
        mock_tap.config["page_size"] = 5000  # Acima do limite

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        page_size = stream._get_optimal_page_size()
        assert page_size == stream.MAX_PAGE_SIZE


class TestStreamURLParams:
    """Testes para construção de parâmetros de URL."""

    @pytest.fixture
    def mock_tap(self):
        """Mock do tap para testes."""
        mock_tap = Mock()
        mock_tap.config = {
            "base_url": "https://wms.test.com",
            "enable_incremental": True,
            "page_size": 1000,
        }
        # Mock methods
        mock_tap.apply_entity_filters.return_value = {}
        mock_tap.apply_incremental_filters.return_value = {
            "mod_ts__gte": "2024-01-01T10:00:00Z",
        }
        mock_tap.apply_full_sync_filters.return_value = {}
        return mock_tap

    @pytest.fixture
    def stream_instance(self, mock_tap):
        """Instância do stream para testes."""
        return WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

    @pytest.mark.unit
    def test_get_url_params_first_request(self, stream_instance) -> None:
        """Testa parâmetros para primeira requisição."""
        params = stream_instance.get_url_params(context=None, next_page_token=None)

        assert isinstance(params, dict)
        assert params["page_mode"] == "sequenced"
        assert params["page_size"] == 1000

    @pytest.mark.unit
    def test_get_url_params_hateoas_continuation(self, stream_instance) -> None:
        """Testa parâmetros para continuação HATEOAS."""
        # Mock ParseResult object
        mock_next_token = Mock()
        mock_next_token.query = "cursor=abc123&page_size=1000&page_mode=sequenced"

        with patch("urllib.parse.parse_qsl") as mock_parse:
            mock_parse.return_value = [
                ("cursor", "abc123"),
                ("page_size", "1000"),
                ("page_mode", "sequenced"),
            ]

            params = stream_instance.get_url_params(
                context=None, next_page_token=mock_next_token,
            )

            assert params["cursor"] == "abc123"
            assert params["page_size"] == "1000"
            assert params["page_mode"] == "sequenced"

    @pytest.mark.unit
    def test_get_url_params_hateoas_error_handling(self, stream_instance) -> None:
        """Testa tratamento de erro na continuação HATEOAS."""
        # Mock ParseResult object com erro
        mock_next_token = Mock()
        mock_next_token.query = "invalid_query"

        with patch("urllib.parse.parse_qsl") as mock_parse:
            mock_parse.side_effect = ValueError("Parse error")

            # Deve fallback para parâmetros base
            params = stream_instance.get_url_params(
                context=None, next_page_token=mock_next_token,
            )

            assert "page_mode" in params
            assert "page_size" in params

    @pytest.mark.unit
    def test_get_url_params_incremental_sync(self, stream_instance, mock_tap) -> None:
        """Testa parâmetros para sync incremental."""
        # Mock bookmark value
        with patch.object(
            stream_instance, "get_starting_replication_key_value",
        ) as mock_bookmark:
            mock_bookmark.return_value = "2024-01-01T10:00:00Z"

            stream_instance.get_url_params(context=None, next_page_token=None)

            # Verifica se apply_incremental_filters foi chamado
            mock_tap.apply_incremental_filters.assert_called_once()

    @pytest.mark.unit
    def test_get_url_params_incremental_fallback(self, mock_tap) -> None:
        """Testa fallback para sync incremental sem método do tap."""
        # Remove método do tap para testar fallback
        del mock_tap.apply_incremental_filters

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        with patch.object(
            stream, "get_starting_replication_key_value",
        ) as mock_bookmark:
            mock_bookmark.return_value = "2024-01-01T10:00:00Z"

            params = stream.get_url_params(context=None, next_page_token=None)

            # Deve incluir filtro mod_ts__gte com overlap de 5 minutos
            assert "mod_ts__gte" in params

            # Verifica se aplicou overlap de 5 minutos
            bookmark_time = datetime.fromisoformat(
                "2024-01-01T10:00:00Z".replace("Z", "+00:00"),
            )
            expected_time = bookmark_time - timedelta(minutes=5)

            param_time = datetime.fromisoformat(
                params["mod_ts__gte"].replace("Z", "+00:00"),
            )
            assert param_time == expected_time

    @pytest.mark.unit
    def test_get_url_params_full_table_sync(self, mock_tap) -> None:
        """Testa parâmetros para sync full table."""
        mock_tap.config["enable_incremental"] = False

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        # Mock resume context
        resume_context = {"min_id_in_target": 1000}
        with patch.object(stream, "_get_resume_context") as mock_resume:
            mock_resume.return_value = resume_context

            stream.get_url_params(context=None, next_page_token=None)

            # Verifica se apply_full_sync_filters foi chamado
            mock_tap.apply_full_sync_filters.assert_called_once()

    @pytest.mark.unit
    def test_get_url_params_full_table_fallback(self, mock_tap) -> None:
        """Testa fallback para sync full table sem método do tap."""
        mock_tap.config["enable_incremental"] = False
        # Remove método do tap para testar fallback
        del mock_tap.apply_full_sync_filters

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        # Mock resume context
        resume_context = {"min_id_in_target": 1000}
        with patch.object(stream, "_get_resume_context") as mock_resume:
            mock_resume.return_value = resume_context

            params = stream.get_url_params(context=None, next_page_token=None)

            # Deve incluir filtro id__lt e ordering
            assert params["id__lt"] == 1000
            assert params["ordering"] == "-id"


class TestStreamResumeContext:
    """Testes para contexto de resume."""

    @pytest.fixture
    def stream_instance(self):
        """Instância do stream para testes."""
        mock_tap = Mock()
        mock_tap.config = {
            "base_url": "https://wms.test.com",
            "resume_config": {
                "test_entity": {
                    "enabled": True,
                    "has_existing_data": True,
                    "min_id_in_target": 5000,
                    "total_records": 100000,
                    "strategy": "id_based_resume",
                },
            },
        }

        return WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

    @pytest.mark.unit
    def test_get_resume_context_enabled(self, stream_instance) -> None:
        """Testa obtenção de contexto de resume habilitado."""
        context = stream_instance._get_resume_context(None)

        assert context is not None
        assert context["has_existing_data"] is True
        assert context["min_id_in_target"] == 5000
        assert context["total_records"] == 100000
        assert context["sync_strategy"] == "id_based_resume"

    @pytest.mark.unit
    def test_get_resume_context_disabled(self) -> None:
        """Testa contexto de resume desabilitado."""
        mock_tap = Mock()
        mock_tap.config = {
            "base_url": "https://wms.test.com",
            "resume_config": {
                "test_entity": {
                    "enabled": False,
                },
            },
        }

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        context = stream._get_resume_context(None)
        assert context is None

    @pytest.mark.unit
    def test_get_resume_context_not_configured(self) -> None:
        """Testa contexto sem configuração de resume."""
        mock_tap = Mock()
        mock_tap.config = {"base_url": "https://wms.test.com"}

        stream = WMSAdvancedStream(
            tap=mock_tap,
            entity_name="test_entity",
            schema={"type": "object"},
        )

        context = stream._get_resume_context(None)
        assert context is None


class TestStreamError:
    """Testes para tratamento de erros no stream."""

    @pytest.mark.unit
    def test_stream_initialization_without_base_url(self) -> None:
        """Testa inicialização sem base_url."""
        mock_tap = Mock()
        mock_tap.config = {}  # Sem base_url

        with pytest.raises(ValueError, match="base_url MUST be configured"):
            WMSAdvancedStream(
                tap=mock_tap,
                entity_name="test_entity",
                schema={"type": "object"},
            )

    @pytest.mark.unit
    def test_stream_initialization_empty_base_url(self) -> None:
        """Testa inicialização com base_url vazia."""
        mock_tap = Mock()
        mock_tap.config = {"base_url": ""}  # Base URL vazia

        with pytest.raises(ValueError, match="base_url MUST be configured"):
            WMSAdvancedStream(
                tap=mock_tap,
                entity_name="test_entity",
                schema={"type": "object"},
            )

    @pytest.mark.unit
    def test_stream_initialization_none_base_url(self) -> None:
        """Testa inicialização com base_url None."""
        mock_tap = Mock()
        mock_tap.config = {"base_url": None}  # Base URL None

        with pytest.raises(ValueError, match="base_url MUST be configured"):
            WMSAdvancedStream(
                tap=mock_tap,
                entity_name="test_entity",
                schema={"type": "object"},
            )
