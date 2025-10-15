# HAWK-AI Test Suite

## Overview

Comprehensive test and debug suite for validating the HAWK-AI functional chain:
**tools → agents → combined reasoning**

## Quick Start

```bash
python3 tests/run_all_tests.py
```

## Test Structure

### ✅ Test Results (Latest Run)

All 5 tests passed in **37.7 seconds**:

| Test | Status | Duration | Description |
|------|--------|----------|-------------|
| 🧭 test_geospatial_tools | ✅ PASS | 1.8s | Validates ACLED data loading, clustering, and map generation |
| 🧠 test_context_enricher | ✅ PASS | 3.4s | Tests historical + web context retrieval and merging |
| 🌍 test_geo_agent | ✅ PASS | 0.3s | Tests GeoAgent country analysis |
| 📊 test_analyst_agent | ✅ PASS | 16.6s | Tests AnalystAgent query analysis with LLM |
| 🔄 test_agent_chain | ✅ PASS | 15.7s | Validates combined agent reasoning |

## Test Details

### 1. Geospatial Tools Test
- **Location**: `test_geospatial_tools()`
- **Tests**: 
  - `load_acled_subset()` - Load conflict data for Sudan (3 years)
  - `cluster_events()` - DBSCAN clustering of geographic events
  - `make_hotspot_map()` - Interactive Leaflet map generation
- **Output**: `data/analysis/test_geospatial.json`
- **Results**:
  - 6,305 events loaded
  - 19 clusters identified
  - 44,569 total fatalities
  - Map: `data/maps/Sudan_hotspot.html`

### 2. Context Enricher Test
- **Location**: `test_context_enricher_tools()`
- **Tests**:
  - `get_historical_context()` - FAISS vector store retrieval
  - `get_web_context()` - DuckDuckGo web search
  - `merge_contexts()` - Context fusion
- **Output**: `data/analysis/test_context_enricher.json`
- **Results**:
  - 3 historical documents retrieved
  - 5 web results retrieved
  - 8 total sources merged

### 3. GeoAgent Test
- **Location**: `test_geo_agent()`
- **Tests**: Full GeoAgent workflow
  - ACLED data loading
  - Event clustering
  - LLM spatial reasoning (with fallback)
  - Interactive map generation
- **Output**: `data/analysis/test_geo_agent.json`
- **Results**:
  - Country: Sudan
  - 6,305 events analyzed
  - 19 hotspot clusters
  - Map generated successfully

### 4. AnalystAgent Test
- **Location**: `test_analyst_agent()`
- **Tests**: Full AnalystAgent workflow
  - Historical context retrieval (FAISS)
  - Web context retrieval (DuckDuckGo)
  - Context merging
  - LLM analysis generation
- **Output**: `data/analysis/test_analyst_agent.json`
- **Results**:
  - 5 historical sources
  - 10 web sources
  - 6,886 character analysis generated
  - Structured context with trend analysis

### 5. Agent Chain Test
- **Location**: `test_agent_chain()`
- **Tests**: Combined AnalystAgent + GeoAgent reasoning
  - Analyst query analysis
  - Geo country analysis
  - Integration validation
- **Output**: `data/analysis/test_agent_chain.json`
- **Results**:
  - Analyst: 5 historical sources, 11,147 char analysis
  - Geo: 6,305 events, 19 clusters
  - Integration: ✅ Success

## Output Files

### Test Results (JSON)
All test results are saved to `data/analysis/`:
- `test_geospatial.json` - Geospatial tools results
- `test_context_enricher.json` - Context enricher results
- `test_geo_agent.json` - GeoAgent results
- `test_analyst_agent.json` - AnalystAgent results
- `test_agent_chain.json` - Combined chain results

### Test Logs
- `logs/test_summary.log` - Timestamped test runs with pass/fail status
- `logs/geo_agent.log` - GeoAgent execution logs
- `logs/analyst_agent.log` - AnalystAgent execution logs

### Generated Maps
- `data/maps/Sudan_hotspot.html` - Interactive conflict hotspot map

## Dependencies

### Required Packages
```bash
pip3 install faiss-cpu pandas numpy scikit-learn \
             langchain-ollama langchain-core \
             python-dotenv requests beautifulsoup4 \
             duckduckgo-search sentence-transformers
```

### Optional (for GPU acceleration)
```bash
pip3 install faiss-gpu torch
```

## Features

