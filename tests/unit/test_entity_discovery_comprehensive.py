"""Comprehensive tests for entity discovery functionality."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import base64
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from flext_tap_oracle_wms.infrastructure.entity_discovery import (
    EntityDescriptionError,
    EntityDiscovery,
    EntityDiscoveryError,
    NetworkError,
)


class TestEntityDiscoveryComprehensive:
    """Comprehensive tests for entity discovery functionality."""

    def create_test_discovery(
        self,
        config: dict[str, Any] | None = None,
        cache_manager: Mock | None = None,
    ) -> EntityDiscovery:
        """Create test entity discovery instance."""
        if config is None:
            config = {
                "base_url": "https://test-wms.oracle.com",
                "username": "test_user",
                "password": "test_pass",
                "auth_method": "basic",
            }

        if cache_manager is None:
            cache_manager = Mock()
            cache_manager.get_cached_value.return_value = None
            cache_manager.set_cached_value.return_value = None

        return EntityDiscovery(config, cache_manager)

    def test_entity_discovery_initialization(self) -> None:
        """Test entity discovery initialization."""
        config = {
            "base_url": "https://test-wms.oracle.com/",
            "username": "test_user",
            "password": "test_pass",
        }
        cache_manager = Mock()
        headers = {"Custom-Header": "value"}

        discovery = EntityDiscovery(config, cache_manager, headers)

        if discovery.config != config:
            msg = f"Expected {config}, got {discovery.config}"
            raise AssertionError(msg)
        assert discovery.cache_manager == cache_manager
        if discovery.headers != headers:
            msg = f"Expected {headers}, got {discovery.headers}"
            raise AssertionError(msg)
        assert discovery.base_url == "https://test-wms.oracle.com"
        if "entity/" not in discovery.entity_endpoint:
            msg = f"Expected {'entity/'} in {discovery.entity_endpoint}"
            raise AssertionError(msg)

    def test_entity_discovery_default_headers(self) -> None:
        """Test entity discovery with default headers."""
        config = {"base_url": "https://test.com"}
        cache_manager = Mock()

        discovery = EntityDiscovery(config, cache_manager)

        if discovery.headers != {}:
            msg = f"Expected {{}}, got {discovery.headers}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_discover_entities_from_cache(self) -> None:
        """Test entity discovery from cache."""
        cached_entities = {"entity1": "url1", "entity2": "url2"}
        cache_manager = Mock()
        cache_manager.get_cached_value.return_value = cached_entities

        discovery = self.create_test_discovery(cache_manager=cache_manager)

        result = await discovery.discover_entities()

        if result != cached_entities:
            msg = f"Expected {cached_entities}, got {result}"
            raise AssertionError(msg)
        cache_manager.get_cached_value.assert_called_once_with("entity:all")
        cache_manager.set_cached_value.assert_not_called()

    @pytest.mark.asyncio
    async def test_discover_entities_from_api(self) -> None:
        """Test entity discovery from API."""
        cache_manager = Mock()
        cache_manager.get_cached_value.return_value = None

        discovery = self.create_test_discovery(cache_manager=cache_manager)

        # Mock API response
        api_response = {"entity1": "url1", "entity2": "url2"}

        with patch.object(
            discovery,
            "_fetch_entities_from_api",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = api_response

            result = await discovery.discover_entities()

            if result != api_response:
                msg = f"Expected {api_response}, got {result}"
                raise AssertionError(msg)
            cache_manager.set_cached_value.assert_called_once_with(
                "entity:all",
                api_response,
            )

    @pytest.mark.asyncio
    async def test_discover_entities_invalid_cache(self) -> None:
        """Test entity discovery with invalid cache data."""
        cache_manager = Mock()
        cache_manager.get_cached_value.return_value = "invalid_data"  # Not a dict

        discovery = self.create_test_discovery(cache_manager=cache_manager)

        api_response = {"entity1": "url1"}

        with patch.object(
            discovery,
            "_fetch_entities_from_api",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = api_response

            result = await discovery.discover_entities()

            if result != api_response:
                msg = f"Expected {api_response}, got {result}"
                raise AssertionError(msg)
            mock_fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_describe_entity_from_cache(self) -> None:
        """Test entity description from cache."""
        cached_metadata = {"fields": ["id", "name"], "type": "object"}
        cache_manager = Mock()
        cache_manager.get_cached_value.return_value = cached_metadata

        discovery = self.create_test_discovery(cache_manager=cache_manager)

        result = await discovery.describe_entity("test_entity")

        if result != cached_metadata:
            msg = f"Expected {cached_metadata}, got {result}"
            raise AssertionError(msg)
        cache_manager.get_cached_value.assert_called_once_with("metadata:test_entity")

    @pytest.mark.asyncio
    async def test_describe_entity_from_api(self) -> None:
        """Test entity description from API."""
        cache_manager = Mock()
        cache_manager.get_cached_value.return_value = None

        discovery = self.create_test_discovery(cache_manager=cache_manager)

        api_metadata = {"fields": ["id", "name"]}

        with patch.object(
            discovery,
            "_fetch_entity_metadata",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = api_metadata

            result = await discovery.describe_entity("test_entity")

            if result != api_metadata:
                msg = f"Expected {api_metadata}, got {result}"
                raise AssertionError(msg)
            cache_manager.set_cached_value.assert_called_once_with(
                "metadata:test_entity",
                api_metadata,
            )

    @pytest.mark.asyncio
    async def test_describe_entity_not_found(self) -> None:
        """Test entity description when entity not found."""
        cache_manager = Mock()
        cache_manager.get_cached_value.return_value = None

        discovery = self.create_test_discovery(cache_manager=cache_manager)

        with patch.object(
            discovery,
            "_fetch_entity_metadata",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = None

            result = await discovery.describe_entity("nonexistent_entity")

            assert result is None
            cache_manager.set_cached_value.assert_not_called()

    @pytest.mark.asyncio
    async def test_describe_entity_invalid_cache(self) -> None:
        """Test entity description with invalid cache data."""
        cache_manager = Mock()
        cache_manager.get_cached_value.return_value = "invalid_data"  # Not a dict

        discovery = self.create_test_discovery(cache_manager=cache_manager)

        api_metadata = {"fields": ["id"]}

        with patch.object(
            discovery,
            "_fetch_entity_metadata",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = api_metadata

            result = await discovery.describe_entity("test_entity")

            if result != api_metadata:
                msg = f"Expected {api_metadata}, got {result}"
                raise AssertionError(msg)
            mock_fetch.assert_called_once()

    def test_filter_entities_no_filters(self) -> None:
        """Test entity filtering with no filters configured."""
        discovery = self.create_test_discovery()
        entities = {"entity1": "url1", "entity2": "url2", "entity3": "url3"}

        result = discovery.filter_entities(entities)

        if result != entities:
            msg = f"Expected {entities}, got {result}"
            raise AssertionError(msg)

    def test_filter_entities_configured_list(self) -> None:
        """Test entity filtering with configured entity list."""
        config = {
            "base_url": "https://test.com",
            "entities": ["entity1", "entity3"],
        }
        discovery = self.create_test_discovery(config)
        entities = {"entity1": "url1", "entity2": "url2", "entity3": "url3"}

        result = discovery.filter_entities(entities)

        expected = {"entity1": "url1", "entity3": "url3"}
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    def test_filter_entities_include_patterns(self) -> None:
        """Test entity filtering with include patterns."""
        config = {
            "base_url": "https://test.com",
            "entity_patterns": {
                "include": ["^order", ".*item.*"],
            },
        }
        discovery = self.create_test_discovery(config)
        entities = {
            "order_header": "url1",
            "order_line": "url2",
            "item_master": "url3",
            "customer": "url4",
        }

        result = discovery.filter_entities(entities)

        expected = {
            "order_header": "url1",
            "order_line": "url2",
            "item_master": "url3",
        }
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    def test_filter_entities_exclude_patterns(self) -> None:
        """Test entity filtering with exclude patterns."""
        config = {
            "base_url": "https://test.com",
            "entity_patterns": {
                "exclude": ["temp_", ".*_backup"],
            },
        }
        discovery = self.create_test_discovery(config)
        entities = {
            "order_header": "url1",
            "temp_table": "url2",
            "data_backup": "url3",
            "customer": "url4",
        }

        result = discovery.filter_entities(entities)

        expected = {
            "order_header": "url1",
            "customer": "url4",
        }
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    def test_filter_entities_combined_patterns(self) -> None:
        """Test entity filtering with both include and exclude patterns."""
        config = {
            "base_url": "https://test.com",
            "entity_patterns": {
                "include": ["^order"],
                "exclude": [".*_temp"],
            },
        }
        discovery = self.create_test_discovery(config)
        entities = {
            "order_header": "url1",
            "order_temp": "url2",
            "customer": "url3",
            "order_line": "url4",
        }

        result = discovery.filter_entities(entities)

        expected = {
            "order_header": "url1",
            "order_line": "url4",
        }
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_fetch_entities_from_api_success(self) -> None:
        """Test successful entity fetching from API."""
        discovery = self.create_test_discovery()

        mock_response = Mock()
        mock_response.json.return_value = {"entity1": "url1", "entity2": "url2"}
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            result = await discovery._fetch_entities_from_api()

            expected = {"entity1": "url1", "entity2": "url2"}
            if result != expected:
                msg = f"Expected {expected}, got {result}"
                raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_fetch_entities_from_api_http_error(self) -> None:
        """Test entity fetching with HTTP error."""
        discovery = self.create_test_discovery()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                httpx.HTTPError("Connection failed")
            )

            with pytest.raises(EntityDiscoveryError) as exc_info:
                await discovery._fetch_entities_from_api()

            if "error during entity discovery" not in str(exc_info.value):
                msg = (
                    f"Expected {'error during entity discovery'} in {exc_info.value!s}"
                )
                raise AssertionError(
                    msg,
                )

    @pytest.mark.asyncio
    async def test_fetch_entities_from_api_unexpected_error(self) -> None:
        """Test entity fetching with unexpected error."""
        discovery = self.create_test_discovery()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                ValueError("Unexpected error")
            )

            with pytest.raises(EntityDiscoveryError) as exc_info:
                await discovery._fetch_entities_from_api()

            if "error during entity discovery" not in str(exc_info.value):
                msg = (
                    f"Expected {'error during entity discovery'} in {exc_info.value!s}"
                )
                raise AssertionError(
                    msg,
                )

    def test_prepare_auth_headers_no_auth(self) -> None:
        """Test auth header preparation with no authentication."""
        config = {"base_url": "https://test.com"}
        discovery = self.create_test_discovery(config)
        discovery.headers = {"Custom": "value"}

        result = discovery._prepare_auth_headers()

        if result != {"Custom": "value"}:
            msg = f"Expected {{'Custom': 'value'}}, got {result}"
            raise AssertionError(msg)
        if "Authorization" not in result:
            msg = f"Expected {'Authorization'} not in {result}"
            raise AssertionError(msg)

    def test_prepare_auth_headers_basic_auth(self) -> None:
        """Test auth header preparation with basic authentication."""
        config = {
            "base_url": "https://test.com",
            "auth_method": "basic",
            "username": "test_user",
            "password": "test_pass",
        }
        discovery = self.create_test_discovery(config)
        discovery.headers = {"Custom": "value"}

        result = discovery._prepare_auth_headers()

        expected_credentials = base64.b64encode(b"test_user:test_pass").decode()
        if result["Authorization"] != f"Basic {expected_credentials}":
            msg = f"Expected {f'Basic {expected_credentials}'}, got {result['Authorization']}"
            raise AssertionError(
                msg,
            )
        assert result["Custom"] == "value"

    def test_prepare_auth_headers_basic_auth_missing_credentials(self) -> None:
        """Test auth header preparation with missing credentials."""
        config = {
            "base_url": "https://test.com",
            "auth_method": "basic",
            "username": "",
            "password": "test_pass",
        }
        discovery = self.create_test_discovery(config)

        result = discovery._prepare_auth_headers()

        if "Authorization" not in result:
            msg = f"Expected {'Authorization'} not in {result}"
            raise AssertionError(msg)

    def test_process_api_response_dict(self) -> None:
        """Test API response processing with dictionary format."""
        discovery = self.create_test_discovery()
        data = {"entity1": "url1", "entity2": "url2"}

        result = discovery._process_api_response(data)

        if result != data:
            msg = f"Expected {data}, got {result}"
            raise AssertionError(msg)

    def test_process_api_response_list(self) -> None:
        """Test API response processing with list format."""
        discovery = self.create_test_discovery()
        data = [
            {"name": "entity1", "url": "url1"},
            {"name": "entity2", "href": "url2"},
        ]

        result = discovery._process_api_response(data)

        expected = {"entity1": "url1", "entity2": "url2"}
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    def test_process_api_response_unexpected_type(self) -> None:
        """Test API response processing with unexpected type."""
        discovery = self.create_test_discovery()

        with patch(
            "flext_tap_oracle_wms.infrastructure.entity_discovery.logger",
        ) as mock_logger:
            result = discovery._process_api_response("unexpected_string")

            if result != {}:
                msg = f"Expected {{}}, got {result}"
                raise AssertionError(msg)
            mock_logger.warning.assert_called_once()

    def test_process_dict_response_direct_mapping(self) -> None:
        """Test dictionary response processing with direct mapping."""
        discovery = self.create_test_discovery()
        data: dict[str, object] = {"entity1": "url1", "entity2": "url2"}

        result = discovery._process_dict_response(data)

        if result != data:
            msg = f"Expected {data}, got {result}"
            raise AssertionError(msg)

    def test_process_dict_response_nested_entities(self) -> None:
        """Test dictionary response processing with nested entities."""
        discovery = self.create_test_discovery()
        data: dict[str, object] = {
            "entities": {"entity1": "url1", "entity2": "url2"},
            "metadata": {"version": "1.0"},
        }

        result = discovery._process_dict_response(data)

        expected = {"entity1": "url1", "entity2": "url2"}
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    def test_process_dict_response_unexpected_format(self) -> None:
        """Test dictionary response processing with unexpected format."""
        discovery = self.create_test_discovery()
        data: dict[str, object] = {"unexpected": {"nested": "data"}}

        with patch(
            "flext_tap_oracle_wms.infrastructure.entity_discovery.logger",
        ) as mock_logger:
            result = discovery._process_dict_response(data)

            if result != {}:
                msg = f"Expected {{}}, got {result}"
                raise AssertionError(msg)
            mock_logger.warning.assert_called_once()

    def test_process_nested_entities_dict(self) -> None:
        """Test nested entities processing with dictionary format."""
        discovery = self.create_test_discovery()
        entity_list = {"entity1": "url1", "entity2": "url2"}

        result = discovery._process_nested_entities(entity_list)

        if result != entity_list:
            msg = f"Expected {entity_list}, got {result}"
            raise AssertionError(msg)

    def test_process_nested_entities_list_with_dicts(self) -> None:
        """Test nested entities processing with list of dictionaries."""
        discovery = self.create_test_discovery()
        entity_list = [
            {"name": "entity1", "url": "url1"},
            {"name": "entity2", "href": "url2"},
        ]

        result = discovery._process_nested_entities(entity_list)

        expected = {"entity1": "url1", "entity2": "url2"}
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    def test_process_nested_entities_list_with_strings(self) -> None:
        """Test nested entities processing with list of strings."""
        discovery = self.create_test_discovery()
        entity_list = ["entity1", "entity2"]

        result = discovery._process_nested_entities(entity_list)

        expected = {
            "entity1": f"{discovery.entity_endpoint}/entity1",
            "entity2": f"{discovery.entity_endpoint}/entity2",
        }
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    def test_process_nested_entities_mixed_list(self) -> None:
        """Test nested entities processing with mixed list format."""
        discovery = self.create_test_discovery()
        entity_list = [
            {"name": "entity1", "url": "url1"},
            "entity2",
            {"name": "entity3", "invalid": "data"},  # Missing url/href
        ]

        result = discovery._process_nested_entities(entity_list)

        expected = {
            "entity1": "url1",
            "entity2": f"{discovery.entity_endpoint}/entity2",
        }
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    def test_process_list_response(self) -> None:
        """Test list response processing."""
        discovery = self.create_test_discovery()
        data: list[object] = [
            {"name": "entity1", "url": "url1"},
            "entity2",
            {"name": "entity3", "href": "url3"},
        ]

        result = discovery._process_list_response(data)

        expected = {
            "entity1": "url1",
            "entity2": f"{discovery.entity_endpoint}/entity2",
            "entity3": "url3",
        }
        if result != expected:
            msg = f"Expected {expected}, got {result}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_fetch_entity_metadata_success(self) -> None:
        """Test successful entity metadata fetching."""
        discovery = self.create_test_discovery()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"fields": ["id", "name"], "type": "object"}
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            result = await discovery._fetch_entity_metadata("test_entity")

            expected = {"fields": ["id", "name"], "type": "object"}
            if result != expected:
                msg = f"Expected {expected}, got {result}"
                raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_fetch_entity_metadata_not_found(self) -> None:
        """Test entity metadata fetching when not found."""
        discovery = self.create_test_discovery()

        mock_response = Mock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            result = await discovery._fetch_entity_metadata("nonexistent_entity")

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_entity_metadata_http_error(self) -> None:
        """Test entity metadata fetching with HTTP error."""
        discovery = self.create_test_discovery()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                httpx.HTTPError("Connection failed")
            )

            with pytest.raises(EntityDescriptionError) as exc_info:
                await discovery._fetch_entity_metadata("test_entity")

            if "HTTP error during entity metadata fetch" not in str(exc_info.value):
                msg = f"Expected {'HTTP error during entity metadata fetch'} in {exc_info.value!s}"
                raise AssertionError(
                    msg,
                )

    @pytest.mark.asyncio
    async def test_fetch_entity_metadata_unexpected_error(self) -> None:
        """Test entity metadata fetching with unexpected error."""
        discovery = self.create_test_discovery()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                ValueError("Unexpected error")
            )

            with pytest.raises(EntityDescriptionError) as exc_info:
                await discovery._fetch_entity_metadata("test_entity")

            if "Entity metadata fetch failed" not in str(exc_info.value):
                msg = f"Expected {'Entity metadata fetch failed'} in {exc_info.value!s}"
                raise AssertionError(
                    msg,
                )

    def test_matches_patterns_regex_match(self) -> None:
        """Test pattern matching with regex patterns."""
        patterns = ["^order", ".*item.*", "customer$"]

        if not (EntityDiscovery._matches_patterns("order_header", patterns)):
            msg = f"Expected True, got {EntityDiscovery._matches_patterns('order_header', patterns)}"
            raise AssertionError(
                msg,
            )
        assert EntityDiscovery._matches_patterns("item_master", patterns) is True
        if not (EntityDiscovery._matches_patterns("main_customer", patterns)):
            msg = f"Expected True, got {EntityDiscovery._matches_patterns('main_customer', patterns)}"
            raise AssertionError(
                msg,
            )
        if EntityDiscovery._matches_patterns("supplier", patterns):
            msg = f"Expected False, got {EntityDiscovery._matches_patterns('supplier', patterns)}"
            raise AssertionError(
                msg,
            )

    def test_matches_patterns_case_insensitive(self) -> None:
        """Test pattern matching is case insensitive."""
        patterns = ["ORDER", "Item"]

        if not (EntityDiscovery._matches_patterns("order_header", patterns)):
            msg = f"Expected True, got {EntityDiscovery._matches_patterns('order_header', patterns)}"
            raise AssertionError(
                msg,
            )
        assert EntityDiscovery._matches_patterns("item_master", patterns) is True
        if not (EntityDiscovery._matches_patterns("ORDER_LINE", patterns)):
            msg = f"Expected True, got {EntityDiscovery._matches_patterns('ORDER_LINE', patterns)}"
            raise AssertionError(
                msg,
            )

    def test_matches_patterns_invalid_regex(self) -> None:
        """Test pattern matching with invalid regex falls back to literal match."""
        patterns = ["[invalid", "item"]  # Invalid regex pattern

        # Should fall back to literal string matching
        if not (EntityDiscovery._matches_patterns("[invalid", patterns)):
            msg = f"Expected True, got {EntityDiscovery._matches_patterns('[invalid', patterns)}"
            raise AssertionError(
                msg,
            )
        assert EntityDiscovery._matches_patterns("item_master", patterns) is True
        if EntityDiscovery._matches_patterns("other", patterns):
            msg = f"Expected False, got {EntityDiscovery._matches_patterns('other', patterns)}"
            raise AssertionError(
                msg,
            )

    def test_matches_patterns_empty_patterns(self) -> None:
        """Test pattern matching with empty pattern list."""
        patterns: list[str] = []

        if EntityDiscovery._matches_patterns("any_entity", patterns):
            msg = f"Expected False, got {EntityDiscovery._matches_patterns('any_entity', patterns)}"
            raise AssertionError(
                msg,
            )

    def test_exception_classes(self) -> None:
        """Test custom exception classes."""
        # Test that exceptions can be raised and inherit from Exception
        with pytest.raises(EntityDiscoveryError):
            self._raise_entity_discovery_error()

        with pytest.raises(EntityDescriptionError):
            self._raise_entity_description_error()

        with pytest.raises(NetworkError):
            self._raise_network_error()

    def _raise_entity_discovery_error(self) -> None:
        """Helper function to raise EntityDiscoveryError for testing."""
        msg = "Test discovery error"
        raise EntityDiscoveryError(msg)

    def _raise_entity_description_error(self) -> None:
        """Helper function to raise EntityDescriptionError for testing."""
        msg = "Test description error"
        raise EntityDescriptionError(msg)

    def _raise_network_error(self) -> None:
        """Helper function to raise NetworkError for testing."""
        msg = "Test network error"
        raise NetworkError(msg)

    def test_config_mapper_integration(self) -> None:
        """Test integration with ConfigMapper."""
        config = {
            "base_url": "https://test.com",
            "api_version": "v11",  # Fixed: ConfigMapper looks for "api_version",
            # not "wms_api_version"
            "endpoint_prefix": "/custom/api",  # Fixed: ConfigMapper looks for
            # "endpoint_prefix", not "api_endpoint_prefix"
        }

        discovery = self.create_test_discovery(config)

        # ConfigMapper should be used for API version and endpoint prefix
        if discovery.api_version != "v11":
            msg = f"Expected {'v11'}, got {discovery.api_version}"
            raise AssertionError(msg)
        if "/custom/api" not in discovery.entity_endpoint:
            msg = f"Expected {'/custom/api'} in {discovery.entity_endpoint}"
            raise AssertionError(
                msg,
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
