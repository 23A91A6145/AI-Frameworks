"""Regression tests for security + correctness fixes:

- cross-tenant ticket isolation on ``ai-handle`` (was: any member could run the
  crew flow against another tenant's ticket)
- ``ai-handle`` on a missing ticket returns 404 (was: 500 AttributeError)
- job-based knowledge ingestion cannot bypass the knowledge-document quota
- the MCP filesystem server stays inside its sandbox (no secrets, no sibling
  ``root*`` prefix escape)
"""

import os
from pathlib import Path

from conftest import TestingSessionLocal, auth_header, register

STORAGE = Path("/tmp/opencode/td-test-storage")


def _org_plan(slug: str) -> str:
    from sqlalchemy import select

    from app.models import Organization

    db = TestingSessionLocal()
    try:
        org = db.execute(select(Organization).where(Organization.slug == slug)).scalar_one()
        return org.plan
    finally:
        db.close()


def test_ai_handle_foreign_ticket_is_404(client):
    owner_a = register(client, "tenanta@example.com", workspace="Tenant A")
    owner_b = register(client, "tenantb@example.com", workspace="Tenant B")
    token_a = owner_a["access_token"]
    slug_a = owner_a["memberships"][0]["organization_slug"]
    slug_b = owner_b["memberships"][0]["organization_slug"]
    token_b = owner_b["access_token"]

    ticket_b = client.post(
        f"/api/v1/workspaces/{slug_b}/tickets",
        json={"subject": "B's ticket", "body": "secret from B", "priority": "high"},
        headers=auth_header(token_b),
    ).json()

    # user in tenant A (member of A) must NOT be able to ai-handle tenant B's
    # ticket by passing A's slug with B's ticket id
    res = client.post(
        f"/api/v1/workspaces/{slug_a}/tickets/{ticket_b['id']}/ai-handle",
        headers=auth_header(token_a),
    )
    assert res.status_code == 404, res.text

    # and the ticket must be untouched by the cross-tenant attempt
    detail = client.get(
        f"/api/v1/workspaces/{slug_b}/tickets/{ticket_b['id']}",
        headers=auth_header(token_b),
    ).json()
    assert detail["status"] != "escalated"
    assert detail["classification"] is None
    assert detail["ai_summary"] is None
    assert detail["message_count"] == 1


def test_ai_handle_missing_ticket_is_404(client):
    user = register(client, "missing@example.com", workspace="Missing Co")
    token = user["access_token"]
    slug = user["memberships"][0]["organization_slug"]

    res = client.post(
        f"/api/v1/workspaces/{slug}/tickets/no-such-ticket/ai-handle",
        headers=auth_header(token),
    )
    assert res.status_code == 404, res.text


def test_batch_faq_job_respects_knowledge_quota(client):
    from app.models import Organization
    from app.services import knowledge_service
    from sqlalchemy import select

    user = register(client, "quota@example.com", workspace="Quota Co")
    token = user["access_token"]
    slug = user["memberships"][0]["organization_slug"]

    db = TestingSessionLocal()
    try:
        org = db.execute(select(Organization).where(Organization.slug == slug)).scalar_one()
        assert org.plan == "free"  # 10-doc limit
        for i in range(10):
            knowledge_service.ingest_faq(
                db,
                organization=org,
                name=f"Existing FAQ {i}",
                content=f"Answer number {i}.",
            )
        db.commit()
    finally:
        db.close()

    job = client.post(
        f"/api/v1/workspaces/{slug}/jobs",
        json={
            "job_type": "batch_faq",
            "items": [{"name": "Bypass", "content": "Should be rejected"}],
        },
        headers=auth_header(token),
    )
    assert job.status_code == 201, job.text
    body = job.json()
    assert body["status"] == "failed", body
    assert "knowledge" in body["error"].lower() or "plan" in body["error"].lower()


def test_mcp_filesystem_sandbox_blocks_secrets_and_escapes():
    from app.mcp.client import mcp_client

    root = STORAGE
    root.mkdir(parents=True, exist_ok=True)
    (root / "welcome.txt").write_text("hello")
    (root / ".env").write_text("SECRET_KEY=leak-me")
    sibling = root.parent / (root.name + "-notes")
    sibling.mkdir(parents=True, exist_ok=True)
    (sibling / "secret.txt").write_text("sibling secret")

    fs = mcp_client.servers["filesystem"]

    # legitimate file inside the sandbox is readable
    ok = fs.execute_tool("fs_read_file", {"path": "welcome.txt"})
    assert "error" not in ok and "hello" in ok["content"]

    # .env inside the sandbox is blocked
    denied = fs.execute_tool("fs_read_file", {"path": ".env"})
    assert "error" in denied

    # traversal back to the backend repo (outside storage root) is blocked
    for escape in ["../.env", "../app/main.py", "..", "../../"]:
        res = fs.execute_tool("fs_read_file", {"path": escape})
        assert "error" in res, escape

    # sibling directory with a root* prefix name must NOT pass the boundary check
    res = fs.execute_tool("fs_read_file", {"path": f"../{root.name}-notes/secret.txt"})
    assert "error" in res

    # search only surfaces sandbox files, never sensitive ones
    search = fs.execute_tool("fs_search_files", {"pattern": "*.txt"})
    assert "welcome.txt" in search["matches"]
    assert not any("secret.txt" in m for m in search["matches"])
