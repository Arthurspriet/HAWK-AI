"""
Agent registry for HAWK-AI.
Manages registration and retrieval of available agents.
"""
from typing import Dict, Any, Optional, List, Type
from enum import Enum
from rich.console import Console

console = Console()


class AgentType(Enum):
    """Types of agents available in the system."""
    SUPERVISOR = "supervisor"
    SEARCH = "search"
    ANALYST = "analyst"
    REDACTOR = "redactor"
    CODEEXEC = "codeexec"


class AgentCapability(Enum):
    """Capabilities that agents can provide."""
    WEB_SEARCH = "web_search"
    NEWS_SEARCH = "news_search"
    CODE_EXECUTION = "code_execution"
    DATA_ANALYSIS = "data_analysis"
    TEXT_SUMMARIZATION = "text_summarization"
    CONTEXT_RETRIEVAL = "context_retrieval"
    PATTERN_DETECTION = "pattern_detection"
    REPORT_GENERATION = "report_generation"
    ORCHESTRATION = "orchestration"


class AgentMetadata:
    """Metadata for an agent."""
    
    def __init__(
        self,
        agent_type: AgentType,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
        dependencies: Optional[List[str]] = None
    ):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.dependencies = dependencies or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "capabilities": [cap.value for cap in self.capabilities],
            "dependencies": self.dependencies
        }


class AgentRegistry:
    """Registry for managing available agents."""
    
    def __init__(self):
        """Initialize agent registry."""
        self.agents: Dict[AgentType, AgentMetadata] = {}
        self.agent_classes: Dict[AgentType, Type] = {}
        self.agent_instances: Dict[AgentType, Any] = {}
        
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register default agent metadata."""
        # Supervisor Agent
        self.register_metadata(AgentMetadata(
            agent_type=AgentType.SUPERVISOR,
            name="Supervisor Agent",
            description="Orchestrates task execution and coordinates other agents",
            capabilities=[AgentCapability.ORCHESTRATION]
        ))
        
        # Search Agent
        self.register_metadata(AgentMetadata(
            agent_type=AgentType.SEARCH,
            name="Search Agent",
            description="Performs web searches and retrieves online information",
            capabilities=[
                AgentCapability.WEB_SEARCH,
                AgentCapability.NEWS_SEARCH
            ],
            dependencies=["duckduckgo-search", "beautifulsoup4"]
        ))
        
        # Analyst Agent
        self.register_metadata(AgentMetadata(
            agent_type=AgentType.ANALYST,
            name="Analyst Agent",
            description="Analyzes data patterns and provides contextual insights",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.PATTERN_DETECTION,
                AgentCapability.CONTEXT_RETRIEVAL
            ],
            dependencies=["pandas", "numpy", "scikit-learn"]
        ))
        
        # Redactor Agent
        self.register_metadata(AgentMetadata(
            agent_type=AgentType.REDACTOR,
            name="Redactor Agent",
            description="Summarizes and reformats text content",
            capabilities=[
                AgentCapability.TEXT_SUMMARIZATION,
                AgentCapability.REPORT_GENERATION
            ],
            dependencies=["tiktoken"]
        ))
        
        # CodeExec Agent
        self.register_metadata(AgentMetadata(
            agent_type=AgentType.CODEEXEC,
            name="CodeExec Agent",
            description="Executes code in a sandboxed environment",
            capabilities=[AgentCapability.CODE_EXECUTION],
            dependencies=["subprocess"]
        ))
    
    def register_metadata(self, metadata: AgentMetadata):
        """
        Register agent metadata.
        
        Args:
            metadata: Agent metadata to register
        """
        self.agents[metadata.agent_type] = metadata
        console.print(f"[green]Registered agent: {metadata.name}[/green]")
    
    def register_class(self, agent_type: AgentType, agent_class: Type):
        """
        Register agent class.
        
        Args:
            agent_type: Type of agent
            agent_class: Agent class to register
        """
        self.agent_classes[agent_type] = agent_class
    
    def get_agent(self, agent_type: AgentType, force_new: bool = False) -> Optional[Any]:
        """
        Get agent instance (creates if doesn't exist).
        
        Args:
            agent_type: Type of agent to retrieve
            force_new: Force creation of new instance
            
        Returns:
            Agent instance or None if not found
        """
        if force_new or agent_type not in self.agent_instances:
            if agent_type in self.agent_classes:
                try:
                    self.agent_instances[agent_type] = self.agent_classes[agent_type]()
                    console.print(f"[cyan]Created instance of {agent_type.value} agent[/cyan]")
                except Exception as e:
                    console.print(f"[red]Error creating {agent_type.value} agent: {e}[/red]")
                    return None
            else:
                console.print(f"[yellow]Agent class not registered: {agent_type.value}[/yellow]")
                return None
        
        return self.agent_instances.get(agent_type)
    
    def get_metadata(self, agent_type: AgentType) -> Optional[AgentMetadata]:
        """
        Get agent metadata.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Agent metadata or None if not found
        """
        return self.agents.get(agent_type)
    
    def list_agents(self) -> List[AgentMetadata]:
        """
        List all registered agents.
        
        Returns:
            List of agent metadata
        """
        return list(self.agents.values())
    
    def find_agents_by_capability(self, capability: AgentCapability) -> List[AgentType]:
        """
        Find agents that have a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agent types with the capability
        """
        return [
            agent_type
            for agent_type, metadata in self.agents.items()
            if capability in metadata.capabilities
        ]
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """
        Get summary of all registered agents.
        
        Returns:
            Dictionary with agent summary
        """
        return {
            "total_agents": len(self.agents),
            "agents": {
                agent_type.value: metadata.to_dict()
                for agent_type, metadata in self.agents.items()
            }
        }


# Global registry instance
_registry = None


def get_agent_registry() -> AgentRegistry:
    """Get or create global agent registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry

