#!/bin/bash

# CORREÇÃO FINAL DEFINITIVA - Fix ALL logger.exception abuse
# Este script corrige TODAS as instâncias problemáticas de logger.exception

echo "🔧 FIXING ALL logger.exception() abuse in flext-tap-oracle-wms..."

cd /home/marlonsc/flext/flext-tap-oracle-wms/src

# Count before
echo "Before: $(rg -c 'logger\.exception' . || echo 0) total logger.exception instances"

# Replace ALL logger.exception with logger.error EXCEPT for truly unexpected errors
find . -name "*.py" -exec sed -i '/Only use logger\.exception for truly unexpected errors/,+1!s/logger\.exception(/logger.error(/g' {} \;
find . -name "*.py" -exec sed -i '/Only use logger\.exception for truly unexpected errors/,+1!s/self\.logger\.exception(/self.logger.error(/g' {} \;

# Count after
echo "After: $(rg -c 'logger\.exception' . || echo 0) total logger.exception instances"

# Show remaining instances (should only be the 2 legitimate ones)
echo ""
echo "🔍 Remaining logger.exception instances (should only be 2 legitimate ones):"
rg -n "logger\.exception" . || echo "No instances found"

echo ""
echo "✅ Fix complete! Only legitimate logger.exception instances should remain."