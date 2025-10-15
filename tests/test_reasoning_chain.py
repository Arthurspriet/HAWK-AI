"""
Test script to run a full reasoning chain and display thinking steps.
Demonstrates the AnalystAgent's transparent multi-step reasoning process.
"""

import sys
import os
import json

sys.path.append(os.path.abspath('.'))

from agents.analyst_agent import AnalystAgent
from tools.reasoning_viewer import show_reasoning_cli


def test_reasoning_chain():
    """Run a full reasoning chain and display results."""
    query = "Explain the causes of political instability in Sudan since 2022"
    
    print(f"🚀 Starting HAWK-AI reasoning chain...")
    print(f"📝 Query: {query}")
    print("=" * 80)
    print()
    
    # Initialize agent and run analysis
    agent = AnalystAgent()
    result = agent.analyze_query(query, framework="pmesii")
    
    # Confirm completion
    print("✅ Analyst reasoning completed. Displaying thinking steps:\n")
    print("=" * 80)
    
    # Display reasoning chain
    show_reasoning_cli()
    
    return result


if __name__ == "__main__":
    try:
        result = test_reasoning_chain()
        print("\n" + "=" * 80)
        print("✅ TEST PASSED: Reasoning chain completed successfully")
        print(f"📊 Runtime: {result['runtime_s']}s")
        print(f"📊 Model: {result['model']}")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

