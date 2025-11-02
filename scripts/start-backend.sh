#!/bin/bash
# Start Browser-Use API Server

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BROWSER_USE_DIR="$SCRIPT_DIR/browser-use copy"

echo "🚀 Starting Browser-Use API Server..."

cd "$BROWSER_USE_DIR" || exit 1
source .venv/bin/activate

python browser_api_server.py
