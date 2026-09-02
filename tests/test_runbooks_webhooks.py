"""
WorkplacePulse - Webhook & Runbook Engine Test Suite
Tests multi-platform webhook formatting, HMAC signatures, async dispatching, runbook execution, and strict multi-tenant isolation.
"""

import os
import time
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from pydantic import ValidationError

from main import app
from webhook_service import (
    WebhookCreate,
    WebhookResponse,
    WebhookDeliveryLog,
    WebhookTestRequest,
    WebhookServiceType,
    WebhookEventType,
    generate_hmac_signature,
    verify_hmac_signature,
    mask_webhook_url,
    format_slack_block_kit,
    format_discord_embed,
    format_teams_card,
    format_generic_json,
    format_payload_for_service,
    dispatch_webhook_with_retry
)
from runbook_service import (
    RunbookAction,
    RunbookExecuteRequest,
    RunbookExecuteResponse,
    list_available_runbooks,
    get_runbook_by_id,
    get_runbook_for_scenario,
    execute_runbook,
    RUNBOOK_CATALOG
)
from database import (
    save_webhook_config,
    get_user_webhooks,
    get_webhook_by_id,
    delete_user_webhook,
    save_webhook_delivery_log,
    get_user_webhook_logs,
    save_runbook_execution_log,
    get_user_runbook_logs,
    _DEMO_STORE
)


# =========================================================
# Tier 1: Webhook Pydantic Validation & Utility Tests
# =========================================================

def test_webhook_pydantic_valid():
    """Test valid webhook creation payload parsing."""
    wh = WebhookCreate(
        name="Security Alert Channel",
        url="https://hooks.slack.com/services/T00/B00/X00",
        service_type=WebhookServiceType.SLACK,
        subscribed_events=[WebhookEventType.RUNBOOK_EXECUTED]
    )
    assert wh.name == "Security Alert Channel"
    assert wh.url.startswith("https://")
    assert wh.service_type == WebhookServiceType.SLACK
    assert WebhookEventType.RUNBOOK_EXECUTED in wh.subscribed_events


def test_webhook_pydantic_invalid_url():
    """Test invalid webhook URL scheme rejection."""
    with pytest.raises(ValidationError):
        WebhookCreate(
            name="Bad URL Channel",
            url="ftp://invalid.url.com/hook"
        )


def test_webhook_pydantic_name_sanitization():
    """Test null-byte stripping and whitespace trimming."""
    wh = WebhookCreate(
        name="  \x00Audit Alert Webhook  ",
        url="https://example.com/webhook"
    )
    assert wh.name == "Audit Alert Webhook"


def test_mask_webhook_url():
    """Test safe masking of webhook URLs."""
    masked = mask_webhook_url("https://hooks.slack.com/services/T0123/B0456/SecretToken12345")
    assert "SecretToken" not in masked
    assert "***" in masked or "..." in masked


# =========================================================
# Tier 1: Cryptographic HMAC-SHA256 Signature Tests
# =========================================================

def test_hmac_signature_generation_and_verification():
    """Test HMAC SHA256 header calculation and validation."""
    secret = "super-secret-key-12345"
    payload = json.dumps({"event": "runbook.executed", "status": "success"})
    
    sig_header, ts = generate_hmac_signature(payload, secret)
    assert sig_header.startswith("t=")
    assert ",v1=" in sig_header
    
    # Valid verification
    is_valid = verify_hmac_signature(payload, sig_header, secret)
    assert is_valid is True
    
    # Tampered payload verification
    tampered_payload = json.dumps({"event": "runbook.executed", "status": "failed"})
    is_invalid = verify_hmac_signature(tampered_payload, sig_header, secret)
    assert is_invalid is False
    
    # Wrong secret verification
    wrong_secret_invalid = verify_hmac_signature(payload, sig_header, "wrong-secret-key")
    assert wrong_secret_invalid is False


def test_hmac_signature_timestamp_replay_rejection():
    """Test rejection of expired HMAC timestamps outside tolerance."""
    secret = "secret-key"
    payload = "{}"
    old_ts = int(time.time()) - 400  # 400s ago (> 300s default tolerance)
    sig_header, _ = generate_hmac_signature(payload, secret, timestamp=old_ts)
    
    is_valid = verify_hmac_signature(payload, sig_header, secret, tolerance_seconds=300)
    assert is_valid is False


# =========================================================
# Tier 1: Multi-Platform Formatter Tests
# =========================================================

def test_format_slack_block_kit():
    """Test Slack Block Kit JSON structure."""
    blocks = format_slack_block_kit(
        title="High SaaS Waste Alert",
        message="Predicted 128 inactive seats costing $56,400/yr.",
        runbook_data={"action_id": "act_saas_reclaim_01", "impact_summary": "Reclaimed 128 seats"},
        event_type="saas.threshold_breach"
    )
    assert "blocks" in blocks
    assert len(blocks["blocks"]) >= 3
    assert blocks["blocks"][0]["type"] == "header"
    assert "High SaaS Waste" in blocks["blocks"][0]["text"]["text"]


