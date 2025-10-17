#!/bin/bash
# HAWK-AI + Open WebUI Integration Test Script
# This script helps verify the integration is working correctly

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 HAWK-AI Integration Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if HAWK-AI backend is running
echo "Test 1: Checking HAWK-AI backend..."
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ HAWK-AI backend is running${NC}"
else
    echo -e "${RED}❌ HAWK-AI backend is NOT running${NC}"
    echo "   Start it with: cd /home/arthurspriet/HAWK-AI && python3 api_server.py"
    exit 1
fi

# Test 2: Check if /chat endpoint responds
echo ""
echo "Test 2: Testing /chat endpoint..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Test message"}')

if echo "$RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✅ /chat endpoint is working${NC}"
    echo "   Response preview: $(echo $RESPONSE | jq -r '.response' 2>/dev/null | head -c 50)..."
else
    echo -e "${RED}❌ /chat endpoint failed${NC}"
    echo "   Response: $RESPONSE"
    exit 1
fi

# Test 3: Check if frontend integration file exists
echo ""
echo "Test 3: Checking frontend integration..."
HAWKAI_FILE="/home/arthurspriet/HAWK-AI/open-webui/src/lib/apis/hawkai/index.ts"
if [ -f "$HAWKAI_FILE" ]; then
    echo -e "${GREEN}✅ HAWK-AI API module exists${NC}"
else
    echo -e "${RED}❌ HAWK-AI API module NOT found${NC}"
    echo "   Expected at: $HAWKAI_FILE"
    exit 1
fi

# Test 4: Check if Chat.svelte uses hawkai import
echo ""
echo "Test 4: Verifying Chat.svelte integration..."
CHAT_FILE="/home/arthurspriet/HAWK-AI/open-webui/src/lib/components/chat/Chat.svelte"
if grep -q "from '\$lib/apis/hawkai'" "$CHAT_FILE"; then
    echo -e "${GREEN}✅ Chat.svelte correctly imports from hawkai${NC}"
else
    echo -e "${RED}❌ Chat.svelte still imports from openai${NC}"
    echo "   File: $CHAT_FILE"
    echo "   Expected: import { generateOpenAIChatCompletion } from '\$lib/apis/hawkai';"
    exit 1
fi

# Test 5: Check CORS settings
echo ""
echo "Test 5: Checking CORS configuration..."
API_SERVER="/home/arthurspriet/HAWK-AI/api_server.py"
if grep -q "localhost:8080" "$API_SERVER"; then
    echo -e "${GREEN}✅ CORS settings include Open WebUI ports${NC}"
else
    echo -e "${YELLOW}⚠️  CORS settings may need updating${NC}"
    echo "   File: $API_SERVER"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Start frontend: cd /home/arthurspriet/HAWK-AI/open-webui && npm run dev"
echo "2. Open browser: http://localhost:5173"
echo "3. Send test message: 'Analyze tensions in Sudan'"
echo "4. Check browser console (F12) for [HAWK-AI] logs"
echo ""
echo "Expected console output:"
echo "  [HAWK-AI] Intercepting chat request"
echo "  [HAWK-AI] Model: supervisor"
echo "  [HAWK-AI] Query: Analyze tensions in Sudan"
echo "  [HAWK-AI] Response received from ..."
echo ""
echo "📚 Documentation:"
echo "  - Quick Start: QUICK_START_INTEGRATION.md"
echo "  - Full Details: OPENWEBUI_INTEGRATION.md"
echo "  - Summary: INTEGRATION_SUMMARY.md"
echo ""

