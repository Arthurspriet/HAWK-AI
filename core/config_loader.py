"""
Configuration loader utility for HAWK-AI.
Loads agent model assignments from YAML config file.
"""
import yaml
import os
import logging

CONFIG_PATH = "config/agents.yaml"


def get_model(agent_name: str, default: str = "magistral:latest") -> str:
    """
    Load agent model from YAML config or return default.
    
    Args:
        agent_name: Name of the agent (e.g., 'analyst', 'geo', 'supervisor')
        default: Default model to use if config is not found
        
    Returns:
        Model name string
    """
    if not os.path.exists(CONFIG_PATH):
        logging.warning(f"Config file {CONFIG_PATH} not found, using default model: {default}")
        return default
    
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = yaml.safe_load(f)
        
        model = cfg.get("models", {}).get(agent_name, default)
        return model
        
    except Exception as e:
        logging.error(f"Error loading config: {e}, using default model: {default}")
        return default


def get_thinking_mode(query: str) -> str:
    """
    Determine the thinking mode based on query keywords.
    
    Args:
        query: The user query string
        
    Returns:
        Thinking mode: 'strategic', 'risk', 'analytical', or 'factual'
    """
    q = query.lower()
    if any(k in q for k in ["predict", "future", "scenario"]): return "strategic"
    if any(k in q for k in ["risk", "threat"]): return "risk"
    if any(k in q for k in ["why", "cause", "impact"]): return "analytical"
    return "factual"


def load_thinking_modes() -> dict:
    """
    Load thinking modes configuration from YAML config file.
    
    Returns:
        Dictionary of thinking modes configuration
    """
    if not os.path.exists(CONFIG_PATH): return {}
    cfg = yaml.safe_load(open(CONFIG_PATH))
    return cfg.get("thinking_modes", {})

