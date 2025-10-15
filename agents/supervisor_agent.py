"""
SupervisorAgent for HAWK-AI.
Central coordinator between specialized sub-agents: SearchAgent, AnalystAgent, GeoAgent, RedactorAgent.
Implements semantic routing, parallel execution, and unified report generation.
"""

import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_ollama import OllamaLLM

from agents.search_agent import SearchAgent
from agents.analyst_agent import AnalystAgent
from agents.geo_agent import GeoAgent

try:
    from agents.redactor_agent import RedactorAgent
except ImportError:
    class RedactorAgent:
        """Stub RedactorAgent if module not available."""
        def create_summary(self, text: str, style: str = None) -> str:
            """Simple text truncation fallback."""
            return text[:4000] if len(text) > 4000 else text


class SupervisorAgent:
    """
    Central orchestration agent that coordinates specialized sub-agents.
    
    Features:
    - Semantic routing based on query intent
    - Parallel agent execution
    - Unified report generation
    - Comprehensive logging
    """
    
    def __init__(self, model: str = "magistral:latest"):
        """
        Initialize SupervisorAgent.
        
        Args:
            model: Ollama model for synthesis and reasoning
        """
        self.model = model
        self.llm = OllamaLLM(model=model, base_url="http://127.0.0.1:11434")
        
        # Initialize sub-agents
        try:
            self.search_agent = SearchAgent()
        except Exception as e:
            print(f"⚠️  Warning: SearchAgent initialization failed: {e}")
            self.search_agent = None
        
        try:
            self.analyst_agent = AnalystAgent()
        except Exception as e:
            print(f"⚠️  Warning: AnalystAgent initialization failed: {e}")
            self.analyst_agent = None
        
        try:
            self.geo_agent = GeoAgent()
        except Exception as e:
            print(f"⚠️  Warning: GeoAgent initialization failed: {e}")
            self.geo_agent = None
        
        try:
            self.redactor_agent = RedactorAgent()
        except Exception as e:
            print(f"⚠️  Warning: RedactorAgent initialization failed: {e}")
            self.redactor_agent = None
        
        # Setup logging
        self.logger = logging.getLogger("SupervisorAgent")
        self._setup_logging()
        
        self.logger.info(f"SupervisorAgent initialized with model: {model}")
    
    def _setup_logging(self):
        """Configure logging to file and console."""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logger
        self.logger.setLevel(logging.INFO)
        
        # File handler
        log_file = log_dir / "supervisor_agent.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add handlers if not already present
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def _detect_intent(self, query: str) -> List[str]:
        """
        Detect which agents should be activated based on query keywords.
        
        Args:
            query: User query string
            
        Returns:
            List of agent names to activate
        """
        q = query.lower()
        agents = []
        
        # Geographic/spatial keywords
        geo_keywords = [
            "map", "where", "region", "hotspot", "geographic", "spatial",
            "location", "cluster", "distribution", "territory", "area"
        ]
        if any(keyword in q for keyword in geo_keywords):
            agents.append("geo")
        
        # Analytical/historical keywords
        analyst_keywords = [
            "trend", "escalation", "conflict", "history", "pattern",
            "analysis", "analyze", "historical", "temporal", "evolution",
            "development", "change over time"
        ]
        if any(keyword in q for keyword in analyst_keywords):
            agents.append("analyst")
        
        # Search/news keywords
        search_keywords = [
            "news", "latest", "today", "update", "recent", "current",
            "breaking", "search", "find", "information about"
        ]
        if any(keyword in q for keyword in search_keywords):
            agents.append("search")
        
        # If no specific intent detected, default to analyst (comprehensive analysis)
        if not agents:
            agents.append("analyst")
        
        self.logger.info(f"Detected intent: {agents}")
        print(f"🧭 Detected intent: {agents}")
        
        return agents
    
    def _extract_country_from_query(self, query: str) -> str:
        """
        Extract country name from query for GeoAgent.
        Simple heuristic: last capitalized word or common country names.
        
        Args:
            query: Query string
            
        Returns:
            Extracted country name or "Sudan" as default
        """
        # Common countries in ACLED data
        common_countries = [
            "Sudan", "South Sudan", "Nigeria", "Somalia", "Ethiopia",
            "Kenya", "Yemen", "Syria", "Iraq", "Afghanistan",
            "Myanmar", "Ukraine", "Mali", "Burkina Faso"
        ]
        
        # Check for exact country matches
        for country in common_countries:
            if country.lower() in query.lower():
                return country
        
        # Fallback: try to extract last capitalized word(s)
        words = query.split()
        for i in range(len(words) - 1, -1, -1):
            if words[i][0].isupper() and len(words[i]) > 3:
                return words[i]
        
        # Default fallback
        return "Sudan"
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Execute the supervisor workflow.
        
        Steps:
        1. Parse query and detect intent
        2. Execute relevant agents in parallel
        3. Merge and synthesize results
        4. Generate unified intelligence report
        5. Save to JSON file
        
        Args:
            query: User query
            
        Returns:
            Complete report dictionary
        """
        start_time = datetime.utcnow()
        self.logger.info(f"Supervisor received query: {query}")
        print(f"\n{'='*80}")
        print(f"HAWK-AI Supervisor Agent")
        print(f"{'='*80}")
        print(f"Query: {query}\n")
        
        # Detect which agents to use
        agents_to_use = self._detect_intent(query)
        
        # Execute agents in parallel
        print(f"🕵️  Running {len(agents_to_use)} agent(s) in parallel...\n")
        results = self._execute_agents_parallel(query, agents_to_use)
        
        # Synthesize results
        print("🧠 Synthesizing results with LLM...\n")
        synthesis = self._synthesize_results(query, results)
        
        # Create final report
        timestamp = start_time.isoformat()
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        report = {
            "timestamp": timestamp,
            "query": query,
            "agents": agents_to_use,
            "results": results,
            "summary": synthesis,
            "duration_seconds": round(duration, 2)
        }
        
        # Save report
        report_path = self._save_report(report)
        
        print(f"✅ Intelligence report saved → {report_path}")
        print(f"⏱️  Total duration: {duration:.2f}s")
        print(f"{'='*80}\n")
        
        self.logger.info(f"Report generated: {report_path} ({duration:.2f}s)")
        
        return report
    
    def _execute_agents_parallel(self, query: str, agents: List[str]) -> Dict[str, Any]:
        """
        Execute multiple agents in parallel using ThreadPoolExecutor.
        
        Args:
            query: User query
            agents: List of agent names to execute
            
        Returns:
            Dictionary of agent results
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            
            # Submit tasks
            if "search" in agents and self.search_agent:
                future = executor.submit(self._run_search_agent, query)
                futures[future] = "search"
            
            if "analyst" in agents and self.analyst_agent:
                future = executor.submit(self._run_analyst_agent, query)
                futures[future] = "analyst"
            
            if "geo" in agents and self.geo_agent:
                country = self._extract_country_from_query(query)
                future = executor.submit(self._run_geo_agent, country)
                futures[future] = "geo"
            
            # Collect results
            for future in as_completed(futures):
                agent_name = futures[future]
                try:
                    result = future.result(timeout=120)
                    results[agent_name] = result
                    print(f"✓ {agent_name.capitalize()}Agent completed")
                    self.logger.info(f"{agent_name.capitalize()}Agent completed successfully")
                except Exception as e:
                    error_msg = f"Error in {agent_name}Agent: {str(e)}"
                    results[agent_name] = {"error": error_msg}
                    print(f"✗ {agent_name.capitalize()}Agent failed: {e}")
                    self.logger.error(error_msg, exc_info=True)
        
        return results
    
    def _run_search_agent(self, query: str) -> Dict[str, Any]:
        """Run SearchAgent and format results."""
        try:
            search_results = self.search_agent.intelligent_search(query)
            return {
                "type": "search",
                "content": search_results,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"SearchAgent execution failed: {e}")
            return {
                "type": "search",
                "error": str(e),
                "status": "failed"
            }
    
    def _run_analyst_agent(self, query: str) -> Dict[str, Any]:
        """Run AnalystAgent and format results."""
        try:
            analyst_results = self.analyst_agent.analyze_query(query)
            return {
                "type": "analyst",
                "content": analyst_results,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"AnalystAgent execution failed: {e}")
            return {
                "type": "analyst",
                "error": str(e),
                "status": "failed"
            }
    
    def _run_geo_agent(self, country: str) -> Dict[str, Any]:
        """Run GeoAgent and format results."""
        try:
            geo_results = self.geo_agent.analyze_country(country, years_back=3)
            return {
                "type": "geo",
                "content": geo_results,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"GeoAgent execution failed: {e}")
            return {
                "type": "geo",
                "error": str(e),
                "status": "failed"
            }
    
    def _synthesize_results(self, query: str, results: Dict[str, Any]) -> str:
        """
        Synthesize multi-agent results into cohesive intelligence brief.
        
        Args:
            query: Original query
            results: Dictionary of agent results
            
        Returns:
            Synthesized intelligence brief
        """
        try:
            # Prepare context for LLM
            context_parts = []
            
            for agent_name, result in results.items():
                if result.get("status") == "success":
                    context_parts.append(f"\n--- {agent_name.upper()} RESULTS ---")
                    
                    content = result.get("content", {})
                    if isinstance(content, dict):
                        # Truncate for LLM context window
                        content_str = json.dumps(content, indent=2)[:3000]
                        context_parts.append(content_str)
                    else:
                        context_parts.append(str(content)[:3000])
            
            combined_context = "\n".join(context_parts)
            
            # Create synthesis prompt
            synthesis_prompt = f"""You are an intelligence analyst synthesizing information from multiple sources.

Query: {query}

Multi-source intelligence data:
{combined_context[:8000]}

Create a comprehensive intelligence brief with the following structure:

1. EXECUTIVE SUMMARY
   - 2-3 sentence overview of key findings

2. KEY FINDINGS
   - Main insights from the analysis
   - Important patterns or trends

3. GEOSPATIAL ANALYSIS (if available)
   - Geographic distribution
   - Hotspot locations

4. TEMPORAL ANALYSIS (if available)
   - Trends over time
   - Escalation patterns

5. IMPLICATIONS
   - Strategic implications
   - Risk factors
   - Regional stability concerns

6. RECOMMENDATIONS
   - Actionable next steps
   - Areas requiring monitoring

Keep the brief clear, actionable, and evidence-based. Focus on synthesis, not repetition."""
            
            # Generate synthesis
            synthesis = self.llm.invoke(synthesis_prompt)
            
            # Apply redaction/summarization if needed
            if self.redactor_agent and len(synthesis) > 5000:
                synthesis = self.redactor_agent.create_summary(synthesis, style="professional")
            
            return synthesis
            
        except Exception as e:
            self.logger.error(f"Synthesis failed: {e}", exc_info=True)
            return f"Synthesis unavailable due to error: {str(e)}"
    
    def _save_report(self, report: Dict[str, Any]) -> str:
        """
        Save report to JSON file.
        
        Args:
            report: Report dictionary
            
        Returns:
            Path to saved report
        """
        # Create analysis directory
        analysis_dir = Path("data/analysis")
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.json"
        filepath = analysis_dir / filename
        
        # Save JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved to: {filepath}")
        
        return str(filepath)


def main():
    """CLI interface for SupervisorAgent."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="HAWK-AI SupervisorAgent - Central orchestration for multi-agent intelligence",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "query",
        type=str,
        help="Analysis query to process"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="magistral:latest",
        help="Ollama model for synthesis"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize and run supervisor
        supervisor = SupervisorAgent(model=args.model)
        report = supervisor.run(args.query)
        
        # Display summary
        print("\n" + "="*80)
        print("INTELLIGENCE BRIEF SUMMARY")
        print("="*80)
        print(report.get("summary", "No summary available"))
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
