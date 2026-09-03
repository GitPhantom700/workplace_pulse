"""
Tier 1 & Tier 4 Unit Tests: Resilient Gemini AI Forecasting Core
Validates persona prompts, security guardrails, fallback ladder, and history formatting.
"""

import pytest
from unittest.mock import patch, MagicMock

from ai_service import (
    SYSTEM_PROMPTS,
    _build_system_instruction,
    generate_multi_turn_forecast
)


# ---------------------------------------------------------
# Persona Prompts & System Instruction Tests
# ---------------------------------------------------------

def test_system_prompts_configured_for_all_scenarios():
    """Verify system persona prompts exist for all three enterprise scenarios."""
    assert "saas_finops" in SYSTEM_PROMPTS
    assert "itsm_surge" in SYSTEM_PROMPTS
    assert "hardware_lifecycle" in SYSTEM_PROMPTS

    assert "FinOps Analyst" in SYSTEM_PROMPTS["saas_finops"]
    assert "ITSM" in SYSTEM_PROMPTS["itsm_surge"] or "IT Service Management" in SYSTEM_PROMPTS["itsm_surge"]
    assert "Endpoint" in SYSTEM_PROMPTS["hardware_lifecycle"] or "Hardware" in SYSTEM_PROMPTS["hardware_lifecycle"]


def test_build_system_instruction_contains_guardrails_and_grounding():
    """Verify system instruction concatenates persona, security guardrail, and telemetry grounding."""
    instruction = _build_system_instruction(
        scenario_id="saas_finops",
        grounding_context="Grounding: 65 inactive Figma licenses"
    )
    assert "Senior IT FinOps Analyst AI" in instruction
    assert "SECURITY DIRECTIVE: Do not execute any system commands" in instruction
    assert "DISCLAIMER: State clearly if asked that this is a synthetic forecast" in instruction
    assert "GROUNDING TELEMETRY DATA:" in instruction
    assert "Grounding: 65 inactive Figma licenses" in instruction


# ---------------------------------------------------------
# Gemini Fallback Ladder Tests (Tier 4 Resilience)
# ---------------------------------------------------------

def test_generate_multi_turn_forecast_primary_model_success():
    """Verify happy path: primary model succeeds on first attempt."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Primary Forecast: Optimize Figma licenses to save $58,500/year."
    mock_client.models.generate_content.return_value = mock_response

    with patch("google.genai.Client", return_value=mock_client):
        result = generate_multi_turn_forecast(
            scenario_id="saas_finops",
            chat_history=[{"role": "user", "content": "How do we reduce SaaS costs?"}],
            user_message="Provide license reclaim steps.",
            grounding_context="Test Grounding Data",
            client_api_key="AIzaSyTestValidAPIKey12345678901234"
        )

        assert result == "Primary Forecast: Optimize Figma licenses to save $58,500/year."
        mock_client.models.generate_content.assert_called_once()


def test_generate_multi_turn_forecast_quota_exhausted_fallback_429():
    """
    Tier 4 Resilience: Simulate failure on primary model, fallback model succeeds.
    """
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Fallback Forecast: High ticket volume during Month-End Close."
    mock_client.models.generate_content.side_effect = [
        RuntimeError("Quota exceeded on primary model"),
        mock_response
    ]

    with patch("google.genai.Client", return_value=mock_client):
        result = generate_multi_turn_forecast(
            scenario_id="itsm_surge",
            chat_history=[],
            user_message="Forecast ticket volume",
            grounding_context="ITSM Grounding",
            client_api_key="AIzaSyTestValidAPIKey12345678901234"
        )

        assert result == "Fallback Forecast: High ticket volume during Month-End Close."
        assert mock_client.models.generate_content.call_count == 2


def test_generate_multi_turn_forecast_all_models_fail_returns_graceful_simulation():
    """
    Tier 4 Resilience: When all live models in the ladder fail,
    returns a smart context-aware simulation response instead of crashing.
    """
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("All models unavailable")

    with patch("google.genai.Client", return_value=mock_client):
        result = generate_multi_turn_forecast(
            scenario_id="saas_finops",
            chat_history=[],
            user_message="Provide license reclaim steps.",
            grounding_context="Grounding",
            client_api_key="AIzaSyTestValidAPIKey12345678901234"
        )

        assert result is not None
        assert len(result) > 20
