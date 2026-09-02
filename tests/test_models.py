"""
Tier 1 Unit Tests: Pydantic Schema Models & Request Validation
Tests field validation, boundary conditions, null-byte sanitization, and serialization.
"""

import pytest
from pydantic import ValidationError
from main import ChatMessageModel, ForecastChatRequest, SeedScenarioRequest
from data_engine import (
    SaaSAppMetric,
    HardwareFleetMetric,
    ITSMIncidentMetric,
    ScenarioDataPayload
)


# ---------------------------------------------------------
# ChatMessageModel Tests
# ---------------------------------------------------------

def test_chat_message_valid_roles():
    """Verify accepted roles: user, model, assistant."""
    for role in ["user", "model", "assistant"]:
        msg = ChatMessageModel(role=role, content="Hello AI")
        assert msg.role == role
        assert msg.content == "Hello AI"


def test_chat_message_invalid_role_raises_validation_error():
    """Verify invalid roles are rejected with ValidationError."""
    for invalid_role in ["system", "admin", "root", "bot"]:
        with pytest.raises((ValueError, ValidationError)):
            ChatMessageModel(role=invalid_role, content="Hello")


def test_chat_message_empty_content_rejected():
    """Verify empty, whitespace-only, and pure null-byte content is rejected."""
    for empty in ["", "   ", "\t\n  ", "\x00", "\x00\x00\x00", "  \x00  "]:
        with pytest.raises((ValueError, ValidationError)):
            ChatMessageModel(role="user", content=empty)


def test_chat_message_null_byte_sanitization():
    """Verify null bytes are stripped during sanitization."""
    msg = ChatMessageModel(role="user", content="Sanitize\x00 this \x00message")
    assert "\x00" not in msg.content
    assert msg.content == "Sanitize this message"


def test_chat_message_length_boundary():
    """Verify 4000 character length limit."""
    # 4000 chars should pass
    valid_content = "A" * 4000
    msg = ChatMessageModel(role="user", content=valid_content)
    assert len(msg.content) == 4000

    # 4001 chars should raise ValueError
    invalid_content = "A" * 4001
    with pytest.raises((ValueError, ValidationError)):
        ChatMessageModel(role="user", content=invalid_content)


# ---------------------------------------------------------
# ForecastChatRequest Tests
# ---------------------------------------------------------

def test_forecast_chat_request_valid():
    """Verify valid ForecastChatRequest structure."""
    req = ForecastChatRequest(
        scenario_id="saas_finops",
        message="What is the potential savings?",
        history=[ChatMessageModel(role="user", content="Initial question")]
    )
    assert req.scenario_id == "saas_finops"
    assert req.message == "What is the potential savings?"
    assert len(req.history) == 1


def test_forecast_chat_request_empty_message_rejected():
    """Verify empty, whitespace-only, and pure null-byte messages raise ValidationError."""
    for empty in ["", "   ", "\t\n  ", "\x00", "\x00\x00\x00", "  \x00  "]:
        with pytest.raises((ValueError, ValidationError)):
            ForecastChatRequest(scenario_id="saas_finops", message=empty)


def test_forecast_chat_request_null_byte_sanitized():
    """Verify null bytes are stripped from ForecastChatRequest message."""
    req = ForecastChatRequest(
        scenario_id="saas_finops",
        message="Prompt\x00Injection\x00Test"
    )
    assert req.message == "PromptInjectionTest"


def test_forecast_chat_request_max_length_boundary():
    """Verify message > 4000 characters is rejected."""
    with pytest.raises((ValueError, ValidationError)):
        ForecastChatRequest(scenario_id="saas_finops", message="X" * 4001)


# ---------------------------------------------------------
# SeedScenarioRequest Tests
# ---------------------------------------------------------

def test_seed_scenario_request_valid():
    """Verify SeedScenarioRequest creation."""
    req = SeedScenarioRequest(scenario_id="hardware_lifecycle")
    assert req.scenario_id == "hardware_lifecycle"


def test_seed_scenario_request_missing_field_rejected():
    """Verify missing scenario_id raises ValidationError."""
    with pytest.raises(ValidationError):
        SeedScenarioRequest.model_validate({})


# ---------------------------------------------------------
# Telemetry Schema Tests
# ---------------------------------------------------------

def test_saas_metric_schema_serialization():
    """Verify SaaSAppMetric model serialization."""
    metric = SaaSAppMetric(
        app_name="Figma Enterprise",
        category="Design",
        total_licenses=150,
        active_last_30d=85,
        inactive_60d_plus=65,
        cost_per_seat_monthly=75.0,
        annual_potential_savings=58500.0,
        okta_sso_configured=True,
        utilization_rate_pct=56.7
    )
    dumped = metric.model_dump()
    assert dumped["app_name"] == "Figma Enterprise"
    assert dumped["annual_potential_savings"] == 58500.0
    assert dumped["okta_sso_configured"] is True


def test_hardware_metric_schema_serialization():
    """Verify HardwareFleetMetric model serialization."""
    metric = HardwareFleetMetric(
        model_name="MacBook Pro 14",
        os_version="macOS 14.4",
        total_units=210,
        battery_critical_units=22,
        out_of_warranty_units=85,
        projected_failures_next_quarter=15,
        estimated_replacement_budget_usd=31500.0,
        jamf_compliance_rate_pct=98.1
    )
    dumped = metric.model_dump()
    assert dumped["total_units"] == 210
    assert dumped["battery_critical_units"] == 22
    assert dumped["estimated_replacement_budget_usd"] == 31500.0


def test_itsm_metric_schema_serialization():
    """Verify ITSMIncidentMetric model serialization."""
    metric = ITSMIncidentMetric(
        category="Financial Close & ERP Access",
        historical_daily_avg=6,
        month_end_surge_daily_avg=42,
        current_open_backlog=18,
        average_resolution_time_hrs=3.8,
        primary_bottleneck="Manual SOX dual-approval workflow",
        escalation_risk_score_1_to_10=9
    )
    dumped = metric.model_dump()
    assert dumped["historical_daily_avg"] == 6
    assert dumped["month_end_surge_daily_avg"] == 42
    assert dumped["escalation_risk_score_1_to_10"] == 9
