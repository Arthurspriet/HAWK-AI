"""
Context Enricher for HAWK-AI
Fuses historical FAISS intelligence with current web context for analytical agents.
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.vector_store import VectorStore
from core.tools_websearch import WebSearchTool

# Configure logging
logger = logging.getLogger("ContextEnricher")


def get_historical_context(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve historical context from FAISS vector store.
    
    Args:
        query: Search query for historical context
        top_k: Number of top results to retrieve
        
    Returns:
        List of historical context documents with metadata and scores
    """
    try:
        logger.info(f"Retrieving historical context for: {query}")
        vector_store = VectorStore()
        results = vector_store.search(query, top_k=top_k)
        logger.info(f"Retrieved {len(results)} historical documents")
        return results
    except Exception as e:
        logger.error(f"Failed to retrieve historical context: {e}")
        return []


def get_web_context(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve current web context using web search.
    
    Args:
        query: Search query for web content
        max_results: Maximum number of web results to retrieve
        
    Returns:
        List of web search results with title, url, and snippet
    """
    try:
        logger.info(f"Retrieving web context for: {query}")
        web_tool = WebSearchTool()
        results = web_tool.search(query, max_results=max_results)
        logger.info(f"Retrieved {len(results)} web results")
        return results
    except Exception as e:
        logger.error(f"Failed to retrieve web context: {e}")
        return []


def merge_contexts(historical: List[Dict[str, Any]], web: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge historical and web contexts into a unified enriched context.
    
    Args:
        historical: Historical context from FAISS vector store
        web: Web search results
        
    Returns:
        Enriched context dictionary with both historical and current information
    """
    try:
        logger.info(f"Merging {len(historical)} historical + {len(web)} web contexts")
        
        enriched = {
            "historical_context": {
                "count": len(historical),
                "sources": [],
                "summary": []
            },
            "web_context": {
                "count": len(web),
                "sources": [],
                "summary": []
            },
            "metadata": {
                "total_sources": len(historical) + len(web),
                "historical_weight": len(historical) / (len(historical) + len(web)) if (len(historical) + len(web)) > 0 else 0,
                "web_weight": len(web) / (len(historical) + len(web)) if (len(historical) + len(web)) > 0 else 0
            }
        }
        
        # Process historical context
        for hist in historical:
            doc = hist.get("document", "")
            meta = hist.get("metadata", {})
            score = hist.get("score", 0.0)
            
            enriched["historical_context"]["sources"].append({
                "source": meta.get("source", "Unknown"),
                "country": meta.get("country", ""),
                "event_type": meta.get("event_type", ""),
                "event_date": meta.get("event_date", ""),
                "relevance_score": score
            })
            
            enriched["historical_context"]["summary"].append({
                "text": doc[:500],  # Truncate for summary
                "score": score
            })
        
        # Process web context
        for web_item in web:
            enriched["web_context"]["sources"].append({
                "title": web_item.get("title", ""),
                "url": web_item.get("url", ""),
                "snippet": web_item.get("snippet", "")[:300]  # Truncate for summary
            })
            
            enriched["web_context"]["summary"].append({
                "title": web_item.get("title", ""),
                "snippet": web_item.get("snippet", "")[:200]
            })
        
        logger.info("Successfully merged contexts")
        return enriched
        
    except Exception as e:
        logger.error(f"Failed to merge contexts: {e}")
        return {
            "historical_context": {"count": 0, "sources": [], "summary": []},
            "web_context": {"count": 0, "sources": [], "summary": []},
            "metadata": {"total_sources": 0, "historical_weight": 0, "web_weight": 0},
            "error": str(e)
        }

