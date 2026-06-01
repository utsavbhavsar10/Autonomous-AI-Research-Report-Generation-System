from app.graph import workflow
from app.services.report_service import ReportService
from app.services.search_service import SearchService
from app.services.job_service import update_job
from app.utils.content_processor import ContentProcessor
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResearchService:
    def __init__(self):
        self.search = SearchService()
        self.report = ReportService()
        self.processor = ContentProcessor()

    async def run(self, job_id: str, query: str, depth: str = "standard") -> dict:
        initial_state = {
            "job_id": job_id,
            "query": query,
            "depth": depth, 
            "search_attempts": 0,
            "current_step": "initialized"
        }
        final_state = await workflow.ainvoke(initial_state)
        return{
            "job_id": job_id,
            "status": "failed" if final_state.get("error") else "complete",
            "file_path": final_state.get("report_path", ""),
            "sources": len(final_state.get("sources", [])),
        }