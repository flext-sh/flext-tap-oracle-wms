#!/bin/bash
# Setup development environment for tap-oracle-wms

echo "=== Setting up tap-oracle-wms development environment ==="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
	echo "Error: pyproject.toml not found. Please run from tap-oracle-wms directory."
	exit 1
fi

# Install poetry if not available
if ! command -v poetry &>/dev/null; then
	echo "Installing Poetry..."
	curl -sSL https://install.python-poetry.org | python3 -
	export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo "Installing dependencies with Poetry..."
poetry install

# Run in poetry shell
echo "Activating poetry shell..."
poetry shell
