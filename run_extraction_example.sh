#!/bin/bash
# Example script to run tap-oracle-wms extraction

echo "🚀 tap-oracle-wms Extraction Example"
echo "===================================="

# Check if .env exists
if [ ! -f .env ]; then
	echo "❌ .env file not found. Please create it with WMS credentials."
	exit 1
fi

# Load environment variables
export $(cat .env | xargs)

echo "✅ Environment loaded"
echo "   - WMS URL: https://ta29.wms.ocs.oraclecloud.com/raizen_test"
echo "   - Username: $WMS_USERNAME"
echo ""

# Create a simple config for facility extraction
cat >example_config.json <<EOF
{
  "base_url": "https://ta29.wms.ocs.oraclecloud.com/raizen_test",
  "auth_method": "basic",
  "username": "$WMS_USERNAME",
  "password": "$WMS_PASSWORD",
  "company_code": "RAIZEN",
  "facility_code": "*",
  "start_date": "2025-01-01T00:00:00Z",
  "pagination_mode": "cursor",
  "page_size": 5,
  "entities": ["facility"]
}
EOF

echo "📝 Created example_config.json"
echo ""

# Run discovery
echo "🔍 Running discovery..."
poetry run tap-oracle-wms --config example_config.json --discover >example_catalog.json

if [ $? -eq 0 ]; then
	echo "✅ Discovery successful! Catalog saved to example_catalog.json"
	echo ""

	# Extract first 5 facilities
	echo "📊 Extracting facility data (first 5 records)..."
	poetry run tap-oracle-wms --config example_config.json --catalog example_catalog.json 2>/dev/null | head -20

	echo ""
	echo "✅ Extraction complete!"
	echo ""
	echo "💡 To extract all data to a file:"
	echo "   poetry run tap-oracle-wms --config example_config.json --catalog example_catalog.json > output.jsonl"
else
	echo "❌ Discovery failed. Check your credentials and connection."
fi
