"""
WorkplacePulse - Autonomous Incident Runbook Remediation Engine
Executes automated, one-click remediation runbooks across enterprise IT scenarios and coordinates multi-platform webhook alerting.
"""

import uuid
import logging
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from webhook_service import (
    WebhookServiceType,
    WebhookEventType,
    WebhookDeliveryLog,
    format_payload_for_service,
    dispatch_webhook_with_retry,
)
from database import (
    get_user_webhooks,
    save_webhook_delivery_log,
    save_runbook_execution_log,
)

logger = logging.getLogger("WorkplacePulse.Runbooks")


# ---------------------------------------------------------
# Runbook Data Models
# ---------------------------------------------------------

class RunbookRemediationType(str, Enum):
    AUTOMATIC = "automatic"
    ONE_CLICK_APPROVAL = "one_click_approval"
    MANUAL_GUIDED = "manual_guided"


class RunbookAction(BaseModel):
    action_id: str
    scenario_id: str
    title: str
    category: str
    description: str
    target_system: str
    remediation_type: RunbookRemediationType
    estimated_impact: str
    parameters_schema: Dict[str, Any]
    default_parameters: Dict[str, Any]


class RunbookExecuteRequest(BaseModel):
    action_id: str = Field(..., description="Unique identifier of the runbook action to execute")
    scenario_id: str = Field(..., description="Active scenario context identifier")
    custom_parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    dispatch_webhooks: bool = Field(default=True, description="Whether to trigger webhook alerting upon execution")


class RunbookExecuteResponse(BaseModel):
    execution_id: str
    action_id: str
    scenario_id: str
    status: str  # "success", "partial_success", "failed"
    executed_by: str
    timestamp: str
    execution_log: List[str]
    impact_summary: str
    remediated_items_count: int
    webhook_deliveries: List[WebhookDeliveryLog]


# ---------------------------------------------------------
# Pre-Built Incident Runbook Catalog
# ---------------------------------------------------------

RUNBOOK_CATALOG: Dict[str, RunbookAction] = {
    "act_saas_reclaim_01": RunbookAction(
        action_id="act_saas_reclaim_01",
        scenario_id="saas_finops",
        title="Okta SCIM License Deprovisioner",
        category="SaaS FinOps",
        description="Scans simulated SaaS directories for inactive seats (>60 days), revokes provisioned entitlements via SCIM 2.0, and notifies department heads.",
        target_system="Okta Universal Directory / SCIM 2.0 API",
        remediation_type=RunbookRemediationType.ONE_CLICK_APPROVAL,
        estimated_impact="Recovers up to $118,260.00/yr in recurring SaaS waste across Figma, Zoom, and Notion.",
        parameters_schema={
            "inactive_days_threshold": {"type": "integer", "default": 60, "minimum": 30},
            "target_apps": {"type": "array", "items": {"type": "string"}, "default": ["Figma", "Zoom", "Notion"]},
            "send_manager_notice": {"type": "boolean", "default": True}
        },
        default_parameters={
            "inactive_days_threshold": 60,
            "target_apps": ["Figma", "Zoom", "Notion"],
            "send_manager_notice": True
        }
    ),
    "act_hardware_quarantine_02": RunbookAction(
        action_id="act_hardware_quarantine_02",
        scenario_id="hardware_lifecycle",
        title="Jamf Pro Battery Quarantine & Depot Refresh",
        category="Endpoint Hardware",
        description="Flags endpoint devices with battery cycles >800 or health <75%, creates warranty RMA tickets in ERP, and pushes maintenance profiles via MDM.",
        target_system="Jamf Pro MDM / Apple Device Enrollment",
        remediation_type=RunbookRemediationType.ONE_CLICK_APPROVAL,
        estimated_impact="Mitigates 42 potential catastrophic battery swelling failures and initiates warranty depot replacements.",
        parameters_schema={
            "battery_cycle_threshold": {"type": "integer", "default": 800},
            "battery_health_min": {"type": "integer", "default": 75},
            "auto_create_rma": {"type": "boolean", "default": True}
        },
        default_parameters={
            "battery_cycle_threshold": 800,
            "battery_health_min": 75,
            "auto_create_rma": True
        }
    ),
    "act_itsm_sox_fasttrack_03": RunbookAction(
        action_id="act_itsm_sox_fasttrack_03",
        scenario_id="itsm_surge",
        title="Emergency SOX Fast-Track Dual-Signer Approval Matrix",
        category="ITSM Service Desk",
        description="Activates a 72-hour pre-approved dual-signer matrix for Month-End Close access requests, unblocking accounting staff and slashing MTTR.",
        target_system="Jira Service Management / ServiceNow",
        remediation_type=RunbookRemediationType.ONE_CLICK_APPROVAL,
        estimated_impact="Reduces Financial Close MTTR from 3.8 hours to 12 minutes during Days -3 to +3 of Month-End.",
        parameters_schema={
            "window_duration_hours": {"type": "integer", "default": 72, "maximum": 120},
            "emergency_tier": {"type": "string", "default": "SOX-Tier1-Finance"},
            "escalate_p1": {"type": "boolean", "default": True}
        },
        default_parameters={
            "window_duration_hours": 72,
            "emergency_tier": "SOX-Tier1-Finance",
            "escalate_p1": True
        }
    )
}


