from app.services.report_service import ReportService
from app.services.search_service import SearchService

# ResearchService orchestrates the research workflow:
# planning queries, running web search, generating and saving the report.


class ResearchService:
    def __init__(self):
        self.search = SearchService()
        self.report = ReportService()

    async def run(self, job_id: str, query: str, depth: str = "standard") -> dict:
        """Run the full research pipeline: search, generate report, save to disk."""

        # 1. Determine search queries based on depth
        queries = self._plan_queries(query, depth)

        # 2. Execute searches
        raw_results = await self.search.search_multiple(queries)

        # Flatten [{"query": q, "results": [...]}] into a flat list of source dicts
        flat_results = [item for group in raw_results for item in group["results"]]

        # 3. Generate report
        report_content = await self.report.generate_report(query, flat_results)

        # 4. Save to disk
        file_path = await self.report.save_report(job_id, report_content)

        print(f"[research_service] Job {job_id} complete -> {file_path} ({len(flat_results)} sources)")

        return {
            "job_id": job_id,
            "status": "complete",
            "file_path": file_path,
            "sources": len(flat_results),
        }

    def _plan_queries(self, query: str, depth: str) -> list[str]:
        """Generate multiple search queries from the main query."""

        base_queries = [query]

        if depth in ["standard", "deep"]:
            base_queries.append(f"{query} market trends")
            base_queries.append(f"{query} recent news analysis")
            base_queries.append(f"{query} recent developments")

        if depth == "deep":
            base_queries.append(f"{query} competitive comparison")
            base_queries.append(f"{query} future trends forecast")

        return base_queries
