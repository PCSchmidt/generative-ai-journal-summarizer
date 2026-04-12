from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _login_token(user_id: str = "portfolio", password: str = "change-this-password") -> str:
    response = client.post("/api/auth/login", json={"user_id": user_id, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


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

    me = client.get("/api/auth/me", headers=_auth_headers(payload["access_token"]))
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

    token = _login_token()
    authorized = client.get("/api/auth/admin-placeholder", headers=_auth_headers(token))
    assert authorized.status_code == 200
    payload = authorized.json()
    assert payload["status"] == "work-in-progress"
    assert payload["manage_users"]["read_only"] is True
    assert len(payload["manage_users"]["rows"]) >= 1


def test_connect_token_guest_forbidden_and_login_allowed(monkeypatch):
    guest_session = client.post("/api/auth/session", json={})
    guest_token = guest_session.json()["access_token"]

    guest_connect = client.post(
        "/api/auth/connect-token",
        headers=_auth_headers(guest_token),
        json={"provider": "openrouter", "token": "sk-test-token-1234567890"},
    )
    assert guest_connect.status_code == 403

    def fake_connect(provider: str, token: str, owner_user_id: str, label=None):
        return {
            "token_id": "tok-test-1",
            "provider": provider,
            "label": label or "",
            "last4": token[-4:],
            "created_at": "2026-04-12T00:00:00Z",
        }

    monkeypatch.setattr(main.ai_service, "connect_user_token", fake_connect)

    login_token = _login_token()
    login_connect = client.post(
        "/api/auth/connect-token",
        headers=_auth_headers(login_token),
        json={"provider": "openrouter", "token": "sk-test-token-1234567890", "label": "test-key"},
    )
    assert login_connect.status_code == 200
    payload = login_connect.json()
    assert payload["status"] == "connected"
    assert payload["token"]["token_id"] == "tok-test-1"


def test_ai_reference_endpoints_contracts():
    diagnostics = client.get("/api/ai/diagnostics")
    assert diagnostics.status_code == 200
    d = diagnostics.json()
    assert "groq_configured" in d
    assert "hf_configured" in d
    assert "fallback_count" in d

    models = client.get("/api/ai/models")
    assert models.status_code == 200
    m = models.json()
    assert "models" in m
    assert "availability" in m

    tier = client.get("/api/ai/tier-info")
    assert tier.status_code == 200
    t = tier.json()
    assert t["status"] == "ok"
    assert isinstance(t["models"], list)
    assert any(item.get("key") == "groq-llama3-70b" for item in t["models"])


def test_sentiment_requires_auth_when_user_token_id_present():
    response = client.post(
        "/api/ai/sentiment",
        json={
            "text": "Test text for auth guard.",
            "task_type": "sentiment",
            "model": "groq-llama3-70b",
            "user_token_id": "tok-abc",
        },
    )
    assert response.status_code == 401


def test_sentiment_metadata_contract_with_mocked_provider(monkeypatch):
    async def fake_analyze_sentiment(text: str, model: str, user_token_id=None, owner_user_id=None):
        return {
            "result": "Mocked sentiment result",
            "confidence": 0.95,
            "sentiment": "positive",
            "model": model,
            "provider_used": "groq",
            "provider_requested": "groq",
            "fallback_used": False,
            "fallback_reason": None,
            "auth_source": "server_key",
        }

    monkeypatch.setattr(main.ai_service, "analyze_sentiment", fake_analyze_sentiment)

    response = client.post(
        "/api/ai/sentiment",
        json={"text": "This is a test entry with enough words for analysis.", "task_type": "sentiment", "model": "groq-llama3-70b"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["task_type"] == "sentiment"
    assert payload["result"] == "Mocked sentiment result"
    assert payload["metadata"]["provider_used"] == "groq"
    assert payload["metadata"]["fallback_used"] is False
