# Autonomous AI Research & Report Generation System

An AI pipeline that takes a research query, plans searches, pulls web sources, runs them through a 4-agent CrewAI crew, and outputs a cited Markdown report (+ optional PDF). Orchestrated with LangGraph, served over FastAPI, traced with LangSmith.

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| API | **FastAPI** + Uvicorn | Async REST API, background task execution |
| Orchestration | **LangGraph** | `StateGraph` with conditional routing / retry loops (`app/graph`) |
| Multi-agent report writing | **CrewAI** | 4 sequential agents (`app/crew`) |
| LLM (CrewAI agents) | **Groq** — `openai/gpt-oss-120b` via `crewai.LLM` | Used by all 4 CrewAI agents |
| LLM (fallback report path) | **OpenAI** — `gpt-4o-mini` | Used only when `USE_CREW=false` |
| Web search | **Tavily** | `tavily-python` client |
| Job persistence | **SQLite** (`aiosqlite`) | `research.db`, single `jobs` table |
| Event log | Flat JSON lines | `jobs_log.json`, append-only |
| Markdown → PDF | **Playwright (Chromium)** + `markdown` lib | `app/services/pdf_service.py` |
| Tracing | **LangSmith** (+ OpenInference/OpenTelemetry) | Auto for LangGraph, opt-in instrumentation for CrewAI |
| UI | **Streamlit** | `streamlit_app.py`, talks to the FastAPI backend over HTTP |
| Content cleanup | BeautifulSoup4 | Strips HTML/whitespace from search results |


---

## Folder Structure

```
AI-Assist-ResearchGeneration/
├── app/
│   ├── main.py                     # FastAPI app, lifespan, CORS, router mounting
│   ├── crew/                       # CrewAI multi-agent system
│   │   ├── agents.py                #   4 Agent definitions + shared Groq LLM factory
│   │   ├── tasks.py                 #   4 Task definitions (sequential handoff)
│   │   └── crew.py                  #   Crew assembly + async kickoff wrapper
│   ├── graph/                      # LangGraph orchestration
│   │   ├── state.py                  #   ResearchState TypedDict (+ reducers)
│   │   ├── nodes.py                  #   plan / search / analyze / report / save nodes
│   │   ├── routing.py                #   conditional edge functions (retry/quality loops)
│   │   └── workflow.py               #   StateGraph wiring, compiled singleton `workflow`
│   ├── routers/
│   │   ├── research.py               # POST /research, GET /research/{id}, GET /research
│   │   └── reports.py                # GET /reports, download .md, download .pdf (on demand)
│   ├── schemas/                    # Pydantic request/response models
│   ├── services/
│   │   ├── search_service.py         # Tavily search wrapper
│   │   ├── report_service.py         # Report generation entrypoint (routes to CrewAI or OpenAI)
│   │   ├── research_service.py       # Thin wrapper that invokes the compiled LangGraph workflow
│   │   ├── job_service.py            # SQLite job CRUD
│   │   ├── notification_service.py   # Rich console panels + jobs_log.json events
│   │   └── pdf_service.py            # Markdown → HTML → PDF via Playwright
│   └── utils/
│       ├── logger.py                  # Rich-based logger factory
│       ├── content_processor.py       # HTML cleanup, dedup, validation of search results
│       └── tracing.py                 # LangSmith / OpenInference setup
├── streamlit_app.py                # Standalone dashboard UI (separate process)
├── draw_graph.py                   # One-off script: renders workflow.png from the LangGraph graph
├── reports/                        # Generated .md / .pdf reports land here
├── jobs_log.json                   # Append-only event log
├── research.db                     # SQLite job tracking
├── pyproject.toml / requirements.txt / uv.lock
└── .env.example
```

---

## How to Run

### 1. Prerequisites
- Python **3.13+** (`.python-version` pins 3.13)
- API keys: OpenAI, Tavily, Groq (LangSmith optional)

### 2. Install dependencies

Using `uv` (this repo has a `uv.lock`):
```bash
uv sync
```
or with pip:
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Install Playwright's browser binary (required for PDF export)
```bash
playwright install chromium
```

### 4. Configure environment

Copy `.env.example` → `.env` and fill in:
```env
OPENAI_API_KEY=...
TAVILY_SEARCH_API_KEY=...

# Not in .env.example but REQUIRED — CrewAI agents run on Groq
GROQ_API=your_groq_api_key_here

# Optional — tracing
LANGSMITH_API_KEY=...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=ai-assist-research
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Optional — bypass CrewAI and use a single OpenAI call instead
USE_CREW=true
```
> `.env.example` is missing `GROQ_API` — add it yourself, `app/crew/agents.py` raises `ValueError` on startup of a research job without it.

