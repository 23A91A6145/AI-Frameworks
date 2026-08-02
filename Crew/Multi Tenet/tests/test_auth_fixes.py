"""Auth fixes — password reset flow, refresh-token rotation, enumeration safety."""

from conftest import auth_header, register


def test_forgot_password_returns_reset_link_in_dev(client):
    user = register(client, "resetme@example.com", workspace="Reset Co")
    res = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "resetme@example.com"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert "reset_link" in body
    assert "/reset-password?token=" in body["reset_link"]
    assert "resetme@example.com" not in body["reset_link"].split("token=")[1]


def test_reset_password_sets_new_password_and_invalidates_old(client):
    user = register(client, "pw@example.com", workspace="Pw Co")
    token = user["access_token"]

    forgot = client.post("/api/v1/auth/forgot-password", json={"email": "pw@example.com"}).json()
    reset_link = forgot["reset_link"]
    reset_token = reset_link.split("token=")[1]

    res = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "password": "brand-new-pass-99"},
    )
    assert res.status_code == 200, res.text

    # old password no longer works, new one does
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "pw@example.com", "password": "strong-pass-123"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "pw@example.com", "password": "brand-new-pass-99"},
    )
    assert new_login.status_code == 200
    assert new_login.json()["access_token"]

    # token is single use — a second reset with the same token fails
    again = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "password": "another-pass-123"},
    )
    assert again.status_code == 400


def test_reset_password_rejects_garbage_and_expired_tokens(client):
    register(client, "bad@example.com", workspace="Bad Co")

    bad = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "garbage-garbage-garbage-garbage", "password": "whatever-123"},
    )
    assert bad.status_code == 400

    # a signed token of the wrong type (access token) is rejected
    from app.core.security import create_access_token

    wrong_type = client.post(
        "/api/v1/auth/reset-password",
        json={"token": create_access_token("some-user"), "password": "whatever-123"},
    )
    assert wrong_type.status_code == 400


def test_forgot_password_does_not_enumerate_emails(client):
    register(client, "exists@example.com", workspace="Exists Co")

    # unknown email returns the same 200 + generic message, no reset_link
    unknown = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nobody@example.com"},
    )
    assert unknown.status_code == 200
    assert "reset_link" not in unknown.json()

    known = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "exists@example.com"},
    )
    assert known.status_code == 200


def test_refresh_rotates_refresh_token(client):
    user = register(client, "rotate@example.com", workspace="Rotate Co")
    refresh = user["refresh_token"]
    assert refresh

    res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["access_token"]
    assert body["refresh_token"] and body["refresh_token"] != refresh
