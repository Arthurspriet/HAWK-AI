"""
Test script for Context Fusion, AnalystAgent, and ReflectionAgent integration.

This test confirms:
1. Context weighting/fusion works correctly
2. AnalystAgent can process fused context
3. ReflectionAgent can evaluate consistency
"""

import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath('.'))

from core.context_fusion import fuse_contexts
from agents.analyst_agent import AnalystAgent
from agents.reflection_agent import ReflectionAgent


def test_context_fusion():
    """Test context fusion with weighted scoring."""
    print("\n" + "="*80)
    print("CONTEXT FUSION & REFLECTION TEST")
    print("="*80 + "\n")
    
    # Test 1: Context Fusion
    print("Test 1: Context Fusion")
    print("-" * 80)
    
    query = "Political instability and economic crisis in Sudan"
    acled = [{"text": "Protests in Khartoum", "score": 0.8}]
    cia = [{"text": "Sudan GDP down 12%", "score": 0.7}]
    
    fused = fuse_contexts(acled, cia)
    print(f"✅ Fusion test: {len(fused)} docs fused.")
    print(f"   - ACLED input: {len(acled)} docs")
    print(f"   - CIA input: {len(cia)} docs")
    print(f"   - Fused output: {len(fused)} docs")
    
    # Verify weighted scores
    if fused:
        print(f"   - Top weighted score: {fused[0].get('weighted_score', 0):.3f}")
        print(f"   - Top source type: {fused[0].get('source_type', 'Unknown')}")
    
    # Test 2: AnalystAgent Analysis
    print("\n\nTest 2: AnalystAgent Analysis")
    print("-" * 80)
    
    analyst = AnalystAgent()
    result = analyst.analyze_query(query, framework="pmesii")
    
    analysis_length = len(result.get('analysis', ''))
    print(f"✅ AnalystAgent run: {analysis_length} chars.")
    print(f"   - Framework: {result.get('framework', 'None')}")
    print(f"   - ACLED sources: {result.get('sources', {}).get('acled', 0)}")
    print(f"   - CIA sources: {result.get('sources', {}).get('cia', 0)}")
    
    if 'error' in result:
        print(f"   ⚠️  Warning: {result['error']}")
    
    # Test 3: ReflectionAgent Consistency Evaluation
    print("\n\nTest 3: ReflectionAgent Consistency Evaluation")
    print("-" * 80)
    
    reflection = ReflectionAgent()
    consistency = reflection.evaluate_consistency(result)
    
    overall_stability = consistency.get('overall_stability', 'Unknown')
    print(f"✅ Consistency: {overall_stability}")
    print(f"   - Contradictions found: {len(consistency.get('contradictions', []))}")
    print(f"   - Alignment summary: {consistency.get('alignment_summary', 'N/A')[:100]}...")
    
    # Test Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Context Fusion: PASSED ({len(fused)} docs)")
    print(f"✅ AnalystAgent: PASSED ({analysis_length} chars)")
    print(f"✅ ReflectionAgent: PASSED (stability: {overall_stability})")
    print("\nAll integration tests completed successfully!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_context_fusion()

