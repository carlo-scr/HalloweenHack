#!/bin/bash
# Quick setup script for Browser-Use backend

echo "🚀 Browser-Use Backend Quick Setup"
echo ""

# Navigate to browser-use directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BROWSER_USE_DIR="$SCRIPT_DIR/browser-use copy"
cd "$BROWSER_USE_DIR" || exit 1

echo "📂 Working directory: $PWD"
echo ""

# Check if venv exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found at .venv"
    echo "Creating new virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

echo ""
echo "📦 Installing dependencies..."
pip install -q fastapi "uvicorn[standard]" > /dev/null 2>&1

echo "✅ Installing browser-use in development mode..."
pip install -q -e . > /dev/null 2>&1

echo ""
echo "🔑 Checking API key..."
if grep -q "BROWSER_USE_API_KEY=bu_" .env 2>/dev/null; then
    echo "✅ API key configured"
else
    echo "⚠️  Warning: No API key found in .env"
    echo "   Add BROWSER_USE_API_KEY to .env file"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  ./start-backend.sh"
echo ""
echo "Or manually:"
echo "  cd 'browser-use copy'"
echo "  source .venv/bin/activate"
echo "  python browser_api_server.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
