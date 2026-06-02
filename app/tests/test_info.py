def test_api_info_endpoint(client):
    response = client.get("/api/info")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Service information fetched successfully"

    info = data["data"]

    assert info["service"] == "Safe NL-to-SQL Analytics Assistant"
    assert info["version"] == "1.0.0"
    assert info["environment"] in ["development", "testing", "production"]
    assert info["database"] == "SQLite"
    assert info["llm_provider"] == "OpenAI"
    assert "openai_model" in info
    assert info["safety_mode"] == "strict"
    assert "rate_limiting_enabled" in info
    assert "api_key_auth_enabled" in info
    assert "max_query_rows" in info
    assert "max_query_seconds" in info