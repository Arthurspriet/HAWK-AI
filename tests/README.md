# HAWK-AI Test Suite

This directory contains test scripts to verify the functionality of HAWK-AI's analytical agents and reasoning chains.

## Test Files

### `test_reasoning_chain.py`
Tests the full multi-step reasoning process of the AnalystAgent.

**Purpose:**
- Verifies that the AnalystAgent can execute a complete reasoning chain
- Validates that all reasoning steps are captured and saved
- Displays thinking steps in a formatted, readable way

**Usage:**
```bash
python3 tests/test_reasoning_chain.py
```

**Expected Output:**
- Pattern recognition step
- Hypothesis generation
- Hypothesis evaluation
- Framework-based synthesis (PMESII)
- Critical review
- Total reasoning time and model information

### `test_reflection_chain.py`
Tests the reflection workflow and memory persistence.

**Purpose:**
- Verifies reflection capabilities
- Tests memory storage and retrieval
- Validates confidence scoring

**Usage:**
```bash
python3 tests/test_reflection_chain.py
```

### `test_context_fusion.py`
Tests context fusion across multiple data sources.

### `test_models_config.py`
Tests model configuration loading and validation.

## Test Data

All test results are saved to `data/analysis/` for inspection:
- `last_reasoning.json` - Latest reasoning chain output
- `report_*.json` - Historical analysis reports

## Viewing Results

Use the reasoning viewer tool to display saved reasoning chains:

```bash
# CLI mode
python3 tools/reasoning_viewer.py

# Streamlit web UI
python3 tools/reasoning_viewer.py --mode streamlit
```

## Running All Tests

```bash
python3 tests/run_all_tests.py
```