def test_format_discord_embed():
    """Test Discord Rich Embed JSON structure."""
    discord_payload = format_discord_embed(
        title="Hardware Swelling Incident",
        message="42 devices require battery depot maintenance.",
        runbook_data={"action_id": "act_hardware_quarantine_02", "remediated_items_count": 42},
        event_type="hardware.critical_risk"
    )
    assert "embeds" in discord_payload
    embed = discord_payload["embeds"][0]
    assert embed["title"].startswith("🚨")
    assert len(embed["fields"]) >= 2
    assert "Sentinel" in discord_payload["username"]


def test_format_teams_card():
    """Test Microsoft Teams Adaptive / MessageCard format."""
    teams_payload = format_teams_card(
        title="Emergency SOX Access Window",
        message="Dual signer matrix active for 72h.",
        runbook_data={"action_id": "act_itsm_sox_fasttrack_03"},
        event_type="itsm.surge_alert"
    )
    assert teams_payload["@type"] == "MessageCard"
    assert teams_payload["summary"] == "Emergency SOX Access Window"


def test_format_generic_json():
    """Test Generic JSON webhook payload."""
    gen_payload = format_generic_json(
        title="Test Ping",
        message="Test alert",
        event_type="system.test_ping"
    )
    assert gen_payload["source"] == "WorkplacePulse"
    assert gen_payload["event_type"] == "system.test_ping"


# =========================================================
# Tier 1 & 2: Runbook Catalog & Execution Unit Tests
# =========================================================

def test_runbook_catalog_completeness():
    """Verify all 3 required domain runbooks exist in catalog."""
    runbooks = list_available_runbooks()
    assert len(runbooks) >= 3
    action_ids = [r.action_id for r in runbooks]
    assert "act_saas_reclaim_01" in action_ids
    assert "act_hardware_quarantine_02" in action_ids
    assert "act_itsm_sox_fasttrack_03" in action_ids


@pytest.mark.asyncio
async def test_execute_saas_reclaim_runbook():
    """Test execution of SaaS FinOps SCIM deprovisioning runbook."""
    result = await execute_runbook(
        user_id="test_user_finops",
        user_email="finops@floqast.com",
        action_id="act_saas_reclaim_01",
        scenario_id="saas_finops",
        dispatch_webhooks=False
    )
    assert result.status == "success"
    assert result.remediated_items_count == 128
    assert "56,460" in result.impact_summary or "56,400" in result.impact_summary
    assert len(result.execution_log) >= 5


@pytest.mark.asyncio
async def test_execute_hardware_quarantine_runbook():
    """Test execution of Jamf Pro hardware quarantine runbook."""
    result = await execute_runbook(
        user_id="test_user_hardware",
        user_email="jamf@floqast.com",
        action_id="act_hardware_quarantine_02",
        scenario_id="hardware_lifecycle",
        dispatch_webhooks=False
    )
    assert result.status == "success"
    assert result.remediated_items_count == 42
    assert "Quarantined 42" in result.impact_summary


@pytest.mark.asyncio
async def test_execute_itsm_sox_fasttrack_runbook():
    """Test execution of ITSM Month-End SOX bypass runbook."""
    result = await execute_runbook(
        user_id="test_user_itsm",
        user_email="itsm@floqast.com",
        action_id="act_itsm_sox_fasttrack_03",
        scenario_id="itsm_surge",
        dispatch_webhooks=False
    )
    assert result.status == "success"
    assert result.remediated_items_count == 64
    assert "Month-End" in result.impact_summary


# =========================================================
# Tier 2: REST Endpoints Dynamic Tests
# =========================================================

def test_api_get_runbooks_200(client):
    """Test GET /api/runbooks returns the 3 catalog runbooks."""
    res = client.get("/api/runbooks")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_api_webhooks_unauthorized_401(client, invalid_auth_headers):
    """Test GET /api/webhooks returns 401 for missing/invalid token."""
    res_no_auth = client.get("/api/webhooks")
    assert res_no_auth.status_code in (401, 403)

    res_invalid = client.get("/api/webhooks", headers=invalid_auth_headers)
    assert res_invalid.status_code == 401


