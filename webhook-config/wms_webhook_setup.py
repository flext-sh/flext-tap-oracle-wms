"""Module wms_webhook_setup."""

# !/usr/bin/env python3
"""Oracle WMS Webhook Configuration Script.

This script helps configure webhooks in Oracle WMS for real-time data synchronization.
It provides both manual configuration instructions and automated setup capabilities.
"""

from datetime import UTC, datetime
import json
import logging
import os


# Constants
HTTP_OK = 200
HTTP_NOT_FOUND = 404

from dotenv import load_dotenv
import httpx


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()


class WMSWebhookConfig:
    """Oracle WMS Webhook Configuration Manager."""

    def __init__(self, base_url: str, username: str, password: str) -> None:
        """Initialize webhook configuration manager."""
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.api_version = "v10"

        # Setup HTTP client
        self.client = httpx.Client(
            auth=(username, password),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "WMS-Webhook-Config/1.0",
            },
            timeout=30,
        )

    def get_webhook_entities(self) -> list[str]:
        """Get list of entities that support webhooks."""
        # Key WMS entities that typically support real-time notifications
        return [
            "facility",
            "item",
            "inventory",
            "location",
            "order_hdr",
            "order_dtl",
            "receipt",
            "receipt_dtl",
            "shipment",
            "allocation",
            "putaway",
            "pick",
            "cycle_count",
            "adjustment",
            "move",
            "wave",
        ]

    def create_webhook_endpoint_config(
        self,
        webhook_url: str,
        entities: list[str],
    ) -> dict:
        """Create webhook endpoint configuration."""
        return {
            "webhook_url": webhook_url,
            "entities": entities,
            "events": [
                "CREATE",  # New record created
                "UPDATE",  # Record updated
                "DELETE",  # Record deleted
                "STATUS_CHANGE",  # Status field changed
            ],
            "filters": {
                "company_code": "RAIZEN",
                "facility_code": "*",  # All facilities
            },
            "format": "json",
            "headers": {
                "Content-Type": "application/json",
                "X-WMS-Source": "Oracle-WMS",
                "X-WMS-Version": "v10",
            },
            "retry_config": {"max_retries": 3, "retry_delay": 5, "timeout": 30},
            "security": {"method": "bearer_token", "token": "${WEBHOOK_AUTH_TOKEN}"},
        }

    def check_webhook_support(self) -> dict[str, bool]:
        """Check which entities support webhook configuration."""
        logger.info("Checking webhook support for WMS entities...")

        supported_entities: dict = {}
        entities = self.get_webhook_entities()

        for entity in entities:
            try:
                # Check if entity has webhook configuration endpoint
                url = f"{self.base_url}/wms/lgfapi/{self.api_version}/entity/{entity}/webhook"
                response = self.client.get(url)

                if response.status_code == HTTP_OK:
                    supported_entities[entity] = True
                    logger.info("✅ %s: Webhook support available", entity)
                elif response.status_code == HTTP_NOT_FOUND:
                    supported_entities[entity] = False
                    logger.info("❌ %s: No webhook support", entity)
                    supported_entities[entity] = False
                    logger.warning(
                        f"⚠️ {entity}: Unknown status ({response.status_code})",
                    )

            except Exception:
                supported_entities[entity] = False
                logger.exception("❌ Error checking support")

        return supported_entities

    def configure_entity_webhook(self, entity: str, webhook_url: str) -> bool:
        """Configure webhook for a specific entity."""
        logger.info("Configuring webhook for entity: %s", entity)

        webhook_config = {
            "url": webhook_url,
            "events": ["CREATE", "UPDATE", "DELETE"],
            "active": True,
            "format": "json",
            "headers": {
                "Content-Type": "application/json",
                "X-WMS-Entity": entity,
                "X-WMS-Timestamp": "{{timestamp}}",
            },
            "filters": {"company_code": "RAIZEN"},
        }

        try:
            url = (
                f"{self.base_url}/wms/lgfapi/{self.api_version}/entity/{entity}/webhook"
            )
            response = self.client.post(url, json=webhook_config)

            if response.status_code in {200, 201}:
                logger.info("✅ Webhook configured for %s", entity)
                return True
            logger.error(
                f"❌ Failed to configure webhook for {entity}: {response.status_code}",
            )
            logger.error("Response: %s", response.text)
            return False

        except Exception:
            logger.exception("❌ Error configuring webhook")
            return False

    def list_existing_webhooks(self) -> dict[str, list]:
        """List all existing webhook configurations."""
        logger.info("Listing existing webhook configurations...")

        webhooks: dict = {}
        entities = self.get_webhook_entities()

        for entity in entities:
            try:
                url = f"{self.base_url}/wms/lgfapi/{self.api_version}/entity/{entity}/webhook"
                response = self.client.get(url)

                if response.status_code == HTTP_OK:
                    webhook_data = response.json()
                    if webhook_data:
                        webhooks[entity] = webhook_data
                        logger.info(
                            f"📋 {entity}: {len(webhook_data)} webhook(s) configured",
                        )

            except Exception:
                logger.exception("Error listing webhooks")

        return webhooks

    def generate_manual_config_instructions(self, webhook_url: str) -> str:
        """Generate manual configuration instructions."""
        entities = self.get_webhook_entities()

        return f"""
# Oracle WMS Webhook Manual Configuration Instructions

## Overview
Configure webhooks in Oracle WMS to send real-time notifications when data changes.

## Target Webhook URL
{webhook_url}

## Entities to Configure
{chr(10).join([f"- {entity}" for entity in entities])}

## Configuration Steps

### 1. Access WMS Admin Console
- Login to Oracle WMS Cloud Console
- Navigate to: Setup > Integration > Webhooks

### 2. Create Webhook Endpoint
- URL: {webhook_url}
- Method: POST
- Format: JSON
- Authentication: Bearer Token

### 3. Configure Each Entity

For each entity ({", ".join(entities)}):

```json
{{
  "entity": "{{entity_name}}",
  "events": ["CREATE", "UPDATE", "DELETE"],
  "url": "{webhook_url}",
  "active": true,
  "format": "json",
  "headers": {{
    "Content-Type": "application/json",
    "X-WMS-Entity": "{{entity_name}}",
    "Authorization": "Bearer {{webhook_token}}"
  }},
  "filters": {{
    "company_code": "RAIZEN",
    "facility_code": "*"
  }},
  "retry_config": {{
    "max_retries": 3,
    "retry_delay": 5
  }}
}}
```

### 4. Test Configuration
- Use WMS test tools to trigger events
- Verify webhook receives notifications
- Check logs for any errors

### 5. Monitor and Maintain
- Set up monitoring for webhook endpoint
- Configure alerting for failed deliveries
- Regular health checks

## Security Considerations
- Use HTTPS for webhook URL
- Implement proper authentication
- Validate webhook signatures
- Rate limiting and DOS protection

## Troubleshooting
- Check WMS logs for webhook errors
- Verify network connectivity
- Test with webhook.site for debugging
- Monitor endpoint response times
"""

    def close(self) -> None:
        """Close HTTP client."""
        self.client.close()


