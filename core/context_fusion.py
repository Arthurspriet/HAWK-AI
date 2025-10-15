"""
Context Fusion Module

This module handles weighted fusion of context retrieved from multiple sources 
(ACLED, CIA_FACTS, FREEDOM_WORLD, IMF, WBI).
"""

import logging
import json


def fuse_contexts(acled_results: list = None,
                  cia_results: list = None,
                  freedom_results: list = None,
                  imf_results: list = None,
                  wbi_results: list = None) -> list:
    """
    Fuses contextual data from multiple sources with reliability-based weighting.
    
    Args:
        acled_results: List of ACLED context results with optional 'score' field
        cia_results: List of CIA Factbook context results with optional 'score' field
        freedom_results: List of Freedom World context results with optional 'score' field
        imf_results: List of IMF context results with optional 'score' field
        wbi_results: List of World Bank context results with optional 'score' field
    
    Returns:
        List of fused context documents sorted by weighted_score in descending order
    """
    all_sources = {
        "ACLED": acled_results or [],
        "CIA_FACTS": cia_results or [],
        "FREEDOM_WORLD": freedom_results or [],
        "IMF": imf_results or [],
        "WBI": wbi_results or []
    }

    # Source reliability weights
    weights = {
        "ACLED": 0.5,           # event-based, volatile
        "CIA_FACTS": 0.6,       # structural, long-term
        "FREEDOM_WORLD": 0.6,   # institutional, moderate confidence
        "IMF": 0.75,            # high reliability, quantitative
        "WBI": 0.7              # robust, socio-economic fundamentals
    }

    fused = []
    for source, docs in all_sources.items():
        for r in docs:
            w = weights.get(source, 0.5)
            r["source_type"] = source
            r["weighted_score"] = r.get("score", 0.5) * w
            fused.append(r)

    fused_sorted = sorted(fused, key=lambda x: x["weighted_score"], reverse=True)
    logging.info(f"Fused {len(fused_sorted)} context docs from sources: {list(all_sources.keys())}")
    return fused_sorted


if __name__ == "__main__":
    dummy_acled = [{"text": "Protests in Khartoum", "score": 0.8}]
    dummy_imf = [{"text": "Sudan GDP contracted 12% in 2023", "score": 0.9}]
    dummy_fw = [{"text": "Freedom score dropped to 25/100", "score": 0.6}]
    fused = fuse_contexts(dummy_acled, None, dummy_fw, dummy_imf)
    print(json.dumps(fused, indent=2))
