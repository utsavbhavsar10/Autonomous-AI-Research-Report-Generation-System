# Autonomous AI Research & Report Generation System
## Complete Implementation Documentation

> **Role**: Principal AI Architect · Senior Backend Engineer · AI Workflow Engineer · Enterprise System Designer  
> **Scope**: Local Development · Portfolio-Grade · Agentic AI System  
> **Stack**: Python · FastAPI · n8n · LangGraph · CrewAI · RAG · Multi-Agent Orchestration

---

## Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [Learning Roadmap Before Building](#2-learning-roadmap-before-building)
3. [Project Development Philosophy](#3-project-development-philosophy)
4. [Core Technology Stack](#4-core-technology-stack)
5. [Phase-Wise Development Plan](#5-phase-wise-development-plan)
6. [Day-Wise Implementation Plan (4 Days)](#6-day-wise-implementation-plan-4-days)
7. [Folder Structure Evolution](#7-folder-structure-evolution)
8. [Detailed Backend Architecture](#8-detailed-backend-architecture)
9. [n8n Workflow Architecture](#9-n8n-workflow-architecture)
10. [LangGraph Architecture](#10-langgraph-architecture)
11. [CrewAI Multi-Agent Architecture](#11-crewai-multi-agent-architecture)
12. [RAG Architecture](#12-rag-architecture)
13. [Memory Architecture](#13-memory-architecture)
14. [API Design](#14-api-design)
15. [Local Development Setup Guide](#15-local-development-setup-guide)
16. [Important Engineering Concepts](#16-important-engineering-concepts)
17. [Common Mistakes & Solutions](#17-common-mistakes--solutions)
18. [MVP Strategy](#18-mvp-strategy)
19. [Future Enhancements](#19-future-enhancements)
20. [Final Expected Architecture](#20-final-expected-architecture)
21. [Final Project Outcome](#21-final-project-outcome)

---

## 1. Executive Overview

### Project Goal

The **Autonomous AI Research & Report Generation System** is a local, multi-agent AI system that accepts a natural language research query and autonomously plans, researches, analyzes, and generates a structured professional report — without human intervention at each step.

**Example query:**
```
"Generate AI semiconductor market research report for NVIDIA and AMD."
```

The system will:
- Break down the query into sub-tasks
- Search the internet and/or local documents
- Extract and analyze relevant information
- Write, review, and refine a structured report
- Generate PDF output
- Trigger downstream automations via n8n

---

### Why This Project Matters

This project sits at the intersection of three of the most powerful trends in enterprise AI:

| Trend | What This Project Demonstrates |
|-------|-------------------------------|
| Agentic AI | Agents plan and execute tasks autonomously |
| Workflow Orchestration | LangGraph manages state, retries, and routing |
| Multi-Agent Collaboration | CrewAI enables role-based agent teams |
| Automation Integration | n8n connects the AI pipeline to real-world actions |
| RAG Systems | Vector search enables context-aware document retrieval |

---

### What Skills It Demonstrates

Building this system proves mastery of:

- **Backend Engineering**: FastAPI, async Python, REST API design
- **AI Orchestration**: LangGraph state machines, conditional routing
- **Multi-Agent Systems**: CrewAI role-based agents, task delegation
- **Retrieval-Augmented Generation**: Embeddings, vector databases, chunking
- **Workflow Automation**: n8n webhooks, event-driven pipelines
- **System Architecture**: Modular, scalable, enterprise-grade design patterns

---

### Why Agentic Workflows Are Important

Traditional AI pipelines are **linear** — input goes in, output comes out. Agentic systems are **dynamic**:

```
Traditional:  Query → LLM → Response

Agentic:      Query
                ↓
              Planner Agent → breaks into tasks
                ↓
              Research Agent → searches web/docs
                ↓
              Analyst Agent → evaluates findings
                ↓
              Writer Agent → drafts structured report
                ↓
              Reviewer Agent → critiques and refines
                ↓
              Final Report + PDF + n8n Trigger
```

Agentic systems can handle **ambiguity, failure, multi-step reasoning**, and **tool use** — capabilities that are transforming enterprise software.

---

### Enterprise Use Cases

- Market research automation for investment firms
- Competitive intelligence pipelines for product teams
- Regulatory compliance document analysis
- Legal document summarization and review
- Technical literature synthesis for R&D teams

---

## 2. Learning Roadmap Before Building

### Recommended Learning Order

Follow this sequence before or during development. Do not skip phases — each builds on the previous.

---

### Stage 1 — Python & Async Fundamentals (Day 0 or alongside Day 1)

**What to learn:**
- Python virtual environments (`venv`, `pip`)
- `async`/`await` patterns in Python
- Python type hints (`BaseModel`, `TypedDict`)
- HTTP concepts: request/response, status codes, headers
- JSON handling

**Resources:**
- Python `asyncio` official docs
- Real Python: Async IO tutorial

---

### Stage 2 — FastAPI Fundamentals (Day 1)

**What to learn:**
- Creating routes with `@app.get`, `@app.post`
- Pydantic models for request/response validation
- Dependency injection (`Depends`)
- Background tasks
- OpenAPI docs (auto-generated at `/docs`)

**Key concept:** FastAPI is your system's front door. Every external call — from Postman, n8n, or a frontend — enters through FastAPI.

---

### Stage 3 — n8n Basics (Day 1)

**What to learn:**
- Installing n8n locally with `npx n8n`
- Creating workflows in the visual editor
- Webhook triggers
- HTTP Request nodes
- Connecting nodes with data flow

**Key concept:** n8n is your automation backbone. It listens for events and triggers actions — sending emails, saving files, calling APIs.

---

### Stage 4 — LLM Fundamentals (Day 2)

**What to learn:**
- How LLMs work (tokens, context window, temperature)
- OpenAI API basics (`chat.completions.create`)
- System prompts vs. user prompts
- Prompt engineering basics
- Tool/function calling

---

### Stage 5 — LangGraph Basics (Day 3)

**What to learn:**
- `StateGraph` concept
- Nodes (functions) and Edges (routing logic)
- `TypedDict` for state definition
- Conditional edges
- Checkpointing and persistence

---

### Stage 6 — CrewAI Basics (Day 4)

**What to learn:**
- `Agent` class: role, goal, backstory
- `Task` class: description, expected output, agent assignment
- `Crew` class: orchestrating agents and tasks
- Tools: web search, file reading, custom tools

---

### Stage 7 — RAG Basics (After Day 4 or Phase 3)

**What to learn:**
- Document loaders (PDF, text, web)
- Text chunking strategies
- Embeddings (OpenAI, sentence-transformers)
- Vector stores (Chroma, FAISS, Qdrant)
- Similarity search

---

## 3. Project Development Philosophy

### Why Start Simple

The single biggest mistake in AI systems projects is **building everything at once**. You end up with:
- A system that never works end-to-end
- Debugging nightmares (is the bug in the LangGraph node, the CrewAI task, the RAG retriever, or the FastAPI layer?)
- Loss of momentum and motivation

**The antidote**: Ship a working system on Day 1, even if it's primitive. Then add complexity layer by layer.

---

### MVP-First Strategy

```
Day 1 MVP:  Query → FastAPI → n8n webhook → simple response
Day 2 MVP:  Query → FastAPI → Research Service → markdown report
Day 3 MVP:  Query → FastAPI → LangGraph workflow → structured report
Day 4 MVP:  Query → FastAPI → LangGraph → CrewAI agents → full report + n8n notification
```

Each day, the system is **fully functional** — just at a different sophistication level.

---

### Principles

**Modular Architecture**: Every component is a separate module. Swap the LLM, change the vector DB, replace the search tool — without touching the rest.

**Avoid Complexity Explosion**: Add one new technology at a time. Validate it works before adding the next.

**Incremental Testing**: After every coding session, test the endpoint before moving on.

**Single Responsibility**: Each agent, node, service, and function does exactly one thing.

---

## 4. Core Technology Stack

### Main Stack (Days 1–2)

| Technology | Role | Why This Tool |
|-----------|------|---------------|
| **Python 3.11+** | Primary language | Best AI/ML ecosystem; async support; huge library support |
| **FastAPI** | API framework | Fastest Python web framework; auto docs; async-native; Pydantic validation |
| **n8n** | Workflow automation | No-code/low-code automation; visual editor; 350+ integrations; self-hostable |

---

### Extended Stack (Days 3–4)

| Technology | Role | Why This Tool |
|-----------|------|---------------|
| **LangGraph** | Workflow orchestration | Stateful graph execution; retry logic; conditional routing; checkpointing |
| **CrewAI** | Multi-agent framework | Role-based agents; task delegation; autonomous collaboration |
| **OpenAI API** | LLM backbone | GPT-4o for reasoning, planning, and generation |
| **Chroma / FAISS** | Vector database | Local, zero-config embedding storage for RAG |
| **PostgreSQL** | Persistent storage | Store reports, queries, job history |
| **SQLite** | Lightweight local DB | Fast local development without Postgres setup |

---

### How They Interact

```
[User Query]
     │
     ▼
[FastAPI] ──────────────────────────────────────────────────────┐
     │                                                           │
     ▼                                                           │
[LangGraph StateGraph]                                          │
  ├── Planner Node                                              │
  ├── Research Node ──── [Web Search Tool]                      │
  ├── RAG Node ─────────── [Vector DB / Chroma]                 │
  ├── Analysis Node                                             │
  └── Report Node ──── [CrewAI Crew]                           │
       ├── Planner Agent                                        │
       ├── Research Agent                                       │
       ├── Writer Agent                                         │
       └── Reviewer Agent                                       │
                 │                                              │
                 ▼                                              │
         [Final Report MD/PDF]                                  │
                 │                                              │
                 ▼                                              │
         [n8n Webhook] ◄──────────────────────────────────────┘
           ├── Save to disk
           ├── Send email notification
           └── Trigger downstream automation
```

---

## 5. Phase-Wise Development Plan

### Phase 1 — Foundation (Day 1)
**Objective**: Working API + n8n connection  
**Output**: POST `/research` endpoint triggers n8n webhook  
**What works**: API receives a query, sends it to n8n, n8n logs it

### Phase 2 — Research Pipeline (Day 2)
**Objective**: Real research + report generation  
**Output**: Markdown report saved to disk  
**What works**: API runs a web search, extracts content, generates a markdown report

### Phase 3 — Orchestration (Day 3)
**Objective**: Stateful workflow with LangGraph  
**Output**: Multi-step autonomous workflow with state management  
**What works**: Conditional routing, retry logic, workflow memory, structured state

### Phase 4 — Multi-Agent System (Day 4)
**Objective**: CrewAI agents collaborate on research and writing  
**Output**: Full autonomous pipeline — query to PDF to n8n notification  
**What works**: Complete end-to-end agentic system

---

## 6. Day-Wise Implementation Plan (4 Days)

---

## DAY 1 — Foundation: FastAPI + n8n Setup

### Objectives
- Set up Python project structure
- Create working FastAPI server
- Install and configure n8n locally
- Build a webhook-triggered workflow
- Test with Postman

---

### Step 1: Python Environment Setup

```bash
# Create project directory
mkdir ai-research-system
cd ai-research-system

# Create virtual environment
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify Python version (needs 3.11+)
python --version
```

---

### Step 2: Install Core Dependencies

```bash
pip install fastapi uvicorn python-dotenv httpx pydantic openai requests
```

Create `requirements.txt`:

```txt
fastapi==0.111.0
uvicorn==0.30.1
python-dotenv==1.0.1
httpx==0.27.0
pydantic==2.7.1
openai==1.35.0
requests==2.32.3
```

---

### Step 3: Project Structure (Day 1)

```
ai-research-system/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── routers/
│   │   ├── __init__.py
│   │   └── research.py      # Research endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── research.py      # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── n8n_service.py   # n8n webhook caller
├── .env
├── requirements.txt
└── README.md
```

Create all directories:
```bash
mkdir -p app/routers app/schemas app/services
touch app/__init__.py app/routers/__init__.py app/schemas/__init__.py app/services/__init__.py
```

---

### Step 4: Environment Variables

Create `.env`:

```env
OPENAI_API_KEY=sk-your-key-here
N8N_WEBHOOK_URL=http://localhost:5678/webhook/research
APP_ENV=development
LOG_LEVEL=debug
```

---

### Step 5: Pydantic Schemas

`app/schemas/research.py`:

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ResearchRequest(BaseModel):
    query: str
    depth: Optional[str] = "standard"  # "quick" | "standard" | "deep"
    format: Optional[str] = "markdown"  # "markdown" | "pdf"


class ResearchResponse(BaseModel):
    job_id: str
    status: str
    message: str
    query: str
    created_at: datetime
```

---

### Step 6: n8n Service

`app/services/n8n_service.py`:

```python
import httpx
import os
from datetime import datetime


async def trigger_n8n_webhook(payload: dict) -> dict:
    """Send data to n8n webhook and return response."""
    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                webhook_url,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return {"success": True, "status_code": response.status_code}
        except httpx.RequestError as e:
            return {"success": False, "error": str(e)}


def build_research_payload(job_id: str, query: str, depth: str) -> dict:
    """Build the payload to send to n8n."""
    return {
        "job_id": job_id,
        "query": query,
        "depth": depth,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "ai-research-system"
    }
```

---

### Step 7: Research Router

`app/routers/research.py`:

```python
import uuid
from fastapi import APIRouter
from datetime import datetime

from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.n8n_service import trigger_n8n_webhook, build_research_payload

router = APIRouter(prefix="/research", tags=["Research"])


@router.post("/", response_model=ResearchResponse)
async def create_research_job(request: ResearchRequest):
    """Accept a research query and trigger the n8n workflow."""
    job_id = str(uuid.uuid4())

    # Build and send payload to n8n
    payload = build_research_payload(job_id, request.query, request.depth)
    await trigger_n8n_webhook(payload)

    return ResearchResponse(
        job_id=job_id,
        status="queued",
        message="Research job created and workflow triggered.",
        query=request.query,
        created_at=datetime.utcnow()
    )


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "research-api"}
```

---

### Step 8: FastAPI Main App

`app/main.py`:

```python
from fastapi import FastAPI
from dotenv import load_dotenv

from app.routers import research

load_dotenv()

app = FastAPI(
    title="Autonomous AI Research System",
    description="AI-powered research and report generation API",
    version="0.1.0"
)

app.include_router(research.router)


@app.get("/")
async def root():
    return {"message": "Autonomous AI Research System is running."}
```

---

### Step 9: Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: `http://localhost:8000/docs` — your interactive Swagger UI is live.

---

### Step 10: Install and Start n8n

```bash
# Install n8n globally
npm install -g n8n

# Start n8n
n8n start
```

Visit: `http://localhost:5678`

**Create a Webhook Workflow in n8n:**

1. New Workflow → Add Node → Webhook
2. Set method: POST, path: `/research`
3. Add a "Set" node to log data
4. Activate the workflow
5. Copy the webhook URL → paste into your `.env`

---

### Step 11: Testing with Postman

```
POST http://localhost:8000/research/
Content-Type: application/json

{
  "query": "Generate AI semiconductor market research for NVIDIA and AMD",
  "depth": "standard",
  "format": "markdown"
}
```

**Expected Response:**
```json
{
  "job_id": "abc123-...",
  "status": "queued",
  "message": "Research job created and workflow triggered.",
  "query": "Generate AI semiconductor market research for NVIDIA and AMD",
  "created_at": "2024-01-15T10:30:00"
}
```

**Day 1 Success Criteria:**
- FastAPI server runs without errors
- `/docs` page loads
- POST request returns a job ID
- n8n webhook receives the payload (check n8n execution log)

---

## DAY 2 — Research Pipeline & Report Generation

### Objectives
- Build a real web search integration
- Create document processing service
- Generate structured markdown reports
- Save reports to local filesystem
- Connect research pipeline to FastAPI

---

### New Dependencies

```bash
pip install langchain langchain-openai langchain-community \
            tavily-python pypdf2 markdown beautifulsoup4 \
            aiofiles python-multipart
```

Update `requirements.txt` accordingly.

---

### New Folder Structure (Day 2 additions)

```
ai-research-system/
├── app/
│   ├── routers/
│   │   └── research.py          # Updated
│   ├── schemas/
│   │   └── research.py          # Updated
│   ├── services/
│   │   ├── n8n_service.py
│   │   ├── research_service.py  # NEW
│   │   ├── search_service.py    # NEW
│   │   └── report_service.py    # NEW
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py        # NEW
│       └── text_utils.py        # NEW
├── reports/                     # NEW - saved reports
├── data/                        # NEW - raw research data
└── .env
```

---

### Step 1: Search Service

`app/services/search_service.py`:

```python
import os
from tavily import TavilyClient


class SearchService:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Search the web and return structured results."""
        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True
        )

        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content"),
                "score": r.get("score", 0)
            })

        return results

    async def search_multiple(self, queries: list[str]) -> list[dict]:
        """Run multiple searches and aggregate results."""
        all_results = []
        for q in queries:
            results = await self.search(q)
            all_results.extend(results)
        return all_results
```

> **Note**: Get a free Tavily API key at `tavily.com`. Add `TAVILY_API_KEY=your-key` to `.env`.

---

### Step 2: Report Service

`app/services/report_service.py`:

```python
import os
import aiofiles
from datetime import datetime
from openai import AsyncOpenAI


class ReportService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate_report(self, query: str, research_data: list[dict]) -> str:
        """Generate a structured markdown report from research data."""

        # Compile research context
        context = self._compile_context(research_data)

        prompt = f"""You are a professional research analyst.

Based on the following research data, write a comprehensive, well-structured market research report.

RESEARCH QUERY: {query}

RESEARCH DATA:
{context}

Generate a report with the following structure:
# [Report Title]

## Executive Summary
## Key Findings
## Market Analysis
## Competitive Landscape
## Data & Statistics
## Conclusions & Recommendations
## Sources

Use professional language. Include specific data points where available.
Format in clean Markdown."""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000
        )

        return response.choices[0].message.content

    def _compile_context(self, results: list[dict]) -> str:
        """Compile search results into a readable context string."""
        context_parts = []
        for i, r in enumerate(results[:8], 1):  # Limit to 8 sources
            context_parts.append(
                f"[Source {i}] {r['title']}\nURL: {r['url']}\n{r['content'][:1500]}\n"
            )
        return "\n---\n".join(context_parts)

    async def save_report(self, report: str, job_id: str) -> str:
        """Save report to disk and return file path."""
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/report_{job_id[:8]}_{timestamp}.md"

        async with aiofiles.open(filename, "w") as f:
            await f.write(report)

        return filename
```

---

### Step 3: Research Service (Orchestrator)

`app/services/research_service.py`:

```python
from app.services.search_service import SearchService
from app.services.report_service import ReportService
from app.services.n8n_service import trigger_n8n_webhook


class ResearchService:
    def __init__(self):
        self.search = SearchService()
        self.report = ReportService()

    async def run(self, job_id: str, query: str, depth: str = "standard") -> dict:
        """Full research pipeline: search → analyze → report → notify."""

        # 1. Determine search queries based on depth
        queries = self._plan_queries(query, depth)

        # 2. Execute searches
        raw_results = await self.search.search_multiple(queries)

        # 3. Generate report
        report_content = await self.report.generate_report(query, raw_results)

        # 4. Save to disk
        file_path = await self.report.save_report(report_content, job_id)

        # 5. Notify n8n
        await trigger_n8n_webhook({
            "event": "report_complete",
            "job_id": job_id,
            "file_path": file_path,
            "query": query,
            "sources_count": len(raw_results)
        })

        return {
            "job_id": job_id,
            "status": "complete",
            "file_path": file_path,
            "sources": len(raw_results)
        }

    def _plan_queries(self, query: str, depth: str) -> list[str]:
        """Generate multiple search queries from the main query."""
        base_queries = [query]
        if depth in ["standard", "deep"]:
            base_queries.append(f"{query} market size statistics 2024")
            base_queries.append(f"{query} recent news analysis")
        if depth == "deep":
            base_queries.append(f"{query} competitive comparison")
            base_queries.append(f"{query} future trends forecast")
        return base_queries
```

---

### Step 4: Update Router for Background Execution

`app/routers/research.py` (updated):

```python
import uuid
from fastapi import APIRouter, BackgroundTasks
from datetime import datetime

from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.research_service import ResearchService

router = APIRouter(prefix="/research", tags=["Research"])
service = ResearchService()


@router.post("/", response_model=ResearchResponse)
async def create_research_job(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    job_id = str(uuid.uuid4())

    # Run research pipeline in background (non-blocking)
    background_tasks.add_task(
        service.run, job_id, request.query, request.depth
    )

    return ResearchResponse(
        job_id=job_id,
        status="processing",
        message="Research pipeline started. Report will be ready shortly.",
        query=request.query,
        created_at=datetime.utcnow()
    )
```

**Day 2 Success Criteria:**
- POST request starts background research
- Web search results are retrieved
- Markdown report is generated and saved in `/reports/`
- n8n receives a `report_complete` event with file path

---

## DAY 3 — LangGraph Orchestration & State Management

### Objectives
- Replace the linear research service with a LangGraph state graph
- Implement conditional routing (success/failure/retry)
- Add state persistence with checkpointing
- Build autonomous task planning within the graph

---

### New Dependencies

```bash
pip install langgraph langchain-core
```

---

### New Folder Structure (Day 3 additions)

```
ai-research-system/
├── app/
│   ├── graphs/               # NEW
│   │   ├── __init__.py
│   │   ├── research_graph.py # NEW - LangGraph state machine
│   │   └── nodes/            # NEW
│   │       ├── __init__.py
│   │       ├── planner.py
│   │       ├── researcher.py
│   │       ├── analyzer.py
│   │       └── reporter.py
│   ├── state/                # NEW
│   │   ├── __init__.py
│   │   └── research_state.py # NEW - TypedDict state definition
```

---

### Step 1: Define the State

`app/state/research_state.py`:

```python
from typing import TypedDict, Optional, List, Annotated
import operator


class ResearchState(TypedDict):
    # Input
    job_id: str
    query: str
    depth: str

    # Planning
    sub_queries: List[str]
    plan: str

    # Research
    raw_results: List[dict]
    sources_count: int

    # Analysis
    key_findings: str
    analysis_complete: bool

    # Report
    report_content: str
    report_file_path: str

    # Control flow
    current_step: str
    retry_count: int
    error: Optional[str]
    status: str

    # Metadata
    messages: Annotated[List[str], operator.add]  # Append-only log
```

---

### Step 2: Planner Node

`app/graphs/nodes/planner.py`:

```python
import os
from openai import AsyncOpenAI
from app.state.research_state import ResearchState

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def planner_node(state: ResearchState) -> ResearchState:
    """Break the research query into structured sub-queries."""

    prompt = f"""You are a research planner.
Break the following research query into 3-5 specific, targeted search queries.

QUERY: {state["query"]}

Return ONLY a JSON array of search strings. Example:
["query 1", "query 2", "query 3"]"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(response.choices[0].message.content)
    sub_queries = result.get("queries", [state["query"]])

    return {
        **state,
        "sub_queries": sub_queries,
        "plan": f"Generated {len(sub_queries)} search queries",
        "current_step": "planned",
        "messages": [f"Planner: Generated {len(sub_queries)} queries"]
    }
```

---

### Step 3: Researcher Node

`app/graphs/nodes/researcher.py`:

```python
from app.state.research_state import ResearchState
from app.services.search_service import SearchService

search_service = SearchService()


async def researcher_node(state: ResearchState) -> ResearchState:
    """Execute web searches for all sub-queries."""

    all_results = []
    for query in state["sub_queries"]:
        results = await search_service.search(query, max_results=3)
        all_results.extend(results)

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    return {
        **state,
        "raw_results": unique_results,
        "sources_count": len(unique_results),
        "current_step": "researched",
        "messages": [f"Researcher: Found {len(unique_results)} unique sources"]
    }
```

---

### Step 4: Analyzer Node

`app/graphs/nodes/analyzer.py`:

```python
import os
from openai import AsyncOpenAI
from app.state.research_state import ResearchState

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def analyzer_node(state: ResearchState) -> ResearchState:
    """Analyze raw research results and extract key findings."""

    context = "\n\n".join([
        f"Source: {r['title']}\n{r['content'][:1000]}"
        for r in state["raw_results"][:6]
    ])

    prompt = f"""Analyze the following research data about: {state['query']}

DATA:
{context}

Extract:
1. Top 5 key findings
2. Important statistics and data points
3. Main themes and patterns
4. Gaps or contradictions in the data

Be specific and factual."""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2000
    )

    return {
        **state,
        "key_findings": response.choices[0].message.content,
        "analysis_complete": True,
        "current_step": "analyzed",
        "messages": ["Analyzer: Key findings extracted"]
    }
```

---

### Step 5: Reporter Node

`app/graphs/nodes/reporter.py`:

```python
import os
import aiofiles
from datetime import datetime
from openai import AsyncOpenAI
from app.state.research_state import ResearchState

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def reporter_node(state: ResearchState) -> ResearchState:
    """Generate the final structured report."""

    prompt = f"""You are a professional report writer.

QUERY: {state['query']}

KEY FINDINGS:
{state['key_findings']}

RAW SOURCES SUMMARY:
{chr(10).join([f"- {r['title']}: {r['content'][:300]}" for r in state['raw_results'][:5]])}

Write a comprehensive, professional market research report in Markdown format.
Include: Executive Summary, Key Findings, Analysis, Recommendations, Sources."""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000
    )

    report_content = response.choices[0].message.content

    # Save report
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = f"reports/report_{state['job_id'][:8]}_{timestamp}.md"

    async with aiofiles.open(file_path, "w") as f:
        await f.write(report_content)

    return {
        **state,
        "report_content": report_content,
        "report_file_path": file_path,
        "current_step": "reported",
        "status": "complete",
        "messages": [f"Reporter: Report saved to {file_path}"]
    }
```

---

### Step 6: Build the State Graph

`app/graphs/research_graph.py`:

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.state.research_state import ResearchState
from app.graphs.nodes.planner import planner_node
from app.graphs.nodes.researcher import researcher_node
from app.graphs.nodes.analyzer import analyzer_node
from app.graphs.nodes.reporter import reporter_node


def should_retry(state: ResearchState) -> str:
    """Conditional edge: retry if insufficient sources found."""
    if state.get("sources_count", 0) < 2:
        if state.get("retry_count", 0) < 2:
            return "retry"
        return "reporter"  # Proceed despite low sources
    return "analyzer"


def build_research_graph():
    """Build and compile the research LangGraph workflow."""

    # Initialize graph with state schema
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("reporter", reporter_node)

    # Define edges
    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")

    # Conditional routing after research
    graph.add_conditional_edges(
        "researcher",
        should_retry,
        {
            "analyzer": "analyzer",
            "retry": "researcher",  # Retry search
            "reporter": "reporter"  # Skip analysis if retries exhausted
        }
    )

    graph.add_edge("analyzer", "reporter")
    graph.add_edge("reporter", END)

    # Add memory checkpointing
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# Singleton graph instance
research_graph = build_research_graph()
```

---

### Step 7: LangGraph Execution Flow Diagram

```
[START]
   │
   ▼
[PLANNER NODE]
  - Receives: query, depth
  - Does: Break query into sub-queries using GPT-4o
  - Outputs: sub_queries[], plan
   │
   ▼
[RESEARCHER NODE]
  - Receives: sub_queries[]
  - Does: Execute web searches via Tavily
  - Outputs: raw_results[], sources_count
   │
   ▼ (Conditional Edge)
  ┌─────────────────────────────────┐
  │  sources_count >= 2?            │
  │  YES → ANALYZER                 │
  │  NO + retries < 2 → RESEARCHER  │
  │  NO + retries >= 2 → REPORTER   │
  └─────────────────────────────────┘
   │
   ▼
[ANALYZER NODE]
  - Receives: raw_results[]
  - Does: Extract key findings via GPT-4o
  - Outputs: key_findings, analysis_complete
   │
   ▼
[REPORTER NODE]
  - Receives: key_findings, raw_results
  - Does: Generate + save markdown report
  - Outputs: report_content, report_file_path
   │
   ▼
[END]
```

---

### Step 8: Update Router to Use Graph

```python
# In app/routers/research.py

from app.graphs.research_graph import research_graph

@router.post("/", response_model=ResearchResponse)
async def create_research_job(request: ResearchRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    initial_state = {
        "job_id": job_id,
        "query": request.query,
        "depth": request.depth,
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

    config = {"configurable": {"thread_id": job_id}}
    background_tasks.add_task(research_graph.ainvoke, initial_state, config)

    return ResearchResponse(
        job_id=job_id,
        status="processing",
        message="LangGraph workflow started.",
        query=request.query,
        created_at=datetime.utcnow()
    )
```

**Day 3 Success Criteria:**
- LangGraph graph compiles without errors
- State flows through all nodes correctly
- Conditional routing works (retry on low sources)
- Reports are generated and saved
- Execution log shows all messages from each node

---

## DAY 4 — CrewAI Multi-Agent Integration

### Objectives
- Define specialized AI agents with roles
- Assign tasks to agents
- Build a CrewAI crew that replaces/enhances the reporter node
- Connect the complete pipeline: FastAPI → LangGraph → CrewAI → n8n

---

### New Dependencies

```bash
pip install crewai crewai-tools
```

---

### New Folder Structure (Day 4 additions)

```
ai-research-system/
├── app/
│   ├── agents/               # NEW
│   │   ├── __init__.py
│   │   ├── planner_agent.py
│   │   ├── research_agent.py
│   │   ├── writer_agent.py
│   │   └── reviewer_agent.py
│   ├── crews/                # NEW
│   │   ├── __init__.py
│   │   └── research_crew.py
│   ├── tasks/                # NEW
│   │   ├── __init__.py
│   │   └── research_tasks.py
```

---

### Step 1: Define Agents

`app/agents/planner_agent.py`:

```python
from crewai import Agent
from crewai_tools import SerperDevTool


def create_planner_agent() -> Agent:
    return Agent(
        role="Research Strategist",
        goal="Break down complex research queries into structured, actionable research plans",
        backstory="""You are an elite research strategist with 20 years of experience 
        in market intelligence and competitive analysis. You excel at identifying the 
        key questions that need answering and designing efficient research strategies.""",
        verbose=True,
        allow_delegation=True,
        max_iter=3
    )
```

`app/agents/research_agent.py`:

```python
from crewai import Agent
from crewai_tools import SerperDevTool, WebsiteSearchTool


def create_research_agent() -> Agent:
    search_tool = SerperDevTool()
    web_tool = WebsiteSearchTool()

    return Agent(
        role="Senior Research Analyst",
        goal="Find, verify, and compile accurate, comprehensive research data on any topic",
        backstory="""You are a veteran research analyst specializing in technology 
        and market intelligence. You have deep expertise in finding credible sources,
        verifying data accuracy, and synthesizing complex information into clear insights.""",
        tools=[search_tool, web_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=5
    )
```

`app/agents/writer_agent.py`:

```python
from crewai import Agent


def create_writer_agent() -> Agent:
    return Agent(
        role="Principal Report Writer",
        goal="Transform research findings into compelling, professional reports",
        backstory="""You are a professional report writer with expertise in creating 
        executive-grade market research reports. Your reports are known for clarity,
        precision, actionable insights, and professional presentation.""",
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
```

`app/agents/reviewer_agent.py`:

```python
from crewai import Agent


def create_reviewer_agent() -> Agent:
    return Agent(
        role="Quality Assurance Director",
        goal="Review and improve report quality, accuracy, and completeness",
        backstory="""You are a meticulous QA director who ensures all research reports 
        meet the highest standards. You identify gaps, factual inconsistencies, 
        and opportunities for clearer communication.""",
        verbose=True,
        allow_delegation=True,
        max_iter=3
    )
```

---

### Step 2: Define Tasks

`app/tasks/research_tasks.py`:

```python
from crewai import Task
from crewai import Agent


def create_planning_task(agent: Agent, query: str) -> Task:
    return Task(
        description=f"""
        Analyze this research query and create a detailed research plan:
        
        QUERY: {query}
        
        Your plan should include:
        1. Key research areas to explore
        2. Specific sub-questions to answer
        3. Priority order for research
        4. Types of data to look for (statistics, trends, competitors, etc.)
        """,
        expected_output="A structured research plan with 3-5 specific research areas and sub-questions",
        agent=agent
    )


def create_research_task(agent: Agent, query: str, research_plan: str = "") -> Task:
    return Task(
        description=f"""
        Conduct comprehensive research based on the following:
        
        ORIGINAL QUERY: {query}
        RESEARCH PLAN: {research_plan}
        
        Research Requirements:
        - Find at least 5 credible sources
        - Gather specific statistics and data points
        - Identify key players, trends, and competitive landscape
        - Note publication dates for recency verification
        """,
        expected_output="Comprehensive research findings with sources, statistics, and key insights organized by topic",
        agent=agent
    )


def create_writing_task(agent: Agent, query: str) -> Task:
    return Task(
        description=f"""
        Write a professional research report based on the research findings provided.
        
        TOPIC: {query}
        
        Required Report Structure:
        # [Report Title]
        ## Executive Summary (3-4 sentences)
        ## Key Findings (5-7 bullet points with data)
        ## Market Analysis (detailed analysis with statistics)
        ## Competitive Landscape (key players and positioning)
        ## Trends & Outlook (future projections)
        ## Recommendations (3-5 actionable items)
        ## Sources (properly cited)
        
        Requirements:
        - Professional, executive-grade language
        - Specific data points throughout
        - Formatted in clean Markdown
        - 1500-2500 words
        """,
        expected_output="A complete, professional market research report in Markdown format",
        agent=agent
    )


def create_review_task(agent: Agent) -> Task:
    return Task(
        description="""
        Review the research report for:
        
        1. Factual accuracy and consistency
        2. Completeness (are all sections present and substantive?)
        3. Clarity and professional tone
        4. Data citation accuracy
        5. Actionability of recommendations
        
        Provide specific improvements and output the final, refined version of the report.
        """,
        expected_output="A refined, final version of the research report with all improvements applied",
        agent=agent
    )
```

---

### Step 3: Assemble the Crew

`app/crews/research_crew.py`:

```python
import os
import aiofiles
from datetime import datetime
from crewai import Crew, Process

from app.agents.planner_agent import create_planner_agent
from app.agents.research_agent import create_research_agent
from app.agents.writer_agent import create_writer_agent
from app.agents.reviewer_agent import create_reviewer_agent
from app.tasks.research_tasks import (
    create_planning_task, create_research_task,
    create_writing_task, create_review_task
)


class ResearchCrew:
    def __init__(self):
        self.planner = create_planner_agent()
        self.researcher = create_research_agent()
        self.writer = create_writer_agent()
        self.reviewer = create_reviewer_agent()

    async def run(self, job_id: str, query: str) -> dict:
        """Run the full CrewAI research crew and return results."""

        # Define tasks (sequential pipeline)
        tasks = [
            create_planning_task(self.planner, query),
            create_research_task(self.researcher, query),
            create_writing_task(self.writer, query),
            create_review_task(self.reviewer)
        ]

        # Assemble crew
        crew = Crew(
            agents=[self.planner, self.researcher, self.writer, self.reviewer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        # Execute (blocking - run in executor for async compatibility)
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)

        # Save report
        report_content = str(result)
        file_path = await self._save_report(report_content, job_id)

        return {
            "job_id": job_id,
            "status": "complete",
            "report_content": report_content,
            "file_path": file_path
        }

    async def _save_report(self, content: str, job_id: str) -> str:
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"reports/crew_report_{job_id[:8]}_{timestamp}.md"
        async with aiofiles.open(path, "w") as f:
            await f.write(content)
        return path
```

---

### Step 4: Full Integration — LangGraph + CrewAI

Update the reporter node to use CrewAI:

`app/graphs/nodes/reporter.py` (updated):

```python
from app.state.research_state import ResearchState
from app.crews.research_crew import ResearchCrew
from app.services.n8n_service import trigger_n8n_webhook

crew_runner = ResearchCrew()


async def reporter_node(state: ResearchState) -> ResearchState:
    """Use CrewAI crew to generate the final polished report."""

    result = await crew_runner.run(
        job_id=state["job_id"],
        query=state["query"]
    )

    # Notify n8n on completion
    await trigger_n8n_webhook({
        "event": "crew_report_complete",
        "job_id": state["job_id"],
        "file_path": result["file_path"],
        "query": state["query"]
    })

    return {
        **state,
        "report_content": result["report_content"],
        "report_file_path": result["file_path"],
        "current_step": "complete",
        "status": "complete",
        "messages": [f"CrewAI: Report complete → {result['file_path']}"]
    }
```

---

### Final Pipeline Flow (Day 4)

```
POST /research
     │
     ▼
[FastAPI Router]
  - Validates request
  - Creates job_id
  - Starts background task
     │
     ▼
[LangGraph StateGraph]
  ├── [Planner Node] → breaks query into sub-queries
  ├── [Researcher Node] → executes web searches
  ├── [Analyzer Node] → extracts key findings
  └── [Reporter Node]
         │
         ▼
    [CrewAI Crew]
      ├── Planner Agent → research strategy
      ├── Research Agent → deep web search
      ├── Writer Agent → drafts report
      └── Reviewer Agent → refines report
         │
         ▼
    [Markdown Report saved to /reports/]
         │
         ▼
    [n8n Webhook triggered]
      ├── Save to database
      ├── Send email notification
      └── Trigger downstream actions
```

**Day 4 Success Criteria:**
- CrewAI crew runs all 4 agents in sequence
- Each agent produces meaningful output
- Final report is saved to disk
- n8n receives `crew_report_complete` event
- End-to-end pipeline works from single POST request

---

## 7. Folder Structure Evolution

### Day 1 Structure
```
ai-research-system/
├── app/
│   ├── main.py
│   ├── routers/research.py
│   ├── schemas/research.py
│   └── services/n8n_service.py
├── .env
└── requirements.txt
```

### Day 2 Structure
```
ai-research-system/
├── app/
│   ├── main.py
│   ├── routers/research.py
│   ├── schemas/research.py
│   ├── services/
│   │   ├── n8n_service.py
│   │   ├── research_service.py     ← NEW
│   │   ├── search_service.py       ← NEW
│   │   └── report_service.py       ← NEW
│   └── utils/
│       ├── file_utils.py           ← NEW
│       └── text_utils.py           ← NEW
├── reports/                        ← NEW
├── data/                           ← NEW
├── .env
└── requirements.txt
```

### Day 3 Structure
```
ai-research-system/
├── app/
│   ├── main.py
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── state/
│   │   └── research_state.py       ← NEW
│   └── graphs/                     ← NEW
│       ├── research_graph.py
│       └── nodes/
│           ├── planner.py
│           ├── researcher.py
│           ├── analyzer.py
│           └── reporter.py
├── reports/
├── data/
├── .env
└── requirements.txt
```

### Day 4 (Final) Structure
```
ai-research-system/
├── app/
│   ├── main.py
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── state/
│   ├── graphs/
│   ├── agents/                     ← NEW
│   │   ├── planner_agent.py
│   │   ├── research_agent.py
│   │   ├── writer_agent.py
│   │   └── reviewer_agent.py
│   ├── crews/                      ← NEW
│   │   └── research_crew.py
│   └── tasks/                      ← NEW
│       └── research_tasks.py
├── reports/
├── data/
├── memory/                         ← NEW (LangGraph checkpoints)
├── .env
└── requirements.txt
```

---

## 8. Detailed Backend Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                  │
│         FastAPI Routers — HTTP request handling       │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                  ORCHESTRATION LAYER                  │
│       LangGraph StateGraph — workflow control         │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                  AGENT LAYER (CrewAI)                 │
│    Planner · Researcher · Writer · Reviewer           │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                   SERVICE LAYER                       │
│   SearchService · ReportService · N8nService          │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                  INFRASTRUCTURE LAYER                 │
│   Vector DB · File System · PostgreSQL · n8n          │
└─────────────────────────────────────────────────────┘
```

### Module Responsibilities

| Module | Path | Responsibility |
|--------|------|---------------|
| **Router** | `app/routers/` | Handle HTTP, validate input, trigger background tasks |
| **Schema** | `app/schemas/` | Pydantic models for request/response validation |
| **Service** | `app/services/` | Business logic: search, report generation, n8n calls |
| **State** | `app/state/` | TypedDict definition for LangGraph state |
| **Graph** | `app/graphs/` | LangGraph StateGraph assembly and compilation |
| **Node** | `app/graphs/nodes/` | Individual graph node functions |
| **Agent** | `app/agents/` | CrewAI Agent definitions with roles and tools |
| **Task** | `app/tasks/` | CrewAI Task definitions with expected outputs |
| **Crew** | `app/crews/` | CrewAI Crew assembly and execution |
| **Utils** | `app/utils/` | Shared utilities: file I/O, text processing |

---

## 9. n8n Workflow Architecture

### Workflow 1: Research Job Received

```
[Webhook: POST /research]
         │
         ▼
[Set Node: Extract job_id, query]
         │
         ▼
[IF Node: depth == "deep"?]
    YES ─→ [Send Slack Notification: "Deep research started"]
    NO  ─→ [Continue]
         │
         ▼
[Wait Node: 30 seconds]
         │
         ▼
[HTTP Request: GET /research/{job_id}/status]
```

---

### Workflow 2: Report Complete Notification

```
[Webhook: POST /webhook/report-complete]
         │
         ▼
[Set Node: Parse payload]
         │
         ▼
[Write Binary File: Save report to /outputs/]
         │
         ├──→ [Send Email: Report ready notification]
         │
         └──→ [HTTP Request: Update job status in DB]
```

---

### Workflow Diagram

```
n8n Workflow: Research Pipeline Monitor

 ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
 │   Webhook    │────→│  Extract     │────→│  Conditional     │
 │  (Trigger)   │     │  Payload     │     │  Routing         │
 └──────────────┘     └──────────────┘     └──────┬───────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                     ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
                     │ Save Report  │    │  Send Email  │    │  Update Database │
                     │  to Disk     │    │Notification  │    │     Status       │
                     └──────────────┘    └──────────────┘    └──────────────────┘
```

---

## 10. LangGraph Architecture

### Core Concepts

| Concept | Definition | Example |
|---------|-----------|---------|
| **StateGraph** | A directed graph where nodes share a typed state | `ResearchState` TypedDict |
| **Node** | An async function that reads/modifies state | `planner_node`, `researcher_node` |
| **Edge** | A fixed transition between two nodes | `planner → researcher` |
| **Conditional Edge** | Dynamic routing based on state values | Route to retry or analyzer |
| **Checkpoint** | Persisted snapshot of state at a node | Enables resume and replay |
| **Thread** | A unique execution instance (identified by `thread_id`) | One per job |

---

### State Flow Diagram

```
ResearchState at each node:

INITIAL STATE:
  job_id: "abc123"
  query: "NVIDIA market analysis"
  sub_queries: []
  raw_results: []
  status: "processing"

AFTER PLANNER:
  sub_queries: ["NVIDIA revenue 2024", "NVIDIA GPU market share", ...]
  plan: "Generated 4 queries"
  current_step: "planned"

AFTER RESEARCHER:
  raw_results: [{title, url, content}, ...]
  sources_count: 12
  current_step: "researched"

AFTER ANALYZER:
  key_findings: "1. NVIDIA revenue grew 122%... 2. ..."
  analysis_complete: true
  current_step: "analyzed"

AFTER REPORTER:
  report_content: "# NVIDIA Market Analysis..."
  report_file_path: "reports/report_abc123_20240115.md"
  status: "complete"
```

---

### Retry Logic Pattern

```python
def should_retry(state: ResearchState) -> str:
    retry_count = state.get("retry_count", 0)
    sources = state.get("sources_count", 0)
    
    if sources < 2 and retry_count < 2:
        # Increment retry counter
        state["retry_count"] = retry_count + 1
        return "retry"   # → back to researcher node
    
    return "analyzer"    # → proceed
```

---

## 11. CrewAI Multi-Agent Architecture

### Agent Roles and Responsibilities

```
┌─────────────────────────────────────────────────────────┐
│                    RESEARCH CREW                          │
│                                                           │
│  ┌─────────────────┐     ┌──────────────────────────┐   │
│  │ PLANNER AGENT   │────→│ Tasks:                   │   │
│  │ Research        │     │ - Analyze query           │   │
│  │ Strategist      │     │ - Create research plan    │   │
│  │                 │     │ - Define search areas     │   │
│  └─────────────────┘     └──────────────────────────┘   │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────┐     ┌──────────────────────────┐   │
│  │ RESEARCH AGENT  │────→│ Tasks:                   │   │
│  │ Senior Research │     │ - Web search             │   │
│  │ Analyst         │     │ - Verify sources         │   │
│  │ Tools: Serper,  │     │ - Extract data points    │   │
│  │ WebSearch       │     │ - Compile findings       │   │
│  └─────────────────┘     └──────────────────────────┘   │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────┐     ┌──────────────────────────┐   │
│  │ WRITER AGENT    │────→│ Tasks:                   │   │
│  │ Principal       │     │ - Structure report       │   │
│  │ Report Writer   │     │ - Write sections         │   │
│  │                 │     │ - Add data citations     │   │
│  └─────────────────┘     └──────────────────────────┘   │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────┐     ┌──────────────────────────┐   │
│  │ REVIEWER AGENT  │────→│ Tasks:                   │   │
│  │ QA Director     │     │ - Check accuracy         │   │
│  │                 │     │ - Improve clarity        │   │
│  │                 │     │ - Final refinement       │   │
│  └─────────────────┘     └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Process Types

| Process | Description | When to Use |
|---------|-------------|-------------|
| `Process.sequential` | Tasks run in order, each sees previous output | Default — most use cases |
| `Process.hierarchical` | Manager agent delegates to workers | Complex, dynamic workflows |

---

## 12. RAG Architecture

### When to Add RAG

Add RAG in **Phase 3** (after Day 4) when you want agents to:
- Query your own document library
- Reference proprietary internal documents
- Search previously generated reports
- Avoid re-searching the web for known information

---

### RAG Pipeline

```
INGESTION PIPELINE:
Document (PDF/Text/Web)
         │
         ▼
[Document Loader] — PyPDF2, BeautifulSoup, LangChain loaders
         │
         ▼
[Text Splitter] — RecursiveCharacterTextSplitter
  chunk_size=1000, chunk_overlap=200
         │
         ▼
[Embedding Model] — OpenAI text-embedding-3-small
         │
         ▼
[Vector Store] — Chroma (local) or Qdrant (advanced)
         │
         ▼
[Persisted to disk: ./chroma_db/]


RETRIEVAL PIPELINE:
Research Query
         │
         ▼
[Query Embedding] — same embedding model
         │
         ▼
[Similarity Search] — top_k=5 most relevant chunks
         │
         ▼
[Context Injection] — inject into agent/node prompt
         │
         ▼
[LLM Generation] — answer grounded in retrieved context
```

---

### RAG Implementation (Phase 3)

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )

    async def ingest_document(self, file_path: str):
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = splitter.split_documents(documents)
        self.vectorstore.add_documents(chunks)

    async def retrieve(self, query: str, k: int = 5) -> list[str]:
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
```

---

## 13. Memory Architecture

### Memory Types in This System

| Memory Type | Implementation | Scope | Persistence |
|-------------|---------------|-------|-------------|
| **Short-term** | LangGraph state (TypedDict) | Single workflow run | In-memory |
| **Workflow** | LangGraph MemorySaver | Across graph nodes | Session |
| **Long-term** | SQLite/PostgreSQL | Across all runs | Permanent |
| **Vector** | Chroma/FAISS | Semantic similarity search | Disk |
| **Agent** | CrewAI task context | Within crew execution | Session |

---

### Memory Architecture Diagram

```
SHORT-TERM MEMORY (per run):
  ResearchState TypedDict
  ├── query
  ├── sub_queries
  ├── raw_results
  └── report_content

WORKFLOW MEMORY (LangGraph):
  MemorySaver checkpoints
  ├── thread_id: "job-abc123"
  ├── checkpoint at each node
  └── enables resume on failure

LONG-TERM MEMORY (SQLite):
  jobs table
  ├── id, query, status, created_at
  ├── report_path
  └── metadata (JSON)

VECTOR MEMORY (Chroma):
  Previous reports embedded
  ├── Similarity search on new queries
  ├── Avoid duplicate research
  └── Build institutional knowledge
```

---

### Agent Memory Sharing

CrewAI agents within a single crew share context through **task output chaining**:

```
Planner output → injected into Researcher task description
Researcher output → injected into Writer task description
Writer output → injected into Reviewer task description
```

This creates a coherent information chain without requiring a shared external memory store.

---

## 14. API Design

### Endpoints

#### POST /research/
Start a new research job.

```json
Request:
{
  "query": "Generate AI semiconductor market research for NVIDIA and AMD",
  "depth": "standard",
  "format": "markdown"
}

Response (202 Accepted):
{
  "job_id": "3f7a1b2c-...",
  "status": "processing",
  "message": "LangGraph workflow started.",
  "query": "Generate AI semiconductor market research...",
  "created_at": "2024-01-15T10:30:00"
}
```

---

#### GET /research/{job_id}
Check job status and retrieve report path.

```json
Response (200 OK):
{
  "job_id": "3f7a1b2c-...",
  "status": "complete",
  "query": "...",
  "report_path": "reports/report_3f7a1b2c_20240115.md",
  "sources_count": 12,
  "created_at": "...",
  "completed_at": "..."
}
```

---

#### GET /research/{job_id}/report
Download the generated report.

```
Response: text/markdown file download
```

---

#### GET /research/health
Health check endpoint.

```json
{
  "status": "ok",
  "service": "research-api",
  "version": "1.0.0"
}
```

---

### Async Pattern

All endpoints use FastAPI's `BackgroundTasks` for non-blocking execution:

```python
@router.post("/")
async def create_job(request: ResearchRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_pipeline, job_id, request.query)
    return {"job_id": job_id, "status": "processing"}
    # Returns immediately — pipeline runs in background
```

---

## 15. Local Development Setup Guide

### System Requirements

| Requirement | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Primary language |
| Node.js | 18+ | n8n runtime |
| Git | Any | Version control |
| VS Code | Latest | IDE |

---

### Complete Setup Script

```bash
# 1. Clone/create project
mkdir ai-research-system && cd ai-research-system

# 2. Python environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 3. Install Python dependencies (Day 1)
pip install fastapi uvicorn python-dotenv httpx pydantic openai requests

# 4. Install n8n
npm install -g n8n

# 5. Create .env
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=your-tavily-key
SERPER_API_KEY=your-serper-key
N8N_WEBHOOK_URL=http://localhost:5678/webhook/research
APP_ENV=development
EOF

# 6. Start FastAPI server
uvicorn app.main:app --reload --port 8000

# 7. Start n8n (in separate terminal)
n8n start
```

---

### API Keys Required

| Service | Purpose | Free Tier | URL |
|---------|---------|-----------|-----|
| OpenAI | LLM backbone | $5 credit | platform.openai.com |
| Tavily | Web search | 1000 free/month | tavily.com |
| Serper | Google search for CrewAI | 2500 free/month | serper.dev |

---

### VS Code Extensions (Recommended)

- Python (Microsoft)
- Pylance
- REST Client (for testing without Postman)
- GitLens
- Python Docstring Generator
- JSON Viewer

---

### Debugging Process

```bash
# Check if FastAPI is running
curl http://localhost:8000/

# Check n8n connection
curl http://localhost:5678/

# View FastAPI logs in real-time
uvicorn app.main:app --reload --log-level debug

# Test research endpoint
curl -X POST http://localhost:8000/research/ \
  -H "Content-Type: application/json" \
  -d '{"query": "NVIDIA market analysis", "depth": "standard"}'
```

---

## 16. Important Engineering Concepts

### Asynchronous Execution

Python's `async`/`await` allows I/O-bound tasks (HTTP calls, file writes) to run concurrently without blocking:

```python
# BLOCKING (avoid for I/O):
result = requests.get(url)       # Blocks entire thread

# NON-BLOCKING (correct):
result = await httpx.get(url)    # Yields control while waiting
```

In FastAPI, every endpoint handler should be `async def` when making network calls.

---

### Workflow Orchestration

LangGraph manages **state transitions** between nodes. This solves the problem of:
- What happens when a node fails?
- How do you pass data between steps?
- How do you retry only the failed step?

The StateGraph is the answer — it's a deterministic state machine for AI workflows.

---

### Event-Driven Systems

n8n implements event-driven architecture: instead of polling for results, your system emits events (`report_complete`) and n8n **reacts** to them. This decouples the AI pipeline from downstream actions.

---

### State Management

LangGraph's TypedDict state ensures:
- Every node knows exactly what data is available
- Type errors are caught at development time
- State is serializable for checkpointing
- The graph execution is deterministic and debuggable

---

### Observability

Add structured logging to every node:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def planner_node(state):
    logger.info(f"[PLANNER] Starting for job {state['job_id']}")
    # ... processing ...
    logger.info(f"[PLANNER] Generated {len(sub_queries)} sub-queries")
```

---

## 17. Common Mistakes & Solutions

### Mistake 1: Overengineering on Day 1

**Problem**: Trying to implement RAG, CrewAI, LangGraph, and a frontend simultaneously.  
**Solution**: Follow the day-by-day plan strictly. Ship a working MVP each day.

---

### Mistake 2: Context Window Overflow

**Problem**: Passing all research results into a single LLM call, exceeding the context limit.  
**Solution**:
```python
# Limit context size
context = "\n".join([r["content"][:1000] for r in results[:6]])
# Max ~6000 tokens — well within GPT-4o's 128k limit
```

---

### Mistake 3: Agent Infinite Loops

**Problem**: CrewAI or LangGraph agent keeps retrying indefinitely.  
**Solution**:
```python
# LangGraph: add retry limit
if state["retry_count"] >= 3:
    return "reporter"  # Force exit

# CrewAI: set max iterations
Agent(max_iter=5)  # Never let an agent run more than 5 times
```

---

### Mistake 4: Workflow Failures With No Error Info

**Problem**: Background task fails silently, no error visible.  
**Solution**:
```python
async def run_pipeline(job_id: str, query: str):
    try:
        result = await research_graph.ainvoke(initial_state, config)
    except Exception as e:
        logger.error(f"Pipeline failed for job {job_id}: {e}")
        # Update job status to "failed" in DB
```

---

### Mistake 5: Blocking the Event Loop

**Problem**: Running synchronous code (like `crew.kickoff()`) inside an `async` function.  
**Solution**:
```python
import asyncio

loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, crew.kickoff)
# run_in_executor runs sync code in a thread pool
```

---

### Mistake 6: Prompt Issues

**Problem**: Inconsistent LLM responses, wrong format, hallucinations.  
**Solution**:
- Use `response_format={"type": "json_object"}` when expecting JSON
- Set `temperature=0.1–0.3` for factual tasks
- Always include explicit output format instructions in prompts
- Validate LLM output before passing to next node

---

### Mistake 7: n8n Webhook Not Receiving Data

**Problem**: FastAPI sends webhook but n8n shows no execution.  
**Solution**:
```bash
# Verify n8n is running
curl http://localhost:5678/

# Check webhook URL matches exactly
echo $N8N_WEBHOOK_URL

# Test webhook directly
curl -X POST http://localhost:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{"test": "ping"}'
```

---

## 18. MVP Strategy

### Minimum Viable System (What Must Work)

| Feature | Priority | Day |
|---------|---------|-----|
| POST endpoint accepts a query | Must | Day 1 |
| n8n receives webhook event | Must | Day 1 |
| Web search executes | Must | Day 2 |
| Markdown report generated and saved | Must | Day 2 |
| LangGraph graph runs end-to-end | Must | Day 3 |
| CrewAI crew produces report | Must | Day 4 |

---

### What to Postpone

| Feature | Reason to Postpone |
|---------|-------------------|
| Frontend UI | Adds complexity, not needed for core validation |
| User authentication | No multi-user scenario in local dev |
| PostgreSQL | SQLite is sufficient initially |
| RAG pipeline | Only needed when you have a document library |
| PDF generation | Markdown is sufficient for validation |
| Streaming responses | Complexity not needed in MVP |

---

### Scaling Strategy

```
MVP (Day 1):     Simple webhook trigger
↓
Core (Day 2):    Real research + reports
↓
Orchestrated (Day 3): LangGraph workflows
↓
Multi-Agent (Day 4):  CrewAI collaboration
↓
Phase 3:         RAG + vector memory
↓
Phase 4:         Frontend + auth + dashboard
↓
Phase 5:         Local LLMs + voice agents
```

---

## 19. Future Enhancements

### Frontend Dashboard
- React + Vite for the UI
- WebSocket connection for real-time job status
- Report viewer with Markdown rendering
- Job history and management

### Authentication
- FastAPI OAuth2 with JWT tokens
- API key management for different users
- Rate limiting per user

### Advanced Memory
- Qdrant for production-grade vector search
- Redis for fast in-memory caching
- PostgreSQL for persistent job history
- Report deduplication using semantic similarity

### Local LLMs
- Ollama for running models locally (no API costs)
- LLaMA 3 or Mistral for research tasks
- Specialized models for different agent roles

### Browser Automation
- Playwright integration for accessing paywalled content
- Screenshot capture for visual data extraction
- Form submission automation

### Voice Agents
- Whisper for speech-to-text query input
- ElevenLabs for report audio summaries
- Real-time voice research interface

### MCP (Model Context Protocol)
- Connect agents to external tools via MCP servers
- Database access, file systems, APIs via standardized protocol

---

## 20. Final Expected Architecture

### Complete System Architecture (Day 4)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL INTERFACES                           │
│                                                                       │
│     Postman / curl          n8n Dashboard        Future: React UI    │
└──────────────┬───────────────────┬───────────────────────────────────┘
               │                   │ (webhooks)
               ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FASTAPI LAYER                                 │
│                                                                       │
│  POST /research/          GET /research/{id}      GET /health        │
│  BackgroundTask runner    Status checker          Health check       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH STATE MACHINE                            │
│                                                                       │
│  ┌──────────┐   ┌────────────┐   ┌──────────┐   ┌──────────────┐  │
│  │ PLANNER  │──→│ RESEARCHER │──→│ ANALYZER │──→│   REPORTER   │  │
│  │   NODE   │   │    NODE    │   │   NODE   │   │    NODE      │  │
│  └──────────┘   └─────┬──────┘   └──────────┘   └──────┬───────┘  │
│                        │ retry logic                      │          │
│  ResearchState ◄────── ┘                                 │          │
│  TypedDict                                                │          │
└───────────────────────────────────────────────────────┬──┘──────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CREWAI MULTI-AGENT SYSTEM                        │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │   PLANNER   │→ │  RESEARCH   │→ │   WRITER    │→ │ REVIEWER  │ │
│  │    AGENT    │  │    AGENT    │  │    AGENT    │  │   AGENT   │ │
│  │             │  │  + Tools:   │  │             │  │           │ │
│  │             │  │  Serper     │  │             │  │           │ │
│  │             │  │  WebSearch  │  │             │  │           │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
└───────────────────────────────────────────────────────┬─────────────┘
                                                        │
                    ┌───────────────────────────────────┘
                    │
         ┌──────────▼───────────────────────────────────────────────┐
         │                    OUTPUT LAYER                            │
         │                                                            │
         │  /reports/report_{id}_{timestamp}.md                      │
         │                          │                                 │
         │                          ▼                                 │
         │                [n8n Webhook Triggered]                     │
         │                    │              │                        │
         │              Save to disk   Send notification              │
         └────────────────────────────────────────────────────────────┘
```

---

## 21. Final Project Outcome

### What the Final System Can Do

By the end of Day 4, you have a system that:

1. **Accepts** a natural language research query via REST API
2. **Plans** research automatically by breaking the query into sub-queries
3. **Searches** the web across multiple targeted queries
4. **Analyzes** findings and extracts structured insights
5. **Orchestrates** specialized AI agents for planning, research, writing, and review
6. **Generates** a professional, multi-section research report in Markdown
7. **Saves** the report to the local filesystem
8. **Notifies** external systems via n8n webhooks
9. **Retries** automatically when searches return insufficient results
10. **Logs** every step for observability and debugging

---

### Engineering Skills Demonstrated

| Skill Category | What You've Built |
|---------------|------------------|
| **API Design** | RESTful FastAPI with async endpoints, Pydantic validation, background tasks |
| **AI Orchestration** | LangGraph stateful workflow with conditional routing and checkpointing |
| **Multi-Agent Systems** | CrewAI role-based agents with task delegation and sequential process |
| **Workflow Automation** | n8n webhook integration with event-driven notifications |
| **Async Python** | Non-blocking I/O, background tasks, async service layers |
| **Clean Architecture** | Layered design: router → service → graph → agent |
| **State Management** | TypedDict state, memory persistence, workflow checkpoints |
| **Tool Integration** | Tavily search, OpenAI LLM, Serper, file system |

---

### Why This Project Is Portfolio-Worthy

This project demonstrates capabilities that are in **extremely high demand** in 2024–2025:

- **Agentic AI development** is the frontier of enterprise software
- **LangGraph** is the production standard for AI workflow orchestration
- **CrewAI** is leading multi-agent frameworks
- **RAG pipelines** are the foundation of enterprise AI knowledge systems
- **n8n** proves integration/automation engineering skills

Most engineers who claim "AI experience" have only built chatbots. This system demonstrates **systems-level thinking** — how to build autonomous, reliable, production-grade AI workflows.

---

### How This Resembles Enterprise AI Systems

| Your System | Enterprise Equivalent |
|------------|----------------------|
| FastAPI backend | Enterprise AI gateway |
| LangGraph orchestration | Workflow execution engine |
| CrewAI agents | AI workforce automation |
| n8n integration | Enterprise integration platform (Zapier/Workato) |
| Research pipeline | Market intelligence system |
| RAG (Phase 3) | Enterprise knowledge base |
| PostgreSQL (Phase 3) | Audit-grade data persistence |

---

*This documentation was generated as a complete implementation blueprint for the Autonomous AI Research & Report Generation System. Follow the day-wise plan strictly, test at every step, and scale complexity incrementally.*

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Scope**: Local Development · Portfolio-Grade · Learning & Implementation