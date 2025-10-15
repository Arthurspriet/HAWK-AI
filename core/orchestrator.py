"""
Orchestrator for HAWK-AI agent system.
Manages task routing, agent coordination, and result aggregation.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import yaml
from rich.console import Console
from rich.panel import Panel

from core.agent_registry import get_agent_registry, AgentType, AgentCapability
from core.local_tracking import get_tracker
from core.vector_store import VectorStore
from core.ollama_client import get_ollama_client

console = Console()


class TaskType:
    """Task type identifiers."""
    SEARCH = "search"
    ANALYSIS = "analysis"
    CODE_EXECUTION = "code_execution"
    SUMMARIZATION = "summarization"
    GENERAL_QUERY = "general_query"


class Orchestrator:
    """Main orchestrator for the agent system."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize orchestrator."""
        self.config = self._load_config(config_path)
        self.registry = get_agent_registry()
        self.tracker = get_tracker(config_path)
        self.ollama_client = get_ollama_client(config_path)
        self.vector_store = VectorStore(config_path)
        
        console.print("[bold green]HAWK-AI Orchestrator initialized[/bold green]")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def classify_task(self, query: str) -> str:
        """
        Classify the task type based on the query.
        
        Args:
            query: User query
            
        Returns:
            Task type identifier
        """
        query_lower = query.lower()
        
        # Simple keyword-based classification
        if any(word in query_lower for word in ['search', 'find', 'look up', 'google', 'web']):
            return TaskType.SEARCH
        
        if any(word in query_lower for word in ['analyze', 'pattern', 'trend', 'statistics', 'data']):
            return TaskType.ANALYSIS
        
        if any(word in query_lower for word in ['execute', 'run code', 'calculate', 'compute']):
            return TaskType.CODE_EXECUTION
        
        if any(word in query_lower for word in ['summarize', 'brief', 'summary', 'tldr']):
            return TaskType.SUMMARIZATION
        
        return TaskType.GENERAL_QUERY
    
    def select_agents(self, task_type: str, query: str) -> List[AgentType]:
        """
        Select appropriate agents for a task.
        
        Args:
            task_type: Type of task
            query: User query
            
        Returns:
            List of agent types to use
        """
        agents = []
        
        if task_type == TaskType.SEARCH:
            agents.append(AgentType.SEARCH)
            agents.append(AgentType.REDACTOR)
        
        elif task_type == TaskType.ANALYSIS:
            agents.append(AgentType.ANALYST)
            agents.append(AgentType.REDACTOR)
        
        elif task_type == TaskType.CODE_EXECUTION:
            agents.append(AgentType.CODEEXEC)
        
        elif task_type == TaskType.SUMMARIZATION:
            agents.append(AgentType.REDACTOR)
        
        else:  # GENERAL_QUERY
            # Check if we need historical context
            if any(word in query.lower() for word in ['conflict', 'event', 'country', 'history', 'acled']):
                agents.append(AgentType.ANALYST)
            
            # Check if we need current information
            if any(word in query.lower() for word in ['recent', 'latest', 'current', 'news']):
                agents.append(AgentType.SEARCH)
            
            # Always include redactor for final output
            agents.append(AgentType.REDACTOR)
        
        return agents if agents else [AgentType.SUPERVISOR]
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant historical context for a query.
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            
        Returns:
            List of relevant context documents
        """
        try:
            console.print(f"[cyan]Retrieving context for: {query}[/cyan]")
            results = self.vector_store.search(query, top_k=top_k)
            
            if results:
                console.print(f"[green]Retrieved {len(results)} relevant documents[/green]")
            
            return results
        except Exception as e:
            console.print(f"[red]Error retrieving context: {e}[/red]")
            return []
    
    def execute_task(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task through the agent system.
        
        Args:
            query: User query
            context: Optional additional context
            
        Returns:
            Dictionary with execution results
        """
        start_time = datetime.now()
        
        console.print(Panel.fit(
            f"[bold]Task:[/bold] {query}",
            title="HAWK-AI Processing",
            border_style="cyan"
        ))
        
        # Track task start
        self.tracker.log_event("task_start", {"query": query})
        
        try:
            # Classify task
            task_type = self.classify_task(query)
            console.print(f"[cyan]Task type: {task_type}[/cyan]")
            
            # Retrieve historical context if relevant
            historical_context = []
            if task_type in [TaskType.ANALYSIS, TaskType.GENERAL_QUERY]:
                historical_context = self.retrieve_context(query)
            
            # Select agents
            selected_agents = self.select_agents(task_type, query)
            console.print(f"[cyan]Selected agents: {[a.value for a in selected_agents]}[/cyan]")
            
            # Execute with supervisor
            supervisor = self.registry.get_agent(AgentType.SUPERVISOR)
            
            if supervisor:
                result = supervisor.run(query=query)
            else:
                # Fallback to direct execution
                result = self._direct_execution(query, task_type, historical_context)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Track task completion
            self.tracker.log_event("task_complete", {
                "query": query,
                "task_type": task_type,
                "duration": duration,
                "agents_used": [a.value for a in selected_agents]
            })
            
            console.print(f"\n[green]✓ Task completed in {duration:.2f}s[/green]")
            
            return {
                "status": "success",
                "query": query,
                "task_type": task_type,
                "result": result,
                "duration": duration,
                "agents_used": [a.value for a in selected_agents]
            }
            
        except Exception as e:
            console.print(f"[red]Error executing task: {e}[/red]")
            self.tracker.log_error("orchestrator", e)
            
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "duration": (datetime.now() - start_time).total_seconds()
            }
    
    def _direct_execution(self, query: str, task_type: str, historical_context: List[Dict[str, Any]]) -> str:
        """
        Direct execution fallback when supervisor is not available.
        
        Args:
            query: User query
            task_type: Type of task
            historical_context: Retrieved historical context
            
        Returns:
            Execution result
        """
        console.print("[yellow]Using direct execution mode[/yellow]")
        
        # Build context
        context_text = ""
        if historical_context:
            context_text = "\n\nHistorical Context:\n"
            for i, ctx in enumerate(historical_context[:3], 1):
                context_text += f"\n{i}. {ctx['document'][:300]}..."
        
        # Build prompt
        prompt = f"""You are HAWK-AI, an OSINT-capable reasoning agent.

Task Type: {task_type}
Query: {query}
{context_text}

Please provide a comprehensive response to the query."""
        
        # Generate response
        console.print("[cyan]Generating response...[/cyan]")
        response = self.ollama_client.generate(prompt)
        
        return response
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            Dictionary with system status information
        """
        vector_stats = self.vector_store.get_stats()
        session_summary = self.tracker.get_session_summary()
        agent_summary = self.registry.get_agent_summary()
        
        return {
            "session": session_summary,
            "agents": agent_summary,
            "vector_store": vector_stats,
            "ollama": {
                "host": self.ollama_client.host,
                "model": self.config['ollama']['model_default']
            }
        }
    
    def display_status(self):
        """Display system status in a formatted way."""
        status = self.get_system_status()
        
        console.print("\n[bold]HAWK-AI System Status[/bold]")
        console.print("=" * 60)
        
        console.print(f"\n[cyan]Session:[/cyan] {status['session']['session_id']}")
        console.print(f"[cyan]Events:[/cyan] {status['session']['total_events']}")
        
        console.print(f"\n[cyan]Agents:[/cyan] {status['agents']['total_agents']} registered")
        for agent_name in status['agents']['agents'].keys():
            console.print(f"  • {agent_name}")
        
        console.print(f"\n[cyan]Vector Store:[/cyan] {status['vector_store']['total_documents']} documents")
        console.print(f"[cyan]Ollama:[/cyan] {status['ollama']['model']} @ {status['ollama']['host']}")
        
        console.print("=" * 60)


def get_orchestrator(config_path: str = "config/settings.yaml") -> Orchestrator:
    """Get or create orchestrator instance."""
    return Orchestrator(config_path)

