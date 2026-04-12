from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login_token(user_id: str = "portfolio", password: str = "change-this-password") -> str:
    response = client.post("/api/auth/login", json={"user_id": user_id, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]
