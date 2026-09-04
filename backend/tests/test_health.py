def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["service"] == "smart-education-backend"
    assert body["version"] == "1.0.0"


def test_docs_available(client):
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_available(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert "/health" in spec["paths"]
    assert "/ready" in spec["paths"]
    assert "/api/courses" in spec["paths"]
