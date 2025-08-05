#!/usr/bin/env bash
#
# Run tests for FLEXT Tap Oracle WMS
#
# This script provides various options for running tests:
# - Unit tests only
# - Integration tests (requires real Oracle WMS)
# - E2E tests
# - Performance tests
# - All tests
# - Coverage report

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Load environment variables
if [ -f .env ]; then
	export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
TEST_TYPE="all"
COVERAGE=false
VERBOSE=false
MARKERS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
	case $1 in
	--unit)
		TEST_TYPE="unit"
		shift
		;;
	--integration)
		TEST_TYPE="integration"
		shift
		;;
	--e2e)
		TEST_TYPE="e2e"
		shift
		;;
	--performance)
		TEST_TYPE="performance"
		MARKERS="-m performance"
		shift
		;;
	--all)
		TEST_TYPE="all"
		shift
		;;
	--coverage)
		COVERAGE=true
		shift
		;;
	-v | --verbose)
		VERBOSE=true
		shift
		;;
	-h | --help)
		echo "Usage: $0 [OPTIONS]"
		echo ""
		echo "Options:"
		echo "  --unit          Run unit tests only"
		echo "  --integration   Run integration tests (requires real Oracle WMS)"
		echo "  --e2e           Run end-to-end tests"
		echo "  --performance   Run performance tests"
		echo "  --all           Run all tests (default)"
		echo "  --coverage      Generate coverage report"
		echo "  -v, --verbose   Verbose output"
		echo "  -h, --help      Show this help message"
		exit 0
		;;
	*)
		echo "Unknown option: $1"
		exit 1
		;;
	esac
done

# Build pytest command
PYTEST_CMD="python -m pytest"

# Add verbose flag
if [ "$VERBOSE" = true ]; then
	PYTEST_CMD="$PYTEST_CMD -v -s"
fi

# Add coverage flags
if [ "$COVERAGE" = true ]; then
	PYTEST_CMD="$PYTEST_CMD --cov=flext_tap_oracle_wms --cov-report=html --cov-report=term"
fi

# Add test directory based on type
case $TEST_TYPE in
unit)
	PYTEST_CMD="$PYTEST_CMD tests/unit/"
	echo -e "${GREEN}Running unit tests...${NC}"
	;;
integration)
	PYTEST_CMD="$PYTEST_CMD tests/integration/"
	echo -e "${GREEN}Running integration tests...${NC}"
	echo -e "${YELLOW}Note: Requires real Oracle WMS connection${NC}"
	;;
e2e)
	PYTEST_CMD="$PYTEST_CMD tests/e2e/"
	echo -e "${GREEN}Running end-to-end tests...${NC}"
	;;
performance)
	PYTEST_CMD="$PYTEST_CMD tests/performance/ $MARKERS"
	echo -e "${GREEN}Running performance tests...${NC}"
	;;
all)
	PYTEST_CMD="$PYTEST_CMD tests/"
	echo -e "${GREEN}Running all tests...${NC}"
	;;
esac

# Check environment for integration tests
if [[ $TEST_TYPE == "integration" || $TEST_TYPE == "all" ]]; then
	if [ -z "$ORACLE_WMS_BASE_URL" ]; then
		echo -e "${RED}Error: ORACLE_WMS_BASE_URL not set${NC}"
		echo "Please set Oracle WMS environment variables in .env file"
		exit 1
	fi
fi

# Run tests
echo ""
echo "Command: $PYTEST_CMD"
echo ""

$PYTEST_CMD

# Check exit code
if [ $? -eq 0 ]; then
	echo ""
	echo -e "${GREEN}✓ Tests passed successfully!${NC}"

	if [ "$COVERAGE" = true ]; then
		echo ""
		echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
	fi
else
	echo ""
	echo -e "${RED}✗ Tests failed${NC}"
	exit 1
fi
