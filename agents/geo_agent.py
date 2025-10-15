"""
GeoAgent: Geospatial Reasoning Agent for HAWK-AI
Controls geospatial reasoning capabilities using ACLED data, 
clustering algorithms, and interactive map generation.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

from langchain_ollama import OllamaLLM

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tools_geospatial import (
    load_acled_subset,
    cluster_events,
    make_hotspot_map
)
from core.config_loader import get_model


class GeoAgent:
    """
    Geospatial reasoning agent for analyzing conflict patterns and hotspots.
    
    Uses Ollama LLM for spatial reasoning and ACLED data for conflict analysis.
    Generates interactive maps showing event clusters and hotspots.
    """
    
    def __init__(
        self,
        model: str = None,
        base_url: str = "http://127.0.0.1:11434",
        log_file: str = "logs/geo_agent.log"
    ):
        """
        Initialize the GeoAgent.
        
        Args:
            model: Ollama model name for spatial reasoning (overrides config)
            base_url: Base URL for Ollama API
            log_file: Path to log file
        """
        # Load model from config or use provided model
        self.model = model if model else get_model("geo", "magistral:latest")
        
        # Initialize LLM with error handling
        try:
            self.llm = OllamaLLM(model=self.model, base_url=base_url)
        except Exception as e:
            logging.error(f"Model {self.model} not found. Run: ollama pull {self.model}")
            raise
        
        # Setup logging
        self.logger = logging.getLogger("GeoAgent")
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add handlers if not already present
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        self.logger.info(f"🗺️  GeoAgent initialized with model: {self.model}")
    
    def analyze_country(
        self,
        country: str,
        years_back: int = 3,
        eps_km: float = 50.0,
        min_samples: int = 5,
        output_dir: str = "data/maps"
    ) -> Dict[str, any]:
        """
        Analyze conflict patterns for a specific country.
        
        Loads ACLED data, performs spatial clustering, generates an LLM summary,
        and creates an interactive hotspot map.
        
        Args:
            country: Country name (e.g., "Sudan", "Nigeria")
            years_back: Number of years to analyze (default: 3)
            eps_km: Maximum distance in km for clustering (default: 50)
            min_samples: Minimum samples per cluster (default: 5)
            output_dir: Directory to save generated maps
            
        Returns:
            Dict containing:
                - country: Country name
                - years_analyzed: Years back analyzed
                - n_events: Total number of events
                - n_clusters: Number of identified clusters
                - summary: LLM-generated spatial analysis
                - map_path: Path to generated map file
                - total_fatalities: Total fatalities in the period
                
        Raises:
            ValueError: If no data found for the country
            FileNotFoundError: If ACLED data files are missing
        """
        import time
        start = time.time()
        self.logger.info(
            f"Starting analysis for {country} (last {years_back} years)"
        )
        
        try:
            # Step 1: Load ACLED data
            self.logger.info(f"Loading ACLED data for {country}...")
            df = load_acled_subset(country=country, years_back=years_back)
            
            if len(df) == 0:
                raise ValueError(
                    f"No events found for {country} in the last {years_back} years"
                )
            
            # Step 2: Cluster events
            self.logger.info(f"Clustering {len(df)} events...")
            df = cluster_events(df, eps_km=eps_km, min_samples=min_samples)
            
            # Step 3: Generate LLM summary
            self.logger.info("Generating spatial reasoning summary...")
            
            # Calculate statistics for the prompt
            n_clusters = len(df[df['cluster'] != -1]['cluster'].unique())
            total_fatalities = int(df['FATALITIES'].sum())
            top_event_types = df['EVENT_TYPE'].value_counts().head(3).to_dict()
            
            summary_prompt = f"""Provide a concise geospatial analysis of conflict distribution in {country} over the last {years_back} years.

Key statistics:
- Total events: {len(df)}
- Identified clusters: {n_clusters}
- Total fatalities: {total_fatalities}
- Top event types: {', '.join([f'{k} ({v})' for k, v in top_event_types.items()])}

