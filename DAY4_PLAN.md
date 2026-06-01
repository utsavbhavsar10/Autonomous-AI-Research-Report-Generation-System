# Day 4 Plan: CrewAI Multi-Agent Report Generation (Junior Developer Guide)

**Date**: 2026-06-02
**Phase**: Phase 4 — Multi-Agent System
**Status**: Planning
**Audience**: Junior developers who have completed Day 3 (LangGraph)

---

## 1. What Are We Building Today? (Plain English)

On Day 3, our `report_node` was a single LLM call:

```
sources  →  one big OpenAI call  →  markdown report
```

That works, but every section of the report — summary, analysis, citations, polish — has to come from **one** prompt. The model has to be a researcher, a writer, and a reviewer all at once. It does an OK job at all three and a great job at none.

**Day 4 replaces that single call with a team of specialized agents.**

We will use **CrewAI** to spin up four roles that hand work off to each other:

1. **Researcher Agent** — reads the raw sources, picks the most relevant facts.
2. **Analyst Agent** — turns those facts into themes, comparisons, and insights.
3. **Writer Agent** — drafts the markdown report from the analysis.
4. **Reviewer Agent** — critiques the draft, demands fixes, signs off when ready.

Each agent has its own role description, its own goal, and its own LLM call. They run **in sequence** (Researcher → Analyst → Writer → Reviewer), passing their output to the next agent like a relay race.

> **Mental model**: Day 3 turned the pipeline into a flowchart. Day 4 turns the **report-generation step** of that flowchart into a small team where each member is good at exactly one thing.

The rest of the LangGraph workflow (plan / search / analyze / save) stays exactly the same. Only `report_node` changes inside.

---

## 2. Why CrewAI? (The "Why" Before The "How")

| Problem with Day 3's single LLM call | How CrewAI Fixes It |
|---|---|
| One prompt has to do everything → mediocre output | Each agent has one job → better focus, better output |
| Hard to inspect what went wrong in the report | Each agent's output is visible separately — you can see where the chain broke |
| No self-correction — bad output goes straight to disk | Reviewer agent can reject and ask for a rewrite before save |
| Adding a new step means rewriting the prompt | Add a new agent + task, no prompt surgery |
| Hard to swap models per role | Each agent can use a different model (cheap for research, strong for writing) |

**Bottom line**: CrewAI = role-based agents + tasks + a process that runs them. Day 3 orchestrates the **pipeline**; Day 4 orchestrates the **agents inside one step** of that pipeline.

---

## 3. Core Concepts (Read This Once, Refer Back Often)

CrewAI has four primitives. Learn these and you can read any CrewAI code.

### 3.1 Agent
A persona with a role, a goal, and a backstory. The role/goal/backstory become the system prompt for that agent's LLM calls.

```python
from crewai import Agent

researcher = Agent(
    role="Senior Research Analyst",
    goal="Extract the most relevant facts and data points from the provided sources.",
    backstory=(
        "You are a meticulous analyst with 10 years of experience. "
        "You ignore marketing fluff and surface only verifiable claims with citations."
    ),
    llm=llm,            # any LangChain-compatible LLM
    verbose=True,
    allow_delegation=False,
)
```

> **Junior tip**: `role` / `goal` / `backstory` are just strings. The model never "becomes" the persona — it's roleplay that biases output style and focus. Write them like a job description.

### 3.2 Task
A single unit of work assigned to one agent. Has a description, an expected output, and the agent that owns it.

```python
from crewai import Task

research_task = Task(
    description=(
        "Read these sources about '{query}' and produce a bullet list of the "
        "20 most relevant facts. Cite each one as [n] matching the source index.\n\n"
        "Sources:\n{sources}"
    ),
    expected_output="A markdown bullet list of facts, each with a [n] citation.",
    agent=researcher,
)
```

The `{query}` / `{sources}` placeholders get filled when the crew runs.

