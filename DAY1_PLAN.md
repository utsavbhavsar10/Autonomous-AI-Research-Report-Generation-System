# Day 1 — FastAPI Foundation + Notification Service

> **Goal**: A working FastAPI server with job tracking (SQLite), event logging
> (jobs_log.json), Rich-formatted terminal output, and clean endpoints to
> create / list / download research jobs and reports — all without n8n.

---

## 1. What Day 1 Delivers

By the end of Day 1 you can:

1. Start the server: `uvicorn app.main:app --reload`
2. POST a research query and get back a `job_id` instantly
3. Poll `GET /research/{job_id}` to watch status flip `queued → processing → complete`
4. List all jobs and download reports through clean REST endpoints
5. See colored startup panels and per-event panels in the terminal
6. Inspect `research.db` (SQLite) and `jobs_log.json` for full history

Day 1 is the **scaffolding**. The real research pipeline runs through it but
will be replaced with LangGraph (Day 3) and CrewAI (Day 4) without changing
any of the surface — same endpoints, same DB, same notifications.

---

## 2. Day 1 Flow (End-to-End)

```
┌─────────────────────────────────────────────────────────────────┐
│  CLIENT (curl / Postman / browser via /docs)                    │
│      POST /research  { "query": "...", "depth": "standard" }    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  FASTAPI ROUTER  (app/routers/research.py)                      │
│   1. Pydantic validates request                                 │
│   2. Generate UUID job_id                                       │
│   3. create_job() → INSERT row in SQLite (status=queued)        │
│   4. background_tasks.add_task(run_pipeline, ...)               │
│   5. Return 202 + job_id immediately                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ (response goes back to client)
                         │
                         ▼ (background task runs)
┌─────────────────────────────────────────────────────────────────┐
│  run_pipeline(job_id, query, depth)                             │
│                                                                 │
│   notifier.job_started()  ── Rich panel + jobs_log.json         │
│   update_job(status=processing)                                 │
│                                                                 │
│   ResearchService.run()                                         │
│     ├─ _plan_queries()         build search query variants      │
│     ├─ SearchService           Tavily web search                │
│     └─ ReportService           OpenAI report + save .md         │
│                                                                 │
│   update_job(status=complete, report_path=..., duration=...)    │
│   notifier.job_complete()  ── green Rich panel + log entry      │
│                                                                 │
│   on error:                                                     │
│   update_job(status=failed, error=...)                          │
│   notifier.job_failed()    ── red Rich panel + log entry        │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLIENT polls GET /research/{job_id}                            │
│   → SQLite SELECT → returns current JobStatus                   │
└─────────────────────────────────────────────────────────────────┘
```

**Key idea**: the client never waits. The HTTP response returns in
milliseconds; the work happens in a background task and the client polls for
status. SQLite is the source of truth for job state, jobs_log.json is the
append-only audit trail.

---

## 3. File Map (What Exists After Day 1)

```
app/
├── main.py                          # FastAPI app + lifespan + startup banner
│
├── routers/
│   ├── research.py                  # POST /research, GET /research, GET /research/{id}
│   └── reports.py                   # GET /reports, GET /reports/{filename}
│
├── schemas/
│   ├── research.py                  # ResearchRequest, ResearchResponse
│   └── job.py                       # JobStatus
│
├── services/
│   ├── job_service.py               # SQLite: init_db, create/update/get/get_all_jobs
│   ├── notification_service.py      # Rich panels + jobs_log.json
│   ├── research_service.py          # Orchestrates search → report (Day 3 swaps in LangGraph)
│   ├── search_service.py            # Tavily web search
│   └── report_service.py            # OpenAI markdown report + aiofiles save
│
└── utils/
    └── logger.py                    # Rich logger singleton

reports/                             # Generated .md reports land here
research.db                          # SQLite DB (auto-created on startup)
jobs_log.json                        # Append-only event log (auto-created)
```

---

## 4. Code Walkthrough

### 4.1 `app/utils/logger.py` — Rich Logger Singleton

A small wrapper around Python `logging` that routes everything through
`RichHandler`. `_configured` ensures `basicConfig` only runs once even if
multiple modules call `get_logger`. Every other module does:

```python
from app.utils.logger import get_logger
logger = get_logger(__name__)
```

Why: consistent colored output, tracebacks rendered nicely, one config point
to change later.

---

### 4.2 `app/schemas/research.py` — Request / Response Models

