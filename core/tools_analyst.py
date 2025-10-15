"""
Analysis tools for HAWK-AI.
Provides data analysis, pattern detection, and contextual reasoning capabilities.
"""
from typing import Dict, Any, Optional, List
import yaml
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
from rich.console import Console

console = Console()


class AnalystTool:
    """Tool for analytical operations."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize analyst tool."""
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def analyze_temporal_patterns(self, events: List[Dict[str, Any]], date_field: str = 'event_date') -> Dict[str, Any]:
        """
        Analyze temporal patterns in event data.
        
        Args:
            events: List of event dictionaries
            date_field: Name of the date field
            
        Returns:
            Dictionary with temporal analysis results
        """
        console.print("[cyan]Analyzing temporal patterns...[/cyan]")
        
        if not events:
            return {"error": "No events provided"}
        
        # Extract dates
        dates = []
        for event in events:
            if date_field in event:
                try:
                    date_str = str(event[date_field])
                    # Try to parse date
                    date = pd.to_datetime(date_str, errors='coerce')
                    if pd.notna(date):
                        dates.append(date)
                except:
                    pass
        
        if not dates:
            return {"error": "No valid dates found"}
        
        dates_series = pd.Series(dates)
        
        analysis = {
            "total_events": len(events),
            "date_range": {
                "start": str(dates_series.min()),
                "end": str(dates_series.max()),
                "span_days": (dates_series.max() - dates_series.min()).days
            },
            "frequency": {
                "daily_average": len(dates) / max((dates_series.max() - dates_series.min()).days, 1),
                "monthly_counts": dates_series.dt.to_period('M').value_counts().to_dict()
            }
        }
        
        console.print(f"[green]Analyzed {len(dates)} dated events[/green]")
        return analysis
    
    def analyze_geographic_distribution(self, events: List[Dict[str, Any]], location_field: str = 'country') -> Dict[str, Any]:
        """
        Analyze geographic distribution of events.
        
        Args:
            events: List of event dictionaries
            location_field: Name of the location field
            
        Returns:
            Dictionary with geographic analysis results
        """
        console.print("[cyan]Analyzing geographic distribution...[/cyan]")
        
        if not events:
            return {"error": "No events provided"}
        
        locations = [event.get(location_field, 'Unknown') for event in events]
        location_counts = Counter(locations)
        
        total = len(locations)
        
        analysis = {
            "total_events": total,
            "unique_locations": len(location_counts),
            "top_locations": dict(location_counts.most_common(10)),
            "distribution": {
                loc: {
                    "count": count,
                    "percentage": round(count / total * 100, 2)
                }
                for loc, count in location_counts.most_common(10)
            }
        }
        
        console.print(f"[green]Analyzed {total} events across {len(location_counts)} locations[/green]")
        return analysis
    
    def analyze_event_types(self, events: List[Dict[str, Any]], type_field: str = 'event_type') -> Dict[str, Any]:
        """
        Analyze distribution of event types.
        
        Args:
            events: List of event dictionaries
            type_field: Name of the event type field
            
        Returns:
            Dictionary with event type analysis results
        """
        console.print("[cyan]Analyzing event types...[/cyan]")
        
        if not events:
            return {"error": "No events provided"}
        
        event_types = [event.get(type_field, 'Unknown') for event in events]
        type_counts = Counter(event_types)
        
        total = len(event_types)
        
        analysis = {
            "total_events": total,
            "unique_types": len(type_counts),
            "type_distribution": {
                etype: {
                    "count": count,
                    "percentage": round(count / total * 100, 2)
                }
                for etype, count in type_counts.most_common()
            }
        }
        
        console.print(f"[green]Analyzed {total} events of {len(type_counts)} types[/green]")
        return analysis
    
    def detect_escalation_patterns(self, events: List[Dict[str, Any]], fatality_field: str = 'fatalities') -> Dict[str, Any]:
        """
        Detect escalation patterns in event data.
        
        Args:
            events: List of event dictionaries
            fatality_field: Name of the fatalities field
            
        Returns:
            Dictionary with escalation analysis results
        """
        console.print("[cyan]Detecting escalation patterns...[/cyan]")
        
        if not events:
            return {"error": "No events provided"}
        
        fatalities = []
        for event in events:
            if fatality_field in event:
                try:
                    fat = float(event[fatality_field])
                    if not np.isnan(fat):
                        fatalities.append(fat)
                except:
                    pass
        
        if not fatalities:
            return {"warning": "No fatality data available"}
        
        fatalities_array = np.array(fatalities)
        
        analysis = {
            "total_events": len(events),
            "events_with_fatalities": len([f for f in fatalities if f > 0]),
            "fatality_statistics": {
                "total": float(np.sum(fatalities_array)),
                "mean": float(np.mean(fatalities_array)),
                "median": float(np.median(fatalities_array)),
                "max": float(np.max(fatalities_array)),
                "std": float(np.std(fatalities_array))
            },
            "severity_categories": {
                "low (0)": len([f for f in fatalities if f == 0]),
                "moderate (1-10)": len([f for f in fatalities if 0 < f <= 10]),
                "high (11-50)": len([f for f in fatalities if 10 < f <= 50]),
                "severe (>50)": len([f for f in fatalities if f > 50])
            }
        }
        
        console.print(f"[green]Analyzed fatality data for {len(fatalities)} events[/green]")
        return analysis
    
    def compare_time_periods(self, events: List[Dict[str, Any]], date_field: str = 'event_date', split_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare metrics between two time periods.
        
        Args:
            events: List of event dictionaries
            date_field: Name of the date field
            split_date: Date to split periods (defaults to midpoint)
            
        Returns:
            Dictionary with comparison results
        """
        console.print("[cyan]Comparing time periods...[/cyan]")
        
        if not events:
            return {"error": "No events provided"}
        
        # Parse dates
        dated_events = []
        for event in events:
            if date_field in event:
                try:
                    date = pd.to_datetime(str(event[date_field]), errors='coerce')
                    if pd.notna(date):
                        dated_events.append({**event, 'parsed_date': date})
                except:
                    pass
        
        if not dated_events:
            return {"error": "No valid dates found"}
        
        # Determine split date
        if split_date:
            split = pd.to_datetime(split_date)
        else:
            dates = [e['parsed_date'] for e in dated_events]
            split = pd.Series(dates).median()
        
        # Split events
        period1 = [e for e in dated_events if e['parsed_date'] < split]
        period2 = [e for e in dated_events if e['parsed_date'] >= split]
        
        analysis = {
            "split_date": str(split),
            "period1": {
                "count": len(period1),
                "date_range": f"{min(e['parsed_date'] for e in period1)} to {split}"
            } if period1 else {"count": 0},
            "period2": {
                "count": len(period2),
                "date_range": f"{split} to {max(e['parsed_date'] for e in period2)}"
            } if period2 else {"count": 0},
            "change": {
                "absolute": len(period2) - len(period1),
                "percentage": round((len(period2) - len(period1)) / max(len(period1), 1) * 100, 2)
            }
        }
        
        console.print(f"[green]Compared {len(period1)} vs {len(period2)} events[/green]")
        return analysis
    
    def generate_summary_statistics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive summary statistics for events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        console.print("[cyan]Generating summary statistics...[/cyan]")
        
        if not events:
            return {"error": "No events provided"}
        
        summary = {
            "total_events": len(events),
            "temporal_analysis": self.analyze_temporal_patterns(events),
            "geographic_analysis": self.analyze_geographic_distribution(events),
            "event_type_analysis": self.analyze_event_types(events),
            "escalation_analysis": self.detect_escalation_patterns(events)
        }
        
        console.print("[green]Summary statistics generated[/green]")
        return summary


def get_analyst_tool(config_path: str = "config/settings.yaml") -> AnalystTool:
    """Get analyst tool instance."""
    return AnalystTool(config_path)

