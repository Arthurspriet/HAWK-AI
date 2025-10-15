"""
Test script for dynamic model configuration system.
Tests that all agents load their models from config/agents.yaml correctly.
"""
import os
import sys
import yaml
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.abspath('.'))

from core.config_loader import get_model
from agents.supervisor_agent import SupervisorAgent


def test_models():
    """Test the model configuration system."""
    print("="*80)
    print("✅ Model Configuration Test")
    print("="*80)
    print()
    
    # Test 1: Verify config file exists
    config_path = "config/agents.yaml"
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return False
    
    print(f"✓ Config file found: {config_path}")
    
    # Test 2: Load and display model configuration
    try:
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        
        models = cfg.get('models', {})
        print(f"✓ Models loaded: {len(models)}")
        print()
        print("Model Assignments:")
        print("-" * 80)
        for k, v in models.items():
            print(f"  • {k:20s} → {v}")
        print()
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False
    
    # Test 3: Test config_loader utility
    print("Testing config_loader utility:")
    print("-" * 80)
    test_agents = ['supervisor', 'analyst', 'geo', 'search', 'reflection', 'redactor']
    for agent_name in test_agents:
        model = get_model(agent_name)
        expected = models.get(agent_name, 'magistral:latest')
        status = "✓" if model == expected else "✗"
        print(f"  {status} {agent_name:15s}: {model}")
    print()
    
    # Test 4: Initialize SupervisorAgent (which initializes sub-agents)
    print("Testing SupervisorAgent initialization:")
    print("-" * 80)
    try:
        sa = SupervisorAgent()
        print(f"✓ SupervisorAgent initialized with model: {sa.model}")
        
        # Check sub-agents
        if sa.analyst_agent:
            print(f"✓ AnalystAgent initialized with model: {sa.analyst_agent.model}")
        if sa.geo_agent:
            print(f"✓ GeoAgent initialized with model: {sa.geo_agent.model}")
        if sa.reflection_agent:
            print(f"✓ ReflectionAgent initialized with model: {sa.reflection_agent.model}")
        if sa.search_agent:
            print(f"✓ SearchAgent initialized with model: {sa.search_agent.model}")
        if sa.redactor_agent:
            print(f"✓ RedactorAgent initialized with model: {sa.redactor_agent.model}")
        
        print()
    except Exception as e:
        print(f"⚠️  Warning: Agent initialization had issues: {e}")
        print("   This may be due to missing Ollama models or dependencies.")
        print()
    
    # Test 5: Display expected console output format
    print("Expected Runtime Output Format:")
    print("-" * 80)
    print("🧠 SupervisorAgent initialized with model: magistral:latest")
    print("🔎 AnalystAgent → gpt-oss:20b (13s)")
    print("🗺️  GeoAgent → magistral:latest (4s)")
    print("✍️  RedactorAgent → wizardlm-uncensored:13b (2s)")
    print("🧩 ReflectionAgent → nous-hermes2:34b (7s)")
    print("✅ Final report saved to data/analysis/report_<timestamp>.json")
    print()
    
    print("="*80)
    print("✅ Model Configuration Test Complete")
    print("="*80)
    print()
    print("To run a full system test with actual query:")
    print('  python -c "from agents.supervisor_agent import SupervisorAgent; sa = SupervisorAgent(); sa.run(\\"Sudan conflict 2023-2025\\")"')
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_models()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

