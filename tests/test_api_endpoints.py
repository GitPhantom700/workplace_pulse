"""
Tier 2 Dynamic REST API & Contract Tests
Executes dynamic HTTP requests against the FastAPI application to verify status codes:
- 200 OK for valid interactions
- 401 Unauthorized for missing/invalid auth tokens
- 422 Unprocessable Entity for schema violations
- Static asset delivery and audit persistence
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


# ---------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------

def test_api_health_returns_200(client):
    """Verify GET /api/health returns 200 OK with healthy status payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "WorkplacePulse"
    assert "timestamp" in data
    assert "environment" in data


# ---------------------------------------------------------
# GET /api/scenarios
# ---------------------------------------------------------

def test_api_scenarios_returns_200_and_catalog(client):
    """Verify GET /api/scenarios returns 200 OK with all 3 enterprise presets."""
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "scenarios" in data
    assert len(data["scenarios"]) == 3

    scenario_ids = [s["id"] for s in data["scenarios"]]
    assert "saas_finops" in scenario_ids
    assert "hardware_lifecycle" in scenario_ids
    assert "itsm_surge" in scenario_ids


# ---------------------------------------------------------
# POST /api/scenarios/seed
# ---------------------------------------------------------

def test_post_scenarios_seed_valid_saas_finops(client):
    """Verify POST /api/scenarios/seed with saas_finops returns 200 OK with telemetry payload."""
    response = client.post("/api/scenarios/seed", json={"scenario_id": "saas_finops"})
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "saas_finops"
    assert "saas_metrics" in data
    assert len(data["saas_metrics"]) > 0
    assert "chart_data" in data
    assert "grounding_context" in data


def test_post_scenarios_seed_valid_hardware_lifecycle(client):
    """Verify POST /api/scenarios/seed with hardware_lifecycle returns 200 OK."""
    response = client.post("/api/scenarios/seed", json={"scenario_id": "hardware_lifecycle"})
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "hardware_lifecycle"
    assert "hardware_metrics" in data
    assert len(data["hardware_metrics"]) > 0


def test_post_scenarios_seed_valid_itsm_surge(client):
    """Verify POST /api/scenarios/seed with itsm_surge returns 200 OK."""
    response = client.post("/api/scenarios/seed", json={"scenario_id": "itsm_surge"})
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "itsm_surge"
    assert "itsm_metrics" in data
    assert len(data["itsm_metrics"]) > 0


def test_post_scenarios_seed_invalid_body_returns_422(client):
    """Verify POST /api/scenarios/seed with invalid body returns 422 Unprocessable Entity."""
    response = client.post("/api/scenarios/seed", json={"wrong_attribute": "saas_finops"})
    assert response.status_code == 422


