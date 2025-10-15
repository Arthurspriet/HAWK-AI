"""
Context Fusion Module

This module handles weighted fusion of context retrieved from multiple sources 
(ACLED, CIA_FACTS, and others).
"""

import json
import logging


def fuse_contexts(acled_results: list, cia_results: list, weight_acled: float = 0.6, weight_cia: float = 0.4) -> list:
    """
    Fuse contextual data from ACLED and CIA Factbook sources with adjustable weights.
    
    Args:
        acled_results: List of ACLED context results with optional 'score' field
        cia_results: List of CIA Factbook context results with optional 'score' field
        weight_acled: Weight multiplier for ACLED results (default: 0.6)
        weight_cia: Weight multiplier for CIA results (default: 0.4)
    
    Returns:
        List of fused context documents sorted by weighted_score in descending order
    """
    if not acled_results and not cia_results:
        logging.warning("No context data to fuse.")
        return []
    
    fused = []
    
    for r in acled_results:
        r["weighted_score"] = r.get("score", 0.5) * weight_acled
        r["source_type"] = "ACLED"
        fused.append(r)
    
    for r in cia_results:
        r["weighted_score"] = r.get("score", 0.5) * weight_cia
        r["source_type"] = "CIA_FACT"
        fused.append(r)
    
    fused_sorted = sorted(fused, key=lambda x: x["weighted_score"], reverse=True)
    logging.info(f"Fused {len(fused_sorted)} context documents (ACLED={len(acled_results)}, CIA={len(cia_results)})")
    
    return fused_sorted

