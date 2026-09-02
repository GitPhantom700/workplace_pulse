"""
Adversarial Dynamic Endpoint & Auth Stress Test Suite (Challenger 1)
Empirically tests failure modes, edge cases, auth bypass attempts, null byte injections,
boundary violations, CORS policy enforcement, and rapid burst resilience across FastAPI endpoints.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """FastAPI TestClient fixture for hermetic dynamic testing."""
    return TestClient(app)


# ==============================================================================
# SECTION 1: AUTHENTICATION & TOKEN ADVERSARIAL CHALLENGES
# ==============================================================================

def test_adv_missing_auth_header(client):
    """
    Adversarial Vector 1.1: Missing Authorization Header.
    Protected endpoint POST /api/forecast/chat MUST reject unauthenticated requests (401 or 403).
    """
    payload = {
        "scenario_id": "saas_finops",
        "message": "Attempt unauthenticated forecast generation.",
        "history": []
    }
    response = client.post("/api/forecast/chat", json=payload)
    assert response.status_code in [401, 403], f"Expected 401/403 for missing auth, got {response.status_code}"


def test_adv_malformed_auth_headers(client):
    """
    Adversarial Vector 1.2: Malformed Authorization Headers.
    Any non-conforming Bearer header must be rejected with 401 or 403.
    """
    malformed_headers = [
        "",                             # Empty string
        "Bearer",                       # Scheme only, missing token
        "Bearer ",                      # Trailing whitespace only
        "Bearer   ",                    # Multiple spaces only
        "Basic dXNlcjpwYXNz",          # Invalid scheme (Basic auth)
        "Token abcdef123456",           # Invalid scheme (Token auth)
        "Digest username=\"admin\"",    # Invalid scheme (Digest auth)
        "Bearer token1 token2 extra",   # Extra token components
        "Bearer: demo-engineer-123",    # Malformed colon in header scheme
    ]
    payload = {
        "scenario_id": "saas_finops",
        "message": "Analyze waste.",
        "history": []
    }
    for header in malformed_headers:
        response = client.post("/api/forecast/chat", json=payload, headers={"Authorization": header})
        assert response.status_code in [401, 403], f"Header '{header}' got status {response.status_code}"


def test_adv_expired_or_invalid_jwt_token(client):
    """
    Adversarial Vector 1.3: Expired / Forged Firebase JWT.
    Verify 401 Unauthorized response with WWW-Authenticate header when Firebase Admin rejects JWT.
    """
    headers = {"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.forged.signature"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "Analyze waste.",
        "history": []
    }
    with patch("firebase_admin.auth.verify_id_token", side_effect=Exception("Firebase ID token has expired")):
        response = client.post("/api/forecast/chat", json=payload, headers=headers)
        assert response.status_code == 401
        assert "Invalid or Expired Authentication Token" in response.json().get("detail", "")
        assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_adv_demo_token_rejected_when_demo_mode_disabled(client, monkeypatch):
    """
    Adversarial Vector 1.4: Forged 'demo-' Tokens when DEMO_MODE is disabled.
    When DEMO_MODE=false, any 'demo-' prefixed token MUST be rejected with 401 Unauthorized.
    """
    demo_disabled_values = ["false", "0", "no", "False", "disabled", "off"]
    payload = {
        "scenario_id": "saas_finops",
        "message": "Attempt demo sandbox bypass in production mode.",
        "history": []
    }
    for env_val in demo_disabled_values:
        monkeypatch.setenv("DEMO_MODE", env_val)
        headers = {"Authorization": "Bearer demo-attacker-privilege-escalation"}
        response = client.post("/api/forecast/chat", json=payload, headers=headers)
        assert response.status_code == 401, f"Expected 401 when DEMO_MODE={env_val}, got {response.status_code}"
        data = response.json()
        assert "Demo mode authentication is disabled" in data.get("detail", "")
        assert response.headers.get("WWW-Authenticate") == "Bearer"


def test_adv_demo_token_case_sensitivity(client):
    """
    Adversarial Vector 1.5: Case Sensitivity in Demo Token Prefix.
    'DEMO-' (uppercase) must NOT match token.startswith('demo-') and must route to Firebase JWT verification.
    """
    headers = {"Authorization": "Bearer DEMO-UPPERCASE-TOKEN"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "Analyze waste.",
        "history": []
    }
    with patch("firebase_admin.auth.verify_id_token", side_effect=Exception("Invalid token format")):
        response = client.post("/api/forecast/chat", json=payload, headers=headers)
        assert response.status_code == 401


# ==============================================================================
# SECTION 2: BOUNDARY & MALICIOUS INPUTS ON /api/scenarios/seed
# ==============================================================================

def test_adv_seed_unrecognized_scenario_ids(client):
    """
    Adversarial Vector 2.1: Unrecognized Scenario IDs on POST /api/scenarios/seed.
    Unknown scenario IDs, path traversals, SQLi, and XSS payloads must return 404 Not Found.
    """
    invalid_ids = [
        "unrecognized_scenario_preset",
        "saas_finops_v2",
        "hardware",
        "",
        "   ",
        "../../etc/passwd",
        "saas_finops; DROP TABLE logs; --",
        "<script>alert('xss')</script>",
        "saas_finops\x00extra",
        "A" * 10000,
    ]
    for inv_id in invalid_ids:
        response = client.post("/api/scenarios/seed", json={"scenario_id": inv_id})
        assert response.status_code == 404, f"Scenario ID '{inv_id}' got status {response.status_code}"
        assert f"Scenario '{inv_id}' not found." in response.json().get("detail", "")


def test_adv_seed_schema_violations(client):
    """
    Adversarial Vector 2.2: Schema Violations on POST /api/scenarios/seed.
    Malformed JSON bodies violating Pydantic schema must return 422 Unprocessable Entity.
    """
    malformed_payloads = [
        {},                                         # Empty object
        {"wrong_key": "saas_finops"},               # Missing required scenario_id field
        {"scenario_id": None},                     # Null value
        {"scenario_id": ["saas_finops"]},           # Array type instead of string
        {"scenario_id": {"nested": "value"}},       # Nested dictionary
    ]
    for payload in malformed_payloads:
        response = client.post("/api/scenarios/seed", json=payload)
        assert response.status_code == 422, f"Payload {payload} got status {response.status_code}"


def test_adv_seed_non_json_body(client):
    """
    Adversarial Vector 2.3: Non-JSON raw bytes payload.
    Sending raw non-JSON bytes must return 422 Unprocessable Entity.
    """
    response = client.post(
        "/api/scenarios/seed",
        content=b"raw-unparsed-binary-data",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


# ==============================================================================
# SECTION 3: BOUNDARY, NULL-BYTE & INJECTION STRESS ON /api/forecast/chat
# ==============================================================================

def test_adv_forecast_chat_unrecognized_scenario_id(client):
    """
    Adversarial Vector 3.1: Valid Auth but Unrecognized Scenario ID on Chat.
    Must return 404 Not Found.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "non_existent_preset",
        "message": "Analyze system.",
        "history": []
    }
    response = client.post("/api/forecast/chat", json=payload, headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json().get("detail", "").lower()


def test_adv_forecast_chat_null_byte_sanitization(client):
    """
    Adversarial Vector 3.2: Null Byte Injections in User Prompt.
    Null bytes ('\\x00') must be automatically stripped and the cleaned prompt processed.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "Calculate\x00 potential \x00annual \x00savings.",
        "history": []
    }
    with patch("main.generate_multi_turn_forecast", return_value="AI Response") as mock_gen:
        with patch("main.save_forecast_log", return_value=True):
            response = client.post("/api/forecast/chat", json=payload, headers=headers)
            assert response.status_code == 200
            assert mock_gen.call_args.kwargs.get("user_message") == "Calculate potential annual savings."


def test_adv_forecast_chat_pure_null_bytes_rejected(client):
    """
    Adversarial Vector 3.3: Pure Null Bytes in Prompt.
    Prompts consisting solely of null bytes ('\\x00\\x00\\x00') strip to empty and must return 422.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "\x00\x00\x00\x00\x00",
        "history": []
    }
    response = client.post("/api/forecast/chat", json=payload, headers=headers)
    assert response.status_code == 422


