"""Volume 6 tests — webhook integration, knowledge text ingest, job delete regression."""

import json

from conftest import auth_header, register


def test_knowledge_text_ingest(client):
    user = register(client, "text@example.com", workspace="Text Co")
    token = user["access_token"]
    slug = user["memberships"][0]["organization_slug"]

    res = client.post(
        f"/api/v1/workspaces/{slug}/knowledge/text",
        json={"name": "Security policy", "content": "Passwords expire every 90 days. Locked accounts reset via email."},
        headers=auth_header(token),
    )
    assert res.status_code == 201, res.text
    doc = res.json()
    assert doc["filename"] == "Security policy"
    assert doc["status"] == "ready"
    assert doc["chunk_count"] >= 1

    hits = client.post(
        f"/api/v1/workspaces/{slug}/knowledge/search",
        json={"query": "password expiration"},
        headers=auth_header(token),
    ).json()["hits"]
    assert any("password" in h["text"].lower() for h in hits)


def test_job_delete_returns_204(client):
    user = register(client, "jobs@example.com", workspace="Jobs Co")
    token = user["access_token"]
    slug = user["memberships"][0]["organization_slug"]

    created = client.post(
        f"/api/v1/workspaces/{slug}/jobs",
        json={"job_type": "weekly_report"},
        headers=auth_header(token),
    )
    assert created.status_code == 201, created.text
    job_id = created.json()["id"]

    deleted = client.delete(f"/api/v1/workspaces/{slug}/jobs/{job_id}", headers=auth_header(token))
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/workspaces/{slug}/jobs/{job_id}", headers=auth_header(token))
    assert missing.status_code == 404


def test_webhook_config_roundtrip_and_signature(client):
    user = register(client, "hooks@example.com", workspace="Hooks Co")
    token = user["access_token"]
    slug = user["memberships"][0]["organization_slug"]

    # default (unset)
    cfg = client.get(f"/api/v1/workspaces/{slug}/webhooks", headers=auth_header(token)).json()
    assert cfg["webhook_url"] == ""

    # set url + secret + subset of events
    res = client.post(
        f"/api/v1/workspaces/{slug}/webhooks",
        json={
            "url": "https://example.com/hook",
            "secret": "s3cret",
            "events": ["ticket.created"],
        },
        headers=auth_header(token),
    )
    assert res.status_code == 200
    cfg = res.json()
    assert cfg["webhook_url"] == "https://example.com/hook"
    assert cfg["webhook_secret"] == "s3cret"
    assert cfg["webhook_events"] == ["ticket.created"]

    # HMAC signature is deterministic and matches a locally recomputed digest
    from app.services import webhooks

    payload = b'{"event":"test.ping"}'
    assert webhooks._sign(payload, "s3cret") == webhooks._sign(payload, "s3cret")

    # test ping to an unreachable endpoint does not raise — returns delivered=False
    client.post(
        f"/api/v1/workspaces/{slug}/webhooks",
        json={"url": "http://127.0.0.1:1/nope", "secret": "s", "events": []},
        headers=auth_header(token),
    )
    ping = client.post(
        f"/api/v1/workspaces/{slug}/webhooks/test", headers=auth_header(token)
    ).json()
    assert ping["delivered"] is False
    assert "error" in ping


def test_ticket_created_fires_webhook_without_crashing(client, monkeypatch):
    user = register(client, "hook2@example.com", workspace="Hook2 Co")
    token = user["access_token"]
    slug = user["memberships"][0]["organization_slug"]

    captured = {}
    from app.services import webhooks

    def fake_deliver(org, event, data):
        captured["org"] = org.slug
        captured["event"] = event
        captured["data"] = data
        return {"delivered": True, "status": 200}

    monkeypatch.setattr(webhooks, "deliver", fake_deliver)

    res = client.post(
        f"/api/v1/workspaces/{slug}/tickets",
        json={"subject": "Help", "body": "Please help", "priority": "high"},
        headers=auth_header(token),
    )
    assert res.status_code == 201
    assert captured["org"] == slug
    assert captured["event"] == "ticket.created"
    assert captured["data"]["subject"] == "Help"
