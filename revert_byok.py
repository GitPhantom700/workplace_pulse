import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

for path in [ws_path, art_path]:
    with open(path, 'r') as f:
        content = f.read()
    
    # We want to replace the current BYOK image block with the placeholder
    old_byok_real = "![BYOK Setup](./assets/screenshots/byok-setup.png)\n*Figure 2: The Bring-Your-Own-Key configuration panel for activating live Gemini AI intelligence.*"
    old_byok_real_art = "![BYOK Setup](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/byok-setup.png)\n*Figure 2: The Bring-Your-Own-Key configuration panel for activating live Gemini AI intelligence.*"

    new_placeholder = "![BYOK Setup](./assets/screenshots/byok-setup.png)\n*(Screenshot Placeholder: The API Credentials form inside the Copilot panel)*"

    if path == ws_path:
        content = content.replace(old_byok_real, new_placeholder)
    else:
        content = content.replace(old_byok_real_art, new_placeholder)
        
    with open(path, 'w') as f:
        f.write(content)

print("Reverted BYOK to placeholder.")
