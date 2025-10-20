from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_login_wrong_password_should_fail():
    resp = client.post("/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"
