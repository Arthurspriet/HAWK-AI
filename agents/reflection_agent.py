"""
ReflectionAgent: Meta-reasoning agent for evaluating coherence,
completeness, and contradictions between other agents' outputs.
"""

import json
import logging
from datetime import datetime
from langchain_ollama import OllamaLLM
from core.config_loader import get_model


class ReflectionAgent:
    """
    ReflectionAgent evaluates outputs from multiple agents (Analyst, Geo, Search, etc.)
    to identify inconsistencies, assign confidence scores, and recommend reruns.
    """
    
    def __init__(self, model: str = None):
        """
        Initialize the ReflectionAgent with a reasoning-capable model.
        
        Args:
            model: The Ollama model to use for reflection (overrides config)
        """
        # Load model from config or use provided model
        self.model = model if model else get_model("reflection", "nous-hermes2:34b")
        
        self.logger = logging.getLogger("ReflectionAgent")
        logging.basicConfig(
            filename="logs/reflection_agent.log",
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Initialize LLM with error handling
        try:
            self.llm = OllamaLLM(model=self.model, base_url="http://127.0.0.1:11434")
        except Exception as e:
            self.logger.error(f"Model {self.model} not found. Run: ollama pull {self.model}")
            raise
        
        self.logger.info(f"🧩 ReflectionAgent initialized with model: {self.model}")
    
    def evaluate_results(self, results: dict) -> dict:
        """
        Evaluate the coherence and completeness of agent outputs.
        
        Args:
            results: Dictionary containing outputs from various agents
            
        Returns:
            Dictionary with confidence score, contradictions, rerun recommendations, and summary
        """
        import time
        start = time.time()
        self.logger.info("Starting evaluation of agent results")
        
        try:
            # Truncate results to avoid overwhelming the model
            results_str = json.dumps(results, indent=2)[:8000]
            
            prompt = f"""
You are a reflection layer analyzing outputs from multiple agents.
Evaluate factual consistency, completeness, and contradictions.
Suggest which agents (if any) need to re-run, and compute an overall confidence (0-1).
Provide a structured JSON:
{{
  "confidence": <float>,
  "contradictions": ["..."],
  "rerun": ["analyst", "geo"],
  "summary": "..."
}}

Results to analyze:
{results_str}
"""
            
            self.logger.info("Invoking LLM for reflection analysis")
            response = self.llm.invoke(prompt)
            
            # Parse the JSON response
            # Try to extract JSON from the response if it contains additional text
            response_text = response.strip()
            
            # Find JSON block in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                reflection_result = json.loads(json_str)
            else:
                # If no JSON found, create a structured response
                reflection_result = {
                    "confidence": 0.5,
                    "contradictions": ["Unable to parse model response"],
                    "rerun": [],
                    "summary": response_text
                }
            
            # Validate structure
            if "confidence" not in reflection_result:
                reflection_result["confidence"] = 0.5
            if "contradictions" not in reflection_result:
                reflection_result["contradictions"] = []
            if "rerun" not in reflection_result:
                reflection_result["rerun"] = []
            if "summary" not in reflection_result:
                reflection_result["summary"] = "No summary provided"
            
            # Ensure confidence is between 0 and 1
            reflection_result["confidence"] = max(0.0, min(1.0, float(reflection_result["confidence"])))
            
            duration = round(time.time() - start, 2)
            self.logger.info(f"🧩 ReflectionAgent finished in {duration}s using {self.model}")
            self.logger.info(f"Evaluation complete. Confidence: {reflection_result['confidence']}")
            
            # Add consistency check between structural and event data
            consistency = self.evaluate_consistency(results)
            reflection_result["consistency_check"] = consistency
            self.logger.info(f"Added consistency analysis: {consistency.get('overall_stability')}")
            
            return reflection_result
            
        except json.JSONDecodeError as e:
            duration = round(time.time() - start, 2)
            self.logger.error(f"JSON parsing error after {duration}s: {e}")
            return {
                "confidence": 0.0,
                "contradictions": [f"Failed to parse LLM response: {str(e)}"],
                "rerun": [],
                "summary": "Error occurred during reflection analysis"
            }
        
        except Exception as e:
            duration = round(time.time() - start, 2)
            self.logger.error(f"Error during evaluation after {duration}s: {e}")
            return {
                "confidence": 0.0,
                "contradictions": [f"Evaluation error: {str(e)}"],
                "rerun": [],
                "summary": "Critical error occurred during reflection analysis"
            }
    
    def evaluate_consistency(self, results: dict) -> dict:
        """
        Evaluate alignment between CIA Factbook (structural data) and ACLED (event data).
        Identifies contradictions and assesses stability coherence.
        
        Args:
            results: Dictionary containing agent outputs with both structural and event data
            
        Returns:
            Dictionary with contradictions, alignment summary, and overall stability assessment
        """
        self.logger.info("Starting consistency evaluation between structural and event data")
        
        prompt = f"""
Evaluate the following combined analytical results for consistency between structural and event data.
Focus on contradictions (e.g., stable governance but increasing unrest).
Provide structured JSON output:
{{
  "contradictions": ["..."],
  "alignment_summary": "...",
  "overall_stability": "Stable / Fragile / Deteriorating"
}}
Data:
{json.dumps(results)[:8000]}
"""
        
        try:
            response = self.llm.invoke(prompt)
            
            # Parse the JSON response
            response_text = response.strip() if isinstance(response, str) else str(response)
            
            # Find JSON block in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                consistency_result = json.loads(json_str)
            else:
                # If no JSON found, create a structured response
                consistency_result = {
                    "contradictions": [],
                    "alignment_summary": "Unable to parse consistency evaluation",
                    "overall_stability": "Unknown"
                }
            
            # Validate structure
            if "contradictions" not in consistency_result:
                consistency_result["contradictions"] = []
            if "alignment_summary" not in consistency_result:
                consistency_result["alignment_summary"] = "No alignment summary provided"
            if "overall_stability" not in consistency_result:
                consistency_result["overall_stability"] = "Unknown"
            
            self.logger.info(f"Consistency evaluation complete: {consistency_result.get('overall_stability')}")
            return consistency_result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error in consistency evaluation: {e}")
            return {
                "contradictions": [],
                "alignment_summary": f"Error parsing response: {str(e)}",
                "overall_stability": "Unknown"
            }
        
        except Exception as e:
            self.logger.error(f"Consistency evaluation failed: {e}")
            return {
                "contradictions": [],
                "alignment_summary": "Error in evaluation",
                "overall_stability": "Unknown"
            }


def main():
    """
    CLI interface for ReflectionAgent.
    Usage: python agents/reflection_agent.py --input data/analysis/report_latest.json
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="ReflectionAgent: Meta-reasoning evaluation")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the analysis report JSON file to evaluate"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-oss:20b",
        help="Ollama model to use for reflection (default: gpt-oss:20b)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for reflection results (default: data/analysis/reflection_<timestamp>.json)"
    )
    
    args = parser.parse_args()
    
    # Load input report
    print(f"Loading report from: {args.input}")
    try:
        with open(args.input, 'r') as f:
            report = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}")
        return
    
    # Initialize ReflectionAgent
    print(f"Initializing ReflectionAgent with model: {args.model}")
    agent = ReflectionAgent(model=args.model)
    
    # Evaluate results
    print("Evaluating agent outputs...")
    reflection = agent.evaluate_results(report)
    
    # Print summary
    print("\n" + "="*60)
    print("REFLECTION ANALYSIS")
    print("="*60)
    print(f"Confidence: {reflection['confidence']:.2f}")
    print(f"\nContradictions Found: {len(reflection['contradictions'])}")
    for contradiction in reflection['contradictions']:
        print(f"  - {contradiction}")
    
    if reflection['rerun']:
        print(f"\nRecommended Reruns: {', '.join(reflection['rerun'])}")
    else:
        print("\nNo reruns recommended")
    
    print(f"\nSummary:\n{reflection['summary']}")
    print("="*60)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/analysis/reflection_{timestamp}.json"
    
    # Save results
    print(f"\nSaving reflection results to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(reflection, f, indent=2)
    
    print("Reflection analysis complete!")


if __name__ == "__main__":
    main()

