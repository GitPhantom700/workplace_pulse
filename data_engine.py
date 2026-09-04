"""
WorkplacePulse - Synthetic Enterprise Data Engine
Generates realistic, privacy-safe IT telemetry for SaaS licenses, hardware fleets, and ITSM ticketing.
Zero real corporate data is required or used.
"""

from typing import Dict, List, Any, Optional
import random
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Pydantic Schemas for Synthetic Telemetry
# ---------------------------------------------------------

class SaaSAppMetric(BaseModel):
    app_name: str
    category: str
    total_licenses: int
    active_last_30d: int
    inactive_60d_plus: int
    cost_per_seat_monthly: float
    annual_potential_savings: float
    okta_sso_configured: bool
    utilization_rate_pct: float


class HardwareFleetMetric(BaseModel):
    model_config = {"protected_namespaces": ()}

    model_name: str
    os_version: str
    total_units: int
    battery_critical_units: int  # Cycle count > 800 or health < 75%
    out_of_warranty_units: int
    projected_failures_next_quarter: int
    estimated_replacement_budget_usd: float
    jamf_compliance_rate_pct: float


class ITSMIncidentMetric(BaseModel):
    category: str
    historical_daily_avg: int
    month_end_surge_daily_avg: int
    current_open_backlog: int
    average_resolution_time_hrs: float
    primary_bottleneck: str
    escalation_risk_score_1_to_10: int


class ScenarioDataPayload(BaseModel):
    scenario_id: str
    title: str
    domain: str
    timestamp: str
    summary: str
    chart_data: Dict[str, Any]
    saas_metrics: List[SaaSAppMetric] = Field(default_factory=list)
    hardware_metrics: List[HardwareFleetMetric] = Field(default_factory=list)
    itsm_metrics: List[ITSMIncidentMetric] = Field(default_factory=list)
    grounding_context: str


# ---------------------------------------------------------
# Synthetic Scenario Generators
# ---------------------------------------------------------

