# Open WebUI Integration with HAWK-AI

This document explains how the Open WebUI frontend has been integrated with the HAWK-AI backend.

## Overview

The integration redirects all chat messages from Open WebUI to the HAWK-AI FastAPI backend (`http://127.0.0.1:8000/chat`) instead of the default Ollama endpoints.

## What Was Changed

### 1. Created HAWK-AI API Module
- **File**: `/home/arthurspriet/hawk-ai-webchat/src/lib/apis/hawkai/index.ts`
- **Purpose**: Provides a wrapper function that mimics the OpenAI API interface but calls HAWK-AI backend
- **Key Functions**:
  - `generateOpenAIChatCompletion()`: Drop-in replacement for OpenAI's chat completion function
  - `sendHawkAIMessage()`: Direct API call to HAWK-AI backend
  - `convertHawkAIToOpenAIFormat()`: Converts HAWK-AI responses to OpenAI-compatible format
  - `checkHawkAIStatus()`: Health check for HAWK-AI backend
  - `getHawkAISystemStatus()`: Get system status and available agents

### 2. Modified Chat Component
- **File**: `/home/arthurspriet/hawk-ai-webchat/src/lib/components/chat/Chat.svelte`
- **Change**: Replaced import statement on line 64:
  ```javascript
  // Before:
  import { generateOpenAIChatCompletion } from '$lib/apis/openai';
  
  // After:
  import { generateOpenAIChatCompletion } from '$lib/apis/hawkai';
  ```
- This single change redirects all chat requests to HAWK-AI

### 3. Updated CORS Settings
- **File**: `/home/arthurspriet/HAWK-AI/api_server.py`
- **Change**: Added Open WebUI default ports to allowed origins:
  ```python
  allow_origins=[
      "http://localhost:3000",
      "http://127.0.0.1:3000",
      "http://localhost:5173",  # Vite default
      "http://127.0.0.1:5173",
      "http://localhost:8080",  # Open WebUI default
      "http://127.0.0.1:8080",
      "http://localhost:3001",  # Alternative port
      "http://127.0.0.1:3001"
  ]
  ```

## How It Works

1. **User sends message** in Open WebUI
2. **Chat.svelte** processes the message and calls `generateOpenAIChatCompletion()`
3. **HAWK-AI wrapper** intercepts the call:
   - Extracts the user's query from the OpenAI-formatted message array
   - Sends a POST request to `http://127.0.0.1:8000/chat`
   - Converts HAWK-AI's response to OpenAI-compatible format
4. **Open WebUI** displays the response normally

## Message Format Conversion

### OpenAI Format (Input)
```json
{
  "model": "supervisor",
  "messages": [
    {"role": "user", "content": "Analyze tensions in Sudan"}
  ],
  "session_id": "abc123",
  ...
}
```

### HAWK-AI Format (Backend Call)
```json
{
  "query": "Analyze tensions in Sudan",
  "session_id": "abc123"
}
```

### HAWK-AI Response
```json
{
  "response": "Analysis of current situation...",
  "status": "success",
  "duration": 2.5,
  "agents_used": ["supervisor", "analyst", "geo"],
  "session_id": "abc123",
  "timestamp": "2025-10-16T10:00:00"
}
```

### OpenAI Format (Output to UI)
```json
{
  "id": "hawk-1697454000000",
  "object": "chat.completion",
  "model": "supervisor",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Analysis of current situation..."
    },
    "finish_reason": "stop"
  }],
  "metadata": {
    "status": "success",
    "duration": 2.5,
    "agents_used": ["supervisor", "analyst", "geo"]
  }
}
```

## Testing the Integration

### Prerequisites
1. HAWK-AI backend must be running:
   ```bash
   cd /home/arthurspriet/HAWK-AI
   python3 api_server.py
   ```
   - Should start on `http://127.0.0.1:8000`
   - Verify at `http://127.0.0.1:8000/docs`

2. Open WebUI frontend must be running:
   ```bash
   cd /home/arthurspriet/hawk-ai-webchat
   npm run dev
   ```
   - Should start on `http://localhost:5173` (or similar)

