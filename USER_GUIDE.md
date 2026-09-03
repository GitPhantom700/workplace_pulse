# WorkplacePulse User Guide

Welcome to the **WorkplacePulse** command center. This platform provides continuous, multi-tenant intelligence, bringing your IT service management (ITSM), HR telemetry, and SaaS licensing data into a unified, actionable dashboard powered by AI.

This guide walks you through the primary workflows, analytics views, and autonomous capabilities of the platform.

---

## 1. Authentication & Setup

When you first navigate to the platform, you will be presented with the **Pre-Login Landing Page**. By default, the system operates in a simulated sandbox.

<br>

![Executive Dashboard (Pre-Login)](./assets/screenshots/executive-dashboard-pre.png)
*Figure 1a: The pre-login landing page. The highlighted buttons in the top right control authentication and Demo Mode.*

<br>

1. Note the **Demo Mode: ON** toggle in the top right corner. This allows you to explore the dashboard using simulated dummy data without connecting live telemetry.
2. To connect to your live enterprise data, toggle Demo Mode to **OFF**. 
3. Click the **Sign in with Google** button in the top right corner. This will trigger the authentication popup.

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

## 2. Navigating the Executive Dashboard

The main dashboard presents an aggregated view of your enterprise's IT health. 

<br>

### Key Performance Indicators (KPIs)
At the top of the dashboard, you will find real-time KPI metrics assessing:
*   **Idle SaaS Capital:** Wasted spend on unused licenses.

    ![Idle SaaS Capital](./assets/screenshots/kpi-idle-saas-capital.png)

*   **Support Ticket Surge:** Volume of active ITSM escalations.

    ![Support Ticket Surge](./assets/screenshots/kpi-itsm-ticket-surge.png)

*   **Hardware Degradation:** Fleet health and end-of-life device counts.

    ![Hardware Degradation](./assets/screenshots/kpi-hardware-degradation.png)

<br>

### Interactive Telemetry Scenarios
You can filter the data visualizations using the left-hand **Scenario Navigation** bar:
*   **SaaS FinOps (Okta/Figma/Zoom):** Visualizes license utilization versus spend.

    ![SaaS FinOps Telemetry](./assets/screenshots/saas-finops-distribution.png)

*   **Hardware Lifecycle (Jamf):** Maps battery degradation and OS compliance.

    ![Hardware Lifecycle (Jamf)](./assets/screenshots/hardware-lifecycle-jamf.png)

*   **ITSM Surge (Jira):** Details support ticket spikes and resolution times.

<br>

### Predictive Forecasting & Trend Velocity (Q4 Forecast Trend)
The **Detailed Telemetry Matrix** in each module includes a forward-looking **Q4 Forecast Trend** column:
* **SaaS FinOps:** Identifies whether license waste is accelerating ahead of upcoming annual contract renewals (e.g., `↗ +35% Waste` on Figma Enterprise due to 65 dormant accounts).
* **Hardware Lifecycle:** Forecasts upcoming battery failures and AppleCare warranty expirations to project exact CapEx hardware refresh budgets.
* **ITSM Surge:** Quantifies the expected surge multiplier (e.g., `⚡ 7.0x Surge`) for accounting close access requests to proactively optimize engineer shift staffing.
* **Micro-Sparklines:** Visual SVG Bézier curves visually indicate trajectory at a glance (🔴 High Risk Spike, 🟠 Moderate Growth, ⚪ Stable, 🟢 Optimized).

<br>
<br>

---

## 3. Gemini Copilot & Bring-Your-Own-Key (BYOK)

WorkplacePulse integrates directly with Google's Gemini AI to offer strategic recommendations based on your active telemetry.

### Connecting Your API Key (Live Data Mode)
By default, the platform runs in a **Simulated Demo Mode**. To enable live AI intelligence:
1. Locate the **Gemini Copilot** panel on the right side of the dashboard.
2. Enter your **GCP Project ID** and **Gemini API Key**.
3. Click **Connect**.
4. The system will authenticate your key, and the UI badges will switch from <span style="color:orange">Dummy Data</span> to <span style="color:green">Live Data</span>.

Once connected, the **Strategic Recommendations** block below the charts will dynamically generate tailored runbooks and cost-saving plans based on the current scenario.

---

## 4. Managing Data Sources

The **Data Sources** view (accessible via the sidebar) allows you to monitor and synchronize third-party integrations.

1. Click on **Data Sources** in the left navigation menu.
2. You will see integration cards for **Figma Enterprise, Zoom Pro, Jamf Pro, Jira Service Management,** and **Okta**.
3. Click **Connect** on any disconnected integration.
4. A **Live Data Sync Terminal** modal will appear, displaying the live execution logs (OAuth handshakes, API scopes, and telemetry ingestion).
5. Once complete, a **Raw Data Preview** table will display a sample of the ingested users, devices, or tickets.

---

## 5. Webhooks & Alerting

WorkplacePulse can autonomously dispatch alerts to your communication platforms when anomalies are detected.

1. Click the 🔔 **Alerts** icon in the top right to open the **Webhook Hub**.
2. Navigate to the **Register Destination** tab to add a Slack, Discord, or Microsoft Teams webhook URL.
3. Use the **Simulation Mode** tab to test payload delivery.
4. The **Delivery Audit Trail** logs the success or failure of all dispatched alerts.

---

## 6. Live Support & Troubleshooting

If you encounter issues, navigate to the **Support** view via the sidebar.

*   **Knowledge Base:** Browse common FAQs regarding connectors, security isolation, and report generation.
*   **Ticket Submission:** Open a direct ITSM ticket for human escalation.
*   **Live Chatbot:** Interact with "Alex", the telemetry-grounded AI support assistant. (Note: If your API key is connected, this chat is powered by live Gemini AI. If not, it runs in a simulated fallback mode).

---

## 7. Generating Executive Reports

For stakeholder meetings, you can export the current dashboard state into a high-fidelity PDF.

1. Click the **Export Report (PDF)** button at the top right of the dashboard.
2. The platform will dynamically render a print-optimized version of your charts, KPIs, and AI recommendations.
3. The resulting PDF eliminates awkward page breaks and preserves the Chart.js canvas elements seamlessly.
