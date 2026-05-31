# Day 1 Summary - What I Built and How It Works

> **Written by**: Junior Developer  
> **Date**: May 30, 2026  
> **Goal**: Build the foundation for an AI Research System

---

## What I Built Today

Today I built the **foundation** of an autonomous AI research system. It's a FastAPI backend that can:

1. Accept research queries from users
2. Run web searches using Tavily API
3. Generate professional markdown reports using OpenAI
4. Track job status in a SQLite database
5. Log all events to a JSON file
6. Provide REST endpoints to check progress and download reports

The coolest part? **Everything runs asynchronously** - users don't wait for the research to complete. They get a `job_id` instantly and can poll for status updates.

---

## The Complete Flow (Step-by-Step)

Let me walk you through what happens when someone requests a research report:

### Step 1: User Sends a Research Request

```bash
POST http://localhost:8000/research
{
  "query": "NVIDIA AI chip market 2024",
  "depth": "standard"
}
```

### Step 2: FastAPI Router Receives the Request

**File**: `app/routers/research.py` → `create_research_job()`

What happens here:
1. **Validation**: Pydantic checks the request (query must be at least 10 characters)
2. **Generate Job ID**: Create a unique UUID like `8c7f-4a2b-9d1e-...`
3. **Save to Database**: Insert a new row in SQLite with `status="queued"`
4. **Start Background Task**: Tell FastAPI to run the pipeline in the background
5. **Return Immediately**: Send back the `job_id` to the user (takes ~50ms)

```python
job_id = str(uuid.uuid4())
await create_job(job_id, request.query, request.depth)
background_tasks.add_task(run_pipeline, job_id, request.query, request.depth)
return ResearchResponse(job_id=job_id, status="queued", ...)
```

**Key insight**: The user gets their response immediately. The actual research happens in the background.

---

### Step 3: Background Pipeline Starts

**File**: `app/routers/research.py` → `run_pipeline()`

This function runs **after** the HTTP response is sent. Here's what it does:

```python
async def run_pipeline(job_id, query, depth):
    start_time = datetime.now(timezone.utc)
    
    # 1. Notify that job started
    await notifier.job_started(job_id, query, depth)
    
    # 2. Update database status
    await update_job(job_id, status="processing")
    
    try:
        # 3. Run the actual research
        result = await research_service.run(job_id, query, depth)
        
        # 4. Calculate duration
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # 5. Update database with results
        await update_job(
            job_id,
            status="complete",
            report_path=result["report_path"],
            sources_count=result["sources_count"],
            duration_seconds=duration
        )
        
        # 6. Notify completion
        await notifier.job_complete(job_id, query, result)
        
    except Exception as e:
        # If anything fails, mark job as failed
        await update_job(job_id, status="failed", error=str(e))
        await notifier.job_failed(job_id, query, str(e))
```

**Key insight**: Everything is wrapped in try/except so if something crashes, the job gets marked as "failed" instead of being stuck in "processing" forever.

---

### Step 4: Research Service Orchestrates the Work

**File**: `app/services/research_service.py` → `run()`

This is where the magic happens. The research service coordinates three sub-services:

```python
async def run(self, job_id: str, query: str, depth: str):
    # 1. Plan the search queries
    search_queries = await self._plan_queries(query, depth)
    
    # 2. Search the web
    search_results = await self.search_service.search(search_queries)
    
    # 3. Generate the report
    report_path = await self.report_service.generate_report(
        job_id, query, search_results
    )
    
    return {
        "report_path": report_path,
        "sources_count": len(search_results)
    }
```

Let me break down each step:

#### 4a. Planning Search Queries

**Method**: `_plan_queries()`

Based on the depth level, we generate different search strategies:

- **quick**: 1 query (the original query)
- **standard**: 3 queries (original + 2 variations)
- **deep**: 5 queries (original + 4 variations covering different angles)

Example for "NVIDIA AI chip market 2024":
```python
[
    "NVIDIA AI chip market 2024",
    "NVIDIA AI chip market share statistics 2024",
    "NVIDIA GPU AI accelerator competition 2024"
]
```

#### 4b. Web Search

**File**: `app/services/search_service.py`

Uses **Tavily API** to search the web. For each query:
- Sends request to Tavily
- Gets back search results with titles, URLs, and content snippets
- Collects all results into one list

```python
async def search(self, queries: List[str]) -> List[Dict]:
    all_results = []
    for query in queries:
        response = await self.client.search(
            query=query,
            max_results=5,
            include_raw_content=True
        )
        all_results.extend(response.get("results", []))
    return all_results
```

#### 4c. Report Generation

**File**: `app/services/report_service.py`

This is where OpenAI comes in:

