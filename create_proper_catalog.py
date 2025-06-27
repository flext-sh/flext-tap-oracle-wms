#!/usr/bin/env python3
"""Create a proper catalog for data extraction testing."""

import json


# Create a properly configured catalog for FULL_TABLE replication
catalog = {
    "streams": [
        {
            "tap_stream_id": "allocation",
            "replication_method": "FULL_TABLE",  # Change to FULL_TABLE to avoid replication key issues
            "key_properties": ["id"],
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "alloc_qty": {"type": "number"},
                    "status_id": {"type": "string"},
                    "create_ts": {"type": ["string", "null"], "format": "date-time"},
                    "mod_ts": {"type": ["string", "null"], "format": "date-time"},
                    "from_inventory_id": {"type": "string"},
                    "order_dtl_id": {"type": "string"},
                },
                "required": [
                    "id",
                    "alloc_qty",
                    "status_id",
                    "from_inventory_id",
                    "order_dtl_id",
                ],
            },
            "metadata": [
                {
                    "breadcrumb": [],
                    "metadata": {
                        "inclusion": "available",
                        "selected": True,
                        "table-key-properties": ["id"],
                    },
                },
            ],
        },
    ],
}

# Save catalog
with open("catalog_full_table.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2)
