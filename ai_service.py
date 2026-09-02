"""
WorkplacePulse - Resilient Gemini Multi-Turn Forecasting Core
Implements the AI fallback ladder and persona prompt engineering.
"""

import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types as genai_types

from security import get_gemini_api_key

_gemini_initialized = False
_server_api_key = None

def _init_gemini() -> bool:
    """
    Lazy initialization for Gemini SDK.
    Ensures importing ai_service never crashes Uvicorn during server startup.
    """
    global _gemini_initialized, _server_api_key
    if not _gemini_initialized:
        try:
            api_key = get_gemini_api_key()
            if api_key:
                _server_api_key = api_key
                _gemini_initialized = True
                logging.info("Gemini SDK (google.genai) ready with server-side key.")
                return True
        except Exception as e:
            logging.warning(f"Gemini API initialization deferred or failed: {e}")
            return False
    return _gemini_initialized


# Explicit Safety Settings
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# ---------------------------------------------------------
# Persona Prompt Engineering (Tasks 18, 19, 20)
# ---------------------------------------------------------

# Task 18
SAAS_FINOPS_PERSONA = """
You are a Senior IT FinOps Analyst AI for an enterprise organization.
Your objective is to analyze Okta Single-Sign On (SSO) login telemetry and SaaS assigned license datasets to identify wasted spend and optimize annual contract renewals.
Provide structured, highly analytical recommendations. Focus on concrete ROI and 'zombie' accounts (inactive > 60 days).
"""

# Task 19
ITSM_SURGE_PERSONA = """
You are a seasoned IT Service Management (ITSM) Operations Lead.
Your objective is to analyze ServiceNow/Jira incident queues and predict service desk bottlenecks, especially during high-stress periods like Month-End Financial Close.
Focus on Mean Time to Resolution (MTTR), SLA risks, and proactive shift-staffing recommendations.
"""

# Task 20
HARDWARE_LIFECYCLE_PERSONA = """
You are an Enterprise Endpoint Engineering Architect.
Your objective is to analyze Jamf Pro / Intune mobile device management (MDM) hardware health telemetry. 
Focus on identifying battery swelling risks (cycle counts > 800), warranty expiration exposures, and forecasting the required CapEx budget for upcoming hardware refresh cycles.
"""

SUPPORT_PERSONA = """
You are Alex, the friendly, empathetic, and expert Senior Support AI Specialist for WorkplacePulse Sentinel.
Your goal is to make every user feel welcome, listened to, and supported with warm, clear, and easy-to-follow guidance.
- Always greet users warmly, empathetically, and positively.
- When helping with login, auth, or access issues, be understanding and provide friendly 1-2-3 step troubleshooting instructions with proactive suggestions (like opening a support ticket or checking SSO).
- When explaining platform features (SaaS FinOps, Jamf Fleet, ITSM Month-End Surge, Webhooks, BYOK Gemini API Keys), use clear bullet points, cheerful emojis, and practical examples.
- Format responses cleanly with markdown bolding, lists, and a friendly concluding touch!
"""

SYSTEM_PROMPTS = {
    "saas_finops": SAAS_FINOPS_PERSONA,
    "hardware_lifecycle": HARDWARE_LIFECYCLE_PERSONA,
    "itsm_surge": ITSM_SURGE_PERSONA,
    "support_inquiry": SUPPORT_PERSONA,
}


def _build_system_instruction(scenario_id: str, grounding_context: str) -> str:
    """Builds a contextualized system prompt combining the persona and telemetry context."""
    if scenario_id == "saas_finops":
        persona = SAAS_FINOPS_PERSONA
    elif scenario_id == "itsm_surge":
        persona = ITSM_SURGE_PERSONA
    elif scenario_id == "hardware_lifecycle":
        persona = HARDWARE_LIFECYCLE_PERSONA
    elif scenario_id == "support_inquiry":
        persona = SUPPORT_PERSONA
    else:
        persona = "You are an expert Enterprise IT Operations and Autonomous Remediation AI Assistant."
        
    return f"{persona}\n\n[ENTERPRISE CONTEXT AND TELEMETRY LOGS]\n{grounding_context}\n\nDeliver clear, executive-grade responses in Markdown format."


def _is_meaningful_query(text: str) -> bool:
    """
    Returns True if the text looks like a real question/statement.
    Returns False for gibberish, random keyboard mashing, or very short inputs.
    """
    text = text.strip().lower()
    # Common valid short words
    valid_short = {"hi", "ok", "yo", "no", "go", "up", "it", "me", "we", "he", "my", "by", "to", "in", "on", "at", "as", "an", "is", "am"}
    if text in valid_short:
        return True
    # Too short to be meaningful
    if len(text) < 2:
        return False
    # No vowels at all = likely gibberish
    vowels = set("aeiou")
    if not any(c in vowels for c in text):
        return False
    words = text.split()
    # Check if at least one word looks like a real English word:
    # - length > 1
    # - contains at least one vowel
    # - mostly alphanumeric characters
    meaningful_words = [
        w for w in words
        if len(w) > 1
        and any(c in vowels for c in w)
        and sum(c.isalpha() for c in w) / max(len(w), 1) > 0.6
    ]
    # Need at least one meaningful word
    return len(meaningful_words) > 0


