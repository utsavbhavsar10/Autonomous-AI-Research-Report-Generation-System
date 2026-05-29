## Pydantic Model
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ResearchRequest(BaseModel):
    query: str
    depth: Optional[str] = "standard" # "quick" | "standard" | "deep"
    format: Optional[str] = "markdown" # "markdown" | "PDF"

class ResearchResponse(BaseModel):
    job_id: str
    status: str
    message:str
    query:str
    created_at: datetime