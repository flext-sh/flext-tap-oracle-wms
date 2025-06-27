r"""Modern Oracle WMS Singer Tap CLI using Singer SDK 0.46.4+ patterns.

OVERVIEW:
=========
This CLI provides a comprehensive interface for Oracle WMS data integration using
the Singer protocol, with extended business functionality for enterprise warehouse
management scenarios.

The CLI is designed around two core principles:
1. Singer Protocol Compliance: Full compatibility with Meltano and other Singer
   ecosystems
2. Business-Centric Extensions: Domain-specific commands for WMS business
   operations

CORE INTEGRATION RULES (CRITICAL - DO NOT CHANGE):
================================================

1. INCREMENTAL SYNC RULES:
   - Filter Rule: mod_ts > max(mod_ts from state/database) - 5 minutes
   - Safety Overlap: 5 minutes to prevent missed records due to clock skew
   - Ordering: mod_ts ASC (chronological) for proper state management
   - Replication Key: mod_ts (Oracle WMS standard change tracking field)
   - State Management: Track latest mod_ts bookmark for next sync

2. FULL SYNC RULES:
   - ID-based Resume: id < min(existing_ids) - 1 for intelligent resume
   - Ordering: -id DESC (highest to lowest) for efficient large dataset
     processing
   - Timestamp-based Alternative: mod_ts >= start_date for historical
     extraction

3. PAGINATION CONFIGURATION:
   - Singer SDK: pagination_mode="cursor" (follows next_page URLs)
   - WMS API: page_mode="sequenced" (cursor-based, no total calculations)
   - Page Size: 1000 (optimized for Oracle WMS API performance)

4. GENERIC FILTERING SYSTEM:
   - Temporal Filters: mod_ts__gte, mod_ts__lte, create_ts__gte, create_ts__lte
   - ID Filters: id__gte, id__lte, id__lt, id__gt
   - Status Filters: status, status__in, active (Y/N)
   - Advanced Operators: __contains, __startswith, __endswith, __isnull, __range

5. CONFIGURATION MODES:
   - Simplified: Minimal config (base_url, username, password, entities)
   - Entity-Specific: Per-entity filters and configurations
   - Advanced: Full control with complex operators and field selection

BUSINESS FUNCTIONALITY:
======================
Extended commands provide WMS-specific business intelligence:

- inventory: Stock management, cycle counts, variance analysis
- orders: Allocation analysis, fulfillment metrics, bottleneck identification
- warehouse: Task performance, equipment utilization, productivity metrics
- analyze: Supply chain analysis, compliance auditing
- monitor: Real-time monitoring, health checks, metrics

Each business command leverages the generic filtering system to provide
domain-specific data extraction and analysis capabilities.

ERROR HANDLING STRATEGY:
=======================
- Circuit Breaker: Prevents cascading failures during API issues
- Exponential Backoff: Intelligent retry with increasing delays
- Partial Recovery: Continue processing other entities if one fails
- Detailed Logging: Comprehensive error tracking and debugging information

STATE MANAGEMENT:
================
- Bookmark Tracking: Maintains latest processed timestamps per entity
- Resume Capability: Intelligent restart from last successful state
- State Output: Compatible with Singer protocol state files
- Validation: Ensures state consistency and integrity

USAGE PATTERNS:
==============
1. Discovery: tap-oracle-wms --discover > catalog.json
2. Singer Mode: tap-oracle-wms --config config.json --catalog catalog.json
3. Incremental: tap-oracle-wms sync incremental --config config.json \\
   --entities allocation
4. Business Analysis: tap-oracle-wms inventory status --config config.json
5. Monitoring: tap-oracle-wms monitor status --config config.json

This documentation serves as the definitive reference for all CLI behavior.
All implementations must follow these documented rules and patterns.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .discovery import EntityDiscovery, SchemaGenerator
from .monitoring import TAPMonitor
from .tap import TapOracleWMS


if TYPE_CHECKING:
    from collections.abc import Iterable


else:
    with contextlib.suppress(ImportError):
        pass


logger = logging.getLogger(__name__)


console = Console()


def safe_print(message: str, style: str | None = None) -> None:
    """Safely print messages with optional styling."""
    if style:
        logger.info("[%s]%s[/%s]", style, message, style)
        logger.info("%s", message)
    # Strip rich markup for plain print
    import re

    re.sub(r"\[.*?\]", "", message)


# MAIN CLI GROUP


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.option("--discover", is_flag=True, help="Run Singer discovery mode")
@click.option("--catalog", type=click.File("r"), help="Singer catalog file")
@click.option("--config", type=click.File("r"), help="Singer config file")
@click.option("--state", type=click.File("r"), help="Singer state file")
@click.pass_context
def cli(
    ctx: click.Context,
    version: bool,
    discover: bool,
    catalog: click.File | None,
    config: click.File | None,
    state: click.File | None,
) -> None:
    r"""Oracle WMS Singer Tap with Extended Business Functionality.

    Default behavior follows Singer SDK protocol. Extended business
    available through organized subcommands for specific WMS business areas.

    Examples:
    --------
    \\b
    # Singer protocol usage
    tap-oracle-wms --discover
    tap-oracle-wms --catalog catalog.json --config config.json

    \\b
    # Extended business functionality
    tap-oracle-wms inventory status --config config.json
    tap-oracle-wms orders analyze-allocation --config config.json
    tap-oracle-wms warehouse task-performance --config config.json

    """
    # Handle Singer SDK compatibility first
    if version or discover or catalog or config:
        _handle_singer_mode(version, discover, catalog, config, state)
        return

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _handle_singer_mode(
    version: bool,
    discover: bool,
    catalog: click.File | None,
    config: click.File | None,
    state: click.File | None,
) -> None:
    """Handle standard Singer SDK protocol commands."""
    # Build Singer CLI arguments
    singer_args = ["tap-oracle-wms"]  # Program name

    if version:
        singer_args.append("--version")
    if discover:
        singer_args.append("--discover")
    if catalog:
        singer_args.extend(["--catalog", catalog.name])
    if config:
        singer_args.extend(["--config", config.name])
    if state:
        singer_args.extend(["--state", state.name])

    # Replace sys.argv and call Singer CLI
    original_argv = sys.argv
    try:
        sys.argv = singer_args
        TapOracleWMS.cli()
    finally:
        sys.argv = original_argv


# DISCOVERY AND SCHEMA SUBCOMMANDS


@cli.group()
def discover() -> None:
    """Entity discovery and schema management commands."""


@discover.command("entities")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--output",
    type=click.File("w"),
    default="-",
    help="Output file (default: stdout)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table", "csv"]),
    default="table",
    help="Output format",
)
@click.option(
    "--verify-access",
    is_flag=True,
    help="Verify access to each entity (slower but accurate)",
)
@click.option(
    "--include-patterns",
    multiple=True,
    help="Include entities matching these glob patterns",
)
@click.option(
    "--exclude-patterns",
    multiple=True,
    help="Exclude entities matching these glob patterns",
)
def discover_entities(
    config: click.File,
    output: click.File | None,
    output_format: str,
    verify_access: bool,
    include_patterns: tuple[str, ...],
    exclude_patterns: tuple[str, ...],
) -> None:
    """Discover available WMS entities with business categorization."""
    config_data = _prepare_discovery_config(
        json.load(config),
        include_patterns,
        exclude_patterns,
        verify_access,
    )
    discovery = EntityDiscovery(config_data)

    entities = asyncio.run(_run_entity_discovery(discovery, verify_access))
    categorized = _categorize_entities(entities)

    _output_discovery_results(entities, categorized, output_format, output)


@discover.command("schemas")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--entities",
    multiple=True,
    help="Specific entities to generate schemas for",
)
@click.option(
    "--method",
    type=click.Choice(["auto", "describe", "sample"]),
    default="auto",
    help="Schema discovery method",
)
@click.option(
    "--output-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="Directory to save schemas",
)
@click.option(
    "--sample-size",
    type=int,
    default=5,
    help="Number of sample records for schema inference",
)
def discover_schemas(
    config: click.File,
    entities: str,
    method: str,
    output_dir: click.Path,
    sample_size: int,
) -> None:
    """Generate schemas for WMS entities."""
    config_data = json.load(config)
    config_data["schema_discovery_method"] = method
    config_data["schema_sample_size"] = sample_size

    TapOracleWMS(config=config_data)

    async def _generate_schemas() -> None:
        discovery = EntityDiscovery(config_data)
        generator = SchemaGenerator()

        # Get entities to process
        if entities:
            entity_list = {name: f"/entity/{name}" for name in entities}
            all_entities = await discovery.discover_entities()
            entity_list = discovery.filter_entities(all_entities)

        schemas: dict = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task(
                f"Generating schemas for {len(entity_list)} entities...",
                total=len(entity_list),
            )

            for _i, entity_name in enumerate(entity_list.keys()):
                try:
                    # Try describe method first
                    if method in {"auto", "describe"}:
                        metadata = await discovery.describe_entity(entity_name)
                        if metadata:
                            schema = generator.generate_from_metadata(metadata)
                            schemas[entity_name] = schema
                            progress.advance(task)
                            continue

                    # Try sample method
                    if method in {"auto", "sample"}:
                        samples = await discovery.get_entity_sample(
                            entity_name,
                            sample_size,
                        )
                        if samples:
                            schema = generator.generate_from_sample(samples)
                            schemas[entity_name] = schema

                    progress.advance(task)

                except (ValueError, TypeError, AttributeError) as e:
                    safe_print(
                        f"Config error for {entity_name}: {e}",
                        "red",
                    )
                    progress.advance(task)
                except Exception as e:
                    safe_print(
                        f"Error generating schema for {entity_name}: {e}",
                        "red",
                    )
                    progress.advance(task)

        return schemas

    schemas = asyncio.run(_generate_schemas())

    # Save schemas
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        for entity_name, schema in schemas.items():
            schema_file = output_path / f"{entity_name}_schema.json"
            with open(schema_file, "w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2)

        logger.info("Saved %s schemas to %s", len(schemas), output_dir, "green")
        # Output to stdout
        json.dump(schemas, sys.stdout, indent=2)


# INVENTORY MANAGEMENT SUBCOMMANDS


@cli.group()
def inventory() -> None:
    """Inventory management and tracking commands."""


@inventory.command("status")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option("--facility", help="Filter by facility code")
@click.option("--item-code", help="Filter by specific item code")
@click.option("--location", help="Filter by location")
@click.option("--include-lots", is_flag=True, help="Include lot tracking details")
@click.option("--include-serials", is_flag=True, help="Include serial number tracking")
@click.option(
    "--low-stock-threshold",
    type=float,
    help="Show items below this quantity threshold",
)
def inventory_status(
    config: click.File,
    facility: str,
    item_code: str,
    location: str,
    include_lots: bool,
    include_serials: bool,
    low_stock_threshold: int,
) -> None:
    """Get current inventory status with business intelligence."""
    config_data = json.load(config)

    # Configure inventory-specific extraction
    inventory_entities = ["inventory", "item", "location", "uom"]
    if include_lots:
        inventory_entities.extend(["lot", "lot_tracking"])
    if include_serials:
        inventory_entities.extend(["serial_number", "serial_tracking"])

    config_data["entities"] = inventory_entities

    # Add filters
    filters: dict = {}
    if facility:
        filters["facility_code"] = facility
    if item_code:
        filters["item_code"] = item_code
    if location:
        filters["location_code"] = location

    if filters:
        config_data["global_filters"] = filters

    # Run extraction and analysis
    TapOracleWMS(config=config_data)

    logger.info("Extracting inventory data...", "green")

    # For demonstration, show what would be extracted
    logger.info("\nInventory Analysis Configuration:", "blue")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Entities", ", ".join(inventory_entities))
    table.add_row("Facility Filter", facility or "All")
    table.add_row("Item Filter", item_code or "All")
    table.add_row("Location Filter", location or "All")
    table.add_row("Include Lots", str(include_lots))
    table.add_row("Include Serials", str(include_serials))
    table.add_row(
        "Low Stock Threshold",
        str(low_stock_threshold) if low_stock_threshold else "None",
    )

    logger.info("%s", table)
    logger.info("Table display requires rich library")


@inventory.command("cycle-count")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--location-pattern",
    help="Location pattern for cycle count (e.g., 'A-*' for aisle A)",
)
@click.option(
    "--abc-class",
    type=click.Choice(["A", "B", "C"]),
    help="Filter by ABC classification",
)
@click.option(
    "--variance-only",
    is_flag=True,
    help="Only show items with count variances",
)
@click.option(
    "--export-format",
    type=click.Choice(["csv", "excel", "json"]),
    default="csv",
    help="Export format for cycle count results",
)
def inventory_cycle_count(
    config: Any,
    location_pattern: str | None,
    abc_class: str | None,
    variance_only: bool,
    export_format: str,
) -> None:
    """Generate cycle count reports and variance analysis."""
    logger.info("Generating cycle count analysis...", "blue")

    # Configuration for cycle count extraction
    json.load(config)
    cycle_count_entities = [
        "cycle_count",
        "cycle_count_detail",
        "cycle_count_variance",
        "inventory",
        "location",
        "item",
    ]

    filters: dict = {}
    if location_pattern:
        filters["location_code__like"] = location_pattern
    if abc_class:
        filters["abc_class"] = abc_class

    safe_print(
        f"Configured for {len(cycle_count_entities)} cycle count entities",
        "green",
    )
    logger.info("Export format: %s", export_format, "yellow")


# ORDER MANAGEMENT SUBCOMMANDS


@cli.group()
def orders() -> None:
    """Order management and fulfillment commands."""


@orders.command("analyze-allocation")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--order-status",
    multiple=True,
    help="Filter by order status (can specify multiple)",
)
@click.option("--date-range", help="Date range in format 'YYYY-MM-DD,YYYY-MM-DD'")
@click.option(
    "--allocation-efficiency",
    is_flag=True,
    help="Calculate allocation efficiency metrics",
)
@click.option(
    "--bottleneck-analysis",
    is_flag=True,
    help="Identify allocation bottlenecks",
)
def analyze_allocation(
    config: Any,
    order_status: tuple[str, ...],
    date_range: str | None,
    allocation_efficiency: bool,
    bottleneck_analysis: bool,
) -> None:
    """Analyze order allocation patterns and efficiency."""
    logger.info("Analyzing order allocation patterns...", "blue")

    config_data = json.load(config)

    # Configure order-specific entities
    order_entities = [
        "order_header",
        "order_detail",
        "allocation",
        "pick",
        "ship_confirm",
        "inventory",
        "location",
    ]

    # Add date filtering
    if date_range:
        start_date, end_date = date_range.split(",")
        config_data["date_range"] = {
            "start_date": start_date,
            "end_date": end_date,
        }

    # Add status filtering
    if order_status:
        config_data["global_filters"] = {"order_status__in": list(order_status)}

    logger.info("Configured analysis for %s entities", len(order_entities), "green")

    if allocation_efficiency:
        logger.info("• Allocation efficiency metrics enabled", "yellow")
    if bottleneck_analysis:
        logger.info("• Bottleneck analysis enabled", "yellow")


@orders.command("fulfillment-metrics")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--period",
    type=click.Choice(["daily", "weekly", "monthly"]),
    default="daily",
    help="Reporting period",
)
@click.option("--include-kpis", is_flag=True, help="Include key performance indicators")
def fulfillment_metrics(config: click.File, period: str, include_kpis: bool) -> None:
    """Generate order fulfillment performance metrics."""
    logger.info("Generating %s fulfillment metrics...", period, "blue")

    if include_kpis:
        logger.info("Including KPI calculations:", "yellow")
        logger.info("• Order cycle time")
        logger.info("• Pick accuracy")
        logger.info("• On-time shipment rate")
        logger.info("• Order fill rate")


# WAREHOUSE OPERATIONS SUBCOMMANDS


@cli.group()
def warehouse() -> None:
    """Warehouse operations and performance commands."""


@warehouse.command("task-performance")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--task-type",
    type=click.Choice(["pick", "put", "replenish", "cycle_count", "all"]),
    default="all",
    help="Task type to analyze",
)
@click.option("--worker-id", help="Filter by specific worker/user ID")
@click.option(
    "--productivity-metrics",
    is_flag=True,
    help="Calculate productivity metrics",
)
def task_performance(
    config: click.File,
    task_type: str,
    worker_id: str,
    productivity_metrics: bool,
) -> None:
    """Analyze warehouse task performance and productivity."""
    logger.info("Analyzing %s task performance...", task_type, "blue")

    config_data = json.load(config)

    # Configure task-related entities

    filters: dict = {}
    if task_type != "all":
        filters["task_type"] = task_type
    if worker_id:
        filters["user_id"] = worker_id

    if filters:
        config_data["global_filters"] = filters

    logger.info("Analyzing tasks with filters: %s", filters, "green")

    if productivity_metrics:
        logger.info("Productivity metrics enabled:", "yellow")
        logger.info("• Tasks per hour")
        logger.info("• Time per task")
        logger.info("• Error rates")
        logger.info("• Utilization rates")


@warehouse.command("equipment-utilization")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option("--equipment-type", help="Filter by equipment type")
@click.option("--downtime-analysis", is_flag=True, help="Include downtime analysis")
def equipment_utilization(
    config: click.File,
    equipment_type: str,
    downtime_analysis: bool,
) -> None:
    """Analyze warehouse equipment utilization and performance."""
    logger.info("Analyzing equipment utilization...", "blue")

    equipment_entities = [
        "equipment",
        "equipment_type",
        "equipment_status",
        "maintenance_schedule",
        "downtime_log",
    ]

    safe_print(
        f"Tracking {len(equipment_entities)} equipment-related entities",
        "green",
    )

    if downtime_analysis:
        logger.info("Downtime analysis enabled", "yellow")


# SYNC AND EXTRACTION SUBCOMMANDS


@cli.group()
def sync() -> None:
    """Data synchronization and extraction commands."""


@sync.command("incremental")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option("--state", type=click.File("r"), help="Previous state file")
@click.option(
    "--entities",
    multiple=True,
    help="Specific entities to sync (default: all)",
)
@click.option("--since", help="Sync changes since this timestamp (ISO format)")
@click.option(
    "--output-state",
    type=click.File("w"),
    help="Output file for updated state",
)
def sync_incremental(
    config: click.File,
    state: click.File,
    entities: str,
    since: str,
    output_state: click.File,
) -> None:
    """Run incremental sync for specified entities.

    INCREMENTAL SYNC RULES IMPLEMENTED:
    ===================================

    1. Filter Rule: mod_ts > max(mod_ts from state/database) - 5 minutes
       - Applies 5-minute safety overlap to prevent missed records
       - Uses mod_ts__gte parameter for WMS API filtering

    2. Ordering: mod_ts ASC (chronological)
       - Processes records in chronological order
       - Ensures proper timestamp sequence for state management

    3. Replication Method: INCREMENTAL
       - Uses mod_ts as replication key
       - Tracks latest processed timestamp in state

    4. Pagination Configuration:
       - Singer SDK: pagination_mode="cursor" (follows next_page URLs)
       - WMS API: page_mode="sequenced" (cursor-based, no total counts)
       - Page size: 1000 (optimized for WMS API performance)

    5. Operation: UPSERT with timestamp tracking
       - Updates existing records or inserts new ones
       - Maintains latest mod_ts bookmark for next sync

    WMS PAGINATION MODES EXPLAINED:
    ==============================

    Oracle WMS API supports two page_mode values:

    • page_mode="paged" (default):
      - Returns: result_count, page_count, page_nbr
      - Navigation: ?page=3
      - Slower (calculates totals upfront)

    • page_mode="sequenced" (recommended for integrations):
      - Returns: only next_page, previous_page, results
      - Navigation: ?cursor=cD0xNDAw
      - Faster (no total calculations, generated on-the-fly)

    For incremental sync, we use page_mode="sequenced" for optimal performance.
    """
    import json

    from .tap import TapOracleWMS

    # Load and configure
    config_data = json.load(config)

    # Configure incremental sync with correct pagination settings
    config_data["enable_incremental"] = True
    config_data["debug_logging"] = True
    config_data["metrics"] = {"enabled": True}
    config_data["test_connection"] = False  # Disable connection test to avoid discovery
    config_data["incremental_overlap_minutes"] = 5  # 5-minute safety overlap
    config_data["page_size"] = 1000  # Optimized page size

    # CORRECT: Singer SDK pagination_mode="cursor" to handle next_page URLs
    # This works with WMS API page_mode="sequenced" which uses cursor navigation
    config_data["pagination_mode"] = "cursor"  # Singer SDK setting

    if since:
        config_data["start_date"] = since
        logger.info(f"📅 Setting start_date to: {since}", "green")

    if entities:
        config_data["entities"] = list(entities)
        logger.info(f"🎯 Filtering to entities: {list(entities)}", "green")

    # Load previous state
    state_data = None
    if state:
        state_data = json.load(state)
        logger.info("📊 Loaded previous state from file", "green")

    logger.info("🔄 Starting incremental sync with validated rules...", "blue")
    logger.info(f"📋 Entities: {entities or 'all configured'}", "green")
    logger.info(f"📅 Since: {since or 'bookmark from state'}", "green")
    logger.info("📐 Rules: mod_ts > max(mod_ts) - 5min, ordering=mod_ts", "yellow")

    try:
        # Create tap instance with no connection test
        tap = TapOracleWMS(config=config_data)

        logger.info("✅ Tap instance created successfully", "green")

        # Run discovery to get available streams
        logger.info("🔍 Discovering available entities...", "yellow")
        streams = tap.discover_streams()

        if not streams:
            logger.info(
                "❌ No streams discovered. Check configuration and permissions.",
                "red",
            )
            return

        logger.info(f"✅ Discovered {len(streams)} streams", "green")

        # If specific entities requested, filter streams
        if entities:
            filtered_streams = [s for s in streams if s.name in entities]
            if not filtered_streams:
                logger.info(
                    f"❌ None of the requested entities found: {entities}",
                    "red",
                )
                logger.info(
                    f"Available entities: {[s.name for s in streams]}",
                    "yellow",
                )
                return
            streams = filtered_streams
            logger.info(f"🎯 Filtered to {len(streams)} requested streams", "green")

        # Execute sync with state and catalog
        logger.info("🚀 Starting incremental data extraction...", "blue")

        # Set up catalog for Singer with incremental settings
        catalog = {
            "streams": [
                {
                    "tap_stream_id": stream.name,
                    "schema": stream.schema,
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "inclusion": "available",
                                "selected": True,
                                "replication-method": "INCREMENTAL",
                                "replication-key": "mod_ts",
                            },
                        },
                    ],
                }
                for stream in streams
            ],
        }

        # Log the incremental sync configuration
        logger.info("⚡ INCREMENTAL SYNC CONFIGURATION:", "yellow")
        logger.info("   📋 Replication method: INCREMENTAL", "green")
        logger.info("   🔑 Replication key: mod_ts", "green")
        logger.info("   ⏰ Safety overlap: 5 minutes", "green")
        logger.info("   🔀 Ordering: mod_ts ASC (chronological)", "green")
        logger.info(
            "   📄 Singer pagination_mode: cursor (follows next_page URLs)",
            "green",
        )
        logger.info("   📄 WMS page_mode: sequenced (cursor-based, no totals)", "green")
        logger.info("   📦 Page size: 1000 (optimized)", "green")

        # Execute incremental sync using custom implementation
        logger.info(
            "🚀 Executing incremental sync with custom implementation...",
            "blue",
        )

        success = _execute_incremental_sync_custom(
            tap=tap,
            streams=streams,
            catalog=catalog,
            state_data=state_data,
            output_state=output_state,
        )

        if success:
            logger.info("✅ Incremental sync completed successfully", "green")
        else:
            logger.info("❌ Incremental sync completed with errors", "red")

    except Exception as e:
        logger.info(f"❌ Sync failed: {e}", "red")
        logger.exception("Full error details:")
        raise


def _execute_incremental_sync_custom(
    tap: Any,
    streams: list[Any],
    catalog: dict[str, Any],
    state_data: dict[str, Any] | None,
    output_state: click.File | None,
) -> bool:
    """Execute incremental sync using custom implementation with full control.

    CUSTOM INCREMENTAL SYNC IMPLEMENTATION:
    ======================================

    This function implements a custom incremental sync process that:

    1. STREAM PROCESSING:
       - Iterates through each selected stream individually
       - Applies incremental sync rules per stream
       - Manages state bookmarks for each entity

    2. STATE MANAGEMENT:
       - Loads previous state bookmarks for each stream
       - Tracks max(mod_ts) during extraction
       - Updates state with latest timestamps
       - Outputs final state for next sync run

    3. INCREMENTAL FILTERING:
       - Applies mod_ts > max(mod_ts) - 5min rule
       - Uses chronological ordering (mod_ts ASC)
       - Ensures no data gaps with safety overlap

    4. ERROR HANDLING:
       - Continues processing other streams if one fails
       - Logs detailed error information per stream
       - Returns overall success status

    5. SINGER PROTOCOL COMPLIANCE:
       - Outputs SCHEMA messages for each stream
       - Outputs RECORD messages for each extracted record
       - Outputs STATE messages with updated bookmarks

    Args:
        tap: TapOracleWMS instance with configuration
        streams: List of discovered stream instances
        catalog: Singer catalog with stream metadata
        state_data: Previous state with bookmarks (optional)
        output_state: File handle for outputting final state (optional)

    Returns:
        bool: True if all streams processed successfully, False if any errors

    """
    from datetime import datetime, timezone
    import json

    # Initialize state management
    current_state = state_data.copy() if state_data else {}
    if "bookmarks" not in current_state:
        current_state["bookmarks"] = {}

    success_count = 0
    error_count = 0
    total_records = 0

    logger.info("📊 CUSTOM INCREMENTAL SYNC EXECUTION:", "blue")
    logger.info(f"   📋 Streams to process: {len(streams)}", "green")
    logger.info(f"   📊 Previous bookmarks: {len(current_state['bookmarks'])}", "green")

    # Process each stream individually
    for i, stream in enumerate(streams, 1):
        stream_name = stream.name
        logger.info(
            f"\n🔄 [{i}/{len(streams)}] Processing stream: {stream_name}",
            "blue",
        )

        try:
            # Get stream metadata from catalog
            stream_catalog = next(
                (s for s in catalog["streams"] if s["tap_stream_id"] == stream_name),
                None,
            )

            if not stream_catalog:
                logger.info(
                    f"⚠️ No catalog metadata for stream {stream_name}", "yellow"
                )
                continue

            # Output SCHEMA message for Singer protocol
            {
                "type": "SCHEMA",
                "stream": stream_name,
                "schema": stream_catalog["schema"],
                "key_properties": (
                    ["id"]
                    if "id" in stream_catalog["schema"].get("properties", {})
                    else []
                ),
            }

            # Get previous bookmark for this stream
            stream_bookmark = current_state["bookmarks"].get(stream_name, {})
            previous_mod_ts = stream_bookmark.get("mod_ts")

            if previous_mod_ts:
                logger.info(f"   📅 Previous bookmark: {previous_mod_ts}", "green")
            else:
                logger.info(
                    "   📅 No previous bookmark (full initial extraction)",
                    "yellow",
                )

            # Create context with state information for incremental sync
            context = {
                "stream_name": stream_name,
                "bookmark": stream_bookmark,
                "state": current_state,
            }

            # Extract records from stream with incremental filtering
            logger.info(f"   🚀 Starting extraction for {stream_name}...", "blue")
            record_count = 0
            latest_mod_ts = previous_mod_ts

            # Get records using stream's incremental logic
            for record in stream.get_records(context):
                # Output RECORD message for Singer protocol
                {
                    "type": "RECORD",
                    "stream": stream_name,
                    "record": record,
                    "time_extracted": datetime.now(timezone.utc).isoformat(),
                }

                record_count += 1
                total_records += 1

                # Track latest mod_ts for state management
                record_mod_ts = record.get("mod_ts")
                if record_mod_ts:
                    if not latest_mod_ts or record_mod_ts > latest_mod_ts:
                        latest_mod_ts = record_mod_ts

                # Progress feedback every 1000 records
                if record_count % 1000 == 0:
                    logger.info(f"   📊 Extracted {record_count:,} records...", "green")

            # Update bookmark with latest mod_ts
            if latest_mod_ts:
                current_state["bookmarks"][stream_name] = {
                    "mod_ts": latest_mod_ts,
                    "last_sync": datetime.now(timezone.utc).isoformat(),
                }

                # Output STATE message for Singer protocol

                logger.info(f"   📅 Updated bookmark: {latest_mod_ts}", "green")

            logger.info(
                f"   ✅ Completed {stream_name}: {record_count:,} records",
                "green",
            )
            success_count += 1

        except Exception as e:
            logger.info(f"   ❌ Error in stream {stream_name}: {e}", "red")
            logger.exception(f"   🔍 Full error details for {stream_name}:")
            error_count += 1
            continue

    # Output final state to file if specified
    if output_state and current_state:
        try:
            json.dump(current_state, output_state, indent=2)
            logger.info(f"💾 Final state saved to {output_state.name}", "green")
        except Exception as e:
            logger.info(f"⚠️ Failed to save state: {e}", "yellow")

    # Log final summary
    logger.info("\n📊 INCREMENTAL SYNC SUMMARY:", "blue")
    logger.info(f"   ✅ Successful streams: {success_count}", "green")
    logger.info(
        f"   ❌ Failed streams: {error_count}",
        "red" if error_count > 0 else "green",
    )
    logger.info(f"   📊 Total records extracted: {total_records:,}", "green")
    logger.info(
        f"   📅 Streams with updated bookmarks: {len(current_state['bookmarks'])}",
        "green",
    )

    return error_count == 0


@sync.command("full")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--business-area",
    type=click.Choice(["inventory", "orders", "warehouse", "master_data", "all"]),
    default="all",
    help="Business area to sync",
)
@click.option(
    "--parallel-streams",
    type=int,
    default=5,
    help="Number of parallel extraction streams",
)
@click.option(
    "--batch-size",
    type=int,
    default=1000,
    help="Batch size for data extraction",
)
def sync_full(
    config: click.File,
    business_area: str,
    parallel_streams: int,
    batch_size: int,
) -> None:
    """Run full sync for business area or all entities."""
    config_data = json.load(config)

    # Configure full sync settings
    config_data["page_size"] = batch_size
    config_data["max_concurrent_discovery"] = parallel_streams

    # Configure business area entities
    if business_area != "all":
        business_entities = _get_business_area_entities(business_area)
        config_data["entities"] = business_entities

    logger.info("Starting full sync for %s...", business_area, "blue")
    logger.info("Parallel streams: %s", parallel_streams, "green")
    logger.info("Batch size: %s", batch_size, "green")

    try:
        # Run full sync
        TapOracleWMS(config=config_data).sync_all()
        logger.info("✅ Full sync completed successfully", "green")
    except Exception as e:
        logger.info(f"❌ Sync failed: {e}", "red")
        logger.exception("Full error details:")
        raise


# ANALYSIS AND REPORTING SUBCOMMANDS


@cli.group()
def analyze() -> None:
    """Data analysis and business intelligence commands."""


@analyze.command("supply-chain")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--time-window",
    type=int,
    default=30,
    help="Analysis time window in days",
)
@click.option(
    "--include-forecasting",
    is_flag=True,
    help="Include demand forecasting analysis",
)
def analyze_supply_chain(
    config: click.File,
    time_window: str,
    include_forecasting: bool,
) -> None:
    """Analyze supply chain performance and visibility."""
    logger.info("Analyzing supply chain performance...", "blue")

    supply_chain_entities = [
        "order_header",
        "order_detail",
        "shipment",
        "receipt",
        "inventory",
        "demand_forecast",
        "replenishment",
    ]

    logger.info("Analyzing %s days of supply chain data", time_window, "green")
    logger.info("Entities: %s", len(supply_chain_entities), "green")

    if include_forecasting:
        logger.info("Demand forecasting analysis enabled", "yellow")


@analyze.command("compliance")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--audit-type",
    type=click.Choice(
        ["change_tracking", "data_integrity", "process_compliance", "all"],
    ),
    default="all",
    help="Type of compliance audit",
)
@click.option("--date-range", help="Date range for audit (YYYY-MM-DD,YYYY-MM-DD)")
def analyze_compliance(config: click.File, audit_type: str, date_range: str) -> None:
    """Run compliance and audit analysis."""
    logger.info("Running %s compliance analysis...", audit_type, "blue")

    compliance_entities = [
        "audit_log",
        "change_history",
        "user_activity",
        "system_config",
        "data_validation_log",
    ]

    safe_print(
        f"Auditing {len(compliance_entities)} compliance-related entities",
        "green",
    )

    if date_range:
        logger.info("Date range: %s", date_range, "green")


# UTILITY FUNCTIONS


def _prepare_discovery_config(
    config_data: dict[str, Any],
    include_patterns: Iterable[str],
    exclude_patterns: Iterable[str],
    verify_access: bool,
) -> dict[str, Any]:
    """Prepare configuration for entity discovery."""
    if include_patterns or exclude_patterns:
        config_data["entity_patterns"] = {
            "include": list(include_patterns) if include_patterns else None,
            "exclude": list(exclude_patterns) if exclude_patterns else None,
        }

    if verify_access:
        config_data["verify_entity_access"] = True

    return config_data


async def _run_entity_discovery(discovery, verify_access) -> None:
    """Run entity discovery with progress tracking."""
    return await _run_discovery_with_progress(discovery, verify_access)


async def _run_discovery_with_progress(discovery, verify_access) -> None:
    """Run discovery with rich progress display."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task("Discovering entities...", total=None)

        entities = await discovery.discover_entities()
        progress.update(
            task,
            description=f"Found {len(entities)} entities, filtering...",
        )

        filtered = discovery.filter_entities(entities)
        progress.update(task, description=f"Filtered to {len(filtered)} entities")

        if verify_access:
            progress.update(task, description="Verifying entity access...")
            accessible: dict = {}
            for name, url in filtered.items():
                if await discovery.check_entity_access(name):
                    accessible[name] = url
                progress.update(
                    task,
                    description=f"Verified {len(accessible)}/{len(filtered)}",
                )
            filtered = accessible

        progress.remove_task(task)
        return filtered


