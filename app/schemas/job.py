from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobStatus(BaseModel):
    job_id: str
    status: str                    # queued | processing | complete | failed
    query: str
    depth: str
    report_path: Optional[str] = None
    sources_count: Optional[int] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None