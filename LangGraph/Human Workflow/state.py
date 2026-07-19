from typing import Literal, TypedDict


class EmailState(TypedDict):
    topic: str
    recipient: str
    tone: str
    draft: str
    feedback: str
    revision_count: int
    status: Literal["drafting", "review", "approved", "max_revisions"]
    final_email: str
