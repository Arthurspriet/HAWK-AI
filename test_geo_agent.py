"""
Test script for GeoAgent - demonstrates programmatic usage.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.geo_agent import GeoAgent


def test_single_country():
    """Test single country analysis."""
    print("\n" + "="*70)
    print("TEST 1: Single Country Analysis")
    print("="*70)
    
    agent = GeoAgent(model="llama3:8b")
    
    try:
        result = agent.analyze_country(
            country="Kenya",
            years_back=2
        )
        
        print(f"\n✓ Country: {result['country']}")
        print(f"✓ Events analyzed: {result['n_events']}")
        print(f"✓ Clusters identified: {result['n_clusters']}")
        print(f"✓ Total fatalities: {result['total_fatalities']}")
        print(f"✓ Map saved to: {result['map_path']}")
        print(f"\nSummary:\n{result['summary']}")
        
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_batch_analysis():
    """Test batch country analysis."""
    print("\n" + "="*70)
    print("TEST 2: Batch Country Analysis")
    print("="*70)
    
    agent = GeoAgent(model="llama3:8b")
    
    countries = ["Somalia", "Ethiopia"]
    
    try:
        results = agent.batch_analyze(
            countries=countries,
            years_back=2
        )
        
        print(f"\n✓ Analyzed {len(results)} countries")
        
        for country, result in results.items():
            if 'error' in result:
                print(f"\n✗ {country}: {result['error']}")
            else:
                print(f"\n✓ {country}:")
                print(f"  - Events: {result['n_events']}")
                print(f"  - Clusters: {result['n_clusters']}")
                print(f"  - Fatalities: {result['total_fatalities']}")
                print(f"  - Map: {result['map_path']}")
        
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_error_handling():
    """Test error handling with invalid country."""
    print("\n" + "="*70)
    print("TEST 3: Error Handling")
    print("="*70)
    
    agent = GeoAgent(model="llama3:8b")
    
    try:
        result = agent.analyze_country(
            country="InvalidCountryName",
            years_back=2
        )
        print("\n✗ Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"\n✓ Correctly raised ValueError: {e}")
        return True
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("GEOAGENT PROGRAMMATIC USAGE TESTS")
    print("="*70)
    
    results = []
    
    # Test 1: Single country
    results.append(("Single Country Analysis", test_single_country()))
    
    # Test 2: Batch analysis
    results.append(("Batch Analysis", test_batch_analysis()))
    
    # Test 3: Error handling
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*70 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

