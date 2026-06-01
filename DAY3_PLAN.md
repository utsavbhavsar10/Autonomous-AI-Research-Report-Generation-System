# Day 3 Plan: LangGraph Orchestration (Junior Developer Guide)

**Date**: 2026-06-01
**Phase**: Phase 3 — Stateful Workflow Orchestration
**Status**: Planning
**Audience**: Junior developers who have completed Day 1 + Day 2

---

## 1. What Are We Building Today? (Plain English)

On Day 2, our pipeline ran like a straight line:

```
search  →  process  →  generate report  →  save
```

If anything failed in the middle, the whole thing crashed. There was no memory of what happened, no retry, no way to skip steps, and no way to branch (e.g. "if results are weak, search again").

**Day 3 turns this straight line into a smart graph.**

We will use **LangGraph** to:
1. Break the pipeline into **nodes** (small functions that do one job).
2. Share data between nodes using a **state object** (a Python dict that travels through the graph).
3. Add **conditional edges** — "if X then go to node A, else go to node B".
4. Add **retry logic** — if search fails, try again up to N times.
5. Keep a **workflow memory** — every node knows what happened before it.
6. Send **progress updates to n8n** at each step (not just at the end).

> **Mental model**: Think of LangGraph as a flowchart you can actually run. Each box is a Python function, each arrow is a rule, and the clipboard everyone passes around is the "state".

---

## 2. Why LangGraph? (The "Why" Before The "How")

| Problem on Day 2 | How LangGraph Fixes It |
|---|---|
| Linear flow — can't branch | `add_conditional_edges()` lets one node decide where to go next |
| No retry on failure | A "retry" edge can loop back to the same node up to N times |
| State lives in local variables → lost on error | State lives in a typed `TypedDict` that LangGraph persists between nodes |
| Hard to add a new step | Add a node + one edge — no rewriting the orchestrator |
| Hard to inspect what happened | LangGraph gives you the full state trace per run |

**Bottom line**: LangGraph = state machine for LLM apps. Each node mutates state. Edges decide routing. That's it.

---

## 3. Core Concepts (Read This Once, Refer Back Often)

### 3.1 State
A typed dictionary that flows through the graph. Every node receives it, returns updates to it.

```python
from typing import TypedDict, List, Optional

class ResearchState(TypedDict):
    # Inputs
    job_id: str
    query: str
    depth: str                  # "standard" | "deep"

    # Planning
    planned_queries: List[str]

    # Search
    raw_results: List[dict]
    sources: List[dict]         # cleaned + deduped
    search_attempts: int        # how many times we retried search

    # Analysis
    sources_quality: str        # "good" | "weak"

    # Report
    report_markdown: Optional[str]
    report_path: Optional[str]

    # Bookkeeping
    error: Optional[str]
    current_step: str           # for progress messages to n8n
```

> **Junior tip**: `TypedDict` is just a dict with type hints. At runtime it's a plain dict. The types help your editor and your reviewer — they don't enforce anything.

### 3.2 Node
A function that takes the state and returns a partial update.

```python
async def search_node(state: ResearchState) -> dict:
    results = await search_service.search_multiple(state["planned_queries"])
    return {"raw_results": results, "current_step": "searched"}
```

LangGraph merges the returned dict into the state. You only return what you changed.

### 3.3 Edge
A connection from one node to another. Two flavors:

- **Static edge**: always go from A → B.
- **Conditional edge**: a function inspects state and returns the name of the next node.

```python
def route_after_analysis(state: ResearchState) -> str:
    if state["sources_quality"] == "weak" and state["search_attempts"] < 2:
        return "plan"           # loop back and try harder
    return "generate_report"    # move forward
```

### 3.4 Graph
The container. You add nodes, add edges, set an entry point, and compile.

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(ResearchState)
graph.add_node("plan", plan_node)
graph.add_node("search", search_node)
graph.add_node("analyze", analyze_node)
graph.add_node("generate_report", report_node)
graph.add_node("save", save_node)

graph.set_entry_point("plan")
graph.add_edge("plan", "search")
graph.add_edge("search", "analyze")
graph.add_conditional_edges("analyze", route_after_analysis, {
    "plan": "plan",
    "generate_report": "generate_report",
})
graph.add_edge("generate_report", "save")
graph.add_edge("save", END)