def generate_saas_finops_scenario() -> ScenarioDataPayload:
    """
    Scenario 1: SaaS License Stale Audit & Renewal Optimization.
    Simulates Okta SSO telemetry & SaaS usage across core enterprise tools.
    """
    apps = [
        {"name": "Figma Enterprise", "cat": "Design", "total": 150, "active": 85, "cost": 75.0, "sso": True},
        {"name": "Zoom Pro", "cat": "Collaboration", "total": 450, "active": 290, "cost": 18.0, "sso": True},
        {"name": "GitHub Enterprise", "cat": "DevOps", "total": 220, "active": 205, "cost": 21.0, "sso": True},
        {"name": "Notion Team", "cat": "Productivity", "total": 300, "active": 160, "cost": 15.0, "sso": True},
        {"name": "Salesforce Sales Cloud", "cat": "CRM", "total": 120, "active": 105, "cost": 165.0, "sso": True},
        {"name": "Miro Business", "cat": "Collaboration", "total": 180, "active": 95, "cost": 16.0, "sso": False},
        {"name": "Datadog Infrastructure", "cat": "Observability", "total": 90, "active": 88, "cost": 110.0, "sso": True},
    ]

    metrics: List[SaaSAppMetric] = []
    total_annual_waste = 0.0

    for item in apps:
        inactive = item["total"] - item["active"]
        util_pct = round((item["active"] / item["total"]) * 100, 1)
        annual_waste = round(inactive * item["cost"] * 12, 2)
        total_annual_waste += annual_waste

        metrics.append(SaaSAppMetric(
            app_name=item["name"],
            category=item["cat"],
            total_licenses=item["total"],
            active_last_30d=item["active"],
            inactive_60d_plus=inactive,
            cost_per_seat_monthly=item["cost"],
            annual_potential_savings=annual_waste,
            okta_sso_configured=item["sso"],
            utilization_rate_pct=util_pct
        ))

    # Chart payload for Chart.js
    labels = [m.app_name for m in metrics]
    active_counts = [m.active_last_30d for m in metrics]
    inactive_counts = [m.inactive_60d_plus for m in metrics]

    chart_data = {
        "type": "bar",
        "labels": labels,
        "datasets": [
            {"label": "Active Users (Last 30d)", "data": active_counts, "backgroundColor": "#a78bfa", "borderRadius": 8},
            {"label": "Stale/Inactive (60d+)", "data": inactive_counts, "backgroundColor": "#f1f5f9", "hoverBackgroundColor": "#e2e8f0", "borderRadius": 8}
        ]
    }

    # NOTE: Telemetry list format ('  * {name} ({cat}): ...') is parsed by _generate_smart_simulation_response in ai_service.py.
    # Keep this layout synchronized across both files if modified.
    app_lines = []
    for m in metrics:
        sso_str = "Configured" if m.okta_sso_configured else "Not Configured"
        app_lines.append(
            f"  * {m.app_name} ({m.category}): {m.total_licenses} total licenses, "
            f"{m.active_last_30d} active (last 30d), {m.inactive_60d_plus} inactive (>60d idle), "
            f"${m.cost_per_seat_monthly:.2f}/seat/mo (${m.cost_per_seat_monthly * 12:.2f}/seat/yr), "
            f"${m.annual_potential_savings:,.2f}/yr potential waste, "
            f"Utilization: {m.utilization_rate_pct}%, Okta SSO: {sso_str}"
        )
    app_breakdown = "\n".join(app_lines)
    total_inactive = sum(m.inactive_60d_plus for m in metrics)

    grounding_text = (
        f"SYNTHETIC SAAS AUDIT TELEMETRY (OKTA SSO & SCIM):\n"
        f"- Total Applications Monitored: {len(metrics)}\n"
        f"- Total Inactive / Idle Seats Across Fleet: {total_inactive} seats\n"
        f"- Projected Annual License Waste Across Fleet: ${total_annual_waste:,.2f}\n"
        f"- Highest Waste App: Figma Enterprise (65 inactive licenses = $58,500.00/yr)\n"
        f"- Detailed Application Inventory & Metrics:\n{app_breakdown}\n"
        f"- Targeted Remediation Runbook: 'Okta SCIM License Deprovisioner' (act_saas_reclaim_01) targets 365 idle seats across Figma (65), Zoom (160), and Notion (140) to reclaim $118,260.00/yr.\n"
        f"- Action Needed: Reclaim inactive licenses prior to upcoming Q4 annual contract renewals."
    )

    return ScenarioDataPayload(
        scenario_id="saas_finops",
        title="SaaS License Stale Audit & Contract Renewal Optimizer",
        domain="Digital Workplace / FinOps",
        timestamp=datetime.now(timezone.utc).isoformat(),
        summary=f"Discovered ${total_annual_waste:,.2f} in reclaimable annualized SaaS spend across {len(metrics)} primary applications.",
        chart_data=chart_data,
        saas_metrics=metrics,
        grounding_context=grounding_text
    )


