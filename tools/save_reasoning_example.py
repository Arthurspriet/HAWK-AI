#!/usr/bin/env python3
"""
Example of how to save reasoning chains for viewing with reasoning_viewer.py

This demonstrates how to integrate reasoning chain saving into your HAWK-AI agents.
"""

import json
import time
from datetime import datetime
from pathlib import Path


def save_reasoning_chain(
    query: str,
    model: str,
    patterns: str,
    hypotheses: str,
    evaluation: str,
    synthesis: str,
    review: str,
    runtime_s: float,
    output_path: str = "data/analysis/last_reasoning.json"
):
    """
    Save a reasoning chain to JSON for viewing with reasoning_viewer.py
    
    Args:
        query: The original query/question
        model: The model name used for reasoning
        patterns: Pattern recognition output
        hypotheses: Hypothesis formation output
        evaluation: Hypothesis evaluation output
        synthesis: Synthesis/integration output
        review: Quality review output
        runtime_s: Total runtime in seconds
        output_path: Where to save the reasoning chain (default: last_reasoning.json)
    """
    reasoning_data = {
        "query": query,
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "runtime_s": round(runtime_s, 2),
        "patterns": patterns,
        "hypotheses": hypotheses,
        "evaluation": evaluation,
        "synthesis": synthesis,
        "review": review
    }
    
    # Ensure directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(reasoning_data, f, indent=2)
    
    print(f"✅ Reasoning chain saved to: {output_path}")
    print(f"   View with: python3 tools/reasoning_viewer.py")
    print(f"   Or: make reasoning")


def example_agent_integration():
    """
    Example showing how to integrate reasoning chain saving into an agent.
    """
    print("🔄 Running example agent analysis...")
    start_time = time.time()
    
    # Simulate agent processing
    query = "What are the key security risks in the Sahel region?"
    model = "nous-hermes2:34b"
    
    # Step 1: Pattern Recognition
    print("  📊 Analyzing patterns...")
    time.sleep(0.5)  # Simulate processing
    patterns = """
Pattern Recognition Analysis:

1. **Increasing Violence**: ACLED data shows 45% increase in violent events
   across Burkina Faso, Mali, and Niger in the past 18 months.

2. **Jihadist Expansion**: JNIM and ISGS territorial control expanding,
   particularly in tri-border area (Liptako-Gourma).

3. **State Fragility**: Military coups in Mali (2021), Burkina Faso (2022),
   and Niger (2023) indicate regional governance crisis.

4. **Humanitarian Crisis**: 5.2M displaced persons across the region,
   with food insecurity affecting 30M people.

5. **Foreign Military Withdrawal**: French and UN forces withdrawing,
   creating security vacuum.
"""
    
    # Step 2: Hypothesis Formation
    print("  💡 Forming hypotheses...")
    time.sleep(0.5)
    hypotheses = """
Hypothesis Generation:

**H1: Regional State Collapse Risk**
The combination of military coups, jihadist expansion, and foreign military
withdrawal suggests high risk of complete state failure in at least one
Sahel country within 12 months.

**H2: Jihadist Consolidation**
JNIM and ISGS may consolidate control over larger territories, potentially
declaring "emirates" or autonomous zones.

**H3: Humanitarian Catastrophe**
Displacement and food insecurity trends suggest a major humanitarian crisis
requiring massive international intervention.

**H4: Regional Spillover**
Instability may spread to coastal West African states (Ghana, Benin, Togo)
as jihadist groups expand southward.
"""
    
    # Step 3: Evaluation
    print("  ⚖️ Evaluating hypotheses...")
    time.sleep(0.5)
    evaluation = """
Hypothesis Evaluation:

**H1 (State Collapse) - HIGH CONFIDENCE (0.78)**
Supporting: Three coups in 2 years, declining state capacity
Supporting: Jihadist groups controlling 30-40% of some territories
Contradicting: Regional organizations (ECOWAS) providing support
Assessment: Very high risk, particularly in Burkina Faso

**H2 (Jihadist Consolidation) - MEDIUM-HIGH CONFIDENCE (0.70)**
Supporting: Territorial gains in recent operations
Supporting: Inter-group coordination improving
Contradicting: Internal divisions, competing local interests
Assessment: Possible but not certain; depends on state response

**H3 (Humanitarian Crisis) - VERY HIGH CONFIDENCE (0.92)**
Supporting: WFP emergency warnings, displacement velocity
Supporting: Climate factors (Sahel drought continuing)
Assessment: Already occurring; escalation nearly certain

**H4 (Regional Spillover) - MEDIUM CONFIDENCE (0.62)**
Supporting: Attacks already occurring in northern Ghana/Benin
Contradicting: Coastal states have stronger security forces
Assessment: Risk exists but containment possible with resources
"""
    
    # Step 4: Synthesis
    print("  🔗 Synthesizing analysis...")
    time.sleep(0.5)
    synthesis = """
Integrated Analysis:

The Sahel region faces an acute multi-dimensional crisis requiring urgent
international attention:

**Security Dimension**: The combination of state fragility (military coups),
jihadist expansion (JNIM/ISGS territorial gains), and foreign military
withdrawal creates a dangerous power vacuum. Burkina Faso is particularly
at risk of state failure.

**Humanitarian Dimension**: 5.2M displaced and 30M food insecure represent
one of the world's most severe humanitarian emergencies. Climate factors
(drought) compound the crisis.

**Regional Stability**: While full regional collapse is unlikely, spillover
to coastal states is a significant risk. Ghana and Benin already experiencing
cross-border attacks.

**Strategic Implications**: 
- Russian Wagner Group filling Western military withdrawal
- Chinese economic influence increasing
- Regional organizations (ECOWAS, AU) lack resources for effective response

**Critical Timeframe**: Next 6-12 months are decisive for preventing
full state collapse in Burkina Faso and massive humanitarian catastrophe.
"""
    
    # Step 5: Review
    print("  ✅ Conducting quality review...")
    time.sleep(0.5)
    review = """
Quality Assurance Review:

✅ **Strengths**:
- Multi-source data integration (ACLED, WFP, UNHCR)
- Regional context well-captured
- Confidence levels appropriately assigned
- Timeline projections realistic

⚠️ **Limitations**:
- Limited real-time intelligence (ACLED lag ~2 weeks)
- Wagner Group activities not fully analyzed
- Economic impacts under-explored
- Ethnic/tribal dynamics need deeper analysis

🔄 **Recommendations for Enhancement**:
1. Integrate Wagner Group/Russian influence analysis
2. Add economic indicators (trade, remittances, inflation)
3. Include local reporting from Sahel media sources
4. Conduct scenario modeling for 3/6/12 month projections

**Confidence in Analysis**: MEDIUM-HIGH (0.75)
Analysis provides solid strategic overview but would benefit from
additional real-time intelligence and economic data.

**Actionability**: HIGH - Clear implications for policy and humanitarian
planning with specific timeframes and risk factors identified.
"""
    
    runtime = time.time() - start_time
    
    # Save the reasoning chain
    save_reasoning_chain(
        query=query,
        model=model,
        patterns=patterns,
        hypotheses=hypotheses,
        evaluation=evaluation,
        synthesis=synthesis,
        review=review,
        runtime_s=runtime
    )
    
    print(f"\n✨ Analysis complete in {runtime:.2f}s")
    print("\n🧠 View the reasoning chain with:")
    print("   make reasoning          # CLI view")
    print("   make reasoning-ui       # Streamlit web UI")


if __name__ == "__main__":
    example_agent_integration()

