from app.graph.state import ResearchState

MAX_SEARCH_RETRIES = 3
MAX_QUALITY_LOOPS = 2

def route_after_plan(state: ResearchState) -> str:
    """Route logic after plan step."""
    if state.get("error"):
        return "fail"
    return "search"

def route_after_search(state: ResearchState) -> str:
    """Route logic after search step."""
    if state.get("error") and state["search_attempts"] < MAX_SEARCH_RETRIES:
        return "search"  # Retry search
    if state.get("error"):
        return "fail"
    return "analyze"

def route_after_analysis(state: ResearchState) -> str:
    """If sources are weak, re-plan and search again (up to quality loop limit)."""
    if state.get("error"):
        return "fail"
    if state["sources_quality"] == "weak" and state.get("plan_attempts", 0) < MAX_QUALITY_LOOPS:
        return "plan"  # Re-plan and search again
    return "generate_report"

def route_after_report(state: ResearchState) -> str:
    """Route logic after report step."""
    if state.get("error"):
        return "fail"
    return "save_report"

def route_after_save(state: ResearchState) -> str:
    """Route logic after save step."""
    if state.get("error"):
        return "fail"
    return "end"
