#!/usr/bin/env bash

# HAWK-AI Complete System Shutdown Script
# This script stops all HAWK-AI services gracefully

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 Stopping HAWK-AI Complete System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to stop a service by PID file and port
stop_service() {
    local SERVICE_NAME=$1
    local PID_FILE=$2
    local PORT=$3
    
    local STOPPED=false
    
    # Try to stop by PID file first
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID 2>/dev/null
            sleep 1
            # Check if still running, force kill if needed
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null
            fi
            echo -e "${GREEN}✓${NC} Stopped $SERVICE_NAME (PID: $PID)"
            STOPPED=true
        fi
        rm -f "$PID_FILE"
    fi
    
    # If not stopped, try to find and kill by port
    if [ "$STOPPED" = false ] && [ -n "$PORT" ]; then
        PID=$(lsof -ti :$PORT 2>/dev/null)
        if [ -n "$PID" ]; then
            kill $PID 2>/dev/null
            sleep 1
            # Check if still running, force kill if needed
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID 2>/dev/null
            fi
            echo -e "${GREEN}✓${NC} Stopped $SERVICE_NAME on port $PORT (PID: $PID)"
            STOPPED=true
        fi
    fi
    
    if [ "$STOPPED" = false ]; then
        echo -e "${YELLOW}⚠️${NC}  $SERVICE_NAME was not running"
    fi
}

# Stop all services
stop_service "HAWK-AI API" "/tmp/hawk_ai_api.pid" "8000"
stop_service "HAWK-AI Dev Backend" "/tmp/hawk_ai_dev.pid" "8001"
stop_service "Open WebUI Backend" "/tmp/openwebui_backend.pid" "8080"
stop_service "Open WebUI Frontend" "/tmp/openwebui_frontend.pid" "5173"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ All HAWK-AI services stopped${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

