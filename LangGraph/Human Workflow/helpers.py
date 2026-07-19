from datetime import datetime
from pathlib import Path

from config.settings import settings


def load_prompt(name: str) -> str:
    path = settings.prompts_dir / name
    return path.read_text(encoding="utf-8").strip()


def save_email(content: str, folder: Path, prefix: str = "email") -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.txt"
    path = folder / filename
    path.write_text(content, encoding="utf-8")
    return path


def parse_feedback(raw: str) -> tuple[str, str]:
    raw = raw.strip()
    if raw.lower() == "approve":
        return "approve", ""
    lower = raw.lower()
    if lower.startswith("edit:"):
        return "edit", raw[5:].strip()
    if lower.startswith("revise:"):
        return "edit", raw[7:].strip()
    return "unknown", raw


def truncate(text: str, max_len: int = 200) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def timestamp_str() -> str:
    return datetime.now().strftime("%H:%M:%S")