def test_api_webhooks_crud_lifecycle(client, demo_auth_headers):
    """Test creating, listing, testing, and deleting a webhook destination."""
    # 1. Create Webhook
    create_payload = {
        "name": "#ops-alerts-channel",
        "url": "https://hooks.slack.com/services/DEMO/OPS/ALERTS",
        "service_type": "slack",
        "subscribed_events": ["runbook.executed", "saas.threshold_breach"],
        "secret_token": "test-hmac-key"
    }
    res_create = client.post("/api/webhooks", json=create_payload, headers=demo_auth_headers)
    assert res_create.status_code == 201
    created_data = res_create.json()
    webhook_id = created_data["webhook_id"]
    assert webhook_id.startswith("wh_")
    assert created_data["has_secret"] is True
    assert "OPS" in created_data["url"] or "***" in created_data["url"]

    # 2. List Webhooks
    res_list = client.get("/api/webhooks", headers=demo_auth_headers)
    assert res_list.status_code == 200
    hooks = res_list.json()
    assert any(h["webhook_id"] == webhook_id for h in hooks)

    # 3. Test Webhook Ping
    res_test = client.post("/api/webhooks/test", json={"webhook_id": webhook_id}, headers=demo_auth_headers)
    assert res_test.status_code == 200
    test_result = res_test.json()
    assert test_result["status"] in ("simulated", "delivered")

    # 4. List Deliveries Audit Trail
    res_deliv = client.get("/api/webhooks/deliveries", headers=demo_auth_headers)
    assert res_deliv.status_code == 200

    # 5. Delete Webhook
    res_delete = client.delete(f"/api/webhooks/{webhook_id}", headers=demo_auth_headers)
    assert res_delete.status_code == 200
    assert res_delete.json()["status"] == "success"

    # 6. Delete again returns 404
    res_delete_404 = client.delete(f"/api/webhooks/{webhook_id}", headers=demo_auth_headers)
    assert res_delete_404.status_code == 404


def test_api_execute_runbook_200(client, demo_auth_headers):
    """Test POST /api/runbooks/execute triggers runbook and persists log."""
    payload = {
        "action_id": "act_saas_reclaim_01",
        "scenario_id": "saas_finops",
        "dispatch_webhooks": True
    }
    res = client.post("/api/runbooks/execute", json=payload, headers=demo_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["action_id"] == "act_saas_reclaim_01"
    assert len(data["execution_log"]) > 0


def test_api_execute_runbook_invalid_action_404(client, demo_auth_headers):
    """Test POST /api/runbooks/execute returns 404 for nonexistent action."""
    payload = {
        "action_id": "nonexistent_action_999",
        "scenario_id": "saas_finops"
    }
    res = client.post("/api/runbooks/execute", json=payload, headers=demo_auth_headers)
    assert res.status_code == 404


# =========================================================
# Tier 3: Strict Multi-Tenant Isolation Tests
# =========================================================

def test_webhook_multi_tenant_isolation():
    """Verify Tenant A cannot access or delete Tenant B's webhooks."""
    user_a = "tenant_a_uuid_111"
    user_b = "tenant_b_uuid_222"

    # Save webhook for Tenant A
    wh_a = {
        "webhook_id": "wh_tenant_a_secret",
        "name": "Tenant A Slack",
        "url": "https://hooks.slack.com/services/TENANT_A",
        "service_type": "slack",
        "subscribed_events": ["runbook.executed"]
    }
    save_webhook_config(user_a, wh_a)

    # Tenant B tries to query webhooks
    tenant_b_hooks = get_user_webhooks(user_b)
    assert not any(h["webhook_id"] == "wh_tenant_a_secret" for h in tenant_b_hooks)

    # Tenant B tries to get webhook A by ID
    assert get_webhook_by_id(user_b, "wh_tenant_a_secret") is None

    # Tenant B tries to delete webhook A
    assert delete_user_webhook(user_b, "wh_tenant_a_secret") is False

    # Tenant A can still access their webhook
    assert get_webhook_by_id(user_a, "wh_tenant_a_secret") is not None
    assert delete_user_webhook(user_a, "wh_tenant_a_secret") is True


def test_runbook_logs_multi_tenant_isolation():
    """Verify Tenant A cannot see Tenant B's runbook execution logs."""
    user_a = "tenant_a_111"
    user_b = "tenant_b_222"

    log_a = {
        "execution_id": "exec_tenant_a_only",
        "action_id": "act_saas_reclaim_01",
        "status": "success"
    }
    save_runbook_execution_log(user_a, log_a)

    logs_b = get_user_runbook_logs(user_b)
    assert not any(l["execution_id"] == "exec_tenant_a_only" for l in logs_b)

    logs_a = get_user_runbook_logs(user_a)
    assert any(l["execution_id"] == "exec_tenant_a_only" for l in logs_a)


# =========================================================
# Tier 4: Async Dispatcher Resilience & Error Handling
# =========================================================

@pytest.mark.asyncio
async def test_async_dispatcher_simulated_mode():
    """Test instantaneous simulated delivery for test/demo URLs."""
    res = await dispatch_webhook_with_retry(
        url="https://hooks.slack.com/services/DEMO/TEST",
        payload={"text": "Test"},
        service_type="slack"
    )
    assert res.status == "simulated"
    assert res.status_code == 200
    assert res.duration_ms > 0


@pytest.mark.asyncio
async def test_async_dispatcher_retry_on_network_failure():
    """Test retry policy and failure status when endpoint fails repeatedly."""
    with patch("httpx.AsyncClient.post", side_effect=Exception("Connection refused")):
        res = await dispatch_webhook_with_retry(
            url="https://api.unreachable-target-domain-12345.com/hook",
            payload={"text": "Test"},
            service_type="generic",
            max_retries=2
        )
        assert res.status == "failed"
        assert "Connection refused" in (res.error_message or "")
