def test_root_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["status"] == "ok"
    assert data["service"] == "Safe NL-to-SQL Analytics Assistant"


def test_api_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "API is healthy"
    assert data["data"]["status"] == "ok"


def test_api_ready_endpoint(client):
    response = client.get("/api/ready")

    assert response.status_code in [200, 503]

    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Service readiness checked"
    assert "checks" in data["data"]
    assert "database" in data["data"]["checks"]
    assert "allowed_schema" in data["data"]["checks"]
    assert "openai_api_key" in data["data"]["checks"]