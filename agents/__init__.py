"""
HAWK-AI Agents Package.
Contains all specialized agent implementations.
"""
from agents.supervisor_agent import SupervisorAgent
from agents.search_agent import SearchAgent
from agents.analyst_agent import AnalystAgent
from agents.redactor_agent import RedactorAgent
from agents.codeexec_agent import CodeExecAgent

__all__ = [
    'SupervisorAgent',
    'SearchAgent',
    'AnalystAgent',
    'RedactorAgent',
    'CodeExecAgent'
]


def register_all_agents():
    """Register all agent classes with the agent registry."""
    from core.agent_registry import get_agent_registry, AgentType
    
    registry = get_agent_registry()
    
    registry.register_class(AgentType.SUPERVISOR, SupervisorAgent)
    registry.register_class(AgentType.SEARCH, SearchAgent)
    registry.register_class(AgentType.ANALYST, AnalystAgent)
    registry.register_class(AgentType.REDACTOR, RedactorAgent)
    registry.register_class(AgentType.CODEEXEC, CodeExecAgent)

