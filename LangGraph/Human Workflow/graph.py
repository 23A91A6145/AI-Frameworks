from langgraph.checkpoint.memory import MemorySaver

from graph.builder import build_graph

builder = build_graph()
checkpointer = MemorySaver()

compiled_graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["review"],
)
