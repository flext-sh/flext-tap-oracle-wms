import sys


sys.path.append("/home/marlonsc/pyauto/client-b-poc-oic-wms/src")

from client-b_poc_oic_wms.client import Client
from client-b_poc_oic_wms.core.config import Config


# Load config
config = Config()

# Create client
client = Client(config.wms)

# Get allocation data with limit for analysis
count = 0
complex_fields_found = set()

for record in client.get_entities("allocation", limit=10, ordering="-id"):
    count += 1

    # Analyze each field for complex objects
    for field_name, field_value in record.items():
        if isinstance(field_value, dict) and field_value:
            if "url" not in field_name.lower():
                complex_fields_found.add(field_name)
        elif isinstance(field_value, list) and field_value:
            if "url" not in field_name.lower():
                complex_fields_found.add(field_name)
                if field_value:
                    pass
        elif "url" not in field_name.lower():
            pass

    if count >= 3:  # Analyze first 3 records
        break

for _field in sorted(complex_fields_found):
    pass
