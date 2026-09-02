import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

for path in [ws_path, art_path]:
    with open(path, 'r') as f:
        content = f.read()
    
    wrong_webhook_art = "![Webhook Hub](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/webhook-hub.png)\n*Figure 4: The Webhook Hub configuration panel for alert destinations.*"
    wrong_webhook = "![Webhook Hub](./assets/screenshots/webhook-hub.png)\n*Figure 4: The Webhook Hub configuration panel for alert destinations.*"

    right_placeholder = "![Webhook Hub](./assets/screenshots/webhook-hub.png)\n*(Screenshot Placeholder: The Webhook Hub modal showing registered destinations or the audit trail)*"

    if path == ws_path:
        content = content.replace(wrong_webhook, right_placeholder)
    else:
        content = content.replace(wrong_webhook_art, right_placeholder)

    with open(path, 'w') as f:
        f.write(content)

print("Restored Webhook placeholder.")
