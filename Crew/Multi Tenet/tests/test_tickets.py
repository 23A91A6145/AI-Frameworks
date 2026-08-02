from conftest import auth_header, register


def _slug(data: dict) -> str:
    return data["memberships"][0]["organization_slug"]


def _create_ticket(client, token, slug, subject="Help needed", body="How do I reset my password?", priority="medium"):
    res = client.post(
        f"/api/v1/workspaces/{slug}/tickets",
        json={"subject": subject, "body": body, "priority": priority},
        headers=auth_header(token),
    )
    assert res.status_code == 201, res.text
    return res.json()


def _knowledge(client, token, slug):
    faq = "Q: How do I reset my password?\nA: Use Settings > Forgot password."
    res = client.post(
        f"/api/v1/workspaces/{slug}/knowledge/faq",
        json={"name": "FAQ", "content": faq},
        headers=auth_header(token),
    )
    assert res.status_code == 201


def test_create_and_list_tickets(client):
    data = register(client, "t1@example.com", workspace="Tickets Co")
    token = data["access_token"]
    slug = _slug(data)

    ticket = _create_ticket(client, token, slug)
    assert ticket["status"] == "new"
    assert ticket["message_count"] == 1

    listed = client.get(f"/api/v1/workspaces/{slug}/tickets", headers=auth_header(token))
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    detail = client.get(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}", headers=auth_header(token)
    )
    assert detail.json()["messages"][0]["sender"] == "user"


def test_add_human_message_reenables_ticket(client):
    data = register(client, "t2@example.com", workspace="Tickets Co")
    token = data["access_token"]
    slug = _slug(data)

    ticket = _create_ticket(client, token, slug, subject="More info")
    msg = client.post(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}/messages",
        json={"content": "Please reset it"},
        headers=auth_header(token),
    )
    assert msg.status_code == 201
    assert msg.json()["sender"] == "user"


def test_ai_handle_resolves_ticket_from_knowledge(client):
    data = register(client, "t3@example.com", workspace="Tickets Co")
    token = data["access_token"]
    slug = _slug(data)

    _knowledge(client, token, slug)
    ticket = _create_ticket(
        client, token, slug,
        subject="Forgot password",
        body="I forgot my password, how do I reset it?",
    )

    res = client.post(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}/ai-handle",
        headers=auth_header(token),
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["classification"] == "account"
    assert payload["awaiting_approval"] is False
    assert payload["draft"], "expected a draft response"
    assert payload["sources"], "expected knowledge sources to be cited"

    detail = client.get(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}", headers=auth_header(token)
    ).json()
    assert detail["status"] == "resolved"
    assert detail["messages"][-1]["sender"] == "ai"


def test_urgent_ticket_waits_for_human_approval_then_publishes(client):
    data = register(client, "t4@example.com", workspace="Tickets Co")
    token = data["access_token"]
    slug = _slug(data)

    _knowledge(client, token, slug)
    ticket = _create_ticket(
        client, token, slug,
        subject="URGENT account locked",
        body="Urgent! My account is locked and I need access tonight, ASAP.",
    )

    res = client.post(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}/ai-handle",
        headers=auth_header(token),
    )
    payload = res.json()
    assert payload["escalate"] is True
    assert payload["awaiting_approval"] is True
    run_id = payload["flow_run"]["id"]

    pending = client.get(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}", headers=auth_header(token)
    ).json()
    assert pending["status"] != "resolved"

    approved = client.post(
        f"/api/v1/workspaces/{slug}/flows/{run_id}/resume",
        json={"approved": True},
        headers=auth_header(token),
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "completed"

    detail = client.get(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}", headers=auth_header(token)
    ).json()
    assert detail["status"] == "escalated"
    assert any(m["sender"] == "ai" for m in detail["messages"])


def test_ai_draft_can_be_rejected(client):
    data = register(client, "t5@example.com", workspace="Tickets Co")
    token = data["access_token"]
    slug = _slug(data)

    _knowledge(client, token, slug)
    ticket = _create_ticket(
        client, token, slug,
        subject="URGENT broken",
        body="Urgent problem, critical, please fix immediately",
    )

    res = client.post(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}/ai-handle?require_approval=true",
        headers=auth_header(token),
    )
    run_id = res.json()["flow_run"]["id"]

    rejected = client.post(
        f"/api/v1/workspaces/{slug}/flows/{run_id}/resume",
        json={"approved": False},
        headers=auth_header(token),
    )
    assert rejected.json()["status"] == "rejected"

    detail = client.get(
        f"/api/v1/workspaces/{slug}/tickets/{ticket['id']}", headers=auth_header(token)
    ).json()
    assert not any(m["sender"] == "ai" for m in detail["messages"])