def test_adv_forecast_chat_null_bytes_in_history_sanitized(client):
    """
    Adversarial Vector 3.4: Null Bytes in Conversation History Content.
    Null bytes inside history items must be stripped cleanly.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "Followup prompt",
        "history": [
            {"role": "user", "content": "Prior\x00 user\x00 query"},
            {"role": "model", "content": "Prior\x00 model\x00 answer"}
        ]
    }
    with patch("main.generate_multi_turn_forecast", return_value="AI Followup") as mock_gen:
        with patch("main.save_forecast_log", return_value=True):
            response = client.post("/api/forecast/chat", json=payload, headers=headers)
            assert response.status_code == 200
            history_passed = mock_gen.call_args.kwargs.get("chat_history")
            assert history_passed[0]["content"] == "Prior user query"
            assert history_passed[1]["content"] == "Prior model answer"


def test_adv_forecast_chat_history_pure_null_bytes_rejected(client):
    """
    Adversarial Vector 3.5: Pure Null Bytes in History Item Content.
    History item with only null bytes strips to empty string and must return 422.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "Valid prompt",
        "history": [{"role": "user", "content": "\x00\x00\x00"}]
    }
    response = client.post("/api/forecast/chat", json=payload, headers=headers)
    assert response.status_code == 422


def test_adv_forecast_chat_4000_char_boundary_accepted(client):
    """
    Adversarial Vector 3.6: Prompt of Exactly 4000 Characters (Upper Boundary).
    Must be accepted (200 OK).
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "X" * 4000,
        "history": []
    }
    with patch("main.generate_multi_turn_forecast", return_value="Accepted"):
        with patch("main.save_forecast_log", return_value=True):
            response = client.post("/api/forecast/chat", json=payload, headers=headers)
            assert response.status_code == 200


def test_adv_forecast_chat_4001_char_boundary_rejected(client):
    """
    Adversarial Vector 3.7: Prompt of 4001 Characters (Boundary Violation).
    Must be rejected with 422 Unprocessable Entity.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "X" * 4001,
        "history": []
    }
    response = client.post("/api/forecast/chat", json=payload, headers=headers)
    assert response.status_code == 422


