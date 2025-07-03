#!/usr/bin/env python3
"""Mock Oracle WMS Server for real testing."""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class MockWMSHandler(BaseHTTPRequestHandler):
    """Handle Oracle WMS API requests."""

    def do_GET(self):  # noqa: N802
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        print(f"[MOCK WMS] {self.command} {path}")
        print(f"[MOCK WMS] Query: {query_params}")
        print(f"[MOCK WMS] Headers: {dict(self.headers)}")

        # Check authentication
        auth_header = self.headers.get("Authorization")
        if not auth_header:
            self._send_error(401, "Authentication required")
            return

        # Route requests
        if path == "/wms/lgfapi/v10/entity/":
            self._handle_entity_discovery()
        elif path.startswith("/wms/lgfapi/v10/entity/") and path.endswith("/describe/"):
            entity_name = path.split("/")[-2]
            self._handle_entity_describe(entity_name)
        elif path.startswith("/wms/lgfapi/v10/entity/"):
            entity_name = path.split("/")[-1]
            self._handle_entity_data(entity_name, query_params)
        else:
            self._send_error(404, f"Endpoint not found: {path}")

    def _handle_entity_discovery(self):
        """Return list of available entities."""
        entities = [
            "item",
            "location",
            "inventory",
            "order_header",
            "order_detail",
            "allocation",
            "pick",
            "shipment",
        ]

        self._send_json_response(200, entities)

    def _handle_entity_describe(self, entity_name):
        """Return entity metadata."""
        if entity_name == "item":
            metadata = {
                "parameters": ["id", "item_code", "description", "mod_ts", "create_ts"],
                "fields": {
                    "id": {"type": "integer", "required": True},
                    "item_code": {"type": "string", "max_length": 50, "required": True},
                    "description": {"type": "string", "max_length": 200, "required": False},
                    "mod_ts": {"type": "datetime", "required": False},
                    "create_ts": {"type": "datetime", "required": False},
                },
            }
        elif entity_name == "location":
            metadata = {
                "parameters": ["id", "location_code", "zone", "mod_ts"],
                "fields": {
                    "id": {"type": "integer", "required": True},
                    "location_code": {"type": "string", "max_length": 20, "required": True},
                    "zone": {"type": "string", "max_length": 10, "required": False},
                    "mod_ts": {"type": "datetime", "required": False},
                },
            }
        else:
            metadata = {
                "parameters": ["id", "code", "mod_ts"],
                "fields": {
                    "id": {"type": "integer", "required": True},
                    "code": {"type": "string", "required": True},
                    "mod_ts": {"type": "datetime", "required": False},
                },
            }

        self._send_json_response(200, metadata)

    def _handle_entity_data(self, entity_name, query_params):
        """Return entity data with pagination."""
        page_size = int(query_params.get("page_size", [100])[0])
        _page_mode = query_params.get("page_mode", ["sequenced"])[0]  # Parameter for future use
        cursor = query_params.get("cursor", [None])[0]

        # Simulate different entities
        if entity_name == "item":
            data = self._generate_item_data(page_size, cursor)
        elif entity_name == "location":
            data = self._generate_location_data(page_size, cursor)
        elif entity_name == "inventory":
            data = self._generate_inventory_data(page_size, cursor)
        else:
            data = self._generate_generic_data(entity_name, page_size, cursor)

        self._send_json_response(200, data)

    def _generate_item_data(self, page_size, cursor):
        """Generate mock item data."""
        start_id = int(cursor) if cursor else 1

        items = []
        for i in range(page_size):
            item_id = start_id + i
            items.append({
                "id": item_id,
                "item_code": f"ITEM{item_id:06d}",
                "description": f"Test Item {item_id}",
                "mod_ts": "2024-01-01T10:00:00Z",
                "create_ts": "2024-01-01T09:00:00Z",
            })

        # Add pagination info
        next_cursor = start_id + page_size if page_size == len(items) else None

        return {
            "results": items,
            "page_nbr": 1,
            "page_count": 10,
            "result_count": len(items),
            "next_page": f"http://localhost:8888/wms/lgfapi/v10/entity/item?cursor={next_cursor}" if next_cursor else None,
        }

    def _generate_location_data(self, page_size, cursor):
        """Generate mock location data."""
        start_id = int(cursor) if cursor else 1

        locations = []
        zones = ["A", "B", "C", "PICK", "PACK"]

        for i in range(page_size):
            loc_id = start_id + i
            locations.append({
                "id": loc_id,
                "location_code": f"LOC{loc_id:04d}",
                "zone": zones[loc_id % len(zones)],
                "mod_ts": "2024-01-01T10:00:00Z",
            })

        return {
            "results": locations,
            "page_nbr": 1,
            "result_count": len(locations),
        }

    def _generate_inventory_data(self, page_size, cursor):
        """Generate mock inventory data."""
        start_id = int(cursor) if cursor else 1

        inventory = []
        for i in range(page_size):
            inv_id = start_id + i
            inventory.append({
                "id": inv_id,
                "item_id": (inv_id % 100) + 1,
                "location_id": (inv_id % 50) + 1,
                "quantity": inv_id * 10,
                "mod_ts": "2024-01-01T11:00:00Z",
            })

        return {
            "results": inventory,
            "result_count": len(inventory),
        }

    def _generate_generic_data(self, entity_name, page_size, cursor):
        """Generate generic mock data."""
        start_id = int(cursor) if cursor else 1

        records = []
        for i in range(page_size):
            record_id = start_id + i
            records.append({
                "id": record_id,
                "code": f"{entity_name.upper()}{record_id:06d}",
                "mod_ts": "2024-01-01T10:00:00Z",
            })

        return {
            "results": records,
            "result_count": len(records),
        }

    def _send_json_response(self, status_code, data):
        """Send JSON response."""
        response_data = json.dumps(data, indent=2)

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(response_data.encode("utf-8"))

        print(f"[MOCK WMS] Response {status_code}: {len(response_data)} bytes")

    def _send_error(self, status_code, message):
        """Send error response."""
        error_data = {"error": message, "status": status_code}
        self._send_json_response(status_code, error_data)

    def log_message(self, format, *args):
        """Override to reduce noise."""


def start_mock_server(port=8888):
    """Start the mock WMS server."""
    server = HTTPServer(("localhost", port), MockWMSHandler)

    def run_server():
        print(f"[MOCK WMS] Starting mock Oracle WMS server on http://localhost:{port}")
        print(f"[MOCK WMS] Entity discovery: http://localhost:{port}/wms/lgfapi/v10/entity/")
        server.serve_forever()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    # Give server time to start
    time.sleep(0.5)
    return server


if __name__ == "__main__":
    server = start_mock_server()
    try:
        print("Mock WMS server running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down mock server...")
        server.shutdown()
        server.server_close()