1. **Compile Context**: Take all search results and format them into a context string
2. **Build Prompt**: Create a detailed prompt asking GPT-4o to write a professional report
3. **Call OpenAI**: Send the prompt and get back a markdown report
4. **Save to File**: Write the report to `reports/report_{job_id}_{timestamp}.md`

```python
async def generate_report(self, job_id: str, query: str, sources: List[Dict]):
    # Format all sources into readable context
    context = self._compile_context(sources)
    
    # Build the prompt
    prompt = f"""You are a professional research analyst...
    
    Research Query: {query}
    
    Source Material:
    {context}
    
    Write a comprehensive report..."""
    
    # Call OpenAI
    response = await self.client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    report_content = response.choices[0].message.content
    
    # Save to file
    filename = f"report_{job_id}_{timestamp}.md"
    async with aiofiles.open(f"reports/{filename}", "w") as f:
        await f.write(report_content)
    
    return f"reports/{filename}"
```

---

### Step 5: Notifications Throughout

**File**: `app/services/notification_service.py`

At every major step, we send notifications. Each notification does **two things**:

1. **Print to Terminal**: Show a colored Rich panel so developers can see what's happening
2. **Log to File**: Append a JSON line to `jobs_log.json` for audit trail

```python
async def job_started(self, job_id: str, query: str, depth: str):
    # Print colored panel to terminal
    console.print(Panel(
        f"Job ID: {job_id}\nQuery: {query}\nDepth: {depth}",
        title="Research Job Started",
        style="cyan"
    ))
    
    # Log to file
    await self._log_event({
        "event": "job_started",
        "job_id": job_id,
        "query": query,
        "depth": depth,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
```

---

### Step 6: Database Updates

**File**: `app/services/job_service.py`

Throughout the pipeline, we update the SQLite database:

```
Initial:     status="queued"
Pipeline starts: status="processing"
Success:     status="complete", report_path="...", duration_seconds=18.4
Failure:     status="failed", error="..."
```

The database is the **source of truth** for job status. When users poll `GET /research/{job_id}`, we just read from SQLite.

---

### Step 7: User Polls for Status

```bash
GET http://localhost:8000/research/8c7f-4a2b-9d1e-...
```

**File**: `app/routers/research.py` → `get_research_job()`

Simple database lookup:

```python
async def get_research_job(job_id: str):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**job)
```

Returns:
```json
{
  "job_id": "8c7f-4a2b-9d1e-...",
  "status": "complete",
  "query": "NVIDIA AI chip market 2024",
  "report_path": "reports/report_8c7f..._20260530_131525.md",
  "sources_count": 12,
  "duration_seconds": 18.4,
  "created_at": "2026-05-30T13:15:20Z",
  "completed_at": "2026-05-30T13:15:38Z"
}
```

---

### Step 8: User Downloads the Report

```bash
GET http://localhost:8000/reports/report_8c7f..._20260530_131525.md
```

**File**: `app/routers/reports.py` → `download_report()`

Reads the markdown file from disk and sends it back:

```python
async def download_report(filename: str):
    file_path = os.path.join("reports", filename)
    
    # Security check: prevent path traversal attacks
    if not os.path.abspath(file_path).startswith(os.path.abspath("reports")):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(file_path, media_type="text/markdown")
```

---

