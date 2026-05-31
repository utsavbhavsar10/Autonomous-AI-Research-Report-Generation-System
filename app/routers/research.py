import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.schemas.research import ResearchRequest, ResearchResponse
from app.schemas.job import JobStatus
from app.services.job_service import create_job, get_job, get_all_jobs, update_job
from app.services.notification_service import NotificationService
from app.services.research_service import ResearchService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/research", tags=["Research"])

notifier = NotificationService()
research_service = ResearchService()


async def run_pipeline(job_id: str, query: str, depth: str):
    """
    Background pipeline runner.
    Day 1 wires ResearchService.run; Day 3 swaps it for the LangGraph state machine.
    """
    start_time = datetime.now(timezone.utc)
    await notifier.job_started(job_id, query, depth)
    await update_job(job_id, status="processing")

    try:
        result = await research_service.run(job_id, query, depth)

        completed_at = datetime.now(timezone.utc)
        duration = (completed_at - start_time).total_seconds()

        await update_job(
            job_id,
            status="complete",
            report_path=result.get("file_path"),
            sources_count=result.get("sources", 0),
            completed_at=completed_at.isoformat(),
            duration_seconds=duration,
        )

        await notifier.job_complete(
            job_id,
            query,
            result.get("file_path", ""),
            result.get("sources", 0),
            duration,
        )

    except Exception as e:
        logger.exception(f"Pipeline failed for job {job_id}")
        await update_job(job_id, status="failed", error=str(e))
        await notifier.job_failed(job_id, query, str(e))


@router.post("", response_model=ResearchResponse, status_code=202)
async def create_research_job(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
):
    """Start a new autonomous research job."""
    job_id = str(uuid.uuid4())

    await create_job(job_id, request.query, request.depth)
    background_tasks.add_task(run_pipeline, job_id, request.query, request.depth)

    return ResearchResponse(
        job_id=job_id,
        status="queued",
        message="Research pipeline started. Poll /research/{job_id} for status.",
        query=request.query,
        created_at=datetime.now(timezone.utc),
    )


@router.get("/{job_id}", response_model=JobStatus)
async def get_research_status(job_id: str):
    """Get current status and result of a research job."""
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job["created_at"] = datetime.fromisoformat(job["created_at"])
    if job.get("completed_at"):
        job["completed_at"] = datetime.fromisoformat(job["completed_at"])
    return JobStatus(**job)


@router.get("", response_model=list[JobStatus])
async def list_jobs(limit: int = 20):
    """List recent research jobs."""
    jobs = await get_all_jobs(limit)
    out = []
    for j in jobs:
        j["created_at"] = datetime.fromisoformat(j["created_at"])
        if j.get("completed_at"):
            j["completed_at"] = datetime.fromisoformat(j["completed_at"])
        out.append(JobStatus(**j))
    return out


@router.get("/health/check")
async def health_check():
    return {"status": "ok", "service": "research-api"}