def generate_hardware_lifecycle_scenario() -> ScenarioDataPayload:
    """
    Scenario 2: Jamf Hardware Fleet Degradation & CapEx Refresh Forecasting.
    Simulates Jamf Pro MDM endpoint health, battery cycle counts, and warranty expiration.
    """
    fleet = [
        {"model": "MacBook Pro 13\" (M1, 2020)", "os": "macOS 13.6 (Ventura)", "total": 140, "battery_bad": 42, "oow": 140, "est_fail": 28, "cost": 1800.0, "compliance": 92.5},
        {"model": "MacBook Pro 14\" (M1 Pro, 2021)", "os": "macOS 14.4 (Sonoma)", "total": 210, "battery_bad": 22, "oow": 85, "est_fail": 15, "cost": 2100.0, "compliance": 98.1},
        {"model": "MacBook Pro 16\" (M2 Pro, 2023)", "os": "macOS 14.5 (Sonoma)", "total": 95, "battery_bad": 3, "oow": 0, "est_fail": 2, "cost": 2600.0, "compliance": 99.0},
        {"model": "Dell XPS 15 (Windows 11)", "os": "Win 11 23H2", "total": 80, "battery_bad": 19, "oow": 50, "est_fail": 12, "cost": 1600.0, "compliance": 88.0},
    ]

    metrics: List[HardwareFleetMetric] = []
    total_capex_required = 0.0

    for item in fleet:
        capex = item["est_fail"] * item["cost"]
        total_capex_required += capex

        metrics.append(HardwareFleetMetric(
            model_name=item["model"],
            os_version=item["os"],
            total_units=item["total"],
            battery_critical_units=item["battery_bad"],
            out_of_warranty_units=item["oow"],
            projected_failures_next_quarter=item["est_fail"],
            estimated_replacement_budget_usd=capex,
            jamf_compliance_rate_pct=item["compliance"]
        ))

    labels = [m.model_name for m in metrics]
    healthy_counts = [m.total_units - m.battery_critical_units for m in metrics]
    critical_counts = [m.battery_critical_units for m in metrics]

    chart_data = {
        "type": "bar",
        "labels": labels,
        "datasets": [
            {"label": "Healthy Battery (<800 cycles)", "data": healthy_counts, "backgroundColor": "#93c5fd", "borderRadius": 8},
            {"label": "Critical / Swelling Risk (>800 cycles)", "data": critical_counts, "backgroundColor": "#e2e8f0", "hoverBackgroundColor": "#cbd5e1", "borderRadius": 8}
        ]
    }

    fleet_lines = []
    for m in metrics:
        fleet_lines.append(
            f"  * {m.model_name} (OS: {m.os_version}): {m.total_units} units total, "
            f"{m.battery_critical_units} battery critical (>800 cycles or <75% health), "
            f"{m.out_of_warranty_units} out of warranty, {m.projected_failures_next_quarter} projected Q4 failures, "
            f"${m.estimated_replacement_budget_usd:,.2f} replacement budget, Jamf Compliance: {m.jamf_compliance_rate_pct}%"
        )
    fleet_breakdown = "\n".join(fleet_lines)

    grounding_text = (
        f"SYNTHETIC HARDWARE FLEET & JAMF MDM TELEMETRY:\n"
        f"- Total Monitored Endpoints: {sum(m.total_units for m in metrics)} devices\n"
        f"- Battery Critical Units (>800 cycles or capacity <75%): {sum(m.battery_critical_units for m in metrics)} units\n"
        f"- Projected Q4 Hardware Replacements Due to Battery Degradation/Aging: {sum(m.projected_failures_next_quarter for m in metrics)} units\n"
        f"- Estimated CapEx Refresh Budget Required: ${total_capex_required:,.2f}\n"
        f"- Detailed Hardware Fleet Inventory by Model:\n{fleet_breakdown}\n"
        f"- Targeted Remediation Runbook: 'Jamf Pro Battery Quarantine & Depot Refresh' (act_hardware_quarantine_02) flags 42 MacBook Pro 13\" (M1) swelling units for depot refresh.\n"
        f"- Compliance Risk: Dell XPS fleet lagging in Jamf/Intune compliance at 88%."
    )

    return ScenarioDataPayload(
        scenario_id="hardware_lifecycle",
        title="Jamf Hardware Fleet Degradation & CapEx Refresh Forecast",
        domain="IT Asset Management / Endpoint Engineering",
        timestamp=datetime.now(timezone.utc).isoformat(),
        summary=f"Identified {sum(m.battery_critical_units for m in metrics)} endpoints at immediate risk of failure, requiring ${total_capex_required:,.2f} CapEx refresh budget.",
        chart_data=chart_data,
        hardware_metrics=metrics,
        grounding_context=grounding_text
    )


