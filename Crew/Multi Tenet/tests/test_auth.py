from conftest import auth_header, register


def test_register_creates_user_and_workspace(client):
    data = register(client, "alice@example.com", workspace="Acme Inc")
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user"]["email"] == "alice@example.com"
    assert data["memberships"][0]["organization_name"] == "Acme Inc"
    assert data["memberships"][0]["role"] == "owner"


def test_register_without_workspace(client):
    data = register(client, "bob@example.com")
    assert data["memberships"] == []


def test_register_duplicate_email(client):
    register(client, "dup@example.com", workspace="Dup")
    res = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Dup", "email": "dup@example.com", "password": "strong-pass-123"},
    )
    assert res.status_code == 409


def test_register_weak_password(client):
    res = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Weak", "email": "weak@example.com", "password": "short"},
    )
    assert res.status_code == 422


def test_login_success_and_wrong_password(client):
    register(client, "carol@example.com", workspace="Carol Co")
    ok = client.post(
        "/api/v1/auth/login",
        json={"email": "carol@example.com", "password": "strong-pass-123"},
    )
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = client.post(
        "/api/v1/auth/login",
        json={"email": "carol@example.com", "password": "wrong-password"},
    )
    assert bad.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_user(client):
    data = register(client, "dave@example.com")
    res = client.get("/api/v1/auth/me", headers=auth_header(data["access_token"]))
    assert res.status_code == 200
    assert res.json()["email"] == "dave@example.com"


def test_refresh_token_issues_new_access(client):
    data = register(client, "erin@example.com")
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": data["refresh_token"]})
    assert res.status_code == 200
    assert res.json()["access_token"]


def test_access_token_rejected_for_refresh(client):
    data = register(client, "frank@example.com")
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": data["access_token"]})
    assert res.status_code == 401