### 3.3 Crew
The container that owns agents + tasks + the order to run them in.

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, analyst, writer, reviewer],
    tasks=[research_task, analysis_task, writing_task, review_task],
    process=Process.sequential,    # run tasks one after another
    verbose=True,
)
```

### 3.4 Process
How tasks flow through the crew. Two flavors:

- `Process.sequential` — task N's output is automatically fed into task N+1's context. **Use this for Day 4.**
- `Process.hierarchical` — a manager agent picks which agent runs next. More flexible, more complex. Skip for now.

That's the whole vocabulary. Everything below applies these four ideas.

---

## 4. Target Architecture

### Day 3 (current)

```
LangGraph workflow
  plan → search → analyze → generate_report → save
                            └──────────────┘
                            single LLM call
                            (one OpenAI call)
```

### Day 4 (target)

```
LangGraph workflow
  plan → search → analyze → generate_report → save
                            └──────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │      CrewAI Crew            │
                    │                             │
                    │  ┌──────────────────────┐   │
                    │  │ 1. Researcher Agent  │   │  pull facts + citations
                    │  └──────────┬───────────┘   │
                    │             ▼               │
                    │  ┌──────────────────────┐   │
                    │  │ 2. Analyst Agent     │   │  group into themes
                    │  └──────────┬───────────┘   │
                    │             ▼               │
                    │  ┌──────────────────────┐   │
                    │  │ 3. Writer Agent      │   │  draft full markdown
                    │  └──────────┬───────────┘   │
                    │             ▼               │
                    │  ┌──────────────────────┐   │
                    │  │ 4. Reviewer Agent    │   │  critique + final polish
                    │  └──────────┬───────────┘   │
                    │             ▼               │
                    │     final markdown          │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                            back to LangGraph
```

**Key insight**: the crew is **called from inside** `report_node`. LangGraph doesn't know CrewAI exists — it just calls a function that happens to use four agents internally.

---

## 5. Success Criteria (Definition of Done)

- [ ] `app/crew/` package exists with `agents.py`, `tasks.py`, `crew.py`
- [ ] All 4 agents implemented (researcher, analyst, writer, reviewer)
- [ ] All 4 tasks implemented and wired in sequential order
- [ ] `ReportService.generate_report()` (or a new method) delegates to the crew
- [ ] The crew runs end-to-end on a sample query and returns valid markdown
- [ ] Each agent's output is visible in logs (verbose=True)
- [ ] Reviewer can request one revision cycle before final output
- [ ] No regressions in the LangGraph workflow (plan/search/analyze/save unchanged)
- [ ] Manual tests: standard query, deep query, low-source-count query all pass
- [ ] Report quality is **demonstrably** better than Day 3 (longer, better-cited, more structured)

---

## 6. Task Breakdown (Do These In Order)

### Task 0 — Install dependencies (5 min)

Add to `requirements.txt`:
```
crewai
crewai-tools
```

Then:
```bash
pip install -r requirements.txt
```

> **Note**: `crewai` brings in its own LangChain dependencies; conflicts with the versions we pinned for Day 3 are possible. If `pip` complains, install `crewai` first in a fresh venv, then re-add the Day 3 packages.

---

### Task 1 — Create the `crew/` package (10 min)

```
app/
└── crew/
    ├── __init__.py
    ├── agents.py         # 4 agent definitions
    ├── tasks.py          # 4 task definitions
    └── crew.py           # build + run the crew
```

**Why a separate package?** Same reason we built `app/graph/` separately on Day 3 — orchestration code lives away from service code. The graph orchestrates the pipeline; the crew orchestrates the report-writing step.

---

### Task 2 — Define agents in `agents.py` (45 min)

One file with four agent factory functions. Each takes an LLM and returns an `Agent`.

```python
# app/crew/agents.py
from crewai import Agent
from langchain_openai import ChatOpenAI
import os


def _llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def researcher_agent() -> Agent:
    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Surface the most relevant, verifiable facts from a list of web "
            "search results. Skip marketing fluff and opinions."
        ),
        backstory=(
            "You spent a decade at a Big Four consultancy reading 200 sources "
            "to write a single 5-page briefing. You are allergic to vague claims."
        ),
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )


def analyst_agent() -> Agent:
    return Agent(
        role="Strategy Analyst",
        goal=(
            "Group raw facts into 3-5 themes. Identify patterns, contradictions, "
            "and gaps. Output structured bullets the writer can lift directly."
        ),
        backstory=(
            "You translate raw research into executive-ready themes. "
            "You always cite the underlying facts by their [n] references."
        ),
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )


def writer_agent() -> Agent:
    return Agent(
        role="Technical Writer",
        goal=(
            "Turn analyzed themes into a polished markdown research report "
            "with Executive Summary, Key Findings, Detailed Analysis, "
            "Conclusions, and Sources sections."
        ),
        backstory=(
            "You write for senior engineers and product leaders. "
            "Clear, neutral, well-cited prose. No filler, no apologies."
        ),
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )


def reviewer_agent() -> Agent:
    return Agent(
        role="Editor-in-Chief",
        goal=(
            "Read the draft, flag missing citations, vague claims, or weak "
            "structure, and return a polished final version."
        ),
        backstory=(
            "You reject anything that wouldn't pass a McKinsey QC review. "
            "If the draft is good, you make small edits. If it's bad, you rewrite it."
        ),
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )
```

**Checklist**:
- [ ] All four agents instantiated
- [ ] Each has a distinct role + goal
- [ ] `allow_delegation=False` (we want strict sequential, not agent-to-agent chatter)
- [ ] `verbose=True` so you can see what each agent says

---

### Task 3 — Define tasks in `tasks.py` (45 min)

```python
# app/crew/tasks.py
from crewai import Task
from crewai.agent import Agent


def research_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Topic: {query}\n\n"
            "Sources (each with index, title, url, snippet):\n{sources}\n\n"
            "Produce a markdown bullet list of the 15-25 most relevant facts. "
            "Each bullet MUST end with a [n] citation referencing the source index."
        ),
        expected_output=(
            "A markdown bullet list. Example:\n"
            "- FastAPI is built on Starlette and Pydantic [1][3]\n"
            "- Average request latency is sub-10ms [2]"
        ),
        agent=agent,
    )


def analysis_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Take the research bullets from the previous task and group them "
            "into 3-5 coherent themes. For each theme: a one-line summary, "
            "supporting bullets with their [n] citations, and any contradictions."
        ),
        expected_output=(
            "Markdown with H3 headings per theme, bullets underneath, "
            "and a 'Gaps & Contradictions' section at the end."
        ),
        agent=agent,
    )


def writing_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Using the themed analysis from the previous task, write the full "
            "research report on '{query}'. Required sections in this order:\n"
            "  # [Title]\n"
            "  ## Executive Summary  (2-3 paragraphs)\n"
            "  ## Key Findings        (5-7 bullets, each cited)\n"
            "  ## Detailed Analysis   (one H3 per theme)\n"
            "  ## Conclusions & Recommendations\n"
            "  ## Sources             (numbered list [n] title - url)\n\n"
            "Sources list to use for the Sources section:\n{sources}"
        ),
        expected_output="A complete markdown report following the structure above.",
        agent=agent,
    )


def review_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Review the draft from the previous task. Check:\n"
            "  1. Every claim has a [n] citation\n"
            "  2. All required sections are present and non-empty\n"
            "  3. No filler ('In conclusion, it is important to note that...')\n"
            "  4. Sources section matches the citations used in-text\n\n"
            "Return the FINAL polished markdown (with your edits applied), "
            "not a critique. Do not add commentary above or below the report."
        ),
        expected_output="The final, ready-to-publish markdown report.",
        agent=agent,
    )