### ✨ Color-Coded Output
- 🟢 Green: Test passed
- 🔴 Red: Test failed
- 🔵 Blue: Info messages
- 🟡 Yellow: Warnings

### 📊 Test Summary
- Individual test status and duration
- Total runtime
- Pass/fail count
- Detailed error traces for failed tests

### 🔄 Sequential Execution
- Tests run in order
- Each test independent (failures don't block others)
- Automatic directory creation

### 📝 Comprehensive Logging
- Timestamped log entries
- Detailed error traces
- Test output saved to JSON
- Runtime metrics

## Architecture

```
tests/run_all_tests.py
│
├── TestRunner (orchestration)
│   ├── run_test() - Execute individual test
│   ├── print_summary() - Display results table
│   └── save_log() - Save to logs/test_summary.log
│
├── test_geospatial_tools()
│   └── core.tools_geospatial.*
│
├── test_context_enricher_tools()
│   └── core.context_enricher.*
│
├── test_geo_agent()
│   └── agents.geo_agent.GeoAgent
│
├── test_analyst_agent()
│   └── agents.analyst_agent.AnalystAgent
│
└── test_agent_chain()
    ├── agents.analyst_agent.AnalystAgent
    └── agents.geo_agent.GeoAgent
```

## Known Issues

### 1. Model Compatibility
- **Issue**: `qwen3-embedding:8b` does not support text generation
- **Impact**: GeoAgent LLM summaries fall back to statistics-based summaries
- **Fix**: Use a text generation model like `llama3:8b` or `qwen2:7b`

### 2. DuckDuckGo Deprecation
- **Warning**: `duckduckgo_search` package renamed to `ddgs`
- **Impact**: Minor deprecation warnings (no functional impact)
- **Fix**: `pip install ddgs` (future upgrade)

### 3. Resource Warnings
- **Issue**: Unclosed socket connections in HTTP client
- **Impact**: No functional impact, just warnings
- **Fix**: Normal behavior for async HTTP clients

## Debugging

### If a test fails:

1. **Check the detailed error output** - printed at the end
2. **Review the log file**: `logs/test_summary.log`
3. **Check module logs**: `logs/geo_agent.log`, `logs/analyst_agent.log`
4. **Verify Ollama is running**: `ollama list`
5. **Check ACLED data**: `historical_context/ACLED/`
6. **Verify FAISS index**: `data/vector_index/`

### Common Issues:

```bash
# Ollama not running
sudo systemctl start ollama
# or
ollama serve

# Missing ACLED data
ls -lh historical_context/ACLED/

# FAISS index missing
ls -lh data/vector_index/

# Dependencies missing
pip3 install -r requirements.txt
```

## Performance Metrics

### Typical Runtime (Intel CPU)
- **Geospatial tools**: 1-2 seconds
- **Context enricher**: 3-5 seconds (includes FAISS + web search)
- **GeoAgent**: 0.3-0.5 seconds (without LLM) or 5-10s (with LLM)
- **AnalystAgent**: 15-20 seconds (LLM generation)
- **Agent chain**: 15-20 seconds (parallel operations)
- **Total**: ~40 seconds

### With GPU (CUDA)
- **FAISS search**: 5-10x faster
- **LLM inference**: 2-3x faster (if using GPU-accelerated Ollama)
- **Total**: ~20-25 seconds

## Advanced Usage

### Run Individual Tests

```python
python3 -c "
from tests.run_all_tests import test_geospatial_tools
result = test_geospatial_tools()
print(result)
"
```

### Custom Test Configuration

Edit `tests/run_all_tests.py` to modify:
- Country for analysis (default: Sudan)
- Years back (default: 3)
- Clustering parameters (eps_km, min_samples)
- LLM models (default: gpt-oss:20b, qwen3-embedding:8b)

### Run with Python Debugger

```bash
python3 -m pdb tests/run_all_tests.py
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: HAWK-AI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip3 install -r requirements.txt
      - name: Run tests
        run: python3 tests/run_all_tests.py
```

## Contributing

When adding new tests:

1. Follow the existing test function pattern
2. Add assertions for key outputs
3. Save results to `data/analysis/`
4. Include detailed logging
5. Handle exceptions gracefully
6. Update this README

## License

Part of the HAWK-AI project. See main repository for license details.

---

**Last Updated**: October 15, 2025  
**Test Suite Version**: 1.0  
**Status**: ✅ All tests passing

