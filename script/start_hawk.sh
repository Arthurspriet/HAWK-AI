#!/usr/bin/env bash

# HAWK-AI Complete System Startup Script
# This script starts all HAWK-AI services:
#   1. Vector Database (ensure it exists)
#   2. HAWK-AI API Server (port 8000)
#   3. HAWK-AI Dev Backend (main.py --dev)
#   4. Open WebUI Backend (port 8080)
#   5. Open WebUI Frontend (port 5173)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HAWK_AI_DIR="$(dirname "$SCRIPT_DIR")"
OPEN_WEBUI_DIR="$HAWK_AI_DIR/open-webui"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting HAWK-AI Complete System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if vector database exists
echo "Checking vector database..."
if [ ! -d "$HAWK_AI_DIR/data/vector_index" ] || [ -z "$(ls -A $HAWK_AI_DIR/data/vector_index)" ]; then
    echo -e "${YELLOW}⚠️  Vector database not found. Please run 'make db' first.${NC}"
else
    echo -e "${GREEN}✓${NC} Vector database exists"
fi

# Check if Open WebUI directory exists
if [ ! -d "$OPEN_WEBUI_DIR" ]; then
    echo -e "${YELLOW}⚠️  Open WebUI directory not found at $OPEN_WEBUI_DIR${NC}"
    echo "   Continuing without Open WebUI..."
    SKIP_WEBUI=true
else
    SKIP_WEBUI=false
fi

# 1. Start HAWK-AI API Server
echo ""
echo "Starting HAWK-AI API Server..."
if lsof -i :8000 2>/dev/null | grep -q LISTEN; then
    echo -e "${GREEN}✓${NC} HAWK-AI API already running on port 8000"
else
    cd "$HAWK_AI_DIR"
    . .venv/bin/activate
    nohup python api_server.py --reload > logs/api_server.log 2>&1 &
    echo $! > /tmp/hawk_ai_api.pid
    sleep 2
    echo -e "${GREEN}✓${NC} HAWK-AI API started (PID: $(cat /tmp/hawk_ai_api.pid))"
fi

# 2. Start HAWK-AI Dev Backend
echo ""
echo "Starting HAWK-AI Dev Backend..."
if lsof -i :8001 2>/dev/null | grep -q LISTEN; then
    echo -e "${GREEN}✓${NC} HAWK-AI Dev Backend already running on port 8001"
else
    cd "$HAWK_AI_DIR"
    . .venv/bin/activate
    nohup python main.py --dev > logs/main_dev.log 2>&1 &
    echo $! > /tmp/hawk_ai_dev.pid
    sleep 2
    echo -e "${GREEN}✓${NC} HAWK-AI Dev Backend started (PID: $(cat /tmp/hawk_ai_dev.pid))"
fi

if [ "$SKIP_WEBUI" = false ]; then
    # 3. Start Open WebUI Backend
    echo ""
    echo "Starting Open WebUI Backend..."
    if lsof -i :8080 2>/dev/null | grep -q LISTEN; then
        echo -e "${GREEN}✓${NC} Open WebUI Backend already running on port 8080"
    else
        cd "$OPEN_WEBUI_DIR/backend"
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}⚠️  Open WebUI backend venv not found. Creating...${NC}"
            python3 -m venv venv
            . venv/bin/activate
            pip install -r requirements.txt
        else
            . venv/bin/activate
        fi
        export CORS_ALLOW_ORIGIN="http://localhost:5173;http://localhost:8080"
        nohup uvicorn open_webui.main:app --port 8080 --host 0.0.0.0 --forwarded-allow-ips '*' > backend.log 2>&1 &
        echo $! > /tmp/openwebui_backend.pid
        sleep 3
        echo -e "${GREEN}✓${NC} Open WebUI Backend started (PID: $(cat /tmp/openwebui_backend.pid))"
    fi

    # 4. Start Open WebUI Frontend
    echo ""
    echo "Starting Open WebUI Frontend..."
    if lsof -i :5173 2>/dev/null | grep -q LISTEN; then
        echo -e "${GREEN}✓${NC} Open WebUI Frontend already running on port 5173"
    else
        cd "$OPEN_WEBUI_DIR"
        if [ ! -d "node_modules" ]; then
            echo -e "${YELLOW}⚠️  node_modules not found. Running npm install...${NC}"
            npm install
        fi
        nohup npm run dev > frontend.log 2>&1 &
        echo $! > /tmp/openwebui_frontend.pid
        sleep 5
        echo -e "${GREEN}✓${NC} Open WebUI Frontend started (PID: $(cat /tmp/openwebui_frontend.pid))"
    fi
fi

# Display summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ All HAWK-AI services are running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}Services:${NC}"
echo "  🔧 HAWK-AI API:        http://127.0.0.1:8000/docs"
echo "  🛠️  HAWK-AI Dev:        Running in background"
if [ "$SKIP_WEBUI" = false ]; then
    echo "  📊 OpenWebUI Backend:  http://127.0.0.1:8080/docs"
    echo "  🌐 OpenWebUI Frontend: http://localhost:5173"
fi
echo ""
echo -e "${BLUE}Logs:${NC}"
echo "  - HAWK-AI API:        $HAWK_AI_DIR/logs/api_server.log"
echo "  - HAWK-AI Dev:        $HAWK_AI_DIR/logs/main_dev.log"
if [ "$SKIP_WEBUI" = false ]; then
    echo "  - OpenWebUI Backend:  $OPEN_WEBUI_DIR/backend/backend.log"
    echo "  - OpenWebUI Frontend: $OPEN_WEBUI_DIR/frontend.log"
fi
echo ""
echo -e "${BLUE}Management:${NC}"
echo "  - Stop all services:  make stop"
echo "  - View logs:          tail -f logs/*.log"
echo ""

