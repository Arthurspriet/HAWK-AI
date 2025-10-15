"""
Analyst Agent for HAWK-AI.
Implements transparent multi-step reasoning with timing and token logging.
"""
import time
import logging
import json
from datetime import datetime
from pathlib import Path

from langchain_ollama import OllamaLLM
from core.vector_store import query_faiss
from core.config_loader import get_model
from core.analytical_frameworks import get_framework_prompt

# Configure logging
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "analyst_agent.log",
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class AnalystAgent:
    """Agent that performs transparent multi-step analytical reasoning."""
    
    def __init__(self):
        """Initialize AnalystAgent with model and logging."""
        self.model = get_model("analyst")
        self.llm = OllamaLLM(model=self.model, base_url="http://127.0.0.1:11434")
        self.logger = logging.getLogger("AnalystAgent")
        self.logger.info(f"AnalystAgent initialized with model: {self.model}")

    def extract_patterns(self, context: str) -> str:
        """
        Identify main actors, causes, and causal relationships in the context.
        
        Args:
            context: The context to analyze
            
        Returns:
            Identified patterns as a string
        """
        prompt = f"Identify main actors, causes, and causal relationships in:\n{context}"
        return self.llm.invoke(prompt)

    def generate_hypotheses(self, patterns: str) -> str:
        """
        Formulate 2–3 possible explanations for the patterns.
        
        Args:
            patterns: The identified patterns
            
        Returns:
            Generated hypotheses as a string
        """
        prompt = f"Formulate 2–3 possible explanations for these patterns:\n{patterns}"
        return self.llm.invoke(prompt)

    def evaluate_hypotheses(self, hypotheses: str) -> str:
        """
        Evaluate hypotheses for plausibility, evidence, and contradictions.
        
        Args:
            hypotheses: The generated hypotheses
            
        Returns:
            Evaluation results as a string
        """
        prompt = f"Evaluate these hypotheses for plausibility, evidence, and contradictions:\n{hypotheses}"
        return self.llm.invoke(prompt)

    def critical_review(self, draft: str) -> str:
        """
        Review the draft analysis for missing variables or logical gaps.
        
        Args:
            draft: The draft analysis to review
            
        Returns:
            Critical review as a string
        """
        prompt = f"Review this draft analysis for missing variables or logical gaps:\n{draft}"
        return self.llm.invoke(prompt)

    def analyze_query(self, query: str, framework: str = None):
        """
        Analyze a query using transparent multi-step reasoning.
        
        Args:
            query: The analytical query
            framework: Optional analytical framework to apply
            
        Returns:
            Dictionary containing reasoning steps, timing, and results
        """
        start = time.time()
        
        # Retrieve context from FAISS
        acled_context = query_faiss(query, source="ACLED", top_k=5)
        cia_context = query_faiss(query, source="CIA_FACTS", top_k=3)
        full_context = acled_context + cia_context
        context_text = json.dumps(full_context)[:8000]

        # Step 1: Pattern extraction
        t1 = time.time()
        patterns = self.extract_patterns(context_text)
        self.logger.info(f"Patterns extracted in {round(time.time()-t1,2)}s")

        # Step 2: Hypothesis generation
        t2 = time.time()
        hypos = self.generate_hypotheses(patterns)
        self.logger.info(f"Hypotheses generated in {round(time.time()-t2,2)}s")

        # Step 3: Hypothesis evaluation
        t3 = time.time()
        evaluation = self.evaluate_hypotheses(hypos)
        self.logger.info(f"Hypotheses evaluated in {round(time.time()-t3,2)}s")

        # Step 4: Framework synthesis (optional)
        if framework:
            framework_prompt = get_framework_prompt(framework, evaluation)
            synthesis = self.llm.invoke(framework_prompt)
        else:
            synth_prompt = f"Combine evaluated hypotheses into a concise analytical synthesis.\n{evaluation}"
            synthesis = self.llm.invoke(synth_prompt)

        # Step 5: Critical review
        review = self.critical_review(synthesis)

        end = time.time()
        total = round(end - start, 2)
        self.logger.info(f"AnalystAgent completed reasoning in {total}s using {self.model}")

        result = {
            "query": query,
            "patterns": patterns,
            "hypotheses": hypos,
            "evaluation": evaluation,
            "synthesis": synthesis,
            "review": review,
            "runtime_s": total,
            "model": self.model,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save reasoning trace
        output_dir = Path(__file__).parent.parent / "data" / "analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "last_reasoning.json", "w") as f:
            json.dump(result, f, indent=2)
        
        return result
