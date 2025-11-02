#!/bin/bash
# Quick status check and fix script for HalloweenHack

echo "🔍 HalloweenHack System Status Check"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Backend
echo -n "Backend (port 8000): "
if lsof -i :8000 | grep -q LISTEN; then
    echo -e "${GREEN}✓ Running${NC}"
    BACKEND_OK=1
else
    echo -e "${RED}✗ Not Running${NC}"
    BACKEND_OK=0
fi

# Check Frontend
echo -n "Frontend (port 8080): "
if lsof -i :8080 | grep -q LISTEN; then
    echo -e "${GREEN}✓ Running${NC}"
    FRONTEND_OK=1
else
    echo -e "${RED}✗ Not Running${NC}"
    FRONTEND_OK=0
fi

echo ""

# Health check
if [ $BACKEND_OK -eq 1 ]; then
    echo "Backend Health Check:"
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
    echo ""
fi

# URLs
echo "📍 Access URLs:"
echo "   Frontend: http://localhost:8080"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Test Page: http://localhost:8080/test"
echo ""

# Offer to fix
if [ $BACKEND_OK -eq 0 ] || [ $FRONTEND_OK -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Some services are not running${NC}"
    echo ""
    echo "To fix, run one of:"
    echo "  make start          # Start both"
    echo "  make start-backend  # Start backend only"
    echo "  make start-frontend # Start frontend only"
else
    echo -e "${GREEN}✅ All systems operational!${NC}"
fi

echo ""