def test_post_scenarios_seed_unknown_scenario_returns_404(client):
    """Verify POST /api/scenarios/seed with unknown scenario_id returns 404 Not Found."""
    response = client.post("/api/scenarios/seed", json={"scenario_id": "non_existent_scenario_123"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------
# POST /api/forecast/chat
# ---------------------------------------------------------

def test_post_forecast_chat_missing_auth_header_returns_401_or_403(client):
    """Verify POST /api/forecast/chat with missing Authorization header is rejected (401 or 403)."""
    payload = {
        "scenario_id": "saas_finops",
        "message": "Analyze waste.",
        "history": []
    }
    response = client.post("/api/forecast/chat", json=payload)
    # FastAPI HTTPBearer returns 403 if header is missing or 401 depending on config
    assert response.status_code in [401, 403]


def test_post_forecast_chat_unknown_scenario_returns_404(client):
    """Verify POST /api/forecast/chat with unknown scenario_id returns 404 Not Found."""
    headers = {"Authorization": "Bearer demo-engineer-123"}
    payload = {
        "scenario_id": "unknown_scenario_999",
        "message": "Analyze spend.",
        "history": []
    }
    response = client.post("/api/forecast/chat", json=payload, headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_post_forecast_chat_invalid_token_returns_401(client):
    """Verify POST /api/forecast/chat with invalid Bearer token returns 401 Unauthorized."""
    headers = {"Authorization": "Bearer invalid-tampered-token-12345"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "Analyze waste.",
        "history": []
    }
    with patch("firebase_admin.auth.verify_id_token", side_effect=Exception("Invalid signature")):
        response = client.post("/api/forecast/chat", json=payload, headers=headers)
        assert response.status_code == 401


def test_post_forecast_chat_valid_demo_token_returns_200(client):
    """Verify POST /api/forecast/chat with valid demo Bearer token returns 200 OK and response."""
    headers = {"Authorization": "Bearer demo-engineer-chandraprakash"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "What is our highest waste software license?",
        "history": []
    }

    with patch("main.generate_multi_turn_forecast", return_value="Figma Enterprise is the highest waste."):
        with patch("main.save_forecast_log", return_value=True):
            response = client.post("/api/forecast/chat", json=payload, headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["scenario_id"] == "saas_finops"
            assert data["user_id"] == "demo_engineer_chandraprakash"
            assert "Figma Enterprise" in data["response"]
            assert "timestamp" in data


def test_post_forecast_chat_empty_message_returns_422(client):
    """Verify POST /api/forecast/chat with empty message returns 422 Unprocessable Entity."""
    headers = {"Authorization": "Bearer demo-engineer-123"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "   ",
        "history": []
    }
    response = client.post("/api/forecast/chat", json=payload, headers=headers)
    assert response.status_code == 422


# ---------------------------------------------------------
# GET / (Root Frontend Asset)
# ---------------------------------------------------------

def test_get_root_serves_frontend_or_status(client):
    """Verify GET / responds with 200 OK serving index.html or welcome JSON."""
    response = client.get("/")
    assert response.status_code == 200


# ---------------------------------------------------------
# Audit Persistence Integration
# ---------------------------------------------------------

def test_forecast_chat_triggers_audit_log_save(client):
    """Verify successful forecast chat calls save_forecast_log with user metadata."""
    headers = {"Authorization": "Bearer demo-lead-user"}
    payload = {
        "scenario_id": "itsm_surge",
        "message": "Plan emergency shifts.",
        "history": []
    }

    with patch("main.generate_multi_turn_forecast", return_value="Shift recommendations generated."):
        with patch("main.save_forecast_log") as mock_save:
            mock_save.return_value = True
            response = client.post("/api/forecast/chat", json=payload, headers=headers)
            assert response.status_code == 200
            mock_save.assert_called_once()
            call_kwargs = mock_save.call_args.kwargs
            assert call_kwargs.get("scenario_id") == "itsm_surge"
            assert call_kwargs.get("user_prompt") == "Plan emergency shifts."


# ---------------------------------------------------------
# GET /api/runbooks & POST /api/forecast/recommendations Auth Tests
# ---------------------------------------------------------

def test_get_runbooks_missing_auth_header_returns_401(client):
    """Verify GET /api/runbooks without Authorization header returns 401 Unauthorized."""
    response = client.get("/api/runbooks")
    assert response.status_code == 401


def test_get_runbooks_invalid_token_returns_401(client):
    """Verify GET /api/runbooks with invalid/unrecognized token returns 401 Unauthorized."""
    response = client.get("/api/runbooks", headers={"Authorization": "Bearer junk-token-999"})
    assert response.status_code == 401


def test_get_runbooks_valid_demo_token_returns_200(client):
    """Verify GET /api/runbooks with valid demo token returns 200 OK and catalog list."""
    response = client.get("/api/runbooks", headers={"Authorization": "Bearer demo-engineer-123"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_post_recommendations_missing_auth_header_returns_401(client):
    """Verify POST /api/forecast/recommendations without Authorization header returns 401 Unauthorized."""
    response = client.post("/api/forecast/recommendations", json={"scenario_id": "saas_finops"})
    assert response.status_code == 401


def test_post_recommendations_invalid_token_returns_401(client):
    """Verify POST /api/forecast/recommendations with invalid token returns 401 Unauthorized."""
    response = client.post(
        "/api/forecast/recommendations",
        json={"scenario_id": "saas_finops"},
        headers={"Authorization": "Bearer junk-token-999"}
    )
    assert response.status_code == 401


def test_post_recommendations_valid_demo_token_returns_200(client):
    """Verify POST /api/forecast/recommendations with valid demo token returns 200 OK and recommendations."""
    response = client.post(
        "/api/forecast/recommendations",
        json={"scenario_id": "saas_finops"},
        headers={"Authorization": "Bearer demo-engineer-123"}
    )
    assert response.status_code == 200
    assert "recommendations" in response.json()