def generate_itsm_surge_scenario() -> ScenarioDataPayload:
    """
    Scenario 3: Month-End Close ITSM Support Surge & Access Bottlenecks.
    Simulates Jira Service Management / ServiceNow incident queues, MTTR, and accounting close surges.
    """
    categories = [
        {"cat": "Financial Close & ERP Access", "daily_normal": 6, "surge": 42, "backlog": 18, "mttr": 3.8, "bottleneck": "Manual SOX dual-approval workflow", "risk": 9},
        {"cat": "SSO & Multi-Factor Auth (MFA)", "daily_normal": 14, "surge": 38, "backlog": 12, "mttr": 1.2, "bottleneck": "Self-service reset bypass failures", "risk": 7},
        {"cat": "Hardware / Peripheral Swaps", "daily_normal": 8, "surge": 11, "backlog": 4, "mttr": 4.5, "bottleneck": "Local stock depot shortage", "risk": 4},
        {"cat": "Software Provisioning & Add-ons", "daily_normal": 18, "surge": 35, "backlog": 15, "mttr": 2.6, "bottleneck": "Okta SCIM synchronization lag", "risk": 6},
        {"cat": "eDiscovery & Legal Access Holds", "daily_normal": 2, "surge": 5, "backlog": 1, "mttr": 8.0, "bottleneck": "Compliance sign-off latency", "risk": 5},
    ]

    metrics: List[ITSMIncidentMetric] = []
    for item in categories:
        metrics.append(ITSMIncidentMetric(
            category=item["cat"],
            historical_daily_avg=item["daily_normal"],
            month_end_surge_daily_avg=item["surge"],
            current_open_backlog=item["backlog"],
            average_resolution_time_hrs=item["mttr"],
            primary_bottleneck=item["bottleneck"],
            escalation_risk_score_1_to_10=item["risk"]
        ))

    labels = [m.category for m in metrics]
    normal_vol = [m.historical_daily_avg for m in metrics]
    surge_vol = [m.month_end_surge_daily_avg for m in metrics]

    chart_data = {
        "type": "line",
        "labels": labels,
        "datasets": [
            {"label": "Standard Daily Ticket Volume", "data": normal_vol, "borderColor": "#cbd5e1", "backgroundColor": "#cbd5e1", "borderWidth": 3, "tension": 0.4, "pointRadius": 0, "fill": False},
            {"label": "Month-End Surge Daily Volume (Projected)", "data": surge_vol, "borderColor": "#a78bfa", "backgroundColor": "#a78bfa", "borderWidth": 3, "tension": 0.4, "pointBackgroundColor": "#ffffff", "pointBorderWidth": 2, "pointRadius": 5, "fill": False}
        ]
    }

    itsm_lines = []
    for m in metrics:
        itsm_lines.append(
            f"  * {m.category}: {m.historical_daily_avg}/day baseline, "
            f"{m.month_end_surge_daily_avg}/day month-end surge, {m.current_open_backlog} open backlog, "
            f"{m.average_resolution_time_hrs} hrs MTTR, Escalation Risk: {m.escalation_risk_score_1_to_10}/10, "
            f"Primary Bottleneck: {m.primary_bottleneck}"
        )
    itsm_breakdown = "\n".join(itsm_lines)

    grounding_text = (
        f"SYNTHETIC ITSM INCIDENT & SERVICE DESK TELEMETRY:\n"
        f"- Target Period: Upcoming Month-End Financial Close (Days -3 to +3)\n"
        f"- Total Standard Baseline Volume: {sum(m.historical_daily_avg for m in metrics)} tickets/day\n"
        f"- Total Projected Month-End Surge Volume: ~{sum(m.month_end_surge_daily_avg for m in metrics)} tickets/day (vs {sum(m.historical_daily_avg for m in metrics)}/day normal)\n"
        f"- High-Risk Incident Category: 'Financial Close & ERP Access' spikes 700% from 6 to 42 tickets/day with a 3.8-hour MTTR.\n"
        f"- Detailed Incident Category Breakdown:\n{itsm_breakdown}\n"
        f"- Critical Bottleneck: SOX dual-approvals stall accounting workflows during reconciliation cutoff.\n"
        f"- Targeted Remediation Runbook: 'Emergency SOX Fast-Track Dual-Signer Approval Matrix' (act_itsm_sox_fasttrack_03) activates 72h pre-approved workflow reducing Close MTTR from 3.8 hours to 12 minutes.\n"
        f"- Action Needed: Deploy pre-authorized emergency approval runbooks and allocate 2 dedicated Tier-2 shifts for Finance systems."
    )

    return ScenarioDataPayload(
        scenario_id="itsm_surge",
        title="Month-End Close ITSM Support Surge & Access Bottleneck Forecast",
        domain="IT Service Management / Operations",
        timestamp=datetime.now(timezone.utc).isoformat(),
        summary="Predicting a 700% surge in the ERP / Financial Close queue specifically (6 → 42 tickets/day, +173% fleet-wide) during month-end cutoff, risking SLA breaches and close delays.",
        chart_data=chart_data,
        itsm_metrics=metrics,
        grounding_context=grounding_text
    )


# ---------------------------------------------------------
# Registry & Seeder Service
# ---------------------------------------------------------

SCENARIO_REGISTRY = {
    "saas_finops": generate_saas_finops_scenario,
    "hardware_lifecycle": generate_hardware_lifecycle_scenario,
    "itsm_surge": generate_itsm_surge_scenario
}