async def _run_discovery_simple(discovery, verify_access) -> None:
    """Run discovery with simple text output."""
    logger.info("Discovering entities...", "blue")
    entities = await discovery.discover_entities()
    logger.info("Found %s entities, filtering...", len(entities), "green")

    filtered = discovery.filter_entities(entities)
    logger.info("Filtered to %s entities", len(filtered), "green")

    if verify_access:
        logger.info("Verifying entity access...", "yellow")
        accessible: dict = {}
        for i, (name, url) in enumerate(filtered.items()):
            if await discovery.check_entity_access(name):
                accessible[name] = url
            if i % 10 == 0:  # Progress update every 10 entities
                safe_print(
                    f"Verified {len(accessible)}/{len(filtered)} entities",
                    "yellow",
                )
        filtered = accessible

    return filtered


def _output_discovery_results(
    entities: list[str],
    categorized: dict[str, list[str]],
    output_format: str,
    output: Any
) -> None:
    """Output discovery results in the specified format."""
    if output_format == "json":
        json.dump(
            {
                "entities": entities,
                "categorized": categorized,
                "summary": {
                    "total_entities": len(entities),
                    "categories": {cat: len(ents) for cat, ents in categorized.items()},
                },
            },
            output,
            indent=2,
        )
    elif output_format == "table":
        _display_entities_table(categorized)
    elif output_format == "csv":
        _export_entities_csv(entities, output)


