# Day 2 Plan: Research Pipeline Implementation

**Date**: 2026-05-31  
**Phase**: Phase 2 — Research Pipeline  
**Status**: Planning

---

## Objectives

Build a functional research pipeline that:
1. Accepts a research query via API
2. Performs web searches to gather information
3. Extracts and processes relevant content
4. Generates a structured markdown report
5. Saves the report to disk
6. Returns the report path and content to the client

---

## Success Criteria

- [ ] Web search integration working (SerpAPI or Tavily)
- [ ] Content extraction from search results
- [ ] LLM-powered report generation (structured markdown)
- [ ] Report saved to `reports/` directory
- [ ] API endpoint returns report metadata
- [ ] Basic error handling and logging
- [ ] Manual testing with sample queries

---

## Architecture Overview

```
POST /research
     │
     ▼
[Research Service]
     │
     ├──→ [Search Service] ──→ Web Search API
     │         │
     │         ▼
     │    Extract URLs & Snippets
     │
     ├──→ [Content Processor]
     │         │
     │         ▼
     │    Clean & Structure Data
     │
     └──→ [Report Service] ──→ LLM (OpenAI/Anthropic)
               │
               ▼
          Generate Markdown
               │
               ▼
          Save to reports/{job_id}.md
               │
               ▼
          Return Report Metadata
```

---

## Task Breakdown

### Task 1: Setup Search Service
**Priority**: High  
**Estimated Time**: 45 minutes

**Implementation Steps**:
1. Choose search provider (SerpAPI or Tavily)
2. Add API key to `.env`
3. Create `app/services/search_service.py`
4. Implement `search_web(query: str, num_results: int) -> List[SearchResult]`
5. Add error handling for API failures
6. Test with sample queries

**Dependencies**:
```python
# Add to requirements.txt
serpapi==2.4.2  # or tavily-python==0.3.0
```

**Code Structure**:
```python
# app/services/search_service.py
from typing import List, Dict
from pydantic import BaseModel

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str

class SearchService:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Perform web search and return structured results"""
        pass
```

---

### Task 2: Content Extraction & Processing
**Priority**: High  
**Estimated Time**: 30 minutes

**Implementation Steps**:
1. Create `app/utils/content_processor.py`
2. Implement text cleaning and normalization
3. Extract key information from search snippets
4. Structure data for LLM consumption
5. Handle edge cases (empty results, malformed data)

**Code Structure**:
```python
# app/utils/content_processor.py
from typing import List
from app.services.search_service import SearchResult

class ContentProcessor:
    @staticmethod
    def process_search_results(results: List[SearchResult]) -> str:
        """Convert search results into structured text for LLM"""
        pass
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove HTML, normalize whitespace, etc."""
        pass
```

---

### Task 3: Report Generation Service
**Priority**: High  
**Estimated Time**: 60 minutes

**Implementation Steps**:
1. Create `app/services/report_service.py`
2. Setup LLM client (OpenAI or Anthropic)
3. Design report generation prompt
4. Implement structured markdown output
5. Add report sections: Executive Summary, Key Findings, Detailed Analysis, Sources
6. Save report to `reports/` directory with job_id naming

**LLM Prompt Template**:
```
You are a professional research analyst. Based on the following search results, 
generate a comprehensive research report on: {query}

Search Results:
{processed_content}

Generate a structured markdown report with:
1. Executive Summary (2-3 paragraphs)
2. Key Findings (bullet points)
3. Detailed Analysis (organized by themes)
4. Sources (numbered references)

Use professional tone, cite sources, and provide actionable insights.
```

**Code Structure**:
```python
# app/services/report_service.py
from typing import Dict
import os
from datetime import datetime

class ReportService:
    def __init__(self, llm_client):
        self.llm = llm_client
        self.reports_dir = "reports"
    
    async def generate_report(
        self, 
        query: str, 
        research_data: str, 
        job_id: str
    ) -> Dict[str, str]:
        """Generate and save markdown report"""
        pass
    
    def _save_report(self, content: str, job_id: str) -> str:
        """Save report to disk and return file path"""
        pass
```

---

### Task 4: Update Research Router
**Priority**: High  
**Estimated Time**: 30 minutes

**Implementation Steps**:
1. Update `app/routers/research.py`
2. Integrate SearchService and ReportService
3. Add job status tracking (in-memory or SQLite)
4. Implement `/research` POST endpoint
5. Implement `/research/{job_id}/status` GET endpoint
6. Add proper error responses

**API Response Schema**:
```python
# app/schemas/research.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ResearchResponse(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    query: str
    created_at: datetime
    report_path: Optional[str] = None
    report_preview: Optional[str] = None  # First 500 chars

class ResearchStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    report_url: Optional[str] = None
    error: Optional[str] = None
```

---

### Task 5: Job Tracking System
**Priority**: Medium  
**Estimated Time**: 45 minutes

