import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

for path in [ws_path, art_path]:
    if path == ws_path:
        img_pre = "./assets/screenshots/executive-dashboard-pre.png"
        img_login = "./assets/screenshots/login-popup.png"
        img_post = "./assets/screenshots/executive-dashboard-post.png"
    else:
        img_pre = "/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre-v4.png"
        img_login = "/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/login-popup.png"
        img_post = "/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post-v5.png"

    with open(path, 'r') as f:
        content = f.read()

    # We will just rewrite the sections from scratch up to section 3
    
    new_top = f"""# WorkplacePulse User Guide

Welcome to the **WorkplacePulse** command center. This platform provides continuous, multi-tenant intelligence, bringing your IT service management (ITSM), HR telemetry, and SaaS licensing data into a unified, actionable dashboard powered by AI.

This guide walks you through the primary workflows, analytics views, and autonomous capabilities of the platform.

---

## 1. Authentication & Setup

When you first navigate to the platform, you will be presented with the **Pre-Login Landing Page**. By default, the system operates in a simulated sandbox.

![Executive Dashboard (Pre-Login)]({img_pre})
*Figure 1a: The pre-login landing page. The highlighted buttons in the top right control authentication and Demo Mode.*

1. Note the **Demo Mode: ON** toggle in the top right corner. This allows you to explore the dashboard using simulated dummy data without connecting live telemetry.
2. To connect to your live enterprise data, toggle Demo Mode to **OFF**. 
3. Click the **Sign in with Google** button in the top right corner. This will trigger the authentication popup.

![Google Login]({img_login})
*Figure 1b: Google Sign-In popup for tenant authentication.*

Upon successful authentication, your unique Tenant ID is assigned, and you will be routed to the live **WorkplacePulse Executive Dashboard**.

![Executive Dashboard (Post-Login)]({img_post})
*Figure 1c: The post-login state showing your active User Profile, Demo Mode OFF, and live telemetry data.*

---

## 2. Navigating the Executive Dashboard

The main dashboard presents an aggregated view of your enterprise's IT health. 

### Key Performance Indicators (KPIs)
At the top of the dashboard, you will find real-time KPI metrics assessing:
*   **Idle SaaS Capital:** Wasted spend on unused licenses.
*   **Support Ticket Surge:** Volume of active ITSM escalations.
*   **Hardware Degradation:** Fleet health and end-of-life device counts.

### Interactive Telemetry Scenarios
You can filter the data visualizations using the left-hand **Scenario Navigation** bar:
*   **SaaS FinOps (Okta/Figma/Zoom):** Visualizes license utilization versus spend.
*   **Hardware Lifecycle (Jamf):** Maps battery degradation and OS compliance.
*   **ITSM Surge (Jira):** Details support ticket spikes and resolution times.

---

## 3. Gemini Copilot"""

    # Replace everything before "## 3. Gemini Copilot" with new_top
    content = re.sub(r'^.*?## 3\. Gemini Copilot', new_top, content, flags=re.DOTALL)
    
    with open(path, 'w') as f:
        f.write(content)

print("Updated structure to strictly flow 1a, 1b, 1c.")
