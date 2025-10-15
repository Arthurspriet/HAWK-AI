"""
Geospatial tools for HAWK-AI.
Loads ACLED data, clusters events, and builds interactive Mapbox maps.
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

logger = logging.getLogger("tools_geospatial")


def load_acled_subset(
    country: str,
    years_back: int = 3,
    data_dir: str = "historical_context/ACLED"
) -> pd.DataFrame:
    """
    Load ACLED data for a specific country over the last N years.
    
    Args:
        country: Country name (e.g., "Sudan", "Nigeria")
        years_back: Number of years to look back from present
        data_dir: Path to ACLED data directory
        
    Returns:
        DataFrame with filtered ACLED events
        
    Raises:
        FileNotFoundError: If ACLED data files are not found
        ValueError: If no data found for the specified country
    """
    logger.info(f"Loading ACLED data for {country}, last {years_back} years")
    
    # Determine which regional file to load based on common regions
    region_map = {
        # Africa
        "algeria": "Africa", "angola": "Africa", "benin": "Africa", 
        "botswana": "Africa", "burkina faso": "Africa", "burundi": "Africa",
        "cameroon": "Africa", "chad": "Africa", "drc": "Africa", "egypt": "Africa",
        "ethiopia": "Africa", "kenya": "Africa", "libya": "Africa", "mali": "Africa",
        "morocco": "Africa", "mozambique": "Africa", "niger": "Africa", 
        "nigeria": "Africa", "somalia": "Africa", "south africa": "Africa",
        "south sudan": "Africa", "sudan": "Africa", "tunisia": "Africa",
        "uganda": "Africa", "zimbabwe": "Africa",
        # Middle East
        "iraq": "Middle-East", "iran": "Middle-East", "israel": "Middle-East",
        "jordan": "Middle-East", "lebanon": "Middle-East", "palestine": "Middle-East",
        "saudi arabia": "Middle-East", "syria": "Middle-East", "turkey": "Middle-East",
        "yemen": "Middle-East",
        # Asia-Pacific
        "afghanistan": "Asia-Pacific", "bangladesh": "Asia-Pacific", 
        "india": "Asia-Pacific", "myanmar": "Asia-Pacific", "pakistan": "Asia-Pacific",
        "philippines": "Asia-Pacific", "thailand": "Asia-Pacific",
        # Europe-Central Asia
        "russia": "Europe-Central-Asia", "ukraine": "Europe-Central-Asia",
        "georgia": "Europe-Central-Asia", "azerbaijan": "Europe-Central-Asia",
        # Latin America
        "mexico": "Latin-America-the-Caribbean", "colombia": "Latin-America-the-Caribbean",
        "brazil": "Latin-America-the-Caribbean", "venezuela": "Latin-America-the-Caribbean",
        # US and Canada
        "united states": "US-and-Canada", "canada": "US-and-Canada",
    }
    
    country_lower = country.lower()
    region = region_map.get(country_lower)
    
    if not region:
        # Try all regions if country not in map
        logger.warning(f"Country {country} not in region map, searching all files")
        regions_to_try = ["Africa", "Middle-East", "Asia-Pacific", 
                         "Europe-Central-Asia", "Latin-America-the-Caribbean", 
                         "US-and-Canada"]
    else:
        regions_to_try = [region]
    
    # Try to load data from appropriate file(s)
    all_dfs = []
    for region in regions_to_try:
        file_path = Path(data_dir) / f"{region}_aggregated_data_up_to-2025-08-23.csv"
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            continue
            
        try:
            df = pd.read_csv(file_path)
            
            # Filter by country (case-insensitive)
            df_country = df[df['COUNTRY'].str.lower() == country_lower].copy()
            
            if len(df_country) > 0:
                all_dfs.append(df_country)
                logger.info(f"Found {len(df_country)} events in {region} file")
                
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            continue
    
    if not all_dfs:
        raise ValueError(f"No ACLED data found for country: {country}")
    
    # Combine all data
    df = pd.concat(all_dfs, ignore_index=True)
    
    # Parse dates and filter by years_back
    df['WEEK'] = pd.to_datetime(df['WEEK'], format='%d/%m/%Y', errors='coerce')
    cutoff_date = datetime.now() - timedelta(days=365 * years_back)
    df = df[df['WEEK'] >= cutoff_date]
    
    # Clean coordinate columns (handle comma as decimal separator)
    if 'CENTROID_LATITUDE' in df.columns:
        df['CENTROID_LATITUDE'] = df['CENTROID_LATITUDE'].astype(str).str.replace(',', '.').astype(float)
    if 'CENTROID_LONGITUDE' in df.columns:
        df['CENTROID_LONGITUDE'] = df['CENTROID_LONGITUDE'].astype(str).str.replace(',', '.').astype(float)
    
    # Drop rows with missing coordinates
    df = df.dropna(subset=['CENTROID_LATITUDE', 'CENTROID_LONGITUDE'])
    
    logger.info(f"Loaded {len(df)} events for {country} from {cutoff_date.date()}")
    return df


def cluster_events(
    df: pd.DataFrame,
    eps_km: float = 50.0,
    min_samples: int = 5
) -> pd.DataFrame:
    """
    Cluster ACLED events using DBSCAN based on geographic proximity.
    
    Args:
        df: DataFrame with CENTROID_LATITUDE and CENTROID_LONGITUDE columns
        eps_km: Maximum distance (in km) between points in a cluster
        min_samples: Minimum number of samples in a cluster
        
    Returns:
        DataFrame with added 'cluster' column
    """
    logger.info(f"Clustering {len(df)} events with eps={eps_km}km, min_samples={min_samples}")
    
    if len(df) == 0:
        df['cluster'] = []
        return df
    
    # Convert coordinates to radians for haversine distance
    coords = df[['CENTROID_LATITUDE', 'CENTROID_LONGITUDE']].values
    coords_rad = np.radians(coords)
    
    # DBSCAN with haversine metric (requires coordinates in radians)
    # eps in radians: eps_km / earth_radius_km
    earth_radius_km = 6371.0
    eps_rad = eps_km / earth_radius_km
    
    clustering = DBSCAN(
        eps=eps_rad,
        min_samples=min_samples,
        metric='haversine',
        n_jobs=-1
    ).fit(coords_rad)
    
    df['cluster'] = clustering.labels_
    
    n_clusters = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
    n_noise = list(clustering.labels_).count(-1)
    
    logger.info(f"Found {n_clusters} clusters, {n_noise} noise points")
    
    return df


def make_hotspot_map(
    df: pd.DataFrame,
    output_path: str = "data/maps/hotspot.html",
    title: Optional[str] = None
) -> Dict[str, any]:
    """
    Generate an interactive Mapbox-style map showing event hotspots.
    
    Args:
        df: DataFrame with clustered ACLED events
        output_path: Where to save the HTML map
        title: Optional map title
        
    Returns:
        Dict with 'path', 'n_events', 'n_clusters'
    """
    logger.info(f"Generating hotspot map with {len(df)} events")
    
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if len(df) == 0:
        logger.warning("No events to map")
        # Create empty map
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>No Data</title></head>
        <body><h1>No events to display</h1></body>
        </html>
        """
        output_file.write_text(html_content)
        return {
            'path': str(output_path),
            'n_events': 0,
            'n_clusters': 0
        }
    
    # Calculate center and bounds
    center_lat = df['CENTROID_LATITUDE'].mean()
    center_lon = df['CENTROID_LONGITUDE'].mean()
    
    # Create a simple HTML map using Leaflet (no external API key needed)
    if title is None:
        country = df['COUNTRY'].iloc[0] if 'COUNTRY' in df.columns else "Unknown"
        title = f"Conflict Hotspots: {country}"
    
    # Prepare cluster data
    cluster_counts = df[df['cluster'] != -1].groupby('cluster').agg({
        'CENTROID_LATITUDE': 'mean',
        'CENTROID_LONGITUDE': 'mean',
        'EVENTS': 'sum',
        'FATALITIES': 'sum'
    }).reset_index()
    
    n_clusters = len(cluster_counts)
    
    # Build HTML with Leaflet
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body {{ margin: 0; padding: 0; }}
            #map {{ width: 100vw; height: 100vh; }}
            .info {{ 
                padding: 10px;
                font: 14px/16px Arial, sans-serif;
                background: white;
                background: rgba(255,255,255,0.9);
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                border-radius: 5px;
            }}
            .info h4 {{ margin: 0 0 5px; color: #333; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{center_lat}, {center_lon}], 6);
            
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                maxZoom: 18
            }}).addTo(map);
            
            // Add info box
            var info = L.control({{position: 'topright'}});
            info.onAdd = function (map) {{
                this._div = L.DomUtil.create('div', 'info');
                this._div.innerHTML = '<h4>{title}</h4>' +
                    '<b>Total Events:</b> {len(df)}<br/>' +
                    '<b>Clusters:</b> {n_clusters}<br/>' +
                    '<b>Total Fatalities:</b> {df["FATALITIES"].sum()}';
                return this._div;
            }};
            info.addTo(map);
    """
    
    # Add individual event markers (sample if too many)
    sample_df = df.sample(n=min(500, len(df)), random_state=42)
    for _, row in sample_df.iterrows():
        lat = row['CENTROID_LATITUDE']
        lon = row['CENTROID_LONGITUDE']
        event_type = row.get('EVENT_TYPE', 'Unknown')
        fatalities = row.get('FATALITIES', 0)
        
        color = 'red' if fatalities > 10 else 'orange' if fatalities > 0 else 'blue'
        
        html_template += f"""
            L.circleMarker([{lat}, {lon}], {{
                color: '{color}',
                fillColor: '{color}',
                fillOpacity: 0.5,
                radius: 5
            }}).bindPopup('<b>{event_type}</b><br/>Fatalities: {fatalities}').addTo(map);
        """
    
    # Add cluster centers as larger markers
    for _, cluster in cluster_counts.iterrows():
        lat = cluster['CENTROID_LATITUDE']
        lon = cluster['CENTROID_LONGITUDE']
        events = cluster['EVENTS']
        fatalities = cluster['FATALITIES']
        cluster_id = cluster['cluster']
        
        radius = min(20, 10 + events / 10)
        
        html_template += f"""
            L.circle([{lat}, {lon}], {{
                color: 'darkred',
                fillColor: '#ff0000',
                fillOpacity: 0.3,
                radius: {radius * 1000}
            }}).bindPopup('<b>Cluster {cluster_id}</b><br/>Events: {events}<br/>Fatalities: {fatalities}').addTo(map);
        """
    
    html_template += """
        </script>
    </body>
    </html>
    """
    
    # Write to file
    output_file.write_text(html_template)
    logger.info(f"Map saved to {output_path}")
    
    return {
        'path': str(output_path),
        'n_events': len(df),
        'n_clusters': n_clusters,
        'total_fatalities': int(df['FATALITIES'].sum())
    }

