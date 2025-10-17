"""
Streaming response formatter for HAWK-AI.
Converts agent results into SSE (Server-Sent Events) format for real-time chat streaming.
"""
import json
from typing import Dict, Any, Generator
from datetime import datetime


def format_progress_chunk(agent_name: str, status: str, chunk_id: str = None) -> str:
    """
    Format agent progress update as SSE chunk.
    
    Args:
        agent_name: Name of the agent (e.g., "search", "analyst", "geo")
        status: Status message (e.g., "starting", "completed", "analyzing")
        chunk_id: Optional unique ID for the chunk
        
    Returns:
        SSE-formatted string
    """
    if chunk_id is None:
        chunk_id = f"chatcmpl-{int(datetime.now().timestamp())}"
    
    # Map agent names to emojis
    agent_emojis = {
        "search": "🔍",
        "analyst": "📊",
        "geo": "🗺️",
        "redactor": "✏️",
        "supervisor": "🧠",
        "reflection": "🤔"
    }
    
    emoji = agent_emojis.get(agent_name.lower(), "⚙️")
    
    # Format status messages
    if status == "starting":
        content = f"{emoji} {agent_name.capitalize()}Agent: Working...\n"
    elif status == "completed":
        content = f"✓ {agent_name.capitalize()}Agent: Done\n"
    else:
        content = f"{emoji} {agent_name.capitalize()}Agent: {status}\n"
    
    chunk = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": "hawk-ai-supervisor",
        "choices": [{
            "index": 0,
            "delta": {"content": content},
            "finish_reason": None
        }]
    }
    
    return f"data: {json.dumps(chunk)}\n\n"


def format_agent_result(agent_name: str, result: Dict[str, Any]) -> str:
    """
    Extract and format agent result for transparent display.
    
    Args:
        agent_name: Name of the agent
        result: Agent result dictionary
        
    Returns:
        Formatted text snippet showing agent contribution
    """
    if result.get("status") != "success":
        return f"⚠️ {agent_name.capitalize()}Agent: {result.get('error', 'Failed')}\n\n"
    
    content = result.get("content", {})
    
    # Agent-specific formatting
    if agent_name == "search":
        # Extract search results summary
        if isinstance(content, dict):
            num_results = len(content.get("results", []))
            return f"🔍 **SearchAgent**: Found {num_results} relevant sources\n\n"
        return f"🔍 **SearchAgent**: Completed web search\n\n"
    
    elif agent_name == "analyst":
        # Extract analyst synthesis or key findings
        if isinstance(content, dict):
            synthesis = content.get("synthesis", "")
            summary = content.get("summary", "")
            
            if synthesis:
                # Truncate to first 200 chars for preview
                preview = synthesis[:200] + "..." if len(synthesis) > 200 else synthesis
                return f"📊 **AnalystAgent**: {preview}\n\n"
            elif summary:
                preview = summary[:200] + "..." if len(summary) > 200 else summary
                return f"📊 **AnalystAgent**: {preview}\n\n"
        
        return f"📊 **AnalystAgent**: Completed analysis\n\n"
    
    elif agent_name == "geo":
        # Extract geo analysis summary
        if isinstance(content, dict):
            hotspots = content.get("hotspots", [])
            if hotspots:
                num_hotspots = len(hotspots)
                return f"🗺️ **GeoAgent**: Identified {num_hotspots} geographic hotspots\n\n"
            
            summary = content.get("summary", "")
            if summary:
                preview = summary[:200] + "..." if len(summary) > 200 else summary
                return f"🗺️ **GeoAgent**: {preview}\n\n"
        
        return f"🗺️ **GeoAgent**: Completed geospatial analysis\n\n"
    
    else:
        return f"✓ **{agent_name.capitalize()}Agent**: Completed\n\n"


