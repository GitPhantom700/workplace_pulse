import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

with open(ws_path, 'r') as f:
    ws_content = f.read()

replacement = """![Executive Dashboard (Pre-Login)](./assets/screenshots/executive-dashboard-pre.png)
*Figure 1a: Pre-login state (Demo Mode ON).*

![Executive Dashboard (Post-Login)](./assets/screenshots/executive-dashboard-post.png)
*Figure 1b: Post-login state showing active User Profile and Demo Mode OFF.*"""

ws_content = ws_content.replace(
    '![Executive Dashboard](./assets/screenshots/executive-dashboard.png)\n*(Screenshot Placeholder: The main dashboard showing the KPI cards and Chart.js visualizations)*',
    replacement
)
with open(ws_path, 'w') as f:
    f.write(ws_content)

with open(art_path, 'r') as f:
    art_content = f.read()

replacement_art = """![Executive Dashboard (Pre-Login)](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre.png)
*Figure 1a: Pre-login state (Demo Mode ON).*

![Executive Dashboard (Post-Login)](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post.png)
*Figure 1b: Post-login state showing active User Profile and Demo Mode OFF.*"""

art_content = art_content.replace(
    '![Executive Dashboard](./assets/screenshots/executive-dashboard.png)\n*(Screenshot Placeholder: The main dashboard showing the KPI cards and Chart.js visualizations)*',
    replacement_art
)
with open(art_path, 'w') as f:
    f.write(art_content)

print("Updated User Guide with Dashboard screenshots.")
