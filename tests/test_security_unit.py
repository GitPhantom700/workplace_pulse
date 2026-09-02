"""
Tier 1 & Tier 3 Unit Tests: Security & Authentication Services
Validates Firebase token validation, Secret Manager retrieval, environment fallback, and error handling.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from google.api_core.exceptions import GoogleAPIError

from security import verify_firebase_token, get_gemini_api_key


# ---------------------------------------------------------
# Firebase Token Verification Tests
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_verify_firebase_token_empty_token_raises_401():
    """Verify empty credentials token raises 401 Unauthorized."""
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
    with pytest.raises(HTTPException) as exc_info:
        await verify_firebase_token(creds)
    assert exc_info.value.status_code == 401
    assert "Token missing" in exc_info.value.detail


@pytest.mark.asyncio
async def test_verify_firebase_token_demo_sandbox_mode():
    """Verify demo- token prefix yields demo sandbox user context."""
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="demo-engineer-auth-12345")
    user = await verify_firebase_token(creds)
    assert user is not None
    assert user["uid"] == "demo_engineer_chandraprakash"
    assert "floqast.com" in user["email"]
    assert user["role"] == "IT Support Lead"


@pytest.mark.asyncio
async def test_verify_firebase_token_valid_firebase_jwt():
    """Verify valid Firebase JWT token is correctly decoded."""
    mock_payload = {
        "uid": "prod_user_firebase_789",
        "email": "lead.architect@enterprise.org",
        "name": "Lead Architect"
    }
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.firebase.jwt.token")
    with patch("firebase_admin.auth.verify_id_token", return_value=mock_payload):
        user = await verify_firebase_token(creds)
        assert user["uid"] == "prod_user_firebase_789"
        assert user["email"] == "lead.architect@enterprise.org"


@pytest.mark.asyncio
async def test_verify_firebase_token_invalid_or_expired_jwt_raises_401():
    """Verify invalid or expired JWT token raises 401 Unauthorized with WWW-Authenticate header."""
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired.jwt.token.123")
    with patch("firebase_admin.auth.verify_id_token", side_effect=Exception("Token expired")):
        with pytest.raises(HTTPException) as exc_info:
            await verify_firebase_token(creds)
        assert exc_info.value.status_code == 401
        assert "Invalid or Expired Authentication Token" in exc_info.value.detail
        assert exc_info.value.headers.get("WWW-Authenticate") == "Bearer"


# ---------------------------------------------------------
# Secret Manager Retrieval Tests
# ---------------------------------------------------------

def test_get_gemini_api_key_local_env_precedence(monkeypatch):
    """Verify local GEMINI_API_KEY environment variable takes immediate precedence."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-local-gemini-key-xyz")
    key = get_gemini_api_key()
    assert key == "test-local-gemini-key-xyz"


def test_get_gemini_api_key_secret_manager_success(monkeypatch):
    """Verify retrieval from Cloud Secret Manager when GEMINI_API_KEY is not in env."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "production-cloud-pulse-project")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.payload.data = b"secret-api-key-from-sm-vault"
    mock_client.access_secret_version.return_value = mock_response

    with patch("google.cloud.secretmanager.SecretManagerServiceClient", return_value=mock_client):
        key = get_gemini_api_key()
        assert key == "secret-api-key-from-sm-vault"
        mock_client.access_secret_version.assert_called_once_with(
            request={"name": "projects/production-cloud-pulse-project/secrets/GEMINI_API_KEY/versions/latest"}
        )


def test_get_gemini_api_key_missing_project_raises_500(monkeypatch):
    """Verify 500 error when neither GEMINI_API_KEY nor GCP Project ID can be found."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)

    with patch("google.auth.default", side_effect=Exception("Metadata server unreachable")):
        with pytest.raises(HTTPException) as exc_info:
            get_gemini_api_key()
        assert exc_info.value.status_code == 500
        assert "Could not determine GCP Project ID" in exc_info.value.detail


def test_get_gemini_api_key_secret_manager_api_error_raises_500(monkeypatch):
    """Verify GoogleAPIError during Secret Manager fetch raises 500 Security Exception."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")

    mock_client = MagicMock()
    mock_client.access_secret_version.side_effect = GoogleAPIError("PermissionDenied: Secret not accessible")

    with patch("google.cloud.secretmanager.SecretManagerServiceClient", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            get_gemini_api_key()
        assert exc_info.value.status_code == 500
        assert "Security Exception: Failed to retrieve API key" in exc_info.value.detail


def test_get_gemini_api_key_unexpected_error_raises_500(monkeypatch):
    """Verify unexpected exception during Secret Manager access raises 500 error."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")

    mock_client = MagicMock()
    mock_client.access_secret_version.side_effect = RuntimeError("Network timeout")

    with patch("google.cloud.secretmanager.SecretManagerServiceClient", return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            get_gemini_api_key()
        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in exc_info.value.detail
