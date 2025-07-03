"""Enhanced CLI for Oracle WMS Tap with additional commands."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import click
from dotenv import load_dotenv

from tap_oracle_wms.discovery import EntityDiscovery
from tap_oracle_wms.tap import TapOracleWMS

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """Oracle WMS Tap CLI - Enhanced commands for development and testing."""


@cli.command()
@click.option("--config", default=".env", help="Configuration file or .env")
def validate(config: str) -> None:
    """Validate tap configuration."""
    click.echo("🔍 Validating Oracle WMS Tap configuration...")

    try:
        tap_config = _load_config(config)
        click.echo("✅ Configuration loaded successfully")

        # Validate required fields
        required = ["base_url"]
        missing = [field for field in required if not tap_config.get(field)]

        if missing:
            click.echo(f"❌ Missing required fields: {', '.join(missing)}")
            sys.exit(1)

        # Validate URL format
        base_url = tap_config["base_url"]
        if not base_url.startswith(("http://", "https://")):
            click.echo("❌ base_url must start with http:// or https://")
            sys.exit(1)

        click.echo("✅ Configuration is valid")

    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception("❌ CONFIGURATION ERROR - Invalid tap configuration: %s", e)
        click.echo(f"❌ Configuration error: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", default=".env", help="Configuration file or .env")
def check_connectivity(config: str) -> None:
    """Check connectivity to Oracle WMS instance."""
    click.echo("🌐 Checking Oracle WMS connectivity...")

    try:
        tap_config = _load_config(config)
        discovery = EntityDiscovery(tap_config)

        # Try to discover entities
        result = asyncio.run(discovery.discover_entities())

        if result:
            click.echo(f"✅ Connected successfully! Found {len(result)} entities")
            for entity in list(result.keys())[:5]:
                click.echo(f"  - {entity}")
            max_display = 5
            if len(result) > max_display:
                click.echo(f"  ... and {len(result) - max_display} more")
        else:
            click.echo("⚠️  Connected but no entities found")

    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception("❌ CONNECTION FAILED - Cannot connect to Oracle WMS: %s", e)
        click.echo(f"❌ Connection failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", default=".env", help="Configuration file or .env")
def list_entities(config: str) -> None:
    """List all available entities in WMS."""
    click.echo("📋 Listing Oracle WMS entities...")

    try:
        tap_config = _load_config(config)
        discovery = EntityDiscovery(tap_config)

        entities = asyncio.run(discovery.discover_entities())

        if not entities:
            click.echo("No entities found")
            return

        click.echo(f"\nFound {len(entities)} entities:")
        click.echo("-" * 40)

        for i, (name, url) in enumerate(entities.items(), 1):
            click.echo(f"{i:2d}. {name}")
            click.echo(f"    URL: {url}")

    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception("❌ ENTITY LISTING FAILED - Cannot list entities: %s", e)
        click.echo(f"❌ Error listing entities: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", default=".env", help="Configuration file or .env")
@click.argument("entity_name")
def describe_entity(config: str, entity_name: str) -> None:
    """Describe specific entity schema."""
    click.echo(f"🔍 Describing entity: {entity_name}")

    try:
        tap_config = _load_config(config)
        discovery = EntityDiscovery(tap_config)

        metadata = asyncio.run(discovery.describe_entity(entity_name))

        if not metadata:
            click.echo(f"❌ Entity '{entity_name}' not found or no metadata available")
            sys.exit(1)

        click.echo(f"\nEntity: {entity_name}")
        click.echo("-" * 40)

        if "fields" in metadata:
            fields = metadata["fields"]
            click.echo(f"Fields ({len(fields)}):")
            for field_name, field_info in fields.items():
                field_type = field_info.get("type", "unknown")
                required = " (required)" if field_info.get("required") else ""
                max_length = (
                    f" max:{field_info['max_length']}"
                    if field_info.get("max_length")
                    else ""
                )
                click.echo(f"  - {field_name}: {field_type}{max_length}{required}")

        if "parameters" in metadata:
            params = metadata["parameters"]
            click.echo(f"\nParameters: {', '.join(params)}")

    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception("❌ ENTITY DESCRIPTION FAILED - Cannot describe entity: %s", e)
        click.echo(f"❌ Error describing entity: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", default=".env", help="Configuration file or .env")
@click.argument("entity_name")
@click.option("--limit", default=5, help="Number of sample records")
def sample_data(config: str, entity_name: str, limit: int) -> None:
    """Get sample data from entity."""
    click.echo(f"📊 Getting sample data from: {entity_name}")

    try:
        tap_config = _load_config(config)
        discovery = EntityDiscovery(tap_config)

        samples = asyncio.run(discovery.get_entity_sample(entity_name, limit=limit))

        if not samples:
            click.echo(f"❌ No sample data available for '{entity_name}'")
            sys.exit(1)

        click.echo(
            f"\nSample data from {entity_name} (showing {len(samples)} records):",
        )
        click.echo("-" * 60)

        for i, record in enumerate(samples, 1):
            click.echo(f"\nRecord {i}:")
            for key, value in record.items():
                click.echo(f"  {key}: {value}")

    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception("❌ SAMPLE DATA FAILED - Cannot get sample data: %s", e)
        click.echo(f"❌ Error getting sample data: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", default=".env", help="Configuration file or .env")
@click.option("--output", default="catalog.json", help="Output catalog file")
def generate_catalog(config: str, output: str) -> None:
    """Generate Singer catalog file."""
    click.echo("📄 Generating Singer catalog...")

    try:
        tap_config = _load_config(config)
        tap = TapOracleWMS(config=tap_config)

        catalog = tap.catalog_dict

        with Path(output).open("w") as f:
            json.dump(catalog, f, indent=2)

        streams = catalog.get("streams", [])
        click.echo(f"✅ Catalog generated: {output}")
        click.echo(f"   Streams: {len(streams)}")

        for stream in streams[:5]:
            click.echo(f"   - {stream.get('stream', 'unknown')}")

        max_display_streams = 5
        if len(streams) > max_display_streams:
            click.echo(f"   ... and {len(streams) - max_display_streams} more streams")

    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception(
            "❌ CATALOG GENERATION FAILED - Cannot generate catalog: %s", e
        )
        click.echo(f"❌ Error generating catalog: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", default=".env", help="Configuration file or .env")
def test_singer(config: str) -> None:
    """Test Singer protocol compliance."""
    click.echo("🎯 Testing Singer protocol compliance...")

    try:
        tap_config = _load_config(config)
        tap = TapOracleWMS(config=tap_config)

        # Test basic Singer interface
        tests = [
            ("name", "tap name", hasattr(tap, "name")),
            ("config", "configuration", hasattr(tap, "config")),
            ("catalog_dict", "catalog generation", hasattr(tap, "catalog_dict")),
            ("state_dict", "state management", hasattr(tap, "state_dict")),
            ("discover_streams", "stream discovery", hasattr(tap, "discover_streams")),
        ]

        all_passed = True
        for _attr, description, passed in tests:
            status = "✅" if passed else "❌"
            click.echo(f"  {status} {description}")
            if not passed:
                all_passed = False

        # Test tap name convention
        if hasattr(tap, "name") and tap.name == "tap-oracle-wms":
            click.echo("  ✅ tap name follows convention")
        else:
            click.echo("  ❌ tap name doesn't follow convention")
            all_passed = False

        if all_passed:
            click.echo("\n🎉 All Singer protocol tests passed!")
        else:
            click.echo("\n❌ Some Singer protocol tests failed!")
            sys.exit(1)

    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception(
            "❌ SINGER TEST FAILED - Singer compatibility test failed: %s", e
        )
        click.echo(f"❌ Error testing Singer compliance: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", default=".env", help="Configuration file or .env")
@click.option("--entity", help="Test specific entity")
def test_extraction(config: str, entity: str | None) -> None:
    """Test data extraction capabilities."""
    click.echo("🚀 Testing data extraction...")

    try:
        tap_config = _load_config(config)

        # Override record limit for testing
        tap_config["record_limit"] = 5

        discovery = EntityDiscovery(tap_config)
        entities = asyncio.run(discovery.discover_entities())

        if not entities:
            click.echo("❌ No entities found for testing")
            sys.exit(1)

        # Test specific entity or first available
        test_entity = entity if entity else next(iter(entities.keys()))

        if test_entity not in entities:
            click.echo(f"❌ Entity '{test_entity}' not found")
            sys.exit(1)

        click.echo(f"Testing extraction from: {test_entity}")

        # Get sample data
        samples = asyncio.run(discovery.get_entity_sample(test_entity, limit=5))

        if samples:
            click.echo(f"✅ Successfully extracted {len(samples)} records")
            click.echo(f"   Sample fields: {', '.join(samples[0].keys())}")
        else:
            click.echo("⚠️  No data available for extraction test")

    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception(
            "❌ EXTRACTION TEST FAILED - Data extraction test failed: %s", e
        )
        click.echo(f"❌ Error testing extraction: {e}")
        sys.exit(1)


def _load_config(config_path: str) -> dict[str, Any]:
    """Load configuration from file or environment."""
    if config_path == ".env" or config_path.endswith(".env"):
        # Load from environment variables

        if Path(config_path).exists():
            load_dotenv(config_path)

        return {
            "base_url": os.getenv("TAP_ORACLE_WMS_BASE_URL", ""),
            "username": os.getenv("TAP_ORACLE_WMS_USERNAME", ""),
            "password": os.getenv("TAP_ORACLE_WMS_PASSWORD", ""),
            "company_code": os.getenv("TAP_ORACLE_WMS_COMPANY_CODE", "*"),
            "facility_code": os.getenv("TAP_ORACLE_WMS_FACILITY_CODE", "*"),
            "page_size": int(os.getenv("TAP_ORACLE_WMS_PAGE_SIZE", "100")),
            "request_timeout": int(os.getenv("TAP_ORACLE_WMS_REQUEST_TIMEOUT", "120")),
            "verify_ssl": os.getenv("TAP_ORACLE_WMS_VERIFY_SSL", "true").lower()
            == "true",
            "record_limit": int(os.getenv("TAP_ORACLE_WMS_RECORD_LIMIT", "1000")),
        }
    # Load from JSON file
    with Path(config_path).open() as f:
        return dict(json.load(f))


if __name__ == "__main__":
    cli()