```python
class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=10, ...)
    depth: Optional[str] = "standard"   # quick | standard | deep
    format: Optional[str] = "markdown"
```

`min_length=10` blocks empty / one-word queries at the framework boundary —
no junk reaches the pipeline. The `Config.json_schema_extra` example fills
the `/docs` "Try it out" form with a real query so testing is one click.

`ResearchResponse` is the lean object the POST returns immediately
(`job_id`, `status`, `message`, `query`, `created_at`).

---

### 4.3 `app/schemas/job.py` — JobStatus Model

The full job record returned by `GET /research/{job_id}`. It mirrors the
SQLite schema exactly. Fields like `report_path`, `sources_count`, `error`,
`completed_at`, `duration_seconds` are `Optional` because they're only
filled in once the job finishes (or fails).

---

### 4.4 `app/services/job_service.py` — SQLite Job Tracker

Five async functions, all using `aiosqlite` so they never block the event
loop:

| Function | Purpose |
|---|---|
| `init_db()` | `CREATE TABLE IF NOT EXISTS jobs` — runs once at startup |
| `create_job(job_id, query, depth)` | INSERT new row, status="queued" |
| `update_job(job_id, **kwargs)` | Dynamic UPDATE — pass any column as a kwarg |
| `get_job(job_id)` | SELECT one — returns dict or `None` |
| `get_all_jobs(limit=20)` | SELECT recent jobs DESC |

`update_job` is the workhorse. It takes any keyword args and builds the
SQL dynamically (`status=?, report_path=?, ...`). That's why router code
can write things like:

```python
await update_job(job_id, status="complete", report_path="...", duration_seconds=12.4)
```

…without us writing a separate function for each field combination.

---

### 4.5 `app/services/notification_service.py` — Replaces n8n

This is the file that does what n8n used to do, in pure Python:

| Method | When called | What happens |
|---|---|---|
| `job_started` | beginning of `run_pipeline` | Cyan Rich panel + log event |
| `job_complete` | end of successful pipeline | Green Rich panel + log event |
| `job_failed` | exception during pipeline | Red Rich panel + log event |
| `step_update` | mid-pipeline progress (Day 3+) | Yellow inline message + log |
| `_log_event` | private helper | append JSON line to `jobs_log.json` |

Every notification does **two things**: prints to terminal (Rich panel) and
appends a JSON line to `jobs_log.json`. The terminal output is for humans
watching the server; the file is for grep / scripts / replay.

`jobs_log.json` is **JSON Lines** format — one JSON object per line. Easy to
parse with `for line in file: json.loads(line)`.

---

### 4.6 `app/routers/research.py` — The Heart of Day 1

Three endpoints, plus a small health check:

#### `POST /research`

```python
async def create_research_job(request, background_tasks):
    job_id = str(uuid.uuid4())
    await create_job(job_id, request.query, request.depth)
    background_tasks.add_task(run_pipeline, job_id, request.query, request.depth)
    return ResearchResponse(job_id=job_id, status="queued", ...)
```

Two important moves:

1. `create_job` runs **before** the background task is added. That guarantees
   the row exists in SQLite the moment the client gets `job_id` back, so a
   poll one millisecond later will succeed.
2. `background_tasks.add_task` is FastAPI's built-in primitive — the function
   runs **after** the response is sent to the client.

#### `run_pipeline` (private, runs in background)

```python
async def run_pipeline(job_id, query, depth):
    start_time = datetime.now(timezone.utc)
    await notifier.job_started(job_id, query, depth)
    await update_job(job_id, status="processing")

    try:
        result = await research_service.run(job_id, query, depth)
        # ... compute duration, update DB to complete, notify
    except Exception as e:
        await update_job(job_id, status="failed", error=str(e))
        await notifier.job_failed(job_id, query, str(e))
```

The whole pipeline is wrapped in `try / except` so a crash never leaves a
job stuck in "processing" forever — it gets marked "failed" with the
exception string.

In Day 1 this calls `ResearchService.run` directly. In Day 3 we replace that
single line with `await research_graph.ainvoke(initial_state, config)` — and
nothing else in this file changes.

#### `GET /research/{job_id}` and `GET /research`

Plain SQLite reads. The router converts ISO date strings back into
`datetime` objects so Pydantic serializes them properly in the response.

---

### 4.7 `app/routers/reports.py` — File Access

Two endpoints:

