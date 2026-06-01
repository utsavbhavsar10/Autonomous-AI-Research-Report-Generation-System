from __future__ import annotations

import operator
from typing import Annotated, List, Optional, TypedDict


def _keep_latest(_old, new):
    """Custom Reducer: ignore the previous value and use the new one.

    LangGraph's default merge behavior for a key is already "overwrite",
    so this reducer is identical to omitting `Annotated` — it's spelled out
    here so the choice is explicit and greppable.
    """
    return new


class ResearchState(TypedDict, total=False):
    # Inputs (set once at graph entry)
    job_id: str
    query: str
    depth: str  # "standard" | "deep"

    # Planning
    # Overwritten each time plan_node runs (re-plan on quality loop).
    planned_queries: Annotated[List[str], _keep_latest]
    plan_attempts: int

    # Search
    # Overwritten on each search attempt (prevents duplication on loops).
    raw_results: Annotated[List[dict], _keep_latest]
    sources: Annotated[List[dict], _keep_latest]

    # search_node itself computes `prev + 1` and returns the new value,
    # so this is overwrite, not add.
    search_attempts: int

    # Analysis
    sources_quality: str  # "good" | "weak"

    # Report
    report_markdown: Optional[str]
    report_path: Optional[str]

    # Bookkeeping
    error: Optional[str]
    current_step: str
