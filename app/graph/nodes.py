from app.graph.state import ResearchState
from app.services.search_service import SearchService
from app.services.report_service import ReportService
from app.services.job_service import update_job
from app.utils.content_processor import ContentProcessor
from app.utils.logger import get_logger

logger = get_logger(__name__)
search = SearchService()
report = ReportService()
processor = ContentProcessor()

async def plan_nodes(state: ResearchState) -> dict:
    """Plan queries based on depth.

    First pass uses the canonical "latest / recent / key insights" angles.
    Re-plan (triggered by weak quality) swaps in different angles so the
    next search round actually hits new sources instead of repeating itself.
    """
    try:
        attempts = state.get("plan_attempts", 0) + 1
        is_replan = attempts > 1
        q = state["query"]

        if is_replan:
            queries = [
                f"{q} alternative perspective",
                f"{q} case studies",
                f"{q} 2026 update",
                f"{q} criticism and limitations",
            ]
            if state["depth"] == "deep":
                queries += [
                    f"{q} academic research",
                    f"{q} industry report",
                    f"{q} real world examples",
                ]
        else:
            queries = [q]
            if state["depth"] in ("standard", "deep"):
                queries += [
                    f"{q} - latest research findings",
                    f"{q} - recent analysis",
                    f"{q} - key insights",
                ]
            if state["depth"] == "deep":
                queries += [
                    f"{q} - comprehensive review",
                    f"{q} - detailed comparison",
                    f"{q} - expert opinions",
                ]

        action = "Re-planning" if is_replan else "Planning"
        await update_job(
            state["job_id"],
            status="searching",
            progress=f"{action} {len(queries)} search queries",
        )
        return {"planned_queries": queries, "current_step": "planned", "plan_attempts": attempts, "error": None}
    except Exception as e:
        logger.error(f"Planning failed: {str(e)}")
        return {"error": f"Planning failed: {str(e)}", "current_step": "planned"}


async def search_nodes(state: ResearchState) -> dict:
    """Execute searches and merges all queries' results together."""
    attempts = state.get("search_attempts", 0) + 1
    logger.info(f"Executing search attempt {attempts} with {len(state['planned_queries'])} queries")
    try:
        raw_results = await search.search_multiple(state["planned_queries"])
        # Flatten results (convert into common format)
        flat_results = [item for group in raw_results for item in group["results"]]
        flat_results = processor.filter_valid_results(flat_results)
        flat_results = processor.deduplicate_results(flat_results)
        return {
            "raw_results": raw_results,
            "sources": flat_results,
            "search_attempts": attempts,
            "current_step": "searched",
            "error": None
        }
    except Exception as e:
        logger.error(f"Search failed on attempt {attempts}: {str(e)}")
        return {
            "error": f"Search failed: {str(e)}",
            "search_attempts": attempts,
            "current_step": "searched"
        }
    
async def analysis_nodes(state: ResearchState) -> dict:
    """Assess the quality of sources and determine if we need to re-search."""
    try:
        n = len(state.get("sources", []))
        quality = "good" if n >= 5 else "weak"
        await update_job(state["job_id"], 
                         status="analyzing", 
                         progress=f"Analyzing {n} sources (quality: {quality})")
        return {"sources_quality": quality, "current_step": "analyzed", "error": None}
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}", "current_step": "analyzed"}

async def report_nodes(state: ResearchState) -> dict:
    try:
        await update_job(state["job_id"],
                         status="generating", 
                         progress=f"Generating report from {len(state.get('sources', []))} sources")
        
        md = await report.generate_report(state["query"], state.get("sources", []))
        return {"report_markdown": md, "current_step": "report_generated", "error": None}
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return {"error": f"Report generation failed: {str(e)}", "current_step": "report_generated"}

async def save_nodes(state: ResearchState) -> dict:
    try:
        path = await report.save_report(state["job_id"], state.get("report_markdown", ""))
        await update_job(state["job_id"], 
                         status="complete", 
                         report_path=path, 
                         sources_count=len(state.get("sources", [])))
        return {"report_path": path, "current_step": "saved", "error": None}
    except Exception as e:
        logger.error(f"Save failed: {str(e)}")
        return {"error": f"Save failed: {str(e)}", "current_step": "saved"}
