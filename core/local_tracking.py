"""
Local tracking and logging system for HAWK-AI.
Provides LangSmith integration and local logging capabilities.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
from rich.console import Console

console = Console()


class LocalTracker:
    """Local tracking system for agent operations."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize local tracker."""
        self.config = self._load_config(config_path)
        self.log_dir = Path(self.config['tracking']['log_dir'])
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_path = self.log_dir / f"session_{self.session_id}.jsonl"
        
        # Initialize LangSmith if enabled
        self._setup_langsmith()
        
        console.print(f"[green]Tracking initialized: {self.session_id}[/green]")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_langsmith(self):
        """Setup LangSmith tracking."""
        if self.config['tracking']['langsmith_enabled']:
            os.environ['LANGCHAIN_TRACING_V2'] = 'true'
            os.environ['LANGCHAIN_PROJECT'] = self.config['tracking']['project_name']
            
            # Set API key if provided (for remote tracking)
            if self.config['tracking'].get('api_key'):
                os.environ['LANGCHAIN_API_KEY'] = self.config['tracking']['api_key']
            else:
                # Local mode - disable remote tracing
                os.environ['LANGCHAIN_ENDPOINT'] = 'http://localhost:1984'
            
            console.print("[green]LangSmith tracking enabled[/green]")
    
    def log_event(self, event_type: str, data: Dict[str, Any], agent: Optional[str] = None):
        """Log an event to the session log."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "agent": agent,
            "data": data
        }
        
        with open(self.session_log_path, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def log_agent_start(self, agent_name: str, task: str):
        """Log agent start event."""
        self.log_event("agent_start", {"task": task}, agent=agent_name)
        console.print(f"[cyan]→ {agent_name} started: {task}[/cyan]")
    
    def log_agent_end(self, agent_name: str, result: Any, duration: float):
        """Log agent completion event."""
        self.log_event(
            "agent_end",
            {
                "result": str(result)[:500],  # Truncate long results
                "duration_seconds": duration
            },
            agent=agent_name
        )
        console.print(f"[green]✓ {agent_name} completed ({duration:.2f}s)[/green]")
    
    def log_error(self, agent_name: str, error: Exception):
        """Log error event."""
        self.log_event(
            "error",
            {
                "error_type": type(error).__name__,
                "error_message": str(error)
            },
            agent=agent_name
        )
        console.print(f"[red]✗ {agent_name} error: {error}[/red]")
    
    def log_tool_call(self, agent_name: str, tool_name: str, inputs: Dict[str, Any], output: Any):
        """Log tool call event."""
        self.log_event(
            "tool_call",
            {
                "tool": tool_name,
                "inputs": inputs,
                "output": str(output)[:500]
            },
            agent=agent_name
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        if not self.session_log_path.exists():
            return {"session_id": self.session_id, "events": 0}
        
        events = []
        with open(self.session_log_path, 'r') as f:
            for line in f:
                events.append(json.loads(line))
        
        return {
            "session_id": self.session_id,
            "total_events": len(events),
            "event_types": {
                event_type: len([e for e in events if e['event_type'] == event_type])
                for event_type in set(e['event_type'] for e in events)
            },
            "agents_used": list(set(e['agent'] for e in events if e.get('agent')))
        }
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all session IDs."""
        sessions = []
        for log_file in self.log_dir.glob("session_*.jsonl"):
            session_id = log_file.stem.replace("session_", "")
            sessions.append(session_id)
        return sorted(sessions, reverse=True)


# Global instance
_tracker = None


def get_tracker(config_path: str = "config/settings.yaml") -> LocalTracker:
    """Get or create global tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = LocalTracker(config_path)
    return _tracker

