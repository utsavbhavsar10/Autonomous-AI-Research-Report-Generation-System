## Pydantic Model
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=10, description="Research query")
    depth: Optional[str] = Field("standard", description="quick | standard | deep")
    format: Optional[str] = Field("markdown", description="markdown | pdf")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Generate AI semiconductor market research for NVIDIA and AMD",
                "depth": "standard",
                "format": "markdown",
            }
        }


class ResearchResponse(BaseModel):
    job_id: str
    status: str
    message: str
    query: str
    created_at: datetime