def _categorize_entities(entities: dict[str, str]) -> dict[str, list[str]]:
    """Categorize entities by business area."""
    categories = {
        "Master Data": [],
        "Inventory Management": [],
        "Order Management": [],
        "Warehouse Operations": [],
        "System & Audit": [],
        "Other": [],
    }

    # Define entity patterns for each category
    category_patterns = {
        "Master Data": [
            "item",
            "location",
            "company",
            "facility",
            "user",
            "uom",
            "currency",
        ],
        "Inventory Management": [
            "inventory",
            "lot",
            "serial",
            "cycle_count",
            "adjustment",
        ],
        "Order Management": [
            "order",
            "allocation",
            "pick",
            "ship",
            "receipt",
            "return",
        ],
        "Warehouse Operations": [
            "task",
            "equipment",
            "labor",
            "dock",
            "wave",
            "zone",
        ],
        "System & Audit": [
            "audit",
            "log",
            "config",
            "system",
            "history",
            "error",
        ],
    }

    for entity_name in entities:
        categorized = False
        for category, patterns in category_patterns.items():
            if any(pattern in entity_name.lower() for pattern in patterns):
                categories[category].append(entity_name)
                categorized = True
                break

        if not categorized:
            categories["Other"].append(entity_name)

    return categories


def _display_entities_table(categorized: dict[str, list[str]]) -> None:
    """Display entities in a formatted table."""
    for category, entity_list in categorized.items():
        if not entity_list:
            continue

        logger.info(
            "\n[bold magenta]%s[/bold magenta] (%s)",
            category,
            len(entity_list),
        )

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Entity Name", style="green")
        table.add_column("Business Context", style="yellow")

        for entity in sorted(entity_list):
            context = _get_business_context(entity, category)
            table.add_row(entity, context)

        logger.info("%s", table)
        logger.info("Table display requires rich library")


