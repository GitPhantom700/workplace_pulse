"""
Tier 1 & Tier 4 Unit Tests: Resilient Gemini AI Forecasting Core
Validates persona prompts, security guardrails, fallback ladder (429/503 simulation), and history formatting.
"""

import pytest
from unittest.mock import patch, MagicMock
from google.api_core import exceptions as google_exceptions

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
    """Verify happy path: primary model gemini-1.5-flash succeeds on first attempt."""
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_instance = MagicMock()
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Primary Forecast: Optimize Figma licenses to save $58,500/year."
        mock_chat.send_message.return_value = mock_response
        mock_instance.start_chat.return_value = mock_chat
        mock_model_cls.return_value = mock_instance

        result = generate_multi_turn_forecast(
            scenario_id="saas_finops",
            chat_history=[{"role": "user", "content": "How do we reduce SaaS costs?"}],
            user_message="Provide license reclaim steps.",
            grounding_context="Test Grounding Data"
        )

        assert result == "Primary Forecast: Optimize Figma licenses to save $58,500/year."
        # Verify model initialization
        mock_model_cls.assert_called_once()
        call_kwargs = mock_model_cls.call_args.kwargs
        assert call_kwargs.get("model_name") == "gemini-1.5-flash"


def test_generate_multi_turn_forecast_quota_exhausted_fallback_429():
    """
    Tier 4 Resilience: Simulate 429 ResourceExhausted on primary model (gemini-1.5-flash).
    Verify fallback to gemini-2.0-flash succeeds.
    """
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        # Primary model instance fails with ResourceExhausted
        primary_instance = MagicMock()
        primary_chat = MagicMock()
        primary_chat.send_message.side_effect = google_exceptions.ResourceExhausted("Quota exceeded for gemini-1.5-flash")
        primary_instance.start_chat.return_value = primary_chat

        # Fallback model instance succeeds
        fallback_instance = MagicMock()
        fallback_chat = MagicMock()
        fallback_response = MagicMock()
        fallback_response.text = "Fallback Forecast: High ticket volume during Month-End Close."
        fallback_chat.send_message.return_value = fallback_response
        fallback_instance.start_chat.return_value = fallback_chat

        mock_model_cls.side_effect = [primary_instance, fallback_instance]

        result = generate_multi_turn_forecast(
            scenario_id="itsm_surge",
            chat_history=[],
            user_message="Forecast ticket volume",
            grounding_context="ITSM Grounding"
        )

        assert result == "Fallback Forecast: High ticket volume during Month-End Close."
        assert mock_model_cls.call_count == 2
        # Verify first call was primary, second call was fallback
        first_call = mock_model_cls.call_args_list[0].kwargs.get("model_name")
        second_call = mock_model_cls.call_args_list[1].kwargs.get("model_name")
        assert first_call == "gemini-1.5-flash"
        assert second_call == "gemini-2.0-flash"


def test_generate_multi_turn_forecast_internal_server_error_fallback_503():
    """
    Tier 4 Resilience: Simulate 503 InternalServerError on primary model.
    Verify fallback to gemini-2.0-flash succeeds.
    """
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        primary_instance = MagicMock()
        primary_chat = MagicMock()
        primary_chat.send_message.side_effect = google_exceptions.InternalServerError("Backend unavailable")
        primary_instance.start_chat.return_value = primary_chat

        fallback_instance = MagicMock()
        fallback_chat = MagicMock()
        fallback_response = MagicMock()
        fallback_response.text = "Fallback Response: Replace aging laptop batteries."
        fallback_chat.send_message.return_value = fallback_response
        fallback_instance.start_chat.return_value = fallback_chat

        mock_model_cls.side_effect = [primary_instance, fallback_instance]

        result = generate_multi_turn_forecast(
            scenario_id="hardware_lifecycle",
            chat_history=[],
            user_message="Check battery status",
            grounding_context="Hardware Grounding"
        )

        assert result == "Fallback Response: Replace aging laptop batteries."
        assert mock_model_cls.call_count == 2


def test_generate_multi_turn_forecast_all_models_fail_returns_graceful_alert():
    """
    Tier 4 Resilience: When all models in the fallback ladder fail,
    returns a user-friendly system alert instead of crashing.
    """
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        failing_instance = MagicMock()
        failing_chat = MagicMock()
        failing_chat.send_message.side_effect = google_exceptions.ResourceExhausted("All quotas exhausted")
        failing_instance.start_chat.return_value = failing_chat

        mock_model_cls.return_value = failing_instance

        result = generate_multi_turn_forecast(
            scenario_id="saas_finops",
            chat_history=[],
            user_message="Help",
            grounding_context="Grounding"
        )

        assert "System Alert: The AI forecasting core is currently experiencing high load" in result
        assert "fallback ladder" in result


def test_generate_multi_turn_forecast_chat_history_mapping():
    """Verify chat history role conversion (assistant -> model)."""
    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_instance = MagicMock()
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Response text"
        mock_chat.send_message.return_value = mock_response
        mock_instance.start_chat.return_value = mock_chat
        mock_model_cls.return_value = mock_instance

        history = [
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1"},
            {"role": "model", "content": "Answer 2"}
        ]

        generate_multi_turn_forecast(
            scenario_id="saas_finops",
            chat_history=history,
            user_message="Question 2",
            grounding_context="Context"
        )

        # Inspect start_chat call arguments
        mock_instance.start_chat.assert_called_once()
        passed_history = mock_instance.start_chat.call_args.kwargs.get("history")
        assert len(passed_history) == 3
        assert passed_history[0]["role"] == "user"
        assert passed_history[0]["parts"] == ["Question 1"]
        assert passed_history[1]["role"] == "model"
        assert passed_history[1]["parts"] == ["Answer 1"]
        assert passed_history[2]["role"] == "model"
        assert passed_history[2]["parts"] == ["Answer 2"]
