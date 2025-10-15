# 🦅 HAWK-AI

**H**ighly **A**daptive **W**eb **K**nowledge **A**nalysis & **I**ntelligence Agent

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-blue)](https://www.langchain.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple)](https://ollama.ai/)

A fully local, privacy-focused OSINT (Open-Source Intelligence) analysis system powered by Ollama models with vectorized historical knowledge (ACLED), real-time web search, geospatial analysis, code execution, and multi-agent orchestration.

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Examples Showcase](#-examples-showcase)
- [Reasoning Viewer](#-reasoning-viewer)
- [Individual Examples](#-individual-examples)
- [Multi-Agent System](#-multi-agent-system)
- [Configuration](#-configuration)
- [Data Sources](#-data-sources)
- [Security](#-security)
- [Use Cases](#-use-cases)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🌟 Features

- **🔍 Web Search**: DuckDuckGo integration with intelligent caching for real-time OSINT gathering
- **📊 Data Analysis**: Advanced ACLED conflict data analysis with FAISS-powered semantic search (868K+ events)
- **🗺️ Geospatial Analysis**: DBSCAN clustering and interactive hotspot map generation
- **💻 Code Execution**: Sandboxed Python code execution for data manipulation and visualization
- **📝 Text Processing**: Intelligent summarization and executive brief generation
- **🤖 Multi-Agent System**: 5 specialized agents (Supervisor, Search, Analyst, Geo, CodeExec) working in parallel
- **🌍 Global Coverage**: 258 country profiles (CIA Factbook) + regional conflict data
- **📈 Local Tracking**: Comprehensive logging and session management
- **🔒 Privacy-First**: Runs entirely offline with local Ollama models - your data never leaves your machine

## 🏗️ Architecture

```
HAWK-AI/
├── main.py                 # Main entry point
├── config/                 # Configuration files
│   ├── settings.yaml      # System settings
│   └── sources.yaml       # Data sources config
├── core/                  # Core system components
│   ├── orchestrator.py    # Task orchestration
│   ├── agent_registry.py  # Agent management
│   ├── local_tracking.py  # Logging & tracking
│   ├── vector_store.py    # FAISS vector database
│   ├── ollama_client.py   # Ollama model client
│   └── tools_*.py         # Specialized tools
├── agents/                # Specialized agents
│   ├── supervisor_agent.py    # Coordinates all agents
│   ├── search_agent.py        # Web search operations
│   ├── analyst_agent.py       # Data analysis
│   ├── redactor_agent.py      # Text processing
│   └── codeexec_agent.py      # Code execution
└── data/                  # Data storage
    ├── vector_index/      # FAISS indexes
    └── historical_context/ # ACLED data
```

## ⚡ Quick Start

Get HAWK-AI running in 3 steps:

```bash
# 1. Install dependencies
make setup

# 2. Build vector database (one-time, ~5-10 minutes)
make db

# 3. Start analyzing!
make run
```

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **Ollama** installed and running at `127.0.0.1:11434`
  ```bash
  # Install Ollama from https://ollama.ai
  ollama serve
  ollama pull magistral:latest  # or your preferred model
  ollama pull snowflake-arctic-embed2:568m  # for embeddings
  ```
- **(Optional)** NVIDIA GPU for faster vector operations

### Detailed Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd HAWK-AI

# Create virtual environment and install dependencies
make setup

# Build vector database from ACLED data
# This indexes 868K+ conflict events and 258 country profiles
make db

# Validate installation
python validate_setup.py

# Run HAWK-AI
make run
```

## 🚀 Usage

### Interactive Mode (Default)

```bash
python main.py --chat
```

Or simply:

```bash
python main.py
```

This launches an interactive chat interface where you can:
- Ask questions
- Request analyses
- Execute searches
- Run code
- Get summaries

### Single Query Mode

```bash
python main.py "Analyze conflict patterns in Sudan since 2023"
```

Save output to file:

```bash
python main.py "Search for latest protests in Kenya" -o results.txt
```

### Development Mode

```bash
python main.py --dev
```

Shows system status and configuration.

### Check System Status

```bash
python main.py --status
```

## 🎬 Examples Showcase

### Run All Capability Demonstrations

HAWK-AI includes a comprehensive showcase demonstrating all agent capabilities:

```bash
# Run all 7 capability examples
python examples_showcase.py

# Run specific example (1-7)
python examples_showcase.py --example 3

# List all available examples
python examples_showcase.py --list
```

**The showcase demonstrates:**
1. 🎯 **Multi-Agent Intelligence Synthesis** - Supervisor coordinating parallel agents
2. 🔍 **Real-Time Web Intelligence + Historical Context** - Web search + ACLED fusion
3. 🗺️ **Geospatial Hotspot Analysis** - DBSCAN clustering + interactive maps
4. 📊 **Temporal Pattern Analysis** - Statistical analysis across 868K+ events
5. 💻 **Code Execution for Data Analysis** - Sandboxed Python execution
6. 📝 **Executive Brief Generation** - Professional report creation
7. 🧠 **Reasoning Chain with Reflection** - Structured analytical reasoning

**Output artifacts:**
- Interactive hotspot maps in `data/maps/`
- Reasoning chains in `data/analysis/`
- Comprehensive session logs in `logs/`

---

## 🧠 Reasoning Viewer

Visualize HAWK-AI's step-by-step reasoning process with the built-in reasoning viewer:

```bash
# CLI mode (terminal output)
python tools/reasoning_viewer.py

# Web UI mode (interactive Streamlit dashboard)
python tools/reasoning_viewer.py --mode streamlit

# View specific reasoning file
python tools/reasoning_viewer.py --data-path data/analysis/custom_reasoning.json
```

**The reasoning viewer displays:**
- 🔍 **Pattern Recognition** - Identified patterns in data
- 💡 **Hypothesis Formation** - Generated hypotheses
- ⚖️ **Evaluation** - Evidence-based hypothesis assessment
- 🔗 **Synthesis** - Integrated analysis
- ✅ **Review** - Quality assurance and recommendations

**Quick Start:**
```bash
# 1. Run an example to generate reasoning data
python examples_showcase.py --example 7

# 2. View the reasoning chain
python tools/reasoning_viewer.py

# 3. Or use the web interface
python tools/reasoning_viewer.py --mode streamlit
```

See `tools/README.md` for detailed reasoning viewer documentation.

---

## 💡 Individual Examples

### 🎯 Intelligence Analysis (Supervisor Agent)
The Supervisor automatically detects intent and coordinates multiple agents:

```bash
python main.py "Conflict escalation and hotspots in Sudan 2022-2025"
```
**What happens**: Supervisor detects geographic + analytical query → Runs GeoAgent (generates map) + AnalystAgent (historical analysis) in parallel → Synthesizes comprehensive intelligence brief

**Output**: 
- Interactive hotspot map (`data/maps/Sudan_hotspot.html`)
- Executive summary with temporal patterns
- Key findings and risk factors
- Structured JSON report

---

### 🔍 Real-Time Web Intelligence
```bash
python main.py "Latest news about conflict in Yemen today"
```
**Agents triggered**: SearchAgent + AnalystAgent  
**Output**: Current news merged with historical ACLED context

---

### 🗺️ Geospatial Analysis
```bash
python agents/geo_agent.py --country Nigeria --years 3
```
**Output**: 
- DBSCAN clustering of conflict events
- Interactive map with color-coded hotspots
- Cluster statistics and spatial summary

---

### 📊 Temporal Pattern Analysis
```bash
python main.py "Analyze escalation trends in the Sahel region"
```
**Agents triggered**: AnalystAgent  
**Output**: Statistical analysis of temporal patterns from 868K+ conflict events

---

### 💻 Data Manipulation
```bash
python main.py "Execute code to analyze top 10 countries by conflict events"
```
**Agents triggered**: CodeExec + Analyst  
**Output**: Code execution results with data analysis

## 🧩 Multi-Agent System

HAWK-AI uses a sophisticated multi-agent architecture where specialized agents work in parallel, coordinated by a central supervisor.

### 🎯 Supervisor Agent
The central orchestration layer that:
- **Semantic Intent Detection**: Automatically routes queries to appropriate agents
- **Parallel Execution**: Runs multiple agents simultaneously using ThreadPoolExecutor
- **Synthesis**: Combines multi-agent outputs into cohesive intelligence briefs
- **Report Export**: Saves structured JSON reports to `data/analysis/`

**Example**: Query "Conflict escalation and hotspots in Sudan" triggers both GeoAgent + AnalystAgent in parallel.

### 🔍 Search Agent
Real-time web intelligence gathering:
- DuckDuckGo integration with intelligent query reformulation
- Local caching system for repeated queries (`data/web_cache/`)
- FAISS vectorization of search results for semantic ranking
- Content deduplication and relevance scoring

### 📊 Analyst Agent
Historical context + web fusion analysis:
- Retrieves relevant ACLED data via FAISS semantic search
- Merges historical intelligence with current web context
- LLM-powered analytical reasoning with temporal/political nuance
- Generates executive summaries with key findings and implications

### 🗺️ Geo Agent
Geospatial analysis and hotspot detection:
- ACLED data loading and country/time filtering
- DBSCAN clustering algorithm for geographic hotspot identification
- Interactive Folium maps with color-coded event markers
- Spatial reasoning and regional analysis via LLM

### 💻 Code Execution Agent
Sandboxed computational analysis:
- Safely executes Python code in isolated subprocess
- Whitelist-based import restrictions (pandas, numpy, matplotlib, etc.)
- Network isolation and timeout enforcement (30s default)
- Output validation and formatting

### 📝 Redactor Agent
Professional report generation:
- Executive brief creation
- Intelligent summarization and key point extraction
- Sensitive information redaction
- Multi-format output support

## 🔧 Configuration

### `config/settings.yaml`

```yaml
ollama:
  host: "127.0.0.1"
  port: 11434
  model_default: "gpt-oss:20b"       # Your LLM model
  embed_model: "snowflake-arctic-embed2:568m"  # Embedding model

vector_store:
  path: "data/vector_index"
  use_gpu: true                       # Use GPU for FAISS

tracking:
  langsmith_enabled: true
  project_name: "HAWK-AI-local"
```

### Supported Models

- **LLM**: Any Ollama model (magistral, llama3, mixtral, gpt-oss, etc.)
- **Embeddings**: snowflake-arctic-embed2, nomic-embed-text, etc.

## 📊 Data Sources

### ACLED (Armed Conflict Location & Event Data)

Place ACLED CSV files in `historical_context/ACLED/`:
- Regional datasets (Africa, Middle East, Asia-Pacific, etc.)
- Event-level data with:
  - Event types and dates
  - Geographic information
  - Actor data
  - Fatality counts

### CIA World Factbook

Place CIA World Factbook data in `historical_context/CIA_FACTS/`:
- Country profiles with comprehensive information
- Demographics and population data
- Government and political structure
- Economic indicators
- Military and security information
- Geography and natural resources
- Supports both JSON and CSV formats

### Rebuild Vector Index

After adding new data sources:

```bash
make db
```

Or rebuild manually:

```bash
# Rebuild all sources
python core/vector_store.py --rebuild

# Ingest ACLED data only
python core/vector_store.py --ingest-acled

# Ingest CIA World Factbook data only
python core/vector_store.py --ingest-cia-facts
```

## 📈 Tracking & Logging

All operations are logged to:
- `logs/session_YYYYMMDD_HHMMSS.jsonl` - Detailed session logs
- `logs/hawk_ai.log` - Application logs
- `data/analysis/last_reasoning.json` - Latest reasoning chain output

View session history:
```
> history
```

## 🛠️ Development

### Run Tests
```bash
make test
```

### Clean Environment
```bash
make clean
```

### Project Structure

- **Core Modules**: Reusable system components
- **Agents**: Specialized task executors
- **Tools**: Domain-specific functionality
- **Config**: YAML-based configuration
- **Data**: Vector indexes and source data

## 🔐 Security

- **Sandboxed Execution**: Code runs in isolated subprocess
- **Import Whitelisting**: Only approved libraries allowed
- **No Network in Sandbox**: Code execution is network-isolated
- **Input Validation**: All code validated before execution
- **Sensitive Data Redaction**: Automatic PII redaction capability

## 🎯 Use Cases

### 🔬 Research & Analysis
- **Conflict Research**: Study temporal and spatial patterns in 868K+ conflict events
- **Academic Research**: Analyze sociopolitical trends with historical context
- **Policy Analysis**: Generate evidence-based intelligence briefs
- **Threat Assessment**: Identify escalation patterns and emerging hotspots

### 📰 Intelligence Gathering
- **OSINT Analysis**: Combine web intelligence with historical data
- **News Monitoring**: Track current events with automated contextual analysis
- **Geopolitical Analysis**: Multi-source intelligence fusion for regional assessments

### 📊 Data Operations
- **Data Exploration**: Semantic search across 868K+ events + 258 country profiles
- **Report Generation**: Automated executive summaries and professional briefs
- **Visualization**: Interactive maps and statistical analysis
- **Code Execution**: Custom data analysis with sandboxed Python

### 🛡️ Security & Humanitarian
- **Humanitarian Planning**: Identify high-risk areas and emerging crises
- **Risk Assessment**: Analyze conflict dynamics and civilian impact
- **Early Warning**: Detect escalation patterns and geographic hotspots

## 📋 Requirements

See `requirements.txt` for full dependencies:

- `crewai[tools]` - Agent framework
- `langgraph` - Agent orchestration
- `langchain-ollama` - Ollama integration
- `faiss-gpu-cu12` - Vector database
- `sentence-transformers` - Embeddings
- `duckduckgo-search` - Web search
- `pandas`, `numpy` - Data processing
- `rich` - Terminal UI

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Adding New Agents
Create a new agent in `agents/` that inherits from the base agent pattern:
```python
# agents/your_agent.py
from langchain_ollama import OllamaLLM
class YourAgent:
    def __init__(self, model="magistral:latest"):
        self.llm = OllamaLLM(model=model, base_url="http://127.0.0.1:11434")
```

### Adding Data Sources
1. Place data files in `historical_context/YOUR_SOURCE/`
2. Update `config/sources.yaml`
3. Add ingestion logic to `core/vector_store.py`
4. Rebuild index: `make db`

### Improving Agents
- Enhance analysis algorithms
- Add new tools and capabilities
- Improve error handling
- Optimize performance

### Testing
```bash
# Run existing tests
make test

# Add your tests to tests/
python tests/run_all_tests.py
```

**Please ensure**:
- Code follows existing patterns
- Security measures are maintained
- Documentation is updated
- Changes are tested

## 📄 License

This project is for research and educational purposes. See [LICENSE](LICENSE) for details.

**Important**: ACLED data is subject to [ACLED Terms of Use](https://acleddata.com/terms-of-use/). If you use HAWK-AI for research, please cite ACLED appropriately.

## 🙏 Acknowledgments

- **ACLED** for conflict data
- **Ollama** for local model serving
- **LangChain** for agent framework
- **FAISS** for vector search

## 🆘 Troubleshooting

### Ollama Connection Error
```bash
# Ensure Ollama is running
ollama serve

# Check available models
ollama list
```

### Vector Store Issues
```bash
# Rebuild vector index
make db
```

### GPU Not Detected
Set `use_gpu: false` in `config/settings.yaml`

### Import Errors
```bash
# Reinstall dependencies
make clean
make setup
```

## 📞 Getting Help

### Debugging Steps
1. **Check logs**: `tail -f logs/hawk_ai.log`
2. **Validate setup**: `python validate_setup.py`
3. **Verify Ollama**: 
   ```bash
   ollama list  # Check available models
   ollama serve  # Ensure Ollama is running
   ```
4. **Check configuration**: Review `config/settings.yaml`
5. **Use dev mode**: `python main.py --dev`

### Common Issues

**"No module named 'faiss'"**
```bash
source .venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt  # Reinstall dependencies
```

**"Connection refused" (Ollama)**
```bash
# Start Ollama service
ollama serve

# Verify it's running
curl http://127.0.0.1:11434/api/tags
```

**"Vector index not found"**
```bash
# Rebuild vector database
make db
```

### Performance Tips
- Use GPU acceleration: Set `use_gpu: true` in `config/settings.yaml` (requires NVIDIA GPU)
- Smaller models for faster inference: `qwen:7b`, `mistral:7b`
- Larger models for better quality: `magistral:latest`, `llama3:70b`

### Need More Help?
- 📖 Check `tests/README.md` for testing documentation
- 🐛 Report issues on GitHub
- 💬 Review logs in `logs/` directory for detailed error messages

---

## ⭐ Show Your Support

If you find HAWK-AI useful, please give it a star! ⭐

---

**Built with 🦅 for local, private, and powerful OSINT analysis**

*Your intelligence, your data, your machine.*

