import os
from tavily import TavilyClient

class SearchService:
    def __init__(self):
        self.client = TavilyClient(api_key = os.getenv("TAVILY_SEARCH_API_KEY"))

    
    async def perform_search(self , query: str , max_results: int = 5) -> list[dict]:
        """Search a web and return structured results"""

        response = self.client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_answer=True

        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content"),
                "answer": response.get("answer")
            })
        return results
    
    async def search_multiple(self , queries: list[str] ) -> list[dict]:
        """Run multiple searches and aggregate results"""

        all_results = []
        for q in queries:
            results = await self.perform_search(q)
            all_results.append({
                "query": q,
                "results": results
            })
        return all_results