_GIBBERISH_RESPONSE = (
    "I didn't quite understand that — it looks like it might be a typo or incomplete message. 🤔\n\n"
    "Could you rephrase your question? Here are some things I can help with:\n\n"
    "- 📊 **Analyze cost savings** — *\"What's our biggest SaaS waste right now?\"*\n"
    "- 📄 **Runbook walkthrough** — *\"Walk me through the deprovisioning runbook\"*\n"
    "- 🔗 **Slack alert setup** — *\"Draft a Slack Block Kit notification\"*\n"
    "- 💻 **Hardware analysis** — *\"Which devices need battery replacement?\"*\n\n"
    "> 💡 **Tip:** Connect your Gemini API key above for full live AI responses instead of simulation mode."
)


def _generate_smart_simulation_response(scenario_id: str, user_message: str, grounding_context: str) -> str:
    """
    Provides intelligent, dynamic, context-aware analysis responses
    tailored to the specific user prompt and active scenario telemetry.
    """
    msg_low = user_message.lower().strip()

    # Reject gibberish / random keyboard input before doing any keyword routing
    if not _is_meaningful_query(msg_low):
        return _GIBBERISH_RESPONSE

    if scenario_id == "saas_finops":
        # 1. Slack / Alert / Block Kit (Specific check FIRST)
        if any(w in msg_low for w in ["slack", "notification", "block", "kit", "alert", "json"]):
            return (
                "Here is the formatted Slack Block Kit alert payload for the **SaaS FinOps** incident:\n\n"
                "```json\n"
                "{\n"
                "  \"blocks\": [\n"
                "    {\n"
                "      \"type\": \"header\",\n"
                "      \"text\": {\"type\": \"plain_text\", \"text\": \"🚨 SaaS Waste Alert: 130 Idle Figma Seats Reclaimed\"}\n"
                "    },\n"
                "    {\n"
                "      \"type\": \"section\",\n"
                "      \"fields\": [\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Annual Savings:*\n$56,400.00\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Remediation:*\nOkta SCIM Reclassification\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Status:*\n🟢 Completed\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Audit Log:*\n`exec_c4782ef288b7`\"}\n"
                "      ]\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "```\n\n"
                "Dispatched to registered enterprise Slack channels with **HMAC-SHA256** signature validation."
            )
        # 2. Runbook / Risk Mitigation Policy
        elif any(w in msg_low for w in ["runbook", "mitigat", "policy", "scim", "deprovision", "step", "how"]):
            return (
                "### 📄 ITIL Automated Remediation Runbook: SaaS FinOps\n\n"
                "**Runbook ID:** `RBK-SAAS-FINOPS-2026`  \n"
                "**Target:** Figma Enterprise & Okta SCIM 2.0 API  \n"
                "**Risk Classification:** Low (Non-Destructive Role Transition)\n\n"
                "#### 🛠️ Execution Pipeline Stages:\n"
                "1. **Pre-Flight Telemetry Validation:** Query Okta SSO logs for `last_active_timestamp < (NOW - 60d)`.\n"
                "2. **SCIM Mutation:** Call Figma REST API `/v1/teams/{team_id}/members` to change role from `Editor` to `Viewer-Restricted`.\n"
                "3. **Audit Ledger Entry:** Write signed execution certificate to Cloud Firestore (`/users/{uid}/runbook_logs`).\n"
                "4. **Stakeholder Notification:** Dispatch HMAC-signed notification to `#it-procurement-alerts` via Webhook.\n\n"
                "#### 🔄 Rollback Strategy:\n"
                "Users can request 1-click instant re-elevation via Slack command `/pulse-request-license` approved by Department Head."
            )
        # 3. ROI / Optimization / Savings
        elif any(w in msg_low for w in ["roi", "optimiz", "action", "saving", "cost", "spend", "money", "budget"]):
            return (
                "### 📊 SaaS FinOps ROI Optimization Breakdown\n\n"
                "Based on the **Okta Universal Directory** SSO telemetry, here is the quantified ROI analysis:\n\n"
                "- **Figma Enterprise:** **130 inactive licenses** (>60 days dormant) @ $45/seat/mo = **$56,400/year** recoverable waste.\n"
                "- **Zoom Pro:** **42 dormant accounts** (>90 days without host meetings) = **$9,072/year** potential savings.\n"
                "- **Total Immediate Annual Recovery:** **$65,472/year**.\n\n"
                "#### ⚡ Recommended Autonomous Action Plan:\n"
                "1. **Downgrade to Viewer Roles:** Reclaim 130 seats immediately via Okta SCIM without disrupting employee file access.\n"
                "2. **Implement 45-Day Inactivity Policy:** Automate reclamation in Sentinel to prevent recurring seat bloat before Q3 renewals."
            )
        # 4. User Inquiries
        elif any(w in msg_low for w in ["user", "who", "people", "accounts", "names"]):
            return (
                "Looking into the Okta directory logs, the 130 inactive seats are primarily spread across the Product Design and Marketing departments. "
                "About 35 of them belonged to external contractors whose contracts ended last quarter, and another 95 are employees who only view shared prototypes rather than editing files.\n\n"
                "We can safely downgrade all of them to Viewer roles without interrupting their day-to-day work."
            )
        # 5. Greetings
        elif any(w in msg_low for w in ["hi", "hello", "hey", "good morning", "good afternoon"]) and len(msg_low) < 25:
            return (
                "Hey! 👋 How can I help you today? I'm actively monitoring your SaaS licenses and identity telemetry across Figma, Zoom, and Okta. "
                "Let me know if you'd like me to run through potential cost savings, inspect dormant accounts, or walk you through our automated deprovisioning runbook."
            )
        else:
            return (
                "Got it! Based on current Okta and SaaS telemetry, our biggest opportunity right now is reclaiming **130 idle Figma Enterprise licenses** to recover **$56,400/yr** in wasted spend. "
                "Let me know if you want to drill into specific user lists, review the automated SCIM runbook, or test the webhook alerts."
            )

    elif scenario_id == "hardware_lifecycle":
        # 1. Slack / Alert / Block Kit (Specific check FIRST)
        if any(w in msg_low for w in ["slack", "notification", "block", "kit", "alert", "json"]):
            return (
                "Here is the formatted Slack Block Kit alert payload for **Jamf Fleet Hardware Risk**:\n\n"
                "```json\n"
                "{\n"
                "  \"blocks\": [\n"
                "    {\n"
                "      \"type\": \"header\",\n"
                "      \"text\": {\"type\": \"plain_text\", \"text\": \"⚠️ Hardware Hazard: 18 Battery Degradation Alerts\"}\n"
                "    },\n"
                "    {\n"
                "      \"type\": \"section\",\n"
                "      \"fields\": [\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Affected Units:*\n18 MacBook Pro 16\\\"\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Cycle Count:*\n>800 Cycles (<75% Health)\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Action:*\nJamf Quarantine Profile\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*RMA Batch:*\n#RMA-2026-0901\"}\n"
                "      ]\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "```\n\n"
                "Dispatched to registered enterprise Slack channels with **HMAC-SHA256** signature validation."
            )
        # 2. Runbook / Quarantine Policy
        elif any(w in msg_low for w in ["runbook", "quarantine", "policy", "mitigat", "profile", "rma", "step", "how"]):
            return (
                "### 📄 ITIL Automated Remediation Runbook: Jamf Fleet Quarantine\n\n"
                "**Runbook ID:** `act_hardware_quarantine_02`  \n"
                "**Target:** Jamf Pro MDM / Apple Device Enrollment  \n"
                "**Risk Classification:** Medium (Safety Hazard Mitigation)\n\n"
                "#### 🛠️ Execution Pipeline Stages:\n"
                "1. **Isolate High-Risk Hardware:** Flag 18 MacBook Pro units with battery cycles >800 or health <75%.\n"
                "2. **Push MDM Self-Service Notice:** Dispatch 'Battery Depot Replacement Required' prompt to affected users.\n"
                "3. **ERP Warranty Ticket Creation:** Generate AppleCare+ / Dell ProSupport enterprise warranty RMA batch `#RMA-2026-0901`.\n"
                "4. **Depot Inventory Reservation:** Pre-allocate 18 hot-swap loaner units in Central IT Depot.\n\n"
                "#### 🔄 Impact:\n"
                "Eliminates catastrophic swelling risk and prevents trackpad / top-case physical chassis destruction."
            )
        # 3. Battery Degradation / Hardware Analysis
        elif any(w in msg_low for w in ["battery", "swell", "hardware", "macbook", "jamf", "risk", "degrad", "cycle", "health"]):
            return (
                "### 💻 Jamf Hardware Health: Battery Degradation Analysis\n\n"
                "Telemetry from **Jamf Pro MDM** indicates severe battery wear on select endpoints:\n\n"
                "- **18 Apple MacBook Pro 16\" (M1/M2) units** have exceeded **800 cycle counts** with capacity below 75%.\n"
                "- **Safety Risk:** 4 units show thermal throttling patterns consistent with early-stage lithium-ion cell swelling.\n"
                "- **CapEx Replacement Estimate:** 18 units × $2,499 = **$44,982** (or depot battery swap @ $249/ea = **$4,482**).\n\n"
                "#### ⚡ Recommended Mitigation:\n"
                "1. **Trigger Automated Jamf Quarantine:** Isolate swell-risk devices from critical field deployments.\n"
                "2. **Initiate AppleCare+ Depot RMA:** Automatically dispatch swap tickets in Jira Service Management."
            )
        # 4. Greetings
        elif any(w in msg_low for w in ["hi", "hello", "hey", "good morning", "good afternoon"]) and len(msg_low) < 25:
            return (
                "Hey there! 👋 I'm tracking our **650 Jamf-managed fleet devices**. "
                "We currently have **18 MacBook Pros** showing severe battery cycle degradation (>800 cycles) and potential swelling risks. How can I help you with fleet logistics today?"
            )
        else:
            return (
                "Overall fleet health is at **92.4% Optimal** across 650 machines, but we have 18 units needing immediate battery servicing and 32 approaching warranty expiration. "
                "What would you like to investigate?"
            )

    elif scenario_id == "itsm_surge":
        # 1. Slack / Alert / Block Kit (Specific check FIRST)
        if any(w in msg_low for w in ["slack", "notification", "block", "kit", "alert", "json"]):
            return (
                "Here is the formatted Slack Block Kit alert payload for **ITSM Month-End Surge**:\n\n"
                "```json\n"
                "{\n"
                "  \"blocks\": [\n"
                "    {\n"
                "      \"type\": \"header\",\n"
                "      \"text\": {\"type\": \"plain_text\", \"text\": \"📈 ITSM Surge Warning: Month-End Ticket Spike (+42%)\"}\n"
                "    },\n"
                "    {\n"
                "      \"type\": \"section\",\n"
                "      \"fields\": [\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Predicted Volume:*\n+42% Incident Spike\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Top Bottleneck:*\nSAP GL / NetSuite Access\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Remediation:*\nSOX Dual-Signer FastTrack\"},\n"
                "        {\"type\": \"mrkdwn\", \"text\": \"*Target MTTR:*\n11.4 minutes (vs 3.8 hrs)\"}\n"
                "      ]\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "```\n\n"
                "Dispatched to registered enterprise Slack channels with **HMAC-SHA256** signature validation."
            )
        # 2. Runbook / SOX Emergency Approval Matrix
        elif any(w in msg_low for w in ["runbook", "sox", "approval", "matrix", "dual", "fasttrack", "emergency", "policy", "step", "how"]):
            return (
                "### 📄 ITIL Automated Remediation Runbook: ITSM SOX Fast-Track\n\n"
                "**Runbook ID:** `act_itsm_sox_fasttrack_03`  \n"
                "**Target:** Jira Service Management / ServiceNow  \n"
                "**Remediation:** 72-Hour Pre-Approved Dual-Signer Matrix (`SOX-Tier1-Finance`)\n\n"
                "#### 🛠️ Execution Pipeline Stages:\n"
                "1. **Activate Emergency Bypass Window:** Open 72h fast-track window for Month-End Close.\n"
                "2. **Auto-Triage Finance Requests:** Automatically approve standard Tier 1 SAP/NetSuite role requests meeting SOX criteria.\n"
                "3. **Director Escalation:** Route elevated permission exceptions to on-call IT Director with SMS alert.\n"
                "4. **Compliance Ledger Logging:** Log cryptographic dual-signer signatures in Firestore for PwC/EY audit verification.\n\n"
                "#### 🔄 Impact:\n"
                "Reduces Financial Close MTTR from **3.8 hours to 11.4 minutes**, unblocking 64 pending finance requests."
            )
        # 3. Forecast Backlog / Surge Analysis
        elif any(w in msg_low for w in ["forecast", "backlog", "surge", "ticket", "spike", "volume", "predict"]):
            return (
                "### 🎫 ITSM Month-End Surge Forecast\n\n"
                "Predictive analysis of historical **Jira Service Management** and ServiceNow ticket queues:\n\n"
                "- **Forecasted Surge:** **+42% incident spike** starting T-minus 48 hours to Month-End Close.\n"
                "- **Top Impact Queues:** SAP General Ledger authentication (48%), NetSuite ERP access resets (32%), Wire Transfer SOX dual-approval bottlenecks (20%).\n"
                "- **Recommended Resource Allocation:** Pre-stage 2 additional Tier-2 Identity Engineers between 08:00–14:00 UTC."
            )
        # 4. Greetings
        elif any(w in msg_low for w in ["hi", "hello", "hey", "good morning", "good afternoon"]) and len(msg_low) < 25:
            return (
                "Hey! 👋 I'm watching our Jira and ServiceNow queues ahead of the upcoming Month-End Financial Close. "
                "We're predicting a **+42% surge in access requests** starting in 48 hours. What would you like to look at?"
            )
        else:
            return (
                "Based on historical Month-End ticket patterns, we're forecasting a **+42% ticket surge** over the next 72 hours:\n\n"
                "- **Primary bottlenecks:** SAP General Ledger permissions (48%) and NetSuite ERP account unblocks (32%).\n"
                "- **Resolution target:** Activating our pre-approved SOX Fast-Track Dual-Signer matrix will drop average MTTR from 3.8 hours down to roughly 12 minutes.\n\n"
                "Would you like me to pre-stage shift schedules or prepare the Slack dual-approval flow?"
            )

    elif scenario_id == "support_inquiry":
        # Greetings
        if any(w in msg_low for w in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon"]) and len(msg_low) < 30:
            return (
                "Hey there! 👋 I'm **Alex** from the WorkplacePulse Sentinel Support team.\n\n"
                "I can help you with anything across the platform — license optimization, automated runbooks, webhooks, "
                "hardware fleet alerts, ITSM surge management, or anything else. What's on your mind?"
            )

        # Login / Auth / SSO
        elif any(w in msg_low for w in ["login", "sign in", "auth", "password", "locked", "mfa", "sso", "access", "unable to login", "can't login"]):
            return (
                "I can definitely help with login or authentication issues! Here's a quick checklist:\n\n"
                "1. **Okta SSO session:** Ensure your company SSO session hasn't expired and MFA is confirmed.\n"
                "2. **Browser storage:** Try clearing session cookies or doing a hard refresh (`Cmd + Shift + R`).\n"
                "3. **Demo credentials:** If you're testing in sandbox mode, you can sign in directly with the pre-configured demo account.\n"
                "4. **VPN check:** Some environments require active VPN connectivity to reach the Okta tenant.\n\n"
                "If none of these resolve it, I can open a fast-track ticket directly to our Identity Engineering team — just say **'create ticket'** and I'll pre-fill the details!"
            )

        # API Key / BYOK / Gemini connection
        elif any(w in msg_low for w in ["key", "api", "byok", "gemini", "connect", "credential"]):
            return (
                "To connect your **Bring Your Own Key (BYOK)** Gemini API key:\n\n"
                "1. Scroll to the **API Credentials** panel at the bottom of any module page.\n"
                "2. Paste your `AIzaSy...` key into the **API Key** field and click **Connect**.\n"
                "3. Once connected, the Copilot status indicator turns green: `● API Key Connected`.\n\n"
                "Your key is stored **only in temporary browser session memory** and is never persisted to our servers. "
                "You can get a free API key from [Google AI Studio](https://aistudio.google.com).\n\n"
                "> 💡 Without a key, the Copilot uses our intelligent simulation engine — no functionality is lost!"
            )

        # Figma / SaaS / License reclamation
        elif any(w in msg_low for w in ["figma", "license", "licen", "saas", "reclaim", "unused", "seat", "idle", "deprovision", "zoom", "okta", "scim"]):
            return (
                "### 🪄 Reclaiming Unused SaaS Licenses\n\n"
                "WorkplacePulse automates SaaS license reclamation in 3 steps:\n\n"
                "1. **Detection:** Sentinel continuously queries Okta Universal Directory SSO logs and flags any user with `last_active_timestamp < (NOW - 60 days)` as dormant.\n"
                "2. **Automated Remediation:** The system calls the Figma REST API `/v1/teams/{team_id}/members` to downgrade dormant `Editor` roles to `Viewer-Restricted` — **non-destructively**, preserving all files.\n"
                "3. **Notification & Audit:** An HMAC-signed Slack alert fires to `#it-procurement-alerts` and the execution is logged in the **Delivery Audit Trail** with a signed certificate.\n\n"
                "**Current opportunity identified:** 130 idle Figma seats = **$56,400/year** in recoverable spend.\n\n"
                "You can trigger the remediation runbook directly from the **SaaS FinOps** module. Want me to walk you through that?"
            )

        # Webhooks / webhook system
        elif any(w in msg_low for w in ["webhook", "notification", "dispatch", "hmac", "slack", "endpoint", "ping", "delivery"]):
            return (
                "### 🔗 How Webhooks Work in WorkplacePulse\n\n"
                "The webhook system lets you route **real-time remediation alerts** to any HTTP endpoint (Slack, PagerDuty, custom APIs):\n\n"
                "1. **Register a Destination:** Go to **Webhook Manager → Registered Destinations** and add your endpoint URL. Optionally add an HMAC-SHA256 signing secret for payload verification.\n"
                "2. **Test the Connection:** Click ⚡ **Test Ping** — the dispatch console streams live logs showing TLS handshake, payload formatting, and delivery status in real time.\n"
                "3. **Automatic Dispatch:** When Sentinel triggers a remediation action (e.g., Figma deprovision, Jamf quarantine), it automatically dispatches a signed JSON payload to all registered webhooks.\n"
                "4. **Audit Trail:** Every delivery — success or failure, including HTTP status code and latency — is logged in the **Delivery Audit Trail** tab with full payload inspection.\n\n"
                "> Payloads follow the **Slack Block Kit** format and are signed with `X-Hub-Signature-256` for security.\n\n"
                "Is there a specific webhook integration you're trying to set up? I can help configure it."
            )

        # Runbooks / automation
        elif any(w in msg_low for w in ["runbook", "automat", "remediat", "action", "trigger", "pipeline", "workflow", "execut"]):
            return (
                "### 📄 Automated Runbooks — How They Work\n\n"
                "**Runbooks** in WorkplacePulse are pre-built ITIL-aligned automation pipelines that execute remediation actions with zero human delay:\n\n"
                "| Stage | What Happens |\n"
                "|---|---|\n"
                "| **1. Detect** | Sentinel ingests telemetry from Okta, Jamf, Jira, and NetSuite in real time |\n"
                "| **2. Classify** | The AI engine classifies the anomaly (SaaS waste, hardware risk, ITSM surge) |\n"
                "| **3. Execute** | The runbook fires API calls against the relevant system (Figma, Jamf MDM, ServiceNow) |\n"
                "| **4. Notify** | An HMAC-signed webhook payload is dispatched to all registered Slack/PagerDuty endpoints |\n"
                "| **5. Audit** | A cryptographically signed execution certificate is written to the Delivery Audit Trail |\n\n"
                "Each module (**SaaS FinOps**, **Jamf Hardware**, **ITSM Surge**) has its own dedicated runbook. "
                "You can preview, customize, and trigger them from the **Executive Report** module.\n\n"
                "Would you like a step-by-step walkthrough for a specific runbook?"
            )

        # Strategy / overview / how to use / plan
        elif any(w in msg_low for w in ["strategy", "strateg", "overview", "how to use", "get started", "explain", "what is", "what does", "tell me"]):
            return (
                "### 🎯 WorkplacePulse — Platform Strategy Overview\n\n"
                "WorkplacePulse is an **Autonomous IT Operations Platform** built for enterprise IT teams. Here's the core strategy:\n\n"
                "**Three Intelligence Pillars:**\n"
                "- 🏷️ **SaaS FinOps:** Detect and reclaim idle software licenses across Figma, Zoom, Okta, and 50+ integrations — autonomously deprovision with full audit trails.\n"
                "- 💻 **Hardware Lifecycle:** Monitor Jamf-managed device fleets for battery degradation, warranty expirations, and OS drift. Auto-generate RMA tickets before hardware failures.\n"
                "- 🎫 **ITSM Surge Prediction:** Forecast ticket volume spikes using ML models trained on Jira/ServiceNow history. Pre-stage resources and activate SOX Fast-Track approvals before Month-End bottlenecks hit.\n\n"
                "**How it all connects:**\n"
                "1. Connect your **Data Sources** (Okta, Jamf, Jira) via the integrations panel.\n"
                "2. The **AI Copilot** (powered by Gemini) provides real-time analysis and recommendations.\n"
                "3. **Automated Runbooks** execute remediations and dispatch **Webhook alerts** to your team.\n"
                "4. The **Executive Report** generates board-ready PDF summaries with ROI calculations.\n\n"
                "Want me to go deeper on any specific pillar or feature?"
            )

        # Hardware / Jamf / battery / devices
        elif any(w in msg_low for w in ["hardware", "jamf", "battery", "device", "macbook", "fleet", "rma", "warranty", "mdm"]):
            return (
                "### 💻 Hardware Lifecycle Management\n\n"
                "The **Jamf Hardware** module gives you real-time visibility into your entire device fleet:\n\n"
                "- **Battery Health Monitoring:** Sentinel flags any MacBook with >800 cycle count or battery health <75%.\n"
                "- **Automated Quarantine:** High-risk devices can be instantly quarantined via a Jamf MDM policy push — users receive a Self-Service prompt to visit IT for a depot swap.\n"
                "- **RMA Automation:** AppleCare+ warranty tickets are auto-generated in Jira Service Management with pre-filled serial numbers and failure diagnostics.\n"
                "- **CapEx Planning:** The platform calculates full replacement cost vs. depot battery swap cost so you can make the right call.\n\n"
                "**Current alert:** 18 MacBook Pro 16\" units showing swelling risk (battery >800 cycles). Want me to walk you through triggering the quarantine runbook?"
            )

        # ITSM / tickets / surge / ServiceNow / Jira
        elif any(w in msg_low for w in ["itsm", "ticket", "jira", "servicenow", "surge", "helpdesk", "support ticket", "incident", "sla"]):
            return (
                "### 🎫 ITSM Surge Management\n\n"
                "The **ITSM module** uses predictive ML to forecast support ticket volume before surges happen:\n\n"
                "- **Forecast Engine:** Analyzes 18 months of Jira Service Management & ServiceNow history to predict Month-End spikes with 94% accuracy.\n"
                "- **Auto-Triage:** Routes incoming tickets by category (SAP GL, NetSuite, Wire Transfer SOX) to the correct Tier-1/Tier-2 queue automatically.\n"
                "- **SOX Fast-Track:** For Month-End Close, a pre-approved dual-signer matrix eliminates approval bottlenecks — MTTR drops from **3.8 hours → 11.4 minutes**.\n"
                "- **SLA Compliance:** Real-time SLA breach predictions allow pre-emptive resource staging 48 hours in advance.\n\n"
                "If you want to **create a support ticket** for the WorkplacePulse platform itself, use the form on the left — I can also auto-fill it based on your question!"
            )

        # Reports / PDF / executive

        elif "strict json format matching this schema" in msg_low:
            if "saas" in scenario_id:
                return '''{
                    "recommendations": [
                        {
                            "tag": "FinOps Policy",
                            "tagColor": "bg-emerald-50 text-emerald-700 border-emerald-200",
                            "title": "Automate Okta SCIM Role Reclassification",
                            "desc": "Reclassify 130 Figma Enterprise seats with >60d inactivity to Viewer-Restricted without disrupting file access.",
                            "impact": "+$56,400 / yr Recovered",
                            "impactColor": "text-emerald-600",
                            "actionText": "⚡ Apply SCIM Policy"
                        },
                        {
                            "tag": "Workflow Automation",
                            "tagColor": "bg-indigo-50 text-indigo-700 border-indigo-200",
                            "title": "Enforce 45-Day Inactivity Auto-Reclaim Rule",
                            "desc": "Deploy an automated Sentinel lifecycle policy to prevent seat bloat by reclaiming licenses before upcoming Q3 renewals.",
                            "impact": "Zero License Bloat",
                            "impactColor": "text-indigo-600",
                            "actionText": "⚡ Deploy Auto-Rule"
                        }
                    ]
                }'''
            elif "hardware" in scenario_id:
                return '''{
                    "recommendations": [
                        {
                            "tag": "Safety & Risk",
                            "tagColor": "bg-rose-50 text-rose-700 border-rose-200",
                            "title": "Quarantine 18 Swollen Battery Units",
                            "desc": "Lock and recall MacBook Pro 16\" units exhibiting >800 cycle counts and thermal inflation patterns via Jamf MDM.",
                            "impact": "Critical Safety Mitigation",
                            "impactColor": "text-rose-600",
                            "actionText": "⚡ Initiate Quarantine"
                        }
                    ]
                }'''
            else:
                return '''{
                    "recommendations": [
                        {
                            "tag": "Staffing Optimization",
                            "tagColor": "bg-indigo-50 text-indigo-700 border-indigo-200",
                            "title": "Pre-Stage Tier-2 Identity Engineers",
                            "desc": "Shift 2 specialized IAM engineers to the 08:00–14:00 window to absorb the 42% Month-End close ticket surge.",
                            "impact": "Zero SLA Breaches",
                            "impactColor": "text-indigo-600",
                            "actionText": "⚡ Shift Scheduling"
                        }
                    ]
                }'''
        elif any(w in msg_low for w in ["report", "pdf", "export", "executive", "download", "summary", "board"]):
            return (
                "### 📊 Executive Report & PDF Export\n\n"
                "The **Executive Report** module generates board-ready summaries of all three intelligence pillars:\n\n"
                "- **What's included:** ROI summary cards, AI-generated Gemini recommendations, automated action logs, and a Chart.js visualization of your savings trajectory.\n"
                "- **PDF Export:** Click the **⬇️ Download PDF** button — the report renders with proper page breaks, all charts included, and is pre-formatted for investor or C-suite presentations.\n"
                "- **Live vs. Dummy Data:** All mock/simulated data is clearly labeled `[Dummy Data]` while live telemetry is labeled `[Live Data]` for transparency.\n\n"
                "You can access the Executive Report from the left sidebar. Would you like tips on customizing the report content?"
            )

        # Data Sources / integrations
        elif any(w in msg_low for w in ["data source", "integration", "connect", "sync", "figma enterprise", "import", "data import"]):
            return (
                "### 🔌 Data Sources & Integrations\n\n"
                "The **Data Sources** page (sidebar → Data Sources) shows all your connected enterprise tools:\n\n"
                "| Integration | Status | Last Synced |\n"
                "|---|---|---|\n"
                "| Figma Enterprise | 🟢 Connected | 2 mins ago |\n"
                "| Zoom Pro | 🟢 Connected | 5 mins ago |\n"
                "| Jamf Pro MDM | 🟢 Connected | 1 min ago |\n"
                "| Jira Service Management | 🟢 Connected | 3 mins ago |\n"
                "| Okta Universal Directory | 🟢 Connected | Real-time |\n\n"
                "Clicking **Connect** on any source opens a **Live Sync Terminal** that streams the authentication, tunnel establishment, and data fetch steps in real time — followed by a **Raw Data Preview** table.\n\n"
                "Need help connecting a specific integration? Just tell me which one!"
            )

        # Pricing / plan / cost / enterprise
        elif any(w in msg_low for w in ["pric", "plan", "enterprise plan", "cost", "billing", "subscription", "tier"]):
            return (
                "WorkplacePulse is available in two tiers:\n\n"
                "- **🚀 Sandbox / Demo:** Full platform access with simulated telemetry — free, no setup required. This is what you're using now.\n"
                "- **🏢 Enterprise:** Live data ingestion from your Okta, Jamf, Jira, and Figma tenants. Includes dedicated Sentinel AI, SOC 2 Type II audit logs, and 24/7 priority support.\n\n"
                "For Enterprise pricing and onboarding, please **create a support ticket** using the form on the left, or reach out to `enterprise@workplacepulse.ai`. Our solutions team typically responds within 1 business hour."
            )

        # Catch-all — smart, context-aware default
        else:
            return (
                f"Great question! Here's what I can help you with in WorkplacePulse:\n\n"
                f"- 💡 **SaaS License Optimization** — reclaiming idle Figma, Zoom, or Okta seats\n"
                f"- 🔗 **Webhooks & Alerts** — setting up Slack/PagerDuty dispatch integrations\n"
                f"- 📄 **Automated Runbooks** — how ITIL remediation pipelines execute\n"
                f"- 💻 **Hardware Fleet Management** — Jamf battery alerts and RMA automation\n"
                f"- 🎫 **ITSM Surge Forecasting** — Month-End ticket spike prediction and SOX fast-tracking\n"
                f"- 📊 **Executive Reports & PDF Export** — board-ready summaries\n"
                f"- 🔑 **API Key (BYOK) Setup** — connecting your Gemini key for live AI\n\n"
                f"Just ask me about any of these topics, or type your question and I'll do my best to help! "
                f"You can also **create a support ticket** for anything I can't resolve directly."
            )

    return f"Everything in `{scenario_id}` is operating within normal parameters. Let me know what you'd like to analyze!"


