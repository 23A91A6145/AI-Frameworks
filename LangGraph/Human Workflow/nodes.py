from langgraph.types import interrupt

from config.settings import settings
from graph.state import EmailState
from utils.display import Display
from utils.helpers import load_prompt, parse_feedback
from utils.llm import get_llm
from utils.logger import logger


def draft_email(state: EmailState) -> dict:
    logger.info("Generating email draft...")
    Display.info("Generating draft...")

    llm = get_llm()
    prompt_template = load_prompt("email_prompt.txt")

    prompt = prompt_template.format(
        topic=state["topic"],
        recipient=state["recipient"],
        tone=state["tone"],
    )

    response = llm.invoke(prompt)
    draft = response.content.strip()

    return {
        "draft": draft,
        "status": "review",
        "revision_count": state.get("revision_count", 0),
    }


def review_interrupt(state: EmailState) -> dict:
    revision = state.get("revision_count", 0) + 1

    Display.draft_panel(state["draft"], version=revision)
    Display.status_bar(revision, settings.max_revisions, "review")
    Display.info('Type "approve" to accept or "edit: <feedback>" to revise')

    human_input = interrupt("awaiting_human_approval")

    return {"feedback": human_input, "status": "drafting"}


def apply_feedback(state: EmailState) -> dict:
    action, feedback = parse_feedback(state["feedback"])

    if action == "approve":
        return {
            "status": "approved",
            "final_email": state["draft"],
            "feedback": "",
        }

    if action == "edit":
        count = state.get("revision_count", 0)
        if count >= settings.max_revisions:
            Display.error(f"Maximum revisions ({settings.max_revisions}) reached")
            return {
                "status": "max_revisions",
                "final_email": state["draft"],
                "feedback": "",
            }

        Display.revision(count + 1)
        return {
            "feedback": feedback,
            "status": "drafting",
            "revision_count": count + 1,
        }

    Display.error("Unknown input. Use 'approve' or 'edit: <feedback>'")
    return {"feedback": "", "status": "review"}


def revise_email(state: EmailState) -> dict:
    logger.info("Revising email with feedback...")
    Display.info("Revising draft...")

    llm = get_llm()
    prompt_template = load_prompt("review_prompt.txt")

    prompt = prompt_template.format(
        feedback=state["feedback"],
        draft=state["draft"],
    )

    response = llm.invoke(prompt)
    revised = response.content.strip()

    return {
        "draft": revised,
        "status": "review",
    }


def approve_email(state: EmailState) -> dict:
    Display.approval()
    return {"status": "approved", "final_email": state["draft"]}


def max_revisions_stop(state: EmailState) -> dict:
    Display.error(f"Max revisions ({settings.max_revisions}) hit. Returning best draft.")
    return {"final_email": state["draft"], "status": "max_revisions"}