workflow = graph.compile()
```

That's the whole vocabulary. Everything below is applying these four ideas.

---

## 4. Day 3 Target Flow

```
                  ┌─────────────────┐
                  │  POST /research │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Create Job (DB) │
                  └────────┬────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │   LangGraph Workflow     │
              │                          │
              │  ┌────────────────────┐  │
              │  │  1. plan_node      │  │  → build search queries
              │  └─────────┬──────────┘  │
              │            ▼             │
              │  ┌────────────────────┐  │
              │  │  2. search_node    │  │  → hit Tavily (with retry)
              │  └─────────┬──────────┘  │
              │            ▼             │
              │  ┌────────────────────┐  │
              │  │  3. analyze_node   │  │  → judge source quality
              │  └─────────┬──────────┘  │
              │            ▼             │
              │       weak? ──── yes ──┐ │
              │            │           │ │
              │            no          │ │
              │            ▼           │ │
              │  ┌────────────────────┐│ │
              │  │ 4. report_node     ││ │
              │  └─────────┬──────────┘│ │
              │            ▼           │ │
              │  ┌────────────────────┐│ │
              │  │ 5. save_node       ││ │
              │  └─────────┬──────────┘│ │
              │            ▼           │ │
              │           END  ◄───────┘ │  (loop limit reached)
              └──────────────┬───────────┘
                             │
                             ▼
                  ┌─────────────────┐
                  │  n8n Webhook    │
                  └─────────────────┘
```

Each node also calls `update_job()` so the `/research/{job_id}` endpoint shows live progress.

---

## 5. Success Criteria (Definition of Done)

- [ ] `app/graph/` package exists with `state.py`, `nodes.py`, `workflow.py`
- [ ] All 5 nodes implemented and unit-callable
- [ ] Conditional edge re-searches when quality is "weak" (max 2 attempts)
- [ ] Retry-on-error works for `search_node` (max 3 attempts, exponential backoff)
- [ ] State is persisted to DB at every node transition (so `/status` is live)
- [ ] `ResearchService.run()` from Day 2 is replaced by `workflow.ainvoke(initial_state)`
- [ ] Manual tests: standard query, deep query, forced failure all pass
- [ ] No regressions in existing API endpoints

---

## 6. Task Breakdown (Do These In Order)

### Task 0 — Install dependencies (5 min)

Add to `requirements.txt`:
```
langgraph
langchain-core
```

Then:
```bash
pip install -r requirements.txt
```

> **Note**: We already have `langchain` and `langchain-openai`. `langgraph` is a separate package that builds on `langchain-core`.

---

### Task 1 — Create the `graph/` package (10 min)

```
app/
└── graph/
    ├── __init__.py
    ├── state.py          # ResearchState TypedDict
    ├── nodes.py          # all node functions
    ├── routing.py        # conditional edge functions
    └── workflow.py       # build + compile the graph
```

**Why a separate package?** Keeps orchestration logic isolated from services. Services do work; the graph decides when to do which work.

---

### Task 2 — Define `state.py` (15 min)

Copy the `ResearchState` `TypedDict` from §3.1. Add `Annotated` reducers later only if you need list-accumulation (you don't yet — we overwrite, not append).

**Checklist**:
- [ ] All fields from Day 2 pipeline are covered
- [ ] `Optional[...]` is used for fields that may not exist yet
- [ ] `current_step` is a string we'll write progress messages into

---

### Task 3 — Implement nodes in `nodes.py` (60 min)

Each node is **async**, takes state, returns a partial dict. Each node also calls `update_job()` so the DB shows live progress.

**Skeleton**:
```python
# app/graph/nodes.py
from app.graph.state import ResearchState
from app.services.search_service import SearchService
from app.services.report_service import ReportService
from app.services.job_service import update_job
from app.utils.content_processor import ContentProcessor
from app.utils.logger import get_logger

logger = get_logger(__name__)
search = SearchService()
report = ReportService()
processor = ContentProcessor()


async def plan_node(state: ResearchState) -> dict:
    queries = [state["query"]]
    if state["depth"] in ("standard", "deep"):
        queries += [
            f"{state['query']} latest trends",
            f"{state['query']} recent analysis",
            f"{state['query']} key insights",
        ]
    if state["depth"] == "deep":
        queries += [
            f"{state['query']} detailed comparison",
            f"{state['query']} expert opinions",
            f"{state['query']} future outlook",
        ]

    await update_job(state["job_id"], status="searching",
                     progress=f"Planning {len(queries)} queries")
    return {"planned_queries": queries, "current_step": "planned"}


