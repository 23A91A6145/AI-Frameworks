"""Smoke test for the CrewAI hierarchical crew build.

Skips automatically when ``crewai`` is not installed (e.g. Python 3.14 env).
Construction never calls the LLM API — only the agent/task/crew wiring.
"""

import pytest

crewai = pytest.importorskip("crewai")


def test_crew_builds_hierarchical(client):
    from conftest import auth_header, register

    from app.core.config import settings
    from app.models import Organization

    settings.LLM_PROVIDER = "openai"
    settings.LLM_API_KEY = "sk-fake-for-construction-test"
    settings.LLM_MODEL = "gpt-4o-mini"
    settings.AI_ENGINE = "auto"

    data = register(client, "crew@example.com", workspace="Crew Co")
    slug = data["memberships"][0]["organization_slug"]
    token = data["access_token"]

    org = client.get(f"/api/v1/workspaces/{slug}", headers=auth_header(token)).json()
    organization = Organization(
        id=org["id"], name=org["name"], slug=org["slug"], plan=org["plan"]
    )

    from app.agents.crew_support import build_crew

    crew = build_crew(
        organization,
        "Forgot password",
        "How do I reset my password? I am locked out.",
    )
    assert isinstance(crew, crewai.Crew)
    assert crew.process.value == "hierarchical"

    # The engine resolver sees crewai + a configured key → crewai engine.
    from app.agents.engine import resolve_engine_name

    assert resolve_engine_name() == "crewai"
