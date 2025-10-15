# GeoAgent - Geospatial Reasoning for HAWK-AI

## Overview

GeoAgent provides geospatial analysis capabilities for HAWK-AI, analyzing conflict patterns from ACLED data, performing spatial clustering, and generating interactive hotspot maps.

## Features

- **ACLED Data Analysis**: Load and filter conflict event data by country and time period
- **Spatial Clustering**: Uses DBSCAN algorithm to identify geographic hotspots
- **LLM Reasoning**: Generates spatial analysis summaries using Ollama models
- **Interactive Maps**: Creates Leaflet-based HTML maps with event markers and cluster visualization
- **Comprehensive Logging**: All operations logged to `logs/geo_agent.log`

## Installation

The GeoAgent is part of the HAWK-AI system. Ensure dependencies are installed:

```bash
make setup
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Basic usage:

```bash
source .venv/bin/activate
python agents/geo_agent.py --country Sudan --years 3
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--country` | Country name to analyze (required) | None |
| `--years` | Number of years back to analyze | 3 |
| `--model` | Ollama model for spatial reasoning | `qwen3-embedding:8b` |
| `--eps-km` | Maximum distance (km) for clustering | 50.0 |
| `--min-samples` | Minimum samples per cluster | 5 |
| `--output-dir` | Directory for generated maps | `data/maps` |
| `--log-file` | Path to log file | `logs/geo_agent.log` |

### Examples

Analyze Sudan over the last 3 years:
```bash
python agents/geo_agent.py --country Sudan --years 3
```

Analyze Nigeria with custom clustering parameters:
```bash
python agents/geo_agent.py --country Nigeria --years 2 --eps-km 30 --min-samples 10
```

Use a specific LLM model (requires model to be available in Ollama):
```bash
python agents/geo_agent.py --country "South Sudan" --years 5 --model llama3:8b
```

### Programmatic Usage

```python
from agents.geo_agent import GeoAgent

# Initialize agent
agent = GeoAgent(model="llama3:8b")

# Analyze a country
result = agent.analyze_country(
    country="Sudan",
    years_back=3,
    eps_km=50.0,
    min_samples=5
)

print(f"Country: {result['country']}")
print(f"Events: {result['n_events']}")
print(f"Clusters: {result['n_clusters']}")
print(f"Summary: {result['summary']}")
print(f"Map: {result['map_path']}")

# Batch analysis
results = agent.batch_analyze(
    countries=["Sudan", "South Sudan", "Ethiopia"],
    years_back=2
)
```

## Output

The agent produces:

1. **Console Output**: Summary statistics and LLM-generated analysis
2. **Interactive Map**: HTML file in `data/maps/` directory
3. **Logs**: Detailed execution logs in `logs/geo_agent.log`

### Example Output

```
======================================================================
GEOSPATIAL ANALYSIS: Sudan
======================================================================

Period: Last 3 years
Events: 6305
Clusters: 19
Total Fatalities: 44569

Analysis based on 6305 events across 19 geographic clusters with 44569 total
fatalities. Primary event types: Strategic developments, Violence against 
civilians, Battles.

Map generated: data/maps/Sudan_hotspot.html
======================================================================
```

### Interactive Map Features

The generated HTML maps include:

- **Event Markers**: Color-coded by severity (red=high fatalities, orange=moderate, blue=low)
- **Cluster Circles**: Large circles showing identified hotspot clusters
- **Info Box**: Summary statistics (total events, clusters, fatalities)
- **Interactive**: Click markers/clusters for detailed information
- **Zoom/Pan**: Fully interactive Leaflet map controls

## Supported Countries

The agent supports countries from the following ACLED data regions:

- **Africa**: Sudan, South Sudan, Nigeria, Ethiopia, Somalia, Kenya, etc.
- **Middle East**: Yemen, Syria, Iraq, Palestine, etc.
- **Asia-Pacific**: Afghanistan, Pakistan, Myanmar, Philippines, etc.
- **Europe-Central Asia**: Ukraine, Russia, Georgia, Azerbaijan, etc.
- **Latin America**: Mexico, Colombia, Brazil, Venezuela, etc.
- **US and Canada**: United States, Canada

## Architecture

### Components

1. **`agents/geo_agent.py`**: Main agent class with CLI interface
2. **`core/tools_geospatial.py`**: Geospatial tools for data loading, clustering, and mapping

### Key Functions

#### `load_acled_subset()`
Loads ACLED data for a specific country and time period.

#### `cluster_events()`
Performs DBSCAN clustering on geographic coordinates using haversine distance.

#### `make_hotspot_map()`
Generates interactive Leaflet-based HTML map visualization.

## Error Handling

The agent includes robust error handling:

- **Missing Data Files**: Raises `FileNotFoundError` with clear message
- **Invalid Country**: Raises `ValueError` if country not found in ACLED data
- **LLM Failure**: Falls back to statistical summary if LLM unavailable
- **Invalid Coordinates**: Filters out events with missing/invalid coordinates

## Logging

All operations are logged to `logs/geo_agent.log` with timestamps:

```
2025-10-15 20:39:39,232 - GeoAgent - INFO - GeoAgent initialized with model: qwen3-embedding:8b
2025-10-15 20:39:39,232 - GeoAgent - INFO - Starting analysis for Sudan (last 3 years)
2025-10-15 20:39:39,384 - GeoAgent - INFO - Clustering 6305 events...
2025-10-15 20:39:39,459 - GeoAgent - INFO - Analysis complete for Sudan
```

## Notes

### LLM Models

The default model `qwen3-embedding:8b` is an embedding model and doesn't support text generation. For full LLM reasoning, use a generative model:

- `llama3:8b` - General purpose, good balance
- `mistral:7b` - Fast and efficient
- `qwen:7b` - Good for analytical tasks

Make sure the model is available in your Ollama instance:
```bash
ollama list
ollama pull llama3:8b  # if needed
```

### Performance

- **Large datasets**: Analysis may take 1-2 minutes for countries with 5000+ events
- **Clustering**: DBSCAN with haversine metric is optimized with `n_jobs=-1`
- **Map generation**: Samples events if >500 to ensure map remains responsive

## Integration with HAWK-AI

The GeoAgent can be integrated into the main HAWK-AI orchestrator:

```python
from agents.geo_agent import GeoAgent

# In orchestrator or agent registry
geo_agent = GeoAgent(model="llama3:8b")

# Use for geospatial queries
result = geo_agent.analyze_country("Sudan", years_back=3)
```

## Troubleshooting

### "No module named 'faiss'"

Make sure you're in the virtual environment:
```bash
source .venv/bin/activate
```

### "Country not found"

Check country name spelling. The agent is case-insensitive but requires correct names as they appear in ACLED data.

### "Model not found"

The specified Ollama model isn't available. Check available models:
```bash
ollama list
```

### Empty Map

If no events found for the time period, try increasing `--years` parameter.

## Future Enhancements

- [ ] Time-series animation of conflict evolution
- [ ] Heatmap density visualization
- [ ] Multi-country comparative analysis
- [ ] Export to GeoJSON/KML formats
- [ ] Integration with additional data sources
- [ ] Predictive hotspot modeling

## License

Part of the HAWK-AI project.

