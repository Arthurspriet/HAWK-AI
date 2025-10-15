# HAWK-AI Test Suite - Quick Start

## 🚀 Run Tests

```bash
cd /home/arthurspriet/HAWK-AI
python3 tests/run_all_tests.py
```

## 📊 Expected Output

```
======================================================================
HAWK-AI TEST SUITE
======================================================================

Setting up test environment...
✓ Directories created

Running tests:

----------------------------------------------------------------------
🧭 test_geospatial_tools ................... ✅ OK (1.8s)
   → 6305 events, 19 clusters
   → Map: data/maps/Sudan_hotspot.html

🧠 test_context_enricher ................... ✅ OK (3.4s)
   → Historical: 3, Web: 5
   → Total sources: 8

🌍 test_geo_agent .......................... ✅ OK (0.3s)
   → 6305 events, 19 clusters
   → Map: data/maps/Sudan_hotspot.html

📊 test_analyst_agent ...................... ✅ OK (16.6s)
   → Sources: 5 historical + 10 web
   → Analysis: 6886 chars

🔄 test_agent_chain ........................ ✅ OK (15.7s)
   → Analyst: 5 hist + 0 web sources
   → Geo: 6305 events, 19 clusters
   → Map: data/maps/Sudan_hotspot.html
----------------------------------------------------------------------

======================================================================
TEST SUMMARY
======================================================================
test_geospatial_tools............................. ✅ PASS (1.8s)
test_context_enricher............................. ✅ PASS (3.4s)
test_geo_agent.................................... ✅ PASS (0.3s)
test_analyst_agent................................ ✅ PASS (16.6s)
test_agent_chain.................................. ✅ PASS (15.7s)
======================================================================
✅ ALL TESTS PASSED (37.7s total)
======================================================================

📝 Test log saved to: logs/test_summary.log
```

## 📁 Generated Files

After running tests, check these locations:

### Test Results (JSON)
```bash
ls -lh data/analysis/
# test_geospatial.json
# test_context_enricher.json
# test_geo_agent.json
# test_analyst_agent.json
# test_agent_chain.json
```

### Interactive Maps
```bash
ls -lh data/maps/
# Sudan_hotspot.html  (open in browser)
```

### Test Logs
```bash
tail -50 logs/test_summary.log
tail -50 logs/geo_agent.log
tail -50 logs/analyst_agent.log
```

## 🔍 View Test Results

### Geospatial Test Results
```bash
cat data/analysis/test_geospatial.json
```
```json
{
  "events_loaded": 6305,
  "clusters_found": 19,
  "map_path": "data/maps/Sudan_hotspot.html",
  "total_fatalities": 44569
}
```

### Agent Chain Results
```bash
cat data/analysis/test_agent_chain.json
```
```json
{
  "query": "Conflict escalation in Sudan 2022–2025",
  "analyst": {
    "historical_sources": 5,
    "web_sources": 0,
    "analysis_length": 11147
  },
  "geo": {
    "country": "Sudan",
    "n_events": 6305,
    "n_clusters": 19,
    "map_path": "data/maps/Sudan_hotspot.html"
  },
  "integration_status": "success"
}
```

## 🗺️ View Generated Map

```bash
# Open the interactive map in your browser
firefox data/maps/Sudan_hotspot.html
# or
google-chrome data/maps/Sudan_hotspot.html
# or
xdg-open data/maps/Sudan_hotspot.html
```

## 🐛 If Tests Fail

### Check Ollama Status
```bash
ollama list
# Should show available models like gpt-oss:20b
```

### Check Dependencies
```bash
pip3 list | grep -E "faiss|langchain|pandas|scikit-learn"
```

### View Detailed Errors
```bash
# Full test output saved to logs
cat logs/test_summary.log

# Check agent-specific logs
tail -100 logs/geo_agent.log
tail -100 logs/analyst_agent.log
```

## 🔧 Run Individual Tests

### Test Only Geospatial Tools
```python
python3 -c "
import sys
sys.path.insert(0, '.')
from tests.run_all_tests import test_geospatial_tools
result = test_geospatial_tools()
print(result)
"
```

### Test Only AnalystAgent
```python
python3 -c "
import sys
sys.path.insert(0, '.')
from tests.run_all_tests import test_analyst_agent
result = test_analyst_agent()
print(result)
"
```

## 📈 Performance Benchmarks

| Component | CPU Time | GPU Time | Notes |
|-----------|----------|----------|-------|
| Geospatial Tools | 1.8s | 1.5s | DBSCAN clustering |
| Context Enricher | 3.4s | 1.2s | FAISS + web search |
| GeoAgent | 0.3s | 0.2s | Without LLM generation |
| AnalystAgent | 16.6s | 8.2s | LLM-heavy |
| Agent Chain | 15.7s | 8.0s | Combined reasoning |
| **Total** | **37.7s** | **19.1s** | Full test suite |

## ✅ Success Indicators

- All 5 tests show ✅ PASS
- Exit code: 0
- JSON files created in `data/analysis/`
- Map created: `data/maps/Sudan_hotspot.html`
- No Python exceptions in output
- Test log updated: `logs/test_summary.log`

## ❌ Failure Indicators

- Any test shows ❌ FAIL
- Exit code: 1
- Detailed error traces printed
- Missing output files
- Python ModuleNotFoundError or ImportError

## 🔄 Continuous Testing

Add to your development workflow:

```bash
# Before committing code
python3 tests/run_all_tests.py && git commit -m "Your message"

# Watch mode (requires entr)
find core/ agents/ -name "*.py" | entr -c python3 tests/run_all_tests.py
```

## 📚 Next Steps

1. **Explore results**: Check JSON files in `data/analysis/`
2. **View map**: Open `data/maps/Sudan_hotspot.html` in browser
3. **Read logs**: Review `logs/test_summary.log`
4. **Modify tests**: Edit `tests/run_all_tests.py` for custom tests
5. **Add tests**: Follow the pattern in existing test functions

## 🆘 Need Help?

- **Documentation**: See `tests/README.md` for full details
- **Logs**: Check `logs/test_summary.log`
- **Agent logs**: `logs/geo_agent.log`, `logs/analyst_agent.log`
- **Issues**: Review error traces at end of test output

---

**Happy Testing! 🧪**

