from conftest import auth_header, register


def test_create_and_get_workspace(client):
    data = register(client, "ws@example.com")
    token = data["access_token"]

    created = client.post(
        "/api/v1/workspaces",
        json={"name": "My Startup"},
        headers=auth_header(token),
    )
    assert created.status_code == 201
    slug = created.json()["slug"]
    assert created.json()["your_role"] == "owner"

    got = client.get(f"/api/v1/workspaces/{slug}", headers=auth_header(token))
    assert got.status_code == 200
    assert got.json()["name"] == "My Startup"


def test_duplicate_slug_gets_suffix(client):
    data = register(client, "slug@example.com")
    token = data["access_token"]
    first = client.post("/api/v1/workspaces", json={"name": "My Co"}, headers=auth_header(token))
    second = client.post("/api/v1/workspaces", json={"name": "My Co"}, headers=auth_header(token))
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["slug"] != second.json()["slug"]


def test_tenant_isolation(client):
    alice = register(client, "alice-isolation@example.com", workspace="Alice Inc")
    bob = register(client, "bob-isolation@example.com")
    slug = alice["memberships"][0]["organization_slug"]

    res = client.get(f"/api/v1/workspaces/{slug}", headers=auth_header(bob["access_token"]))
    assert res.status_code == 403

    res = client.get(f"/api/v1/workspaces/{slug}/members", headers=auth_header(bob["access_token"]))
    assert res.status_code == 403


def test_invite_member_and_list(client):
    alice = register(client, "alice-invite@example.com", workspace="Invite Co")
    bob = register(client, "bob-invite@example.com")
    token = alice["access_token"]
    slug = alice["memberships"][0]["organization_slug"]

    invited = client.post(
        f"/api/v1/workspaces/{slug}/members",
        json={"email": "bob-invite@example.com", "role": "user"},
        headers=auth_header(token),
    )
    assert invited.status_code == 201
    assert invited.json()["role"] == "user"

    members = client.get(f"/api/v1/workspaces/{slug}/members", headers=auth_header(token))
    assert members.status_code == 200
    assert len(members.json()) == 2


def test_invite_unregistered_email(client):
    alice = register(client, "alice-miss@example.com", workspace="Miss Co")
    token = alice["access_token"]
    slug = alice["memberships"][0]["organization_slug"]
    res = client.post(
        f"/api/v1/workspaces/{slug}/members",
        json={"email": "nobody@example.com", "role": "agent"},
        headers=auth_header(token),
    )
    assert res.status_code == 404


def test_role_enforcement(client):
    alice = register(client, "alice-rbac@example.com", workspace="RBAC Co")
    bob = register(client, "bob-rbac@example.com")
    atoken = alice["access_token"]
    btoken = bob["access_token"]
    slug = alice["memberships"][0]["organization_slug"]

    client.post(
        f"/api/v1/workspaces/{slug}/members",
        json={"email": "bob-rbac@example.com", "role": "agent"},
        headers=auth_header(atoken),
    )

    members = client.get(f"/api/v1/workspaces/{slug}/members", headers=auth_header(atoken)).json()
    bob_member = [m for m in members if m["user"]["email"] == "bob-rbac@example.com"][0]
    bob_id = bob_member["user"]["id"]

    # agent cannot update workspace settings
    res = client.patch(
        f"/api/v1/workspaces/{slug}",
        json={"name": "Hacked"},
        headers=auth_header(btoken),
    )
    assert res.status_code == 403

    # agent cannot invite members
    res = client.post(
        f"/api/v1/workspaces/{slug}/members",
        json={"email": "someone@example.com", "role": "user"},
        headers=auth_header(btoken),
    )
    assert res.status_code == 403

    # promote bob to admin -> now allowed
    promoted = client.patch(
        f"/api/v1/workspaces/{slug}/members/{bob_id}",
        json={"role": "admin"},
        headers=auth_header(atoken),
    )
    assert promoted.status_code == 200
    res = client.patch(
        f"/api/v1/workspaces/{slug}",
        json={"name": "RBAC Co Updated"},
        headers=auth_header(btoken),
    )
    assert res.status_code == 200
    assert res.json()["name"] == "RBAC Co Updated"


def test_remove_member(client):
    alice = register(client, "alice-rm@example.com", workspace="RM Co")
    bob = register(client, "bob-rm@example.com")
    atoken = alice["access_token"]
    slug = alice["memberships"][0]["organization_slug"]

    client.post(
        f"/api/v1/workspaces/{slug}/members",
        json={"email": "bob-rm@example.com", "role": "user"},
        headers=auth_header(atoken),
    )
    members = client.get(f"/api/v1/workspaces/{slug}/members", headers=auth_header(atoken)).json()
    bob_id = [m for m in members if m["user"]["email"] == "bob-rm@example.com"][0]["user"]["id"]

    res = client.delete(
        f"/api/v1/workspaces/{slug}/members/{bob_id}",
        headers=auth_header(atoken),
    )
    assert res.status_code == 204

    members = client.get(f"/api/v1/workspaces/{slug}/members", headers=auth_header(atoken)).json()
    assert len(members) == 1


def test_only_owner_can_delete(client):
    alice = register(client, "alice-del@example.com", workspace="Del Co")
    bob = register(client, "bob-del@example.com")
    atoken = alice["access_token"]
    btoken = bob["access_token"]
    slug = alice["memberships"][0]["organization_slug"]

    client.post(
        f"/api/v1/workspaces/{slug}/members",
        json={"email": "bob-del@example.com", "role": "admin"},
        headers=auth_header(atoken),
    )

    denied = client.delete(f"/api/v1/workspaces/{slug}", headers=auth_header(btoken))
    assert denied.status_code == 403

    ok = client.delete(f"/api/v1/workspaces/{slug}", headers=auth_header(atoken))
    assert ok.status_code == 204

    gone = client.get(f"/api/v1/workspaces/{slug}", headers=auth_header(atoken))
    assert gone.status_code == 403


def test_activity_feed_and_stats(client):
    data = register(client, "act@example.com", workspace="Act Co")
    token = data["access_token"]
    slug = data["memberships"][0]["organization_slug"]

    feed = client.get(f"/api/v1/workspaces/{slug}/activity", headers=auth_header(token))
    assert feed.status_code == 200
    actions = [a["action"] for a in feed.json()]
    assert "workspace.created" in actions

    stats = client.get(f"/api/v1/workspaces/{slug}/stats", headers=auth_header(token))
    assert stats.status_code == 200
    body = stats.json()
    assert body["member_count"] == 1
    assert body["total_activity"] >= 1
    assert len(body["activity_7d"]) == 7


def test_super_admin_requires_flag(client):
    data = register(client, "sa@example.com")
    res = client.get("/api/v1/admin/overview", headers=auth_header(data["access_token"]))
    assert res.status_code == 403
