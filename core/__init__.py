"""
HAWK-AI Core Package.
Contains core system components and tools.
"""
from core.orchestrator import Orchestrator, get_orchestrator
from core.agent_registry import AgentRegistry, get_agent_registry, AgentType, AgentCapability
from core.local_tracking import LocalTracker, get_tracker
from core.ollama_client import OllamaClientWrapper, get_ollama_client
from core.vector_store import VectorStore
from core.tools_websearch import WebSearchTool, get_websearch_tool
from core.tools_codeexec import CodeExecutionTool, get_codeexec_tool
from core.tools_analyst import AnalystTool, get_analyst_tool
from core.tools_redactor import RedactionTool, get_redaction_tool

__all__ = [
    'Orchestrator',
    'get_orchestrator',
    'AgentRegistry',
    'get_agent_registry',
    'AgentType',
    'AgentCapability',
    'LocalTracker',
    'get_tracker',
    'OllamaClientWrapper',
    'get_ollama_client',
    'VectorStore',
    'WebSearchTool',
    'get_websearch_tool',
    'CodeExecutionTool',
    'get_codeexec_tool',
    'AnalystTool',
    'get_analyst_tool',
    'RedactionTool',
    'get_redaction_tool'
]

