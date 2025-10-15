#!/usr/bin/env python3
"""
HAWK-AI Comprehensive Test Suite
==================================
Validates the functional chain: tools → agents → combined reasoning

Tests:
1. Geospatial tools (load_acled_subset, cluster_events, make_hotspot_map)
2. Context enricher (get_historical_context, get_web_context, merge_contexts)
3. GeoAgent (analyze_country)
4. AnalystAgent (analyze_query)
5. Agent chain (combined reasoning)

Usage:
    python tests/run_all_tests.py
"""

import sys
import json
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Callable

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Warning: python-dotenv not installed. Env vars may not load properly.")

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Ensure required directories exist
def setup_directories():
    """Create necessary directories if they don't exist."""
    dirs = [
        Path("data/maps"),
        Path("data/analysis"),
        Path("logs"),
        Path("tests")
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)


# Test result tracking
class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.duration = 0.0
        self.error = None
        self.output = None


class TestRunner:
    def __init__(self):
        self.results = []
        self.start_time = None
        
    def run_test(self, test_func: Callable, name: str, icon: str) -> TestResult:
        """Run a single test function and capture results."""
        result = TestResult(name)
        
        print(f"{icon} {name} ", end="", flush=True)
        dots_printed = 0
        
        start = time.time()
        try:
            # Run the test
            output = test_func()
            result.passed = True
            result.output = output
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
            result.output = traceback.format_exc()
            
        finally:
            result.duration = time.time() - start
            
        # Print result
        padding = max(1, 40 - len(name) - dots_printed * 4)
        print("." * padding, end=" ")
        
        if result.passed:
            print(f"{Colors.OKGREEN}✅ OK{Colors.ENDC} ({result.duration:.1f}s)")
        else:
            print(f"{Colors.FAIL}❌ FAILED{Colors.ENDC} ({result.duration:.1f}s)")
            print(f"{Colors.FAIL}   Error: {result.error}{Colors.ENDC}")
            
        return result
    
    def print_summary(self):
        """Print summary table of all test results."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total_time = sum(r.duration for r in self.results)
        
        print("\n" + "="*70)
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
        print("="*70)
        
        for result in self.results:
            status = f"{Colors.OKGREEN}✅ PASS{Colors.ENDC}" if result.passed else f"{Colors.FAIL}❌ FAIL{Colors.ENDC}"
            print(f"{result.name:.<50} {status} ({result.duration:.1f}s)")
        
        print("="*70)
        
        if failed == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✅ ALL TESTS PASSED{Colors.ENDC} ({total_time:.1f}s total)")
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}❌ {failed}/{len(self.results)} TESTS FAILED{Colors.ENDC} ({total_time:.1f}s total)")
        
        print("="*70 + "\n")
        
        return failed == 0
    
    def save_log(self):
        """Save test summary to log file."""
        log_path = Path("logs/test_summary.log")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_path, "a") as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"HAWK-AI Test Run: {timestamp}\n")
            f.write(f"{'='*70}\n\n")
            
            for result in self.results:
                status = "PASS" if result.passed else "FAIL"
                f.write(f"{result.name}: {status} ({result.duration:.1f}s)\n")
                if not result.passed:
                    f.write(f"  Error: {result.error}\n")
                    f.write(f"  Traceback:\n")
                    for line in result.output.split('\n'):
                        f.write(f"    {line}\n")
                f.write("\n")
            
            passed = sum(1 for r in self.results if r.passed)
            total = len(self.results)
            f.write(f"Result: {passed}/{total} tests passed\n")
            f.write(f"{'='*70}\n\n")


# ============================================================================
# TEST 1: Geospatial Tools
# ============================================================================

def test_geospatial_tools() -> Dict[str, Any]:
    """Test geospatial tools: load_acled_subset, cluster_events, make_hotspot_map."""
    from core.tools_geospatial import load_acled_subset, cluster_events, make_hotspot_map
    
    # Load ACLED data for Sudan
    df = load_acled_subset(country="Sudan", years_back=3)
    assert not df.empty, "ACLED data is empty"
    assert len(df) > 0, "No events loaded"
    
    # Cluster events
    df = cluster_events(df)
    assert "cluster" in df.columns, "Missing cluster column"
    
    # Check for valid clusters
    n_clusters = len(df[df['cluster'] != -1]['cluster'].unique())
    
    # Generate hotspot map
    map_info = make_hotspot_map(df, output_path="data/maps/Sudan_hotspot.html")
    assert map_info["n_events"] > 0, "No events plotted"
    assert Path(map_info["path"]).exists(), "Map file not created"
    
    result = {
        "events_loaded": len(df),
        "clusters_found": n_clusters,
        "map_path": map_info["path"],
        "total_fatalities": map_info.get("total_fatalities", 0)
    }
    
    # Save result
    with open("data/analysis/test_geospatial.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n   → {result['events_loaded']} events, {result['clusters_found']} clusters")
    print(f"   → Map: {result['map_path']}")
    
    return result


# ============================================================================
# TEST 2: Context Enricher Tools
# ============================================================================

def test_context_enricher_tools() -> Dict[str, Any]:
    """Test context enricher: get_historical_context, get_web_context, merge_contexts."""
    from core.context_enricher import get_historical_context, get_web_context, merge_contexts
    
    query = "Conflict escalation in Sudan since 2022"
    
    # Get historical context
    hist = get_historical_context(query, top_k=3)
    assert isinstance(hist, list), "Historical context not a list"
    
    # Get web context
    web = get_web_context(query, max_results=5)
    assert isinstance(web, list), "Web context not a list"
    
    # Merge contexts
    merged = merge_contexts(hist, web)
    assert isinstance(merged, dict), "merge_contexts did not return a dict"
    assert "historical_context" in merged, "Missing 'historical_context'"
    assert "web_context" in merged, "Missing 'web_context'"
    assert "metadata" in merged, "Missing 'metadata'"
    
    result = {
        "query": query,
        "historical_count": len(hist),
        "web_count": len(web),
        "total_sources": merged["metadata"]["total_sources"],
        "merged_structure": list(merged.keys())
    }
    
    # Save result
    with open("data/analysis/test_context_enricher.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n   → Historical: {result['historical_count']}, Web: {result['web_count']}")
    print(f"   → Total sources: {result['total_sources']}")
    
    return result


# ============================================================================
# TEST 3: GeoAgent
# ============================================================================

def test_geo_agent() -> Dict[str, Any]:
    """Test GeoAgent: analyze_country."""
    from agents.geo_agent import GeoAgent
    
    # Initialize agent
    agent = GeoAgent(model="qwen3-embedding:8b")
    
    # Run analysis
    result = agent.analyze_country("Sudan", years_back=3)
    
    # Validate results
    assert "map_path" in result, "GeoAgent missing map_path"
    assert "summary" in result, "GeoAgent missing summary"
    assert "n_events" in result, "GeoAgent missing n_events"
    assert "n_clusters" in result, "GeoAgent missing n_clusters"
    assert result["n_events"] > 0, "No events in GeoAgent result"
    
    # Check map exists
    assert Path(result["map_path"]).exists(), "GeoAgent map file not created"
    
    # Save result
    output = {
        "country": result["country"],
        "years_analyzed": result["years_analyzed"],
        "n_events": result["n_events"],
        "n_clusters": result["n_clusters"],
        "total_fatalities": result.get("total_fatalities", 0),
        "map_path": result["map_path"],
        "summary": result["summary"][:200] + "..." if len(result["summary"]) > 200 else result["summary"]
    }
    
    with open("data/analysis/test_geo_agent.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n   → {result['n_events']} events, {result['n_clusters']} clusters")
    print(f"   → Map: {result['map_path']}")
    
    return output


# ============================================================================
# TEST 4: AnalystAgent
# ============================================================================

def test_analyst_agent() -> Dict[str, Any]:
    """Test AnalystAgent: analyze_query."""
    from agents.analyst_agent import AnalystAgent
    
    # Initialize agent
    agent = AnalystAgent(model="gpt-oss:20b")
    
    # Run analysis
    result = agent.analyze_query("Conflict escalation in Sudan since 2022")
    
    # Validate results
    assert "structured_context" in result, "AnalystAgent missing structured_context"
    assert "analysis" in result, "AnalystAgent missing analysis"
    assert "query" in result, "AnalystAgent missing query"
    
    ctx = result["structured_context"]
    assert isinstance(ctx, dict), "structured_context is not a dict"
    
    # Check context has data
    hist_count = ctx.get("historical_context", {}).get("count", 0)
    web_count = ctx.get("web_context", {}).get("count", 0)
    
    # Check analysis is substantial
    analysis = result["analysis"]
    assert isinstance(analysis, str), "Analysis is not a string"
    assert len(analysis) > 50, f"Analysis too short ({len(analysis)} chars)"
    
    # Save result
    output = {
        "query": result["query"],
        "historical_sources": hist_count,
        "web_sources": web_count,
        "total_sources": hist_count + web_count,
        "analysis_length": len(analysis),
        "analysis_preview": analysis[:300] + "..." if len(analysis) > 300 else analysis
    }
    
    with open("data/analysis/test_analyst_agent.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n   → Sources: {hist_count} historical + {web_count} web")
    print(f"   → Analysis: {len(analysis)} chars")
    
    return output


# ============================================================================
# TEST 5: Agent Chain (Combined Reasoning)
# ============================================================================

def test_agent_chain() -> Dict[str, Any]:
    """Test combined agent chain: AnalystAgent + GeoAgent."""
    from agents.analyst_agent import AnalystAgent
    from agents.geo_agent import GeoAgent
    
    # Initialize both agents
    analyst = AnalystAgent(model="gpt-oss:20b")
    geo = GeoAgent(model="qwen3-embedding:8b")
    
    # Run analyst analysis
    ares = analyst.analyze_query("Conflict escalation in Sudan 2022–2025")
    assert "structured_context" in ares, "Missing structured_context from AnalystAgent"
    assert "analysis" in ares, "Missing analysis from AnalystAgent"
    
    # Run geo analysis
    gres = geo.analyze_country("Sudan", years_back=3)
    assert "map_path" in gres, "GeoAgent missing map_path output"
    assert "summary" in gres, "GeoAgent missing summary"
    
    # Validate integration
    assert Path(gres["map_path"]).exists(), "Geo map file not created"
    
    # Save combined result
    combined = {
        "query": ares["query"],
        "analyst": {
            "historical_sources": ares["structured_context"].get("historical_context", {}).get("count", 0),
            "web_sources": ares["structured_context"].get("web_context", {}).get("count", 0),
            "analysis_length": len(ares["analysis"])
        },
        "geo": {
            "country": gres["country"],
            "n_events": gres["n_events"],
            "n_clusters": gres["n_clusters"],
            "map_path": gres["map_path"]
        },
        "integration_status": "success"
    }
    
    with open("data/analysis/test_agent_chain.json", "w") as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n   → Analyst: {combined['analyst']['historical_sources']} hist + {combined['analyst']['web_sources']} web sources")
    print(f"   → Geo: {combined['geo']['n_events']} events, {combined['geo']['n_clusters']} clusters")
    print(f"   → Map: {combined['geo']['map_path']}")
    
    return combined


# ============================================================================
# MAIN RUNNER
# ============================================================================

def main():
    """Main test runner."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("="*70)
    print("HAWK-AI TEST SUITE")
    print("="*70)
    print(f"{Colors.ENDC}\n")
    
    # Setup
    print(f"{Colors.OKCYAN}Setting up test environment...{Colors.ENDC}")
    setup_directories()
    print(f"{Colors.OKGREEN}✓ Directories created{Colors.ENDC}\n")
    
    # Initialize test runner
    runner = TestRunner()
    
    print(f"{Colors.BOLD}Running tests:{Colors.ENDC}\n")
    print("-"*70)
    
    # Run all tests
    tests = [
        (test_geospatial_tools, "test_geospatial_tools", "🧭"),
        (test_context_enricher_tools, "test_context_enricher", "🧠"),
        (test_geo_agent, "test_geo_agent", "🌍"),
        (test_analyst_agent, "test_analyst_agent", "📊"),
        (test_agent_chain, "test_agent_chain", "🔄"),
    ]
    
    for test_func, name, icon in tests:
        result = runner.run_test(test_func, name, icon)
        runner.results.append(result)
        
        # Stop on first failure if critical
        if not result.passed:
            print(f"\n{Colors.WARNING}⚠️  Test failed. Continuing with remaining tests...{Colors.ENDC}\n")
    
    print("-"*70)
    
    # Print summary
    all_passed = runner.print_summary()
    
    # Save log
    runner.save_log()
    print(f"{Colors.OKCYAN}📝 Test log saved to: logs/test_summary.log{Colors.ENDC}")
    
    # Print detailed errors if any
    failed_tests = [r for r in runner.results if not r.passed]
    if failed_tests:
        print(f"\n{Colors.FAIL}{Colors.BOLD}DETAILED ERROR INFORMATION:{Colors.ENDC}\n")
        for result in failed_tests:
            print(f"{Colors.FAIL}{'='*70}")
            print(f"FAILED TEST: {result.name}")
            print(f"{'='*70}{Colors.ENDC}")
            print(result.output)
            print()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

