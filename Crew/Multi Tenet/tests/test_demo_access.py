"""One-click demo access — no account/setup required, idempotent, self-healing."""

from conftest import auth_header


def test_demo_returns_tokens_without_credentials(client):
    res = client.post("/api/v1/auth/demo")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["email"] == "owner@demo.com"


def test_demo_provisions_workspace_and_baseline_content(client):
    res = client.post("/api/v1/auth/demo")
    token = res.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers=auth_header(token))
    assert me.status_code == 200

    workspaces = client.get("/api/v1/workspaces", headers=auth_header(token))
    assert workspaces.status_code == 200
    slug = workspaces.json()[0]["slug"]

    # every module has content so the demo is fully populated
    stats = client.get(f"/api/v1/workspaces/{slug}/stats", headers=auth_header(token))
    assert stats.status_code == 200
    assert stats.json()["plan"] == "free"

    tickets = client.get(f"/api/v1/workspaces/{slug}/tickets", headers=auth_header(token))
    assert len(tickets.json()) >= 4

    knowledge = client.get(f"/api/v1/workspaces/{slug}/knowledge", headers=auth_header(token))
    assert len(knowledge.json()) >= 1

    flows = client.get(f"/api/v1/workspaces/{slug}/flows", headers=auth_header(token))
    assert len(flows.json()) >= 1

    jobs = client.get(f"/api/v1/workspaces/{slug}/jobs", headers=auth_header(token))
    assert len(jobs.json()) >= 1

    widget = client.get(f"/api/v1/workspaces/{slug}/widget/config", headers=auth_header(token))
    assert widget.json()["widget_enabled"] is True
    assert widget.json()["widget_token"]

    analytics = client.get(f"/api/v1/workspaces/{slug}/analytics/overview", headers=auth_header(token))
    assert analytics.json()["summary"]["requests_month"] > 0


def test_demo_is_idempotent(client):
    first = client.post("/api/v1/auth/demo").json()
    second = client.post("/api/v1/auth/demo").json()

    token = second["access_token"]
    workspaces = client.get("/api/v1/workspaces", headers=auth_header(token)).json()
    assert len(workspaces) == 1
    slug = workspaces[0]["slug"]

    # no duplicate tickets/jobs/flow runs from re-provisioning
    tickets = client.get(f"/api/v1/workspaces/{slug}/tickets", headers=auth_header(token)).json()
    assert len(tickets) == len({t["id"] for t in tickets})
    assert len(tickets) >= 4


def test_demo_user_can_also_log_in_normally(client):
    res = client.post("/api/v1/auth/demo")
    assert res.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@demo.com", "password": "demo-password-123"},
    )
    assert login.status_code == 200, login.text
