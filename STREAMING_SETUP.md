# HAWK-AI Streaming Chat Setup

## Changes Made

The streaming chat support has been successfully implemented! Here's what was added:

### 1. New Files
- `core/streaming_formatter.py` - SSE formatting utilities for streaming responses

### 2. Modified Files
- `api_server.py` - Added streaming support to both `/chat` and `/v1/chat/completions` endpoints
- `agents/supervisor_agent.py` - Added progress callbacks for real-time updates
- `core/orchestrator.py` - Added `execute_task_streaming()` wrapper method

### 3. Key Features
✅ **Streaming support on both endpoints** - `/chat` and `/v1/chat/completions`
✅ **Progress updates** - See agents working in real-time (🔍 SearchAgent, 📊 AnalystAgent, 🗺️ GeoAgent)
✅ **Agent transparency** - Shows which agent contributed what
✅ **Backward compatible** - Non-streaming requests still work
✅ **OpenAI-compatible** - Uses standard SSE format

## How to Test

### Step 1: Start the API Server

```bash
cd /home/arthurspriet/HAWK-AI
python3 api_server.py
```

The server will start on `http://127.0.0.1:8000`

### Step 2: Test Streaming with Curl

**Test the `/chat` endpoint with streaming:**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze tensions in Sudan",
    "stream": true
  }'
```

**Test the OpenAI-compatible endpoint:**

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is happening in Sudan?"}],
    "model": "hawk-ai-supervisor",
    "stream": true
  }'
```

You should see:
1. Progress updates as agents start working
2. Agent completion messages
3. Agent result summaries
4. The final synthesis streaming word-by-word
5. `data: [DONE]` at the end

### Step 3: Configure Open WebUI

Open WebUI needs to send `stream: true` in its requests. Check your integration file:

**File:** `src/lib/apis/hawkai/index.ts` (in your Open WebUI directory)

Make sure the request includes:
```javascript
const response = await fetch('http://127.0.0.1:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: userMessage,
    stream: true  // ← This enables streaming!
  })
});
```

## Debugging

### Check if Streaming is Enabled

When a streaming request is received, the server will print:
```
🔄 Streaming mode enabled for query: Analyze tensions in Sudan...
```

If you don't see this message, it means `stream: true` is not being sent in the request.

### View Server Logs

The server outputs progress in real-time:
```
╭────── HAWK-AI Processing (Streaming) ──────╮
│ Task: Analyze tensions in Sudan            │
╰────────────────────────────────────────────╯
Task type: analysis
🧭 Detected intent: ['analyst']
🕵️  Running 1 agent(s) in parallel...
✓ AnalystAgent completed
🧠 Synthesizing results with LLM...
✅ Intelligence report saved
```

### Test Non-Streaming (Backward Compatible)

To verify backward compatibility works:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze tensions in Sudan",
    "stream": false
  }'
```

This should return a complete JSON response at the end (no streaming).

## Expected Streaming Output Format

When streaming works correctly, you'll see output like:

```
data: {"id":"chatcmpl-1234567890","object":"chat.completion.chunk","created":1234567890,"model":"hawk-ai-supervisor","choices":[{"index":0,"delta":{"content":"🔍 SearchAgent: Working...\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-1234567890","object":"chat.completion.chunk","created":1234567890,"model":"hawk-ai-supervisor","choices":[{"index":0,"delta":{"content":"✓ AnalystAgent: Done\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-1234567890","object":"chat.completion.chunk","created":1234567890,"model":"hawk-ai-supervisor","choices":[{"index":0,"delta":{"content":"\n**Analysis Complete**\n\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-1234567890","object":"chat.completion.chunk","created":1234567890,"model":"hawk-ai-supervisor","choices":[{"index":0,"delta":{"content":"📊 **AnalystAgent**: Historical data shows escalating pattern...\n\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-1234567890","object":"chat.completion.chunk","created":1234567890,"model":"hawk-ai-supervisor","choices":[{"index":0,"delta":{"content":"---\n\n**Synthesis**\n\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-1234567890","object":"chat.completion.chunk","created":1234567890,"model":"hawk-ai-supervisor","choices":[{"index":0,"delta":{"content":"Based on the "},"finish_reason":null}]}

data: {"id":"chatcmpl-1234567890","object":"chat.completion.chunk","created":1234567890,"model":"hawk-ai-supervisor","choices":[{"index":0,"delta":{"content":"analysis conducted by "},"finish_reason":null}]}

... (synthesis continues word by word)

data: {"id":"chatcmpl-1234567890","object":"chat.completion.chunk","created":1234567890,"model":"hawk-ai-supervisor","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

## Troubleshooting

### Problem: Nothing appears in Open WebUI

**Solution 1: Check if stream parameter is being sent**
- Look for the `🔄 Streaming mode enabled` message in server output
- If not present, Open WebUI is not sending `stream: true`

**Solution 2: Check the integration file**
- Verify `src/lib/apis/hawkai/index.ts` exists in Open WebUI
- Ensure it's sending `stream: true` in the request body

**Solution 3: Test with curl first**
- If curl streaming works but Open WebUI doesn't, the issue is in the frontend
- If curl doesn't work either, check the server logs for errors

### Problem: Streaming works in curl but not in Open WebUI

This means Open WebUI's integration file needs to be updated to handle streaming responses.

**Update the hawkai integration** (in Open WebUI directory):

```javascript
// In src/lib/apis/hawkai/index.ts

export async function generateOpenAIChatCompletion(body) {
  const response = await fetch('http://127.0.0.1:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: body.messages[body.messages.length - 1].content,
      stream: true
    })
  });

  // Return the response stream directly
  return response;
}
```

## Next Steps

1. **Start the server:** `python3 api_server.py`
2. **Test with curl** to verify streaming works
3. **Check Open WebUI integration** to ensure `stream: true` is sent
4. **Monitor server output** for the streaming indicator
5. **Test in Open WebUI** and watch for real-time updates

The implementation is complete and ready to use! 🚀

