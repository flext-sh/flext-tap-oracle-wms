"""Date utilities for Oracle WMS TAP with simplified date expressions.

This module provides intelligent date conversion from human-friendly expressions
to Oracle WMS-compatible ISO format timestamps.

Supported expressions:
- today, yesterday, tomorrow
- today-7d, today+3d (relative days)
- today-2w, today+1w (relative weeks)
- today-3m, today+1m (relative months)
- now (current timestamp)

Oracle WMS expects ISO format: 2024-07-01T15:30:00Z or 2024-07-01T15:30:00+00:00
"""

from __future__ import annotations

import calendar
import re
from datetime import datetime, timedelta, timezone
from typing import Any


class SimpleDateConverter:
    """Converts simplified date expressions to Oracle WMS ISO format."""

    def __init__(self) -> None:
        """Initialize the date converter."""
        # Regex patterns for different date expressions
        self.patterns = {
            "now": re.compile(r"^now$", re.IGNORECASE),
            "today": re.compile(r"^today$", re.IGNORECASE),
            "yesterday": re.compile(r"^yesterday$", re.IGNORECASE),
            "tomorrow": re.compile(r"^tomorrow$", re.IGNORECASE),
            "relative_days": re.compile(r"^today([+-])(\d+)d$", re.IGNORECASE),
            "relative_weeks": re.compile(r"^today([+-])(\d+)w$", re.IGNORECASE),
            "relative_months": re.compile(r"^today([+-])(\d+)m$", re.IGNORECASE),
        }

    def convert_expression(self, expression: str) -> str:
        """Convert a simple date expression to ISO format.

        Args:
            expression: Simple date expression (e.g., 'today-7d', 'yesterday')

        Returns:
            ISO format timestamp string for Oracle WMS

        Examples:
            >>> converter = SimpleDateConverter()
            >>> converter.convert_expression("today-7d")
            '2024-06-24T00:00:00Z'  # If today is 2024-07-01
            >>> converter.convert_expression("now")
            '2024-07-01T15:30:45Z'  # Current timestamp
        """
        expression = expression.strip()
        now = datetime.now(timezone.utc)

        # Handle 'now' - current timestamp
        if self.patterns["now"].match(expression):
            return now.isoformat().replace("+00:00", "Z")

        # Handle 'today' - start of today UTC
        if self.patterns["today"].match(expression):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return today.isoformat().replace("+00:00", "Z")

        # Handle 'yesterday'
        if self.patterns["yesterday"].match(expression):
            yesterday = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            return yesterday.isoformat().replace("+00:00", "Z")

        # Handle 'tomorrow'
        if self.patterns["tomorrow"].match(expression):
            tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            return tomorrow.isoformat().replace("+00:00", "Z")

        # Handle relative days (today+3d, today-7d)
        if match := self.patterns["relative_days"].match(expression):
            operator, days_str = match.groups()
            days = int(days_str)
            if operator == "-":
                days = -days
            target_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days)
            return target_date.isoformat().replace("+00:00", "Z")

        # Handle relative weeks (today+2w, today-1w)
        if match := self.patterns["relative_weeks"].match(expression):
            operator, weeks_str = match.groups()
            weeks = int(weeks_str)
            if operator == "-":
                weeks = -weeks
            target_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(weeks=weeks)
            return target_date.isoformat().replace("+00:00", "Z")

        # Handle relative months (today+1m, today-3m)
        if match := self.patterns["relative_months"].match(expression):
            operator, months_str = match.groups()
            months = int(months_str)
            if operator == "-":
                months = -months

            # Precise month calculation using datetime operations
            base_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            target_year = base_date.year
            target_month = base_date.month + months

            # Handle month overflow/underflow
            while target_month > 12:
                target_month -= 12
                target_year += 1
            while target_month < 1:
                target_month += 12
                target_year -= 1

            try:
                target_date = base_date.replace(year=target_year, month=target_month)
            except ValueError:
                # Handle day overflow (e.g., Jan 31 + 1 month = Feb 31, which doesn't exist)
                # Fall back to last day of target month
                last_day = calendar.monthrange(target_year, target_month)[1]
                target_date = base_date.replace(year=target_year, month=target_month, day=min(base_date.day, last_day))

            return target_date.isoformat().replace("+00:00", "Z")

        # If not a recognized pattern, assume it's already in correct format
        return expression

    def process_entity_filters(self, entity_filters: dict[str, Any]) -> dict[str, Any]:
        """Process entity filters and convert simple date expressions.

        Args:
            entity_filters: Dictionary with entity filter configurations

        Returns:
            Processed filters with converted date expressions

        Examples:
            >>> converter = SimpleDateConverter()
            >>> filters = {
            ...     "allocation": {
            ...         "mod_ts__gte": "today-7d",
            ...         "id__gte": 1000
            ...     }
            ... }
            >>> converter.process_entity_filters(filters)
            {
                "allocation": {
                    "mod_ts__gte": "2024-06-24T00:00:00Z",
                    "id__gte": 1000
                }
            }
        """
        processed_filters = {}

        for entity_name, filters in entity_filters.items():
            processed_entity_filters = {}

            for filter_key, filter_value in filters.items():
                # Check if this looks like a timestamp field filter
                if isinstance(filter_value, str) and any(
                    timestamp_field in filter_key.lower()
                    for timestamp_field in ["ts", "date", "time", "created", "modified", "updated"]
                ):
                    # Convert the date expression
                    processed_entity_filters[filter_key] = self.convert_expression(filter_value)
                else:
                    # Keep non-date filters as-is
                    processed_entity_filters[filter_key] = filter_value

            processed_filters[entity_name] = processed_entity_filters

        return processed_filters

    def process_simple_date_expressions(self, simple_date_config: dict[str, Any]) -> dict[str, Any]:
        """Process simple_date_expressions configuration.

        This method takes the simple_date_expressions config and converts all
        date expressions to proper ISO format for Oracle WMS.

        Args:
            simple_date_config: Configuration from simple_date_expressions

        Returns:
            Converted entity_filters configuration
        """
        return self.process_entity_filters(simple_date_config)