### Test Steps
1. Open the frontend in your browser (e.g., `http://localhost:5173`)
2. Start a new chat
3. Send a test message: "Analyze current tensions in Sudan"
4. Check the browser console (F12) for HAWK-AI logs:
   ```
   [HAWK-AI] Intercepting chat request
   [HAWK-AI] Model: supervisor
   [HAWK-AI] Query: Analyze current tensions in Sudan
   [HAWK-AI] Response received from supervisor, analyst, geo
   [HAWK-AI] Duration: 2.5 seconds
   ```
5. Check HAWK-AI backend terminal for:
   ```
   [CHAT] Incoming (supervisor): Analyze current tensions in Sudan
   ```
6. Verify the response appears in the chat UI

### Troubleshooting

**Issue**: Connection refused or CORS errors
- **Solution**: Ensure HAWK-AI backend is running and check CORS settings in `api_server.py`

**Issue**: "No user message found in request"
- **Solution**: This usually means the message format changed. Check the `generateOpenAIChatCompletion` function in `hawkai/index.ts`

**Issue**: Response not showing in UI
- **Solution**: Check browser console for errors. Ensure the response is being converted to OpenAI format correctly

**Issue**: Backend receives request but doesn't respond
- **Solution**: Check HAWK-AI backend logs. Ensure orchestrator is initialized correctly

## Debugging

### Frontend Console Logs
All HAWK-AI integration logs are prefixed with `[HAWK-AI]`:
```javascript
console.log('[HAWK-AI] Intercepting chat request');
console.log('[HAWK-AI] Model:', body.model);
console.log('[HAWK-AI] Query:', query);
console.log('[HAWK-AI] Response received from', agents);
console.error('[HAWK-AI] Error:', error);
```

### Backend Logs
HAWK-AI backend logs include:
- Startup messages: `🚀 Starting HAWK-AI API Server...`
- Request logs: `[CHAT] Incoming (model): query`
- Error logs: Stack traces with details

## Benefits of This Approach

1. **Minimal Changes**: Only one import statement changed in the frontend
2. **Backward Compatible**: Can easily switch back to OpenAI/Ollama by changing the import
3. **No UI Changes**: All existing Open WebUI features continue to work
4. **Error Handling**: Graceful error messages displayed in the chat
5. **Debugging**: Console logs help track the flow of requests
6. **Extensible**: Easy to add more HAWK-AI specific features later

## Future Enhancements

Potential improvements:
1. Add streaming support for real-time responses
2. Display agent chain visualization in the UI
3. Add HAWK-AI specific settings panel
4. Support for file uploads and document analysis
5. Integration with HAWK-AI's analytical frameworks selector
6. Display reasoning steps and sources used by agents

## Architecture Diagram

```
┌─────────────────┐
│   Open WebUI    │
│   (Frontend)    │
└────────┬────────┘
         │ Chat message
         │
         ▼
┌─────────────────────────────┐
│  hawkai/index.ts            │
│  generateOpenAIChatCompletion()
│  - Extract query            │
│  - Call HAWK-AI backend     │
│  - Convert response         │
└────────┬────────────────────┘
         │ HTTP POST
         │ /chat
         ▼
┌─────────────────────────────┐
│  HAWK-AI Backend            │
│  (api_server.py)            │
│  - Receive query            │
│  - Route to orchestrator    │
│  - Execute agent chain      │
│  - Return response          │
└─────────────────────────────┘
```

## Maintenance

When updating either system:

### Updating HAWK-AI Backend
- Ensure `/chat` endpoint signature remains compatible
- Test with Open WebUI after backend changes
- Update CORS settings if frontend port changes

### Updating Open WebUI Frontend
- Check if `generateOpenAIChatCompletion` signature changes
- Update `hawkai/index.ts` wrapper if needed
- Test integration after frontend updates
- Re-apply the import change if `Chat.svelte` is regenerated

## Rollback

To revert to original OpenAI/Ollama integration:

```bash
cd /home/arthurspriet/hawk-ai-webchat

# Change the import back
# In src/lib/components/chat/Chat.svelte line 64:
# import { generateOpenAIChatCompletion } from '$lib/apis/openai';

# Optionally delete the HAWK-AI module
rm -rf src/lib/apis/hawkai/
```

## Contact & Support

For issues or questions:
- Check HAWK-AI logs in `/home/arthurspriet/HAWK-AI/logs/`
- Review Open WebUI console logs (browser F12)
- Verify both services are running and accessible

