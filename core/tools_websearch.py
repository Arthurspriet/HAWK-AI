"""
HAWK-AI Web Search Tools
========================
Provides reliable, local-friendly web search via DuckDuckGo with caching and vectorization support.

Features:
- DuckDuckGo web search with result caching
- Local FAISS vectorization using Ollama embeddings
- CLI test mode for quick queries
- Persistent storage under data/web_cache/ and data/vector_index/

Dependencies:
- duckduckgo-search
- faiss-cpu
- langchain-ollama
- tqdm
"""

import json
import logging
import os
import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import hashlib

import numpy as np
from tqdm import tqdm

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Error: duckduckgo-search not installed. Run: pip install duckduckgo-search")
    sys.exit(1)

try:
    import faiss
except ImportError:
    print("Error: faiss not installed. Run: pip install faiss-cpu")
    sys.exit(1)

try:
    from langchain_ollama import OllamaEmbeddings
except ImportError:
    print("Error: langchain-ollama not installed. Run: pip install langchain-ollama")
    sys.exit(1)


# Configure logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "websearch.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "data" / "web_cache"
VECTOR_INDEX_DIR = BASE_DIR / "data" / "vector_index"

# Create directories
CACHE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Ollama configuration
OLLAMA_MODEL = "snowflake-arctic-embed2:568m"
OLLAMA_BASE_URL = "http://127.0.0.1:11434"


def _get_cache_key(query: str, max_results: int) -> str:
    """Generate a unique cache key for a query."""
    key_string = f"{query}_{max_results}"
    return hashlib.md5(key_string.encode()).hexdigest()


def _load_from_cache(cache_key: str) -> Optional[List[Dict]]:
    """Load search results from cache if available."""
    cache_file = CACHE_DIR / f"{cache_key}.pkl"
    
    if cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                logger.info(f"Loaded results from cache: {cache_key}")
                return cached_data
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_key}: {e}")
            return None
    return None


def _save_to_cache(cache_key: str, results: List[Dict]) -> None:
    """Save search results to cache."""
    cache_file = CACHE_DIR / f"{cache_key}.pkl"
    
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(results, f)
        logger.info(f"Saved {len(results)} results to cache: {cache_key}")
    except Exception as e:
        logger.error(f"Failed to save to cache {cache_key}: {e}")


def smart_search(query: str, max_results: int = 20, use_cache: bool = True) -> List[Dict[str, str]]:
    """
    Perform a web search using DuckDuckGo with optional caching.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 20)
        use_cache: Whether to use cached results if available (default: True)
    
    Returns:
        List of dictionaries containing {title, body, href} for each result
        
    Example:
        >>> results = smart_search("AI safety research", max_results=10)
        >>> for result in results:
        ...     print(result['title'], result['href'])
    """
    logger.info(f"Searching for: '{query}' (max_results={max_results})")
    
    # Check cache first
    if use_cache:
        cache_key = _get_cache_key(query, max_results)
        cached_results = _load_from_cache(cache_key)
        if cached_results:
            return cached_results
    
    # Perform search
    results = []
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                keywords=query,
                max_results=max_results,
                backend="api"
            )
            
            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'body': result.get('body', ''),
                    'href': result.get('href', '')
                })
        
        logger.info(f"Retrieved {len(results)} results from DuckDuckGo")
        
        # Save to cache
        if use_cache and results:
            cache_key = _get_cache_key(query, max_results)
            _save_to_cache(cache_key, results)
        
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []


