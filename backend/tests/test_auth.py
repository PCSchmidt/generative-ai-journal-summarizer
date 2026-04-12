from conftest import auth_headers, client, login_token


def test_root_and_health_endpoints():
    root = client.get("/")
    assert root.status_code == 200
    assert "API is running" in root.json()["message"]

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"


def test_auth_session_and_me_contract():
    session = client.post("/api/auth/session", json={})
    assert session.status_code == 200
    payload = session.json()
    assert payload["status"] == "ok"
    assert payload["guest"] is True
    assert payload["access_token"]

    me = client.get("/api/auth/me", headers=auth_headers(payload["access_token"]))
    assert me.status_code == 200
    me_payload = me.json()
    assert me_payload["status"] == "ok"
    assert me_payload["guest"] is True
    assert me_payload["user_id"].startswith("guest-")


def test_login_success_and_failure_paths():
    success = client.post("/api/auth/login", json={"user_id": "portfolio", "password": "change-this-password"})
    assert success.status_code == 200
    success_payload = success.json()
    assert success_payload["guest"] is False
    assert success_payload["access_token"]

    failure = client.post("/api/auth/login", json={"user_id": "portfolio", "password": "wrong-password"})
    assert failure.status_code == 401


def test_admin_placeholder_requires_auth_and_returns_read_only_table():
    unauthorized = client.get("/api/auth/admin-placeholder")
    assert unauthorized.status_code == 401

    token = login_token()
    authorized = client.get("/api/auth/admin-placeholder", headers=auth_headers(token))
    assert authorized.status_code == 200
    payload = authorized.json()
    assert payload["status"] == "work-in-progress"
    assert payload["manage_users"]["read_only"] is True
    assert len(payload["manage_users"]["rows"]) >= 1
