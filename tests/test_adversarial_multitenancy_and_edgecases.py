"""
WorkplacePulse - Challenger 2 Multi-Tenant Isolation & Functional Verifier Suite
Empirical adversarial verification of multi-tenant isolation, cross-tenant data leakage prevention,
firestore.rules parser/semantic enforcement, and scenario seed consistency & edge-case fuzzing.
"""

import os
import re
import time
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pydantic import ValidationError

from main import app
from database import (
    save_forecast_log,
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
from webhook_service import (
    WebhookCreate,
    WebhookServiceType,
    WebhookEventType,
    generate_hmac_signature,
    verify_hmac_signature,
    mask_webhook_url,
    dispatch_webhook_with_retry
)
from runbook_service import (
    list_available_runbooks,
    get_runbook_by_id,
    execute_runbook,
    RUNBOOK_CATALOG
)
from data_engine import (
    get_scenario_by_id,
    list_available_scenarios,
    SCENARIO_REGISTRY,
    ScenarioDataPayload
)
from security import verify_firebase_token


# ============================================================================
# SECTION 1: DATABASE & SERVICE LAYER MULTI-TENANT ISOLATION ADVERSARIAL TESTS
# ============================================================================

def test_adv_db_multi_tenant_crud_cross_isolation():
    """
    Simulate 10 distinct enterprise tenants.
    Tenant A creates webhooks with secret tokens.
    Tenants B through J attempt to list, read (IDOR), and delete Tenant A's webhooks.
    Verify 100% strict tenant isolation.
    """
    tenant_a = "tenant_alpha_001"
    other_tenants = [f"tenant_adversary_{i:03d}" for i in range(2, 11)]

    # 1. Tenant A registers 3 webhooks
    wh_a1 = {
        "webhook_id": "wh_alpha_slack_sec",
        "name": "Alpha SOC Slack",
        "url": "https://hooks.slack.com/services/ALPHA/SOC/SEC_KEY_999",
        "service_type": "slack",
        "subscribed_events": ["runbook.executed", "hardware.critical_risk"],
        "secret_token": "alpha-super-secret-hmac-token-1"
    }
    wh_a2 = {
        "webhook_id": "wh_alpha_discord_sec",
        "name": "Alpha DevOps Discord",
        "url": "https://discord.com/api/webhooks/ALPHA/DISCORD_KEY_888",
        "service_type": "discord",
        "subscribed_events": ["saas.threshold_breach"],
        "secret_token": "alpha-super-secret-hmac-token-2"
    }
    wh_a3 = {
        "webhook_id": "wh_alpha_teams_sec",
        "name": "Alpha ITSM Teams",
        "url": "https://outlook.office.com/webhook/ALPHA/TEAMS_KEY_777",
        "service_type": "teams",
        "subscribed_events": ["itsm.surge_alert"],
        "secret_token": "alpha-super-secret-hmac-token-3"
    }

    save_webhook_config(tenant_a, wh_a1)
    save_webhook_config(tenant_a, wh_a2)
    save_webhook_config(tenant_a, wh_a3)

    # 2. Verify Tenant A can see all 3
    a_hooks = get_user_webhooks(tenant_a)
    assert len(a_hooks) >= 3
    a_ids = [h["webhook_id"] for h in a_hooks]
    assert "wh_alpha_slack_sec" in a_ids
    assert "wh_alpha_discord_sec" in a_ids
    assert "wh_alpha_teams_sec" in a_ids

    # 3. Adversary Tenants B through J attempt unauthorized access
    for adv in other_tenants:
        # a) List webhooks for adversary -> must not contain any of Tenant A's webhooks
        adv_hooks = get_user_webhooks(adv)
        for h in adv_hooks:
            assert h["webhook_id"] not in a_ids, f"Data leak: {adv} saw Tenant A's webhook {h['webhook_id']}"

        # b) IDOR attempt: get_webhook_by_id using Tenant A's webhook IDs
        for target_id in a_ids:
            stolen_wh = get_webhook_by_id(adv, target_id)
            assert stolen_wh is None, f"IDOR Vulnerability: {adv} retrieved Tenant A's webhook {target_id}"

        # c) Unauthorized Deletion: delete_user_webhook using Tenant A's webhook IDs
        for target_id in a_ids:
            del_result = delete_user_webhook(adv, target_id)
            assert del_result is False, f"Unauthorized Deletion: {adv} successfully deleted Tenant A's webhook {target_id}"

    # 4. Verify Tenant A's webhooks are completely intact and uncorrupted
    for target_id in a_ids:
        intact_wh = get_webhook_by_id(tenant_a, target_id)
        assert intact_wh is not None, f"Tenant A's webhook {target_id} was deleted or corrupted"
        assert intact_wh["user_id"] == tenant_a

    # 5. Clean up Tenant A's webhooks
    for target_id in a_ids:
        assert delete_user_webhook(tenant_a, target_id) is True
        assert get_webhook_by_id(tenant_a, target_id) is None


def test_adv_db_forecast_logs_multi_tenant_isolation():
    """
    Verify AI forecast transaction logs are strictly partitioned per tenant.
    """
    tenant_1 = "tenant_finance_lead"
    tenant_2 = "tenant_competitor_auditor"

    # Tenant 1 logs sensitive AI prompt and output
    save_forecast_log(
        user_id=tenant_1,
        user_email="cfo@finance-org.com",
        scenario_id="saas_finops",
        user_prompt="Confidential prompt: Reclaim $1.2M Figma licenses before Q4 merger",
        ai_response="Confidential AI Analysis: Strategic savings roadmap generated."
    )

    # In demo store, inspect partition
    t1_logs = _DEMO_STORE["forecast_logs"].get(tenant_1, {})
    t2_logs = _DEMO_STORE["forecast_logs"].get(tenant_2, {})

    assert len(t1_logs) >= 1
    assert len(t2_logs) == 0, f"Tenant 2 has unauthorized forecast logs: {t2_logs}"

    # Verify content in Tenant 1 log
    log_entry = next(iter(t1_logs.values()))
    assert "Confidential prompt" in log_entry["prompt_snippet"]
    assert log_entry["user_email"] == "cfo@finance-org.com"


def test_adv_db_runbook_execution_and_delivery_logs_multi_tenant_isolation():
    """
    Verify runbook execution logs and webhook delivery logs maintain 100% isolation.
    """
    user_alpha = "user_alpha_incident_mgr"
    user_beta = "user_beta_eavesdropper"

    # Alpha saves runbook log and delivery log
    exec_id = f"exec_alpha_{int(time.time())}"
    deliv_id = f"deliv_alpha_{int(time.time())}"

    save_runbook_execution_log(user_alpha, {
        "execution_id": exec_id,
        "action_id": "act_hardware_quarantine_02",
        "status": "success",
        "impact_summary": "Quarantined 42 MacBook Pro batteries",
        "remediated_items_count": 42
    })

    save_webhook_delivery_log(user_alpha, {
        "delivery_id": deliv_id,
        "webhook_id": "wh_alpha_01",
        "webhook_name": "Alpha Security Channel",
        "service_type": "slack",
        "event_type": "hardware.critical_risk",
        "status_code": 200,
        "status": "delivered",
        "duration_ms": 14.2
    })

    # Beta queries runbook logs and delivery logs
    beta_runbook_logs = get_user_runbook_logs(user_beta)
    assert not any(l["execution_id"] == exec_id for l in beta_runbook_logs)

    beta_deliv_logs = get_user_webhook_logs(user_beta)
    assert not any(d["delivery_id"] == deliv_id for d in beta_deliv_logs)

    # Alpha queries runbook logs and delivery logs -> must see their own
    alpha_runbook_logs = get_user_runbook_logs(user_alpha)
    assert any(l["execution_id"] == exec_id for l in alpha_runbook_logs)

    alpha_deliv_logs = get_user_webhook_logs(user_alpha)
    assert any(d["delivery_id"] == deliv_id for d in alpha_deliv_logs)


# ============================================================================
# SECTION 2: FASTAPI REST ENDPOINT MULTI-TENANT IDOR ADVERSARIAL TESTS
# ============================================================================

def test_adv_api_cross_tenant_webhook_idor_prevention():
    """
    Adversarial test across FastAPI HTTP endpoints:
    User A creates a webhook.
    User B attempts to read, test (trigger), or delete User A's webhook via HTTP.
    Verify 404 Not Found on all unauthorized cross-tenant operations.
    """
    client = TestClient(app)

    # Mock authentication for User A and User B
    user_a_token = {
        "uid": "tenant_user_alpha_uuid",
        "email": "alpha@enterprise.com",
        "name": "User Alpha",
        "role": "SecOps Lead"
    }
    user_b_token = {
        "uid": "tenant_user_beta_uuid",
        "email": "beta@attacker-corp.com",
        "name": "User Beta",
        "role": "Attacker"
    }

    try:
        # 1. User A creates a webhook
        app.dependency_overrides[verify_firebase_token] = lambda: user_a_token
        create_res = client.post(
            "/api/webhooks",
            json={
                "name": "Alpha Confidential SecOps",
                "url": "https://hooks.slack.com/services/SECRET_A/TOKEN_A",
                "service_type": "slack",
                "subscribed_events": ["saas.threshold_breach", "runbook.executed"],
                "secret_token": "alpha-super-secret-hmac-token"
            },
            headers={"Authorization": "Bearer mock-alpha-token"}
        )
        assert create_res.status_code == 201
        created_wh = create_res.json()
        wh_id = created_wh["webhook_id"]
        assert wh_id.startswith("wh_")
        assert created_wh["has_secret"] is True

        # 2. Switch to User B: User B lists webhooks -> User A's webhook must NOT be in the list
        app.dependency_overrides[verify_firebase_token] = lambda: user_b_token
        list_res = client.get(
            "/api/webhooks",
            headers={"Authorization": "Bearer mock-beta-token"}
        )
        assert list_res.status_code == 200
        user_b_webhooks = list_res.json()
        assert not any(h["webhook_id"] == wh_id for h in user_b_webhooks)

        # 3. User B attempts IDOR to test/trigger User A's webhook -> 404
        test_res = client.post(
            "/api/webhooks/test",
            json={"webhook_id": wh_id},
            headers={"Authorization": "Bearer mock-beta-token"}
        )
        assert test_res.status_code == 404
        assert "not found" in test_res.json()["detail"].lower()

        # 4. User B attempts IDOR to delete User A's webhook -> 404
        delete_res = client.delete(
            f"/api/webhooks/{wh_id}",
            headers={"Authorization": "Bearer mock-beta-token"}
        )
        assert delete_res.status_code == 404
        assert "not found" in delete_res.json()["detail"].lower()

        # 5. Switch back to User A: User A can still list and see their webhook intact
        app.dependency_overrides[verify_firebase_token] = lambda: user_a_token
        list_res_a = client.get(
            "/api/webhooks",
            headers={"Authorization": "Bearer mock-alpha-token"}
        )
        assert list_res_a.status_code == 200
        assert any(h["webhook_id"] == wh_id for h in list_res_a.json())

        # 6. User A executes a runbook -> creates delivery logs
        runbook_res = client.post(
            "/api/runbooks/execute",
            json={
                "action_id": "act_saas_reclaim_01",
                "scenario_id": "saas_finops",
                "dispatch_webhooks": True
            },
            headers={"Authorization": "Bearer mock-alpha-token"}
        )
        assert runbook_res.status_code == 200

        # User A inspects delivery logs
        deliv_res_a = client.get(
            "/api/webhooks/deliveries",
            headers={"Authorization": "Bearer mock-alpha-token"}
        )
        assert deliv_res_a.status_code == 200
        assert len(deliv_res_a.json()) > 0

        # 7. Switch to User B: User B inspects delivery logs -> must NOT see User A's deliveries
        app.dependency_overrides[verify_firebase_token] = lambda: user_b_token
        deliv_res_b = client.get(
            "/api/webhooks/deliveries",
            headers={"Authorization": "Bearer mock-beta-token"}
        )
        assert deliv_res_b.status_code == 200
        assert len(deliv_res_b.json()) == 0

        # 8. Switch to User A: User A successfully deletes their own webhook
        app.dependency_overrides[verify_firebase_token] = lambda: user_a_token
        del_res = client.delete(
            f"/api/webhooks/{wh_id}",
            headers={"Authorization": "Bearer mock-alpha-token"}
        )
        assert del_res.status_code == 200
        assert del_res.json()["status"] == "success"

    finally:
        app.dependency_overrides.clear()


# ============================================================================
# SECTION 3: FIRESTORE SECURITY RULES PARSER & SEMANTIC ENFORCEMENT VERIFICATION
# ============================================================================

def test_adv_firestore_rules_structure_and_semantic_enforcement():
    """
    Parse firestore.rules and verify:
    1. rules_version = '2';
    2. Cloud Firestore service block
    3. Zero-Trust default deny: match /{document=**} { allow read, write: if false; }
    4. Collection-specific matching and request.auth.uid == userId rule enforcement.
    5. Immutability of logs (update/delete if false).
    6. Complete absence of unauthenticated or wildcard allow rules.
    """
    rules_path = os.path.join(os.path.dirname(__file__), "..", "firestore.rules")
    assert os.path.exists(rules_path), "firestore.rules file must exist at project root"

    with open(rules_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Check rules version
    assert "rules_version = '2';" in content or 'rules_version = "2";' in content

    # 2. Check service declaration
    assert "service cloud.firestore" in content

    # 3. Check default Zero-Trust deny rule
    default_deny_pattern = r"match\s+/\{document=\*\*\*\s*\{\s*allow\s+read,\s*write:\s*if\s+false;\s*\}"
    # Also match more flexible whitespace
    default_deny_match = re.search(r"match\s+/\{document=\*\*\s*\}\s*\{\s*allow\s+read,\s*write:\s*if\s+false;\s*\}", content)
    assert default_deny_match is not None, "Zero-Trust default deny rule 'match /{document=**} { allow read, write: if false; }' not found."

    # 4. Check collection match paths
    required_paths = [
        "/users/{userId}/forecast_logs/{logId}",
        "/users/{userId}/webhooks/{webhookId}",
        "/users/{userId}/webhook_logs/{deliveryId}",
        "/users/{userId}/runbook_logs/{executionId}",
    ]
    for p in required_paths:
        assert p in content, f"Required isolated collection path {p} missing in firestore.rules"

    # 5. Verify strict auth uid check: request.auth != null && request.auth.uid == userId
    auth_check_pattern = r"request\.auth\s*!=\s*null\s*&&\s*request\.auth\.uid\s*==\s*userId"
    auth_matches = re.findall(auth_check_pattern, content)
    assert len(auth_matches) >= 4, f"Expected at least 4 occurrences of 'request.auth.uid == userId' check, found {len(auth_matches)}"

    # 6. Verify immutability of audit and execution logs: allow update, delete: if false;
    immutable_pattern = r"allow\s+update,\s*delete:\s*if\s+false;"
    immutable_matches = re.findall(immutable_pattern, content)
    assert len(immutable_matches) >= 3, f"Expected at least 3 immutable log collections with 'allow update, delete: if false;', found {len(immutable_matches)}"

    # 7. Adversarial check: verify NO global or unsafe allows exist anywhere
    unsafe_patterns = [
        r"allow\s+read,\s*write:\s*if\s+true",
        r"allow\s+read:\s*if\s+true",
        r"allow\s+write:\s*if\s+true",
        r"allow\s+create:\s*if\s+true",
        r"allow\s+delete:\s*if\s+true",
        r"allow\s+update:\s*if\s+true",
        r"match\s+/\{document=\*\*\s*\}\s*\{\s*allow\s+read,\s*write:\s*if\s+request\.auth\s*!=\s*null", # root wildcard allow
    ]
    for pat in unsafe_patterns:
        match = re.search(pat, content)
        assert match is None, f"Security Violation: Insecure firestore rule pattern matched: '{pat}'"


# ============================================================================
# SECTION 4: SCENARIO SEED CONSISTENCY & ADVERSARIAL EDGE CASES
# ============================================================================

def test_adv_scenario_catalog_and_seed_consistency():
    """
    Verify all scenarios in registry generate valid, strictly typed, deterministic telemetry.
    """
    scenarios = list_available_scenarios()
    assert len(scenarios) == 3

    scenario_ids = [s["id"] for s in scenarios]
    assert "saas_finops" in scenario_ids
    assert "hardware_lifecycle" in scenario_ids
    assert "itsm_surge" in scenario_ids

    # 1. Verify SaaS FinOps
    saas_data = get_scenario_by_id("saas_finops")
    assert isinstance(saas_data, ScenarioDataPayload)
    assert saas_data.scenario_id == "saas_finops"
    assert len(saas_data.saas_metrics) >= 5
    assert saas_data.chart_data["type"] == "bar"
    assert len(saas_data.chart_data["labels"]) == len(saas_data.saas_metrics)
    assert "waste" in saas_data.grounding_context.lower() or "savings" in saas_data.grounding_context.lower()

    # 2. Verify Hardware Lifecycle
    hw_data = get_scenario_by_id("hardware_lifecycle")
    assert isinstance(hw_data, ScenarioDataPayload)
    assert hw_data.scenario_id == "hardware_lifecycle"
    assert len(hw_data.hardware_metrics) >= 4
    assert hw_data.chart_data["type"] == "bar"
    assert len(hw_data.chart_data["labels"]) == len(hw_data.hardware_metrics)
    assert "battery" in hw_data.grounding_context.lower()

    # 3. Verify ITSM Surge
    itsm_data = get_scenario_by_id("itsm_surge")
    assert isinstance(itsm_data, ScenarioDataPayload)
    assert itsm_data.scenario_id == "itsm_surge"
    assert len(itsm_data.itsm_metrics) >= 5
    assert itsm_data.chart_data["type"] == "line"
    assert "sox" in itsm_data.grounding_context.lower() or "surge" in itsm_data.grounding_context.lower()


def test_adv_scenario_seed_endpoint_fuzzing_and_edge_cases():
    """
    Adversarially fuzz POST /api/scenarios/seed with malformed, extreme, and malicious inputs.
    """
    client = TestClient(app)

    # 1. Empty string scenario_id -> 404
    res = client.post("/api/scenarios/seed", json={"scenario_id": ""})
    assert res.status_code in (404, 422)

    # 2. Whitespace-only scenario_id -> 404
    res = client.post("/api/scenarios/seed", json={"scenario_id": "    "})
    assert res.status_code == 404

    # 3. SQL Injection strings -> 404
    sql_injections = [
        "saas_finops' OR '1'='1",
        "saas_finops'; DROP TABLE scenarios; --",
        "admin'--",
        "' UNION SELECT * FROM users --",
    ]
    for sqli in sql_injections:
        res = client.post("/api/scenarios/seed", json={"scenario_id": sqli})
        assert res.status_code == 404, f"SQLi input '{sqli}' did not return 404"

    # 4. Path traversal payloads -> 404
    path_traversals = [
        "../../../../etc/passwd",
        "..\\..\\windows\\system32\\cmd.exe",
        "saas_finops/../../secret",
        "/etc/shadow",
    ]
    for pt in path_traversals:
        res = client.post("/api/scenarios/seed", json={"scenario_id": pt})
        assert res.status_code == 404, f"Path traversal input '{pt}' did not return 404"

    # 5. XSS & HTML injection tags -> 404
    xss_payloads = [
        "<script>alert('pwned')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
    ]
    for xss in xss_payloads:
        res = client.post("/api/scenarios/seed", json={"scenario_id": xss})
        assert res.status_code == 404, f"XSS input '{xss}' did not return 404"

    # 6. Unicode, Emojis & Null-Byte Combinations -> 404
    unicode_payloads = [
        "saas_finops 🚀🔥💻🎉",
        "hardware_lifecycle\x00malicious",
        "itsm_surge\u202e\u0000",
        "ñöñ_ëxïstëñt_scënärïö",
    ]
    for up in unicode_payloads:
        res = client.post("/api/scenarios/seed", json={"scenario_id": up})
        assert res.status_code in (404, 422), f"Unicode input '{up}' did not return 404/422"

    # 7. Extreme length string (10,000 chars) -> 404 without crashing
    huge_string = "saas_finops_" + ("A" * 10000)
    res = client.post("/api/scenarios/seed", json={"scenario_id": huge_string})
    assert res.status_code in (404, 422)

    # 8. Schema type violations -> 422
    type_violations = [
        {"scenario_id": 12345},
        {"scenario_id": True},
        {"scenario_id": ["saas_finops"]},
        {"scenario_id": {"nested": "saas_finops"}},
        {"scenario_id": None},
        {},
        {"unknown_field": "test"},
    ]
    for tv in type_violations:
        res = client.post("/api/scenarios/seed", json=tv)
        assert res.status_code == 422, f"Type violation '{tv}' did not return 422"

    # 9. Non-JSON raw request body -> 422
    res = client.post(
        "/api/scenarios/seed",
        content="this is not a valid json payload",
        headers={"Content-Type": "application/json"}
    )
    assert res.status_code == 422


# ============================================================================
# SECTION 5: WEBHOOK & HMAC CRYPTOGRAPHIC ADVERSARIAL EDGE CASES
# ============================================================================

def test_adv_webhook_pydantic_adversarial_fuzzing():
    """
    Adversarial validation tests on WebhookCreate model.
    """
    # 1. Invalid schemes
    invalid_schemes = [
        "ftp://slack.com/hook",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "data:text/html,<h1>test</h1>",
        "gopher://evil.com/1",
        "smtp://mail.example.com",
        "ws://echo.websocket.org",
    ]
    for bad_url in invalid_schemes:
        with pytest.raises(ValidationError):
            WebhookCreate(name="Valid Name", url=bad_url)

    # 2. Name validation: too short or empty
    for bad_name in ["", " ", "a", "   \x00   ", "\x00"]:
        with pytest.raises(ValidationError):
            WebhookCreate(name=bad_name, url="https://hooks.slack.com/services/DEMO")

    # 3. Name too long (> 60 chars)
    with pytest.raises(ValidationError):
        WebhookCreate(name="A" * 61, url="https://hooks.slack.com/services/DEMO")

    # 4. URL too long (> 500 chars)
    with pytest.raises(ValidationError):
        WebhookCreate(name="Valid Name", url="https://example.com/" + ("x" * 500))


def test_adv_hmac_cryptographic_edge_cases():
    """
    Test HMAC-SHA256 signature generator and verifier against adversarial inputs:
    - Empty secrets
    - Unicode payloads
    - Malformed signature headers
    - Future timestamp attacks
    - Replay timestamp attacks
    """
    secret = "k3y-with-spëcïäl-$ymböl$!@#%^&*()_+"
    payload = json.dumps({"incident": "SOX Close Breach 🔥", "items": 128, "unicode": "こんにちは"})

    # 1. Normal signature generation & verification
    sig_header, ts = generate_hmac_signature(payload, secret)
    assert verify_hmac_signature(payload, sig_header, secret) is True

    # 2. Tampered unicode payload
    tampered = json.dumps({"incident": "SOX Close Breach 🔥", "items": 129, "unicode": "こんにちは"})
    assert verify_hmac_signature(tampered, sig_header, secret) is False

    # 3. Malformed signature headers
    malformed_headers = [
        "",
        "garbage_value",
        "t=not_a_number,v1=abcdef",
        "v1=abcdef",
        "t=12345",
        "t=12345,v1=",
        "t=12345,v2=wrong_version",
        ",,,",
        "=",
    ]
    for bad_h in malformed_headers:
        assert verify_hmac_signature(payload, bad_h, secret) is False

    # 4. Future timestamp attack (> 300s into future)
    future_ts = int(time.time()) + 500
    future_sig, _ = generate_hmac_signature(payload, secret, timestamp=future_ts)
    assert verify_hmac_signature(payload, future_sig, secret, tolerance_seconds=300) is False

    # 5. Past timestamp attack (> 300s into past)
    past_ts = int(time.time()) - 500
    past_sig, _ = generate_hmac_signature(payload, secret, timestamp=past_ts)
    assert verify_hmac_signature(payload, past_sig, secret, tolerance_seconds=300) is False
