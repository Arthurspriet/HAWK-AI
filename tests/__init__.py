"""
HAWK-AI Test Suite Package

Comprehensive test and debug suite for validating the functional chain:
tools → agents → combined reasoning

Usage:
    python3 tests/run_all_tests.py

Individual tests can also be imported:
    from tests.run_all_tests import test_geospatial_tools, test_geo_agent
"""

__version__ = "1.0.0"
__author__ = "HAWK-AI Team"

__all__ = [
    "test_geospatial_tools",
    "test_context_enricher_tools",
    "test_geo_agent",
    "test_analyst_agent",
    "test_agent_chain",
]

