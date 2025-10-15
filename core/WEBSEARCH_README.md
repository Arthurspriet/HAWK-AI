# HAWK-AI Web Search Tools

A reliable, local-friendly web search module using DuckDuckGo with caching and vectorization support.

## Features

- 🔍 **Web Search**: DuckDuckGo search with customizable result limits
- 💾 **Local Caching**: Automatic caching of search results under `data/web_cache/`
- 🧠 **Vectorization**: FAISS-based vector storage using Ollama embeddings
- 🎯 **Relevance Ranking**: Find most relevant results using semantic similarity
- 📊 **CLI Interface**: Quick testing from command line
- 📝 **Logging**: Comprehensive logging to `logs/websearch.log`

## Requirements

All dependencies are in `requirements.txt`:
- `duckduckgo-search`
- `faiss-cpu` or `faiss-gpu`
- `langchain-ollama`
- `tqdm`
- Python 3.8+

## Installation

```bash
# Activate your virtual environment
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Ensure Ollama is running with the embedding model
ollama pull snowflake-arctic-embed2:568m
```

## Quick Start

### CLI Usage

```bash
# Basic search
python core/tools_websearch.py "AI safety research"

# Search specific topic
python core/tools_websearch.py "conflict escalation in Sudan 2024"
```

The CLI will:
1. Search DuckDuckGo for results
2. Display all results with titles, URLs, and snippets
3. Find and display top-3 most relevant results
4. Save vectorized results to FAISS index

### Programmatic Usage

```python
from core.tools_websearch import smart_search, vectorize_results, find_most_relevant

# 1. Simple search
results = smart_search("quantum computing", max_results=10)

for result in results:
    print(result['title'], result['href'])

# 2. Find most relevant results
query = "machine learning applications"
results = smart_search(query, max_results=20)
top_3 = find_most_relevant(query, results, top_k=3)

# 3. Vectorize and save to FAISS
index, indexed_results = vectorize_results(
    results, 
    query=query, 
    index_name="my_search"
)

# 4. Load saved index
from core.tools_websearch import load_vector_index
index, metadata = load_vector_index("my_search")
print(f"Loaded {index.ntotal} vectors")
```

## API Reference

### `smart_search(query, max_results=20, use_cache=True)`

Perform a web search using DuckDuckGo with optional caching.

**Parameters:**
- `query` (str): Search query string
- `max_results` (int): Maximum number of results (default: 20)
- `use_cache` (bool): Use cached results if available (default: True)

**Returns:**
- List[Dict]: List of results with keys: `title`, `body`, `href`

**Example:**
```python
results = smart_search("climate change impacts", max_results=15)
```

### `vectorize_results(results, query=None, index_name="web_index")`

Vectorize search results using Ollama embeddings and save to FAISS index.

**Parameters:**
- `results` (List[Dict]): Search results from `smart_search()`
- `query` (str, optional): Original query for metadata
- `index_name` (str): Name for the FAISS index file (default: "web_index")

**Returns:**
- Tuple[faiss.Index, List[Dict]]: FAISS index and indexed results

**Example:**
```python
index, indexed = vectorize_results(results, query="AI research", index_name="ai_search")
```

### `find_most_relevant(query, results, top_k=3)`

Find the most relevant results using vector similarity.

**Parameters:**
- `query` (str): Query to compare against
- `results` (List[Dict]): Search results
- `top_k` (int): Number of top results to return (default: 3)

**Returns:**
- List[Dict]: Top-k most relevant results

**Example:**
```python
top_results = find_most_relevant("neural networks", results, top_k=5)
```

### `load_vector_index(index_name="web_index")`

Load a previously saved FAISS index and metadata.

**Parameters:**
- `index_name` (str): Name of the index to load

**Returns:**
- Tuple[faiss.Index, Dict]: FAISS index and metadata

