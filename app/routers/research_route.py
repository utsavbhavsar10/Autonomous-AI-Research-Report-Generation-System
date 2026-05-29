import uuid 
from fastapi import APIRouter
from datetime import datetime, timezone

from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.n8n_service import build_research_payload, trigger_n8n_workflow

router = APIRouter(prefix="/research", tags=["research"])

@router.post("/",response_model=ResearchResponse)
async def create_research_job(request: ResearchRequest) :
    """Accept a research job and trigger n8n workflow"""
    job_id = str(uuid.uuid4())

    # Build and send payload for n8n
    payload = build_research_payload(job_id, request.query, request.depth)
    await trigger_n8n_workflow(payload)

    return ResearchResponse(
        job_id=job_id,
        status="queued",
        message="Research job created and workflow triggered",
        query=request.query,
        created_at=datetime.now(timezone.utc)
    )

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "research-api"}