### 5. Start the API
```bash
uvicorn app.main:app --reload --port 8000
```
Docs at `http://localhost:8000/docs`.

### 6. (Optional) Start the Streamlit dashboard
In a second terminal, with the API already running:
```bash
streamlit run streamlit_app.py
```

### 7. Try it
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "AI semiconductor market analysis for NVIDIA and AMD", "depth": "standard"}'

curl http://localhost:8000/research/<job_id>
curl http://localhost:8000/reports
curl -OJ http://localhost:8000/reports/<filename>.md
curl -OJ http://localhost:8000/reports/<filename>.md/pdf   # generated on first request, then cached
```

---

## PDF Service — Windows Issue & Fix

Generating PDFs uses **Playwright's Chromium**, which needs to spawn a subprocess. On Windows, asyncio's default **`SelectorEventLoop`** cannot spawn subprocesses (`NotImplementedError: Proactor is required`). Uvicorn on Windows also defaults to the selector loop, and even after switching the global policy, Uvicorn's reload/watcher machinery can still hand Playwright a selector-based loop.

Two fixes are layered in this codebase (`app/main.py` + `app/services/pdf_service.py`):

1. **Global policy switch** — `app/main.py`, top of file, before any other imports:
   ```python
   if sys.platform == "win32":
       asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
   ```
   This makes the *default* loop Proactor-based, which is enough for a plain `python app/main.py` run.

2. **Thread-isolated Proactor loop for the PDF call itself** — because Uvicorn (`--reload` especially) can still override the loop policy after startup, `pdf_service.py` doesn't trust the ambient loop at all. It runs the PDF generation in its own thread with a fresh `ProactorEventLoop`:
   ```python
   def _sync_generate_pdf(markdown_text, output_path, title):
       if sys.platform == "win32":
           loop = asyncio.ProactorEventLoop()
       else:
           loop = asyncio.new_event_loop()
       asyncio.set_event_loop(loop)
       try:
           return loop.run_until_complete(generate_pdf(markdown_text, output_path, title=title))
       finally:
           loop.close()

   async def md_path_to_pdf_path(md_path, title="Research Report"):
       ...
       return await asyncio.to_thread(_sync_generate_pdf, markdown_text, pdf_path, title)
   ```
   `asyncio.to_thread` hands this off to a worker thread, which gets its own event loop entirely independent of Uvicorn's — sidestepping the "which loop is currently active" problem altogether.

**Practical notes if you hit this again:**
- Always run `playwright install chromium` after a fresh `pip install`/`uv sync` — Playwright ships the driver but not the browser binary.
- If PDFs still fail with a `NotImplementedError`, it's almost always this event-loop mismatch, not Playwright itself — check that `--reload` isn't resetting the loop policy before your fix runs.
- PDF generation is on-demand and cached: `GET /reports/{filename}/pdf` only calls Playwright if the `.pdf` sibling doesn't already exist next to the `.md`.

---

## CrewAI Implementation

### Where it fits in the pipeline
CrewAI is **not** the top-level orchestrator — LangGraph is. The LangGraph `report` node (`app/graph/nodes.py::report_nodes`) calls `ReportService.generate_report()`, which — when `USE_CREW=true` (default) — delegates to `run_crew()` in `app/crew/crew.py`. If `USE_CREW=false`, it falls back to a single `gpt-4o-mini` completion instead (no multi-agent step).

### The 4 agents (`app/crew/agents.py`)
All four share one `LLM` factory (`_llm()`): Groq-hosted `openai/gpt-oss-120b`, `temperature=0.3`. Each `Agent` has `allow_delegation=False` — they run strictly in sequence, no agent hands work back.

| Agent | Role | Job |
|---|---|---|
| `researcher_agent` | Senior Research Analyst | Extracts 15–25 verifiable, `[n]`-cited facts from raw search results |
| `analyst_agent` | Strategy Analyst | Groups facts into 3–5 themes, flags contradictions/gaps |
| `writer_agent` | Technical Writer | Drafts the full report (Exec Summary, Key Findings, Analysis, Conclusions, Sources) |
| `reviewer_agent` | Editor-in-Chief | Reviews the draft, fixes citation/structure issues, returns the **final** markdown only |

### The 4 tasks (`app/crew/tasks.py`)
Each `Task` is bound to one agent and consumes the previous task's output implicitly (CrewAI's sequential process passes prior task outputs into context automatically). Only the first task's `description` is templated with runtime inputs:
- `{query}` and `{sources}` are injected via `crew.kickoff(inputs={...})` — CrewAI does the string `.format()`-style substitution on task descriptions at kickoff time.
- Every task enforces a `[n]` citation discipline in its `description`/`expected_output` so citations survive from raw facts → themes → draft → final report.

### Crew assembly & execution (`app/crew/crew.py`)
```python
Crew(
    agents=[researcher, analyst, writer, reviewer],
    tasks=[research_task(researcher), analysis_task(analyst),
           writing_task(writer), review_task(reviewer)],
    process=Process.sequential,
    verbose=True,
)
```
- `process=Process.sequential` — tasks run in list order, each with the prior task's output in context. (The alternative, `Process.hierarchical`, would need a manager LLM and isn't used here.)
- `crew.kickoff()` is **synchronous** and CPU/network-bound, so it's never awaited directly — it's run via `asyncio.to_thread(crew.kickoff, inputs=...)` so it doesn't block the FastAPI event loop.
- Inputs passed at kickoff: `{"query": <research query>, "sources": <formatted source list>}`. `_format_sources()` renders up to the first 25 sources as `[i] title - url\n    snippet` blocks for the researcher task's `{sources}` placeholder.
- Return value: `result.raw` (CrewAI's `CrewOutput.raw` attribute) — the reviewer's final markdown string, saved straight to `reports/*.md` by `ReportService.save_report()`.

### Key parameters to know
- `LLM(model="openai/gpt-oss-120b", temperature=0.3, api_key=GROQ_API)` — same model/temperature for all 4 agents, no per-agent tuning.
- `allow_delegation=False` on every agent — enforces the sequential contract; no agent can delegate sub-tasks back into the crew.
- `verbose=True` on both agents and the `Crew` — dumps each agent's reasoning/tool calls to stdout, which is what LangSmith/OpenInference tracing (below) also captures as structured spans.
- No `tools=[...]` are attached to any agent — this crew is pure LLM reasoning over the search results already gathered by the LangGraph `search` node; it does not call Tavily or any tool itself.

---

## Traceability (Tracing)

Tracing is wired in `app/utils/tracing.py`, called once from `app/main.py`'s module-level `init_langsmith()` at startup.

### How it works
1. **LangGraph/LangChain nodes are traced automatically.** LangChain picks up tracing purely from environment variables — no code instrumentation needed. `init_langsmith()` just normalizes config:
   - Reads `LANGSMITH_API_KEY` / `LANGSMITH_TRACING` / `LANGSMITH_PROJECT` / `LANGSMITH_ENDPOINT` from `.env`.
   - Mirrors them into the older `LANGCHAIN_*` variable names some LangChain internals still check (`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, `LANGCHAIN_ENDPOINT`).
   - If `LANGSMITH_API_KEY` is unset, tracing is disabled entirely and the function returns early — no crash, just no traces.

2. **CrewAI + OpenAI calls are traced via OpenTelemetry, opportunistically.** `_instrument_crewai()`:
   - Tries to import `openinference.instrumentation.crewai.CrewAIInstrumentor`, `openinference.instrumentation.openai.OpenAIInstrumentor`, and the OTLP HTTP span exporter. If any of those packages aren't installed, it logs and skips silently — CrewAI still runs, it's just untraced.
   - Builds an OpenTelemetry `TracerProvider` tagged with `service.name`/`langsmith.project`, pointed at `{LANGSMITH_ENDPOINT}/otel/v1/traces` via `OTLPSpanExporter`, authenticated with `x-api-key` + `Langsmith-Project` headers.
   - Calls `CrewAIInstrumentor().instrument(...)` and `OpenAIInstrumentor().instrument(...)` against that provider — this monkey-patches CrewAI's and the OpenAI SDK's internals so every agent step and LLM call emits a span automatically, no manual `with tracer.start_span(...)` calls anywhere in `app/crew/`.

### End result
With `LANGSMITH_API_KEY` set and the OTLP exporter packages installed (they're in `pyproject.toml`: `openinference-instrumentation-crewai`, `openinference-instrumentation-openai`), a single research job produces one connected trace in the LangSmith project (`LANGSMITH_PROJECT`, default `ai-assist-research`) spanning:
```
LangGraph run
 ├─ plan (LLM-free, but state transitions traced)
 ├─ search (Tavily calls)
 ├─ analyze
 ├─ generate_report
 │   └─ CrewAI crew.kickoff (OTel spans)
 │       ├─ researcher_agent → LLM call (Groq)
 │       ├─ analyst_agent    → LLM call (Groq)
 │       ├─ writer_agent     → LLM call (Groq)
 │       └─ reviewer_agent   → LLM call (Groq)
 └─ save_report
```
Note the two LLM providers show up separately: the LangGraph nodes' own OpenAI calls (`gpt-4o-mini` fallback, or none if `USE_CREW=true`) trace via LangChain's native tracing, while the CrewAI agents' Groq calls trace via the OpenInference/OTel path — both land in the same LangSmith project because they share the same endpoint/API key/project name.

If you don't need tracing, just leave `LANGSMITH_API_KEY` unset — the app runs identically, only without traces.