**Example:**
```python
index, metadata = load_vector_index("my_search")
if index:
    print(f"Loaded {index.ntotal} vectors")
    print(f"Original query: {metadata['query']}")
```

## File Structure

```
HAWK-AI/
├── core/
│   ├── tools_websearch.py         # Main module
│   └── tools_websearch_example.py # Usage examples
├── data/
│   ├── web_cache/                 # Cached search results (*.pkl)
│   └── vector_index/              # FAISS indices
│       ├── web_index.faiss        # Default FAISS index
│       └── web_index_metadata.pkl # Metadata
└── logs/
    └── websearch.log              # Search logs
```

## Caching

Search results are automatically cached using MD5 hash of `query + max_results`:

- **Cache Location**: `data/web_cache/<hash>.pkl`
- **Cache Key**: MD5 hash of `{query}_{max_results}`
- **Format**: Python pickle format

To bypass cache:
```python
results = smart_search(query, use_cache=False)
```

## Vectorization

Uses Ollama's `snowflake-arctic-embed2:568m` model for embeddings:

- **Model**: snowflake-arctic-embed2:568m (1024 dimensions)
- **Ollama URL**: http://127.0.0.1:11434
- **Index Type**: FAISS IndexFlatL2 (L2 distance)
- **Storage**: `data/vector_index/<index_name>.faiss`

Each vectorized index includes:
- FAISS index file (`.faiss`)
- Metadata file (`_metadata.pkl`) with:
  - Original results
  - Query string
  - Timestamp
  - Vector dimensions
  - Number of vectors

## Logging

All operations are logged to `logs/websearch.log`:

```python
2025-10-15 20:07:52,715 - __main__ - INFO - Searching for: 'AI safety' (max_results=20)
2025-10-15 20:07:52,827 - __main__ - INFO - Retrieved 20 results from DuckDuckGo
2025-10-15 20:07:52,828 - __main__ - INFO - Saved 20 results to cache: abc123...
2025-10-15 20:07:59,602 - __main__ - INFO - Saved FAISS index to .../web_index.faiss
```

## Configuration

To customize Ollama settings, edit the module constants:

```python
# In tools_websearch.py
OLLAMA_MODEL = "snowflake-arctic-embed2:568m"  # Change model
OLLAMA_BASE_URL = "http://127.0.0.1:11434"     # Change Ollama URL
```

## Performance

- **First search**: ~3-5 seconds (network + DuckDuckGo)
- **Cached search**: <0.1 seconds (instant)
- **Vectorization**: ~0.07 seconds per document (with local Ollama)
- **Relevance search**: <1 second for 20 documents

## Troubleshooting

### Ollama Connection Error

```bash
# Ensure Ollama is running
ollama serve

# Pull the embedding model
ollama pull snowflake-arctic-embed2:568m
```

### DuckDuckGo Search Fails

The module will log errors but continue gracefully:
```python
logger.error(f"Search failed: {e}")
return []
```

### Cache Issues

Clear cache manually if needed:
```bash
rm -rf data/web_cache/*.pkl
```

## Integration with HAWK-AI

This module integrates with the HAWK-AI agent system:

```python
# In your agent code
from core.tools_websearch import smart_search, find_most_relevant

def search_tool(query: str) -> str:
    """Tool for agent to search the web"""
    results = smart_search(query, max_results=10)
    top_results = find_most_relevant(query, results, top_k=3)
    
    # Format for agent
    output = []
    for r in top_results:
        output.append(f"Title: {r['title']}\nURL: {r['href']}\n{r['body']}\n")
    
    return "\n".join(output)
```

## Examples

See `tools_websearch_example.py` for complete examples:

```bash
python core/tools_websearch_example.py
```

## License

Part of the HAWK-AI project.

## Support

For issues or questions:
- Check `logs/websearch.log` for detailed error messages
- Ensure Ollama is running: `ollama list`
- Verify dependencies: `pip list | grep -E "duckduckgo|faiss|langchain-ollama"`

