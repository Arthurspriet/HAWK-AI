# Reasoning Viewer Quick Start

## 🚀 Quick Commands

```bash
# Generate example reasoning data
python3 tools/save_reasoning_example.py

# View in terminal (CLI mode)
make reasoning

# View in web browser (Streamlit UI)
make reasoning-ui

# Or use directly
python3 tools/reasoning_viewer.py --mode cli
python3 tools/reasoning_viewer.py --mode streamlit
```

## 📝 Integrate Into Your Agent

```python
from tools.save_reasoning_example import save_reasoning_chain
import time

# Your agent code here...
start = time.time()

# ... perform analysis ...

# Save reasoning chain
save_reasoning_chain(
    query="Your query",
    model="your-model-name",
    patterns="Pattern recognition output",
    hypotheses="Hypothesis formation output",
    evaluation="Hypothesis evaluation output",
    synthesis="Synthesis output",
    review="Quality review output",
    runtime_s=time.time() - start
)

# Then view with: make reasoning
```

## 🎯 What Each Step Shows

- **🔍 PATTERNS**: What patterns were identified in the data
- **💡 HYPOTHESES**: What hypotheses were formed from patterns
- **⚖️ EVALUATION**: How hypotheses were evaluated with confidence scores
- **🔗 SYNTHESIS**: Integrated analysis combining all findings
- **✅ REVIEW**: Quality assurance and recommendations

## 📍 Files

- **Viewer**: `tools/reasoning_viewer.py`
- **Example**: `tools/save_reasoning_example.py`
- **Data**: `data/analysis/last_reasoning.json`
- **Docs**: `tools/README.md`

## 🐛 Troubleshooting

**"No reasoning file found"**
```bash
# Generate example data first
python3 tools/save_reasoning_example.py
```

**"Streamlit not found"**
```bash
# Install streamlit
pip install streamlit
# Or reinstall all dependencies
make setup
```

## 📚 Learn More

See `tools/README.md` for complete documentation.