# Utility functions for direct usage
def convert_simple_date(expression: str) -> str:
    """Convert a simple date expression to ISO format.

    Convenience function for one-off date conversions.

    Args:
        expression: Simple date expression

    Returns:
        ISO format timestamp string
    """
    converter = SimpleDateConverter()
    return converter.convert_expression(expression)


def process_date_filters(entity_filters: dict[str, Any]) -> dict[str, Any]:
    """Process entity filters and convert date expressions.

    Convenience function for processing filter dictionaries.

    Args:
        entity_filters: Entity filter configuration

    Returns:
        Processed filters with converted dates
    """
    converter = SimpleDateConverter()
    return converter.process_entity_filters(entity_filters)


# Examples and documentation
EXAMPLE_EXPRESSIONS = {
    "now": "Current timestamp (e.g., 2024-07-01T15:30:45Z)",
    "today": "Start of today UTC (e.g., 2024-07-01T00:00:00Z)",
    "yesterday": "Start of yesterday UTC (e.g., 2024-06-30T00:00:00Z)",
    "tomorrow": "Start of tomorrow UTC (e.g., 2024-07-02T00:00:00Z)",
    "today-7d": "7 days ago from start of today (e.g., 2024-06-24T00:00:00Z)",
    "today+3d": "3 days from start of today (e.g., 2024-07-04T00:00:00Z)",
    "today-2w": "2 weeks ago from start of today (e.g., 2024-06-17T00:00:00Z)",
    "today+1w": "1 week from start of today (e.g., 2024-07-08T00:00:00Z)",
    "today-3m": "3 months ago (approx) from start of today",
    "today+1m": "1 month from start of today (approx)",
}

EXAMPLE_USAGE = """
Example configuration using simple date expressions:

{
  "simple_date_expressions": {
    "allocation": {
      "mod_ts__gte": "today-7d",
      "mod_ts__lte": "today",
      "create_ts__gte": "yesterday"
    },
    "order_hdr": {
      "mod_ts__gte": "today-1w",
      "create_ts__lte": "now"
    }
  }
}

This will be automatically converted to:

{
  "entity_filters": {
    "allocation": {
      "mod_ts__gte": "2024-06-24T00:00:00Z",
      "mod_ts__lte": "2024-07-01T00:00:00Z",
      "create_ts__gte": "2024-06-30T00:00:00Z"
    },
    "order_hdr": {
      "mod_ts__gte": "2024-06-24T00:00:00Z",
      "create_ts__lte": "2024-07-01T15:30:45Z"
    }
  }
}
"""
