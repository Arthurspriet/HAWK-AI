"""
Analytical reasoning frameworks used by AnalystAgent and ReflectionAgent.

This module provides structured prompts for intelligence analysis using 
established frameworks like DIME and PMESII.
"""

import json


def apply_dime(context: str) -> str:
    """
    Apply the DIME (Diplomatic, Information, Military, Economic) framework.
    Produces a structured JSON analysis of each vector based on provided context text.
    
    Args:
        context: The text to analyze using the DIME framework.
        
    Returns:
        A formatted prompt template string for DIME analysis.
    """
    template = f"""
    You are an intelligence analyst applying the DIME framework.
    Analyze the following context by categorizing information into:
    Diplomatic, Information, Military, and Economic components.
    Provide JSON output:
    {{
      "Diplomatic": "...",
      "Information": "...",
      "Military": "...",
      "Economic": "...",
      "Summary": "..."
    }}
    Context:
    {context}
    """
    return template


def apply_pmesii(context: str) -> str:
    """
    Apply the PMESII (Political, Military, Economic, Social, Information, Infrastructure) framework.
    Produces structured JSON output.
    
    Args:
        context: The text to analyze using the PMESII framework.
        
    Returns:
        A formatted prompt template string for PMESII analysis.
    """
    template = f"""
    Use the PMESII framework to assess the situation described below.
    Classify findings under each domain and summarize overall stability.
    JSON output example:
    {{
      "Political": "...",
      "Military": "...",
      "Economic": "...",
      "Social": "...",
      "Information": "...",
      "Infrastructure": "...",
      "Stability_Assessment": "...",
      "Summary": "..."
    }}
    Context:
    {context}
    """
    return template


def get_framework_prompt(framework: str, context: str) -> str:
    """
    Helper function to get the appropriate framework prompt based on the framework name.
    
    Args:
        framework: The name of the framework to apply ("dime" or "pmesii").
        context: The text to analyze.
        
    Returns:
        A formatted prompt template string for the specified framework,
        or the original context if framework is not recognized.
    """
    if framework.lower() == "dime":
        return apply_dime(context)
    elif framework.lower() == "pmesii":
        return apply_pmesii(context)
    else:
        return context

