# 🦅 HAWK-AI

**H**ighly **A**daptive **W**eb **K**nowledge **A**nalysis & **I**ntelligence Agent

A fully local, offline-capable OSINT reasoning agent powered by Ollama models with vectorized historical knowledge (ACLED), web search, code execution, and multi-agent orchestration.

## 🌟 Features

- **🔍 Web Search**: DuckDuckGo integration for real-time information retrieval
- **📊 Data Analysis**: Advanced ACLED conflict data analysis with FAISS vector search
- **💻 Code Execution**: Sandboxed Python code execution
- **📝 Text Processing**: Intelligent summarization and redaction
- **🤖 Multi-Agent System**: Specialized agents coordinated by a supervisor
- **📈 Local Tracking**: LangSmith integration for complete observability
- **🔒 Fully Local**: Runs entirely offline with local Ollama models

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

## 📦 Installation

### Prerequisites

- Python 3.8+
- Ollama installed and running at `127.0.0.1:11434`
- (Optional) NVIDIA GPU for faster vector operations

### Setup

```bash
# Clone the repository
cd HAWK-AI

# Create virtual environment and install dependencies
make setup

# Build vector database from ACLED data
make db

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

## 💡 Examples

### Web Search
```
> Search for recent developments in Niger
```

### Historical Analysis
```
> Analyze conflict escalation patterns in the Sahel region
```

### Data Analysis with Context
```
> What are the trends in civilian-targeting events in Sudan?
```

### Code Execution
```
> Execute this code:
```python
import pandas as pd
data = pd.DataFrame({'country': ['Sudan', 'Niger'], 'events': [150, 89]})
print(data.describe())
```
```

### Summarization
```
> Create an executive brief on Middle East tensions based on recent data
```

## 🧩 Agent System

### Supervisor Agent
Orchestrates task execution and coordinates specialized agents based on query requirements.

### Search Agent
- Performs web searches via DuckDuckGo
- Retrieves news articles
- Scrapes and analyzes web content

### Analyst Agent
- Analyzes ACLED conflict data
- Detects temporal and geographic patterns
- Identifies escalation trends
- Generates statistical reports

### Redactor Agent
- Creates summaries and executive briefs
- Extracts key points
- Formats professional reports
- Redacts sensitive information

### Code Execution Agent
- Safely executes Python code in sandbox
- Validates code before execution
- Returns formatted results

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

- **OSINT Analysis**: Analyze open-source intelligence data
- **Conflict Research**: Study patterns in conflict data
- **News Monitoring**: Track and analyze current events
- **Report Generation**: Create professional analytical reports
- **Data Exploration**: Query and visualize historical datasets
- **Academic Research**: Analyze sociopolitical patterns

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

This is a local research tool. Feel free to:
- Add new agent types
- Integrate additional data sources
- Enhance analysis capabilities
- Improve security features

## 📄 License

This project is for research and educational purposes.

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

## 📞 Support

For issues and questions:
1. Check logs in `logs/`
2. Use `--dev` mode to debug
3. Verify Ollama model availability
4. Check configuration in `config/settings.yaml`

---

**Built with 🦅 for local, private, and powerful OSINT analysis**

