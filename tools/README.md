# HAWK-AI Tools

Utility tools for HAWK-AI system monitoring, visualization, and debugging.

## Reasoning Viewer

Display HAWK-AI reasoning chains with detailed step-by-step breakdown.

### Features

- 🖥️ **CLI Mode**: Terminal-based reasoning chain display
- 🌐 **Streamlit Mode**: Interactive web-based visualization
- 📊 Displays all reasoning steps: patterns, hypotheses, evaluation, synthesis, and review
- ⏱️ Shows runtime metrics and model information
- 📥 Export reasoning data (Streamlit mode)

### Installation

Ensure Streamlit is installed for web UI mode:

```bash
pip install streamlit
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Usage

#### CLI Mode (Default)

```bash
# View reasoning from default location (data/analysis/last_reasoning.json)
python tools/reasoning_viewer.py

# Or with explicit CLI mode flag
python tools/reasoning_viewer.py --mode cli

# View from custom location
python tools/reasoning_viewer.py --data-path /path/to/reasoning.json
```

#### Streamlit Mode

```bash
# Launch web UI
python tools/reasoning_viewer.py --mode streamlit

# Or run directly with streamlit
streamlit run tools/reasoning_viewer.py
```

The Streamlit UI will open in your browser at `http://localhost:8501`

### Expected Data Format

The reasoning viewer expects JSON files with the following structure:

```json
{
  "query": "Your analysis query",
  "model": "Model name used",
  "timestamp": "ISO timestamp",
  "runtime_s": 45.2,
  "patterns": "Identified patterns...",
  "hypotheses": "Generated hypotheses...",
  "evaluation": "Hypothesis evaluation...",
  "synthesis": "Integrated analysis...",
  "review": "Quality review..."
}
```

### Output Example

**CLI Mode:**
```
🧠 HAWK-AI Reasoning Chain for: Analyze the geopolitical situation in Sudan
======================================================================

🔹 PATTERNS
----------------------------------------------------------------------
Analysis identified several key patterns:
1. Escalating Violence: ACLED data shows...
----------------------------------------------------------------------

🔹 HYPOTHESES
----------------------------------------------------------------------
Based on the identified patterns, several hypotheses emerge...
----------------------------------------------------------------------

⏱️  Total reasoning time: 45.2s
📊 Model: nous-hermes2:34b
```

**Streamlit Mode:**
- Interactive expandable sections for each reasoning step
- Syntax highlighting for JSON data
- Downloadable reasoning export
- Real-time metrics display

### Integration with HAWK-AI

To generate reasoning data that can be viewed with this tool, ensure your agents save their reasoning chains to `data/analysis/last_reasoning.json`.

#### Quick Integration

Use the helper function from `save_reasoning_example.py`:

```python
from tools.save_reasoning_example import save_reasoning_chain

# After your agent completes analysis
save_reasoning_chain(
    query="Your user query",
    model="model-name",
    patterns="Pattern recognition output...",
    hypotheses="Hypothesis formation output...",
    evaluation="Hypothesis evaluation output...",
    synthesis="Synthesis output...",
    review="Quality review output...",
    runtime_s=elapsed_time
)
```

#### Manual Integration

```python
import json
from datetime import datetime

reasoning_data = {
    "query": user_query,
    "model": model_name,
    "timestamp": datetime.now().isoformat(),
    "runtime_s": runtime,
    "patterns": patterns_analysis,
    "hypotheses": hypotheses_generated,
    "evaluation": evaluation_results,
    "synthesis": synthesis_output,
    "review": quality_review
}

with open("data/analysis/last_reasoning.json", "w") as f:
    json.dump(reasoning_data, f, indent=2)
```

#### Try the Example

Run the included example to see how it works:

```bash
# Generate example reasoning data
python3 tools/save_reasoning_example.py

# View the results
make reasoning
# or
python3 tools/reasoning_viewer.py
```

### Troubleshooting

**"No reasoning file found"**
- Ensure you've run a HAWK-AI analysis that generates reasoning output
- Check that the file exists at `data/analysis/last_reasoning.json`
- Use `--data-path` to specify a different location

**Streamlit import error**
- Install streamlit: `pip install streamlit`
- The tool will fall back to CLI mode if Streamlit is unavailable

**JSON parsing error**
- Verify the reasoning file contains valid JSON
- Check that all required fields are present

## Future Tools

Additional monitoring and debugging tools will be added:

- Agent performance metrics viewer
- Vector store inspector
- Memory graph visualizer
- Real-time log aggregator

