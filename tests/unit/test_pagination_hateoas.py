"""Testes unitários para paginação HATEOAS."""

from unittest.mock import Mock
from urllib.parse import urlparse

import pytest
from singer_sdk.pagination import BaseHATEOASPaginator

from tap_oracle_wms.streams import WMSAdvancedPaginator


class TestWMSAdvancedPaginator:
    """Testes para o paginador HATEOAS moderno."""

    @pytest.mark.unit
    def test_paginator_inheritance(self) -> None:
        """Testa se herda corretamente de BaseHATEOASPaginator."""
        paginator = WMSAdvancedPaginator()
        assert isinstance(paginator, BaseHATEOASPaginator)

    @pytest.mark.unit
    def test_paginator_initialization(self) -> None:
        """Testa inicialização do paginador."""
        paginator = WMSAdvancedPaginator()

        # Verifica estado inicial
        assert paginator.current_value is None
        assert paginator.finished is False
        assert paginator.count == 0

    @pytest.mark.unit
    def test_get_next_url_with_next_page(self) -> None:
        """Testa extração de next_page URL quando presente."""
        paginator = WMSAdvancedPaginator()

        # Mock response com next_page
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "next_page": "https://wms.test.com/entity?cursor=abc123&page_size=1000"
        }

        next_url = paginator.get_next_url(mock_response)

        assert next_url == "https://wms.test.com/entity?cursor=abc123&page_size=1000"

    @pytest.mark.unit
    def test_get_next_url_without_next_page(self) -> None:
        """Testa extração quando não há next_page."""
        paginator = WMSAdvancedPaginator()

        # Mock response sem next_page
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 98}, {"id": 99}],
            "page_nbr": 5,
            "page_count": 5
        }

        next_url = paginator.get_next_url(mock_response)

        assert next_url is None

    @pytest.mark.unit
    def test_get_next_url_empty_next_page(self) -> None:
        """Testa extração quando next_page está vazio."""
        paginator = WMSAdvancedPaginator()

        # Mock response com next_page vazio
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 99}],
            "next_page": None
        }

        next_url = paginator.get_next_url(mock_response)

        assert next_url is None

    @pytest.mark.unit
    def test_get_next_url_json_error(self) -> None:
        """Testa tratamento de erro JSON."""
        paginator = WMSAdvancedPaginator()

        # Mock response com erro JSON
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")

        next_url = paginator.get_next_url(mock_response)

        assert next_url is None

    @pytest.mark.unit
    def test_get_next_url_key_error(self) -> None:
        """Testa tratamento de KeyError."""
        paginator = WMSAdvancedPaginator()

        # Mock response com estrutura incompleta
        mock_response = Mock()
        mock_response.json.return_value = {"other_field": "value"}

        next_url = paginator.get_next_url(mock_response)

        assert next_url is None

    @pytest.mark.unit
    def test_has_more_with_next_page_and_results(self) -> None:
        """Testa has_more com next_page e resultados."""
        paginator = WMSAdvancedPaginator()

        # Mock response com next_page e resultados
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "next_page": "https://wms.test.com/entity?cursor=def456"
        }

        has_more = paginator.has_more(mock_response)

        assert has_more is True

    @pytest.mark.unit
    def test_has_more_without_next_page(self) -> None:
        """Testa has_more sem next_page."""
        paginator = WMSAdvancedPaginator()

        # Mock response sem next_page
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 99}]
        }

        has_more = paginator.has_more(mock_response)

        assert has_more is False

    @pytest.mark.unit
    def test_has_more_empty_results_no_next(self) -> None:
        """Testa has_more com resultados vazios e sem next_page."""
        paginator = WMSAdvancedPaginator()

        # Mock response vazio
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": []
        }

        has_more = paginator.has_more(mock_response)

        assert has_more is False

    @pytest.mark.unit
    def test_has_more_empty_results_with_next(self) -> None:
        """Testa has_more com resultados vazios mas com next_page."""
        paginator = WMSAdvancedPaginator()

        # Mock response vazio mas com next_page
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [],
            "next_page": "https://wms.test.com/entity?cursor=empty123"
        }

        has_more = paginator.has_more(mock_response)

        # Para primeira página (count == 0), precisa de resultados
        assert has_more is False

    @pytest.mark.unit
    def test_has_more_subsequent_page_empty_results_with_next(self) -> None:
        """Testa has_more em página subsequente com resultados vazios mas next_page."""
        paginator = WMSAdvancedPaginator()

        # Simula que já processou uma página
        paginator._page_count = 1

        # Mock response vazio mas com next_page
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [],
            "next_page": "https://wms.test.com/entity?cursor=empty123"
        }

        has_more = paginator.has_more(mock_response)

        # Para páginas subsequentes, next_page é suficiente
        assert has_more is True

    @pytest.mark.unit
    def test_has_more_error_handling(self) -> None:
        """Testa tratamento de erro em has_more."""
        paginator = WMSAdvancedPaginator()

        # Mock response com erro
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("JSON Error")

        has_more = paginator.has_more(mock_response)

        assert has_more is False

    @pytest.mark.unit
    def test_has_more_attribute_error(self) -> None:
        """Testa tratamento de AttributeError em has_more."""
        paginator = WMSAdvancedPaginator()

        # Mock response sem método json
        mock_response = Mock()
        del mock_response.json

        has_more = paginator.has_more(mock_response)

        assert has_more is False