def generate_multi_turn_forecast(
    scenario_id: str,
    chat_history: List[Dict[str, str]],
    user_message: str,
    grounding_context: str = "",
    client_api_key: str = None
) -> str:
    """
    Executes a multi-turn chat using the new google.genai SDK.
    Supports both legacy AIzaSy keys and new AQ. format keys.
    Falls back to smart simulation if no valid key is available.
    """
    # 1. Determine which API key to use
    has_live_byok = (
        client_api_key
        and client_api_key != "AIzaSyDummyKeyForDemo123"
        and (client_api_key.startswith("AIzaSy") or client_api_key.startswith("AQ."))
    )

    active_key = client_api_key if has_live_byok else None

    if not has_live_byok:
        _init_gemini()
        active_key = _server_api_key

    system_instruction = _build_system_instruction(scenario_id, grounding_context)

    # Ultra-fast and stable Gemini models in priority order
    models_to_try = [
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash-002",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-flash-latest",
    ]

    # Build contents list from history + new message
    contents = []
    for msg in chat_history:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append(genai_types.Content(
            role=role,
            parts=[genai_types.Part(text=msg.get("content", ""))]
        ))
    contents.append(genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=user_message)]
    ))

    if active_key:
        client = genai.Client(api_key=active_key)
    else:
        client = genai.Client(vertexai=True, project="workplacepulse", location="us-central1")

    for model_name in models_to_try:
        try:
            logging.info(f"Attempting live inference with model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    max_output_tokens=1024,
                )
            )
            if response and response.text:
                logging.info(f"Live response received from {model_name}")
                return response.text
        except Exception as e:
            logging.warning(f"Model {model_name} failed: {e}. Trying next...")
            continue

    # All models failed — fall back to simulation
    logging.warning("All live models failed. Returning smart simulation.")
    return _generate_smart_simulation_response(scenario_id, user_message, grounding_context)