async def search_node(state: ResearchState) -> dict:
    attempts = state.get("search_attempts", 0) + 1
    try:
        raw = await search.search_multiple(state["planned_queries"])
        flat = [item for group in raw for item in group["results"]]
        flat = processor.filter_valid_results(flat)
        flat = processor.deduplicate_results(flat)
        return {
            "raw_results": raw,
            "sources": flat,
            "search_attempts": attempts,
            "current_step": "searched",
        }
    except Exception as e:
        logger.error(f"search_node failed (attempt {attempts}): {e}")
        return {"error": str(e), "search_attempts": attempts}


async def analyze_node(state: ResearchState) -> dict:
    n = len(state.get("sources", []))
    quality = "good" if n >= 5 else "weak"
    await update_job(state["job_id"], status="analyzing",
                     progress=f"Analyzed {n} sources → {quality}")
    return {"sources_quality": quality, "current_step": "analyzed"}


async def report_node(state: ResearchState) -> dict:
    await update_job(state["job_id"], status="generating",
                     progress=f"Generating report from {len(state['sources'])} sources")
    md = await report.generate_report(state["query"], state["sources"])
    return {"report_markdown": md, "current_step": "report_generated"}


async def save_node(state: ResearchState) -> dict:
    path = await report.save_report(state["job_id"], state["report_markdown"])
    await update_job(state["job_id"], status="complete",
                     progress="Report saved", report_path=path)
    return {"report_path": path, "current_step": "saved"}
```

**Checklist**:
- [ ] Each node logs entry + exit
- [ ] Each node calls `update_job` so `/status` works
- [ ] No node raises — errors go into `state["error"]` and routing decides what to do

---

### Task 4 — Routing functions in `routing.py` (20 min)

```python
# app/graph/routing.py
from app.graph.state import ResearchState

MAX_SEARCH_RETRIES = 3
MAX_QUALITY_LOOPS = 2


def route_after_search(state: ResearchState) -> str:
    """If search errored and we have retries left, try again. Else analyze."""
    if state.get("error") and state["search_attempts"] < MAX_SEARCH_RETRIES:
        return "search"
    if state.get("error"):
        return "fail"
    return "analyze"


def route_after_analysis(state: ResearchState) -> str:
    """If sources are weak and we haven't looped too many times, re-plan."""
    if state["sources_quality"] == "weak" and state["search_attempts"] < MAX_QUALITY_LOOPS:
        return "plan"
    return "generate_report"
```

> **Junior tip**: Conditional edges return **string names of nodes**, not the node functions themselves. The mapping from string → node is configured when you wire the graph (Task 5).

---

### Task 5 — Build the graph in `workflow.py` (30 min)

```python
# app/graph/workflow.py
from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.graph.nodes import (
    plan_node, search_node, analyze_node, report_node, save_node,
)
from app.graph.routing import route_after_search, route_after_analysis


async def fail_node(state):
    from app.services.job_service import update_job
    await update_job(state["job_id"], status="failed",
                     progress=f"Pipeline failed: {state.get('error')}")
    return {"current_step": "failed"}


def build_workflow():
    g = StateGraph(ResearchState)

    g.add_node("plan", plan_node)
    g.add_node("search", search_node)
    g.add_node("analyze", analyze_node)
    g.add_node("generate_report", report_node)
    g.add_node("save", save_node)
    g.add_node("fail", fail_node)

    g.set_entry_point("plan")
    g.add_edge("plan", "search")

    g.add_conditional_edges("search", route_after_search, {
        "search": "search",
        "analyze": "analyze",
        "fail": "fail",
    })

    g.add_conditional_edges("analyze", route_after_analysis, {
        "plan": "plan",
        "generate_report": "generate_report",
    })

    g.add_edge("generate_report", "save")
    g.add_edge("save", END)
    g.add_edge("fail", END)

    return g.compile()


workflow = build_workflow()
```

---

### Task 6 — Wire it into `ResearchService` (20 min)

Replace the body of `ResearchService.run()` with a single call to the workflow:

```python
# app/services/research_service.py
from app.graph.workflow import workflow

class ResearchService:
    async def run(self, job_id: str, query: str, depth: str = "standard") -> dict:
        initial_state = {
            "job_id": job_id,
            "query": query,
            "depth": depth,
            "search_attempts": 0,
            "current_step": "init",
        }
        final_state = await workflow.ainvoke(initial_state)
        return {
            "job_id": job_id,
            "status": "failed" if final_state.get("error") else "complete",
            "file_path": final_state.get("report_path"),
            "sources": len(final_state.get("sources", [])),
        }