class TestPaginatorIntegration:
    """Testes de integração do paginador."""

    @pytest.mark.unit
    def test_paginator_full_cycle(self) -> None:
        """Testa ciclo completo de paginação."""
        paginator = WMSAdvancedPaginator()

        # Primeira resposta com next_page
        first_response = Mock()
        first_response.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "next_page": "https://wms.test.com/entity?cursor=page2"
        }

        # Segunda resposta sem next_page
        second_response = Mock()
        second_response.json.return_value = {
            "results": [{"id": 3}, {"id": 4}]
        }

        # Testa primeira página
        assert paginator.has_more(first_response) is True
        next_url_1 = paginator.get_next_url(first_response)
        assert next_url_1 == "https://wms.test.com/entity?cursor=page2"

        # Simula avanço para próxima página
        paginator._page_count = 1

        # Testa segunda página
        assert paginator.has_more(second_response) is False
        next_url_2 = paginator.get_next_url(second_response)
        assert next_url_2 is None

    @pytest.mark.unit
    def test_paginator_with_real_oracle_wms_response(self) -> None:
        """Testa com formato real da resposta Oracle WMS."""
        paginator = WMSAdvancedPaginator()

        # Resposta no formato Oracle WMS real
        mock_response = Mock()
        mock_response.json.return_value = {
            "result_count": 1000,
            "page_count": 10,
            "page_nbr": 3,
            "next_page": "https://ta29.wms.ocs.oraclecloud.com/raizen_test/wms/lgfapi/v10/entity/allocation?cursor=cD0zNDAw&page_size=1000&page_mode=sequenced",
            "previous_page": "https://ta29.wms.ocs.oraclecloud.com/raizen_test/wms/lgfapi/v10/entity/allocation?cursor=cD0xNDAw&page_size=1000&page_mode=sequenced",
            "results": [
                {
                    "id": 2401,
                    "facility_code": "RAIZEN",
                    "company_code": "RAIZEN",
                    "item_id": "ITEM001",
                    "location_id": "A01-01-01",
                    "alloc_qty": 100.0,
                    "mod_ts": "2024-01-01T12:00:00Z"
                }
            ]
        }

        # Testa extração de URL
        next_url = paginator.get_next_url(mock_response)
        expected_url = "https://ta29.wms.ocs.oraclecloud.com/raizen_test/wms/lgfapi/v10/entity/allocation?cursor=cD0zNDAw&page_size=1000&page_mode=sequenced"
        assert next_url == expected_url

        # Testa detecção de mais páginas
        has_more = paginator.has_more(mock_response)
        assert has_more is True

    @pytest.mark.unit
    def test_paginator_cursor_parameter_extraction(self) -> None:
        """Testa extração de parâmetros do cursor."""
        paginator = WMSAdvancedPaginator()

        # URL com cursor complexo
        cursor_url = "https://wms.test.com/entity?cursor=cD0zNDAw&page_size=1000&page_mode=sequenced&ordering=mod_ts"

        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1}],
            "next_page": cursor_url
        }

        next_url = paginator.get_next_url(mock_response)
        assert next_url == cursor_url

        # Verifica se a URL pode ser parseada corretamente
        parsed_url = urlparse(next_url)
        assert parsed_url.netloc == "wms.test.com"
        assert "cursor=cD0zNDAw" in parsed_url.query
        assert "page_size=1000" in parsed_url.query

    @pytest.mark.unit
    @pytest.mark.parametrize(("response_data", "expected_has_more", "expected_next_url"), [
        # Caso 1: Com next_page e resultados
        (
            {
                "results": [{"id": 1}],
                "next_page": "https://test.com/next"
            },
            True,
            "https://test.com/next"
        ),
        # Caso 2: Sem next_page
        (
            {
                "results": [{"id": 1}]
            },
            False,
            None
        ),
        # Caso 3: next_page None
        (
            {
                "results": [{"id": 1}],
                "next_page": None
            },
            False,
            None
        ),
        # Caso 4: next_page string vazia
        (
            {
                "results": [{"id": 1}],
                "next_page": ""
            },
            False,
            None
        ),
        # Caso 5: Resultados vazios sem next_page
        (
            {
                "results": []
            },
            False,
            None
        ),
    ])
    def test_paginator_various_responses(self, response_data, expected_has_more, expected_next_url) -> None:
        """Testa paginador com várias respostas diferentes."""
        paginator = WMSAdvancedPaginator()

        mock_response = Mock()
        mock_response.json.return_value = response_data

        has_more = paginator.has_more(mock_response)
        next_url = paginator.get_next_url(mock_response)

        assert has_more == expected_has_more
        assert next_url == expected_next_url
