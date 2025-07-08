"""Modern Oracle WMS Tap - Clean, enterprise-ready implementation."""

from __future__ import annotations

import logging
import os
from typing import Any

from singer_sdk import Tap, typing as th

from .client import WMSClient
from .discovery_modern import EntityDiscovery
from .models import TapMetrics, WMSConfig
from .stream_modern import WMSStream

logger = logging.getLogger(__name__)


class TapOracleWMS(Tap):
    """Modern Oracle WMS Tap - Enterprise implementation.

    Simplified from over-engineered original with:
    - Single configuration system (no more 4 overlapping systems)
    - Clean Pydantic models
    - SOLID architecture
    - Minimal dependencies
    - Maximum performance
    """

    name = "tap-oracle-wms"

    # Simplified configuration schema using Singer SDK patterns
    config_jsonschema = th.PropertiesList(
        th.Property(
            "base_url",
            th.StringType,
            required=True,
            description="Oracle WMS base URL",
        ),
        th.Property("username", th.StringType, required=True, description="Username"),
        th.Property("password", th.StringType, required=True, description="Password"),
        th.Property(
            "company_code",
            th.StringType,
            default="*",
            description="Company code",
        ),
        th.Property(
            "facility_code",
            th.StringType,
            default="*",
            description="Facility code",
        ),
        th.Property(
            "page_size",
            th.IntegerType,
            default=100,
            description="Records per page",
        ),
        th.Property(
            "request_timeout",
            th.IntegerType,
            default=120,
            description="Request timeout",
        ),
        th.Property(
            "verify_ssl",
            th.BooleanType,
            default=True,
            description="Verify SSL",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Start date for incremental sync",
        ),
    ).to_dict()

    def __init__(
        self,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Initialize tap with configuration."""
        super().__init__(*args, **kwargs)

        # Initialize components
        self.wms_config = self._create_wms_config()
        self.metrics = TapMetrics()
        self.client: WMSClient | None = None
        self.discovery: EntityDiscovery | None = None

    def _create_wms_config(self) -> WMSConfig:
        """Create WMS configuration from Singer config.

        Replaces the complex 4-layer configuration system with simple mapping.
        """
        # Map environment variables (simplified from 50+ variables)
        env_mapping = {
            "base_url": "TAP_ORACLE_WMS_BASE_URL",
            "username": "TAP_ORACLE_WMS_USERNAME",
            "password": "TAP_ORACLE_WMS_PASSWORD",
            "company_code": "TAP_ORACLE_WMS_COMPANY_CODE",
            "facility_code": "TAP_ORACLE_WMS_FACILITY_CODE",
        }

        # Build config with precedence: config file > env vars > defaults
        config_data = dict(self.config)

        for config_key, env_key in env_mapping.items():
            env_value = os.getenv(env_key)
            if env_value and config_key not in config_data:
                config_data[config_key] = env_value

        try:
            return WMSConfig(**config_data)
        except Exception:
            self.logger.exception("Invalid configuration")
            raise

    def discover_streams(self) -> list[WMSStream]:
        """Discover available WMS streams.

        Simplified from complex multi-class discovery system.
        """
        logger.info("Starting stream discovery")

        # Initialize client and discovery
        with WMSClient(self.wms_config, self.metrics) as client:
            discovery = EntityDiscovery(client, self.metrics)

            # Discover entities
            entities = discovery.discover_all_entities()

            if not entities:
                logger.warning("No entities discovered")
                return []

            # Create streams
            streams = []
            for entity_name, entity in entities.items():
                try:
                    # Generate schema for entity
                    schema = discovery.get_entity_schema(entity)

                    # Create stream
                    stream = WMSStream(
                        tap=self,
                        entity=entity,
                        client=client,
                        metrics=self.metrics,
                        schema=schema,
                    )

                    streams.append(stream)
                    logger.debug("Created stream: %s", entity_name)

                except (ValueError, KeyError, TypeError) as e:
                    logger.warning("Failed to create stream for %s: %s", entity_name, e)
                    continue

            logger.info("Discovered %d streams", len(streams))
            return streams

    def test_connection(self) -> bool:
        """Test connection to Oracle WMS."""
        logger.info("Testing WMS connection")

        try:
            with WMSClient(self.wms_config, self.metrics) as client:
                success = client.test_connection()

            if success:
                logger.info("Connection test successful")
            else:
                logger.error("Connection test failed")

        except (ValueError, KeyError, TypeError):
            logger.exception("Connection test error")
            return False
        else:
            return success

    def get_metrics(self) -> dict[str, Any]:
        """Get tap performance metrics."""
        return {
            "records_extracted": self.metrics.records_extracted,
            "entities_discovered": self.metrics.entities_discovered,
            "api_calls_made": self.metrics.api_calls_made,
            "duration_seconds": (
                self.metrics.last_activity - self.metrics.start_time
            ).total_seconds(),
        }


# CLI entry point
def main() -> None:
    """Run the CLI entry point."""
    TapOracleWMS.cli()


if __name__ == "__main__":
    main()
