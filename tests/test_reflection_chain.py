"""
Test script to verify reflection workflow and memory persistence.
"""

import json
import sys
import os

sys.path.append(os.path.abspath('.'))

from agents.supervisor_agent import SupervisorAgent
from core.memory_manager import load_memory


def test_reflection_chain():
    """Test the reflection workflow and memory persistence."""
    query = "Conflict escalation and hotspots in Sudan 2022–2025"
    
    print(f"Running query: {query}")
    print("-" * 80)
    
    # Initialize supervisor agent and run query
    sa = SupervisorAgent()
    report = sa.run(query)
    
    # Verify reflection exists in results
    assert "reflection" in report["results"], "Reflection missing"
    
    # Extract and display confidence
    conf = report["results"]["reflection"]["confidence"]
    print(f"✅ Reflection confidence: {conf}")
    
    # Load and verify memory persistence
    memory = load_memory()
    print(f"✅ Memory entries: {len(memory)} | Last query: {memory[-1]['query']}")
    
    print("✅ Reflection chain operational")
    
    return report


if __name__ == "__main__":
    try:
        report = test_reflection_chain()
        print("\n" + "=" * 80)
        print("TEST PASSED: Reflection chain working correctly")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