```

**Why placeholders like `{query}` and `{sources}`?**
CrewAI substitutes these when you call `crew.kickoff(inputs={"query": ..., "sources": ...})`. The intermediate task outputs are auto-injected into the next task's prompt — you don't write them yourself.

---

### Task 4 — Build the crew in `crew.py` (20 min)

```python
# app/crew/crew.py
from crewai import Crew, Process
from app.crew.agents import (
    researcher_agent, analyst_agent, writer_agent, reviewer_agent,
)
from app.crew.tasks import (
    research_task, analysis_task, writing_task, review_task,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_research_crew() -> Crew:
    researcher = researcher_agent()
    analyst = analyst_agent()
    writer = writer_agent()
    reviewer = reviewer_agent()

    return Crew(
        agents=[researcher, analyst, writer, reviewer],
        tasks=[
            research_task(researcher),
            analysis_task(analyst),
            writing_task(writer),
            review_task(reviewer),
        ],
        process=Process.sequential,
        verbose=True,
    )


async def run_crew(query: str, sources: list[dict]) -> str:
    """Run the crew and return final markdown."""
    crew = build_research_crew()

    formatted_sources = "\n".join(
        f"[{i + 1}] {s.get('title', '?')} - {s.get('url', '?')}\n    {s.get('content', s.get('snippet', ''))[:400]}"
        for i, s in enumerate(sources[:25])
    )

    logger.info(f"Kicking off crew for query: {query[:80]!r} with {len(sources)} sources")
    result = crew.kickoff(inputs={"query": query, "sources": formatted_sources})

    # crewai returns a CrewOutput object; .raw is the string of the last task
    return getattr(result, "raw", str(result))
```

> **Junior tip**: `crew.kickoff()` is **synchronous** in current CrewAI. If you must run it inside an async context (we do), wrap it in `asyncio.to_thread`:
> ```python
> import asyncio
> result = await asyncio.to_thread(crew.kickoff, inputs={...})
> ```

---

### Task 5 — Wire the crew into `report_node` (20 min)

`report_node` lives in `app/graph/nodes.py`. Two options:

**Option A** — call `run_crew` directly from the node (simpler):
```python
# app/graph/nodes.py
from app.crew.crew import run_crew

async def report_nodes(state: ResearchState) -> dict:
    await update_job(
        state["job_id"],
        status="generating",
        progress=f"Crew drafting report from {len(state.get('sources', []))} sources",
    )
    md = await run_crew(state["query"], state.get("sources", []))
    return {"report_markdown": md, "current_step": "report_generated"}
```

**Option B** — keep `ReportService.generate_report()` as the seam, swap its body:
```python
# app/services/report_service.py
async def generate_report(self, query: str, sources: list[dict]) -> str:
    from app.crew.crew import run_crew
    return await run_crew(query, sources)
```

Either works. **Pick Option B** if you want the choice of "single call vs crew" to be configurable later via a flag. Otherwise A is cleaner.

---

### Task 6 — Add per-agent progress updates (optional, 30 min)

By default you only see "generating" in `/research/{job_id}`. To show per-agent progress, use CrewAI's `step_callback`:

```python
# app/crew/crew.py
def make_step_callback(job_id: str):
    async def _cb(step):
        # step has .agent and .raw (or .task_name in newer versions)
        agent_role = getattr(step.agent, "role", "agent")
        from app.services.job_service import update_job
        await update_job(job_id, progress=f"{agent_role} finished a step")
    return _cb
```

Then pass it when building the crew:
```python
Crew(..., step_callback=make_step_callback(job_id))
```

Skip this on the first pass; add it once the basic flow works.

---

### Task 7 — Manual Testing (45 min)

| Test | Query | Expected |
|---|---|---|
| **T1 happy path** | "What is FastAPI?" | All 4 agents run, final markdown has all sections, citations align |
| **T2 deep query** | "Compare LangChain vs LlamaIndex for RAG" | Analyst surfaces themes per framework, Writer produces a comparison-style report |
| **T3 thin sources** | obscure term (force 3-4 sources) | Crew still produces output; Reviewer flags thin evidence in conclusions |
| **T4 LangGraph integration** | any standard query | `/research/{job_id}` walks plan → search → analyze → generating → complete with no regression |
| **T5 cost / latency check** | "What is FastAPI?" | Note token use + total time. Expect ~4× the Day 3 cost — this is the trade-off |

**Checklist after each test**:
- [ ] Report file written to `reports/`
- [ ] Each section present and non-empty
- [ ] Citations [n] in body match the Sources list
- [ ] Logs show all four agent turns (verbose=True)
- [ ] No exception in LangGraph workflow

---

## 7. File Map (What Will Exist At End Of Day 4)

```
app/
├── crew/                        ← NEW
│   ├── __init__.py
│   ├── agents.py                ← researcher / analyst / writer / reviewer
│   ├── tasks.py                 ← 4 task definitions
│   └── crew.py                  ← build_research_crew + run_crew
├── graph/
│   ├── nodes.py                 ← MODIFIED: report_node calls run_crew
│   ├── state.py                 ← unchanged
│   ├── routing.py               ← unchanged
│   └── workflow.py              ← unchanged
├── services/
│   ├── report_service.py        ← MODIFIED (only if you pick Option B)
│   └── (others unchanged)
└── routers/                     ← unchanged
```

---

## 8. Common Pitfalls (Read Before You Code)

1. **Forgetting to convert sources to a string**
   `kickoff(inputs={...})` expects strings, not Python lists/dicts. Format sources into a single string before passing.

2. **`crew.kickoff()` is synchronous — don't `await` it directly**
   It returns immediately with a result object, not a coroutine. To use inside async code: `await asyncio.to_thread(crew.kickoff, inputs={...})`.

3. **Token blow-up from `verbose=True` in production**
   Verbose dumps every prompt and response into stdout. Great for dev, noisy in prod. Turn it off (or send to a file) once the crew is stable.

4. **`allow_delegation=True` makes agents chat with each other**
   For a strict sequential pipeline you do NOT want this. Leave it `False` until you understand the cost.

5. **Reviewer returning a critique instead of the final report**
   The Reviewer task's `description` MUST say "Return the FINAL polished markdown, not a critique." Otherwise you'll get a list of suggestions as your output. Re-read your own prompt out loud.

6. **CrewAI version drift**
   The library is young and the API changes. `result.raw` vs `result` vs `result[0]` differs across versions. If something breaks, `print(type(result))` first.

7. **Mixing CrewAI's own LLM and LangChain's LLM**
   CrewAI accepts either. Stay consistent — we use `ChatOpenAI` from LangChain so the rest of the project shares one LLM client style.

8. **Quietly losing citations between Analyst and Writer**
   Each agent prompt MUST repeat the rule "every claim must end with a [n] citation". Without that reminder the Writer rewrites in clean prose and drops the numbers.

---

## 9. Glossary (Quick Reference)

| Term | One-liner |
|---|---|
| **Agent** | A role/goal/backstory persona with an LLM. |
| **Task** | A single instruction assigned to one agent. |
| **Crew** | A bundle of agents + tasks + a process. |
| **Process** | How tasks flow — `sequential` (line) or `hierarchical` (manager picks). |
| **kickoff()** | Runs the crew once with given inputs. Synchronous. |
| **step_callback** | Hook called after each task — use for live progress. |
| **inputs** | Dict of placeholder values for `{query}`, `{sources}`, etc. |

---

## 10. Implementation Order Recap

1. Install `crewai` + `crewai-tools` (5 min)
2. Create `app/crew/` package (10 min)
3. Write `agents.py` — 4 agents (45 min)
4. Write `tasks.py` — 4 tasks (45 min)
5. Write `crew.py` — build + run (20 min)
6. Wire `report_node` to call `run_crew` (20 min)
7. (Optional) Add `step_callback` for per-agent progress (30 min)
8. Run all 5 manual tests (45 min)

**Total estimated time**: ~3.5 hours (4 hours with step_callback).

---

## 11. What Day 4 Does NOT Do (Out Of Scope)

- **No PDF generation** yet — still markdown only. PDF is a downstream step we add after this works.
- **No tool use by agents** — agents only read what we hand them. No agent fires its own web search. (CrewAI supports it; we keep search inside LangGraph for clean separation.)
- **No hierarchical process** — sticking with sequential. Hierarchical adds a manager LLM call per task; expensive and harder to debug.
- **No retry on Reviewer rejection** — the Reviewer rewrites in-place rather than looping back to the Writer. Looping would need a second LangGraph pass and isn't worth the complexity yet.

---

## 12. Next Steps (Day 5 Preview)

After Day 4 ships, Day 5 candidates:
- **PDF export** — render the final markdown via `weasyprint` or `markdown-pdf`.
- **n8n integration** — fire the webhook we deferred on Day 3.
- **Agent tool use** — give the Researcher its own search tool so it can ask follow-up queries.
- **Caching** — cache crew outputs per `(query, source-hash)` so repeated identical jobs return instantly.

---

**End of Day 4 Plan**