- `GET /reports` — lists files in the `reports/` folder
- `GET /reports/{filename}` — sends the markdown file

The download endpoint also has a path-traversal guard
(`os.path.abspath(file_path).startswith(os.path.abspath("reports"))`) so a
request like `/reports/../../etc/passwd` is rejected.

---

### 4.8 `app/main.py` — App Wiring

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()                  # create tables if needed
    console.print(Panel(...))        # green startup banner
    yield
    logger.info("Shutting down.")

app = FastAPI(..., lifespan=lifespan)
app.include_router(research.router)
app.include_router(reports.router)
```

The `lifespan` context manager runs at startup (before any request is
served) and shutdown. Putting `init_db()` here means the database is
guaranteed ready before the first request lands.

---

## 5. The Pieces Working Together (Concrete Example)

You run:

```bash
uvicorn app.main:app --reload
```

Terminal shows the green panel:

```
+----------------------------------------+
| Autonomous AI Research System          |
| API Docs:  http://localhost:8000/docs  |
| Status:    Running                     |
+----------------------------------------+
```

You POST:

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "NVIDIA AI chip market 2024", "depth": "standard"}'
```

Response (within ~50ms):

```json
{
  "job_id": "8c7f...",
  "status": "queued",
  "message": "Research pipeline started. Poll /research/{job_id} for status.",
  "query": "NVIDIA AI chip market 2024",
  "created_at": "2026-05-29T10:30:00+00:00"
}
```

Terminal prints:

```
+--- AI Research System ---+
| Research Job Started     |
| Job ID: 8c7f...          |
| Query:  NVIDIA AI chip..  |
| Depth:  standard         |
+--------------------------+
```

A new line appears in `jobs_log.json`:

```json
{"event": "job_started", "job_id": "8c7f...", "timestamp": "...", "query": "...", "depth": "standard"}
```

The pipeline runs in the background — Tavily searches, OpenAI writes the
report, file saved to `reports/report_8c7f...md`.

You poll:

```bash
curl http://localhost:8000/research/8c7f...
```

Response:

```json
{
  "job_id": "8c7f...",
  "status": "complete",
  "report_path": "reports/report_8c7f..._20260529_103045.md",
  "sources_count": 12,
  "duration_seconds": 18.4,
  ...
}
```

Terminal shows the green completion panel. `jobs_log.json` gets a
`job_complete` line.

---

## 6. Why Things Are The Way They Are

| Choice | Reason |
|---|---|
| `BackgroundTasks` instead of returning result inline | Tavily + GPT-4o takes 15–30s — too long for an HTTP response |
| SQLite + `aiosqlite` | Zero-config, async-friendly, one file on disk, perfect for local dev |
| `jobs_log.json` (JSONL) | Append-only audit log — losing a single line never corrupts the rest |
| Rich panels in `NotificationService` | Visual feedback during long jobs; replaces what n8n's UI used to give us |
| Pipeline wrapped in try/except | Guarantees no job ever sticks in "processing" — failure path always updates DB |
| `lifespan` for `init_db` | Table created exactly once, before any request can arrive |

---

## 7. Day 1 Success Criteria

Tick these off:

- [x] `uvicorn app.main:app` starts and shows green startup panel
- [x] `POST /research` returns `job_id` in under 200ms
- [x] `research.db` is created on first startup
- [x] `jobs_log.json` receives event lines as the pipeline runs
- [x] `GET /research/{job_id}` returns current status from SQLite
- [x] `GET /research` lists recent jobs
- [x] `GET /reports` lists generated files
- [x] `GET /reports/{filename}` downloads a report
- [x] `/docs` Swagger UI shows all endpoints
- [x] Pipeline crash → job row goes to `status="failed"` with `error` populated

---

## 8. What's Next

| Day | Focus | What changes |
|---|---|---|
| **Day 2** | Polish search + report services | Dedup sources, scoring, structured `compile_context`, better prompts |
| **Day 3** | LangGraph orchestration | Replace `ResearchService.run` body with a `StateGraph` (Planner → Researcher → Analyzer → Reporter), conditional retry on too few sources |
| **Day 4** | CrewAI multi-agent | Reporter node delegates to a 4-agent crew (Planner / Research / Writer / Reviewer); full PDF + email later |

The router, schemas, DB, notifier, and lifespan are stable from Day 1
onwards — Day 2/3/4 only swap the pipeline internals, not the surface.
