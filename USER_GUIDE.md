# WorkplacePulse User Guide

Welcome to the **WorkplacePulse** command center. This platform provides continuous, multi-tenant intelligence, bringing your IT service management (ITSM), endpoint fleet health, and SaaS licensing telemetry into a unified, actionable dashboard powered by Google Gemini AI.

This guide walks you through the primary workflows, analytics views, and autonomous capabilities of the platform.

<br>

### 📑 Table of Contents
* [🔐 **1. Authentication & Setup** — *Sandbox Exploration & Live Google Auth*](#1-authentication--setup)
* [📊 **2. Navigating the Executive Dashboard** — *KPIs, Scenarios & Predictive Velocity Sparklines*](#2-navigating-the-executive-dashboard)
* [🤖 **3. Gemini Copilot & Bring-Your-Own-Key (BYOK)** — *Live AI Grounding & Prompt Pills*](#3-gemini-copilot--bring-your-own-key-byok)
* [🛡️ **4. Autonomous Incident Runbooks & Executive Compliance Reports** — *1-Click Execution & ITIL Post-Mortem*](#4-autonomous-incident-runbooks--remediation)
* [🔌 **5. Managing Data Sources** — *Integrations, Live Sync Terminal & Raw Preview*](#5-managing-data-sources)
* [🔔 **6. Webhooks & Alerting** — *HMAC-SHA256 Signed Multi-Platform Delivery*](#6-webhooks--alerting)
* [🎧 **7. Live Support & Troubleshooting** — *Knowledge Base, Form Tickets & AI Assistant*](#7-live-support--troubleshooting)

<br>

---

<br>

## 1. Authentication & Setup

> **💡 Purpose & Significance:**  
> Enterprise IT platforms require strict tenant segregation. WorkplacePulse enforces zero-trust data partitioning under `/users/{userId}/...` via Firebase Admin SDK and Cloud Firestore security rules. The Demo Mode toggle provides evaluators with a 60-second instant sandbox to explore all features with zero cloud configuration or credit cards required.

<br>

When you first navigate to the platform, you will be presented with the **Pre-Login Landing Page**. By default, the system operates in a simulated sandbox.

<br>

![Executive Dashboard (Pre-Login)](./assets/screenshots/executive-dashboard-pre.png)
*Figure 1a: The pre-login landing page. The highlighted controls in the top right manage authentication and Demo Mode.*

<br>

### Getting Started Steps:

1. **Explore Sandbox:** Note the **Demo Mode: ON** toggle in the top right corner. This allows you to explore the dashboard using simulated dummy data without connecting live telemetry.
2. **Switch to Live Mode:** To connect to your live enterprise data, toggle Demo Mode to **OFF**. 
3. Click the **Sign in with Google** button in the top right corner. This will trigger the secure authentication popup.

<br>

![Google Login](./assets/screenshots/login-popup.png)
*Figure 1b: Google Sign-In popup for tenant authentication.*

<br>

Upon successful authentication, your unique Tenant ID is assigned, and you will be routed to the live **WorkplacePulse Executive Dashboard**.

<br>

![Executive Dashboard (Post-Login)](./assets/screenshots/executive-dashboard-post.png)
*Figure 1c: The post-login state showing your active User Profile, Demo Mode OFF, and live telemetry data.*

<br>
<br>

---

<br>

## 2. Navigating the Executive Dashboard

The main dashboard presents an aggregated, real-time command center for enterprise IT operations, hardware fleets, and software licensing.

<br>

### Key Performance Indicators (KPIs)

> **💡 Purpose & Significance:**  
> IT executives and FinOps leads cannot parse through thousands of raw log lines during incidents. These KPI summary cards deliver an immediate 5-second pulse check on total financial waste, operational workload surges, and hardware safety hazards—enabling rapid decision-making before drilling down into granular data.

<br>

At the top of the dashboard, real-time KPI metric cards provide an immediate snapshot of top operational exposures:

<br>

#### 1. Idle SaaS Capital
Tracks wasted annual spend on unassigned or dormant software licenses across your enterprise SaaS catalog.

<br>

![Idle SaaS Capital](./assets/screenshots/kpi-idle-saas-capital.png)

<br>
<br>

#### 2. Support Ticket Surge
Monitors active service desk queues and flags volume anomalies exceeding normal operational baselines.

<br>

![Support Ticket Surge](./assets/screenshots/kpi-itsm-ticket-surge.png)

<br>
<br>

#### 3. Hardware Degradation
Evaluates physical endpoint fleet health, highlighting battery degradation and warranty expiration risks.

<br>

![Hardware Degradation](./assets/screenshots/kpi-hardware-degradation.png)

<br>
<br>

---

<br>

### Interactive Telemetry Scenarios

> **💡 Purpose & Significance:**  
> Enterprise IT is traditionally fragmented across isolated silos (FinOps in finance, Jamf in endpoint engineering, Jira in the service desk). Interactive Telemetry Scenarios unify these disparate domains into a single pane of glass, giving IT leaders complete cross-functional visibility.

<br>

You can filter data visualizations and re-pivot the entire dashboard using the left-hand **Scenario Navigation** bar:

<br>

#### Scenario A: SaaS FinOps (Okta / Figma / Zoom)
Visualizes license utilization versus spend to identify dormant accounts (>60 days inactive) and optimize upcoming contract renewals.

<br>

![SaaS FinOps Telemetry](./assets/screenshots/saas-finops-distribution.png)

<br>
<br>

#### Scenario B: Hardware Lifecycle (Jamf Fleet)
Maps device battery degradation (>800 cycle counts), thermal swelling risks, and AppleCare/Dell warranty expiration timelines across your endpoint fleet.

<br>

![Hardware Lifecycle (Jamf)](./assets/screenshots/hardware-lifecycle-jamf.png)

<br>
<br>

#### Scenario C: ITSM Surge (Jira Service Management)
Details support ticket spikes, Mean Time to Resolution (MTTR), and service desk bottlenecks during critical periods like Month-End Financial Close.

<br>

![ITSM Surge (Jira)](./assets/screenshots/itsm-surge-distribution.png)

<br>
<br>

---

<br>

### Predictive Forecasting & Trend Velocity (Q4 Forecast Trend)

> **💡 Purpose & Significance:**  
> Traditional IT dashboards only report historical failures after they happen. WorkplacePulse shifts IT operations from *reactive firefighting* to *predictive mitigation*, saving thousands of dollars in unneeded renewals, CapEx waste, and costly operational downtime.

<br>

The **Detailed Telemetry Matrix** in each module includes a forward-looking **Q4 Forecast Trend** column powered by leading velocity indicators:

*   **SaaS FinOps Velocity:** Evaluates dormancy accumulation velocity (e.g., `↗ +35% Waste` on Figma Enterprise) to calculate contract exposure before annual renewal lock-in.

<br>

![Detailed Telemetry Matrix (Q4 Forecast Trend)](./assets/screenshots/saas-matrix-forecast.png)

<br>
<br>

*   **Hardware Lifecycle Velocity:** Projects quarterly failure rates across laptop batches to calculate exact CapEx refresh budgets before hardware fails in the field.

<br>

![Hardware Degradation Forecast Matrix](./assets/screenshots/hardware-matrix-forecast.png)

<br>
<br>

*   **ITSM Surge Multiplier:** Quantifies projected ticket surge multipliers (e.g., `⚡ 7.0x Surge` in ERP access) to schedule engineer shifts and prevent SLA breaches.

<br>

![ITSM Surge Forecast Matrix](./assets/screenshots/itsm-matrix-forecast.png)

<br>
<br>

*   **Micro-Sparklines:** Inline SVG Bézier curves visually indicate trajectory at a glance (🔴 High Risk Spike, 🟠 Moderate Growth, ⚪ Stable, 🟢 Optimized).

<br>

| SaaS FinOps Sparklines | Hardware Lifecycle Sparklines | ITSM Surge Sparklines |
| :---: | :---: | :---: |
| ![SaaS Sparklines](./assets/screenshots/sparklines-saas.png) | ![Hardware Sparklines](./assets/screenshots/sparklines-hardware.png) | ![ITSM Sparklines](./assets/screenshots/sparklines-itsm.png) |

<br>
<br>

---

<br>

## 3. Gemini Copilot & Bring-Your-Own-Key (BYOK)

> **💡 Purpose & Significance:**  
> Generative AI without grounding produces generic hallucinations. WorkplacePulse serializes live telemetry into structured Pydantic payloads that feed Gemini's context window. Gemini acts as an autonomous staff-level FinOps consultant—instantly identifying exact dollar savings, drafting ITIL runbooks, and formatting Slack Block Kit alert payloads. The BYOK architecture guarantees client privacy by storing keys strictly in ephemeral browser session memory.

<br>

WorkplacePulse integrates directly with Google's Gemini AI to offer strategic recommendations grounded in your active telemetry.

<br>

### Connecting Your API Key (Live Data Mode)

By default, the platform runs with a resilient multi-client ladder. To test with your personal Google AI Studio credentials:

1. Locate the **Gemini Copilot** panel on the right side of the dashboard.

<br>

<img src="./assets/screenshots/gemini-copilot-panel-retina.png" width="280" alt="Gemini Copilot Panel" />

<br>
<br>

2. Expand the **Gemini API Key (BYOK)** drawer.

<br>

![Gemini API Key BYOK Drawer](./assets/screenshots/byok-drawer-expanded.png)

<br>
<br>

3. Enter your **Gemini API Key** and click **Connect**.

<br>

![Gemini API Key Connected](./assets/screenshots/byok-key-connected.png)

<br>
<br>

4. The system validates your key in session memory and switches the telemetry badges to <span style="color:green">Live Data</span>.

<br>

![Live Data Badge Active](./assets/screenshots/copilot-live-data-badge.png)

<br>
<br>

5. **Ask Grounded Operational Questions:** Type an inquiry into the chat box (e.g., *"Can you forecast Zoom pro demand for the next three months?"*) or select a suggested prompt pill. Gemini analyzes the active telemetry context in real time.

<br>

| 1. Submitting Inquiry (Thinking State) | 2. Completed FinOps Telemetry Assessment |
| :---: | :---: |
| ![Gemini Copilot Query - Thinking](./assets/screenshots/copilot-query-thinking.png) | ![Gemini Copilot Query - Completed Assessment](./assets/screenshots/copilot-query-response.png) |

<br>
<br>

---

<br>

## 4. Autonomous Incident Runbooks & Remediation

> **💡 Purpose & Significance:**  
> AI insights are ineffective if remediation requires manual ticket ping-pong. WorkplacePulse bridges predictive analytics directly into automated ITIL workflows. With 1-click execution, IT leads can trigger automated role transitions in Okta, maintenance quarantines in Jamf, or SOX emergency bypasses in Jira—reducing Mean Time to Resolution (MTTR) from hours to seconds while logging immutable audit trails to Cloud Firestore.

<br>

### End-to-End Autonomous Execution Workflow:

#### Step 1: Review & Trigger Autonomous Remediation
Locate the context-aware **Sentinel Autonomous Remediation** card at the bottom of the active scenario dashboard. Review the target infrastructure and estimated ROI, then click **`🚀 Execute Runbook & Dispatch Alert`**.

<br>

![Step 1: Trigger Autonomous Runbook](./assets/screenshots/runbook-workflow-step1-trigger.png)

<br>
<br>

#### Step 2: Live Execution Log Stream & Webhook Dispatch
The system initializes the enterprise API connector, executes the SCIM/MDM/ITSM transaction, emits immutable audit records to Cloud Firestore, and dispatches HMAC-signed alerts to your configured channels (Slack, Discord, Teams).

<br>

![Step 2: Execution Log Stream](./assets/screenshots/runbook-workflow-step2-stream.png)

<br>
<br>

#### Step 3: Executive Incident Remediation & SOC 2 Compliance Report
Click **`📄 View Executive Report`** in the log stream header to review the complete **Executive Incident Remediation & Compliance Audit**. This delivers a print-ready, SOC 2 Type II compliant attestation containing root cause diagnosis, telemetry graphs, chronological execution traces, and trust service criteria evidence.

<br>

<img src="./assets/screenshots/runbook-workflow-step3-report-retina.png" width="480" alt="Executive Incident Remediation & Compliance Audit" />

<br>
<br>

*Section 5 of Compliance Report: Live Gemini AI Strategic Recommendations & Interactive Policies:*

<br>

![Gemini AI Strategic Recommendations & Next Actions](./assets/screenshots/executive-report-gemini-recommendations.png)

<br>
<br>

### 📋 Pre-Built Runbook Catalog Across All 3 Modules:

Each scenario module is equipped with a specialized, automated runbook designed to resolve the specific operational bottleneck discovered by the telemetry engine:

<br>

| Module / Domain | Runbook Name & Target API | Anomaly Trigger Condition | Automated Remediation Action | Quantified Enterprise Impact |
| :--- | :--- | :--- | :--- | :--- |
| **💰 SaaS FinOps** | **Okta SCIM License Deprovisioner**<br>*(Okta SCIM 2.0 / SSO)* | Discovers users with no SSO logins for **60+ consecutive days** | Revokes provisioned Editor entitlements via SCIM 2.0 while preserving document view access | **Recovers up to $56,400/yr** in recurring SaaS waste across Figma, Zoom & Notion |
| **💻 Jamf Fleet** | **Jamf Pro Battery Quarantine & Refresh**<br>*(Jamf Pro MDM / ERP)* | Flags laptops with **battery cycle count >800** or health **<75%** | Pushes maintenance profiles via MDM and automatically submits warranty RMA tickets | **Mitigates 42 battery failure hazards** and prevents unplanned employee downtime |
| **🎫 ITSM Surge** | **Emergency SOX Fast-Track Approval**<br>*(Jira Service Management)* | Month-End close cutoff spikes ERP access requests by **700%** | Temporarily activates pre-approved dual-signer matrix for 72-hour window | **Reduces MTTR from 3.8 hrs to 12 mins**, unblocking finance teams for accounting close |

<br>
<br>

### 📑 Generating & Exporting Executive Reports (PDF & Markdown)

> **💡 Purpose & Significance:**  
> IT and FinOps managers spend hours manually aggregating data and formatting slide decks for executive reviews. The Executive Report generator automates this entire process in one click, producing audit-ready financial summaries for quarterly budget approvals and executive sign-offs.

<br>

WorkplacePulse includes an automated reporting engine designed for C-suite and board presentations.

1. Click the **Export Report (PDF)** button at the top right of the dashboard (or click **📄 View Executive Report** from any active runbook execution).
2. The platform renders a clean, print-optimized executive summary modal containing key ROI metrics, active Chart.js visualizations, Gemini strategic recommendations, and audit logs.
3. Click **⬇️ Download PDF** to generate an uncorrupted, multi-page PDF document free of awkward page breaks, or copy the audit-ready markdown format.

<br>
<br>

---

<br>

## 5. Managing Data Sources

> **💡 Purpose & Significance:**  
> Enterprise transparency requires proving where data originates. The Data Sources hub and Live Sync Terminal provide full visibility into the ingestion pipeline, ensuring compliance officers and security teams can verify data provenance, API scopes, and encryption protocols.

<br>

The **Data Sources** view (accessible via the sidebar) allows IT administrators to manage third-party integrations across Okta, Figma, Jamf Pro, Jira, and Zoom.

<br>

<img src="./assets/screenshots/data-sources-overview.png" width="720" alt="Data Sources & Integrations Hub" />

<br>
<br>

1. Click on **Data Sources** in the left navigation menu.
2. You will see connection cards for all supported enterprise platforms.
3. Click **Connect / Sync** on any integration to launch the **Live Data Sync Terminal**.
4. The terminal streams the real-time mTLS handshake, OAuth token exchange, REST endpoint queries, and delta calculation steps, followed by a **Raw Data Preview Table**.

<br>

<img src="./assets/screenshots/data-sources-sync-terminal.png" width="560" alt="Live Data Sync Terminal & Raw Data Preview" />

<br>
<br>

---

<br>

## 6. Webhooks & Alerting

> **💡 Purpose & Significance:**  
> Insights are useless if they remain trapped in a dashboard. The Webhook Engine closes the loop by automatically dispatching formatted, actionable alerts to incident response channels, enabling engineers to approve 1-click license reclaims or shift adjustments without leaving Slack.

<br>

WorkplacePulse autonomously bridges predictive intelligence into your team's everyday communication channels.

1. Click the 🔔 **Alerts** icon or navigate to **Webhook Hub** in the sidebar.
2. Register destination endpoints for **Slack**, **Discord**, **Microsoft Teams**, or custom REST webhooks using 1-click test presets.

<br>

| 1️⃣ Registered Destinations | 2️⃣ Register Destination (+ Presets) |
| :---: | :---: |
| <img src="./assets/screenshots/webhook-modal-destinations.png" width="360" alt="Webhook Hub - Registered Destinations" /> | <img src="./assets/screenshots/webhook-modal-register.png" width="360" alt="Webhook Hub - Register Destination" /> |

<br>
<br>

3. Outgoing alert notifications sent to Slack, Teams, or Discord are formatted as interactive rich cards (with buttons and impact metrics) and cryptographically signed with an `X-Pulse-Signature: sha256=<hex>` HMAC-SHA256 header for enterprise security verification.

<br>

<img src="./assets/screenshots/webhook-test-ping-success-v2.png" width="560" alt="Webhook Test Ping Dispatch & Audit" />

<br>
<br>

4. Inspect the **Delivery Audit Trail** to view execution timestamps and HTTP delivery response codes.

<br>

<img src="./assets/screenshots/webhook-delivery-audit-trail.png" width="560" alt="Webhook Delivery Audit Trail" />

<br>
<br>

5. Use the **Simulation Mode** tab to test payload delivery.

<br>

<img src="./assets/screenshots/webhook-simulation-pipeline.png" width="560" alt="Webhook Simulation Mode & Pipeline Visualizer" />

<br>
<br>

---

<br>

## 7. Live Support & Troubleshooting

> **💡 Purpose & Significance:**  
> Reduces Tier-1 IT helpdesk burden by resolving common user queries autonomously while providing a clear, auditable escalation path for enterprise procurement and security inquiries.

<br>

The **Support & Help** section provides self-service onboarding assistance and direct escalation channels.

*   **Interactive Knowledge Base:** Browse expandable FAQs regarding BYOK setup, billing tiers, and data governance.
*   **Ticket Submission:** Open a formal IT escalation ticket with built-in form validation.
*   **Sentinel Support Copilot:** Chat in real time with "Alex", the empathetic AI support specialist, for 24/7 troubleshooting and guidance.

<br>

<img src="./assets/screenshots/support-help-center.png" width="720" alt="Support & Help Center Hub" />

<br>
<br>
