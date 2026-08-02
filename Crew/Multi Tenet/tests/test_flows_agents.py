from conftest import auth_header, register


def _slug(data: dict) -> str:
    return data["memberships"][0]["organization_slug"]


def _ticket(client, token, slug):
    res = client.post(
        f"/api/v1/workspaces/{slug}/tickets",
        json={"subject": "Issue", "body": "Need help please"},
        headers=auth_header(token),
    )
    return res.json()


def test_escalation_and_feedback_flows(client):
    data = register(client, "f1@example.com", workspace="Flows Co")
    token = data["access_token"]
    slug = _slug(data)
    ticket = _ticket(client, token, slug)

    esc = client.post(
        f"/api/v1/workspaces/{slug}/flows/trigger",
        json={"flow_key": "escalation", "ticket_id": ticket["id"], "reason": "customer angry"},
        headers=auth_header(token),
    )
    assert esc.status_code == 201
    assert esc.json()["status"] == "completed"
    assert esc.json()["flow_key"] == "escalation"

    fb = client.post(
        f"/api/v1/workspaces/{slug}/flows/trigger",
        json={"flow_key": "feedback", "ticket_id": ticket["id"], "rating": 5, "comment": "Great!"},
        headers=auth_header(token),
    )
    assert fb.status_code == 201
    assert fb.json()["status"] == "completed"
    assert fb.json()["output_data"]["rating"] == 5


def test_flow_runs_are_listed_and_isolated(client):
    alice = register(client, "f2@example.com", workspace="Flows Co")
    bob = register(client, "f3@example.com", workspace="Flows Two")
    alice_slug = _slug(alice)
    bob_slug = _slug(bob)

    ticket = _ticket(client, alice["access_token"], alice_slug)
    client.post(
        f"/api/v1/workspaces/{alice_slug}/flows/trigger",
        json={"flow_key": "feedback", "ticket_id": ticket["id"], "rating": 4},
        headers=auth_header(alice["access_token"]),
    )

    alice_runs = client.get(
        f"/api/v1/workspaces/{alice_slug}/flows", headers=auth_header(alice["access_token"])
    ).json()
    bob_runs = client.get(
        f"/api/v1/workspaces/{bob_slug}/flows", headers=auth_header(bob["access_token"])
    ).json()
    assert len(alice_runs) == 1
    assert bob_runs == []

    cross = client.get(
        f"/api/v1/workspaces/{alice_slug}/flows/{alice_runs[0]['id']}",
        headers=auth_header(bob["access_token"]),
    )
    assert cross.status_code == 403


def test_agents_seeded_and_engine_status(client):
    data = register(client, "a1@example.com", workspace="Agents Co")
    token = data["access_token"]
    slug = _slug(data)

    agents = client.get(f"/api/v1/workspaces/{slug}/agents", headers=auth_header(token))
    assert agents.status_code == 200
    keys = {a["key"] for a in agents.json()}
    assert keys == {"manager", "router", "knowledge", "support", "escalation", "report"}

    engine = client.get(f"/api/v1/workspaces/{slug}/agents/engine", headers=auth_header(token))
    assert engine.json()["engine"] in ("fallback", "crewai", "llm")

    updated = client.patch(
        f"/api/v1/workspaces/{slug}/agents/support",
        json={"enabled": False, "llm_model": "custom-model"},
        headers=auth_header(token),
    )
    assert updated.status_code == 200
    assert updated.json()["enabled"] is False
    assert updated.json()["llm_model"] == "custom-model"
