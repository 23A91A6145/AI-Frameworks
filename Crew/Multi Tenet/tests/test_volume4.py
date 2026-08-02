"""Volume 4 tests — plans/quota, analytics, long-running jobs, public widget."""

import time

from conftest import auth_header, register


def _workspace_and_headers(client) -> tuple[str, dict]:
    data = register(client, "vol4@example.com", "Vol4 Workspace")
    headers = auth_header(data["access_token"])
    return "vol4-workspace", headers


def _make_ticket(client, slug, headers) -> str:
    res = client.post(
        f"/api/v1/workspaces/{slug}/tickets",
        json={"subject": "Password reset not working", "body": "I cannot log in, the reset link fails"},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_billing_summary_and_quota_enforcement(client):
    slug, headers = _workspace_and_headers(client)

    res = client.get(f"/api/v1/workspaces/{slug}/billing/summary", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["plan"] == "free"
    assert body["plan_details"]["requests_per_month"] == 500
    assert body["plan_details"]["knowledge_docs"] == 10
    assert body["plan_details"]["seats"] == 5
    assert any(item["key"] == "requests" for item in body["items"])
    assert any(item["key"] == "seats" for item in body["items"])
    assert len(body["all_plans"]) == 3


def test_change_plan_updates_limits(client):
    slug, headers = _workspace_and_headers(client)

    res = client.post(f"/api/v1/workspaces/{slug}/billing/change", json={"plan": "pro"}, headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["plan"] == "pro"
    assert res.json()["plan_details"]["requests_per_month"] == 5000

    # free plan switch back
    res = client.post(f"/api/v1/workspaces/{slug}/billing/change", json={"plan": "free"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["plan"] == "free"

    # same-plan change is rejected
    res = client.post(f"/api/v1/workspaces/{slug}/billing/change", json={"plan": "free"}, headers=headers)
    assert res.status_code == 409


def test_analytics_endpoints_return_shapes(client):
    slug, headers = _workspace_and_headers(client)

    # Generate some data
    ticket_id = _make_ticket(client, slug, headers)
    client.post(f"/api/v1/workspaces/{slug}/tickets/{ticket_id}/ai-handle", headers=headers)
    client.post(
        f"/api/v1/workspaces/{slug}/knowledge/faq",
        json={"name": "Login FAQ", "content": "Q: How do I reset my password?\nA: Use the reset link."},
        headers=headers,
    )

    res = client.get(f"/api/v1/workspaces/{slug}/analytics/overview", headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert "summary" in body and "usage" in body and "tickets" in body
    assert "knowledge" in body and "agents" in body
    assert body["summary"]["tickets_open"] >= 1
    assert body["summary"]["knowledge_docs"] >= 1
    assert isinstance(body["usage"]["daily_requests"], list)
    assert isinstance(body["usage"]["by_kind"], list)
    assert isinstance(body["tickets"]["by_status"], list)
    assert isinstance(body["agents"]["flows"], list)

    res = client.get(f"/api/v1/workspaces/{slug}/analytics/usage", headers=headers)
    assert res.status_code == 200
    assert any(day["count"] > 0 for day in res.json()["daily_requests"])


def test_job_creation_and_execution(client):
    slug, headers = _workspace_and_headers(client)

    # weekly report job
    res = client.post(
        f"/api/v1/workspaces/{slug}/jobs",
        json={"job_type": "weekly_report", "label": "Test weekly report"},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    job = res.json()
    assert job["status"] == "completed"
    assert "report_markdown" in job["result"]
    assert job["progress"] == 100

    # batch FAQ job
    res = client.post(
        f"/api/v1/workspaces/{slug}/jobs",
        json={
            "job_type": "batch_faq",
            "items": [
                {"name": "Refund Policy", "content": "Q: Refund policy?\nA: 30 days."},
                {"name": "Shipping", "content": "Q: Shipping times?\nA: 2-5 days."},
            ],
        },
        headers=headers,
    )
    assert res.status_code == 201, res.text
    assert res.json()["status"] == "completed"
    assert res.json()["result"]["count"] == 2

    # job listing
    res = client.get(f"/api/v1/workspaces/{slug}/jobs", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 2

    # retry an invalid job type should fail at validation
    res = client.post(
        f"/api/v1/workspaces/{slug}/jobs", json={"job_type": "not_a_job"}, headers=headers
    )
    assert res.status_code == 422


def test_reindex_document_job(client):
    slug, headers = _workspace_and_headers(client)

    res = client.post(
        f"/api/v1/workspaces/{slug}/knowledge/faq",
        json={"name": "Billing FAQ", "content": "Q: How do I get a refund?\nA: Contact support."},
        headers=headers,
    )
    doc_id = res.json()["id"]

    res = client.post(
        f"/api/v1/workspaces/{slug}/jobs",
        json={"job_type": "index_document", "document_id": doc_id},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    assert res.json()["status"] == "completed"
    assert res.json()["result"]["document_id"] == doc_id
    assert res.json()["result"]["chunks"] >= 1

    # search still works after re-index
    res = client.post(
        f"/api/v1/workspaces/{slug}/knowledge/search",
        json={"query": "refund", "top_k": 3},
        headers=headers,
    )
    assert res.status_code == 200
    assert len(res.json()["hits"]) >= 1


def test_public_widget_chat(client):
    slug, headers = _workspace_and_headers(client)

    # widget disabled by default → 403
    res = client.post(
        f"/api/v1/public/{slug}/chat",
        json={"message": "how do i reset my password"},
        headers={"X-Widget-Token": "nope"},
    )
    assert res.status_code == 403

    # enable widget + get token
    res = client.post(f"/api/v1/workspaces/{slug}/widget/enable", headers=headers)
    assert res.status_code == 200, res.text
    token = res.json()["token"]
    assert token

    # wrong token → 401
    res = client.post(
        f"/api/v1/public/{slug}/chat",
        json={"message": "hello"},
        headers={"X-Widget-Token": "wrong"},
    )
    assert res.status_code == 401

    # correct token → AI answer (fallback engine works offline)
    res = client.post(
        f"/api/v1/public/{slug}/chat",
        json={"message": "how do i reset my password"},
        headers={"X-Widget-Token": token},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["answer"]
    assert body["tenant"] == "Vol4 Workspace"

    # rotate token invalidates old one
    res = client.post(f"/api/v1/workspaces/{slug}/widget/rotate", headers=headers)
    assert res.status_code == 200
    new_token = res.json()["token"]
    assert new_token != token

    res = client.post(
        f"/api/v1/public/{slug}/chat",
        json={"message": "hello"},
        headers={"X-Widget-Token": token},
    )
    assert res.status_code == 401

    res = client.post(
        f"/api/v1/public/{slug}/chat",
        json={"message": "hello again"},
        headers={"X-Widget-Token": new_token},
    )
    assert res.status_code == 200

    # widget ticket creation
    res = client.post(
        f"/api/v1/public/{slug}/tickets",
        json={"message": "I need a human please"},
        headers={"X-Widget-Token": new_token},
    )
    assert res.status_code == 201, res.text
    assert res.json()["ticket_id"]


def test_usage_metering_records_kinds(client):
    slug, headers = _workspace_and_headers(client)

    ticket_id = _make_ticket(client, slug, headers)
    client.post(f"/api/v1/workspaces/{slug}/tickets/{ticket_id}/ai-handle", headers=headers)
    client.post(
        f"/api/v1/workspaces/{slug}/knowledge/search",
        json={"query": "reset", "top_k": 3},
        headers=headers,
    )

    summary = client.get(f"/api/v1/workspaces/{slug}/analytics/summary", headers=headers).json()
    kinds = client.get(f"/api/v1/workspaces/{slug}/analytics/usage", headers=headers).json()["by_kind"]
    kind_names = {item["kind"] for item in kinds}

    assert summary["requests_month"] >= 2
    assert "flow" in kind_names
    assert "search" in kind_names
