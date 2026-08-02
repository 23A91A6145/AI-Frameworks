from conftest import auth_header, register

FAQ = """Q: How do I reset my password?
A: Go to Settings and click Forgot password.
Q: Where is my invoice?
A: Invoices live in the Billing section.
Q: How do I add a teammate?
A: Invite them from the Users page.
"""


def _workspace_slug(data: dict) -> str:
    return data["memberships"][0]["organization_slug"]


def _upload(client, token, slug, content, filename="docs.txt", tags="faq"):
    return client.post(
        f"/api/v1/workspaces/{slug}/knowledge",
        headers=auth_header(token),
        data={"tags": tags},
        files={"file": (filename, content, "text/plain")},
    )


def test_upload_and_search_document(client):
    data = register(client, "know@example.com", workspace="Know Co")
    token = data["access_token"]
    slug = _workspace_slug(data)

    res = _upload(client, token, slug, FAQ, "faq.txt")
    assert res.status_code == 201
    doc = res.json()
    assert doc["status"] == "ready"
    assert doc["chunk_count"] >= 1
    assert "faq" in doc["tags"]

    found = client.post(
        f"/api/v1/workspaces/{slug}/knowledge/search",
        json={"query": "reset my password"},
        headers=auth_header(token),
    )
    assert found.status_code == 200
    hits = found.json()["hits"]
    assert hits, "expected at least one hit"
    assert any("password" in hit["text"].lower() for hit in hits)


def test_list_and_tags(client):
    data = register(client, "tags@example.com", workspace="Tag Co")
    token = data["access_token"]
    slug = _workspace_slug(data)

    _upload(client, token, slug, FAQ, "faq.txt")

    listed = client.get(f"/api/v1/workspaces/{slug}/knowledge", headers=auth_header(token))
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    tags = client.get(f"/api/v1/workspaces/{slug}/knowledge/tags", headers=auth_header(token))
    assert tags.status_code == 200
    assert any(t["name"] == "faq" for t in tags.json())


def test_tenant_knowledge_isolation(client):
    alice = register(client, "alice-k@example.com", workspace="Alice KB")
    bob = register(client, "bob-k@example.com", workspace="Bob KB")
    alice_slug = _workspace_slug(alice)
    bob_slug = _workspace_slug(bob)

    _upload(client, alice["access_token"], alice_slug, FAQ, "alice-secret.txt")

    bob_search = client.post(
        f"/api/v1/workspaces/{bob_slug}/knowledge/search",
        json={"query": "reset my password"},
        headers=auth_header(bob["access_token"]),
    )
    assert bob_search.json()["hits"] == []

    alice_cross = client.post(
        f"/api/v1/workspaces/{alice_slug}/knowledge/search",
        json={"query": "reset my password"},
        headers=auth_header(bob["access_token"]),
    )
    assert alice_cross.status_code == 403


def test_delete_document_removes_vectors(client):
    data = register(client, "del@example.com", workspace="Del Co")
    token = data["access_token"]
    slug = _workspace_slug(data)

    doc = _upload(client, token, slug, FAQ, "faq.txt").json()

    deleted = client.delete(
        f"/api/v1/workspaces/{slug}/knowledge/{doc['id']}", headers=auth_header(token)
    )
    assert deleted.status_code == 204

    found = client.post(
        f"/api/v1/workspaces/{slug}/knowledge/search",
        json={"query": "reset password"},
        headers=auth_header(token),
    )
    assert found.json()["hits"] == []


def test_unsupported_file_rejected(client):
    data = register(client, "bad@example.com", workspace="Bad Co")
    token = data["access_token"]
    slug = _workspace_slug(data)

    res = _upload(client, token, slug, b"x", "evil.exe")
    assert res.status_code == 422


def test_faq_ingestion_endpoint(client):
    data = register(client, "faq@example.com", workspace="Faq Co")
    token = data["access_token"]
    slug = _workspace_slug(data)

    res = client.post(
        f"/api/v1/workspaces/{slug}/knowledge/faq",
        json={"name": "Pricing FAQ", "content": FAQ},
        headers=auth_header(token),
    )
    assert res.status_code == 201
    assert res.json()["source_type"] == "faq"
    assert res.json()["status"] == "ready"
