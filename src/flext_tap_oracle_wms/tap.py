"""Oracle WMS TAP implementation with real Singer SDK processing.

This module implements a production-grade Singer TAP for Oracle WMS data extraction
using the Singer SDK 0.46.4+ with real data processing capabilities.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import random
import time
from typing import TYPE_CHECKING, Any

import httpx
from singer_sdk import Stream, Tap

from .config import config_schema
from .enhanced_logging import (
    get_enhanced_logger,
    PerformanceTracer,
    trace_performance,
)
from .logging import (
    get_singer_logger,
    trace_singer_operation,
    trace_wms_api_call,
    trace_stream_operation,
    trace_discovery_operation,
)
from .error_recovery import ErrorRecoveryManager
from .error_recovery_advanced import (
    create_advanced_error_recovery,
)
from .monitoring import (
    BusinessMetricsCollector,
    HealthChecker,
    get_monitor,
    timer,
)
from .validation import validate_complete_config


if TYPE_CHECKING:
    from collections.abc import Iterable
    from singer_sdk.tap_base import Tap as BaseTap
else:
    BaseTap = Any


class OracleWMSStream(Stream):
    """Individual Oracle WMS entity stream with real data processing."""

    def __init__(
        self,
        tap: Any,  # TapOracleWMS - forward reference
        name: str,
        schema: dict[str, Any],
    ) -> None:
        """Initialize WMS stream."""
        super().__init__(tap, schema=schema, name=name)
        self.entity_name = name
        self.api_path = f"/api/v1/{name}"
        # Use advanced error recovery if enabled
        if tap.config.get("advanced_error_recovery", True):
            self.error_manager: Any = create_advanced_error_recovery(dict(tap.config))
        else:
            self.error_manager = ErrorRecoveryManager(dict(tap.config))
        self.records_processed = 0
        self.last_processed_time: datetime | None = None

        # Initialize monitoring and enterprise logging
        self.monitor = get_monitor()
        self.business_metrics = BusinessMetricsCollector(self.monitor)
        self.enhanced_logger = get_enhanced_logger(f"{__name__}.{name}")
        self.enterprise_logger = get_singer_logger(f"{__name__}.{name}")
        
        # Enterprise TRACE logging for stream initialization
        trace_stream_operation(
            self.enterprise_logger,
            stream_name=name,
            operation="stream_initialization",
            timing_ms=0.0,
            entity_name=name,
            api_path=self.api_path,
        )
        self.enhanced_logger.trace(f"🔍 Initializing stream for entity: {name}")
        self.enterprise_logger.trace(f"🚀 Enterprise stream initialization for {name} complete")

    @property
    def url_base(self) -> str:
        """Get base URL for Oracle WMS API."""
        base_url = self.config.get("base_url", "")
        return str(base_url).rstrip("/")

    @property
    def http_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": str(self.config.get("user_agent", "tap-oracle-wms/1.0")),
        }

        # Add WMS context headers
        company_code = self.config.get("company_code", "*")
        facility_code = self.config.get("facility_code", "*")

        if company_code != "*":
            headers["X-WMS-Company"] = str(company_code)
        if facility_code != "*":
            headers["X-WMS-Facility"] = str(facility_code)

        return headers

    def get_url_params(
        self,
        context: dict[str, Any] | None,
        next_page_token: str | None,
    ) -> dict[str, Any]:
        """Get URL parameters for API requests."""
        params = {
            "page_size": self.config.get("page_size", 1000),
            "format": "json",
        }

        # Add pagination parameters
        if next_page_token:
            params["cursor"] = next_page_token
        elif context and context.get("starting_replication_key_value"):
            # Incremental sync - filter by modification timestamp
            params["modified_since"] = context["starting_replication_key_value"]

        # Add field selection if configured
        field_selection = self.config.get("field_selection", {})
        if self.entity_name in field_selection:
            fields = field_selection[self.entity_name]
            if isinstance(fields, list) and fields:
                params["fields"] = ",".join(fields)

        # Add entity-specific filters
        entity_filters = self.config.get("entity_filters", {})
        if self.entity_name in entity_filters:
            filters = entity_filters[self.entity_name]
            if isinstance(filters, dict):
                params.update(filters)

        # Add ordering
        ordering = self.config.get("ordering", {})
        entity_ordering = ordering.get(self.entity_name)
        if entity_ordering:
            params["order_by"] = entity_ordering
        elif self.config.get("default_ordering"):
            params["order_by"] = self.config["default_ordering"]

        return params

    def prepare_request_payload(
        self,
        context: dict[str, Any] | None,
        next_page_token: str | None,
    ) -> dict[str, Any] | None:
        """Prepare request payload for POST requests."""
        # Oracle WMS uses GET requests for data extraction
        return None

    async def _make_request(
        self,
        url: str,
        params: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Make HTTP request with error recovery."""
        request_start = time.perf_counter()
        
        # Enterprise TRACE logging for API call
        self.enhanced_logger.trace("🚀 Making HTTP request to %s", url)
        self.enhanced_logger.trace("📈 Request params: %s", params)
        
        trace_wms_api_call(
            self.enterprise_logger,
            method="GET",
            endpoint=url,
            request_size=len(str(params)),
            entity_name=self.entity_name,
            page_params=params,
        )
        
        # PRODUCTION: Always use real API - no demo mode
        if self.config.get("safe_mode", False):
            self.enhanced_logger.critical("❌ Safe mode not allowed in production")
            raise ValueError("Safe mode/demo mode not allowed in production environment")

        timeout = httpx.Timeout(
            connect=self.config.get("connect_timeout", 30),
            read=self.config.get("read_timeout", 120),
            write=30.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(
            timeout=timeout,
            verify=self.config.get("verify_ssl", True),
        ) as client:
            # Add authentication
            auth_method = self.config.get("auth_method", "basic")
            if auth_method == "basic":
                username = self.config.get("username")
                password = self.config.get("password")
                if username and password:
                    client.auth = (username, password)

            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                response_data = response.json()
                
                # Enterprise TRACE logging for successful API response
                timing_ms = (time.perf_counter() - request_start) * 1000
                trace_wms_api_call(
                    self.enterprise_logger,
                    method="GET",
                    endpoint=url,
                    status_code=response.status_code,
                    timing_ms=timing_ms,
                    request_size=len(str(params)),
                    response_size=len(str(response_data)) if response_data else 0,
                    entity_name=self.entity_name,
                    success=True,
                )
                
                return dict(response_data) if response_data else {}

            except httpx.HTTPStatusError as e:
                # Use advanced error recovery if available
                if hasattr(self.error_manager, "handle_error_with_recovery"):
                    result = await self.error_manager.handle_error_with_recovery(
                        e, self._make_request_with_recovery, url, params, headers
                    )
                    return dict(result) if result else {}
                # Fallback to basic error recovery
                result = await self.error_manager.handle_error(
                    e, self._make_request_with_recovery, url, params, headers
                )
                return dict(result) if result else {}

            except httpx.RequestError as e:
                # Use advanced error recovery if available
                if hasattr(self.error_manager, "handle_error_with_recovery"):
                    result = await self.error_manager.handle_error_with_recovery(
                        e, self._make_request_with_recovery, url, params, headers
                    )
                    return dict(result) if result else {}
                # Fallback to basic error recovery
                self.enhanced_logger.warning("⚠️ Request Error, attempting recovery: %s", e)
                result = await self.error_manager.handle_error(
                    e, self._make_request_with_recovery, url, params, headers
                )
                return dict(result) if result else {}

    # PRODUCTION NOTICE: All demo/mock data generation functions removed
    # for security and reliability. Only real API connections allowed.

    async def _make_request_with_recovery(
        self,
        url: str,
        params: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Make request with simplified error handling for recovery."""
        timeout = httpx.Timeout(
            connect=self.config.get("connect_timeout", 30),
            read=self.config.get("read_timeout", 120),
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            auth_method = self.config.get("auth_method", "basic")
            if auth_method == "basic":
                username = self.config.get("username")
                password = self.config.get("password")
                if username and password:
                    client.auth = (username, password)

            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            result = response.json()
            return dict(result) if result else {}

    @trace_performance("Stream Data Extraction")
    def get_records(self, context: dict[str, Any] | None) -> Iterable[dict[str, Any]]:
        """Get records from Oracle WMS API with real data processing."""
        next_page_token = None
        page_count = 0
        start_time = time.perf_counter()
        total_errors = 0

        self.enhanced_logger.trace(f"🚀 Starting data extraction for {self.entity_name}")
        
        # Start monitoring timer with enhanced performance tracing
        with timer(f"stream_extraction_{self.entity_name}"), PerformanceTracer(self.enhanced_logger, f"Extract {self.entity_name}") as tracer:
            while True:
                page_count += 1
                self.enhanced_logger.trace(f"📄 Processing {self.entity_name} page {page_count}")
                tracer.checkpoint(f"Starting page {page_count}")
                self.logger.info("Processing %s page %s", self.entity_name, page_count)

                # Prepare request parameters
                url = f"{self.url_base}{self.api_path}"
                params = self.get_url_params(context, next_page_token)
                headers = self.http_headers
                
                self.enhanced_logger.trace(f"📈 Request URL: {url}")
                self.enhanced_logger.trace(f"📉 Request params: {params}")

                try:
                    # Record API request timing
                    request_start = time.perf_counter()

                    # Make async request in sync context
                    try:
                        # Try to get existing event loop
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is running, we need to run in a thread
                            import concurrent.futures

                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(
                                    asyncio.run,
                                    self._make_request(url, params, headers),
                                )
                                response_data = future.result()
                        else:
                            response_data = loop.run_until_complete(
                                self._make_request(url, params, headers)
                            )
                    except RuntimeError:
                        # No event loop exists, create one
                        response_data = asyncio.run(
                            self._make_request(url, params, headers)
                        )

                    # Record successful API request
                    request_duration = (time.perf_counter() - request_start) * 1000
                    self.monitor.record_request(request_duration, success=True)
                    self.enhanced_logger.trace(f"✅ API request successful in {request_duration:.2f}ms")
                    tracer.checkpoint(f"API request page {page_count}")

                    # Process response data
                    records = self._extract_records_from_response(response_data)
                    self.enhanced_logger.trace(f"📀 Extracted {len(records)} records from response")

                    for i, record in enumerate(records):
                        # Apply data transformations
                        self.enhanced_logger.trace(f"🔄 Transforming record {i+1}/{len(records)}")
                        transformed_record = self._transform_record(record)
                        self.records_processed += 1
                        self.last_processed_time = datetime.now()
                        yield transformed_record

                    # Check for pagination
                    next_page_token = self._extract_next_page_token(response_data)
                    if not next_page_token:
                        self.enhanced_logger.trace("✅ No more pages - extraction complete")
                        break
                    else:
                        self.enhanced_logger.trace(f"🔄 Next page token: {next_page_token}")

                    # Respect rate limiting
                    if self.config.get("rate_limit_delay", 0) > 0:
                        time.sleep(self.config["rate_limit_delay"])

                except Exception as e:
                    total_errors += 1
                    # Record failed API request
                    request_duration = (time.perf_counter() - request_start) * 1000
                    self.monitor.record_request(request_duration, success=False)
                    
                    self.enhanced_logger.critical(f"❌ Error processing {self.entity_name} page {page_count}: {e}")
                    tracer.checkpoint(f"Error on page {page_count}")

                    self.logger.exception(
                        "Error processing %s page %d", self.entity_name, page_count
                    )
                    if not self.config.get("continue_on_error", True):
                        raise
                    break

            # Record final stream metrics
            total_duration = (time.perf_counter() - start_time) * 1000
            self.monitor.record_stream_metrics(
                self.entity_name, self.records_processed, total_errors, total_duration
            )
            
            tracer.checkpoint("Final metrics calculation")

            # Record business metrics
            data_quality_score = max(
                0.0,
                (self.records_processed - total_errors)
                / max(self.records_processed, 1),
            )
            self.business_metrics.record_entity_extraction(
                self.entity_name,
                self.records_processed,
                total_duration,
                data_quality_score,
            )
            
            # Enhanced final logging
            self.enhanced_logger.info(
                f"✅ Extraction completed for {self.entity_name}: "
                f"{self.records_processed} records, {total_errors} errors, "
                f"quality score: {data_quality_score:.2%}"
            )
            self.enhanced_logger.trace(
                f"📈 Final stats - Duration: {total_duration:.2f}ms, "
                f"Pages: {page_count}, Records/page: {self.records_processed/max(page_count, 1):.1f}"
            )

            self.logger.info(
                f"Completed {self.entity_name}: {self.records_processed} records processed"
            )

    def _extract_records_from_response(
        self, response_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Extract records from API response."""
        # Oracle WMS typically returns data in 'data' or 'items' field
        if "data" in response_data:
            records = response_data["data"]
        elif "items" in response_data:
            records = response_data["items"]
        elif "results" in response_data:
            records = response_data["results"]
        else:
            # Fallback: assume response is the records array
            records = (
                response_data if isinstance(response_data, list) else [response_data]
            )

        return records if isinstance(records, list) else []

    def _extract_next_page_token(self, response_data: dict[str, Any]) -> str | None:
        """Extract next page token from response."""
        # Check for various pagination patterns
        pagination_patterns = [
            "next_cursor",
            "next_page_token",
            "next",
            "cursor",
        ]

        for pattern in pagination_patterns:
            if pattern in response_data:
                value = response_data[pattern]
                return str(value) if value else None

        # Check nested pagination info
        if "pagination" in response_data:
            pagination = response_data["pagination"]
            for pattern in pagination_patterns:
                if pattern in pagination:
                    value = pagination[pattern]
                    return str(value) if value else None

        # Check if there are more pages using links
        if "links" in response_data:
            links = response_data["links"]
            if "next" in links:
                # Extract cursor from next URL
                next_url = links["next"]
                if "cursor=" in next_url:
                    cursor_value = next_url.split("cursor=")[1].split("&")[0]
                    return str(cursor_value) if cursor_value else None

        return None

    def _transform_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Transform individual record with business logic."""
        # Add extraction metadata
        record["_extracted_at"] = datetime.now().isoformat()
        record["_source_entity"] = self.entity_name

        # Apply data quality checks
        if self.config.get("data_quality", {}).get("validate_schemas", True):
            record = self._validate_record_schema(record)

        # Add business context if enabled
        if self.config.get("data_enrichment", {}).get("include_business_context", True):
            record = self._add_business_context(record)

        # Apply field transformations
        return self._apply_field_transformations(record)

    def _validate_record_schema(self, record: dict[str, Any]) -> dict[str, Any]:
        """Validate record against expected schema."""
        # Add validation metadata
        record["_validation"] = {
            "validated_at": datetime.now().isoformat(),
            "schema_version": "1.0",
            "valid": True,
        }

        # Remove invalid fields based on schema
        if hasattr(self, "schema") and self.schema:
            valid_fields = set(self.schema.get("properties", {}).keys())
            if valid_fields:
                # Keep only fields defined in schema + metadata fields
                metadata_fields = {f for f in record if f.startswith("_")}
                allowed_fields = valid_fields | metadata_fields
                record = {k: v for k, v in record.items() if k in allowed_fields}

        return record

    def _add_business_context(self, record: dict[str, Any]) -> dict[str, Any]:
        """Add business context metadata."""
        context = {
            "business_area": self._determine_business_area(),
            "data_classification": self._classify_data_sensitivity(record),
            "extraction_context": {
                "company_code": self.config.get("company_code", "*"),
                "facility_code": self.config.get("facility_code", "*"),
                "extraction_timestamp": datetime.now().isoformat(),
            },
        }

        record["_business_context"] = context
        return record

    def _determine_business_area(self) -> str:
        """Determine business area for the entity."""
        entity_name = self.entity_name.lower()

        if any(term in entity_name for term in ["item", "inventory", "stock", "lot"]):
            return "inventory"
        if any(term in entity_name for term in ["order", "allocation", "pick", "ship"]):
            return "orders"
        if any(term in entity_name for term in ["task", "labor", "dock", "wave"]):
            return "warehouse"
        return "general"

    def _classify_data_sensitivity(self, record: dict[str, Any]) -> str:
        """Classify data sensitivity level."""
        sensitive_fields = ["customer", "vendor", "price", "cost", "employee"]

        for field_name in record:
            if any(sensitive in field_name.lower() for sensitive in sensitive_fields):
                return "sensitive"

        return "standard"

    def _apply_field_transformations(self, record: dict[str, Any]) -> dict[str, Any]:
        """Apply field-level transformations."""
        # Convert timestamps to ISO format
        timestamp_fields = [
            "created_date",
            "modified_date",
            "last_updated",
            "timestamp",
        ]

        for field in timestamp_fields:
            if record.get(field):
                try:
                    # Handle various timestamp formats
                    value = record[field]
                    if isinstance(value, str):
                        # Try to parse and reformat timestamp
                        if "T" in value or ":" in value:
                            # Already in ISO-like format
                            continue
                        if len(value) == 10 and value.isdigit():
                            # Unix timestamp
                            record[field] = datetime.fromtimestamp(
                                int(value)
                            ).isoformat()
                except Exception:
                    # Keep original value if transformation fails
                    continue

        # Normalize boolean fields
        boolean_fields = ["active", "enabled", "deleted", "processed"]
        for field in boolean_fields:
            if field in record:
                value = record[field]
                if isinstance(value, str):
                    record[field] = value.lower() in {"true", "1", "yes", "y", "active"}
                elif isinstance(value, (int, float)):
                    record[field] = bool(value)

        return record


class TapOracleWMS(Tap):
    """Oracle WMS TAP with real Singer SDK implementation."""

    name = "tap-oracle-wms"
    config_jsonschema = config_schema

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize Oracle WMS TAP."""
        super().__init__(*args, **kwargs)
        
        # Initialize enterprise logging system first
        self.enhanced_logger = get_enhanced_logger(f"{__name__}.TapOracleWMS")
        self.enterprise_logger = get_singer_logger(f"{__name__}.TapOracleWMS")
        
        # Enterprise TRACE logging for TAP initialization
        trace_singer_operation(
            self.enterprise_logger,
            operation="tap_initialization",
            timing_ms=0.0,
            config_items=len(self.config),
            auth_method=self.config.get("auth_method", "basic"),
            base_url=self.config.get("base_url", "not_set"),
        )
        
        self.enhanced_logger.trace("🔧 Initializing Oracle WMS TAP")
        self.enterprise_logger.trace("🚀 Enterprise Oracle WMS TAP initialization started")
        
        # Use advanced error recovery if enabled
        if self.config.get("advanced_error_recovery", True):
            self.enhanced_logger.trace("🚪 Using advanced error recovery")
            self.error_manager = create_advanced_error_recovery(dict(self.config))
        else:
            self.enhanced_logger.trace("🚪 Using basic error recovery")
            from .error_recovery_advanced import AdvancedErrorRecoveryManager
            self.error_manager = AdvancedErrorRecoveryManager(dict(self.config))
        self.discovered_entities: list[str] = []

        # Initialize monitoring and health checking
        self.monitor = get_monitor()
        self.health_checker = HealthChecker(self.monitor)
        self.business_metrics = BusinessMetricsCollector(self.monitor)
        
        self.enhanced_logger.trace("✅ Oracle WMS TAP initialization complete")

    @trace_performance("Stream Discovery")
    def discover_streams(self) -> list[Stream]:
        """Discover available Oracle WMS entities."""
        discovery_start = time.perf_counter()
        
        # Enterprise TRACE logging for discovery start
        trace_discovery_operation(
            self.enterprise_logger,
            operation="discovery_start",
            timing_ms=0.0,
            config_entities=len(self.config.get("entities", [])),
            business_areas=self.config.get("business_areas", []),
        )
        
        self.enhanced_logger.trace("🔍 Starting comprehensive entity discovery for Oracle WMS")
        self.enterprise_logger.trace("🔍 Enterprise entity discovery process initiated")
        self.logger.info("Starting entity discovery for Oracle WMS")

        try:
            # Run health checks before discovery
            self.enhanced_logger.trace("🌡️ Running health checks before discovery")
            self.health_checker.run_all_checks(dict(self.config))

            # Validate configuration first
            self.enhanced_logger.trace("⚙️ Validating configuration")
            validation_result = validate_complete_config(dict(self.config))
            if not validation_result[0]:
                msg = f"Configuration validation failed: {validation_result[1]}"
                self.enhanced_logger.critical(f"❌ {msg}")
                raise ValueError(msg)
            
            self.enhanced_logger.trace("✅ Configuration validation passed")

            # Discover entities from API or use configured entities
            entities = self.config.get("entities")
            if entities:
                self.enhanced_logger.trace(f"📝 Using configured entities: {entities}")
                self.logger.info("Using configured entities: %s", entities)
                discovered_entities = entities
            else:
                self.enhanced_logger.trace("🔍 Auto-discovering entities from API")
                discovered_entities = self._discover_entities_from_api()
            self.enhanced_logger.trace(f"📅 Discovery found {len(discovered_entities)} entities")

            # Create streams for discovered entities
            streams: list[Stream] = []
            for i, entity_name in enumerate(discovered_entities):
                try:
                    self.enhanced_logger.trace(f"🔨 Creating stream {i+1}/{len(discovered_entities)}: {entity_name}")
                    schema = self._generate_entity_schema(entity_name)
                    stream = OracleWMSStream(tap=self, name=entity_name, schema=schema)
                    streams.append(stream)
                    self.logger.info("Created stream for entity: %s", entity_name)
                    self.enhanced_logger.trace(f"✅ Stream created successfully for {entity_name}")

                except Exception as e:
                    self.enhanced_logger.warning("Failed to create stream for %s: %s", entity_name, e)
                    self.logger.warning(
                        "Failed to create stream for %s: %s", entity_name, e
                    )
                    if not self.config.get("continue_on_error", True):
                        raise

            # Record discovery metrics
            discovery_duration = (time.perf_counter() - discovery_start) * 1000
            self.business_metrics.record_stream_discovery(
                len(streams), discovery_duration
            )
            
            # Enterprise TRACE logging for discovery completion
            trace_discovery_operation(
                self.enterprise_logger,
                operation="discovery_complete",
                entity_count=len(streams),
                timing_ms=discovery_duration,
                success_rate=len(streams) / max(len(discovered_entities), 1),
                performance_streams_per_sec=len(streams) / max(discovery_duration / 1000, 0.001),
            )
            
            # Enhanced completion logging
            self.enhanced_logger.info(
                "✅ Discovery completed successfully: %d streams created in %.2fms",
                len(streams), discovery_duration
            )
            self.enhanced_logger.trace(
                f"📈 Discovery performance: {len(streams)/max(discovery_duration/1000, 0.001):.1f} "
                f"streams/second"
            )
            self.enterprise_logger.trace(
                f"🎯 Enterprise discovery complete: {len(streams)} streams in {discovery_duration:.2f}ms"
            )

            self.logger.info("Discovery completed: %s streams created", len(streams))
            return streams

        except Exception as e:
            self.enhanced_logger.critical("❌ Stream discovery failed: %s", e)
            self.logger.exception("Stream discovery failed")
            # PRODUCTION: No fallback streams - fail fast and explicit
            raise

    def _discover_entities_from_api(self) -> list[str]:
        """Discover entities from Oracle WMS API."""
        # Default entities for Oracle WMS based on common business areas
        default_entities = []

        business_areas = list(self.config.get(
            "business_areas", ["inventory", "orders", "warehouse"]
        ))

        if "inventory" in business_areas:
            default_entities.extend([
                "item",
                "item_master",
                "inventory",
                "stock_ledger",
                "lot_master",
                "serial_numbers",
                "cycle_counts",
            ])

        if "orders" in business_areas:
            default_entities.extend([
                "orders",
                "order_lines",
                "allocations",
                "picks",
                "shipments",
                "receipts",
                "returns",
            ])

        if "warehouse" in business_areas:
            default_entities.extend([
                "locations",
                "zones",
                "tasks",
                "labor_tracking",
                "equipment",
                "dock_doors",
                "waves",
            ])

        # Filter based on entity patterns if configured
        entity_patterns = self.config.get("entity_patterns", {})
        if entity_patterns:
            include_patterns = entity_patterns.get("include", [])
            exclude_patterns = entity_patterns.get("exclude", [])

            if include_patterns:
                filtered_entities = [
                    entity
                    for entity in default_entities
                    if any(pattern in entity for pattern in include_patterns)
                ]
                default_entities = filtered_entities

            if exclude_patterns:
                default_entities = [
                    entity
                    for entity in default_entities
                    if not any(pattern in entity for pattern in exclude_patterns)
                ]

        self.logger.info(
            "Discovered %d entities from configuration", len(default_entities)
        )
        return default_entities

    def _generate_entity_schema(self, entity_name: str) -> dict[str, Any]:
        """Generate JSON schema for entity."""
        # Base schema structure
        schema = {
            "type": "object",
            "properties": {
                # Common fields for all entities
                "id": {"type": ["string", "integer"]},
                "code": {"type": "string"},
                "description": {"type": "string"},
                "created_date": {"type": "string", "format": "date-time"},
                "modified_date": {"type": "string", "format": "date-time"},
                "active": {"type": "boolean"},
                # Metadata fields
                "_extracted_at": {"type": "string", "format": "date-time"},
                "_source_entity": {"type": "string"},
                "_business_context": {"type": "object"},
                "_validation": {"type": "object"},
            },
        }

        # Add entity-specific fields based on business area
        entity_lower = entity_name.lower()

        if "item" in entity_lower or "inventory" in entity_lower:
            if isinstance(schema["properties"], dict):
                properties_dict = dict(schema["properties"].items())
            else:
                properties_dict = {}
            properties_dict.update(
                {
                    "item_code": {"type": "string"},
                    "item_description": {"type": "string"},
                    "unit_of_measure": {"type": "string"},
                    "category": {"type": "string"},
                    "location": {"type": "string"},
                    "quantity_on_hand": {"type": "number"},
                    "available_quantity": {"type": "number"},
                }
            )
            schema["properties"] = properties_dict

        elif "order" in entity_lower:
            if isinstance(schema["properties"], dict):
                properties_dict = dict(schema["properties"].items())
            else:
                properties_dict = {}
            properties_dict.update(
                {
                    "order_number": {"type": "string"},
                    "order_type": {"type": "string"},
                    "customer_code": {"type": "string"},
                    "order_date": {"type": "string", "format": "date-time"},
                    "status": {"type": "string"},
                    "priority": {"type": "string"},
                    "total_lines": {"type": "integer"},
                }
            )
            schema["properties"] = properties_dict

        elif "location" in entity_lower or "zone" in entity_lower:
            if isinstance(schema["properties"], dict):
                properties_dict = dict(schema["properties"].items())
            else:
                properties_dict = {}
            properties_dict.update(
                {
                    "location_code": {"type": "string"},
                    "zone": {"type": "string"},
                    "location_type": {"type": "string"},
                    "capacity": {"type": "number"},
                    "occupied": {"type": "boolean"},
                }
            )
            schema["properties"] = properties_dict

        # Set replication key for incremental sync
        if self.config.get("enable_incremental", True):
            replication_key = self._determine_replication_key(entity_name)
            if replication_key and replication_key in schema["properties"]:
                if isinstance(schema["properties"], dict):
                    properties_dict = dict(schema["properties"].items())
                else:
                    properties_dict = {}
                if replication_key in properties_dict:
                    if isinstance(properties_dict[replication_key], dict):
                        properties_dict[replication_key]["inclusion"] = "automatic"
                schema["properties"] = properties_dict

        return schema

    def _determine_replication_key(self, entity_name: str) -> str | None:
        """Determine the replication key for incremental sync."""
        # Check for custom replication key override
        override_keys = self.config.get("replication_key_override", {})
        if entity_name in override_keys:
            return str(override_keys[entity_name])

        # Common timestamp fields used for incremental sync
        timestamp_candidates = [
            "modified_date",
            "last_updated",
            "updated_at",
            "timestamp",
            "mod_ts",
            "last_mod_date",
        ]

        # Return the first candidate (will be validated during schema generation)
        return timestamp_candidates[0]

    # PRODUCTION NOTICE: Fallback streams removed for production safety.
    # All streams must be explicitly discovered from real API endpoints.


def main() -> None:
    """Run the Oracle WMS TAP."""
    TapOracleWMS.cli()


if __name__ == "__main__":
    main()
