from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState

from app.graph.nodes import (
    plan_nodes,search_nodes,analysis_nodes,report_nodes,save_nodes
)
from app.graph.routing import (
    route_after_plan, route_after_search, route_after_analysis, route_after_report, route_after_save
)
from app.services.job_service import update_job


async def fail_node(state):
    await update_job(state["job_id"], 
                     status="failed", 
                     progress=f"Pipeline failed: {state.get('error')}")
    return {"current_step": "failed"}

def build_workflow():

    g = StateGraph(ResearchState)

    g.add_node("plan", plan_nodes)
    g.add_node("search", search_nodes)
    g.add_node("analyze", analysis_nodes)
    g.add_node("generate_report", report_nodes)
    g.add_node("save_report", save_nodes)
    g.add_node("fail", fail_node)

    g.set_entry_point("plan")
    
    g.add_conditional_edges("plan", route_after_plan, {
        "search": "search",
        "fail": "fail"
    })

    g.add_conditional_edges("search", route_after_search , {
        "search": "search",
        "analyze": "analyze",
        "fail": "fail",
    })

    g.add_conditional_edges("analyze", route_after_analysis , {
        "plan": "plan",
        "generate_report": "generate_report",
        "fail": "fail"
    })

    g.add_conditional_edges("generate_report", route_after_report, {
        "save_report": "save_report",
        "fail": "fail"
    })
    
    g.add_conditional_edges("save_report", route_after_save, {
        "end": END,
        "fail": "fail"
    })
    
    g.add_edge("fail", END)

    return g.compile()

workflow = build_workflow()