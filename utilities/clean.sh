#!/bin/bash
# Quick cleanup script for astropy-app project
# This script calls the comprehensive Python cleanup tool

# Get the script's directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧹 Running astropy-app cleanup..."

# Run the Python cleanup script from the project root
cd "$PROJECT_ROOT"
python3 utilities/clean_cache.py

echo "✅ Cleanup completed!"