def vectorize_results(
    results: List[Dict[str, str]],
    query: Optional[str] = None,
    index_name: str = "web_index"
) -> Tuple[Optional[faiss.Index], Optional[List[Dict]]]:
    """
    Vectorize search results using Ollama embeddings and save to FAISS index.
    
    Args:
        results: List of search result dictionaries from smart_search()
        query: Optional query string for context
        index_name: Name for the FAISS index file (default: "web_index")
    
    Returns:
        Tuple of (faiss_index, indexed_results) or (None, None) if failed
        
    Example:
        >>> results = smart_search("machine learning")
        >>> index, indexed_results = vectorize_results(results, query="machine learning")
    """
    if not results:
        logger.warning("No results to vectorize")
        return None, None
    
    logger.info(f"Vectorizing {len(results)} results using {OLLAMA_MODEL}")
    
    try:
        # Initialize embeddings
        embeddings = OllamaEmbeddings(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        
        # Prepare texts for embedding
        texts = []
        for result in results:
            # Combine title and body for richer embeddings
            text = f"{result['title']}\n{result['body']}"
            texts.append(text)
        
        # Generate embeddings with progress bar
        logger.info("Generating embeddings...")
        embeddings_list = []
        
        for text in tqdm(texts, desc="Embedding documents", disable=len(texts) < 5):
            try:
                embedding = embeddings.embed_query(text)
                embeddings_list.append(embedding)
            except Exception as e:
                logger.error(f"Failed to embed text: {e}")
                # Use zero vector as fallback
                embeddings_list.append([0.0] * 768)  # Assuming 768 dimensions
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings_list, dtype='float32')
        dimension = embeddings_array.shape[1]
        
        logger.info(f"Created embeddings with dimension: {dimension}")
        
        # Create FAISS index
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)
        
        logger.info(f"Added {index.ntotal} vectors to FAISS index")
        
        # Save index and metadata
        index_path = VECTOR_INDEX_DIR / f"{index_name}.faiss"
        metadata_path = VECTOR_INDEX_DIR / f"{index_name}_metadata.pkl"
        
        faiss.write_index(index, str(index_path))
        logger.info(f"Saved FAISS index to {index_path}")
        
        # Save metadata
        metadata = {
            'results': results,
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'dimension': dimension,
            'num_vectors': index.ntotal
        }
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        logger.info(f"Saved metadata to {metadata_path}")
        
        return index, results
        
    except Exception as e:
        logger.error(f"Vectorization failed: {e}")
        return None, None


def load_vector_index(index_name: str = "web_index") -> Tuple[Optional[faiss.Index], Optional[Dict]]:
    """
    Load a previously saved FAISS index and its metadata.
    
    Args:
        index_name: Name of the index to load
    
    Returns:
        Tuple of (faiss_index, metadata) or (None, None) if not found
    """
    index_path = VECTOR_INDEX_DIR / f"{index_name}.faiss"
    metadata_path = VECTOR_INDEX_DIR / f"{index_name}_metadata.pkl"
    
    if not index_path.exists() or not metadata_path.exists():
        logger.warning(f"Index '{index_name}' not found")
        return None, None
    
    try:
        index = faiss.read_index(str(index_path))
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        logger.info(f"Loaded index '{index_name}' with {index.ntotal} vectors")
        return index, metadata
        
    except Exception as e:
        logger.error(f"Failed to load index '{index_name}': {e}")
        return None, None


