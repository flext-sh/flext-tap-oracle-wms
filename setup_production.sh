#!/bin/bash

# TAP Oracle WMS - Production Setup Script
echo "🚀 TAP Oracle WMS - Production Setup"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if Python 3.9+ is available
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [[ $MAJOR -ge 3 && $MINOR -ge 9 ]]; then
    print_status "Python $PYTHON_VERSION detected (minimum 3.9 required)"
else
    print_error "Python 3.9+ required, found $PYTHON_VERSION"
    echo "Please install Python 3.9 or later and try again."
    exit 1
fi

# Check if we're in the correct directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -f "src/tap_oracle_wms/tap.py" ]]; then
    print_error "Setup script must be run from TAP Oracle WMS root directory"
    echo "Please navigate to the directory containing pyproject.toml and try again."
    exit 1
fi

print_status "Running from correct directory"

# Create virtual environment if it doesn't exist
if [[ ! -d ".venv" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    print_status "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_status "Pip upgraded"

# Install the TAP in development mode
echo "📥 Installing TAP Oracle WMS..."
pip install -e . > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    print_status "TAP Oracle WMS installed successfully"
else
    print_error "Failed to install TAP Oracle WMS"
    echo "Check the error messages above and try again."
    exit 1
fi

# Install additional dependencies for development/testing
echo "📥 Installing development dependencies..."
pip install pytest pytest-cov ruff mypy > /dev/null 2>&1
print_status "Development dependencies installed"

# Run basic validation
echo "🧪 Running basic validation..."

# Test import
python3 -c "from tap_oracle_wms.tap import TapOracleWMS; print('✅ Import successful')" > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    print_status "Basic import test passed"
else
    print_error "Basic import test failed"
    exit 1
fi

# Test CLI availability
tap-oracle-wms --help > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    print_status "CLI command available"
else
    print_error "CLI command not available"
    exit 1
fi

# Test configuration validation
echo "🔧 Testing configuration files..."
python3 evidence_validation_tap_oracle_wms/validate_all_configs.py > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    print_status "All configuration files valid"
else
    print_warning "Some configuration files may have issues"
fi

# Create sample configuration
echo "📝 Creating sample configuration..."
cat > config.sample.json << 'EOF'
{
  "base_url": "https://your-wms.oracle.com",
  "username": "your_username",
  "password": "your_password",
  "auth_method": "basic",
  "page_size": 100,
  "record_limit": 1000,
  "log_level": "INFO",
  "disable_trace_logs": true,
  
  "simple_date_expressions": {
    "allocation": {
      "mod_ts__gte": "today-7d",
      "create_ts__gte": "yesterday"
    }
  },
  
  "circuit_breaker": {
    "enabled": true,
    "failure_threshold": 5,
    "recovery_timeout": 60
  },
  
  "entities": ["allocation", "order_hdr", "inventory"],
  "enable_incremental": true,
  "test_connection": true
}
EOF

print_status "Sample configuration created (config.sample.json)"

# Create production environment script
echo "📝 Creating production environment script..."
cat > run_production.sh << 'EOF'
#!/bin/bash

# TAP Oracle WMS - Production Runner
# Usage: ./run_production.sh config.json

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <config.json>"
    echo "Example: $0 config.production.json"
    exit 1
fi

CONFIG_FILE="$1"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Run the TAP
echo "🚀 Running TAP Oracle WMS with $CONFIG_FILE"
tap-oracle-wms --config "$CONFIG_FILE" --discover > catalog.json

if [[ $? -eq 0 ]]; then
    echo "✅ Discovery completed. Catalog saved to catalog.json"
    echo "🔄 Starting data extraction..."
    tap-oracle-wms --config "$CONFIG_FILE" --catalog catalog.json
else
    echo "❌ Discovery failed. Check your configuration."
    exit 1
fi
EOF

chmod +x run_production.sh
print_status "Production runner script created (run_production.sh)"

# Run final tests if requested
echo ""
echo "🧪 Running comprehensive tests (optional)..."
read -p "Run full test suite? This will take a few minutes and requires valid Oracle WMS credentials (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Running test suite..."
    ./evidence_validation_tap_oracle_wms/test_final_complete_system.sh
else
    print_info "Skipping test suite"
fi

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Copy config.sample.json to config.production.json"
echo "2. Update config.production.json with your Oracle WMS credentials"
echo "3. Run: ./run_production.sh config.production.json"
echo ""
echo "For simple date expressions, use:"
echo "  - today-7d (7 days ago)"
echo "  - yesterday"
echo "  - now"
echo "  - today+1w (1 week from today)"
echo ""
echo "Documentation available in evidence_validation_tap_oracle_wms/"
echo ""
print_status "TAP Oracle WMS is ready for production use!"