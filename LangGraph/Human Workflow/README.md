# Human-Approved Email Drafter

![Python](https://img.shields.io/badge/python-3.11+-blue)
![LangGraph](https://img.shields.io/badge/langgraph-0.2+-red)
![License](https://img.shields.io/badge/license-MIT-green)

A LangGraph-powered email drafter with **human-in-the-loop** interrupt/resume pattern. AI generates a draft, pauses for human review, and resumes based on approval or feedback.

## How It Works

```
User Input (topic, recipient, tone)
        |
    [draft_email]  ── LLM generates email
        |
    [review]  ── interrupt() pauses graph
        |
    Human types "approve" or "edit: ..."
        |
    [apply_feedback]  ── routes based on input
       / \
      /   \
[approve] [revise]
    |        |
   END    [review]  ── loop back
```

## Quick Start

```bash
# Clone
git clone https://github.com/yourname/humaan-email-drafter.git
cd humaan-email-drafter

# Setup
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure (pick one provider)
cp .env.example .env
# Edit .env with your API key (Groq is free: https://console.groq.com)

# Run
python app.py
```

## Features

- **Human-in-the-loop** — interrupt/resume via `langgraph.types.interrupt`
- **Multi-provider** — Groq (free), OpenAI, Gemini, Ollama (local), Mistral
- **Rich terminal UI** — colored panels, status bars, draft display
- **Revision safety** — max 3 revisions by default (configurable)
- **Auto-save** — approved emails saved to `outputs/approved/`
- **Checkpointing** — graph state persisted via `MemorySaver`

## Configuration

| Setting | Default | Description |
|---|---|---|
| `provider` | `groq` | LLM provider |
| `model_name` | `llama-3.1-8b-instant` | Model identifier |
| `max_revisions` | `3` | Max edit rounds |
| `temperature` | `0.7` | Generation temperature |

## Tech Stack

- **LangGraph** — graph orchestration + interrupt/resume
- **LangChain** — LLM abstraction layer
- **Rich** — terminal UI rendering
- **Pydantic** — settings validation

## License

MIT
