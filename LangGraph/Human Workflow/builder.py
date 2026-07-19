from langgraph.graph import END, START, StateGraph

from graph.nodes import (
    apply_feedback,
    approve_email,
    draft_email,
    max_revisions_stop,
    review_interrupt,
    revise_email,
)
from graph.state import EmailState


def route_after_feedback(state: EmailState) -> str:
    status = state.get("status", "")
    if status == "approved":
        return "approve"
    if status == "max_revisions":
        return "max_rev"
    if status == "drafting":
        return "revise"
    return "approve"


def build_graph() -> StateGraph:
    builder = StateGraph(EmailState)

    builder.add_node("draft", draft_email)
    builder.add_node("review", review_interrupt)
    builder.add_node("apply_feedback", apply_feedback)
    builder.add_node("revise", revise_email)
    builder.add_node("approve", approve_email)
    builder.add_node("max_revisions", max_revisions_stop)

    builder.add_edge(START, "draft")
    builder.add_edge("draft", "review")
    builder.add_edge("review", "apply_feedback")

    builder.add_conditional_edges(
        "apply_feedback",
        route_after_feedback,
        {
            "approve": "approve",
            "max_rev": "max_revisions",
            "revise": "revise",
        },
    )

    builder.add_edge("revise", "review")
    builder.add_edge("approve", END)
    builder.add_edge("max_revisions", END)

    return builder