def list_available_runbooks() -> List[RunbookAction]:
    """Returns all pre-built runbooks in the catalog."""
    return list(RUNBOOK_CATALOG.values())


def get_runbook_by_id(action_id: str) -> Optional[RunbookAction]:
    """Retrieves a specific runbook definition by action ID."""
    return RUNBOOK_CATALOG.get(action_id)


def get_runbook_for_scenario(scenario_id: str) -> Optional[RunbookAction]:
    """Finds the primary runbook matching a given scenario preset."""
    for action in RUNBOOK_CATALOG.values():
        if action.scenario_id == scenario_id:
            return action
    return None


# ---------------------------------------------------------
# Runbook Execution Handler
# ---------------------------------------------------------

async def execute_runbook(
    user_id: str,
    user_email: str,
    action_id: str,
    scenario_id: str,
    custom_parameters: Optional[Dict[str, Any]] = None,
    dispatch_webhooks: bool = True
) -> RunbookExecuteResponse:
    """
    Executes a runbook remediation action, generates audit logs, and dispatches webhook notifications.
    """
    runbook = get_runbook_by_id(action_id)
    if not runbook:
        raise ValueError(f"Runbook action '{action_id}' not found in catalog.")

    if runbook.scenario_id != scenario_id:
        logger.warning(f"Runbook scenario mismatch: {runbook.scenario_id} != {scenario_id}")

    execution_id = f"exec_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.now(timezone.utc).isoformat()
    params = {**runbook.default_parameters, **(custom_parameters or {})}

    execution_log: List[str] = []
    impact_summary = ""
    remediated_items_count = 0

    # 1. Simulate Domain-Specific Execution Steps
    if action_id == "act_saas_reclaim_01":
        days_thresh = params.get("inactive_days_threshold", 60)
        apps = params.get("target_apps", ["Figma", "Zoom", "Notion"])
        base_time = datetime.now(timezone.utc)
        
        t0 = base_time.isoformat()
        t1 = (base_time + timedelta(milliseconds=120)).isoformat()
        t2 = (base_time + timedelta(milliseconds=280)).isoformat()
        t3 = (base_time + timedelta(milliseconds=450)).isoformat()
        t4 = (base_time + timedelta(milliseconds=620)).isoformat()
        t5 = (base_time + timedelta(milliseconds=790)).isoformat()
        t6 = (base_time + timedelta(milliseconds=940)).isoformat()
        t7 = (base_time + timedelta(milliseconds=1120)).isoformat()

        execution_log.append(f"[{t0}] Initializing SCIM 2.0 connector to Okta Universal Directory...")
        execution_log.append(f"[{t1}] Querying active enterprise directories for inactive seat threshold > {days_thresh} days...")
        execution_log.append(f"[{t2}] Discovered 365 inactive licenses across 3 target applications: {', '.join(apps)}.")
        execution_log.append(f"[{t3}] [Stage 1/3] Revoking 65 dormant Figma Enterprise seats @ $75.00/mo ($4,875.00/mo • $58,500.00/yr saved).")
        execution_log.append(f"[{t4}] [Stage 2/3] Transitioning 160 unutilized Zoom Pro hosts @ $18.00/mo ($2,880.00/mo • $34,560.00/yr saved).")
        execution_log.append(f"[{t5}] [Stage 3/3] Reclaiming 140 idle Notion Team seats @ $15.00/mo ($2,100.00/mo • $25,200.00/yr saved).")
        if params.get("send_manager_notice", True):
            execution_log.append(f"[{t6}] Dispatched automated seat reclaim notices to 14 departmental billing owners via Okta Event Hooks.")
        execution_log.append(f"[{t7}] Emitted immutable audit log to Cloud Firestore Native and SIEM.")
        impact_summary = "Successfully reclaimed 365 inactive licenses across Figma, Zoom, and Notion, realizing $118,260.00/yr in recurring savings."
        remediated_items_count = 365

    elif action_id == "act_hardware_quarantine_02":
        cycle_thresh = params.get("battery_cycle_threshold", 800)
        execution_log.append(f"[{timestamp}] Connecting to Jamf Pro MDM Cloud API endpoint...")
        execution_log.append(f"[{timestamp}] Evaluating telemetry for battery cycle count > {cycle_thresh} or health < 75%...")
        execution_log.append(f"[{timestamp}] Isolated 42 high-risk devices (30 MacBook Pro 16\", 12 Dell XPS 15).")
        execution_log.append(f"[{timestamp}] Pushed Jamf Pro self-service prompt 'Battery Depot Replacement Required' to affected users.")
        if params.get("auto_create_rma", True):
            execution_log.append(f"[{timestamp}] Generated AppleCare / Dell ProSupport enterprise warranty RMA batch #RMA-2026-0901.")
        execution_log.append(f"[{timestamp}] Reserved 42 hot-swap loaner units in Central IT Depot.")
        execution_log.append(f"[{timestamp}] Hardware risk status mitigated; audit trail written to Firestore.")
        impact_summary = "Quarantined 42 critical wear endpoints, scheduled depot refresh, and eliminated outage risk."
        remediated_items_count = 42

    elif action_id == "act_itsm_sox_fasttrack_03":
        duration = params.get("window_duration_hours", 72)
        tier = params.get("emergency_tier", "SOX-Tier1-Finance")
        execution_log.append(f"[{timestamp}] Activating emergency ITSM bypass window ({duration}h) for Month-End Close...")
        execution_log.append(f"[{timestamp}] Applied pre-approved dual-signer matrix: {tier} in Jira Service Management.")
        execution_log.append(f"[{timestamp}] Auto-triaging 87 pending ERP/NetSuite/FloQast access requests...")
        execution_log.append(f"[{timestamp}] Auto-approved 64 standard financial close requests meeting SOX Tier 1 criteria.")
        execution_log.append(f"[{timestamp}] Escalated 23 elevated permission requests to on-call IT Director with SMS alert.")
        execution_log.append(f"[{timestamp}] Month-End average resolution MTTR reduced from 3.8 hrs to 11.4 minutes.")
        execution_log.append(f"[{timestamp}] Compliance ledger signed with cryptographic timestamp.")
        impact_summary = "Fast-tracked 64 Month-End access requests, resolving backlog surge and protecting close deadline."
        remediated_items_count = 64

    else:
        execution_log.append(f"[{timestamp}] Executing generic automated runbook: {action_id}...")
        execution_log.append(f"[{timestamp}] Remediation steps completed successfully.")
        impact_summary = f"Runbook {action_id} completed successfully."
        remediated_items_count = 1

    # 2. Webhook Notification Dispatch
    webhook_deliveries: List[WebhookDeliveryLog] = []

    if dispatch_webhooks:
        registered_webhooks = get_user_webhooks(user_id)
        # If user has not yet registered any webhooks, create a simulated default alert
        target_webhooks = registered_webhooks if registered_webhooks else [{
            "webhook_id": "default_sandbox_slack",
            "name": "Default IT Operations Alert Channel",
            "url": "https://hooks.slack.com/services/DEMO/WORKPLACEPULSE/DEFAULT",
            "service_type": "slack",
            "subscribed_events": ["runbook.executed"],
            "secret_token": None,
            "is_active": True
        }]

        event_type = WebhookEventType.RUNBOOK_EXECUTED
        runbook_payload_data = {
            "execution_id": execution_id,
            "action_id": action_id,
            "scenario_id": scenario_id,
            "status": "success",
            "executed_by": user_email or user_id,
            "impact_summary": impact_summary,
            "remediated_items_count": remediated_items_count,
            "timestamp": timestamp
        }

        title = f"Runbook Executed: {runbook.title}"
        message = f"**{runbook.title}** was executed by `{user_email or user_id}` in scenario `{scenario_id}`.\n\n**Impact**: {impact_summary}"

        for wh in target_webhooks:
            if not wh.get("is_active", True):
                continue

            srv_type_str = wh.get("service_type", "slack").lower()
            try:
                srv_type = WebhookServiceType(srv_type_str)
            except ValueError:
                srv_type = WebhookServiceType.GENERIC

            payload = format_payload_for_service(
                service_type=srv_type,
                title=title,
                message=message,
                runbook_data=runbook_payload_data,
                event_type=event_type
            )

            delivery_log = await dispatch_webhook_with_retry(
                url=wh.get("url", "https://hooks.slack.com/services/DEMO"),
                payload=payload,
                service_type=srv_type_str,
                secret_token=wh.get("secret_token"),
                event_type=event_type,
                webhook_id=wh.get("webhook_id", "wh_unknown"),
                webhook_name=wh.get("name", "Alert Destination"),
                max_retries=1,
                timeout=2.0
            )

            # Persist delivery log in Firestore
            save_webhook_delivery_log(user_id, delivery_log.model_dump())
            webhook_deliveries.append(delivery_log)

    # 3. Persist Immutable Runbook Execution Log
    execution_record = {
        "execution_id": execution_id,
        "action_id": action_id,
        "scenario_id": scenario_id,
        "status": "success",
        "executed_by": user_email or user_id,
        "timestamp": timestamp,
        "execution_log": execution_log,
        "impact_summary": impact_summary,
        "remediated_items_count": remediated_items_count,
        "parameters": params,
        "webhook_deliveries_count": len(webhook_deliveries)
    }
    save_runbook_execution_log(user_id, execution_record)

    return RunbookExecuteResponse(
        execution_id=execution_id,
        action_id=action_id,
        scenario_id=scenario_id,
        status="success",
        executed_by=user_email or user_id,
        timestamp=timestamp,
        execution_log=execution_log,
        impact_summary=impact_summary,
        remediated_items_count=remediated_items_count,
        webhook_deliveries=webhook_deliveries
    )
