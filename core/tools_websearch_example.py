"""
Example usage of tools_websearch module
========================================
This file demonstrates how to use the HAWK-AI web search tools programmatically.
"""

from tools_websearch import smart_search, vectorize_results, find_most_relevant, load_vector_index
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


def example_basic_search():
    """Example: Basic web search with caching"""
    print("\n" + "="*80)
    print("Example 1: Basic Web Search")
    print("="*80 + "\n")
    
    query = "artificial intelligence safety research"
    results = smart_search(query, max_results=10)
    
    print(f"Found {len(results)} results for: '{query}'\n")
    
    for i, result in enumerate(results[:3], 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['href']}")
        print(f"   {result['body'][:100]}...\n")


def example_vectorize_and_search():
    """Example: Vectorize results and find most relevant"""
    print("\n" + "="*80)
    print("Example 2: Vectorize and Find Most Relevant")
    print("="*80 + "\n")
    
    query = "climate change impact on agriculture"
    
    # Search
    results = smart_search(query, max_results=15)
    print(f"Retrieved {len(results)} results")
    
    # Find most relevant using embeddings
    print("\nFinding top-3 most relevant results...\n")
    top_results = find_most_relevant(query, results, top_k=3)
    
    for i, result in enumerate(top_results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['href']}\n")
    
    # Vectorize and save to FAISS
    print("Saving to FAISS index...")
    index, indexed_results = vectorize_results(results, query=query, index_name="example_index")
    
    if index:
        print(f"✅ Saved {index.ntotal} vectors to FAISS index")


def example_load_index():
    """Example: Load a previously saved index"""
    print("\n" + "="*80)
    print("Example 3: Load Saved Index")
    print("="*80 + "\n")
    
    index, metadata = load_vector_index("web_index")
    
    if index:
        print(f"✅ Loaded index with {index.ntotal} vectors")
        print(f"   Original query: {metadata.get('query', 'N/A')}")
        print(f"   Timestamp: {metadata.get('timestamp', 'N/A')}")
        print(f"   Number of results: {len(metadata.get('results', []))}")
    else:
        print("❌ No saved index found")


def example_cached_search():
    """Example: Demonstrate caching"""
    print("\n" + "="*80)
    print("Example 4: Caching Demonstration")
    print("="*80 + "\n")
    
    query = "quantum computing applications"
    
    print("First search (will hit DuckDuckGo)...")
    results1 = smart_search(query, max_results=5, use_cache=True)
    
    print("\nSecond search (will use cache)...")
    results2 = smart_search(query, max_results=5, use_cache=True)
    
    print(f"\n✅ Both searches returned {len(results1)} results")
    print("Check the logs - second search was much faster!")


if __name__ == "__main__":
    # Run all examples
    # Uncomment the ones you want to try
    
    # example_basic_search()
    # example_vectorize_and_search()
    example_load_index()
    # example_cached_search()