Focus on:
1. Geographic distribution patterns
2. Hotspot locations and intensity
3. Implications for regional stability

Keep the analysis brief (3-4 sentences) and actionable."""
            
            try:
                reasoning = self.llm.invoke(summary_prompt)
            except Exception as e:
                self.logger.error(f"LLM invocation failed: {e}")
                reasoning = (
                    f"Analysis based on {len(df)} events across {n_clusters} "
                    f"geographic clusters with {total_fatalities} total fatalities. "
                    f"Primary event types: {', '.join(list(top_event_types.keys())[:3])}."
                )
            
            # Step 4: Generate hotspot map
            self.logger.info("Generating interactive map...")
            output_path = f"{output_dir}/{country.replace(' ', '_')}_hotspot.html"
            map_info = make_hotspot_map(
                df,
                output_path=output_path,
                title=f"Conflict Hotspots: {country} ({years_back}Y)"
            )
            
            # Compile results
            result = {
                'country': country,
                'years_analyzed': years_back,
                'n_events': len(df),
                'n_clusters': n_clusters,
                'summary': reasoning,
                'map_path': map_info['path'],
                'total_fatalities': total_fatalities
            }
            
            duration = round(time.time() - start, 2)
            self.logger.info(f"🗺️  GeoAgent finished in {duration}s using {self.model}")
            return result
            
        except FileNotFoundError as e:
            self.logger.error(f"Data file not found: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Value error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            raise
    
    def batch_analyze(
        self,
        countries: list,
        years_back: int = 3
    ) -> Dict[str, Dict]:
        """
        Analyze multiple countries in batch.
        
        Args:
            countries: List of country names
            years_back: Number of years to analyze
            
        Returns:
            Dict mapping country names to analysis results
        """
        self.logger.info(f"Starting batch analysis for {len(countries)} countries")
        
        results = {}
        for country in countries:
            try:
                result = self.analyze_country(country, years_back=years_back)
                results[country] = result
            except Exception as e:
                self.logger.error(f"Failed to analyze {country}: {e}")
                results[country] = {'error': str(e)}
        
        self.logger.info(f"Batch analysis complete: {len(results)} countries processed")
        return results


def main():
    """
    CLI entry point for GeoAgent.
    
    Example usage:
        python agents/geo_agent.py --country Sudan --years 3
        python agents/geo_agent.py --country "South Sudan" --years 5 --model llama3:8b
    """
    parser = argparse.ArgumentParser(
        description='GeoAgent: Analyze conflict patterns and generate hotspot maps',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--country',
        type=str,
        required=True,
        help='Country name to analyze (e.g., "Sudan", "Nigeria")'
    )
    
    parser.add_argument(
        '--years',
        type=int,
        default=3,
        help='Number of years back to analyze'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='qwen3-embedding:8b',
        help='Ollama model for spatial reasoning'
    )
    
    parser.add_argument(
        '--eps-km',
        type=float,
        default=50.0,
        help='Maximum distance (km) for event clustering'
    )
    
    parser.add_argument(
        '--min-samples',
        type=int,
        default=5,
        help='Minimum samples per cluster'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/maps',
        help='Directory for generated maps'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='logs/geo_agent.log',
        help='Path to log file'
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    try:
        agent = GeoAgent(model=args.model, log_file=args.log_file)
        
        # Run analysis
        result = agent.analyze_country(
            country=args.country,
            years_back=args.years,
            eps_km=args.eps_km,
            min_samples=args.min_samples,
            output_dir=args.output_dir
        )
        
        # Print results
        print("\n" + "="*70)
        print(f"GEOSPATIAL ANALYSIS: {result['country']}")
        print("="*70)
        print(f"\nPeriod: Last {result['years_analyzed']} years")
        print(f"Events: {result['n_events']}")
        print(f"Clusters: {result['n_clusters']}")
        print(f"Total Fatalities: {result['total_fatalities']}")
        print(f"\n{result['summary']}")
        print(f"\nMap generated: {result['map_path']}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

