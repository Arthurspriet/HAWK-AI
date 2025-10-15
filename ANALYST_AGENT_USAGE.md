# AnalystAgent Usage Guide

## Overview

The AnalystAgent fuses historical FAISS intelligence with current web context for comprehensive analytical reasoning. It uses a reasoning model (default: `gpt-oss:20b`) to generate analytical briefs with temporal and political nuance.

## Architecture

```
Query → Historical Context (FAISS) ┐
                                    ├→ Context Enrichment → LLM Analysis → Output
Query → Web Context (DuckDuckGo)  ┘
```

## Components

### 1. Context Enricher (`core/context_enricher.py`)
- `get_historical_context(query)`: Retrieves ACLED/CIA data from FAISS vector store
- `get_web_context(query)`: Retrieves current web results via DuckDuckGo
- `merge_contexts(hist, web)`: Fuses both sources into enriched JSON

### 2. AnalystAgent (`agents/analyst_agent.py`)
- Orchestrates context retrieval
- Generates analytical prompts
- Produces structured intelligence reports

## CLI Usage

### Basic Query
```bash
python agents/analyst_agent.py "Conflict escalation in Sudan 2022–2025"
```

### Expected Output
```
================================================================================
HAWK-AI Analyst Agent
================================================================================

Query: Conflict escalation in Sudan 2022–2025

Initializing agent...

Performing analysis...

================================================================================
ANALYTICAL BRIEF
================================================================================

Context Sources:
  • Historical: 5 documents
  • Web: 10 results
  • Total: 15 sources

Historical Context:
  1. ACLED - Sudan (Violence against civilians) - Score: 0.892
  2. ACLED - Sudan (Armed conflict) - Score: 0.875
  3. CIA_FACTS - Sudan - Score: 0.834

Web Context:
  1. Sudan conflict: Latest developments 2025
     https://example.com/sudan-2025
  2. Humanitarian crisis deepens in Sudan
     https://example.com/humanitarian
  ...

────────────────────────────────────────────────────────────────────────────────
ANALYSIS:
────────────────────────────────────────────────────────────────────────────────

1. Executive Summary
[LLM-generated analysis]

2. Historical Patterns
[Based on FAISS data]

3. Current Developments
[Based on web data]

4. Temporal Analysis
[Trends over time]

5. Political and Strategic Implications
[Expert analysis]

6. Key Risk Factors
[Risk assessment]

================================================================================
```

## Programmatic Usage

### Python API

```python
from agents.analyst_agent import AnalystAgent

# Initialize agent
agent = AnalystAgent(model="gpt-oss:20b")

# Perform analysis
result = agent.analyze_query("Conflict escalation in Sudan 2022–2025")

# Access results
print(f"Query: {result['query']}")
print(f"Historical sources: {result['structured_context']['historical_context']['count']}")
print(f"Web sources: {result['structured_context']['web_context']['count']}")
print(f"Analysis: {result['analysis']}")
```

### Integration with SupervisorAgent

```python
from agents.analyst_agent import AnalystAgent

# In SupervisorAgent
analyst = AnalystAgent()
intel_report = analyst.analyze_query(user_query)

# Process JSON output
structured_output = {
    "query": intel_report["query"],
    "context_summary": {
        "historical_count": intel_report["structured_context"]["historical_context"]["count"],
        "web_count": intel_report["structured_context"]["web_context"]["count"]
    },
    "analysis": intel_report["analysis"],
    "status": "error" if "error" in intel_report else "success"
}
```

## Configuration

### Model Selection
```python
# Use different Ollama model
agent = AnalystAgent(model="llama3.1:70b")
agent = AnalystAgent(model="mistral:latest")
agent = AnalystAgent(model="gpt-oss:20b")  # Default - reasoning model
```

### Context Parameters
The agent retrieves:
- **Historical**: Top 5 most relevant FAISS documents
- **Web**: Top 10 most recent web results

To modify, edit `core/context_enricher.py`:
```python
def get_historical_context(query: str, top_k: int = 5)
def get_web_context(query: str, max_results: int = 10)
```

## Logging

All operations are logged to `logs/analyst_agent.log`:
```
2025-10-15 10:30:45 - AnalystAgent - INFO - AnalystAgent initialized with model: gpt-oss:20b
2025-10-15 10:30:46 - AnalystAgent - INFO - Analyzing query: Conflict escalation in Sudan 2022–2025
2025-10-15 10:30:47 - ContextEnricher - INFO - Retrieved 5 historical documents
2025-10-15 10:30:50 - ContextEnricher - INFO - Retrieved 10 web results
2025-10-15 10:30:51 - AnalystAgent - INFO - Analysis completed successfully
```

## Output Format

The agent returns a dictionary with:
```json
{
  "query": "Original query string",
  "structured_context": {
    "historical_context": {
      "count": 5,
      "sources": [...],
      "summary": [...]
    },
    "web_context": {
      "count": 10,
      "sources": [...],
      "summary": [...]
    },
    "metadata": {
      "total_sources": 15,
      "historical_weight": 0.33,
      "web_weight": 0.67
    }
  },
  "analysis": "Full LLM-generated analytical brief..."
}
```

## Dependencies

Required packages (in `requirements.txt`):
- `langchain-ollama`: LLM interface
- `faiss-gpu` or `faiss-cpu`: Vector search
- `sentence-transformers`: Embeddings for FAISS
- `duckduckgo-search`: Web search
- `pandas`, `numpy`: Data processing

## Prerequisites

1. **Ollama running locally**:
   ```bash
   ollama serve
   ollama pull gpt-oss:20b
   ```

2. **FAISS vector store populated**:
   ```bash
   python core/vector_store.py --rebuild
   ```

3. **Dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

## Testing

Run the test script:
```bash
python test_analyst_agent_new.py
```

## Error Handling

If analysis fails, the agent returns:
```json
{
  "query": "...",
  "structured_context": {},
  "analysis": "Error: Analysis failed - [reason]",
  "error": "[detailed error message]"
}
```

Common issues:
- **FAISS index not found**: Run `python core/vector_store.py --rebuild`
- **Ollama not running**: Start with `ollama serve`
- **Model not found**: Pull with `ollama pull gpt-oss:20b`
- **No web results**: Check internet connection

## Examples

### Example 1: Conflict Analysis
```bash
python agents/analyst_agent.py "Conflict escalation in Sudan 2022–2025"
```

### Example 2: Regional Security
```bash
python agents/analyst_agent.py "Security situation in Sahel region 2024"
```

### Example 3: Terrorism Analysis
```bash
python agents/analyst_agent.py "Terrorism trends in West Africa 2023-2025"
```

### Example 4: Humanitarian Crisis
```bash
python agents/analyst_agent.py "Humanitarian impact of Yemen conflict"
```

## Integration Points

The AnalystAgent is designed to integrate with:
- **SupervisorAgent**: For multi-agent orchestration
- **GeoAgent**: For geospatial visualization of analysis results
- **RedactorAgent**: For PII removal from reports
- **SearchAgent**: For deeper web research

## Performance

- **Historical context retrieval**: ~1-2 seconds
- **Web context retrieval**: ~2-3 seconds
- **LLM analysis**: ~10-30 seconds (depends on model)
- **Total**: ~15-40 seconds per query

## Future Enhancements

- [ ] Add news-specific web search
- [ ] Support for multi-turn conversations
- [ ] Custom prompt templates
- [ ] Confidence scoring
- [ ] Citation tracking
- [ ] Export to PDF/Markdown