def test_adv_forecast_chat_100k_char_dos_payload_rejected(client):
    """
    Adversarial Vector 3.8: Massive 100,000-character Oversized Prompt.
    Must be rejected immediately with 422 Unprocessable Entity.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "A" * 100000,
        "history": []
    }
    response = client.post("/api/forecast/chat", json=payload, headers=headers)
    assert response.status_code == 422


def test_adv_forecast_chat_history_content_4001_chars_rejected(client):
    """
    Adversarial Vector 3.9: History Turn Exceeding 4000 Characters.
    Must return 422 Unprocessable Entity.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    payload = {
        "scenario_id": "saas_finops",
        "message": "Valid prompt",
        "history": [{"role": "user", "content": "M" * 4001}]
    }
    response = client.post("/api/forecast/chat", json=payload, headers=headers)
    assert response.status_code == 422


def test_adv_forecast_chat_invalid_roles_rejected(client):
    """
    Adversarial Vector 3.10: Disallowed History Roles (Privilege Injections).
    Only 'user', 'model', and 'assistant' are permitted; all others must return 422.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    invalid_roles = ["system", "admin", "root", "bot", "attacker", ""]
    for inv_role in invalid_roles:
        payload = {
            "scenario_id": "saas_finops",
            "message": "Analyze waste.",
            "history": [{"role": inv_role, "content": "Instruction override"}]
        }
        response = client.post("/api/forecast/chat", json=payload, headers=headers)
        assert response.status_code == 422, f"Role '{inv_role}' got status {response.status_code}"


def test_adv_forecast_chat_large_history_array(client):
    """
    Adversarial Vector 3.11: 100 Conversation History Turns.
    Verify high turn-count payload does not cause recursion errors, unhandled crashes, or timeouts.
    """
    headers = {"Authorization": "Bearer demo-engineer-valid"}
    large_history = [
        {"role": "user" if i % 2 == 0 else "model", "content": f"Turn {i} summary context"}
        for i in range(100)
    ]
    payload = {
        "scenario_id": "saas_finops",
        "message": "Summarize full multi-turn discussion.",
        "history": large_history
    }
    with patch("main.generate_multi_turn_forecast", return_value="Multi-turn forecast generated successfully."):
        with patch("main.save_forecast_log", return_value=True):
            response = client.post("/api/forecast/chat", json=payload, headers=headers)
            assert response.status_code == 200
            assert response.json()["status"] == "success"


# ==============================================================================
# SECTION 4: SECURITY HEADERS & CORS HARDENING
# ==============================================================================

def test_adv_security_headers_present_on_all_responses(client):
    """
    Adversarial Vector 4.1: Mandatory Security Headers.
    Verifies that X-Content-Type-Options, X-Frame-Options, X-XSS-Protection,
    Referrer-Policy, and Permissions-Policy are attached to HTTP responses.
    """
    endpoints = ["/api/health", "/api/scenarios", "/"]
    for path in endpoints:
        response = client.get(path)
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert response.headers.get("Permissions-Policy") == "geolocation=(), microphone=(), camera=()"


def test_adv_cors_unauthorized_origin_not_reflected(client):
    """
    Adversarial Vector 4.2: Unauthorized CORS Origin.
    Origins not matching allowed origins or regex must not receive allow-origin reflections.
    """
    headers = {
        "Origin": "https://attacker-domain.evil.com",
        "Access-Control-Request-Method": "POST"
    }
    response = client.options("/api/scenarios/seed", headers=headers)
    allow_origin = response.headers.get("Access-Control-Allow-Origin")
    assert allow_origin != "https://attacker-domain.evil.com"


def test_adv_cors_valid_origins_accepted(client):
    """
    Adversarial Vector 4.3: Valid CORS Origins.
    Local development origins and Google Cloud Run domain patterns must be accepted.
    """
    allowed_origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://workplace-pulse-app-xyz.run.app",
        "https://my-service.run.app",
    ]
    for origin in allowed_origins:
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": "GET"
        }
        response = client.options("/api/health", headers=headers)
        assert response.headers.get("Access-Control-Allow-Origin") == origin, f"Origin {origin} not accepted"
        assert response.headers.get("Access-Control-Allow-Credentials") == "true"


# ==============================================================================
# SECTION 5: RAPID BURST & HIGH-VOLUME RESILIENCE
# ==============================================================================

def test_adv_rapid_burst_endpoint_stress(client):
    """
    Adversarial Vector 5.1: High-Volume Rapid Sequential Request Burst.
    Sends 50 rapid requests across core endpoints to verify connection stability and zero leaks.
    """
    headers = {"Authorization": "Bearer demo-engineer-burst"}
    chat_payload = {
        "scenario_id": "saas_finops",
        "message": "Burst test query",
        "history": []
    }

    with patch("main.generate_multi_turn_forecast", return_value="Burst response"):
        with patch("main.save_forecast_log", return_value=True):
            for i in range(50):
                # Health check
                r_health = client.get("/api/health")
                assert r_health.status_code == 200

                # Scenarios catalog
                r_scen = client.get("/api/scenarios")
                assert r_scen.status_code == 200

                # Seed scenario
                r_seed = client.post("/api/scenarios/seed", json={"scenario_id": "saas_finops"})
                assert r_seed.status_code == 200

                # Forecast chat
                r_chat = client.post("/api/forecast/chat", json=chat_payload, headers=headers)
                assert r_chat.status_code == 200
