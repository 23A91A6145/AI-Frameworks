"""Volume 5 tests — platform admin console, widget config, CLI tooling."""

from conftest import auth_header, register


def _promote(client, email: str, token: str):
    """Make a user a super admin directly via the ORM (mirrors scripts.create_superadmin)."""
    from sqlalchemy.orm import Session

    def grab(db: Session):
        from app.models import User

        user = db.query(User).filter(User.email == email).one()
        user.is_super_admin = True
        db.commit()
        return user

    db = next(client.app.dependency_overrides[next(iter(client.app.dependency_overrides))]())
    grab(db)


def test_superadmin_guard_blocks_non_admins(client):
    user = register(client, "member@example.com", workspace="Member Co")
    token = user["access_token"]

    res = client.get("/api/v1/admin/overview", headers=auth_header(token))
    assert res.status_code == 403
    assert "Super admin" in res.json()["detail"]

    res = client.get("/api/v1/admin/workspaces", headers=auth_header(token))
    assert res.status_code == 403


def test_superadmin_promotion_via_cli_logic(client):
    from scripts.create_superadmin import promote

    user = register(client, "boss@example.com", workspace="Boss Inc")
    token = user["access_token"]

    def session_factory():
        return next(client.app.dependency_overrides[next(iter(client.app.dependency_overrides))]())

    promoted = promote("boss@example.com", session_factory=session_factory)
    assert promoted.is_super_admin is True

    res = client.get("/api/v1/admin/overview", headers=auth_header(token))
    assert res.status_code == 200
    body = res.json()
    assert body["users"] >= 1
    assert body["workspaces"] >= 1
    assert {"free", "pro", "enterprise"}.issubset(body["plans"].keys())

    res = client.get("/api/v1/admin/workspaces", headers=auth_header(token))
    assert res.status_code == 200
    slugs = [w["slug"] for w in res.json()]
    assert "boss-inc" in slugs
    assert {"name", "slug", "plan", "member_count"}.issubset(res.json()[0].keys())


def test_widget_config_endpoint(client):
    user = register(client, "widget@example.com", workspace="Widget Co")
    token = user["access_token"]
    slug = user["memberships"][0]["organization_slug"]

    # config before enable
    res = client.get(f"/api/v1/workspaces/{slug}/widget/config", headers=auth_header(token))
    assert res.status_code == 200
    cfg = res.json()
    assert cfg["widget_enabled"] is False
    assert cfg["widget_token"] == ""
    assert f"/api/v1/public/{slug}/chat" in cfg["widget_url"]

    # enable → token generated, config reflects it
    res = client.post(f"/api/v1/workspaces/{slug}/widget/enable", headers=auth_header(token))
    assert res.status_code == 200
    enabled_token = res.json()["token"]

    res = client.get(f"/api/v1/workspaces/{slug}/widget/config", headers=auth_header(token))
    cfg = res.json()
    assert cfg["widget_enabled"] is True
    assert cfg["widget_token"] == enabled_token

    # rotate → new token
    res = client.post(f"/api/v1/workspaces/{slug}/widget/rotate", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json()["token"] != enabled_token
    cfg = client.get(
        f"/api/v1/workspaces/{slug}/widget/config", headers=auth_header(token)
    ).json()
    assert cfg["widget_token"] == res.json()["token"]

    # disable → token revoked
    res = client.post(f"/api/v1/workspaces/{slug}/widget/disable", headers=auth_header(token))
    assert res.status_code == 200
    cfg = client.get(
        f"/api/v1/workspaces/{slug}/widget/config", headers=auth_header(token)
    ).json()
    assert cfg["widget_enabled"] is False

    # disabled widget rejects public chat (with the previously-valid token)
    chat = client.post(
        f"/api/v1/public/{slug}/chat",
        json={"message": "hi"},
        headers={"X-Widget-Token": cfg["widget_token"]},
    )
    assert chat.status_code == 403