def get_scenario_by_id(scenario_id: str) -> Optional[ScenarioDataPayload]:
    """Retrieve or generate synthetic scenario telemetry by ID. Returns None if scenario not found."""
    generator = SCENARIO_REGISTRY.get(scenario_id)
    if not generator:
        return None
    return generator()


def build_support_grounding_context() -> str:
    """
    Programmatically builds comprehensive, cross-module telemetry grounding for the Alex Support AI
    by deriving accurate metrics directly from all active scenarios in data_engine.py.
    """
    saas = get_scenario_by_id("saas_finops")
    hw = get_scenario_by_id("hardware_lifecycle")
    itsm = get_scenario_by_id("itsm_surge")

    saas_total_waste = sum(m.annual_potential_savings for m in saas.saas_metrics) if saas and saas.saas_metrics else 170700.0
    saas_total_inactive = sum(m.inactive_60d_plus for m in saas.saas_metrics) if saas and saas.saas_metrics else 482
    saas_lines = []
    if saas and saas.saas_metrics:
        for m in saas.saas_metrics:
            saas_lines.append(f"  * {m.app_name}: {m.total_licenses} total licenses, {m.active_last_30d} active, {m.inactive_60d_plus} inactive seats (>60d idle), ${m.cost_per_seat_monthly:.0f}/seat/mo, ${m.annual_potential_savings:,.2f}/yr waste")
    saas_breakdown = "\n".join(saas_lines)

    hw_total_units = sum(m.total_units for m in hw.hardware_metrics) if hw and hw.hardware_metrics else 525
    hw_total_battery = sum(m.battery_critical_units for m in hw.hardware_metrics) if hw and hw.hardware_metrics else 86
    hw_total_fail = sum(m.projected_failures_next_quarter for m in hw.hardware_metrics) if hw and hw.hardware_metrics else 57
    hw_total_capex = sum(m.estimated_replacement_budget_usd for m in hw.hardware_metrics) if hw and hw.hardware_metrics else 106300.0
    hw_lines = []
    if hw and hw.hardware_metrics:
        for m in hw.hardware_metrics:
            hw_lines.append(f"  * {m.model_name}: {m.total_units} units total, {m.battery_critical_units} battery critical (>800 cycles or <75% health), {m.out_of_warranty_units} out-of-warranty, {m.projected_failures_next_quarter} projected Q4 failures, ${m.estimated_replacement_budget_usd:,.2f} refresh budget")
    hw_breakdown = "\n".join(hw_lines)

    itsm_normal = sum(m.historical_daily_avg for m in itsm.itsm_metrics) if itsm and itsm.itsm_metrics else 48
    itsm_surge_vol = sum(m.month_end_surge_daily_avg for m in itsm.itsm_metrics) if itsm and itsm.itsm_metrics else 131
    erp_metric = next((m for m in itsm.itsm_metrics if "ERP" in m.category), None) if itsm and itsm.itsm_metrics else None
    erp_mttr = erp_metric.average_resolution_time_hrs if erp_metric else 3.8
    erp_surge = erp_metric.month_end_surge_daily_avg if erp_metric else 42
    erp_normal = erp_metric.historical_daily_avg if erp_metric else 6
    itsm_lines = []
    if itsm and itsm.itsm_metrics:
        for m in itsm.itsm_metrics:
            itsm_lines.append(f"  * {m.category}: {m.historical_daily_avg}/day baseline, {m.month_end_surge_daily_avg}/day month-end surge, {m.average_resolution_time_hrs} hrs MTTR, Escalation Risk {m.escalation_risk_score_1_to_10}/10, Bottleneck: {m.primary_bottleneck}")
    itsm_breakdown = "\n".join(itsm_lines)

    return (
        "=== WORKPLACEPULSE PLATFORM KNOWLEDGE BASE & GROUND TRUTH TELEMETRY ===\n\n"
        "1. ARCHITECTURE & PLATFORM INTEGRATIONS:\n"
        "- WorkplacePulse Sentinel is an IT Operations & FinOps Command Center running on Google Cloud Run.\n"
        "- Ingests operational telemetry from Okta Universal Directory, Figma Enterprise, Zoom Pro, Jamf Pro MDM, and Jira Service Management.\n"
        "- Storage: Cloud Firestore Native with Application Default Credentials (ADC) in append-only audit mode.\n"
        "- Security: Google Cloud Secret Manager for credentials, zero hardcoded API keys.\n"
        "- Authentication: Firebase Auth (Google Sign-In or Continue as Guest for anonymous evaluation).\n\n"
        "2. SAAS FINOPS TELEMETRY (OKTA SSO & SCIM):\n"
        f"- Total Annual SaaS License Waste Across Fleet: ${saas_total_waste:,.2f}/yr\n"
        f"- Total Inactive Seats (>60 days idle): {saas_total_inactive} seats across 7 applications\n"
        f"- Highest Waste Application: Figma Enterprise (65 inactive licenses, ${58500:,.2f}/yr waste, $75/seat/mo)\n"
        f"- Detailed SaaS Application Inventory:\n{saas_breakdown}\n"
        "- Runbook: 'Okta SCIM License Deprovisioner' (act_saas_reclaim_01) auto-reclaims idle seats via SCIM 2.0 API.\n\n"
        "3. HARDWARE FLEET & MDM TELEMETRY (JAMF PRO):\n"
        f"- Total Monitored Endpoints in Fleet: {hw_total_units} devices\n"
        f"- Battery Critical Units (>800 cycles or capacity <75%): {hw_total_battery} devices ({((hw_total_battery / hw_total_units) * 100):.1f}% of fleet)\n"
        f"- Projected Q4 Hardware Replacements: {hw_total_fail} units\n"
        f"- Required CapEx Refresh Budget: ${hw_total_capex:,.2f}\n"
        f"- Detailed Fleet Inventory by Model:\n{hw_breakdown}\n"
        "- Most Critical Hazard Fleet: MacBook Pro 13\" (M1, 2020) with 42 battery critical units (100% out of warranty).\n"
        "- Runbook: 'Jamf Pro Battery Quarantine & Depot Refresh' (act_hardware_quarantine_02) applies quarantine MDM profiles.\n\n"
        "4. ITSM SERVICE DESK & MONTH-END SURGE (JIRA SERVICE MANAGEMENT):\n"
        f"- Fleet-Wide Baseline Daily Ticket Volume: {itsm_normal} tickets/day\n"
        f"- Projected Month-End Close Surge Volume: {itsm_surge_vol} tickets/day (+{round(((itsm_surge_vol - itsm_normal) / itsm_normal) * 100)}% fleet-wide increase)\n"
        f"- Financial Close & ERP Access Queue: Spikes 700% specifically from {erp_normal} to {erp_surge} tickets/day with {erp_mttr} hours MTTR.\n"
        f"- Detailed Incident Category Inventory:\n{itsm_breakdown}\n"
        "- Runbook: 'Emergency SOX Fast-Track Dual-Signer Approval Matrix' (act_itsm_sox_fasttrack_03) reduces ERP MTTR from 3.8 hours to 12 minutes.\n\n"
        "5. MULTI-PLATFORM WEBHOOK ALERTING:\n"
        "- Supports Slack (Block Kit), Microsoft Teams (MessageCard), Discord (Embed), and Generic JSON webhooks with HMAC-SHA256 signatures."
    )


def list_available_scenarios() -> List[Dict[str, str]]:
    """List summary catalog of available scenario presets."""
    return [
        {
            "id": "saas_finops",
            "title": "SaaS License Stale Audit",
            "description": "Forecast unassigned & idle SaaS seats (Figma, Zoom, Notion) to optimize annual contracts."
        },
        {
            "id": "hardware_lifecycle",
            "title": "Jamf Hardware Fleet Degradation",
            "description": "Predict battery failures & warranty lapses across laptop fleets to budget CapEx refreshes."
        },
        {
            "id": "itsm_surge",
            "title": "Month-End Close ITSM Surge",
            "description": "Forecast ticket spikes in accounting & ERP access to prevent month-end close bottlenecks."
        }
    ]


if __name__ == "__main__":
    # Self-test verification
    for s_id in SCENARIO_REGISTRY:
        payload = get_scenario_by_id(s_id)
        print(f"Generated {payload.scenario_id}: {payload.title} (Summary: {payload.summary[:60]}...)")
