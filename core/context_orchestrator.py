import logging


class ContextOrchestrator:
    """
    Automatically detects which data sources (ACLED, CIA_FACTS, FREEDOM_WORLD, IMF, WBI)
    and analytical framework (PMESII, DIME, SWOT) to use based on the user query.
    Called by SupervisorAgent before launching AnalystAgent.
    """

    def __init__(self):
        self.logger = logging.getLogger("ContextOrchestrator")
        logging.basicConfig(filename="logs/context_orchestrator.log", level=logging.INFO)

    def plan_sources(self, query: str) -> list:
        """
        Detects query theme and returns the relevant data sources.

        Args:
            query: The user query string to analyze

        Returns:
            List of relevant data source names
        """
        q = query.lower()

        if any(k in q for k in ["economy", "growth", "gdp", "inflation", "finance", "debt", "trade"]):
            sources = ["IMF", "WBI", "CIA_FACTS"]
        elif any(k in q for k in ["conflict", "violence", "war", "security", "protest", "instability"]):
            sources = ["ACLED", "CIA_FACTS", "FREEDOM_WORLD"]
        elif any(k in q for k in ["governance", "democracy", "liberty", "rights", "regime", "institution"]):
            sources = ["FREEDOM_WORLD", "CIA_FACTS", "IMF"]
        elif any(k in q for k in ["development", "education", "poverty", "social"]):
            sources = ["WBI", "CIA_FACTS", "FREEDOM_WORLD"]
        else:
            sources = ["CIA_FACTS"]

        self.logger.info(f"Planned sources for query '{query}': {sources}")
        return sources

    def select_framework(self, query: str) -> str:
        """
        Chooses the analytical framework dynamically.

        Args:
            query: The user query string to analyze

        Returns:
            The selected framework name (PMESII, DIME, or SWOT)
        """
        q = query.lower()

        if any(k in q for k in ["conflict", "war", "security", "instability"]):
            framework = "PMESII"
        elif any(k in q for k in ["economy", "finance", "trade", "diplomacy"]):
            framework = "DIME"
        elif any(k in q for k in ["risk", "forecast", "stability", "scenario"]):
            framework = "SWOT"
        else:
            framework = "PMESII"

        self.logger.info(f"Selected framework for '{query}': {framework}")
        return framework


# Example usage in SupervisorAgent:
# from core.context_orchestrator import ContextOrchestrator
# self.orchestrator = ContextOrchestrator()
# sources = self.orchestrator.plan_sources(query)
# framework = self.orchestrator.select_framework(query)
# contexts = [query_faiss(query, source=s) for s in sources]

