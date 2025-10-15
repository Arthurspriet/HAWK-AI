"""
Search Agent for HAWK-AI.
Performs web searches and retrieves online information.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from rich.console import Console

from core.tools_websearch import get_websearch_tool
from core.local_tracking import get_tracker
from core.ollama_client import get_ollama_client

console = Console()


class SearchAgent:
    """Agent for web search operations."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize search agent."""
        self.config_path = config_path
        self.search_tool = get_websearch_tool(config_path)
        self.tracker = get_tracker(config_path)
        self.ollama_client = get_ollama_client(config_path)
        
        console.print("[green]Search Agent initialized[/green]")
    
    def search_and_report(self, query: str, max_results: int = 5) -> str:
        """
        Search the web and create a report.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Formatted search report
        """
        start_time = datetime.now()
        self.tracker.log_agent_start("search", query)
        
        try:
            # Perform search
            results = self.search_tool.search(query, max_results)
            
            if not results:
                return "No search results found."
            
            # Log the search
            self.tracker.log_tool_call(
                "search",
                "web_search",
                {"query": query, "max_results": max_results},
                f"Found {len(results)} results"
            )
            
            # Format results
            report = self._format_search_results(query, results)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.tracker.log_agent_end("search", report, duration)
            
            return report
            
        except Exception as e:
            console.print(f"[red]Search agent error: {e}[/red]")
            self.tracker.log_error("search", e)
            return f"Error performing search: {str(e)}"
    
    def search_news(self, query: str, max_results: int = 5) -> str:
        """
        Search for news articles.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Formatted news report
        """
        start_time = datetime.now()
        self.tracker.log_agent_start("search", f"News: {query}")
        
        try:
            # Perform news search
            results = self.search_tool.get_news(query, max_results)
            
            if not results:
                return "No news results found."
            
            # Log the search
            self.tracker.log_tool_call(
                "search",
                "news_search",
                {"query": query, "max_results": max_results},
                f"Found {len(results)} news results"
            )
            
            # Format results
            report = self._format_news_results(query, results)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.tracker.log_agent_end("search", report, duration)
            
            return report
            
        except Exception as e:
            console.print(f"[red]Search agent error: {e}[/red]")
            self.tracker.log_error("search", e)
            return f"Error performing news search: {str(e)}"
    
    def scrape_and_analyze(self, url: str) -> str:
        """
        Scrape a URL and analyze its content.
        
        Args:
            url: URL to scrape
            
        Returns:
            Analysis of the scraped content
        """
        try:
            console.print(f"[cyan]Scraping URL: {url}[/cyan]")
            
            # Scrape the URL
            scraped_data = self.search_tool.scrape_url(url)
            
            if scraped_data['status'] != 'success':
                return f"Failed to scrape URL: {scraped_data.get('error', 'Unknown error')}"
            
            # Log the scrape
            self.tracker.log_tool_call(
                "search",
                "scrape_url",
                {"url": url},
                f"Scraped {scraped_data['length']} characters"
            )
            
            # Create summary of content
            content = scraped_data['content']
            summary = f"Title: {scraped_data['title']}\n"
            summary += f"URL: {url}\n"
            summary += f"Content Length: {scraped_data['length']} characters\n\n"
            summary += f"Content Preview:\n{content[:500]}..."
            
            return summary
            
        except Exception as e:
            console.print(f"[red]Scraping error: {e}[/red]")
            return f"Error scraping URL: {str(e)}"
    
    def _format_search_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a readable report.
        
        Args:
            query: Original query
            results: List of search results
            
        Returns:
            Formatted report
        """
        report_parts = [
            f"WEB SEARCH RESULTS FOR: {query}",
            f"Found {len(results)} results\n",
            "=" * 80
        ]
        
        for i, result in enumerate(results, 1):
            report_parts.append(f"\n{i}. {result['title']}")
            report_parts.append(f"   URL: {result['url']}")
            report_parts.append(f"   {result['snippet']}")
        
        report_parts.append("\n" + "=" * 80)
        
        return "\n".join(report_parts)
    
    def _format_news_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Format news results into a readable report.
        
        Args:
            query: Original query
            results: List of news results
            
        Returns:
            Formatted report
        """
        report_parts = [
            f"NEWS SEARCH RESULTS FOR: {query}",
            f"Found {len(results)} news articles\n",
            "=" * 80
        ]
        
        for i, result in enumerate(results, 1):
            report_parts.append(f"\n{i}. {result['title']}")
            report_parts.append(f"   Source: {result.get('source', 'Unknown')}")
            report_parts.append(f"   Date: {result.get('date', 'N/A')}")
            report_parts.append(f"   URL: {result['url']}")
            report_parts.append(f"   {result.get('body', '')}")
        
        report_parts.append("\n" + "=" * 80)
        
        return "\n".join(report_parts)
    
    def intelligent_search(self, query: str) -> str:
        """
        Perform an intelligent search with LLM-enhanced query reformulation.
        
        Args:
            query: Original query
            
        Returns:
            Search results with intelligent analysis
        """
        try:
            console.print("[cyan]Performing intelligent search...[/cyan]")
            
            # Reformulate query for better results
            reformulation_prompt = f"""Given this user query: "{query}"
            
Generate 2-3 optimized search queries that would find the most relevant information. Return only the queries, one per line."""
            
            reformulated = self.ollama_client.generate(reformulation_prompt)
            search_queries = [q.strip() for q in reformulated.split('\n') if q.strip()][:3]
            
            console.print(f"[cyan]Generated {len(search_queries)} search variations[/cyan]")
            
            # Perform multiple searches
            all_results = []
            for sq in search_queries:
                results = self.search_tool.search(sq, max_results=3)
                all_results.extend(results)
            
            # Deduplicate by URL
            seen_urls = set()
            unique_results = []
            for result in all_results:
                if result['url'] not in seen_urls:
                    seen_urls.add(result['url'])
                    unique_results.append(result)
            
            # Format and return
            return self._format_search_results(query, unique_results[:10])
            
        except Exception as e:
            console.print(f"[red]Intelligent search error: {e}[/red]")
            # Fallback to regular search
            return self.search_and_report(query)