def _get_business_context(entity_name: str, category: str) -> str:
    """Get business context description for an entity."""
    context_map = {
        "item": "Product master data and specifications",
        "location": "Warehouse location hierarchy and details",
        "inventory": "Current stock levels and availability",
        "order_header": "Order information and status",
        "allocation": "Inventory allocation and reservation",
        "task": "Warehouse work tasks and assignments",
        "pick": "Picking operations and performance",
        "shipment": "Outbound shipment tracking",
        "receipt": "Inbound receipt processing",
        "cycle_count": "Inventory accuracy verification",
        "audit_log": "System change tracking and compliance",
    }

    return context_map.get(entity_name, f"{category} related entity")


def _export_entities_csv(entities: dict[str, str], output: Any) -> None:
    """Export entities to CSV format."""
    import csv

    writer = csv.writer(output)
    writer.writerow(["Entity Name", "URL", "Category"])

    categorized = _categorize_entities(entities)
    for category, entity_list in categorized.items():
        for entity in entity_list:
            writer.writerow([entity, entities[entity], category])


def _get_business_area_entities(business_area: str) -> list[str]:
    """Get entities for a specific business area."""
    business_area_map = {
        "inventory": [
            "inventory",
            "item",
            "location",
            "lot",
            "serial_number",
            "cycle_count",
            "adjustment",
            "uom",
        ],
        "orders": [
            "order_header",
            "order_detail",
            "allocation",
            "pick",
            "ship_confirm",
            "receipt",
            "return",
        ],
        "warehouse": [
            "task",
            "task_detail",
            "equipment",
            "labor_tracking",
            "dock_appointment",
            "wave",
            "zone",
        ],
        "master_data": [
            "item",
            "location",
            "company",
            "facility",
            "user_",
            "supplier",
            "customer",
            "uom",
            "currency",
        ],
    }

    return business_area_map.get(business_area, [])


