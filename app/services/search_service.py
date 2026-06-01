import os
from tavily import TavilyClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SearchService:
    def __init__(self):
        api_key = os.getenv("TAVILY_SEARCH_API_KEY")
        if not api_key:
            logger.error("TAVILY_SEARCH_API_KEY not found in environment")
            raise ValueError("TAVILY_SEARCH_API_KEY is required")

        self.client = TavilyClient(api_key=api_key)
        logger.info("SearchService initialized with Tavily API")

    async def perform_search(self, query: str, max_results: int = 5) -> list[dict]:
        """Search the web and return structured results with error handling"""

        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return []

        try:
            logger.info(f"Searching: '{query}' (max_results={max_results})")

            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True
            )

            results = []
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", "Untitled"),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "answer": response.get("answer", "")
                })

            logger.info(f"Search completed: {len(results)} results for '{query}'")
            return results

        except Exception as e:
            logger.error(f"Search failed for query '{query}': {str(e)}")
            return []

    async def search_multiple(self, queries: list[str]) -> list[dict]:
        """Run multiple searches and aggregate results with error handling"""

        if not queries:
            logger.warning("No queries provided to search_multiple")
            return []

        logger.info(f"Running {len(queries)} searches")
        all_results = []
        successful_searches = 0

        for q in queries:
            results = await self.perform_search(q)
            if results:
                successful_searches += 1
            all_results.append({
                "query": q,
                "results": results
            })

        logger.info(f"Completed {successful_searches}/{len(queries)} successful searches")
        return all_results