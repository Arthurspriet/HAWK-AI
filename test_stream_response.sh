#!/bin/bash
# Test script to verify HAWK-AI streaming is working

echo "Testing HAWK-AI streaming response..."
echo "======================================"
echo ""

curl -N -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "quick test"}],
    "model": "hawk-ai-supervisor",
    "stream": true
  }' 2>&1 | head -30

echo ""
echo "======================================"
echo "If you see 'data: {' lines above, streaming is working!"

