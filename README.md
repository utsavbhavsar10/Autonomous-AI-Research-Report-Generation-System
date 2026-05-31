# Autonomous AI Research & Report Generation System
## Clean Implementation Plan — No n8n Required

> **Stack**: Python · FastAPI · LangGraph · CrewAI · RAG  
> **Scope**: Local Development · Portfolio-Grade · Agentic AI  
> **n8n**: Removed from core. Optional integration guide included at the end.

---

## Table of Contents

1. [What Changed (No n8n)](#1-what-changed-no-n8n)
2. [Final Tech Stack](#2-final-tech-stack)
3. [Complete Folder Structure](#3-complete-folder-structure)
4. [Environment Setup](#4-environment-setup)
5. [Day 1 — FastAPI Foundation + Notification Service](#5-day-1--fastapi-foundation--notification-service)
6. [Day 2 — Research Pipeline + Report Generation](#6-day-2--research-pipeline--report-generation)
7. [Day 3 — LangGraph Orchestration](#7-day-3--langgraph-orchestration)
8. [Day 4 — CrewAI Multi-Agent System](#8-day-4--crewai-multi-agent-system)
9. [Folder Structure Evolution](#9-folder-structure-evolution)
10. [Full Pipeline Flow](#10-full-pipeline-flow)
11. [API Design](#11-api-design)
12. [Job Status & Tracking System](#12-job-status--tracking-system)
13. [Common Mistakes & Solutions](#13-common-mistakes--solutions)
14. [Optional: Add n8n Later](#14-optional-add-n8n-later)

---

## 1. What Changed (No n8n)

Everything n8n handled is now done in clean Python inside the project itself.

| Old (with n8n) | New (pure Python) |
|---|---|
| n8n webhook trigger on job start | `NotificationService.job_started()` — logs to file + terminal |
| n8n webhook on report complete | `NotificationService.job_complete()` — logs + prints path |
| n8n email notification | `EmailNotifier` via Python `smtplib` (optional) |
| n8n workflow execution log | `jobs_log.json` — append-only event log |
| n8n job status dashboard | `GET /research/{job_id}` — FastAPI status endpoint |
| n8n file save action | `ReportService.save_report()` — direct async file write |

**Result**: Fewer moving parts, easier debugging, faster startup, same functionality.

---

## 2. Final Tech Stack

### Core Stack (All 4 Days)

| Technology | Role | Why |
|-----------|------|-----|
| **Python 3.11+** | Primary language | Best AI ecosystem, async support |
| **FastAPI** | REST API framework | Async-native, auto docs, Pydantic validation |
| **LangGraph** | Workflow orchestration | Stateful graph, retry logic, conditional routing |
| **CrewAI** | Multi-agent framework | Role-based agents, task delegation |
| **OpenAI API** | LLM backbone | GPT-4o for all reasoning and generation |
| **Tavily** | Web search | Clean API, best for AI agent search tasks |
| **SQLite** | Job persistence | Zero-config local database for job tracking |
| **Chroma** | Vector database | Local vector store for RAG (Phase 3) |

### Replacing n8n With Python

| Need | Python Solution |
|------|----------------|
| Event logging | `NotificationService` → `jobs_log.json` |
| Job status tracking | SQLite `jobs` table |
| Terminal alerts | `print` + `logging` with colors |
| Email notification | `smtplib` (optional, 15 lines) |
| File saving | `aiofiles` async file writes |
| Scheduling | `APScheduler` or `cron` (Phase 3) |

---

## 3. Complete Folder Structure

### Final Structure (End of Day 4)

```
ai-research-system/
│
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app entry point
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── research.py                # Research job endpoints
│   │   └── reports.py                 # Report download endpoints
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── research.py                # Request/Response Pydantic models
│   │   └── job.py                     # Job status models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── search_service.py          # Tavily web search
│   │   ├── report_service.py          # Report generation + saving
│   │   ├── notification_service.py    # Replaces n8n — logging + alerts
│   │   └── job_service.py             # SQLite job tracking
│   │
│   ├── state/
│   │   ├── __init__.py
│   │   └── research_state.py          # LangGraph TypedDict state
│   │
│   ├── graphs/
│   │   ├── __init__.py
│   │   ├── research_graph.py          # LangGraph StateGraph assembly
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── planner.py             # Node: query decomposition
│   │       ├── researcher.py          # Node: web search execution
│   │       ├── analyzer.py            # Node: findings extraction
│   │       └── reporter.py            # Node: calls CrewAI crew
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner_agent.py           # CrewAI: Research Strategist
│   │   ├── research_agent.py          # CrewAI: Senior Research Analyst
│   │   ├── writer_agent.py            # CrewAI: Principal Report Writer
│   │   └── reviewer_agent.py          # CrewAI: QA Director
│   │
│   ├── crews/
│   │   ├── __init__.py
│   │   └── research_crew.py           # CrewAI Crew assembly + execution
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── research_tasks.py          # CrewAI Task definitions
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py              # File path helpers
│       ├── text_utils.py              # Text truncation, cleaning
│       └── logger.py                  # Colored terminal logger
│
├── reports/                           # Generated markdown reports
├── data/                              # Raw research data (optional cache)
├── memory/                            # LangGraph checkpoints
├── logs/                              # Application logs
├── jobs_log.json                      # Append-only event log (replaces n8n log)
├── research.db                        # SQLite job tracking database
│
├── .env                               # API keys and config
├── requirements.txt                   # All dependencies
└── README.md
```

---

## 4. Environment Setup

### Step 1: System Requirements

```bash
# Check Python version (needs 3.11+)
python --version

# Check Node.js (NOT needed anymore — no n8n!)
# You only need Python now
```

### Step 2: Create Project

```bash
mkdir ai-research-system
cd ai-research-system

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### Step 3: Install All Dependencies

Create `requirements.txt`:

```txt
# API Framework
fastapi==0.111.0
uvicorn==0.30.1
python-dotenv==1.0.1
pydantic==2.7.1

# HTTP
httpx==0.27.0
requests==2.32.3

# LLM + AI
openai==1.35.0
langchain==0.2.5
langchain-openai==0.1.9
langchain-community==0.2.5
langchain-core==0.2.9

# Orchestration
langgraph==0.1.19

# Multi-Agent
crewai==0.36.0
crewai-tools==0.4.6

# Search
tavily-python==0.3.3

# File handling
aiofiles==23.2.1
pypdf2==3.0.1

# Database (job tracking)
aiosqlite==0.20.0

# Vector DB (RAG - Phase 3)
chromadb==0.5.0

# Utilities
python-multipart==0.0.9
rich==13.7.1
```

Install:

```bash
pip install -r requirements.txt
```

### Step 4: Create .env

```env
# LLM
OPENAI_API_KEY=sk-your-openai-key-here

# Search
TAVILY_API_KEY=tvly-your-tavily-key-here
SERPER_API_KEY=your-serper-key-here

# App Config
APP_ENV=development
LOG_LEVEL=debug
MAX_RETRY_COUNT=2
MAX_SEARCH_RESULTS=5

# Optional Email Notification
EMAIL_SENDER=you@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECEIVER=you@gmail.com
```

### Step 5: Create Folder Structure

```bash
mkdir -p app/routers app/schemas app/services app/state \
         app/graphs/nodes app/agents app/crews app/tasks app/utils \
         reports data memory logs

touch app/__init__.py \
      app/routers/__init__.py \
      app/schemas/__init__.py \
      app/services/__init__.py \
      app/state/__init__.py \
      app/graphs/__init__.py \
      app/graphs/nodes/__init__.py \
      app/agents/__init__.py \
      app/crews/__init__.py \
      app/tasks/__init__.py \
      app/utils/__init__.py
```

---

## 5. Day 1 — FastAPI Foundation + Notification Service

### Objectives
- Working FastAPI server
- Pydantic schemas defined
- SQLite job tracker set up
- `NotificationService` replacing n8n
- Colored terminal logger
- Test with Postman/curl

---

### File 1: Colored Logger

`app/utils/logger.py`:

```python
import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()

def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )
    return logging.getLogger(name)
```

---

### File 2: Pydantic Schemas

`app/schemas/research.py`:

```python
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
                "format": "markdown"
            }
        }


class ResearchResponse(BaseModel):
    job_id: str
    status: str
    message: str
    query: str
    created_at: datetime
```

`app/schemas/job.py`:

```python
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
```

---

### File 3: Job Service (SQLite)

`app/services/job_service.py`:

```python
import aiosqlite
import json
from datetime import datetime
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)
DB_PATH = "research.db"


async def init_db():
    """Create jobs table if it doesn't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                query TEXT NOT NULL,
                depth TEXT DEFAULT 'standard',
                report_path TEXT,
                sources_count INTEGER DEFAULT 0,
                error TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                duration_seconds REAL
            )
        """)
        await db.commit()
    logger.info("Database initialized.")


async def create_job(job_id: str, query: str, depth: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO jobs (job_id, status, query, depth, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (job_id, "queued", query, depth, datetime.utcnow().isoformat())
        )
        await db.commit()


async def update_job(job_id: str, **kwargs):
    """Dynamically update any job fields."""
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [job_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE jobs SET {fields} WHERE job_id = ?", values)
        await db.commit()


async def get_job(job_id: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_all_jobs(limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
```

---

### File 4: Notification Service (Replaces n8n)

`app/services/notification_service.py`:

```python
import json
import aiofiles
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from app.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()
LOG_FILE = "jobs_log.json"


class NotificationService:
    """
    Handles all event notifications without n8n.
    Logs to file + rich terminal output.
    Optionally sends email (configure in .env).
    """

    async def job_started(self, job_id: str, query: str, depth: str):
        console.print(Panel(
            f"[bold cyan]🚀 Research Job Started[/bold cyan]\n"
            f"[white]Job ID:[/white] {job_id}\n"
            f"[white]Query:[/white] {query[:80]}\n"
            f"[white]Depth:[/white] {depth}",
            title="[bold]AI Research System[/bold]",
            border_style="cyan"
        ))
        await self._log_event("job_started", job_id, query=query, depth=depth)

    async def job_complete(self, job_id: str, query: str,
                           report_path: str, sources_count: int, duration: float):
        console.print(Panel(
            f"[bold green]✅ Report Generated Successfully[/bold green]\n"
            f"[white]Job ID:[/white] {job_id}\n"
            f"[white]Query:[/white] {query[:80]}\n"
            f"[white]Report:[/white] [link]{report_path}[/link]\n"
            f"[white]Sources:[/white] {sources_count}\n"
            f"[white]Duration:[/white] {duration:.1f}s",
            title="[bold]Research Complete[/bold]",
            border_style="green"
        ))
        await self._log_event("job_complete", job_id,
                              query=query, report_path=report_path,
                              sources_count=sources_count, duration=duration)

    async def job_failed(self, job_id: str, query: str, error: str):
        console.print(Panel(
            f"[bold red]❌ Research Job Failed[/bold red]\n"
            f"[white]Job ID:[/white] {job_id}\n"
            f"[white]Query:[/white] {query[:80]}\n"
            f"[white]Error:[/white] {error}",
            title="[bold]Job Failed[/bold]",
            border_style="red"
        ))
        await self._log_event("job_failed", job_id, query=query, error=error)

    async def step_update(self, job_id: str, step: str, message: str):
        console.print(f"  [dim]→[/dim] [yellow]{step}[/yellow]: {message}")
        await self._log_event("step_update", job_id, step=step, message=message)

    async def _log_event(self, event: str, job_id: str, **kwargs):
        entry = {
            "event": event,
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        async with aiofiles.open(LOG_FILE, "a") as f:
            await f.write(json.dumps(entry) + "\n")


# Optional Email Notification (uncomment to enable)
# import smtplib
# from email.message import EmailMessage
# import os
#
# async def send_email_notification(subject: str, body: str):
#     msg = EmailMessage()
#     msg["Subject"] = subject
#     msg["From"] = os.getenv("EMAIL_SENDER")
#     msg["To"] = os.getenv("EMAIL_RECEIVER")
#     msg.set_content(body)
#     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#         smtp.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
#         smtp.send_message(msg)
```

---

### File 5: FastAPI Main App

`app/main.py`:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from app.routers import research, reports
from app.services.job_service import init_db
from app.utils.logger import get_logger, console
from rich.panel import Panel

load_dotenv()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    console.print(Panel(
        "[bold green]Autonomous AI Research System[/bold green]\n"
        "[white]API Docs:[/white] http://localhost:8000/docs\n"
        "[white]Status:[/white] Running",
        border_style="green"
    ))
    yield
    # Shutdown
    logger.info("Shutting down.")


app = FastAPI(
    title="Autonomous AI Research System",
    description="Multi-agent AI research and report generation — no n8n required.",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(research.router)
app.include_router(reports.router)


@app.get("/")
async def root():
    return {
        "system": "Autonomous AI Research System",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "running"
    }
```

---

### File 6: Research Router

`app/routers/research.py`:

```python
import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime

from app.schemas.research import ResearchRequest, ResearchResponse
from app.schemas.job import JobStatus
from app.services.job_service import create_job, get_job, get_all_jobs
from app.services.notification_service import NotificationService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/research", tags=["Research"])
notifier = NotificationService()


async def run_pipeline(job_id: str, query: str, depth: str):
    """Entry point for background pipeline execution."""
    from app.graphs.research_graph import research_graph
    from app.services.job_service import update_job

    start_time = datetime.utcnow()
    await notifier.job_started(job_id, query, depth)
    await update_job(job_id, status="processing")

    initial_state = {
        "job_id": job_id,
        "query": query,
        "depth": depth,
        "sub_queries": [],
        "plan": "",
        "raw_results": [],
        "sources_count": 0,
        "key_findings": "",
        "analysis_complete": False,
        "report_content": "",
        "report_file_path": "",
        "current_step": "init",
        "retry_count": 0,
        "error": None,
        "status": "processing",
        "messages": []
    }

    try:
        config = {"configurable": {"thread_id": job_id}}
        final_state = await research_graph.ainvoke(initial_state, config)

        duration = (datetime.utcnow() - start_time).total_seconds()

        await update_job(
            job_id,
            status="complete",
            report_path=final_state.get("report_file_path"),
            sources_count=final_state.get("sources_count", 0),
            completed_at=datetime.utcnow().isoformat(),
            duration_seconds=duration
        )

        await notifier.job_complete(
            job_id, query,
            final_state.get("report_file_path", ""),
            final_state.get("sources_count", 0),
            duration
        )

    except Exception as e:
        logger.error(f"Pipeline failed for job {job_id}: {e}")
        await update_job(job_id, status="failed", error=str(e))
        await notifier.job_failed(job_id, query, str(e))


@router.post("/", response_model=ResearchResponse, status_code=202)
async def create_research_job(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
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
        created_at=datetime.utcnow()
    )


@router.get("/{job_id}", response_model=JobStatus)
async def get_research_status(job_id: str):
    """Get current status and result of a research job."""
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**job, created_at=datetime.fromisoformat(job["created_at"]))


@router.get("/", response_model=list[JobStatus])
async def list_jobs(limit: int = 20):
    """List recent research jobs."""
    jobs = await get_all_jobs(limit)
    return [
        JobStatus(**j, created_at=datetime.fromisoformat(j["created_at"]))
        for j in jobs
    ]
```

---

### File 7: Reports Router

`app/routers/reports.py`:

```python
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{filename}")
async def download_report(filename: str):
    """Download a generated report by filename."""
    file_path = f"reports/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        path=file_path,
        media_type="text/markdown",
        filename=filename
    )


@router.get("/")
async def list_reports():
    """List all generated reports."""
    if not os.path.exists("reports"):
        return []
    files = os.listdir("reports")
    return [{"filename": f, "path": f"reports/{f}"} for f in sorted(files, reverse=True)]
```

### Run and Test Day 1

```bash
uvicorn app.main:app --reload --port 8000
```

Test:
```bash
curl -X POST http://localhost:8000/research/ \
  -H "Content-Type: application/json" \
  -d '{"query": "NVIDIA and AMD AI chip market analysis 2024", "depth": "standard"}'
```

**Day 1 Success Criteria:**
- Server starts with colored startup panel
- POST returns job_id immediately
- `research.db` created automatically
- `jobs_log.json` starts receiving events
- `/docs` shows all endpoints

---

## 6. Day 2 — Research Pipeline + Report Generation

### Objectives
- Tavily web search integration
- Multi-query research execution
- GPT-4o report generation
- Async file saving

---

### File 1: Search Service

`app/services/search_service.py`:

```python
import os
from tavily import TavilyClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SearchService:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.max_results = int(os.getenv("MAX_SEARCH_RESULTS", 5))

    async def search(self, query: str, max_results: int = None) -> list[dict]:
        """Execute a single web search and return structured results."""
        max_results = max_results or self.max_results
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True
            )
            results = []
            for r in response.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0.0)
                })
            logger.debug(f"Search '{query[:50]}' → {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []

    async def search_multiple(self, queries: list[str]) -> list[dict]:
        """Run multiple queries and return deduplicated results."""
        all_results = []
        seen_urls = set()

        for query in queries:
            results = await self.search(query)
            for r in results:
                if r["url"] not in seen_urls:
                    seen_urls.add(r["url"])
                    all_results.append(r)

        logger.info(f"Multi-search: {len(queries)} queries → {len(all_results)} unique sources")
        return all_results

    def plan_queries(self, query: str, depth: str) -> list[str]:
        """Generate search query variants from the main query."""
        queries = [query]
        if depth in ["standard", "deep"]:
            queries += [
                f"{query} market size statistics 2024",
                f"{query} latest news analysis"
            ]
        if depth == "deep":
            queries += [
                f"{query} competitive comparison forecast",
                f"{query} investment trends outlook"
            ]
        return queries
```

---

### File 2: Report Service

`app/services/report_service.py`:

```python
import os
import aiofiles
from datetime import datetime
from openai import AsyncOpenAI
from app.utils.logger import get_logger

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ReportService:

    async def generate(self, query: str, key_findings: str, raw_results: list[dict]) -> str:
        """Generate a structured markdown report using GPT-4o."""

        sources_context = "\n".join([
            f"- [{r['title']}]({r['url']}): {r['content'][:400]}"
            for r in raw_results[:8]
        ])

        prompt = f"""You are a Principal Research Analyst at a top-tier strategy firm.

RESEARCH QUERY: {query}

KEY FINDINGS (pre-analyzed):
{key_findings}

SOURCE DATA:
{sources_context}

Write a comprehensive, executive-grade research report in Markdown with these sections:

# [Report Title]

## Executive Summary
## Key Findings
## Market Analysis
## Competitive Landscape
## Data & Statistics
## Trends & Outlook
## Strategic Recommendations
## Sources

Requirements:
- Professional, precise language
- Specific data points and numbers where available
- Bold key statistics
- Actionable recommendations
- Minimum 1500 words"""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4000
        )

        return response.choices[0].message.content

    async def save(self, content: str, job_id: str) -> str:
        """Save report markdown to disk and return file path."""
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{job_id[:8]}_{timestamp}.md"
        file_path = f"reports/{filename}"

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)

        logger.info(f"Report saved: {file_path}")
        return file_path
```

---

### File 3: Text Utilities

`app/utils/text_utils.py`:

```python
def truncate(text: str, max_chars: int = 1000) -> str:
    return text[:max_chars] + "..." if len(text) > max_chars else text


def compile_context(results: list[dict], max_results: int = 6) -> str:
    parts = []
    for i, r in enumerate(results[:max_results], 1):
        parts.append(
            f"[Source {i}] {r['title']}\n"
            f"URL: {r['url']}\n"
            f"{truncate(r['content'], 1200)}"
        )
    return "\n\n---\n\n".join(parts)
```

---

## 7. Day 3 — LangGraph Orchestration

### Objectives
- Define typed ResearchState
- Build 4 graph nodes
- Conditional routing with retry logic
- Compile and run the StateGraph

---

### File 1: Research State

`app/state/research_state.py`:

```python
from typing import TypedDict, Optional, List, Annotated
import operator


class ResearchState(TypedDict):
    # Input
    job_id: str
    query: str
    depth: str

    # Planning output
    sub_queries: List[str]
    plan: str

    # Research output
    raw_results: List[dict]
    sources_count: int

    # Analysis output
    key_findings: str
    analysis_complete: bool

    # Report output
    report_content: str
    report_file_path: str

    # Control
    current_step: str
    retry_count: int
    error: Optional[str]
    status: str

    # Append-only execution log
    messages: Annotated[List[str], operator.add]
```

---

### File 2: Planner Node

`app/graphs/nodes/planner.py`:

```python
import json
import os
from openai import AsyncOpenAI
from app.state.research_state import ResearchState
from app.utils.logger import get_logger

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def planner_node(state: ResearchState) -> dict:
    logger.info(f"[PLANNER] Job: {state['job_id']}")

    prompt = f"""You are a research planning expert.
Break this query into 3-5 specific, targeted web search queries.

QUERY: {state['query']}
DEPTH: {state['depth']}

Return ONLY valid JSON:
{{"queries": ["query 1", "query 2", "query 3"]}}"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        sub_queries = data.get("queries", [state["query"]])
    except Exception as e:
        logger.warning(f"Planner JSON parse failed: {e}. Using base query.")
        sub_queries = [state["query"]]

    logger.info(f"[PLANNER] Generated {len(sub_queries)} sub-queries")

    return {
        "sub_queries": sub_queries,
        "plan": f"Decomposed into {len(sub_queries)} search queries",
        "current_step": "planned",
        "messages": [f"Planner: {len(sub_queries)} queries generated"]
    }
```

---

### File 3: Researcher Node

`app/graphs/nodes/researcher.py`:

```python
from app.state.research_state import ResearchState
from app.services.search_service import SearchService
from app.utils.logger import get_logger

logger = get_logger(__name__)
search_service = SearchService()


async def researcher_node(state: ResearchState) -> dict:
    logger.info(f"[RESEARCHER] Job: {state['job_id']} | Retry: {state.get('retry_count', 0)}")

    results = await search_service.search_multiple(state["sub_queries"])

    logger.info(f"[RESEARCHER] Found {len(results)} sources")

    return {
        "raw_results": results,
        "sources_count": len(results),
        "current_step": "researched",
        "messages": [f"Researcher: {len(results)} sources collected"]
    }
```

---

### File 4: Analyzer Node

`app/graphs/nodes/analyzer.py`:

```python
import os
from openai import AsyncOpenAI
from app.state.research_state import ResearchState
from app.utils.text_utils import compile_context
from app.utils.logger import get_logger

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def analyzer_node(state: ResearchState) -> dict:
    logger.info(f"[ANALYZER] Job: {state['job_id']}")

    context = compile_context(state["raw_results"])

    prompt = f"""You are a senior research analyst.

TOPIC: {state['query']}

RESEARCH DATA:
{context}

Extract and structure:
1. Top 5-7 key findings with specific data points
2. Critical statistics and numbers
3. Main competitive dynamics
4. Emerging trends
5. Gaps or conflicting information

Be specific. Include numbers when available."""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000
    )

    findings = response.choices[0].message.content
    logger.info(f"[ANALYZER] Analysis complete")

    return {
        "key_findings": findings,
        "analysis_complete": True,
        "current_step": "analyzed",
        "messages": ["Analyzer: Key findings extracted"]
    }
```

---

### File 5: Reporter Node

`app/graphs/nodes/reporter.py`:

```python
from app.state.research_state import ResearchState
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def reporter_node(state: ResearchState) -> dict:
    logger.info(f"[REPORTER] Job: {state['job_id']} — launching CrewAI crew")

    from app.crews.research_crew import ResearchCrew
    crew = ResearchCrew()

    result = await crew.run(
        job_id=state["job_id"],
        query=state["query"],
        key_findings=state["key_findings"],
        raw_results=state["raw_results"]
    )

    logger.info(f"[REPORTER] Report saved: {result['file_path']}")

    return {
        "report_content": result["report_content"],
        "report_file_path": result["file_path"],
        "current_step": "complete",
        "status": "complete",
        "messages": [f"Reporter: Report → {result['file_path']}"]
    }
```

---

### File 6: LangGraph State Machine

`app/graphs/research_graph.py`:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.state.research_state import ResearchState
from app.graphs.nodes.planner import planner_node
from app.graphs.nodes.researcher import researcher_node
from app.graphs.nodes.analyzer import analyzer_node
from app.graphs.nodes.reporter import reporter_node
from app.utils.logger import get_logger

logger = get_logger(__name__)


def route_after_research(state: ResearchState) -> str:
    """
    Conditional routing after web search:
    - Enough sources → proceed to analyzer
    - Too few + retries left → retry researcher
    - Too few + no retries → skip to reporter
    """
    sources = state.get("sources_count", 0)
    retries = state.get("retry_count", 0)
    max_retries = 2

    if sources >= 3:
        logger.info(f"Route: {sources} sources → analyzer")
        return "analyzer"
    elif retries < max_retries:
        logger.warning(f"Route: only {sources} sources, retry {retries + 1}/{max_retries}")
        # Increment retry in state
        state["retry_count"] = retries + 1
        return "retry"
    else:
        logger.warning(f"Route: max retries reached, proceeding with {sources} sources")
        return "reporter"


def build_research_graph():
    graph = StateGraph(ResearchState)

    # Register all nodes
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("reporter", reporter_node)

    # Entry point
    graph.set_entry_point("planner")

    # Fixed edges
    graph.add_edge("planner", "researcher")

    # Conditional routing after researcher
    graph.add_conditional_edges(
        "researcher",
        route_after_research,
        {
            "analyzer": "analyzer",
            "retry": "researcher",
            "reporter": "reporter"
        }
    )

    # Fixed edges after analysis
    graph.add_edge("analyzer", "reporter")
    graph.add_edge("reporter", END)

    # Compile with memory checkpointing
    memory = MemorySaver()
    compiled = graph.compile(checkpointer=memory)
    logger.info("LangGraph research graph compiled successfully.")
    return compiled


# Singleton — compiled once at import time
research_graph = build_research_graph()
```

---

### LangGraph Flow Diagram

```
[START]
   │
   ▼
┌─────────────────────────────┐
│        PLANNER NODE          │
│  Input:  query, depth        │
│  Action: GPT-4o → sub_queries│
│  Output: sub_queries[], plan │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       RESEARCHER NODE        │
│  Input:  sub_queries[]       │
│  Action: Tavily web search   │
│  Output: raw_results[]       │
└──────────────┬──────────────┘
               │
    ┌──────────▼──────────┐
    │  CONDITIONAL ROUTING │
    │  sources >= 3?       │
    │  YES → analyzer      │
    │  NO + retries left   │
    │      → researcher    │
    │  NO + max retries    │
    │      → reporter      │
    └──────────┬──────────┘
               │
               ▼
┌─────────────────────────────┐
│        ANALYZER NODE         │
│  Input:  raw_results[]       │
│  Action: GPT-4o analysis     │
│  Output: key_findings        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│        REPORTER NODE         │
│  Input:  key_findings,       │
│          raw_results          │
│  Action: CrewAI crew.run()   │
│  Output: report_file_path    │
└──────────────┬──────────────┘
               │
             [END]
```

---

## 8. Day 4 — CrewAI Multi-Agent System

### Objectives
- 4 specialized agents with distinct roles
- Sequential task pipeline with context chaining
- Crew execution inside the reporter node
- Full end-to-end pipeline working

---

### File 1: Planner Agent

`app/agents/planner_agent.py`:

```python
from crewai import Agent


def create_planner_agent() -> Agent:
    return Agent(
        role="Research Strategist",
        goal=(
            "Analyze the research topic and design a precise, structured research strategy "
            "that identifies the most important areas to investigate."
        ),
        backstory=(
            "You are a former McKinsey research director with 20 years of experience "
            "designing research frameworks for Fortune 500 companies. You see patterns "
            "others miss and know exactly which questions to ask."
        ),
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
```

---

### File 2: Research Agent

`app/agents/research_agent.py`:

```python
from crewai import Agent
from crewai_tools import SerperDevTool


def create_research_agent() -> Agent:
    search_tool = SerperDevTool()

    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Gather comprehensive, accurate, and current data on the research topic. "
            "Prioritize credible sources, specific statistics, and verifiable facts."
        ),
        backstory=(
            "You are a veteran research analyst specializing in technology markets and "
            "competitive intelligence. You have a reputation for finding the exact "
            "data point everyone else missed."
        ),
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=5
    )
```

---

### File 3: Writer Agent

`app/agents/writer_agent.py`:

```python
from crewai import Agent


def create_writer_agent() -> Agent:
    return Agent(
        role="Principal Report Writer",
        goal=(
            "Transform raw research findings into a compelling, executive-grade "
            "research report that is precise, well-structured, and immediately actionable."
        ),
        backstory=(
            "You are a professional research writer whose reports are read by C-suite "
            "executives at top investment banks. Your work is known for clarity, "
            "precision, and the ability to make complex topics instantly understandable."
        ),
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
```

---

### File 4: Reviewer Agent

`app/agents/reviewer_agent.py`:

```python
from crewai import Agent


def create_reviewer_agent() -> Agent:
    return Agent(
        role="Quality Assurance Director",
        goal=(
            "Ensure the research report meets the highest standards of accuracy, "
            "completeness, and professional presentation before final delivery."
        ),
        backstory=(
            "You are a meticulous QA director who has reviewed thousands of "
            "research reports. You catch inconsistencies, gaps, and vague claims "
            "that others overlook. You always improve what you review."
        ),
        verbose=True,
        allow_delegation=True,
        max_iter=3
    )
```

---

### File 5: Research Tasks

`app/tasks/research_tasks.py`:

```python
from crewai import Task, Agent


def planning_task(agent: Agent, query: str) -> Task:
    return Task(
        description=f"""
Analyze this research request and create a structured research plan:

QUERY: {query}

Deliver:
1. Research scope definition (what to cover, what to exclude)
2. 5 key questions this report must answer
3. Types of data to look for (market size, growth rates, competitors, trends)
4. Recommended source types (analyst reports, earnings calls, industry data)
        """,
        expected_output=(
            "A clear research plan with defined scope, 5 key questions, "
            "and a prioritized list of data types to gather."
        ),
        agent=agent
    )


def research_task(agent: Agent, query: str, key_findings: str) -> Task:
    return Task(
        description=f"""
Conduct deep research based on this plan.

TOPIC: {query}

PRE-ANALYZED FINDINGS TO EXPAND ON:
{key_findings[:1500]}

Your research must:
- Find specific statistics (market size, growth %, revenue figures)
- Identify top 3-5 companies/players and their positioning
- Find at least 3 recent developments (last 6-12 months)
- Note analyst forecasts and projections
- Identify key risks and challenges
        """,
        expected_output=(
            "Comprehensive research findings with specific data points, "
            "company comparisons, statistics, and cited sources."
        ),
        agent=agent
    )


def writing_task(agent: Agent, query: str) -> Task:
    return Task(
        description=f"""
Write a professional research report on: {query}

Use ALL findings from the research task above.

Required structure:
# [Descriptive Report Title]

## Executive Summary
(3-4 sentences, key takeaways only)

## Key Findings
(5-7 bullet points with specific data)

## Market Analysis
(Detailed analysis with statistics, size, growth rates)

## Competitive Landscape
(Top players, market share, positioning, differentiation)

## Trends & Outlook
(Current trends + future projections with timeframes)

## Strategic Recommendations
(3-5 specific, actionable recommendations)

## Sources
(List all sources referenced)

Requirements: Professional tone, minimum 1500 words, bold key numbers.
        """,
        expected_output=(
            "A complete, professional research report in Markdown format, "
            "minimum 1500 words, with all required sections."
        ),
        agent=agent
    )


def review_task(agent: Agent) -> Task:
    return Task(
        description="""
Review the complete research report from the writing task.

Check for:
1. Factual consistency (no contradictory statements)
2. Section completeness (all required sections present and substantive)
3. Data citation accuracy (numbers referenced correctly)
4. Professional tone throughout
5. Actionability of recommendations (specific enough to act on)
6. Executive Summary alignment with body content

Make improvements directly. Output the final, polished version of the complete report.
        """,
        expected_output=(
            "The final, reviewed, and improved research report in complete Markdown format, "
            "ready for delivery."
        ),
        agent=agent
    )
```

---

### File 6: Research Crew

`app/crews/research_crew.py`:

```python
import asyncio
import os
import aiofiles
from datetime import datetime
from crewai import Crew, Process

from app.agents.planner_agent import create_planner_agent
from app.agents.research_agent import create_research_agent
from app.agents.writer_agent import create_writer_agent
from app.agents.reviewer_agent import create_reviewer_agent
from app.tasks.research_tasks import planning_task, research_task, writing_task, review_task
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResearchCrew:

    def __init__(self):
        self.planner = create_planner_agent()
        self.researcher = create_research_agent()
        self.writer = create_writer_agent()
        self.reviewer = create_reviewer_agent()

    async def run(self, job_id: str, query: str,
                  key_findings: str = "", raw_results: list = None) -> dict:
        """
        Execute the full CrewAI research crew.
        Returns dict with report_content and file_path.
        """
        raw_results = raw_results or []

        tasks = [
            planning_task(self.planner, query),
            research_task(self.researcher, query, key_findings),
            writing_task(self.writer, query),
            review_task(self.reviewer)
        ]

        crew = Crew(
            agents=[self.planner, self.researcher, self.writer, self.reviewer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        logger.info(f"[CREW] Kicking off 4-agent crew for job {job_id}")

        # crew.kickoff() is synchronous — run in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)

        report_content = str(result)
        file_path = await self._save_report(report_content, job_id)

        return {
            "report_content": report_content,
            "file_path": file_path
        }

    async def _save_report(self, content: str, job_id: str) -> str:
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = f"reports/report_{job_id[:8]}_{timestamp}.md"
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)
        logger.info(f"[CREW] Report saved: {file_path}")
        return file_path
```

---

### Final Test — Full Pipeline

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Submit research job
curl -X POST http://localhost:8000/research/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI semiconductor market analysis for NVIDIA and AMD in 2024",
    "depth": "deep"
  }'

# Poll status (replace job_id)
curl http://localhost:8000/research/YOUR-JOB-ID-HERE

# List all reports
curl http://localhost:8000/reports/

# List all jobs
curl http://localhost:8000/research/
```

**Day 4 Success Criteria:**
- 4 CrewAI agents run sequentially
- Each agent produces meaningful output visible in terminal
- Final report saved in `/reports/`
- Job status shows `complete` in SQLite
- `jobs_log.json` has full event history

---

## 9. Folder Structure Evolution

```
DAY 1                          DAY 2                          DAY 3                         DAY 4
─────────────────────          ─────────────────────          ─────────────────────         ─────────────────────
app/                           app/                           app/                          app/
├── main.py                    ├── main.py                    ├── main.py                   ├── main.py
├── routers/                   ├── routers/                   ├── routers/                  ├── routers/
│   ├── research.py            │   ├── research.py            │   ├── research.py           │   ├── research.py
│   └── reports.py             │   └── reports.py             │   └── reports.py            │   └── reports.py
├── schemas/                   ├── schemas/                   ├── schemas/                  ├── schemas/
│   ├── research.py            │   ├── research.py            │   ├── research.py           │   ├── research.py
│   └── job.py                 │   └── job.py                 │   └── job.py                │   └── job.py
├── services/                  ├── services/                  ├── services/                 ├── services/
│   ├── job_service.py         │   ├── job_service.py         │   ├── job_service.py        │   ├── job_service.py
│   └── notification_          │   ├── notification_          │   ├── notification_          │   ├── notification_
│       service.py             │   │   service.py             │   │   service.py             │   │   service.py
└── utils/                     │   ├── search_service.py ←NEW │   ├── search_service.py     │   ├── search_service.py
    ├── logger.py              │   └── report_service.py ←NEW │   └── report_service.py     │   └── report_service.py
    └── text_utils.py          └── utils/                     ├── state/              ←NEW  ├── state/
                                   ├── logger.py              │   └── research_state.py     │   └── research_state.py
reports/                           ├── text_utils.py          ├── graphs/             ←NEW  ├── graphs/
data/                              └── file_utils.py ←NEW     │   ├── research_graph.py     │   ├── research_graph.py
jobs_log.json                                                  │   └── nodes/                │   └── nodes/
research.db                   reports/                        │       ├── planner.py         │       ├── planner.py
                              data/                           │       ├── researcher.py      │       ├── researcher.py
                              jobs_log.json                   │       ├── analyzer.py        │       ├── analyzer.py
                              research.db                     │       └── reporter.py        │       └── reporter.py
                                                              └── utils/               ←NEW  ├── agents/         ←NEW
                                                                  ├── logger.py              │   ├── planner_agent.py
                                                                  └── text_utils.py          │   ├── research_agent.py
                                                                                             │   ├── writer_agent.py
                                                              reports/                        │   └── reviewer_agent.py
                                                              memory/              ←NEW       ├── crews/           ←NEW
                                                              jobs_log.json                   │   └── research_crew.py
                                                              research.db                     ├── tasks/           ←NEW
                                                                                             │   └── research_tasks.py
                                                                                             └── utils/
                                                                                                 ├── logger.py
                                                                                                 └── text_utils.py

                                                                                             reports/
                                                                                             memory/
                                                                                             logs/
                                                                                             jobs_log.json
                                                                                             research.db
```

---

## 10. Full Pipeline Flow

```
                        ┌─────────────────────────────────────┐
                        │         USER / POSTMAN / CURL        │
                        │   POST /research/  {query, depth}    │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │           FASTAPI ROUTER             │
                        │  - Validate request (Pydantic)       │
                        │  - Generate job_id (UUID)            │
                        │  - create_job() → SQLite             │
                        │  - Start BackgroundTask              │
                        │  - Return 202 + job_id immediately   │
                        └──────────────────┬──────────────────┘
                                           │ (background)
                                           ▼
                        ┌─────────────────────────────────────┐
                        │      NOTIFICATION SERVICE            │
                        │  job_started() → terminal + log      │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │       LANGGRAPH STATE MACHINE         │
                        │                                       │
                        │  ┌──────────┐                         │
                        │  │ PLANNER  │ GPT-4o → sub_queries   │
                        │  └────┬─────┘                         │
                        │       │                               │
                        │  ┌────▼─────┐                         │
                        │  │RESEARCHER│ Tavily search × N       │
                        │  └────┬─────┘                         │
                        │       │ conditional routing            │
                        │  ┌────▼─────┐                         │
                        │  │ ANALYZER │ GPT-4o key findings     │
                        │  └────┬─────┘                         │
                        │       │                               │
                        │  ┌────▼─────┐                         │
                        │  │ REPORTER │ → calls CrewAI          │
                        │  └──────────┘                         │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │        CREWAI MULTI-AGENT CREW        │
                        │                                       │
                        │  [Planner Agent]                      │
                        │    → Research strategy + scope        │
                        │         │                             │
                        │  [Research Agent] + SerperDevTool     │
                        │    → Deep web search + data           │
                        │         │                             │
                        │  [Writer Agent]                       │
                        │    → Full structured report draft     │
                        │         │                             │
                        │  [Reviewer Agent]                     │
                        │    → QA + refinement + final report   │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │           OUTPUT LAYER               │
                        │                                       │
                        │  reports/report_{id}_{ts}.md  saved  │
                        │  SQLite: status = "complete"          │
                        │  jobs_log.json: job_complete event    │
                        │  Terminal: ✅ Rich success panel      │
                        └─────────────────────────────────────┘
```

---

## 11. API Design

### Endpoints Reference

#### `POST /research/`
Start a new research job.

```json
// Request
{
  "query": "AI semiconductor market research for NVIDIA and AMD",
  "depth": "deep",
  "format": "markdown"
}

// Response 202
{
  "job_id": "3f7a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "status": "queued",
  "message": "Research pipeline started. Poll /research/{job_id} for status.",
  "query": "AI semiconductor market research for NVIDIA and AMD",
  "created_at": "2024-01-15T10:30:00"
}
```

---

#### `GET /research/{job_id}`
Poll job status.

```json
// Processing
{
  "job_id": "3f7a1b2c-...",
  "status": "processing",
  "query": "AI semiconductor market...",
  "depth": "deep",
  "report_path": null,
  "sources_count": 0,
  "error": null,
  "created_at": "2024-01-15T10:30:00",
  "completed_at": null,
  "duration_seconds": null
}

// Complete
{
  "job_id": "3f7a1b2c-...",
  "status": "complete",
  "query": "AI semiconductor market...",
  "depth": "deep",
  "report_path": "reports/report_3f7a1b2c_20240115_103045.md",
  "sources_count": 14,
  "error": null,
  "created_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:33:22",
  "duration_seconds": 202.4
}
```

---

#### `GET /research/`
List recent jobs.

```bash
curl "http://localhost:8000/research/?limit=10"
```

---

#### `GET /reports/{filename}`
Download a report file.

```bash
curl http://localhost:8000/reports/report_3f7a1b2c_20240115_103045.md
```

---

#### `GET /reports/`
List all generated reports.

```json
[
  {"filename": "report_3f7a1b2c_20240115.md", "path": "reports/report_3f7a1b2c_20240115.md"},
  {"filename": "report_9a8b7c6d_20240114.md", "path": "reports/report_9a8b7c6d_20240114.md"}
]
```

---

## 12. Job Status & Tracking System

### How It Replaces n8n Monitoring

n8n was being used partly as a job monitor. The SQLite + NotificationService combo replaces this completely.

### Job Lifecycle

```
[POST /research/]
      │
      ▼
  status: "queued"        → SQLite write, jobs_log entry
      │
      ▼
  status: "processing"    → SQLite update, terminal panel
      │
      ▼ (pipeline runs)
  status: "complete"      → SQLite update, report_path saved
      │ or
  status: "failed"        → SQLite update, error saved
```

### Query jobs_log.json

```bash
# Show all completed jobs
cat jobs_log.json | python -c "
import json, sys
for line in sys.stdin:
    e = json.loads(line)
    if e['event'] == 'job_complete':
        print(f\"{e['job_id'][:8]} | {e['query'][:50]} | {e['report_path']}\")
"

# Count events by type
cat jobs_log.json | python -c "
import json, sys
from collections import Counter
events = [json.loads(l)['event'] for l in sys.stdin]
for k, v in Counter(events).items():
    print(f'{k}: {v}')
"
```

### Query SQLite Directly

```bash
sqlite3 research.db "SELECT job_id, status, substr(query,1,50), duration_seconds FROM jobs ORDER BY created_at DESC LIMIT 10;"
```

---

## 13. Common Mistakes & Solutions

### Mistake 1: Running crew.kickoff() Inside async Without Executor

```python
# WRONG — blocks the event loop
result = crew.kickoff()

# CORRECT — runs in thread pool
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, crew.kickoff)
```

---

### Mistake 2: Context Window Overflow in Nodes

```python
# WRONG — passes all raw content to LLM
context = str(state["raw_results"])  # could be 50,000 tokens

# CORRECT — truncate and limit
from app.utils.text_utils import compile_context
context = compile_context(state["raw_results"], max_results=6)
# ~6000 tokens max
```

---

### Mistake 3: Not Handling LLM JSON Parse Failures

```python
# WRONG — crashes on bad JSON
data = json.loads(response.choices[0].message.content)

# CORRECT — fallback gracefully
try:
    data = json.loads(response.choices[0].message.content)
    sub_queries = data.get("queries", [state["query"]])
except (json.JSONDecodeError, KeyError):
    logger.warning("JSON parse failed — using base query")
    sub_queries = [state["query"]]
```

---

### Mistake 4: Background Task Errors Silently Disappearing

```python
# WRONG — no error handling
background_tasks.add_task(run_pipeline, job_id, query, depth)

# CORRECT — wrap pipeline in try/except, update DB on failure
async def run_pipeline(job_id, query, depth):
    try:
        await research_graph.ainvoke(...)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        await update_job(job_id, status="failed", error=str(e))
        await notifier.job_failed(job_id, query, str(e))
```

---

### Mistake 5: LangGraph Retry Node Mutating State Incorrectly

```python
# WRONG — modifying state dict directly in routing function
def route_after_research(state):
    state["retry_count"] += 1  # This may not persist correctly
    return "retry"

# CORRECT — return updated fields from the node itself
async def researcher_node(state):
    # ... search logic ...
    return {
        "raw_results": results,
        "sources_count": len(results),
        "retry_count": state.get("retry_count", 0) + 1  # update here
    }
```

---

### Mistake 6: Using Synchronous File Writes in Async Context

```python
# WRONG — blocks event loop
with open(file_path, "w") as f:
    f.write(content)

# CORRECT — async file writes
import aiofiles
async with aiofiles.open(file_path, "w") as f:
    await f.write(content)
```

---

## 14. Optional: Add n8n Later

> **Read this when**: Your system is working, and you want Slack notifications, Google Drive uploads, scheduled research, or third-party integrations — without writing authentication code.

---

### When n8n Becomes Worth Adding

| Scenario | Without n8n | With n8n |
|---|---|---|
| Slack notification on report complete | Write Slack API code + OAuth | 2 nodes, drag and drop |
| Save report to Google Drive | Google API + OAuth2 flow | 1 Google Drive node |
| Daily scheduled research job | APScheduler + cron | n8n Schedule trigger |
| Email with report attached | smtplib code | Gmail node, 1 click |
| Notify Notion database | Notion API code | Notion node |
| Post to Teams/Discord/Telegram | Each API separately | Single HTTP Request node |

**Rule of thumb**: If you need 2+ third-party integrations, add n8n. If you need 0–1, stay pure Python.

---

### How to Add n8n Without Breaking Existing System

The integration is purely **additive** — you don't touch any existing code.

#### Step 1: Install n8n

```bash
# Install n8n globally
npm install -g n8n

# Start n8n
n8n start
# Visit: http://localhost:5678
```

---

#### Step 2: Add n8n Webhook Call to NotificationService

Modify **only** `app/services/notification_service.py` — add one optional method:

```python
import os
import httpx

class NotificationService:
    # ... existing methods unchanged ...

    async def _trigger_n8n(self, event: str, payload: dict):
        """
        Optional n8n webhook trigger.
        Only fires if N8N_WEBHOOK_URL is set in .env.
        Existing behavior is completely unchanged if not set.
        """
        webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if not webhook_url:
            return  # n8n not configured — skip silently

        full_payload = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            **payload
        }

        try:
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json=full_payload, timeout=10.0)
            logger.debug(f"n8n triggered: {event}")
        except Exception as e:
            logger.warning(f"n8n webhook failed (non-critical): {e}")
            # Never let n8n failure break the main pipeline
```

Then call it from your existing methods:

```python
async def job_complete(self, job_id, query, report_path, sources_count, duration):
    # ... existing terminal output and log (unchanged) ...

    # Optional n8n trigger — fires only if N8N_WEBHOOK_URL is set
    await self._trigger_n8n("job_complete", {
        "job_id": job_id,
        "query": query,
        "report_path": report_path,
        "sources_count": sources_count,
        "duration_seconds": duration
    })
```

---

#### Step 3: Add to .env (Only When Ready)

```env
# Add this line to .env when you want n8n active
# Leave it out or commented to disable n8n completely
N8N_WEBHOOK_URL=http://localhost:5678/webhook/research-complete
```

---

#### Step 4: Build n8n Workflows

**Workflow 1: Report Complete → Slack Notification**

```
[Webhook: POST /webhook/research-complete]
         │
         ▼
[IF: event == "job_complete"]
         │
         ▼
[Slack: Send Message]
  Channel: #research-reports
  Message: "✅ Report ready!\nQuery: {{$json.query}}\nFile: {{$json.report_path}}"
```

---

**Workflow 2: Report Complete → Save to Google Drive**

```
[Webhook: POST /webhook/research-complete]
         │
         ▼
[Read Binary File: {{$json.report_path}}]
         │
         ▼
[Google Drive: Upload File]
  Folder: Research Reports/
  Filename: {{$json.job_id}}_report.md
```

---

**Workflow 3: Scheduled Daily Research**

```
[Schedule Trigger: Every day at 08:00]
         │
         ▼
[HTTP Request: POST http://localhost:8000/research/]
  Body: {
    "query": "AI industry daily briefing {{$now.format('MMMM D, YYYY')}}",
    "depth": "quick"
  }
         │
         ▼
[Set: Store job_id for monitoring]
```

---

**Workflow 4: Report Complete → Notion Database Entry**

```
[Webhook: research-complete]
         │
         ▼
[Notion: Create Database Item]
  Database: Research Reports
  Properties:
    Title: {{$json.query}}
    Status: Complete
    File Path: {{$json.report_path}}
    Sources: {{$json.sources_count}}
    Date: {{$now}}
```

---

### n8n Integration Architecture (When Added)

```
EXISTING SYSTEM (unchanged):
  FastAPI → LangGraph → CrewAI → File System → SQLite → Terminal

ADDED LAYER (purely optional):
  NotificationService._trigger_n8n()
         │
         ▼
  n8n Webhook (localhost:5678)
    ├── Workflow 1: Slack notification
    ├── Workflow 2: Google Drive upload
    ├── Workflow 3: Notion entry
    └── Workflow 4: Email with attachment
```

**Key design principle**: n8n is a **side-channel** — the main pipeline never depends on it. If n8n is down, the research still completes, the report is still saved, and only the notifications are missed.

---

### n8n Quick Reference

| Task | n8n Node |
|------|---------|
| Receive event from Python | Webhook node |
| Send Slack message | Slack node |
| Send email | Gmail / SMTP node |
| Save to Google Drive | Google Drive node |
| Create Notion record | Notion node |
| Run on a schedule | Schedule Trigger node |
| Call FastAPI | HTTP Request node |
| Save file to disk | Write Binary File node |
| Branch on condition | IF node |
| Wait before next step | Wait node |

---

### Summary: n8n Decision Guide

```
Do you need third-party integrations? (Slack, Drive, Notion, Teams)
  YES → Add n8n. Takes 30 min to set up.
  NO  → Stay pure Python. Jobs done.

Do you need scheduled research? (daily briefings, cron jobs)
  YES → Either APScheduler (Python) or n8n Schedule Trigger
  NO  → Don't need either.

Do you need to connect 3+ external services?
  YES → n8n is the right tool. Visual editor saves days of API work.
  NO  → NotificationService handles everything in Python.
```

---

*End of Documentation*

---

**Version**: 2.0.0 — Clean Python, No n8n Required  
**n8n**: Optional integration guide in Section 14  
**Stack**: FastAPI · LangGraph · CrewAI · SQLite · Rich