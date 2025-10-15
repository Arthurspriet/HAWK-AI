"""
Analyst Agent for HAWK-AI.
Fuses historical FAISS intelligence with current web context for analytical reasoning.
"""
import logging
import json
import sys
from pathlib import Path
from typing import Dict, Any

from langchain_ollama import OllamaLLM
from core.context_enricher import get_historical_context, get_web_context, merge_contexts

# Configure logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "analyst_agent.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)


class AnalystAgent:
    """Agent that fuses historical and web intelligence for analytical reasoning."""
    
    def __init__(self, model: str = "gpt-oss:20b"):
        """
        Initialize AnalystAgent.
        
        Args:
            model: Ollama model name (default: gpt-oss:20b)
        """
        self.llm = OllamaLLM(model=model, base_url="http://127.0.0.1:11434")
        self.logger = logging.getLogger("AnalystAgent")
        self.logger.info(f"AnalystAgent initialized with model: {model}")
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query by fusing historical and web context.
        
        Args:
            query: Analytical query to process
            
        Returns:
            Dictionary containing query, structured_context, and analysis
        """
        self.logger.info(f"Analyzing query: {query}")
        
        try:
            # Retrieve historical context from FAISS
            self.logger.info("Retrieving historical context...")
            hist = get_historical_context(query)
            
            # Retrieve web context
            self.logger.info("Retrieving web context...")
            web = get_web_context(query)
            
            # Merge contexts
            self.logger.info("Merging contexts...")
            enriched = merge_contexts(hist, web)
            
            # Create interpretation prompt
            interpretation_prompt = f"""Provide an analytical brief on: {query}

Use the enriched JSON context below. Add temporal and political nuance.

ENRICHED CONTEXT:
{json.dumps(enriched, indent=2)}

Provide:
1. Executive Summary
2. Historical Patterns (based on FAISS data)
3. Current Developments (based on web data)
4. Temporal Analysis (trends over time)
5. Political and Strategic Implications
6. Key Risk Factors

Be analytical, specific, and evidence-based."""
            
            # Generate analysis using LLM
            self.logger.info("Generating LLM analysis...")
            response = self.llm.invoke(interpretation_prompt)
            
            self.logger.info("Analysis completed successfully")
            
            return {
                "query": query,
                "structured_context": enriched,
                "analysis": response
            }
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {
                "query": query,
                "structured_context": {},
                "analysis": f"Error: Analysis failed - {str(e)}",
                "error": str(e)
            }


def main():
    """CLI interface for AnalystAgent."""
    if len(sys.argv) < 2:
        print("Usage: python agents/analyst_agent.py \"<query>\"")
        print('Example: python agents/analyst_agent.py "Conflict escalation in Sudan 2022–2025"')
        sys.exit(1)
    
    query = sys.argv[1]
    
    print(f"\n{'='*80}")
    print(f"HAWK-AI Analyst Agent")
    print(f"{'='*80}\n")
    print(f"Query: {query}\n")
    
    # Initialize agent
    print("Initializing agent...")
    agent = AnalystAgent()
    
    # Perform analysis
    print("\nPerforming analysis...\n")
    result = agent.analyze_query(query)
    
    # Display results
    print(f"\n{'='*80}")
    print("ANALYTICAL BRIEF")
    print(f"{'='*80}\n")
    
    # Display structured context summary
    context = result.get("structured_context", {})
    hist_count = context.get("historical_context", {}).get("count", 0)
    web_count = context.get("web_context", {}).get("count", 0)
    
    print(f"Context Sources:")
    print(f"  • Historical: {hist_count} documents")
    print(f"  • Web: {web_count} results")
    print(f"  • Total: {hist_count + web_count} sources\n")
    
    # Display historical sources summary
    if hist_count > 0:
        print("Historical Context:")
        hist_sources = context.get("historical_context", {}).get("sources", [])
        for i, src in enumerate(hist_sources[:3], 1):  # Show top 3
            print(f"  {i}. {src.get('source', 'Unknown')} - {src.get('country', '')} "
                  f"({src.get('event_type', '')}) - Score: {src.get('relevance_score', 0):.3f}")
        print()
    
    # Display web sources summary
    if web_count > 0:
        print("Web Context:")
        web_sources = context.get("web_context", {}).get("sources", [])
        for i, src in enumerate(web_sources[:3], 1):  # Show top 3
            print(f"  {i}. {src.get('title', 'Untitled')}")
            print(f"     {src.get('url', '')}")
        print()
    
    # Display analysis
    print(f"{'─'*80}")
    print("ANALYSIS:")
    print(f"{'─'*80}\n")
    print(result.get("analysis", "No analysis available"))
    
    print(f"\n{'='*80}")
    print(f"Analysis complete! Full log available in: {LOG_FILE}")
    print(f"{'='*80}\n")
    
    # Output JSON for programmatic consumption
    print("\nJSON OUTPUT (for SupervisorAgent):")
    print(json.dumps({
        "query": result.get("query"),
        "context_summary": {
            "historical_count": hist_count,
            "web_count": web_count,
            "total_sources": hist_count + web_count
        },
        "analysis": result.get("analysis"),
        "status": "error" if "error" in result else "success"
    }, indent=2))


if __name__ == "__main__":
    main()
