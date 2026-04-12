from conftest import client


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

    monkeypatch.setattr("main.ai_service.analyze_sentiment", fake_analyze_sentiment)

    response = client.post(
        "/api/ai/sentiment",
        json={
            "text": "This is a test entry with enough words for analysis.",
            "task_type": "sentiment",
            "model": "groq-llama3-70b",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["task_type"] == "sentiment"
    assert payload["result"] == "Mocked sentiment result"
    assert payload["metadata"]["provider_used"] == "groq"
    assert payload["metadata"]["fallback_used"] is False
