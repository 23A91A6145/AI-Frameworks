from config.settings import settings
from utils.helpers import load_prompt, parse_feedback, truncate


def test_parse_approve():
    action, feedback = parse_feedback("approve")
    assert action == "approve"
    assert feedback == ""


def test_parse_approve_case():
    action, _ = parse_feedback("APPROVE")
    assert action == "approve"


def test_parse_edit():
    action, feedback = parse_feedback("edit: make it shorter")
    assert action == "edit"
    assert feedback == "make it shorter"


def test_parse_revise():
    action, feedback = parse_feedback("revise: add more detail")
    assert action == "edit"
    assert feedback == "add more detail"


def test_parse_unknown():
    action, feedback = parse_feedback("hello world")
    assert action == "unknown"
    assert feedback == "hello world"


def test_parse_edit_empty():
    action, feedback = parse_feedback("edit:")
    assert action == "edit"
    assert feedback == ""


def test_truncate_short():
    assert truncate("hi", 10) == "hi"


def test_truncate_long():
    result = truncate("hello world this is long", 10)
    assert len(result) == 10
    assert result.endswith("...")


def test_load_prompt():
    prompt = load_prompt("email_prompt.txt")
    assert "{topic}" in prompt
    assert "{recipient}" in prompt
    assert "{tone}" in prompt


def test_settings_dirs_exist():
    assert settings.drafts_dir.exists()
    assert settings.approved_dir.exists()
    assert settings.prompts_dir.exists()
