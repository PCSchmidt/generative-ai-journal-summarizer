from conftest import auth_headers, client, login_token


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


def test_connect_token_guest_forbidden_and_login_allowed(monkeypatch):
    guest_session = client.post("/api/auth/session", json={})
    guest_token = guest_session.json()["access_token"]

    guest_connect = client.post(
        "/api/auth/connect-token",
        headers=auth_headers(guest_token),
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

    monkeypatch.setattr("main.ai_service.connect_user_token", fake_connect)

    token = login_token()
    login_connect = client.post(
        "/api/auth/connect-token",
        headers=auth_headers(token),
        json={"provider": "openrouter", "token": "sk-test-token-1234567890", "label": "test-key"},
    )
    assert login_connect.status_code == 200
    payload = login_connect.json()
    assert payload["status"] == "connected"
    assert payload["token"]["token_id"] == "tok-test-1"