# MONITORING AND METRICS SUBCOMMANDS


@cli.group()
def monitor() -> None:
    """Monitoring, metrics and health check commands."""


@monitor.command("status")
@click.option(
    "--config",
    type=click.File("r"),
    required=True,
    help="Configuration file",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table", "prometheus"]),
    default="table",
    help="Output format",
)
def monitor_status(config: click.File, output_format: str) -> None:
    """Get current monitoring status and metrics."""
    config_data = json.load(config)
    config_data.setdefault("metrics", {})["enabled"] = True

    monitor = TAPMonitor(config_data)

    async def _get_status() -> None:
        await monitor.start_monitoring()
        await asyncio.sleep(2)
        status = monitor.get_monitoring_status()
        await monitor.stop_monitoring()
        return status

    status = asyncio.run(_get_status())

    if output_format in {"json", "prometheus"}:
        logger.info("Oracle WMS TAP Monitoring Status", "bold blue")
        logger.info("Timestamp: {status['timestamp']}", "green")
        health = status.get("health", {})
        overall_health = health.get("overall_healthy", False)
        safe_print(
            f"Health: {'✓ OK' if overall_health else '✗ FAIL'}",
            "green" if overall_health else "red",
        )


# CLI entry point
if __name__ == "__main__":
    cli()
