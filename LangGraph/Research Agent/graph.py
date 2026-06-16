from pathlib import Path

from database.db import (
    initialize_database,
    save_report
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from langgraph.graph import (
    StateGraph,
    END
)

from state import ResearchState

from agents.researcher import research_agent
from agents.analyzer import analyzer_agent
from agents.writer import writer_agent
from agents.reviewer import reviewer_agent


initialize_database()


def research_node(state):

    notes = research_agent(
        state["query"]
    )

    return {
        "research_notes": notes
    }


def analyze_node(state):

    analysis = analyzer_agent(
        state["research_notes"]
    )

    return {
        "analysis": analysis
    }


def writer_node(state):

    report = writer_agent(
        state["analysis"]
    )

    return {
        "report": report
    }


def reviewer_node(state):

    final_report = reviewer_agent(
        state["report"]
    )

    return {
        "final_report": final_report
    }


def save_node(state):

    reports_dir = Path(
        "outputs/reports"
    )

    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        state["query"]
        .lower()
        .replace(" ", "_")
        + ".md"
    )

    file_path = reports_dir / filename

    file_path.write_text(
        state["final_report"],
        encoding="utf-8"
    )

    return {
        "saved_file": str(file_path)
    }


def pdf_node(state):

    markdown_path = Path(
        state["saved_file"]
    )

    pdf_path = markdown_path.with_suffix(
        ".pdf"
    )

    doc = SimpleDocTemplate(
        str(pdf_path)
    )

    styles = getSampleStyleSheet()

    content = []

    for line in state[
        "final_report"
    ].split("\n"):

        if line.strip():

            content.append(
                Paragraph(
                    line,
                    styles["BodyText"]
                )
            )

            content.append(
                Spacer(1, 6)
            )

    doc.build(content)

    return {
        "pdf_file": str(pdf_path)
    }


def database_node(state):

    save_report(
        topic=state["query"],
        markdown_path=state["saved_file"],
        pdf_path=state["pdf_file"],
        report=state["final_report"]
    )

    return {
        "db_saved": True
    }


workflow = StateGraph(
    ResearchState
)

workflow.add_node(
    "research",
    research_node
)

workflow.add_node(
    "analyze",
    analyze_node
)

workflow.add_node(
    "writer",
    writer_node
)

workflow.add_node(
    "review",
    reviewer_node
)

workflow.add_node(
    "save",
    save_node
)

workflow.add_node(
    "pdf",
    pdf_node
)

workflow.add_node(
    "database",
    database_node
)

workflow.set_entry_point(
    "research"
)

workflow.add_edge(
    "research",
    "analyze"
)

workflow.add_edge(
    "analyze",
    "writer"
)

workflow.add_edge(
    "writer",
    "review"
)

workflow.add_edge(
    "review",
    "save"
)

workflow.add_edge(
    "save",
    "pdf"
)

workflow.add_edge(
    "pdf",
    "database"
)

workflow.add_edge(
    "database",
    END
)

app_graph = workflow.compile()