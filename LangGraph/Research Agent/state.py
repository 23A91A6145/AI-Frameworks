from typing import TypedDict


class ResearchState(TypedDict):
    query: str

    research_notes: str

    analysis: str

    report: str

    final_report: str

    saved_file: str

    pdf_file: str

    db_saved: bool