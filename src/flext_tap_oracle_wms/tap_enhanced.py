"""Enhanced Oracle WMS TAP with integrated error recovery and resilience."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING, Any

import httpx
from singer_sdk import Stream, Tap

from .auth import get_wms_headers
from .config import WMSConfig
from .error_recovery import ErrorRecoveryManager
from .validation import validate_complete_config


if TYPE_CHECKING:
    from collections.abc import Generator


logger = logging.getLogger(__name__)


class EnhancedWMSTap(Tap):
    """Enhanced Oracle WMS TAP with error recovery and resilience features."""

    name = "tap-oracle-wms-enhanced"
    config_jsonschema = WMSConfig.model_json_schema()

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize enhanced WMS TAP with error recovery.

        Args:
        ----
            config: Configuration dictionary

        """
        super().__init__(config=config)

        # Initialize error recovery manager
        self.error_manager = ErrorRecoveryManager(config)

        # Initialize HTTP client with timeouts
        timeout_config = httpx.Timeout(
            connect=config.get("connect_timeout", 30.0),
            read=config.get("request_timeout", 7200.0),
            write=config.get("write_timeout", 30.0),
            pool=config.get("pool_timeout", 30.0),
        )

        self.client = httpx.AsyncClient(
            timeout=timeout_config,
            verify=config.get("verify_ssl", True),
            headers=get_wms_headers(config),
        )

        # Performance tracking
        self.metrics = {
            "requests_made": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "records_extracted": 0,
            "errors_recovered": 0,
            "start_time": datetime.now(timezone.utc),
        }

    def discover_streams(self) -> list[Stream]:
        """Discover available streams from WMS API.

        Returns:
        -------
            List of discovered streams

        """
        streams = []

        # Define standard WMS entities
        entities = self.config.get(
            "entities",
            [
                "inventory",
                "orders",
                "shipments",
                "items",
                "locations",
                "receipts",
                "picks",
                "adjustments",
            ],
        )

        for entity in entities:
            stream = WMSStream(
                tap=self,
                name=entity,
                schema=self._get_entity_schema(entity),
                path=f"/api/{entity}",
            )
            streams.append(stream)

        return streams

    def _get_entity_schema(self, entity_name: str) -> dict[str, Any]:
        """Get JSON schema for an entity.

        Args:
        ----
            entity_name: Name of the entity

        Returns:
        -------
            JSON schema for the entity

        """
        # Base properties common to all entities
        base_properties = {
            "id": {"type": "integer"},
            "created_at": {"type": "string", "format": "date-time"},
            "updated_at": {"type": "string", "format": "date-time"},
        }

        # Entity-specific properties
        entity_properties = {
            "inventory": {
                "item_code": {"type": "string"},
                "location_code": {"type": "string"},
                "quantity_on_hand": {"type": "number"},
                "quantity_available": {"type": "number"},
                "unit_of_measure": {"type": "string"},
            },
            "orders": {
                "order_number": {"type": "string"},
                "customer_code": {"type": "string"},
                "order_date": {"type": "string", "format": "date"},
                "status": {"type": "string"},
                "total_amount": {"type": "number"},
            },
            "shipments": {
                "shipment_number": {"type": "string"},
                "order_id": {"type": "integer"},
                "carrier": {"type": "string"},
                "tracking_number": {"type": "string"},
                "ship_date": {"type": "string", "format": "date"},
            },
        }

        properties = {**base_properties}
        if entity_name in entity_properties:
            properties.update(entity_properties[entity_name])

        return {"type": "object", "properties": properties}

    async def _make_request(
        self, url: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make HTTP request with error recovery.

        Args:
        ----
            url: Request URL
            params: Query parameters

        Returns:
        -------
            Response data

        """
        self.metrics["requests_made"] += 1

        async def request_operation():
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()

        try:
            result = await self.error_manager.handle_error(
                Exception("Initial request"),  # Placeholder for first call
                request_operation,
            )
            self.metrics["requests_successful"] += 1
            return result

        except Exception:
            # If error recovery also fails, try direct request once
            try:
                response = await self.client.get(url, params=params)
                response.raise_for_status()
                result = response.json()
                self.metrics["requests_successful"] += 1
                return result
            except Exception as final_error:
                self.metrics["requests_failed"] += 1
                logger.exception(
                    f"Request failed after recovery attempts: {final_error}"
                )
                raise

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance and error metrics.

        Returns:
        -------
            Dictionary of performance metrics

        """
        runtime = datetime.now(timezone.utc) - self.metrics["start_time"]
        error_summary = self.error_manager.get_error_summary()

        return {
            "runtime_seconds": runtime.total_seconds(),
            "requests": {
                "made": self.metrics["requests_made"],
                "successful": self.metrics["requests_successful"],
                "failed": self.metrics["requests_failed"],
                "success_rate": (
                    self.metrics["requests_successful"]
                    / max(self.metrics["requests_made"], 1)
                )
                * 100,
            },
            "extraction": {
                "records_extracted": self.metrics["records_extracted"],
                "rate_per_minute": (
                    self.metrics["records_extracted"]
                    / max(runtime.total_seconds() / 60, 1)
                ),
            },
            "errors": error_summary,
            "recovery": {"errors_recovered": self.metrics["errors_recovered"]},
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # For sync context, we'll handle cleanup differently

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


class WMSStream(Stream):
    """Enhanced WMS stream with error recovery."""

    def __init__(self, tap: EnhancedWMSTap, name: str, schema: dict, path: str) -> None:
        """Initialize WMS stream.

        Args:
        ----
            tap: Parent TAP instance
            name: Stream name
            schema: JSON schema
            path: API path

        """
        super().__init__(tap, schema, name)
        self.path = path
        self.wms_tap = tap

    def get_records(self, context: dict | None = None) -> Generator[dict, None, None]:
        """Extract records from WMS API.

        Args:
        ----
            context: Stream context

        Yields:
        ------
            Individual records

        """
        # Run async extraction in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            records = loop.run_until_complete(self._extract_records_async(context))
            yield from records
        finally:
            loop.close()

    async def _extract_records_async(self, context: dict | None = None) -> list[dict]:
        """Async record extraction with pagination and error recovery.

        Args:
        ----
            context: Stream context

        Returns:
        -------
            List of extracted records

        """
        all_records = []
        page = 1
        page_size = self.wms_tap.config.get("page_size", 1000)

        while True:
            try:
                params = {"page": page, "page_size": page_size}

                # Add filters from config
                if self.wms_tap.config.get("company_code") != "*":
                    params["company"] = self.wms_tap.config["company_code"]

                if self.wms_tap.config.get("facility_code") != "*":
                    params["facility"] = self.wms_tap.config["facility_code"]

                # Add incremental sync parameters
                if context and "replication_key_value" in context:
                    params["modified_since"] = context["replication_key_value"]

                # Make request with error recovery
                url = f"{self.wms_tap.config['base_url']}{self.path}"

                response_data = await self.wms_tap._make_request(url, params)

                records = response_data.get("results", [])
                if not records:
                    break

                # Process and validate records
                processed_records = []
                for record in records:
                    try:
                        # Basic data validation and transformation
                        processed_record = self._process_record(record)
                        processed_records.append(processed_record)
                        self.wms_tap.metrics["records_extracted"] += 1

                    except Exception as record_error:
                        # Handle individual record errors
                        error_context = {
                            "entity_name": self.name,
                            "record_id": record.get("id"),
                            "error_context": {"record_processing": True},
                        }

                        try:
                            await self.wms_tap.error_manager.handle_error(
                                record_error,
                                self._process_record,
                                record,
                                error_context=error_context,
                            )
                        except:
                            # Skip invalid records
                            logger.warning(
                                f"Skipping invalid record in {self.name}: {record_error}"
                            )
                            continue

                all_records.extend(processed_records)

                # Check for more pages
                if not response_data.get("next_page") or len(records) < page_size:
                    break

                page += 1

            except Exception as page_error:
                logger.exception(
                    f"Error extracting page {page} from {self.name}: {page_error}"
                )

                # Try to recover from page-level errors
                try:
                    await self.wms_tap.error_manager.handle_error(
                        page_error, self._extract_page, page, page_size, context
                    )
                    self.wms_tap.metrics["errors_recovered"] += 1
                except:
                    # If recovery fails, stop extraction
                    logger.exception(
                        f"Failed to recover from error in {self.name}, stopping extraction"
                    )
                    break

logger.info("Extracted %s records from %s", len(all_records), self.name)
        return all_records

    def _process_record(self, record: dict) -> dict:
        """Process and validate individual record.

        Args:
        ----
            record: Raw record from API

        Returns:
        -------
            Processed record

        """
        # Ensure required fields exist
        if "id" not in record:
            msg = "Record missing required 'id' field"
            raise ValueError(msg)

        # Add metadata
        processed = dict(record)
        processed["_extracted_at"] = datetime.now(timezone.utc).isoformat()
        processed["_source_system"] = "oracle_wms"
        processed["_stream_name"] = self.name

        return processed

    async def _extract_page(
        self, page: int, page_size: int, context: dict | None = None
    ):
        """Extract a specific page (for error recovery).

        Args:
        ----
            page: Page number
            page_size: Records per page
            context: Stream context

        Returns:
        -------
            Page data

        """
        params = {"page": page, "page_size": page_size}
        url = f"{self.wms_tap.config['base_url']}{self.path}"
        return await self.wms_tap._make_request(url, params)


# Factory function for creating enhanced TAP
def create_enhanced_wms_tap(config: dict[str, Any]) -> EnhancedWMSTap:
    """Create enhanced WMS TAP with validation.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Enhanced WMS TAP instance

    """
    # Validate configuration
    is_valid, errors = validate_complete_config(config)
    if not is_valid:
        error_msg = "Configuration validation failed:\n"
        for category, error_list in errors.items():
            error_msg += f"  {category}: {', '.join(error_list)}\n"
        raise ValueError(error_msg)

    return EnhancedWMSTap(config)