def format_synthesis_chunk(text: str, chunk_id: str = None) -> str:
    """
    Format synthesis text as SSE chunk.
    
    Args:
        text: Text content to stream
        chunk_id: Optional unique ID for the chunk
        
    Returns:
        SSE-formatted string
    """
    if chunk_id is None:
        chunk_id = f"chatcmpl-{int(datetime.now().timestamp())}"
    
    chunk = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": "hawk-ai-supervisor",
        "choices": [{
            "index": 0,
            "delta": {"content": text},
            "finish_reason": None
        }]
    }
    
    return f"data: {json.dumps(chunk)}\n\n"


def format_done_chunk(chunk_id: str = None) -> str:
    """
    Format the final [DONE] chunk.
    
    Args:
        chunk_id: Optional unique ID for the chunk
        
    Returns:
        SSE-formatted done signal
    """
    if chunk_id is None:
        chunk_id = f"chatcmpl-{int(datetime.now().timestamp())}"
    
    chunk = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": "hawk-ai-supervisor",
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    
    return f"data: {json.dumps(chunk)}\n\ndata: [DONE]\n\n"


def extract_synthesis_from_result(result: Dict[str, Any]) -> str:
    """
    Extract the synthesis/summary text from supervisor result.
    
    Args:
        result: Supervisor result dictionary
        
    Returns:
        Synthesis text or fallback message
    """
    # Direct summary field
    if "summary" in result:
        summary = result["summary"]
        if isinstance(summary, str):
            return summary
    
    # From results dict
    if "result" in result:
        result_data = result["result"]
        
        if isinstance(result_data, dict):
            # Try summary field
            if "summary" in result_data:
                return result_data["summary"]
            
            # Try nested analyst content
            if "results" in result_data and "analyst" in result_data["results"]:
                analyst = result_data["results"]["analyst"]
                if isinstance(analyst, dict) and "content" in analyst:
                    content = analyst["content"]
                    if isinstance(content, dict):
                        return content.get("synthesis", content.get("summary", ""))
        
        # If result is a string
        if isinstance(result_data, str):
            return result_data
    
    return "Analysis completed. Please check the full report for details."


def stream_supervisor_result(result: Dict[str, Any]) -> Generator[str, None, None]:
    """
    Stream supervisor result as SSE chunks.
    
    Args:
        result: Complete supervisor result dictionary
        
    Yields:
        SSE-formatted chunks
    """
    chunk_id = f"chatcmpl-{int(datetime.now().timestamp())}"
    
    # 1. Stream agent results if available
    if "results" in result:
        yield format_synthesis_chunk("\n**Multi-Agent Analysis Results**\n\n", chunk_id)
        
        for agent_name, agent_result in result["results"].items():
            if agent_name not in ["reflection", "fusion_ratio"]:
                agent_summary = format_agent_result(agent_name, agent_result)
                yield format_synthesis_chunk(agent_summary, chunk_id)
    
    # 2. Stream separator
    yield format_synthesis_chunk("---\n\n**Synthesis**\n\n", chunk_id)
    
    # 3. Stream the synthesis
    synthesis = extract_synthesis_from_result(result)
    
    # Stream synthesis in chunks (word by word for smooth effect)
    words = synthesis.split()
    for i in range(0, len(words), 3):  # Stream 3 words at a time
        chunk_text = " ".join(words[i:i+3]) + " "
        yield format_synthesis_chunk(chunk_text, chunk_id)
    
    # 4. Add final newline
    yield format_synthesis_chunk("\n", chunk_id)
    
    # 5. Done signal
    yield format_done_chunk(chunk_id)


def create_progress_callback(callback_queue):
    """
    Create a progress callback function that adds events to a queue.
    
    Args:
        callback_queue: Queue to add progress events to
        
    Returns:
        Callback function
    """
    def progress_callback(event_type: str, data: Dict[str, Any]):
        """
        Progress callback for agent execution.
        
        Args:
            event_type: Type of event ("agent_start", "agent_complete", "synthesis_start", etc.)
            data: Event data
        """
        callback_queue.put({"type": event_type, "data": data})
    
    return progress_callback

