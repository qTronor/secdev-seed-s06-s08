from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_index_page_renders_and_escapes_by_default():
    resp = client.get("/")
    assert resp.status_code == 200
    html = client.get("/echo", params={"msg": "<b>bold</b>"}).text
    assert "<b>bold</b>" not in html
    assert "&lt;b&gt;bold&lt;/b&gt;" in html