def find_most_relevant(
    query: str,
    results: List[Dict[str, str]],
    top_k: int = 3
) -> List[Dict[str, str]]:
    """
    Find the most relevant results for a query using vector similarity.
    
    Args:
        query: Query string to compare against
        results: List of search results
        top_k: Number of top results to return
    
    Returns:
        List of top-k most relevant results
    """
    if not results:
        return []
    
    try:
        embeddings = OllamaEmbeddings(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        
        # Embed query
        query_embedding = embeddings.embed_query(query)
        query_vector = np.array([query_embedding], dtype='float32')
        
        # Embed all results
        texts = [f"{r['title']}\n{r['body']}" for r in results]
        result_embeddings = []
        
        for text in texts:
            try:
                emb = embeddings.embed_query(text)
                result_embeddings.append(emb)
            except:
                # Fallback to zero vector
                result_embeddings.append([0.0] * len(query_embedding))
        
        result_vectors = np.array(result_embeddings, dtype='float32')
        
        # Create temporary index
        dimension = query_vector.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(result_vectors)
        
        # Search for top-k
        distances, indices = index.search(query_vector, min(top_k, len(results)))
        
        # Return top results
        top_results = [results[i] for i in indices[0]]
        return top_results
        
    except Exception as e:
        logger.error(f"Failed to find most relevant: {e}")
        # Fallback: return first k results
        return results[:top_k]


def main():
    """CLI test mode for web search."""
    if len(sys.argv) < 2:
        print("Usage: python core/tools_websearch.py <query>")
        print('Example: python core/tools_websearch.py "conflict escalation in Sudan 2024"')
        sys.exit(1)
    
    query = sys.argv[1]
    
    print(f"\n{'='*80}")
    print(f"HAWK-AI Web Search: {query}")
    print(f"{'='*80}\n")
    
    # Perform search
    print("🔍 Searching DuckDuckGo...")
    results = smart_search(query, max_results=20)
    
    if not results:
        print("❌ No results found")
        return
    
    print(f"✅ Found {len(results)} results\n")
    
    # Display all results
    print(f"\n{'─'*80}")
    print("All Results:")
    print(f"{'─'*80}\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['href']}")
        print(f"   {result['body'][:150]}...")
        print()
    
    # Vectorize and find most relevant
    print(f"\n{'─'*80}")
    print("🧠 Vectorizing and finding top-3 most relevant...")
    print(f"{'─'*80}\n")
    
    top_results = find_most_relevant(query, results, top_k=3)
    
    if top_results:
        print("⭐ Top 3 Most Relevant Results:\n")
        for i, result in enumerate(top_results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['href']}")
            print(f"   {result['body'][:200]}...")
            print()
        
        # Save vectorized results
        print("💾 Saving vectorized index...")
        index, indexed_results = vectorize_results(results, query=query)
        if index:
            print(f"✅ Saved {index.ntotal} vectors to data/vector_index/web_index.faiss")
    
    print(f"\n{'='*80}")
    print(f"✅ Search complete! Check logs/websearch.log for details")
    print(f"{'='*80}\n")


class WebSearchTool:
    """
    Wrapper class for search_agent.py compatibility.
    Provides object-oriented interface to web search functions.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize web search tool.
        
        Args:
            config_path: Optional path to config file (for future use)
        """
        self.config_path = config_path
        logger.info("WebSearchTool initialized")
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Perform web search (compatible with search_agent.py).
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of dicts with keys: url, title, snippet (body)
        """
        results = smart_search(query, max_results=max_results)
        
        # Normalize keys for compatibility (body -> snippet, href -> url)
        normalized = []
        for r in results:
            normalized.append({
                'url': r.get('href', ''),
                'title': r.get('title', ''),
                'snippet': r.get('body', '')
            })
        
        return normalized
    
    def get_news(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Search for news articles (uses DuckDuckGo news).
        
        Args:
            query: News search query
            max_results: Maximum results to return
            
        Returns:
            List of news articles with url, title, body, date, source
        """
        try:
            with DDGS() as ddgs:
                news_results = ddgs.news(
                    keywords=query,
                    max_results=max_results
                )
                
                results = []
                for article in news_results:
                    results.append({
                        'url': article.get('url', ''),
                        'title': article.get('title', ''),
                        'body': article.get('body', ''),
                        'date': article.get('date', 'N/A'),
                        'source': article.get('source', 'Unknown')
                    })
                
                logger.info(f"Retrieved {len(results)} news articles for: {query}")
                return results
                
        except Exception as e:
            logger.error(f"News search failed: {e}")
            return []
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dict with status, content, title, length
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else 'No title'
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            logger.info(f"Scraped {len(text)} characters from {url}")
            
            return {
                'status': 'success',
                'content': text,
                'title': title,
                'length': len(text),
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'content': '',
                'title': '',
                'length': 0,
                'url': url
            }


def get_websearch_tool(config_path: Optional[str] = None) -> WebSearchTool:
    """
    Factory function to create a WebSearchTool instance.
    Compatible with search_agent.py interface.
    
    Args:
        config_path: Optional configuration file path
        
    Returns:
        WebSearchTool instance
        
    Example:
        >>> search_tool = get_websearch_tool()
        >>> results = search_tool.search("AI research", max_results=5)
    """
    return WebSearchTool(config_path)


if __name__ == "__main__":
    main()
