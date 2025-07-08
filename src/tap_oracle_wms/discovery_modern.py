"""Modern entity discovery for Oracle WMS - Simplified and efficient."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .models import TapMetrics, WMSEntity

if TYPE_CHECKING:
    from .client import WMSClient

logger = logging.getLogger(__name__)


class EntityDiscovery:
    """Simplified entity discovery replacing the over-engineered multi-class system.

    Consolidates functionality from:
    - EntityDiscovery (facade)
    - EntityDiscoveryCore
    - SchemaGenerator
    - Multiple discovery helpers

    Into a single, focused class following KISS principle.
    """

    def __init__(self, client: WMSClient, metrics: TapMetrics) -> None:
        """Initialize entity discovery with client and metrics."""
        self.client = client
        self.metrics = metrics

    def discover_all_entities(self) -> dict[str, WMSEntity]:
        """Discover all available WMS entities.

        Returns:
            Dictionary mapping entity names to WMSEntity objects

        """
        logger.info("Starting entity discovery")

        entities = {}

        # Try API-based discovery first
        try:
            api_entities = self.client.discover_entities()
            for entity_data in api_entities:
                entity = self._parse_entity_from_api(entity_data)
                if entity:
                    entities[entity.name] = entity
        except (ValueError, KeyError, TypeError) as e:
            logger.warning("API discovery failed: %s", e)

        # Fallback to common WMS entities if API discovery fails
        if not entities:
            entities = self._get_common_wms_entities()

        self.metrics.entities_discovered = len(entities)
        logger.info("Discovered %d entities", len(entities))

        return entities

    def get_entity_schema(self, entity: WMSEntity) -> dict[str, Any]:
        """Generate JSON schema for entity.

        Simplified from complex schema generation system.
        """
        logger.debug("Generating schema for entity: %s", entity.name)

        # Try to get a sample record to infer schema
        try:
            data = self.client.get_entity_data(
                entity.name,
                {"limit": 1, "page_size": 1},
            )

            records = self._extract_records_from_response(data)
            if records:
                return self._infer_schema_from_record(records[0])

        except (ValueError, KeyError, TypeError) as e:
            logger.warning("Failed to sample %s: %s", entity.name, e)

        # Fallback to generic schema
        return self._get_generic_schema()

    def _parse_entity_from_api(self, entity_data: dict[str, Any]) -> WMSEntity | None:
        """Parse entity from API discovery response."""
        try:
            name = entity_data.get("name") or entity_data.get("entity_name")
            endpoint = entity_data.get("endpoint") or f"/api/{name}"

            if not name:
                return None

            # Check if entity supports incremental sync
            has_mod_ts = (
                "mod_ts" in entity_data.get("fields", [])
                or "modified_timestamp" in entity_data.get("fields", [])
                or entity_data.get("supports_incremental", False)
            )

            return WMSEntity(
                name=name,
                endpoint=endpoint,
                has_mod_ts=has_mod_ts,
                fields=entity_data.get("fields", []),
            )

        except (ValueError, KeyError, TypeError) as e:
            logger.warning("Failed to parse entity: %s", e)
            return None

    def _get_common_wms_entities(self) -> dict[str, WMSEntity]:
        """Get common Oracle WMS entities as fallback.

        Based on standard Oracle WMS API entities.
        """
        common_entities = [
            ("item_master", True),
            ("location", False),
            ("order_hdr", True),
            ("order_dtl", True),
            ("allocation", True),
            ("inventory", True),
            ("receiving", True),
            ("picking", True),
        ]

        entities = {}
        for name, has_mod_ts in common_entities:
            # Test if entity actually exists
            try:
                self.client.get_entity_data(name, {"limit": 1})
                entities[name] = WMSEntity(
                    name=name,
                    endpoint=f"/api/{name}",
                    has_mod_ts=has_mod_ts,
                    fields=[],
                )
                logger.debug("Confirmed entity exists: %s", name)
            except (ValueError, KeyError, TypeError):
                logger.debug("Entity not available: %s", name)
                continue

        return entities

    def _extract_records_from_response(
        self,
        data: dict[str, Any] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Extract records from API response."""
        # Handle different response formats
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Try common pagination patterns
            for key in ["data", "records", "items", "results"]:
                if key in data and isinstance(data[key], list):
                    return data[key]  # type: ignore[no-any-return]
            # Single record response
            if "id" in data or "name" in data:
                return [data]

        return []

    def _infer_schema_from_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Infer JSON schema from sample record.

        Simplified from complex schema generation logic.
        """
        properties = {}

        for field_name, value in record.items():
            field_type = "string"  # Default

            if isinstance(value, bool):
                field_type = "boolean"
            elif isinstance(value, int):
                field_type = "integer"
            elif isinstance(value, float):
                field_type = "number"
            elif isinstance(value, list):
                field_type = "array"
            elif isinstance(value, dict):
                field_type = "object"
            elif value is None:
                field_type = "null"

            properties[field_name] = {"type": field_type}

        return {
            "type": "object",
            "properties": properties,
            "additionalProperties": True,  # Allow extra fields
        }

    def _get_generic_schema(self) -> dict[str, Any]:
        """Return generic schema for when sampling fails."""
        return {
            "type": "object",
            "properties": {
                "id": {"type": ["string", "integer", "null"]},
                "mod_ts": {"type": ["string", "null"], "format": "date-time"},
            },
            "additionalProperties": True,
        }
