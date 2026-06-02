from unittest.mock import patch


def test_query_endpoint_success_dry_run(client):
    mocked_result = {
        "question": "Show employees in Engineering",
        "generated_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
        "final_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
        "explanation": "Shows employee names.",
        "confidence": 0.95,
        "dry_run": True,
        "safety": {
            "is_safe": True,
            "blocked": False,
            "original_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
            "final_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
            "blocked_reason": None,
            "checks_passed": ["select_only", "limit_enforced"],
            "detected_tables": ["employees"],
            "detected_columns": ["first_name", "last_name"],
        },
        "execution": None,
    }

    with patch(
        "app.api.query_controller.service_container.nl_to_sql_service.process_question",
        return_value=mocked_result,
    ):
        response = client.post(
            "/api/query",
            json={
                "question": "Show employees in Engineering",
                "dry_run": True,
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Query processed successfully"
    assert data["data"]["dry_run"] is True
    assert data["data"]["safety"]["blocked"] is False
    assert data["data"]["execution"] is None


def test_query_endpoint_success_execution(client):
    mocked_result = {
        "question": "Show employees in Engineering",
        "generated_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
        "final_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
        "explanation": "Shows employee names.",
        "confidence": 0.95,
        "dry_run": False,
        "safety": {
            "is_safe": True,
            "blocked": False,
            "original_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
            "final_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
            "blocked_reason": None,
            "checks_passed": ["select_only", "limit_enforced"],
            "detected_tables": ["employees"],
            "detected_columns": ["first_name", "last_name"],
        },
        "execution": {
            "columns": ["first_name", "last_name"],
            "rows": [
                {
                    "first_name": "Aarav",
                    "last_name": "Menon",
                }
            ],
            "row_count": 1,
            "execution_time_ms": 2.5,
        },
    }

    with patch(
        "app.api.query_controller.service_container.nl_to_sql_service.process_question",
        return_value=mocked_result,
    ):
        response = client.post(
            "/api/query",
            json={
                "question": "Show employees in Engineering",
                "dry_run": False,
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["dry_run"] is False
    assert data["data"]["execution"]["row_count"] == 1


def test_query_endpoint_blocked_sql_returns_400(client):
    mocked_result = {
        "question": "Delete all employees",
        "generated_sql": "DELETE FROM employees",
        "final_sql": None,
        "explanation": "Attempts to delete employees.",
        "confidence": 0.9,
        "dry_run": True,
        "safety": {
            "is_safe": False,
            "blocked": True,
            "original_sql": "DELETE FROM employees",
            "final_sql": None,
            "blocked_reason": "Only SELECT queries are allowed",
            "checks_passed": [],
            "detected_tables": [],
            "detected_columns": [],
        },
        "execution": None,
    }

    with patch(
        "app.api.query_controller.service_container.nl_to_sql_service.process_question",
        return_value=mocked_result,
    ):
        response = client.post(
            "/api/query",
            json={
                "question": "Delete all employees",
                "dry_run": True,
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert data["error_code"] == "REQUEST_BLOCKED_BY_SAFETY"
    assert data["details"]["safety"]["blocked"] is True


def test_query_endpoint_rejects_missing_question(client):
    response = client.post(
        "/api/query",
        json={
            "dry_run": True,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert data["error_code"] == "REQUEST_VALIDATION_ERROR"


def test_query_endpoint_rejects_short_question(client):
    response = client.post(
        "/api/query",
        json={
            "question": "Hi",
            "dry_run": True,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert data["error_code"] == "REQUEST_VALIDATION_ERROR"

def test_query_history_endpoint_returns_items(client):
    response = client.get("/api/query-history?limit=5")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Query history fetched successfully"
    assert "items" in data["data"]
    assert "count" in data["data"]
    assert "limit" in data["data"]
    assert data["data"]["limit"] == 5


def test_query_history_endpoint_caps_large_limit(client):
    response = client.get("/api/query-history?limit=999")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["limit"] == 100


def test_query_history_endpoint_handles_invalid_limit(client):
    response = client.get("/api/query-history?limit=-5")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["limit"] == 20