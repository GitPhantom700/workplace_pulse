"""
WorkplacePulse - FastAPI Application Backend
Serves REST APIs for synthetic enterprise telemetry, Gemini multi-turn forecasting, 
autonomous incident runbooks, multi-platform webhooks, and static frontend assets.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from data_engine import (
    get_scenario_by_id, 
    list_available_scenarios, 
    ScenarioDataPayload
)
from ai_service import generate_multi_turn_forecast
from security import verify_firebase_token
from database import (
    save_forecast_log,
    save_webhook_config,
    get_user_webhooks,
    get_webhook_by_id,
    delete_user_webhook,
    save_webhook_delivery_log,
    get_user_webhook_logs,
    get_user_runbook_logs
)
from webhook_service import (
    WebhookCreate,
    WebhookResponse,
    WebhookDeliveryLog,
    WebhookTestRequest,
    WebhookServiceType,
    WebhookEventType,
    mask_webhook_url,
    format_payload_for_service,
    dispatch_webhook_with_retry
)
from runbook_service import (
    RunbookAction,
    RunbookExecuteRequest,
    RunbookExecuteResponse,
    list_available_runbooks,
    get_runbook_by_id,
    execute_runbook
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkplacePulse")

app = FastAPI(
    title="WorkplacePulse API",
    description="Enterprise IT & SaaS Predictive Operations Command Center with Autonomous Runbook Remediation",
    version="1.1.0"
)

# Configure CORS origins cleanly and securely
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|.*\.run\.app)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# ---------------------------------------------------------
# Pydantic Request Models & Sanitation (Task 25)
# ---------------------------------------------------------

class ChatMessageModel(BaseModel):
    role: str
    content: str

    @field_validator("content")
    def sanitize_content(cls, v: str) -> str:
        if not v:
            raise ValueError("Message content cannot be empty.")
        sanitized = v.replace("\x00", "").strip()
        if not sanitized:
            raise ValueError("Message content cannot be empty or whitespace only.")
        if len(sanitized) > 4000:
            raise ValueError("Message exceeds maximum allowed character length (4000).")
        return sanitized

    @field_validator("role")
    def validate_role(cls, v: str) -> str:
        if v not in ["user", "model", "assistant"]:
            raise ValueError("Role must be 'user' or 'model'/'assistant'.")
        return v


class ForecastChatRequest(BaseModel):
    scenario_id: str = Field(..., description="The ID of the active scenario preset")
    message: str = Field(..., description="User's prompt or question")
    history: List[ChatMessageModel] = Field(default_factory=list, description="Previous conversation turns")

    @field_validator("message")
    def sanitize_message(cls, v: str) -> str:
        if not v:
            raise ValueError("Message content cannot be empty.")
        sanitized = v.replace("\x00", "").strip()
        if not sanitized:
            raise ValueError("Message content cannot be empty or whitespace only.")
        if len(sanitized) > 4000:
            raise ValueError("Message exceeds maximum allowed character length (4000).")
        return sanitized


class SeedScenarioRequest(BaseModel):
    scenario_id: str = Field(..., description="ID of the preset scenario to generate")


# ---------------------------------------------------------
# REST Endpoints (Tasks 21 - 24)
# ---------------------------------------------------------

@app.get("/api/health", tags=["System"])
async def health_check():
    """Task 24: Health check endpoint for Cloud Run container liveness."""
    return {
        "status": "healthy",
        "service": "WorkplacePulse",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.environ.get("ENV", "production")
    }


@app.get("/api/scenarios", tags=["Scenarios"])
async def get_scenarios():
    """List all available enterprise scenario presets."""
    return {
        "status": "success",
        "scenarios": list_available_scenarios()
    }


@app.post("/api/scenarios/seed", response_model=ScenarioDataPayload, tags=["Scenarios"])
async def seed_scenario(payload: SeedScenarioRequest):
    """
    Task 22: Generate high-fidelity synthetic telemetry for a chosen scenario.
    Provides immediate grounding data for both charts and AI chat.
    """
    logger.info(f"Generating synthetic telemetry for scenario: {payload.scenario_id}")
    data = get_scenario_by_id(payload.scenario_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{payload.scenario_id}' not found."
        )
    return data


from fastapi import Header
from typing import Optional

@app.post("/api/forecast/chat", tags=["Forecasting"])
async def forecast_chat(
    payload: ForecastChatRequest,
    user_token: dict = Depends(verify_firebase_token),
    x_gemini_api_key: Optional[str] = Header(None)
):
    """
    Task 23: Multi-turn forecasting conversation with Gemini.
    Protected by Firebase Auth token verification.
    """
    user_id = user_token.get("uid", "anonymous")
    user_email = user_token.get("email", "unknown")
    logger.info(f"Chat request from user: {user_id} ({user_email}) on scenario: {payload.scenario_id}")

    # Fetch current scenario grounding data
    if payload.scenario_id == "support_inquiry":
        from data_engine import build_support_grounding_context
        grounding_context = build_support_grounding_context()
    else:
        scenario_data = get_scenario_by_id(payload.scenario_id)
        if not scenario_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario '{payload.scenario_id}' not found."
            )
        grounding_context = scenario_data.grounding_context

    # Format message history
    history_dicts = [{"role": msg.role, "content": msg.content} for msg in payload.history]

    # Generate response via resilient Gemini fallback ladder
    ai_response = generate_multi_turn_forecast(
        scenario_id=payload.scenario_id,
        chat_history=history_dicts,
        user_message=payload.message,
        grounding_context=grounding_context,
        client_api_key=x_gemini_api_key
    )

    # Persist to Firestore
    save_forecast_log(
        user_id=user_id,
        user_email=user_email,
        scenario_id=payload.scenario_id,
        user_prompt=payload.message,
        ai_response=ai_response
    )

    return {
        "status": "success",
        "scenario_id": payload.scenario_id,
        "user_id": user_id,
        "response": ai_response,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ---------------------------------------------------------
# Webhook REST Endpoints (Standout Feature)
# ---------------------------------------------------------

@app.get("/api/webhooks", response_model=List[WebhookResponse], tags=["Webhooks"])
async def list_webhooks(user_token: dict = Depends(verify_firebase_token)):
    """
    List all configured webhooks for the authenticated tenant.
    URLs are masked for security.
    """
    user_id = user_token.get("uid", "anonymous")
    raw_hooks = get_user_webhooks(user_id)
    response_items = []
    for h in raw_hooks:
        srv_type = h.get("service_type", "slack")
        try:
            enum_srv = WebhookServiceType(srv_type)
        except ValueError:
            enum_srv = WebhookServiceType.GENERIC

        sub_events = []
        for ev in h.get("subscribed_events", []):
            try:
                sub_events.append(WebhookEventType(ev))
            except ValueError:
                pass

        response_items.append(WebhookResponse(
            webhook_id=h.get("webhook_id", ""),
            user_id=user_id,
            name=h.get("name", "Webhook"),
            url=mask_webhook_url(h.get("url", "")),
            service_type=enum_srv,
            subscribed_events=sub_events,
            is_active=h.get("is_active", True),
            created_at=h.get("created_at", datetime.now(timezone.utc).isoformat()),
            has_secret=bool(h.get("secret_token"))
        ))
    return response_items


@app.post("/api/webhooks", status_code=status.HTTP_201_CREATED, response_model=WebhookResponse, tags=["Webhooks"])
async def create_webhook(
    payload: WebhookCreate,
    user_token: dict = Depends(verify_firebase_token)
):
    """
    Register a new webhook destination for incident alerts and runbook triggers.
    """
    user_id = user_token.get("uid", "anonymous")
    import uuid
    webhook_id = f"wh_{uuid.uuid4().hex[:12]}"
    doc = {
        "webhook_id": webhook_id,
        "user_id": user_id,
        "name": payload.name,
        "url": payload.url,
        "service_type": payload.service_type.value,
        "subscribed_events": [e.value for e in payload.subscribed_events],
        "secret_token": payload.secret_token,
        "is_active": payload.is_active,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    saved = save_webhook_config(user_id, doc)
    return WebhookResponse(
        webhook_id=saved["webhook_id"],
        user_id=user_id,
        name=saved["name"],
        url=mask_webhook_url(saved["url"]),
        service_type=WebhookServiceType(saved["service_type"]),
        subscribed_events=[WebhookEventType(e) for e in saved["subscribed_events"]],
        is_active=saved["is_active"],
        created_at=saved["created_at"],
        has_secret=bool(saved.get("secret_token"))
    )


@app.post("/api/webhooks/test", response_model=WebhookDeliveryLog, tags=["Webhooks"])
async def test_webhook(
    payload: WebhookTestRequest,
    user_token: dict = Depends(verify_firebase_token)
):
    """
    Dispatches a live test ping payload to verify webhook delivery and latency.
    """
    user_id = user_token.get("uid", "anonymous")
    url = payload.target_url
    service_type = payload.service_type
    secret_token = None
    webhook_name = "Ad-hoc Test Destination"
    webhook_id = "test_ping"

    if payload.webhook_id:
        wh = get_webhook_by_id(user_id, payload.webhook_id)
        if not wh:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Webhook '{payload.webhook_id}' not found."
            )
        url = wh.get("url")
        srv_str = wh.get("service_type", "slack")
        try:
            service_type = WebhookServiceType(srv_str)
        except ValueError:
            service_type = WebhookServiceType.GENERIC
        secret_token = wh.get("secret_token")
        webhook_name = wh.get("name", "Registered Webhook")
        webhook_id = wh.get("webhook_id", "test_ping")

    if not url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either webhook_id or target_url must be provided."
        )

    title = "WorkplacePulse Test Ping"
    message = "🔔 This is a verified test alert from WorkplacePulse Sentinel Dispatch Engine."
    formatted = format_payload_for_service(
        service_type=service_type,
        title=title,
        message=message,
        runbook_data={"test": True, "sender": user_token.get("email", user_id)},
        event_type=payload.event_type.value
    )

    delivery_log = await dispatch_webhook_with_retry(
        url=url,
        payload=formatted,
        service_type=service_type.value,
        secret_token=secret_token,
        event_type=payload.event_type.value,
        webhook_id=webhook_id,
        webhook_name=webhook_name,
        max_retries=1,
        timeout=2.5
    )

    # Save delivery log to Firestore / Demo store
    save_webhook_delivery_log(user_id, delivery_log.model_dump())

    return delivery_log


@app.delete("/api/webhooks/{webhook_id}", tags=["Webhooks"])
async def delete_webhook_endpoint(
    webhook_id: str,
    user_token: dict = Depends(verify_firebase_token)
):
    """
    Deletes a registered webhook for the authenticated tenant.
    """
    user_id = user_token.get("uid", "anonymous")
    wh = get_webhook_by_id(user_id, webhook_id)
    if not wh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook '{webhook_id}' not found."
        )
    deleted = delete_user_webhook(user_id, webhook_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook '{webhook_id}' not found."
        )
    return {
        "status": "success",
        "message": f"Webhook '{webhook_id}' successfully deleted."
    }


@app.get("/api/webhooks/deliveries", response_model=List[WebhookDeliveryLog], tags=["Webhooks"])
async def list_webhook_deliveries(
    limit: int = 50,
    user_token: dict = Depends(verify_firebase_token)
):
    """
    Retrieves the append-only audit log of recent webhook deliveries.
    """
    user_id = user_token.get("uid", "anonymous")
    raw_logs = get_user_webhook_logs(user_id, limit=limit)
    return [WebhookDeliveryLog(**log) for log in raw_logs]


# ---------------------------------------------------------
# Runbook REST Endpoints (Standout Feature)
# ---------------------------------------------------------

@app.get("/api/runbooks", response_model=List[RunbookAction], tags=["Runbooks"])
async def get_runbooks(user_token: dict = Depends(verify_firebase_token)):
    """
    List all available automated incident remediation runbooks in the catalog.
    Requires authenticated Firebase ID token or verified demo token.
    """
    return list_available_runbooks()


@app.post("/api/runbooks/execute", response_model=RunbookExecuteResponse, tags=["Runbooks"])
async def execute_runbook_endpoint(
    payload: RunbookExecuteRequest,
    user_token: dict = Depends(verify_firebase_token)
):
    """
    Triggers execution of an automated remediation runbook with audit logging and webhook dispatch.
    """
    user_id = user_token.get("uid", "anonymous")
    user_email = user_token.get("email", "unknown")
    try:
        result = await execute_runbook(
            user_id=user_id,
            user_email=user_email,
            action_id=payload.action_id,
            scenario_id=payload.scenario_id,
            custom_parameters=payload.custom_parameters,
            dispatch_webhooks=payload.dispatch_webhooks
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Runbook execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Runbook execution failed: {str(e)}"
        )


# ---------------------------------------------------------
# Static Frontend Serving (Task 26 preparation)
# ---------------------------------------------------------

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_index():
    """Serves the single-page application dashboard with no-cache headers to ensure immediate live updates."""
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return {
        "message": "WorkplacePulse Backend is live. Frontend static files will be scaffolded in Phase 6.",
        "docs_url": "/docs"
    }


# Tunable FinOps Recovery Validation Boundaries
MAX_FINOPS_RECOVERY_PCT: float = 0.75  # Target high-ROI subset: Reject if claimed recovery exceeds 75% of total portfolio waste

class RecommendationsRequest(BaseModel):
    scenario_id: str

@app.post("/api/forecast/recommendations", tags=["Forecasting"])
async def get_recommendations(
    payload: RecommendationsRequest,
    user_token: dict = Depends(verify_firebase_token),
    x_gemini_api_key: Optional[str] = Header(None)
):
    from data_engine import get_scenario_by_id
    from ai_service import generate_multi_turn_forecast
    import json
    import re
    
    scenario = payload.scenario_id or "saas_finops"
    sc_data = get_scenario_by_id(scenario)
    
    scenario_defaults = {
        "saas_finops": [
            {
                "tag": "FinOps Priority",
                "tagColor": "bg-rose-50 text-rose-700 border-rose-200",
                "title": "Downgrade 65 Inactive Figma Seats",
                "desc": "Revoke 65 dormant Figma Editor seats (>60d inactive) to free Viewer tier via Okta SCIM 2.0.",
                "impact": "+$58,500/yr Saved",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ Reclaim Licenses"
            },
            {
                "tag": "Renewal Prep",
                "tagColor": "bg-amber-50 text-amber-700 border-amber-200",
                "title": "Tier-1 Zoom Host License Optimization",
                "desc": "Transition 160 unutilized Zoom Pro hosts to Zoom Basic prior to Q4 contract renewal lock-in.",
                "impact": "+$34,560/yr Saved",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ Optimize Zoom"
            },
            {
                "tag": "Workspace Audit",
                "tagColor": "bg-indigo-50 text-indigo-700 border-indigo-200",
                "title": "Notion Team Workspace Consolidation",
                "desc": "Decommission 140 unmanaged team workspace seats to consolidate into enterprise root directory.",
                "impact": "+$25,200/yr Saved",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ Consolidate Workspaces"
            }
        ],
        "hardware_lifecycle": [
            {
                "tag": "Safety Critical",
                "tagColor": "bg-rose-50 text-rose-700 border-rose-200",
                "title": "Quarantine 42 Battery-Critical MacBook Units",
                "desc": "Push maintenance quarantine profiles via Jamf Pro MDM for units with battery cycles >800.",
                "impact": "42 Hazards Mitigated",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ Push Jamf Profile"
            },
            {
                "tag": "Warranty Protection",
                "tagColor": "bg-amber-50 text-amber-700 border-amber-200",
                "title": "Proactive AppleCare+ Warranty Sweep",
                "desc": "File bulk warranty refresh requests for 35 MacBook Pro 14 units expiring within 60 days.",
                "impact": "Zero Out-of-Pocket CapEx",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ File Warranty Claims"
            },
            {
                "tag": "CapEx Planning",
                "tagColor": "bg-indigo-50 text-indigo-700 border-indigo-200",
                "title": "Authorize Q4 Dell XPS 15 Fleet Refresh",
                "desc": "Pre-approve $19,200 budget allocation for 19 thermal-throttling Windows 11 endpoints.",
                "impact": "+100% Fleet Uptime",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ Approve CapEx Budget"
            }
        ],
        "itsm_surge": [
            {
                "tag": "SOX Compliance",
                "tagColor": "bg-rose-50 text-rose-700 border-rose-200",
                "title": "Activate 72h SOX Fast-Track Dual Signers",
                "desc": "Deploy automated dual-approval matrix to unblock Month-End financial close access tickets.",
                "impact": "MTTR: 3.8h → 12m",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ Activate Fast-Track"
            },
            {
                "tag": "Self-Service",
                "tagColor": "bg-amber-50 text-amber-700 border-amber-200",
                "title": "Deploy Self-Service MFA Reset Automation",
                "desc": "Route 38 password and token desynchronization tickets through Okta Verify self-healing bot.",
                "impact": "38 Tickets Cleared",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ Deploy Self-Service"
            },
            {
                "tag": "Staff Allocation",
                "tagColor": "bg-indigo-50 text-indigo-700 border-indigo-200",
                "title": "Reallocate Tier-2 Support Engineers",
                "desc": "Shift 4 Identity Access specialists to primary ERP queue during Day -2 to Day +3.",
                "impact": "Zero SLA Breaches",
                "impactColor": "text-emerald-600",
                "actionText": "⚡ Reallocate Staff"
            }
        ]
    }

    # Programmatically derive constraints and ceilings from ScenarioDataPayload
    max_allowed_savings = 0.0
    if scenario == "saas_finops":
        metrics = sc_data.saas_metrics or []
        total_waste = sum(m.annual_potential_savings for m in metrics)
        total_inactive = sum(m.inactive_60d_plus for m in metrics)
        max_allowed_savings = total_waste * MAX_FINOPS_RECOVERY_PCT

        app_lines = []
        for i, m in enumerate(metrics, 1):
            app_lines.append(
                f"  {i}. {m.app_name}: {m.inactive_60d_plus} inactive seats ({m.utilization_rate_pct}% utilization) "
                f"at ${m.cost_per_seat_monthly:,.0f}/mo (${(m.cost_per_seat_monthly * 12):,.0f}/yr) = "
                f"${m.annual_potential_savings:,.2f}/yr potential waste"
            )
        app_catalog = "\n".join(app_lines)

        scenario_constraints = (
            f"CRITICAL FINANCIAL & AUDIT CONSTRAINTS (Strictly Enforced):\n"
            f"- Total portfolio waste across all {len(metrics)} audited applications: ${total_waste:,.2f}/yr ({total_inactive} inactive seats).\n"
            f"- Grounding Telemetry Catalog (only reference these exact applications and figures):\n"
            f"{app_catalog}\n"
            f"- REALISTIC FINOPS TARGETING: Do NOT claim 100% recovery across the entire portfolio. Realistic FinOps remediation targets the highest-ROI, immediately actionable subset (e.g. tier-1 dormant licenses like Figma, Zoom, Notion, or Salesforce).\n"
            f"- The SUM of claimed savings across all 3 actions MUST NOT exceed 75% of total portfolio waste (${max_allowed_savings:,.2f}/yr ceiling).\n"
            f"- In the 'desc' field of each recommendation, explicitly state the exact application(s), inactive seat count(s), and specific action (e.g. Okta SCIM deprovisioning, license tier downgrade, or workspace consolidation).\n"
            f"- In the 'impact' field, provide the exact summed dollar savings for the targeted application(s) in the format '+$XX,XXX/yr Saved'.\n"
        )
    elif scenario == "hardware_lifecycle":
        metrics = sc_data.hardware_metrics or []
        total_endpoints = sum(m.total_units for m in metrics)
        total_critical = sum(m.battery_critical_units for m in metrics)
        total_capex = sum(m.estimated_replacement_budget_usd for m in metrics)

        hw_lines = []
        for i, m in enumerate(metrics, 1):
            hw_lines.append(
                f"  {i}. {m.model_name}: {m.total_units} total units, {m.battery_critical_units} critical battery (>800 cycles), "
                f"{m.out_of_warranty_units} out of warranty, {m.projected_failures_next_quarter} projected Q4 failures (${m.estimated_replacement_budget_usd:,.2f} CapEx)"
            )
        hw_catalog = "\n".join(hw_lines)

        scenario_constraints = (
            f"CRITICAL HARDWARE FLEET CONSTRAINTS:\n"
            f"- Total Monitored Endpoints: {total_endpoints} devices across {len(metrics)} models.\n"
            f"- Total Battery Critical / Swelling Hazard Units: {total_critical} units.\n"
            f"- Total Projected Q4 CapEx Budget: ${total_capex:,.2f}.\n"
            f"- Grounding Telemetry Catalog:\n"
            f"{hw_catalog}\n"
            f"- Recommendations must directly reference specific hardware models, Jamf Pro MDM profile pushes, AppleCare+ warranty sweeps, or CapEx pre-allocations.\n"
            f"- In the 'impact' field, provide specific quantifiable operational impacts (e.g. '42 Hazards Mitigated', 'Zero Out-of-Pocket CapEx', '+100% Fleet Uptime').\n"
        )
    elif scenario == "itsm_surge":
        metrics = sc_data.itsm_metrics or []
        itsm_lines = []
        for i, m in enumerate(metrics, 1):
            itsm_lines.append(
                f"  {i}. {m.category}: Standard {m.historical_daily_avg}/day -> Month-End Surge {m.month_end_surge_daily_avg}/day "
                f"(Backlog: {m.current_open_backlog}, MTTR: {m.average_resolution_time_hrs}h, Bottleneck: '{m.primary_bottleneck}', Risk: {m.escalation_risk_score_1_to_10}/10)"
            )
        itsm_catalog = "\n".join(itsm_lines)

        scenario_constraints = (
            f"CRITICAL ITSM INCIDENT QUEUE CONSTRAINTS:\n"
            f"- Month-End accounting close causes severe surges in access and authorization queues.\n"
            f"- Grounding Queue Catalog:\n"
            f"{itsm_catalog}\n"
            f"- Recommendations must target specific bottlenecks (e.g. manual SOX dual-approval, MFA reset loops, Okta SCIM sync lag).\n"
            f"- In the 'impact' field, provide quantifiable MTTR or ticket reduction metrics (e.g. 'MTTR: 3.8h → 12m', '38 Tickets Cleared', 'Zero SLA Breaches').\n"
        )
    else:
        scenario_constraints = "- Ensure all figures in recommendations strictly match the scenario grounding telemetry.\n"

    def _validate_recommendations(scenario_name: str, recs: list) -> tuple[bool, str]:
        """Validates that AI recommendations strictly adhere to audited telemetry constraints."""
        if not isinstance(recs, list) or len(recs) != 3:
            return False, f"Expected exactly 3 recommendations, received {len(recs) if isinstance(recs, list) else type(recs)}"

        required_fields = ["tag", "tagColor", "title", "desc", "impact", "impactColor", "actionText"]
        for idx, r in enumerate(recs, 1):
            if not isinstance(r, dict):
                return False, f"Recommendation #{idx} is not a valid JSON object"
            for field in required_fields:
                if not r.get(field) or not str(r.get(field)).strip():
                    return False, f"Recommendation #{idx} missing required field '{field}'"

        if scenario_name == "saas_finops":
            total_savings = 0.0
            for r in recs:
                impact_str = str(r.get("impact", ""))
                amounts = re.findall(r'[\$]?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)', impact_str)
                for a in amounts:
                    try:
                        val = float(a.replace(",", ""))
                        total_savings += val
                    except ValueError:
                        pass

            # Ceiling check: Must not exceed 75% realistic subset ceiling
            if total_savings > max_allowed_savings:
                return False, f"Claimed savings ${total_savings:,.2f} exceeds realistic recovery ceiling ${max_allowed_savings:,.2f} ({MAX_FINOPS_RECOVERY_PCT*100:.0f}% of waste)"

            if total_savings <= 0:
                return False, "No valid positive financial savings parsed from impact fields"

            logger.info(f"AI recommendations validated: Total claimed savings = ${total_savings:,.2f} (Ceiling: ${max_allowed_savings:,.2f})")

        return True, "Valid"

    fallback_reason = "Unknown"
    try:
        prompt = (
            f"Generate exactly 3 strategic FinOps/IT remediation actions for scenario '{scenario}' in strict JSON format.\n"
            f"{scenario_constraints}"
            "Output JSON schema: {\"recommendations\": [{\"tag\": \"str\", \"tagColor\": \"bg-indigo-50 text-indigo-700 border-indigo-200\", \"title\": \"str\", \"desc\": \"str\", \"impact\": \"str\", \"impactColor\": \"text-emerald-600\", \"actionText\": \"⚡ Apply\"}]}.\n"
            "Return ONLY the raw JSON object. No Markdown code fences, no conversational text."
        )
        
        resp_text = generate_multi_turn_forecast(
            scenario_id=scenario,
            chat_history=[],
            user_message=prompt,
            client_api_key=x_gemini_api_key
        )
        
        # Parse JSON
        match = re.search(r'\{.*\}', resp_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            recs = parsed.get("recommendations", [])
            is_valid, validation_msg = _validate_recommendations(scenario, recs)
            if is_valid:
                return {
                    "recommendations": recs,
                    "is_live": True,
                    "source": "gemini-3.6-flash"
                }
            else:
                fallback_reason = f"Validation failed ({validation_msg})"
                logger.warning(f"Recommendation validation failed: {validation_msg} — serving static defaults")
        else:
            fallback_reason = "No JSON found in model output"
            logger.warning("Recommendation parsing failed: No JSON found in model output — serving static defaults")
    except Exception as e:
        fallback_reason = f"Inference exception: {type(e).__name__}: {e}"
        logger.warning(f"Dynamic recommendation generation error: {e} — serving static defaults")
        
    return {
        "recommendations": scenario_defaults.get(scenario, scenario_defaults["saas_finops"]),
        "is_live": False,
        "source": "static_fallback",
        "fallback_reason": fallback_reason
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
