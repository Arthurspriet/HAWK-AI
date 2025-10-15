"""
Supervisor Agent for HAWK-AI.
Orchestrates task execution and coordinates sub-agents.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from rich.console import Console

from core.agent_registry import AgentType, get_agent_registry
from core.local_tracking import get_tracker
from core.ollama_client import get_ollama_client

console = Console()


class SupervisorAgent:
    """Supervisor agent that coordinates other agents."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize supervisor agent."""
        self.config_path = config_path
        self.registry = get_agent_registry()
        self.tracker = get_tracker(config_path)
        self.ollama_client = get_ollama_client(config_path)
        
        console.print("[green]Supervisor Agent initialized[/green]")
    
    def execute(
        self,
        query: str,
        task_type: str,
        agents: List[AgentType],
        historical_context: Optional[List[Dict[str, Any]]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a task by coordinating sub-agents.
        
        Args:
            query: User query
            task_type: Type of task
            agents: List of agents to coordinate
            historical_context: Historical context from vector store
            additional_context: Additional context data
            
        Returns:
            Final result after coordinating agents
        """
        start_time = datetime.now()
        self.tracker.log_agent_start("supervisor", query)
        
        try:
            console.print(f"\n[bold cyan]Supervisor coordinating {len(agents)} agents[/bold cyan]")
            
            agent_results = {}
            
            # Execute each agent
            for agent_type in agents:
                if agent_type == AgentType.SUPERVISOR:
                    continue  # Skip self
                
                agent = self.registry.get_agent(agent_type)
                if agent:
                    console.print(f"\n[cyan]→ Executing {agent_type.value} agent...[/cyan]")
                    
                    agent_start = datetime.now()
                    
                    try:
                        # Execute agent based on type
                        result = self._execute_agent(
                            agent_type,
                            agent,
                            query,
                            historical_context,
                            agent_results
                        )
                        
                        agent_results[agent_type.value] = result
                        
                        duration = (datetime.now() - agent_start).total_seconds()
                        self.tracker.log_agent_end(agent_type.value, result, duration)
                        
                    except Exception as e:
                        console.print(f"[red]Error in {agent_type.value} agent: {e}[/red]")
                        self.tracker.log_error(agent_type.value, e)
                        agent_results[agent_type.value] = f"Error: {str(e)}"
            
            # Synthesize final response
            final_result = self._synthesize_results(query, task_type, agent_results, historical_context)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.tracker.log_agent_end("supervisor", final_result, duration)
            
            return final_result
            
        except Exception as e:
            console.print(f"[red]Supervisor error: {e}[/red]")
            self.tracker.log_error("supervisor", e)
            return f"Error in task execution: {str(e)}"
    
    def _execute_agent(
        self,
        agent_type: AgentType,
        agent: Any,
        query: str,
        historical_context: Optional[List[Dict[str, Any]]],
        previous_results: Dict[str, Any]
    ) -> str:
        """
        Execute a specific agent.
        
        Args:
            agent_type: Type of agent
            agent: Agent instance
            query: User query
            historical_context: Historical context
            previous_results: Results from previous agents
            
        Returns:
            Agent execution result
        """
        if agent_type == AgentType.SEARCH:
            return agent.search_and_report(query)
        
        elif agent_type == AgentType.ANALYST:
            return agent.analyze(query, historical_context)
        
        elif agent_type == AgentType.REDACTOR:
            # Collect all previous results
            combined_text = f"Query: {query}\n\n"
            for agent_name, result in previous_results.items():
                combined_text += f"\n{agent_name.upper()} RESULTS:\n{result}\n"
            
            return agent.create_summary(combined_text)
        
        elif agent_type == AgentType.CODEEXEC:
            # Extract code from query if present
            return agent.execute_from_query(query)
        
        else:
            return f"Agent type {agent_type.value} execution not implemented"
    
    def _synthesize_results(
        self,
        query: str,
        task_type: str,
        agent_results: Dict[str, Any],
        historical_context: Optional[List[Dict[str, Any]]]
    ) -> str:
        """
        Synthesize results from multiple agents into final response.
        
        Args:
            query: User query
            task_type: Type of task
            agent_results: Results from all agents
            historical_context: Historical context used
            
        Returns:
            Synthesized final response
        """
        console.print("\n[cyan]Synthesizing final response...[/cyan]")
        
        # Build synthesis prompt
        prompt_parts = [
            "You are HAWK-AI, an OSINT-capable reasoning agent.",
            f"\nOriginal Query: {query}",
            f"Task Type: {task_type}",
            "\nThe following sub-agents have provided their analyses:\n"
        ]
        
        for agent_name, result in agent_results.items():
            prompt_parts.append(f"\n{agent_name.upper()}:")
            prompt_parts.append(f"{str(result)[:1000]}")  # Truncate long results
        
        if historical_context:
            prompt_parts.append("\n\nHistorical Context:")
            for i, ctx in enumerate(historical_context[:2], 1):
                prompt_parts.append(f"\n{i}. {ctx['document'][:300]}...")
        
        prompt_parts.append("\n\nPlease synthesize all this information into a comprehensive, well-structured response that directly addresses the original query. Be concise but thorough.")
        
        prompt = "\n".join(prompt_parts)
        
        # Generate synthesis
        response = self.ollama_client.generate(prompt)
        
        return response
    
    def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """
        Analyze query complexity to determine execution strategy.
        
        Args:
            query: User query
            
        Returns:
            Dictionary with complexity analysis
        """
        word_count = len(query.split())
        has_multiple_questions = query.count('?') > 1
        
        # Simple complexity scoring
        complexity_score = 0
        if word_count > 20:
            complexity_score += 2
        if has_multiple_questions:
            complexity_score += 2
        if any(word in query.lower() for word in ['analyze', 'compare', 'evaluate']):
            complexity_score += 1
        
        return {
            "word_count": word_count,
            "multiple_questions": has_multiple_questions,
            "complexity_score": complexity_score,
            "complexity_level": "high" if complexity_score >= 3 else "medium" if complexity_score >= 1 else "low"
        }

