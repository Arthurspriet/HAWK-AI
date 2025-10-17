#!/usr/bin/env python3
"""
FastAPI server for HAWK-AI
Provides REST API endpoints for the web frontend.
"""
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import get_orchestrator
from agents import register_all_agents
from core.streaming_formatter import (
    format_progress_chunk,
    format_agent_result,
    stream_supervisor_result,
    extract_synthesis_from_result
)

# Initialize FastAPI app
app = FastAPI(
    title="HAWK-AI API",
    description="OSINT-Capable Reasoning Agent API",
    version="1.0.0"
)

# Configure CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
        "http://localhost:5174",  # Vite alternative port
        "http://127.0.0.1:5174",
        "http://localhost:8080",  # Open WebUI default
        "http://127.0.0.1:8080",
        "http://localhost:3001",  # Alternative port
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for maps and analysis outputs
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent)), name="static")

# Global orchestrator instance
orchestrator = None


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str
    session_id: Optional[str] = None
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    status: str
    duration: float
    agents_used: list[str]
    session_id: str
    timestamp: str


class StatusResponse(BaseModel):
    """System status response."""
    status: str
    agents: list[str]
    models: dict
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize HAWK-AI on startup."""
    global orchestrator
    print("🚀 Starting HAWK-AI API Server...")
    print("📋 Registering agents...")
    register_all_agents()
    print("🔧 Initializing orchestrator...")
    orchestrator = get_orchestrator()
    print("✅ HAWK-AI ready!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "HAWK-AI API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "chat": "/chat",
            "status": "/status",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Get registered agents
    from core.agent_registry import get_agent_registry
    registry = get_agent_registry()
    
    return StatusResponse(
        status="online",
        agents=list(registry.agents.keys()),
        models={},  # Could be extended to show model info
        timestamp=datetime.now().isoformat()
    )


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Process a chat query through HAWK-AI with streaming support.
    
    Args:
        request: ChatRequest with query, optional session_id, and stream flag
        
    Returns:
        ChatResponse (non-streaming) or StreamingResponse (streaming)
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Check if streaming is requested
        if request.stream:
            print(f"🔄 Streaming mode enabled for query: {request.query[:50]}...")
            # Return streaming response in OpenAI format
            return StreamingResponse(
                stream_chat_response(request.query, "hawk-ai-supervisor"),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # Non-streaming mode (original behavior)
        # Execute query through orchestrator
        result = await asyncio.to_thread(
            orchestrator.execute_task,
            request.query
        )
        
        # Prepare response
        if result['status'] == 'success':
            # Extract response with agent transparency
            response_text = extract_response_with_agents(result)
            
            response = ChatResponse(
                response=str(response_text),
                status="success",
                duration=result['duration'],
                agents_used=result.get('agents_used', []),
                session_id=request.session_id or "default",
                timestamp=datetime.now().isoformat()
            )
            return response
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Unknown error occurred')
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.get("/history")
async def get_history():
    """Get session history."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        summary = orchestrator.tracker.get_session_summary()
        return {
            "session_id": summary['session_id'],
            "total_events": summary['total_events'],
            "event_types": summary.get('event_types', {}),
            "agents_used": summary.get('agents_used', []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def stream_chat_response(query: str, model: str):
    """
    Async generator for streaming chat responses.
    
    Args:
        query: User query
        model: Model name
        
    Yields:
        SSE-formatted chunks
    """
    import queue
    import threading
    
    # Create a queue for progress updates
    progress_queue = queue.Queue()
    result_container = {}
    
    def execute_with_callback():
        """Execute orchestrator in background thread with progress callback."""
        def progress_callback(event_type: str, data: dict):
            progress_queue.put({"type": event_type, "data": data})
        
        try:
            # Execute with streaming support
            result = orchestrator.execute_task_streaming(query, progress_callback=progress_callback)
            result_container['result'] = result
            progress_queue.put({"type": "done", "data": {}})
        except Exception as e:
            result_container['error'] = str(e)
            progress_queue.put({"type": "error", "data": {"error": str(e)}})
    
    # Start background execution
    thread = threading.Thread(target=execute_with_callback, daemon=True)
    thread.start()
    
    chunk_id = f"chatcmpl-{int(datetime.now().timestamp())}"
    
    # Stream progress updates
    while True:
        try:
            event = progress_queue.get(timeout=0.5)
            
            if event["type"] == "agent_start":
                agent_name = event["data"].get("agent", "unknown")
                yield format_progress_chunk(agent_name, "starting", chunk_id)
            
            elif event["type"] == "agent_complete":
                agent_name = event["data"].get("agent", "unknown")
                yield format_progress_chunk(agent_name, "completed", chunk_id)
            
            elif event["type"] == "synthesis_start":
                yield format_progress_chunk("supervisor", "Synthesizing results...", chunk_id)
            
            elif event["type"] == "done":
                # Stream the final result
                if 'result' in result_container:
                    result = result_container['result']
                    async for chunk in async_stream_result(result, chunk_id):
                        yield chunk
                break
            
            elif event["type"] == "error":
                error_msg = event["data"].get("error", "Unknown error")
                yield format_progress_chunk("error", f"Error: {error_msg}", chunk_id)
                break
        
        except queue.Empty:
            # Check if thread is still alive
            if not thread.is_alive() and 'result' in result_container:
                # Thread finished, stream the result
                result = result_container['result']
                async for chunk in async_stream_result(result, chunk_id):
                    yield chunk
                break
            elif not thread.is_alive() and 'error' in result_container:
                error_msg = result_container['error']
                yield format_progress_chunk("error", f"Error: {error_msg}", chunk_id)
                break


async def async_stream_result(result: dict, chunk_id: str):
    """
    Async wrapper for streaming supervisor result.
    
    Args:
        result: Supervisor result dictionary
        chunk_id: Chunk ID for SSE
        
    Yields:
        SSE chunks
    """
    from core.streaming_formatter import format_synthesis_chunk, format_done_chunk
    
    # Extract agent results and format them
    if result.get('status') == 'success' and 'result' in result:
        supervisor_result = result['result']
        
        # Stream agent summaries
        if isinstance(supervisor_result, dict) and 'results' in supervisor_result:
            yield format_synthesis_chunk("\n**Analysis Complete**\n\n", chunk_id)
            
            for agent_name, agent_result in supervisor_result['results'].items():
                if agent_name not in ["reflection", "fusion_ratio"]:
                    agent_summary = format_agent_result(agent_name, agent_result)
                    yield format_synthesis_chunk(agent_summary, chunk_id)
            
            yield format_synthesis_chunk("---\n\n**Synthesis**\n\n", chunk_id)
        
        # Stream synthesis
        synthesis = extract_synthesis_from_result(supervisor_result)
        
        # Stream word by word for smooth effect
        words = synthesis.split()
        for i in range(0, len(words), 3):
            chunk_text = " ".join(words[i:i+3]) + " "
            yield format_synthesis_chunk(chunk_text, chunk_id)
            await asyncio.sleep(0.01)  # Small delay for smooth streaming
        
        yield format_synthesis_chunk("\n", chunk_id)
    else:
        # Error case
        error_msg = result.get('error', 'Unknown error occurred')
        yield format_synthesis_chunk(f"Error: {error_msg}\n", chunk_id)
    
    # Done signal
    yield format_done_chunk(chunk_id)


@app.post("/v1/chat/completions")
@app.post("/api/chat/completions")
async def chat_completions(request: dict):
    """
    OpenAI-compatible chat completions endpoint with streaming support.
    This allows OpenWebUI to call HAWK-AI using the standard OpenAI API format.
    
    Supports both streaming and non-streaming modes:
    - If request contains 'stream': true, returns SSE stream
    - Otherwise, returns complete response (backward compatible)
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Log the incoming request for debugging
        print(f"\n{'='*60}")
        print(f"📥 Incoming request to /v1/chat/completions")
        print(f"Request keys: {list(request.keys())}")
        print(f"Stream parameter: {request.get('stream', 'NOT SET')}")
        print(f"{'='*60}\n")
        
        # Extract messages from OpenAI format
        messages = request.get('messages', [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Get the last user message
        user_messages = [m for m in messages if m.get('role') == 'user']
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_message = user_messages[-1]
        query = last_message.get('content', '')
        
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Empty query")
        
        # Get model and other parameters
        model = request.get('model', 'hawk-ai-supervisor')
        session_id = request.get('session_id') or request.get('chat_id', 'default')
        # DEFAULT TO STREAMING for Open WebUI compatibility
        stream = request.get('stream', True)
        
        # Check if streaming is requested
        if stream:
            print(f"🔄 Streaming mode enabled (OpenAI endpoint) for query: {query[:50]}...")
            # Return streaming response
            return StreamingResponse(
                stream_chat_response(query, model),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # Non-streaming mode (backward compatible)
        # Execute query through orchestrator
        result = await asyncio.to_thread(
            orchestrator.execute_task,
            query
        )
        
        # Prepare OpenAI-compatible response
        if result['status'] == 'success':
            # Extract response with agent transparency
            response_text = extract_response_with_agents(result)
            
            # Return OpenAI-compatible format
            return {
                "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": str(response_text)
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(query.split()),
                    "completion_tokens": len(str(response_text).split()),
                    "total_tokens": len(query.split()) + len(str(response_text).split())
                }
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Unknown error occurred')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


def extract_response_with_agents(result: dict) -> str:
    """
    Extract response with agent transparency (showing agent names + findings).
    
    Args:
        result: Orchestrator result dictionary
        
    Returns:
        Formatted response text with agent contributions
    """
    if result.get('status') != 'success':
        return f"Error: {result.get('error', 'Unknown error')}"
    
    response_parts = []
    
    # Extract supervisor result
    supervisor_result = result.get('result', {})
    
    # Add agent results if available
    if isinstance(supervisor_result, dict) and 'results' in supervisor_result:
        response_parts.append("**Multi-Agent Analysis**\n")
        
        for agent_name, agent_result in supervisor_result['results'].items():
            if agent_name not in ["reflection", "fusion_ratio"]:
                agent_summary = format_agent_result(agent_name, agent_result)
                response_parts.append(agent_summary)
        
        response_parts.append("\n---\n\n**Synthesis**\n\n")
    
    # Add synthesis/summary
    synthesis = extract_synthesis_from_result(supervisor_result)
    response_parts.append(synthesis)
    
    return "".join(response_parts)


@app.get("/v1/models")
@app.get("/api/models")
async def get_models():
    """
    OpenAI-compatible models endpoint.
    Returns available HAWK-AI agents as models for OpenWebUI integration.
    """
    from core.agent_registry import get_agent_registry
    
    try:
        registry = get_agent_registry()
        models_data = []
        
        # Define HAWK-AI models based on registered agents
        hawk_models = [
            {
                "id": "hawk-ai-supervisor",
                "name": "HAWK-AI Supervisor",
                "description": "Multi-agent orchestrator for complex geopolitical analysis",
                "capabilities": ["osint", "geospatial", "analysis", "web_search"]
            },
            {
                "id": "hawk-ai-analyst",
                "name": "HAWK-AI Analyst",
                "description": "Expert analytical agent for in-depth geopolitical insights",
                "capabilities": ["analysis", "frameworks", "reasoning"]
            },
            {
                "id": "hawk-ai-geo",
                "name": "HAWK-AI Geo",
                "description": "Geospatial analysis and mapping specialist",
                "capabilities": ["geospatial", "mapping", "visualization"]
            },
            {
                "id": "hawk-ai-search",
                "name": "HAWK-AI Search",
                "description": "Web search and information gathering specialist",
                "capabilities": ["web_search", "osint", "data_collection"]
            }
        ]
        
        # Convert to OpenAI format
        current_time = int(datetime.now().timestamp())
        for model in hawk_models:
            models_data.append({
                "id": model["id"],
                "object": "model",
                "created": current_time,
                "owned_by": "hawk-ai",
                "permission": [],
                "root": model["id"],
                "parent": None,
                "name": model["name"],
                "description": model["description"],
                "capabilities": model["capabilities"],
                # OpenWebUI specific fields
                "info": {
                    "meta": {
                        "description": model["description"],
                        "capabilities": model["capabilities"]
                    }
                }
            })
        
        return {
            "object": "list",
            "data": models_data
        }
    
    except Exception as e:
        print(f"Error getting models: {e}")
        return {
            "object": "list",
            "data": []
        }


def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HAWK-AI FastAPI Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"""
╦ ╦╔═╗╦ ╦╦╔═  ╔═╗╦
║═╣╠═╣║║║╠╩╗  ╠═╣║
╩ ╩╩ ╩╚╩╝╩ ╩  ╩ ╩╩
OSINT-Capable Reasoning Agent

🌐 Starting API Server on http://{args.host}:{args.port}
📚 API Documentation: http://{args.host}:{args.port}/docs
🔍 Interactive API: http://{args.host}:{args.port}/redoc
    """)
    
    run_server(host=args.host, port=args.port, reload=args.reload)

