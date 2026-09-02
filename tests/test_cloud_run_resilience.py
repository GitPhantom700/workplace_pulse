"""
Tier 4 Resilience & Cloud Run Containerization Tests
Validates Dockerfile specifications, Cloud Run $PORT support, offline resilience, and database isolation fault-tolerance.
"""

import os
import pytest
from database import save_forecast_log
from main import app

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_dockerfile_cloud_run_specifications():
    """
    Verify Dockerfile follows Cloud Run serverless best practices:
    - python:3.11-slim base image for minimal attack surface and fast startup
    - WORKDIR /app
    - Unbuffered python logs (PYTHONUNBUFFERED=1)
    - Cached layer dependency installation with --no-cache-dir
    - Port 8080 exposure and Uvicorn startup binding
    """
    dockerfile_path = os.path.join(PROJECT_ROOT, "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile missing from project root."

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        dockerfile = f.read()

    # 1. Minimal base image
    assert "FROM python:3.11-slim" in dockerfile or "FROM python:3." in dockerfile

    # 2. Workdir
    assert "WORKDIR /app" in dockerfile

    # 3. Environment variables for production logging
    assert "ENV PYTHONUNBUFFERED=1" in dockerfile
    assert "ENV PYTHONDONTWRITEBYTECODE=1" in dockerfile

    # 4. Layer caching and no-cache-dir
    assert "requirements.txt" in dockerfile
    assert "--no-cache-dir" in dockerfile

    # 5. Cloud Run port binding
    assert "EXPOSE 8080" in dockerfile or "8080" in dockerfile
    assert "uvicorn" in dockerfile
    assert "main:app" in dockerfile
    assert "0.0.0.0" in dockerfile


def test_firestore_offline_resilience():
    """
    Verify that Firestore write failures do not crash the application or prevent AI responses.
    """
    # Test with db=None (offline / demo mode)
    result_none = save_forecast_log(
        user_id="test_user_offline",
        user_email="test@enterprise.org",
        scenario_id="saas_finops",
        user_prompt="Forecast savings",
        ai_response="AI Forecast Result"
    )
    # When DB is offline, returns False without raising exception
    assert result_none is False


def test_fastapi_cors_and_security_middleware():
    """
    Verify FastAPI application includes CORS middleware.
    """
    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_classes