**Implementation Steps**:
1. Create `app/services/job_service.py`
2. Implement in-memory job store (dict) or SQLite
3. Track job lifecycle: created → searching → generating → completed
4. Add job metadata: timestamps, query, status, error messages
5. Implement job retrieval and status updates

**Code Structure**:
```python
# app/services/job_service.py
from typing import Dict, Optional
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    SEARCHING = "searching"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class JobService:
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
    
    def create_job(self, job_id: str, query: str) -> Dict:
        """Create new job entry"""
        pass
    
    def update_status(self, job_id: str, status: JobStatus, **kwargs):
        """Update job status and metadata"""
        pass
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Retrieve job by ID"""
        pass
```

---

### Task 6: Error Handling & Logging
**Priority**: Medium  
**Estimated Time**: 30 minutes

**Implementation Steps**:
1. Add structured logging with `loguru` or Python `logging`
2. Log all API requests and responses
3. Log search queries and result counts
4. Log LLM API calls and token usage
5. Implement try-catch blocks in all services
6. Return user-friendly error messages

**Logging Strategy**:
```python
import logging

logger = logging.getLogger(__name__)

# Log levels:
# - INFO: API requests, job creation, report generation
# - WARNING: API rate limits, empty search results
# - ERROR: API failures, LLM errors, file I/O errors
```

---

### Task 7: Testing & Validation
**Priority**: High  
**Estimated Time**: 45 minutes

**Test Cases**:
1. **Simple Query**: "What is FastAPI?"
   - Expected: 5-10 search results, 500-word report
2. **Complex Query**: "Compare LangChain vs LlamaIndex for RAG applications"
   - Expected: 10+ results, 1000+ word report with comparisons
3. **Edge Cases**:
   - Empty query → 400 error
   - Very long query (500+ chars) → truncate or reject
   - Search API failure → graceful error message
   - LLM timeout → retry logic

**Manual Testing Checklist**:
- [ ] POST `/research` with valid query returns job_id
- [ ] GET `/research/{job_id}/status` shows progress
- [ ] Report file created in `reports/` directory
- [ ] Report contains all required sections
- [ ] Sources are properly cited
- [ ] API returns 404 for invalid job_id
- [ ] API handles concurrent requests

---

## Environment Setup

### Required API Keys
```bash
# .env
OPENAI_API_KEY=sk-...          # or ANTHROPIC_API_KEY
SERPAPI_API_KEY=...            # or TAVILY_API_KEY
```

### Directory Structure
```
reports/
├── {job_id_1}.md
├── {job_id_2}.md
└── ...
```

---

## Dependencies to Add

```txt
# requirements.txt
openai==1.12.0              # or anthropic==0.21.0
serpapi==2.4.2              # or tavily-python==0.3.0
pydantic==2.6.1
python-dotenv==1.0.1
httpx==0.26.0               # for async HTTP requests
beautifulsoup4==4.12.3      # optional: for content extraction
```

---

## API Endpoint Specifications

### POST `/research`
**Request**:
```json
{
  "query": "What are the latest trends in AI agents?",
  "depth": "standard",
  "max_sources": 10
}
```

**Response** (202 Accepted):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "query": "What are the latest trends in AI agents?",
  "created_at": "2026-05-31T10:30:00Z",
  "status_url": "/research/550e8400-e29b-41d4-a716-446655440000/status"
}
```

### GET `/research/{job_id}/status`
**Response** (200 OK):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": "Report generated successfully",
  "report_url": "/reports/550e8400-e29b-41d4-a716-446655440000.md",
  "created_at": "2026-05-31T10:30:00Z",
  "completed_at": "2026-05-31T10:32:15Z"
}
```

---

## Implementation Order

1. **Setup** (15 min)
   - Create `reports/` directory
   - Add API keys to `.env`
   - Install dependencies

2. **Search Service** (45 min)
   - Implement web search
   - Test with sample queries

3. **Report Service** (60 min)
   - Setup LLM client
   - Implement report generation
   - Test markdown output

4. **Job Tracking** (45 min)
   - Create job service
   - Add status tracking

5. **API Integration** (30 min)
   - Update research router
   - Wire all services together

6. **Testing** (45 min)
   - Manual API testing
   - Validate report quality
   - Check error handling

**Total Estimated Time**: 4 hours

---

## Success Metrics

- ✅ API responds within 30 seconds for standard queries
- ✅ Reports are well-structured and readable
- ✅ Search results are relevant to query
- ✅ Error messages are clear and actionable
- ✅ All test cases pass
- ✅ Reports saved to disk successfully

---

## Next Steps (Day 3 Preview)

After Day 2 completion, Day 3 will focus on:
- LangGraph state management
- Conditional workflow routing
- Retry logic for failed steps
- Workflow memory and context preservation
- Integration with n8n for status updates

---

## Notes

- Keep Day 2 simple: focus on working end-to-end flow
- Don't over-engineer: in-memory job store is fine for now
- Prioritize report quality over speed
- Document any API rate limits or quotas
- Save example reports for reference

---

**End of Day 2 Plan**