```

The router doesn't change at all. From the outside, the API is identical — but inside, it's now a state machine.

---

### Task 7 — Update n8n notification (15 min)

`NotificationService` already fires on completion. Day 3 just adds richer payload fields from the final state:

- `final_state["current_step"]`
- `final_state["search_attempts"]` (so n8n can show "succeeded after 2 retries")
- `final_state["sources_quality"]`

No new endpoints — just include these in the existing webhook body.

---

### Task 8 — Manual Testing (30 min)

| Test | Query | Expected |
|---|---|---|
| **T1 happy path standard** | "What is FastAPI?" | plan → search → analyze (good) → report → save |
| **T2 happy path deep** | "Compare LangChain vs LlamaIndex" | same as T1 with 7 planned queries |
| **T3 quality loop** | obscure made-up term, e.g. "zzqxblat 2026 forecast" | analyze returns weak → loops back to plan once → completes |
| **T4 search retry** | temporarily set `TAVILY_API_KEY=bad` → restore mid-run | search retries 3× then routes to `fail` node |
| **T5 status polling** | any query | `/research/{id}` shows distinct progress messages: Planning → Searched → Analyzed → Generating → Complete |

**Checklist after each test**:
- [ ] Report file exists on disk
- [ ] `/research/{id}` returns the right final status
- [ ] n8n webhook was called once
- [ ] Logs show node-by-node entry

---

## 7. File Map (What Will Exist At End Of Day 3)

```
app/
├── graph/                       ← NEW
│   ├── __init__.py
│   ├── state.py                 ← ResearchState
│   ├── nodes.py                 ← 5 nodes + fail_node
│   ├── routing.py               ← 2 conditional edge funcs
│   └── workflow.py              ← build_workflow() + compiled `workflow`
├── services/
│   ├── research_service.py      ← MODIFIED: delegates to workflow
│   ├── search_service.py        ← unchanged
│   ├── report_service.py        ← unchanged
│   ├── job_service.py           ← unchanged
│   └── notification_service.py  ← MODIFIED: richer payload
├── utils/
│   └── content_processor.py     ← unchanged
└── routers/
    └── research.py              ← unchanged
```

---

## 8. Common Pitfalls (Read Before You Code)

1. **Forgetting to return a dict from a node**
   Nodes must return `dict` (or `None`). Returning a string or a list silently breaks the merge.

2. **Mutating state in-place**
   Don't do `state["sources"].append(...)`. Return `{"sources": new_list}` instead. LangGraph expects immutable-style updates.

3. **Conditional edge returns a node function**
   Return the **string name** (`"analyze"`), not the function reference.

4. **Infinite loops**
   Always have a counter (`search_attempts`) and a max. A graph that loops forever will look like a hang.

5. **Mixing sync and async nodes**
   Pick one style. We're using `async` everywhere because services are async.

6. **`update_job` called inside the node returns**
   Call `update_job` BEFORE you `return`. It's a side effect, not state.

---

## 9. Glossary (Quick Reference)

| Term | One-liner |
|---|---|
| **State** | Typed dict that flows through the graph. |
| **Node** | Async function: state → partial state update. |
| **Edge** | Rule for which node runs next. |
| **Conditional edge** | An edge whose target is chosen by a function. |
| **Entry point** | The first node when the graph starts. |
| **END** | Sentinel meaning "stop the graph". |
| **`compile()`** | Turns the graph definition into a runnable object. |
| **`ainvoke(state)`** | Runs the graph once with the given initial state. |

---

## 10. Implementation Order Recap

1. Install `langgraph` (5 min)
2. Create `app/graph/` package (10 min)
3. Write `state.py` (15 min)
4. Write `nodes.py` (60 min)
5. Write `routing.py` (20 min)
6. Write `workflow.py` (30 min)
7. Swap `ResearchService.run()` to call workflow (20 min)
8. Update notification payload (15 min)
9. Run all 5 manual tests (30 min)

**Total estimated time**: ~3.5 hours.

---

## 11. Next Steps (Day 4 Preview)

Day 4 turns the single-node `report_node` into a **CrewAI crew** of cooperating agents:
- Planner agent (refines queries)
- Research agent (executes searches)
- Writer agent (drafts the report)
- Reviewer agent (critiques and asks for revisions)

The LangGraph workflow we build today is what hosts those agents tomorrow. Build it clean.

---

**End of Day 3 Plan**