## The Architecture (Visual)

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                              │
│  POST /research → gets job_id → polls GET /research/{id}   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI ROUTER                           │
│  • Validates request with Pydantic                          │
│  • Creates job in SQLite (status=queued)                    │
│  • Starts background task                                   │
│  • Returns job_id immediately                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKGROUND PIPELINE                        │
│                                                             │
│  run_pipeline()                                             │
│    ├─ NotificationService.job_started()                     │
│    ├─ update_job(status="processing")                       │
│    │                                                        │
│    ├─ ResearchService.run()                                 │
│    │    ├─ _plan_queries() → ["query1", "query2", ...]     │
│    │    ├─ SearchService.search() → Tavily API             │
│    │    └─ ReportService.generate_report() → OpenAI        │
│    │                                                        │
│    ├─ update_job(status="complete", report_path=...)        │
│    └─ NotificationService.job_complete()                    │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                        │
│  • research.db (SQLite) → job status, metadata             │
│  • jobs_log.json → append-only event log                   │
│  • reports/*.md → generated markdown reports               │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Technologies I Used

| Technology | Purpose | Why I Chose It |
|------------|---------|----------------|
| **FastAPI** | Web framework | Fast, async, auto-generates API docs |
| **Pydantic** | Request validation | Type-safe, automatic validation |
| **SQLite + aiosqlite** | Database | Zero config, async-friendly, perfect for local dev |
| **Tavily API** | Web search | Built for AI agents, returns clean content |
| **OpenAI GPT-4o** | Report generation | Best at writing structured, professional content |
| **Rich** | Terminal UI | Beautiful colored output, panels, progress bars |
| **aiofiles** | Async file I/O | Non-blocking file operations |

---

## Files I Created

```
app/
├── main.py                      # FastAPI app + startup logic
├── routers/
│   ├── research.py              # POST /research, GET /research/{id}
│   └── reports.py               # GET /reports, GET /reports/{filename}
├── schemas/
│   ├── research.py              # ResearchRequest, ResearchResponse
│   └── job.py                   # JobStatus
├── services/
│   ├── job_service.py           # SQLite CRUD operations
│   ├── notification_service.py  # Rich panels + JSON logging
│   ├── research_service.py      # Orchestrates search → report
│   ├── search_service.py        # Tavily web search
│   └── report_service.py        # OpenAI report generation
└── utils/
    └── logger.py                # Rich logger singleton

reports/                         # Generated reports land here
research.db                      # SQLite database (auto-created)
jobs_log.json                    # Event log (auto-created)
```

---

## What I Learned

### 1. **Async/Await is Powerful**
Everything is `async def` and `await`. This means:
- The server can handle multiple requests at once
- Long operations (API calls, file I/O) don't block other requests
- Background tasks run without blocking the HTTP response

### 2. **Background Tasks Pattern**
FastAPI's `BackgroundTasks` is perfect for long-running operations:
- User gets instant response
- Work happens after response is sent
- No timeouts, no waiting

### 3. **Database as Source of Truth**
SQLite stores the current state of every job. Everything else (logs, notifications) is derived from that state.

### 4. **Error Handling is Critical**
Wrapping the pipeline in try/except ensures jobs never get stuck. If something fails, we:
- Mark the job as "failed"
- Store the error message
- Notify the user
- Keep the system running

### 5. **Separation of Concerns**
Each service has one job:
- `JobService` → database operations
- `SearchService` → web search
- `ReportService` → report generation
- `NotificationService` → logging and terminal output
- `ResearchService` → orchestrates everything

This makes the code easy to test and modify.

---

## Testing It Out

### Start the Server
```bash
uvicorn app.main:app --reload
```

### Create a Research Job
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest developments in quantum computing 2024",
    "depth": "standard"
  }'
```

Response:
```json
{
  "job_id": "abc-123-def-456",
  "status": "queued",
  "message": "Research pipeline started. Poll /research/{job_id} for status.",
  "query": "Latest developments in quantum computing 2024",
  "created_at": "2026-05-30T13:15:20Z"
}
```

### Check Status
```bash
curl http://localhost:8000/research/abc-123-def-456
```

### List All Jobs
```bash
curl http://localhost:8000/research
```

### Download Report
```bash
curl http://localhost:8000/reports/report_abc123_20260530_131525.md
```

---

## What's Next (Day 2+)

Day 1 built the **scaffolding**. The pipeline works but it's simple. Here's what's coming:

### Day 2: Polish the Pipeline
- Deduplicate search results (same URL shouldn't appear twice)
- Score sources by relevance
- Better context compilation
- Improved prompts for report generation

### Day 3: LangGraph Orchestration
Replace `ResearchService.run()` with a **state machine**:
```
Planner → Researcher → Analyzer → Reporter
```
Each step is a node in a graph. We can add:
- Conditional routing (if too few sources, search again)
- Retry logic
- State persistence

### Day 4: Multi-Agent System (CrewAI)
Replace the single OpenAI call with a **team of AI agents**:
- **Planner Agent**: Breaks down the query
- **Research Agent**: Finds sources
- **Writer Agent**: Drafts the report
- **Reviewer Agent**: Critiques and refines

Each agent has its own role, goal, and tools. They collaborate to produce better reports.

---

## Success Metrics

✅ All Day 1 criteria met:
- [x] Server starts with green startup panel
- [x] POST /research returns job_id in <200ms
- [x] research.db auto-created on startup
- [x] jobs_log.json receives event lines
- [x] GET /research/{job_id} returns current status
- [x] GET /research lists recent jobs
- [x] GET /reports lists generated files
- [x] GET /reports/{filename} downloads report
- [x] /docs shows Swagger UI
- [x] Pipeline crash → job marked as "failed"

**Proof**: `reports/report_b6b018e0_20260530T131525Z.md` exists, showing a complete end-to-end run.

---

## Conclusion

Day 1 was about building a **solid foundation**. I now have:
- A working REST API
- Async job processing
- Database persistence
- Event logging
- Web search integration
- AI report generation

The architecture is clean and modular. Days 2-4 will enhance the pipeline without changing the surface API. The router, database, and notification system stay the same - only the internal pipeline logic evolves.

This is how you build scalable systems: **stable interfaces, swappable implementations**.
