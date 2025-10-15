"""
Ollama client wrapper for HAWK-AI.
Provides unified interface for language model and embedding operations.
"""
import os
from typing import List, Dict, Any, Optional
import yaml
from ollama import Client
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from rich.console import Console

console = Console()


class OllamaClientWrapper:
    """Wrapper for Ollama client with LangChain integration."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize Ollama client with configuration."""
        self.config = self._load_config(config_path)
        self.host = f"http://{self.config['ollama']['host']}:{self.config['ollama']['port']}"
        
        # Initialize native Ollama client
        self.client = Client(host=self.host)
        
        # Initialize LangChain components
        self.llm = OllamaLLM(
            base_url=self.host,
            model=self.config['ollama']['model_default'],
            timeout=self.config['ollama'].get('timeout', 300)
        )
        
        self.embeddings = OllamaEmbeddings(
            base_url=self.host,
            model=self.config['ollama']['embed_model']
        )
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate text completion using Ollama."""
        model_name = model or self.config['ollama']['model_default']
        
        try:
            response = self.client.generate(
                model=model_name,
                prompt=prompt,
                **kwargs
            )
            return response['response']
        except Exception as e:
            console.print(f"[red]Error generating response: {e}[/red]")
            raise
    
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        """Chat completion using Ollama."""
        model_name = model or self.config['ollama']['model_default']
        
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                **kwargs
            )
            return response['message']['content']
        except Exception as e:
            console.print(f"[red]Error in chat: {e}[/red]")
            raise
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            console.print(f"[red]Error generating embeddings: {e}[/red]")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            console.print(f"[red]Error generating query embedding: {e}[/red]")
            raise
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            models = self.client.list()
            return [m['name'] for m in models['models']]
        except Exception as e:
            console.print(f"[red]Error listing models: {e}[/red]")
            return []
    
    def check_model_availability(self, model: str) -> bool:
        """Check if a model is available."""
        available_models = self.list_models()
        return model in available_models


# Global instance
_ollama_client = None


def get_ollama_client(config_path: str = "config/settings.yaml") -> OllamaClientWrapper:
    """Get or create global Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClientWrapper(config_path)
    return _ollama_client