def main() -> None:
    """Main webhook configuration function."""
    logger.info("🔗 Oracle WMS Webhook Configuration Tool")
    logger.info("=" * 50)

    # Get configuration
    base_url = os.getenv("WMS_URL")
    if not base_url:
        msg = "WMS_URL environment variable MUST be configured - NO hardcode allowed"
        raise ValueError(msg)
    username = os.getenv("WMS_USERNAME")
    password = os.getenv("WMS_PASSWORD")
    webhook_url = os.getenv("WEBHOOK_URL", "https://your-api.example.com/wms-webhook")

    if not username or not password:
        logger.error("❌ WMS_USERNAME and WMS_PASSWORD must be set in environment")
        return

    logger.info("WMS URL: %s", base_url)
    logger.info("Username: %s", username)
    logger.info("Webhook URL: %s", webhook_url)

    # Initialize webhook manager
    webhook_manager = WMSWebhookConfig(base_url, username, password)

    try:
        # Check webhook support
        logger.info("\n🔍 Checking webhook support...")
        supported = webhook_manager.check_webhook_support()

        supported_count = sum(1 for v in supported.values() if v)
        total_count = len(supported)

        logger.info("\n📊 Webhook Support Summary:")
        logger.info("✅ Supported: %s/%s entities", supported_count, total_count)

        # List existing webhooks
        logger.info("\n📋 Checking existing webhooks...")
        existing = webhook_manager.list_existing_webhooks()

        if existing:
            logger.info("Found webhooks configured for: %s", ", ".join(existing.keys()))
            logger.info("No existing webhooks found")

        # Generate manual instructions
        logger.info("\n📝 Generating configuration instructions...")
        instructions = webhook_manager.generate_manual_config_instructions(webhook_url)

        # Save instructions to file
        with open("wms_webhook_instructions.md", "w", encoding="utf-8") as f:
            f.write(instructions)

        logger.info("✅ Instructions saved to: wms_webhook_instructions.md")

        # Save configuration summary
        summary = {
            "timestamp": datetime.now(UTC).isoformat(),
            "wms_url": base_url,
            "webhook_url": webhook_url,
            "supported_entities": supported,
            "existing_webhooks": existing,
            "next_steps": [
                "Review wms_webhook_instructions.md",
                "Configure webhook endpoint to receive notifications",
                "Test webhook configuration with sample data",
                "Set up monitoring and alerting",
            ],
        }

        with open("webhook_config_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info("✅ Summary saved to: webhook_config_summary.json")

        logger.info("\n🎯 Next Steps:")
        logger.info("1. Review the generated instructions file")
        logger.info("2. Configure your webhook endpoint")
        logger.info("3. Follow manual configuration steps in WMS console")
        logger.info("4. Test the integration")

    except Exception:
        logger.exception("❌ Error during webhook configuration")
        raise
    finally:
        webhook_manager.close()


if __name__ == "__main__":
    main()
