from graph.builder import build_graph
from graph.state import EmailState


def test_graph_compiles():
    builder = build_graph()
    graph = builder.compile()
    assert graph is not None


def test_graph_has_nodes():
    builder = build_graph()
    graph = builder.compile()
    nodes = list(graph.get_graph().nodes)
    expected = {"draft", "review", "apply_feedback", "revise", "approve", "max_revisions"}
    assert expected.issubset(set(nodes))


def test_initial_state_valid():
    state: EmailState = {
        "topic": "test",
        "recipient": "test@test.com",
        "tone": "formal",
        "draft": "",
        "feedback": "",
        "revision_count": 0,
        "status": "drafting",
        "final_email": "",
    }
    assert state["topic"] == "test"
    assert state["revision_count"] == 0
