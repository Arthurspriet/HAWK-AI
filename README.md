# 🦅 HAWK-AI

**H**ighly **A**daptive **W**eb **K**nowledge **A**nalysis & **I**ntelligence Agent

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-blue)](https://www.langchain.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple)](https://ollama.ai/)

A fully local, privacy-focused multi-agent OSINT (Open-Source Intelligence) analysis system powered by Ollama models with advanced analytical reasoning, multi-source data fusion, geospatial analysis, code execution, and meta-cognitive reflection capabilities.

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Multi-Agent System](#-multi-agent-system)
- [Analytical Frameworks](#-analytical-frameworks)
- [Data Sources & Context Fusion](#-data-sources--context-fusion)
- [Examples Showcase](#-examples-showcase)
- [Reasoning Viewer](#-reasoning-viewer)
- [Configuration](#-configuration)
- [Memory & Collaboration](#-memory--collaboration)
- [Security](#-security)
- [Use Cases](#-use-cases)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Features

### Core Intelligence Capabilities
- **🧠 Multi-Agent Orchestration**: 6 specialized agents (Supervisor, Search, Analyst, Geo, CodeExec, Redactor, Reflection) working in parallel with intelligent coordination
- **🔍 Real-Time Web Intelligence**: DuckDuckGo integration with intelligent caching and semantic ranking
- **📊 Multi-Source Data Fusion**: Weighted fusion from 5 data sources (ACLED, CIA Factbook, Freedom World, IMF, World Bank) with reliability-based scoring
- **🗺️ Geospatial Analysis**: DBSCAN clustering and interactive hotspot map generation with Folium
- **💻 Sandboxed Code Execution**: Safe Python execution for data manipulation and visualization
- **🧩 Meta-Cognitive Reflection**: Self-evaluation, consistency checking, and adaptive re-execution

### Web Interface & API
- **🌐 REST API Server**: FastAPI-based API with OpenAI-compatible endpoints
- **💬 Open WebUI Integration**: Beautiful web chat interface with real-time streaming
- **🔄 Streaming Responses**: Server-Sent Events (SSE) for progressive output and agent progress updates
- **📡 OpenAI-Compatible**: Drop-in replacement for OpenAI API endpoints (`/v1/chat/completions`)
- **🎨 Real-Time Agent Transparency**: See which agents are working and their contributions in real-time
- **🔌 Easy Integration**: Standard REST API for integration with any frontend or application

### Advanced Analytical Features
- **🎯 Structured Reasoning Framework**: Pattern extraction → Hypothesis generation → Evaluation → Synthesis → Critical review
- **📐 Military Intelligence Frameworks**: PMESII, DIME, and SWOT framework integration
- **🔗 Context Orchestration**: Automatic detection of relevant data sources and analytical frameworks based on query intent
- **⚖️ Consistency Analysis**: Cross-validation between structural data (CIA/IMF) and event data (ACLED)
- **💾 Memory Management**: Persistent inter-agent memory for historical reasoning and collaboration
- **📈 Confidence Scoring**: Automatic quality assessment with adaptive agent re-runs for low-confidence results

### Data & Scale
- **🌍 Global Coverage**: 1M+ conflict events (ACLED) + 258 country profiles (CIA) + economic indicators (IMF/WBI) + freedom indices
- **🔄 Parallel Execution**: ThreadPoolExecutor-based concurrent agent execution
- **📦 FAISS Vector Search**: GPU-accelerated semantic search across millions of data points
- **🔒 Privacy-First**: Runs entirely offline with local Ollama models - your data never leaves your machine

---

## 🏗️ Architecture

```
HAWK-AI/
├── main.py                      # Main entry point with CLI/interactive modes
├── api_server.py               # FastAPI REST API server with streaming
├── config/
│   ├── agents.yaml             # Agent model assignments & thinking modes
│   ├── settings.yaml           # System configuration (Ollama, FAISS, etc.)
│   └── sources.yaml            # Data source configuration
├── core/                       # Core system components
│   ├── orchestrator.py         # Task orchestration & routing (streaming support)
│   ├── agent_registry.py       # Agent management system
│   ├── vector_store.py         # FAISS vector database (5 sources)
│   ├── context_fusion.py       # Multi-source weighted fusion
│   ├── context_orchestrator.py # Automatic source/framework selection
│   ├── memory_manager.py       # Persistent inter-agent memory
│   ├── analytical_frameworks.py # PMESII, DIME, SWOT frameworks
│   ├── streaming_formatter.py  # SSE formatting for streaming responses
│   ├── config_loader.py        # Configuration management
│   └── tools_*.py              # Specialized tool implementations
├── agents/                     # Specialized agent implementations
│   ├── supervisor_agent.py     # Central coordinator (parallel execution + progress callbacks)
│   ├── analyst_agent.py        # Structured reasoning & analysis
│   ├── search_agent.py         # Web intelligence gathering
│   ├── geo_agent.py            # Geospatial analysis & clustering
│   ├── codeexec_agent.py       # Sandboxed code execution
│   ├── redactor_agent.py       # Report generation & summarization
│   └── reflection_agent.py     # Meta-reasoning & quality control
├── data/
│   ├── vector_index/           # FAISS indexes (multi-source)
│   ├── web_cache/              # Search result caching
│   ├── analysis/               # Generated reports & reasoning chains
│   ├── maps/                   # Interactive geospatial maps
│   └── memory/                 # Agent collaboration memory
├── historical_context/         # Data sources (5 integrated sources)
│   ├── ACLED/                  # Conflict event data (1M+ events)
│   ├── CIA_FACTS/              # 258 country profiles
│   ├── FREEDOM_WORLD/          # Democracy & freedom indices
│   ├── IMF/                    # Economic indicators & forecasts
│   └── WBI/                    # World Bank socio-economic data
├── open-webui/                 # Integrated web chat interface (git submodule)
├── script/                     # Service management scripts
│   ├── start_hawk.sh           # Start all services
│   ├── stop_hawk.sh            # Stop all services
│   └── test_integration.sh     # Test web integration
└── tools/                      # Analysis & visualization tools
    ├── reasoning_viewer.py     # CLI/Streamlit reasoning visualization
    └── save_reasoning_example.py
```

### System Flow

```
User Query
    ↓
Orchestrator (Intent Detection)
    ↓
Context Orchestrator (Source/Framework Selection)
    ↓
Supervisor Agent (Parallel Coordination)
    ↓
┌─────────────────────────────────────────┐
│  Parallel Agent Execution (ThreadPool)  │
├─────────────────────────────────────────┤
│  • SearchAgent → Web Intelligence      │
│  • AnalystAgent → Multi-source Fusion  │
│  • GeoAgent → Spatial Analysis         │
│  • CodeExecAgent → Data Processing     │
└─────────────────────────────────────────┘
    ↓
Context Fusion (Weighted Multi-source Integration)
    ↓
Reflection Agent (Quality Assessment & Consistency Check)
    ↓
┌─────────────────────────────────┐
│  If Confidence < 0.7:           │
│  → Re-run low-confidence agents │
│  → Re-evaluate                  │
└─────────────────────────────────┘
    ↓
Synthesis & Report Generation
    ↓
Memory Manager (Store for future collaboration)
    ↓
User Response + Artifacts (maps, reports, reasoning chains)
```

---

## ⚡ Quick Start

### Option 1: Web Interface (Recommended)

Get HAWK-AI with web chat interface running in 4 steps:

```bash
# 1. Install dependencies
make setup

# 2. Build vector database (one-time, ~10-15 minutes for all sources)
make db

# 3. Start all services (API + Open WebUI)
make hawk

# 4. Open browser to http://localhost:5173
```

### Option 2: CLI Mode

For command-line usage:

```bash
# 1. Install dependencies
make setup

# 2. Build vector database
make db

# 3. Start interactive CLI
make run
```

### Option 3: API Server Only

To use the REST API for custom integration:

```bash
# Start API server with auto-reload
make api

# API docs available at: http://127.0.0.1:8000/docs
```

---

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **Ollama** installed and running at `127.0.0.1:11434`
  ```bash
  # Install Ollama from https://ollama.ai
  ollama serve
  
  # Pull required models (see config/agents.yaml for current models)
  ollama pull magistral:latest          # Supervisor
  ollama pull gpt-oss:20b              # Analyst
  ollama pull qwen2.5:7b               # Search
  ollama pull mixtral:8x7b             # Code execution
  ollama pull nous-hermes2:34b         # Reflection
  ollama pull wizardlm-uncensored:13b  # Redactor
  
  # Embedding models
  ollama pull snowflake-arctic-embed2:568m
  ```
- **(Optional)** NVIDIA GPU for faster vector operations

### Detailed Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd HAWK-AI

# Create virtual environment and install dependencies
make setup

# Build vector database from all data sources
# This indexes: ACLED (1M+ events), CIA (258 countries), 
#               Freedom World, IMF economic data, World Bank indicators
make db

# Build individual sources (optional)
make db-acled      # ACLED conflict data only
make db-cia        # CIA World Factbook only
make db-wbi        # World Bank indicators only

# Validate installation
python validate_setup.py

# Run HAWK-AI
make run
```

---

## 🚀 Usage

### Web Interface (Recommended)

Start the complete web interface with streaming chat:

```bash
# Start all services (API + Open WebUI)
make hawk

# Or manually:
# Terminal 1: Start API server
make api

# Terminal 2: Start Open WebUI (if integrated)
cd open-webui && npm run dev
```

Access the interface at: **http://localhost:5173**

**Features:**
- 💬 Real-time streaming chat interface
- 🎨 Beautiful, modern UI with dark mode
- 📊 Agent transparency (see which agents are working)
- 🗺️ Interactive maps and visualizations
- 📁 File upload support (documents, data)
- 💾 Persistent chat history
- 🔄 Progressive streaming responses

**Stop all services:**
```bash
make stop
```

### REST API Mode

Use the API for custom integrations:

```bash
# Start API server
make api

# Access API documentation
# http://127.0.0.1:8000/docs (Swagger UI)
# http://127.0.0.1:8000/redoc (ReDoc)
```

**API Endpoints:**
- `POST /chat` - Send query to HAWK-AI (with streaming support)
- `POST /v1/chat/completions` - OpenAI-compatible endpoint
- `GET /v1/models` - List available HAWK-AI agents
- `GET /status` - System status
- `GET /health` - Health check
- `GET /history` - Session history

**Example API call with streaming:**
```bash
curl -N -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze tensions in Sudan",
    "stream": true
  }'
```

**Example OpenAI-compatible call:**
```bash
curl -N -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Analyze tensions in Sudan"}],
    "model": "hawk-ai-supervisor",
    "stream": true
  }'
```

### Interactive CLI Mode

Traditional command-line interface:

```bash
python main.py --chat
# or simply
python main.py
```

This launches an interactive chat interface where you can:
- Ask analytical questions
- Request multi-agent analyses
- Execute searches and code
- Generate executive briefs
- View reasoning chains

**Available Commands:**
- `help` - Show available commands
- `status` - System status and configuration
- `history` - View session history
- `clear` - Clear screen
- `exit/quit` - Exit HAWK-AI

### Single Query Mode

```bash
python main.py "Analyze conflict escalation patterns in Sudan since 2023"
```

Save output to file:

```bash
python main.py "Provide intelligence brief on Yemen situation" -o report.txt
```

### Development Mode

```bash
python main.py --dev
```

Shows system status, model configuration, and available agents.

---

## 🧩 Multi-Agent System

HAWK-AI uses a sophisticated multi-agent architecture with specialized roles and parallel execution.

### 🎯 Supervisor Agent

**Central orchestration layer:**
- **Semantic Intent Detection**: Automatically routes queries to appropriate agents
- **Parallel Execution**: Runs multiple agents simultaneously using ThreadPoolExecutor
- **Context Orchestration**: Selects relevant data sources and analytical frameworks
- **Synthesis**: Combines multi-agent outputs into cohesive intelligence briefs
- **Report Export**: Saves structured JSON reports with full reasoning traces

**Example routing:**
```python
Query: "Conflict escalation and hotspots in Sudan"
→ Detects: geographic (map) + analytical (trends) + search (current)
→ Triggers: GeoAgent + AnalystAgent + SearchAgent (parallel)
→ Synthesizes: Unified intelligence brief with map + analysis + context
```

### 📊 Analyst Agent

**Structured analytical reasoning:**

1. **Pattern Extraction**: Identifies actors, causes, and causal relationships
2. **Hypothesis Generation**: Formulates 2-3 possible explanations
3. **Hypothesis Evaluation**: Assesses plausibility and evidence
4. **Synthesis**: Integrates hypotheses with analytical frameworks (PMESII/DIME)
5. **Critical Review**: Identifies logical gaps and missing variables

**Multi-source fusion:**
- Retrieves context from ACLED (events), CIA (structure), IMF (economy), Freedom World (governance)
- Applies weighted scoring based on source reliability
- Cross-validates structural vs. event data for consistency

**Model**: `gpt-oss:20b` (configurable in `config/agents.yaml`)

### 🔍 Search Agent

**Real-time web intelligence:**
- DuckDuckGo integration with intelligent query reformulation
- Local caching system (`data/web_cache/`) with content hashing
- FAISS vectorization of search results for semantic ranking
- Content deduplication and relevance scoring

**Model**: `qwen2.5:7b`

### 🗺️ Geo Agent

**Geospatial analysis and hotspot detection:**
- ACLED data loading with country/time filtering
- DBSCAN clustering algorithm for geographic hotspot identification
- Interactive Folium maps with color-coded event markers
- Cluster statistics and spatial reasoning via LLM

**Outputs**: `data/maps/{Country}_hotspot.html`

**Model**: `magistral:latest`

### 💻 Code Execution Agent

**Sandboxed computational analysis:**
- Safely executes Python code in isolated subprocess
- Whitelist-based import restrictions (pandas, numpy, matplotlib, seaborn, sklearn, scipy)
- Network isolation and timeout enforcement (30s default)
- Output validation and error handling

**Model**: `mixtral:8x7b`

### 📝 Redactor Agent

**Professional report generation:**
- Executive brief creation with structured formatting
- Intelligent summarization and key point extraction
- Sensitive information redaction capabilities
- Multi-format output support

**Model**: `wizardlm-uncensored:13b`

### 🧩 Reflection Agent

**Meta-cognitive quality control:**
- **Coherence Analysis**: Evaluates consistency across agent outputs
- **Confidence Scoring**: Assigns overall confidence (0-1) to results
- **Contradiction Detection**: Identifies conflicts in findings
- **Consistency Check**: Cross-validates structural (CIA/IMF) vs. event (ACLED) data
- **Adaptive Re-execution**: Recommends re-running agents if confidence < 0.7

**Example reflection output:**
```json
{
  "confidence": 0.88,
  "contradictions": [],
  "rerun": [],
  "consistency_check": {
    "overall_stability": "Deteriorating",
    "contradictions": ["Stable governance indicators but increasing unrest events"],
    "alignment_summary": "Economic decline correlates with rising protests"
  }
}
```

**Model**: `nous-hermes2:34b`

---

## 📐 Analytical Frameworks

HAWK-AI implements military and intelligence analytical frameworks for structured reasoning.

### PMESII Framework

**Political, Military, Economic, Social, Information, Infrastructure**

Used for comprehensive stability assessments:

```python
# Automatically selected for: conflict, security, instability queries
Query: "Assess stability in Syria"
→ Framework: PMESII
→ Output: Structured analysis across all 6 domains
```

### DIME Framework

**Diplomatic, Information, Military, Economic**

Used for strategic power analysis:

```python
# Automatically selected for: economy, finance, diplomacy queries
Query: "Analyze economic leverage in Ukraine situation"
→ Framework: DIME
→ Output: Power dynamics across 4 vectors
```

### SWOT Framework

**Strengths, Weaknesses, Opportunities, Threats**

Used for risk and scenario forecasting:

```python
# Automatically selected for: risk, forecast, scenario queries
Query: "Risk assessment for Horn of Africa region"
→ Framework: SWOT
→ Output: Strategic risk matrix
```

### Context Orchestrator

The `ContextOrchestrator` automatically selects:
1. **Relevant Data Sources** based on query theme
2. **Appropriate Framework** based on analytical intent

**Example automatic selection:**

| Query Theme | Data Sources | Framework |
|------------|-------------|-----------|
| Conflict/Security | ACLED + CIA_FACTS + FREEDOM_WORLD | PMESII |
| Economic/Finance | IMF + WBI + CIA_FACTS | DIME |
| Governance/Democracy | FREEDOM_WORLD + CIA_FACTS + IMF | PMESII |
| Development/Social | WBI + CIA_FACTS + FREEDOM_WORLD | SWOT |

---

## 📊 Data Sources & Context Fusion

HAWK-AI integrates 5 complementary data sources with intelligent fusion.

### Available Data Sources

#### 1. ACLED (Armed Conflict Location & Event Data)
- **Coverage**: 1M+ conflict events globally (up to Aug 2025)
- **Regions**: Africa, Middle East, Asia-Pacific, Europe-Central Asia, Latin America, US-Canada
- **Data**: Event types, dates, locations, actors, fatalities, detailed notes
- **Reliability Weight**: 0.5 (event-based, volatile)
- **Path**: `historical_context/ACLED/`

#### 2. CIA World Factbook
- **Coverage**: 258 country profiles
- **Data**: Demographics, government structure, economic indicators, military, geography, resources
- **Reliability Weight**: 0.6 (structural, long-term)
- **Path**: `historical_context/CIA_FACTS/`

#### 3. Freedom in the World
- **Coverage**: Democracy and freedom indices (2013-2025)
- **Data**: Political rights, civil liberties, freedom scores, regime type
- **Reliability Weight**: 0.6 (institutional, moderate confidence)
- **Path**: `historical_context/FREEDOM_WORLD/`

#### 4. IMF World Economic Outlook
- **Coverage**: Global economic indicators and forecasts
- **Data**: GDP, inflation, debt, trade balance, fiscal data
- **Reliability Weight**: 0.75 (high reliability, quantitative)
- **Path**: `historical_context/IMF/`

#### 5. World Bank Indicators
- **Coverage**: Socio-economic development indicators
- **Data**: GDP growth, per capita income, PPP, development metrics
- **Reliability Weight**: 0.7 (robust, socio-economic fundamentals)
- **Path**: `historical_context/WBI/`

### Context Fusion Algorithm

The `context_fusion.py` module implements weighted fusion:

```python
def fuse_contexts(acled_results, cia_results, freedom_results, imf_results, wbi_results):
    """
    Weighted fusion with reliability-based scoring:
    
    weighted_score = similarity_score × source_reliability_weight
    
    Results sorted by weighted_score (descending)
    """
```

**Example fusion output:**
```json
{
  "fusion_ratio": {
    "ACLED": 5,      // 5 ACLED docs retrieved
    "CIA_FACTS": 3,  // 3 CIA docs retrieved
    "IMF": 2,        // 2 IMF docs retrieved
    "FREEDOM_WORLD": 1,
    "WBI": 1
  },
  "top_contexts": [
    {"text": "...", "source_type": "IMF", "weighted_score": 0.675},
    {"text": "...", "source_type": "WBI", "weighted_score": 0.56},
    {"text": "...", "source_type": "ACLED", "weighted_score": 0.4}
  ]
}
```

### Building Vector Indexes

```bash
# Build all sources at once (~10-15 minutes)
make db

# Or build individually:
make db-acled    # ACLED conflict data
make db-cia      # CIA World Factbook
make db-wbi      # World Bank indicators
# IMF and Freedom World indices built with db-acled by default

# Rebuild from scratch
python core/vector_store.py --rebuild

# Ingest specific source
python core/vector_store.py --ingest-acled
python core/vector_store.py --ingest-cia-facts
python core/vector_store.py --ingest-wbi
python core/vector_store.py --ingest-imf
python core/vector_store.py --ingest-freedom-world
```

---

## 🎬 Examples Showcase

HAWK-AI includes a comprehensive showcase demonstrating all capabilities:

```bash
# Run all 7 capability examples
make examples
# or
python examples_showcase.py

# Run specific example (1-7)
python examples_showcase.py --example 3

# List all available examples
make examples-list
# or
python examples_showcase.py --list
```

### The 7 Capability Demonstrations

1. **🎯 Multi-Agent Intelligence Synthesis**
   - Supervisor coordinating GeoAgent + AnalystAgent in parallel
   - Hotspot map generation + multi-source analytical fusion
   - Structured JSON report with confidence scoring

2. **🔍 Real-Time Web Intelligence + Historical Context**
   - SearchAgent web scraping with semantic ranking
   - AnalystAgent fusion of web results + ACLED + CIA data
   - Context enrichment and temporal correlation

3. **🗺️ Geospatial Hotspot Analysis**
   - DBSCAN clustering on 100K+ geographic coordinates
   - Interactive Folium map with color-coded hotspots
   - Cluster statistics and spatial reasoning

4. **📊 Temporal Pattern Analysis**
   - Statistical analysis across 1M+ events
   - Trend identification and escalation detection
   - FAISS semantic search with temporal filtering

5. **💻 Code Execution for Data Analysis**
   - Sandboxed Python execution (pandas, numpy, matplotlib)
   - Data manipulation and visualization
   - Network-isolated secure execution

6. **📝 Executive Brief Generation**
   - Professional report creation with RedactorAgent
   - Key findings extraction and summarization
   - Multi-source synthesis into actionable insights

7. **🧠 Reasoning Chain with Reflection**
   - Structured analytical reasoning (5 steps)
   - Meta-cognitive quality assessment
   - Adaptive re-execution for low-confidence results

**Output Artifacts:**
- Interactive maps: `data/maps/{Country}_hotspot.html`
- Reasoning chains: `data/analysis/last_reasoning.json`
- Session logs: `logs/session_*.jsonl`
- Reports: `data/analysis/report_*.json`

---

## 🧠 Reasoning Viewer

Visualize HAWK-AI's step-by-step reasoning process with the built-in viewer:

```bash
# CLI mode (terminal output)
make reasoning
# or
python tools/reasoning_viewer.py

# Web UI mode (interactive Streamlit dashboard)
make reasoning-ui
# or
python tools/reasoning_viewer.py --mode streamlit

# View specific reasoning file
python tools/reasoning_viewer.py --data-path data/analysis/custom_reasoning.json
```

### The Reasoning Viewer Displays:

- 🔍 **Pattern Recognition**: Identified actors, causes, and relationships
- 💡 **Hypothesis Formation**: Generated explanations (2-3 hypotheses)
- ⚖️ **Evaluation**: Evidence-based hypothesis assessment
- 🔗 **Synthesis**: Integrated analysis with frameworks (PMESII/DIME)
- ✅ **Review**: Critical review identifying gaps and recommendations

**Quick Start:**
```bash
# 1. Run example to generate reasoning data
python examples_showcase.py --example 7

# 2. View reasoning chain
make reasoning

# 3. Or use web interface
make reasoning-ui
```

See `tools/README.md` for detailed reasoning viewer documentation.

---

## 🔧 Configuration

### Available Commands

HAWK-AI includes convenient `make` commands for all operations:

**Setup & Database:**
- `make setup` - Install dependencies in virtual environment
- `make db` - Build all vector indexes (~10-15 min)
- `make db-acled` - Build ACLED index only
- `make db-cia` - Build CIA World Factbook index
- `make db-wbi` - Build World Bank indicators index

**Running Services:**
- `make hawk` - Start all services (API + Open WebUI)
- `make stop` - Stop all services
- `make api` - Start API server with auto-reload (dev)
- `make api-prod` - Start API server in production mode
- `make run` - Start CLI interactive mode
- `make dev` - Start development mode with diagnostics

**Analysis & Tools:**
- `make examples` - Run all capability demonstrations
- `make examples-list` - List available examples
- `make reasoning` - View reasoning chains (CLI)
- `make reasoning-ui` - View reasoning chains (Streamlit web UI)

**Maintenance:**
- `make test` - Run test suite
- `make clean` - Clean virtual environment and cache

### `config/agents.yaml`

Agent model assignments and thinking modes:

```yaml
models:
  supervisor: magistral:latest
  search: qwen2.5:7b
  analyst: gpt-oss:20b
  geo: magistral:latest
  redactor: wizardlm-uncensored:13b
  reflection: nous-hermes2:34b
  code: mixtral:8x7b
  embed_primary: snowflake-arctic-embed2:568m
  embed_secondary: qwen3-embedding:8b

thinking_modes:
  factual: "Summarize verified data only. Avoid speculation."
  analytical: "Identify causes, effects, and underlying motivations."
  strategic: "Predict scenarios and long-term geopolitical implications."
  risk: "Assess threat levels, vulnerabilities, and risk exposure."
```

### `config/settings.yaml`

System configuration:

```yaml
ollama:
  host: "127.0.0.1"
  port: 11434
  model_default: "gpt-oss:20b"
  embed_model: "snowflake-arctic-embed2:568m"
  timeout: 300

vector_store:
  path: "data/vector_index"
  use_gpu: true          # GPU acceleration for FAISS
  dimension: 768
  index_type: "flat"
  top_k: 5

search:
  max_results: 5
  timeout: 10

code_execution:
  timeout: 30
  max_output_length: 10000
  allowed_imports: ["numpy", "pandas", "matplotlib", "seaborn", "sklearn", "scipy"]

tracking:
  langsmith_enabled: true
  project_name: "HAWK-AI-local"
  log_dir: "logs"
```

### `config/sources.yaml`

Data source configuration:

```yaml
acled:
  enabled: true
  path: "historical_context/ACLED"
  file_pattern: "*.csv"

search_sources:
  duckduckgo:
    enabled: true
    region: "wt-wt"
    safesearch: "moderate"
```

---

## 💾 Memory & Collaboration

HAWK-AI implements persistent memory for inter-agent collaboration and historical reasoning.

### Memory Manager

Stores and retrieves:
- Previous queries and results
- Agent invocations and outputs
- Confidence scores and reflections
- Cross-session reasoning history

**Usage:**

```python
from core.memory_manager import append_entry, get_recent_entries, search_memory

# Store memory entry
append_entry({
    "query": "Conflict escalation in Sudan",
    "agents": ["analyst", "geo"],
    "confidence": 0.88,
    "summary": "Analysis completed successfully"
})

# Retrieve recent entries
recent = get_recent_entries(count=5)

# Search memory
results = search_memory(
    query_text="Sudan",
    agent_name="analyst",
    min_confidence=0.7
)
```

**CLI Interface:**

```bash
# View recent memory entries
python core/memory_manager.py --show

# View last 10 entries
python core/memory_manager.py --show --count 10

# Search memory
python core/memory_manager.py --search "Sudan"
python core/memory_manager.py --search-agent analyst
python core/memory_manager.py --min-confidence 0.8

# Memory statistics
python core/memory_manager.py --stats

# Clear memory (caution!)
python core/memory_manager.py --clear
```

### Collaborative Features

1. **Historical Context**: Agents access past analyses for continuity
2. **Pattern Recognition**: Identify recurring themes across sessions
3. **Confidence Tracking**: Learn from low-confidence results
4. **Query Refinement**: Improve future analyses based on history

---

## 📈 Tracking & Logging

Comprehensive logging system for transparency and debugging:

### Log Files

- **`logs/hawk_ai.log`**: Main application logs
- **`logs/supervisor_agent.log`**: Supervisor coordination logs
- **`logs/analyst_agent.log`**: Analyst reasoning traces
- **`logs/geo_agent.log`**: Geospatial analysis logs
- **`logs/websearch.log`**: Web search operations
- **`logs/session_YYYYMMDD_HHMMSS.jsonl`**: Detailed session logs (JSONL format)

### Session Tracking

View session history in interactive mode:

```bash
> history
```

Outputs:
- Session ID
- Total events processed
- Event types distribution
- Agents used
- Performance metrics

### Reasoning Artifacts

- **`data/analysis/last_reasoning.json`**: Latest reasoning chain
- **`data/analysis/report_*.json`**: Generated intelligence reports
- **`data/maps/*.html`**: Interactive geospatial maps

---

## 🔐 Security

HAWK-AI implements multiple security layers:

### Sandboxed Code Execution
- **Isolated Subprocess**: Code runs in separate process
- **Import Whitelisting**: Only approved libraries (pandas, numpy, matplotlib, seaborn, sklearn, scipy)
- **Network Isolation**: No network access from sandbox
- **Timeout Enforcement**: 30-second execution limit
- **Output Validation**: All outputs validated before display

### Privacy-First Design
- **Fully Local**: All processing on your machine
- **No Cloud Dependencies**: Uses local Ollama models
- **No Data Transmission**: Your data never leaves your system
- **Local Caching**: Web search results cached locally

### Input Validation
- Query sanitization
- Code validation before execution
- Path traversal prevention
- SQL injection protection (for data sources)

---

## 🎯 Use Cases

### 🔬 Research & Analysis
- **Conflict Research**: Study patterns in 1M+ conflict events across multiple regions
- **Academic Research**: Analyze sociopolitical trends with multi-source historical context
- **Policy Analysis**: Generate evidence-based intelligence briefs with framework analysis
- **Threat Assessment**: Identify escalation patterns and emerging hotspots with reflection

### 📰 Intelligence Gathering
- **OSINT Analysis**: Combine web intelligence with 5 historical data sources
- **News Monitoring**: Track current events with automated contextual analysis
- **Geopolitical Analysis**: Multi-source intelligence fusion for regional assessments
- **Strategic Forecasting**: PMESII/DIME framework analysis for scenario planning

### 📊 Data Operations
- **Data Exploration**: Semantic search across millions of data points
- **Report Generation**: Automated executive summaries with multi-agent synthesis
- **Visualization**: Interactive maps and statistical analysis
- **Code Execution**: Custom data analysis with sandboxed Python

### 🛡️ Security & Humanitarian
- **Humanitarian Planning**: Identify high-risk areas with geospatial clustering
- **Risk Assessment**: Analyze conflict dynamics with consistency checking
- **Early Warning**: Detect escalation patterns with temporal analysis
- **Stability Assessment**: PMESII framework for comprehensive evaluation

---

## 📋 Requirements

See `requirements.txt` for full dependencies:

**Core Dependencies:**
- `crewai[tools]` - Agent framework
- `langgraph` - Agent orchestration
- `langchain-ollama` - Ollama integration
- `faiss-gpu` - GPU-accelerated vector database
- `sentence-transformers` - Embedding generation
- `duckduckgo-search` - Web search
- `pandas`, `numpy` - Data processing
- `folium` - Interactive map generation
- `scikit-learn` - Clustering algorithms (DBSCAN)
- `rich` - Terminal UI
- `pyyaml` - Configuration management
- `tqdm` - Progress bars

**API & Web Interface:**
- `fastapi` - REST API framework
- `uvicorn[standard]` - ASGI server with auto-reload
- `pydantic` - Data validation and serialization
- `streamlit` - Web UI for reasoning viewer (optional)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Adding New Agents

Create a new agent in `agents/` following the existing pattern:

```python
# agents/your_agent.py
from langchain_ollama import OllamaLLM
from core.config_loader import get_model

class YourAgent:
    def __init__(self, model: str = None):
        self.model = model if model else get_model("your_agent", "default-model:latest")
        self.llm = OllamaLLM(model=self.model, base_url="http://127.0.0.1:11434")
    
    def execute(self, query: str):
        # Agent logic here
        pass
```

Register in `config/agents.yaml`:
```yaml
models:
  your_agent: your-model:latest
```

### Adding Data Sources

1. Place data files in `historical_context/YOUR_SOURCE/`
2. Update `config/sources.yaml`
3. Add ingestion method to `core/vector_store.py`:

```python
def ingest_your_source_data(self, source_path: Optional[str] = None):
    """Ingest YOUR_SOURCE data into vector store."""
    # Implement data loading and embedding
    pass
```

4. Rebuild index: `make db`

### Adding Analytical Frameworks

Add framework to `core/analytical_frameworks.py`:

```python
def apply_your_framework(context: str) -> str:
    """Apply YOUR_FRAMEWORK for analysis."""
    template = f"""
    Framework prompt template here
    Context: {context}
    """
    return template
```

Update `core/context_orchestrator.py` for automatic selection.

### Testing

```bash
# Run existing tests
make test

# Add tests to tests/
python tests/run_all_tests.py
```

**Please ensure:**
- Code follows existing patterns
- Security measures are maintained
- Documentation is updated
- Changes are tested
- Model configurations are in YAML files

---

## 🆘 Troubleshooting

### Ollama Connection Error

```bash
# Ensure Ollama is running
ollama serve

# Check available models
ollama list

# Pull missing models
ollama pull magistral:latest
```

### Vector Store Issues

```bash
# Rebuild vector index
make db

# Check index status
python core/vector_store.py --status
```

### GPU Not Detected

Set `use_gpu: false` in `config/settings.yaml`:

```yaml
vector_store:
  use_gpu: false
```

### Import Errors

```bash
# Reinstall dependencies
make clean
make setup

# Activate virtual environment
source .venv/bin/activate
```

### Memory Issues

If you encounter memory errors with large datasets:

```yaml
# Adjust in config/settings.yaml
vector_store:
  top_k: 3  # Reduce from 5
  
code_execution:
  max_output_length: 5000  # Reduce from 10000
```

### Model Not Found

```bash
# Check configured models
cat config/agents.yaml

# Pull missing models
ollama pull gpt-oss:20b
ollama pull nous-hermes2:34b
```

---

## 📞 Getting Help

### Debugging Steps

1. **Check logs**: `tail -f logs/hawk_ai.log`
2. **Validate setup**: `python validate_setup.py`
3. **Verify Ollama**:
   ```bash
   ollama list  # Check available models
   ollama serve  # Ensure Ollama is running
   curl http://127.0.0.1:11434/api/tags
   ```
4. **Check configuration**: `python main.py --dev`
5. **Verify data sources**: `ls historical_context/*/`
6. **Test vector store**: `python core/vector_store.py --status`

### Performance Tips

- **GPU Acceleration**: Set `use_gpu: true` (requires NVIDIA GPU + CUDA)
- **Model Selection**:
  - Faster: `qwen2.5:7b`, `mistral:7b`, `llama3:8b`
  - Balanced: `gpt-oss:20b`, `magistral:latest`
  - Quality: `nous-hermes2:34b`, `mixtral:8x7b`
- **Parallel Execution**: Already optimized (ThreadPoolExecutor with 3 workers)
- **Caching**: Web search results automatically cached in `data/web_cache/`

### Common Issues

**"No module named 'faiss'"**
```bash
source .venv/bin/activate
pip install faiss-gpu-cu12  # or faiss-cpu if no GPU
```

**"Connection refused" (Ollama)**
```bash
ollama serve
```

**"Vector index not found"**
```bash
make db
```

**"Low confidence results"**
- Check if Reflection Agent is enabled
- Review `logs/reflection_agent.log`
- System automatically re-runs agents if confidence < 0.7

### API & Web Interface Issues

**"API server not starting"**
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill process if needed
kill -9 <PID>
# Restart API
make api
```

**"Open WebUI connection refused"**
```bash
# Verify API server is running
curl http://127.0.0.1:8000/health
# Should return: {"status": "healthy"}

# Check CORS settings in api_server.py
# Ensure Open WebUI port is allowed
```

**"Streaming not working"**
```bash
# Test streaming with curl
curl -N -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Test", "stream": true}'
```

**"Services won't stop"**
```bash
# Force stop all services
make stop
# Or manually:
pkill -f "api_server.py"
pkill -f "main.py"
```

### Need More Help?

- 📖 Check `OPENWEBUI_INTEGRATION.md` for web interface setup
- 📖 Check `QUICK_START_INTEGRATION.md` for quick start guide
- 📖 Check `STREAMING_SETUP.md` for streaming configuration
- 📖 Check `tests/README.md` for testing documentation
- 📖 Check `tools/README.md` for reasoning viewer documentation
- 🐛 Report issues on GitHub with logs from `logs/`
- 💬 Review detailed error messages in log files
- 🌐 API docs available at http://127.0.0.1:8000/docs when running

---

## 📄 License

This project is for research and educational purposes. See [LICENSE](LICENSE) for details.

**Important**: ACLED data is subject to [ACLED Terms of Use](https://acleddata.com/terms-of-use/). If you use HAWK-AI for research, please cite ACLED appropriately.

**Data Source Citations:**
- **ACLED**: Armed Conflict Location & Event Data Project (www.acleddata.com)
- **CIA World Factbook**: Central Intelligence Agency (www.cia.gov/the-world-factbook)
- **Freedom in the World**: Freedom House (freedomhouse.org)
- **IMF World Economic Outlook**: International Monetary Fund (www.imf.org)
- **World Bank Indicators**: World Bank Group (data.worldbank.org)

---

## 🙏 Acknowledgments

- **ACLED** for comprehensive conflict data
- **CIA World Factbook** for country profiles
- **Freedom House** for democracy indices
- **IMF** for economic indicators
- **World Bank** for development data
- **Ollama** for local model serving
- **LangChain** for agent framework
- **FAISS** for vector search
- **scikit-learn** for clustering algorithms

---

## ⭐ Show Your Support

If you find HAWK-AI useful, please give it a star! ⭐

---

**Built with 🦅 for local, private, and powerful OSINT analysis**

*Your intelligence, your data, your machine.*

---

## 🚀 Deployment & Integration

### Deployment Options

**1. Local Development**
```bash
make hawk  # Start all services locally
```

**2. Production Deployment**
```bash
# API only (for backend integration)
make api-prod

# Or with docker-compose (if using Open WebUI's docker setup)
cd open-webui && docker-compose up -d
```

**3. Cloud Deployment**
- Deploy `api_server.py` to any Python-compatible cloud platform
- Ensure Ollama is accessible (local or remote endpoint)
- Configure CORS for your frontend domain
- Set environment variables in production

### Integration Guides

HAWK-AI provides multiple integration points:

- 📖 **[OPENWEBUI_INTEGRATION.md](OPENWEBUI_INTEGRATION.md)** - Complete Open WebUI integration guide
- 📖 **[QUICK_START_INTEGRATION.md](QUICK_START_INTEGRATION.md)** - Quick start for web interface
- 📖 **[STREAMING_SETUP.md](STREAMING_SETUP.md)** - Streaming configuration and testing
- 📖 **[REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)** - Project structure overview

### API Integration

Use HAWK-AI as a drop-in replacement for OpenAI API:

```python
import openai

# Point to HAWK-AI server
openai.api_base = "http://127.0.0.1:8000/v1"
openai.api_key = "not-needed"  # API key not required for local

# Use standard OpenAI client
response = openai.ChatCompletion.create(
    model="hawk-ai-supervisor",
    messages=[
        {"role": "user", "content": "Analyze tensions in Sudan"}
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end="")
```

---

## 📊 System Requirements

### Minimum
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 10GB (with vector indexes)
- **GPU**: Optional (CPU-only mode supported)

### Recommended
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 20GB+ SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for faster inference)

### Performance Tips
- Enable GPU acceleration: `use_gpu: true` in `config/settings.yaml`
- Use SSD for vector indexes
- Run Ollama with GPU support
- Adjust `top_k` and model size based on available resources

---

**Version**: 2.0.0  
**Last Updated**: October 17, 2025

**Major Updates in 2.0:**
- ✨ REST API server with FastAPI
- 💬 Open WebUI integration
- 🔄 Streaming chat support
- 📡 OpenAI-compatible endpoints
- 🎨 Real-time agent transparency
- 🚀 Production-ready deployment options
