import re
import shutil

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'
user_upload = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788324250120.png'

# Save BYOK image (cache bust by renaming to byok-setup-v2.png)
shutil.copy(user_upload, '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/byok-setup-v2.png')
shutil.copy(user_upload, '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/byok-setup-v2.png')

for path in [ws_path, art_path]:
    with open(path, 'r') as f:
        content = f.read()
    
    # We want to replace the current placeholder
    placeholder = "![BYOK Setup](./assets/screenshots/byok-setup.png)\n*(Screenshot Placeholder: The API Credentials form inside the Copilot panel)*"
    placeholder_art = "![BYOK Setup](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/byok-setup.png)\n*(Screenshot Placeholder: The API Credentials form inside the Copilot panel)*"

    real = "![BYOK Setup](./assets/screenshots/byok-setup-v2.png)\n*Figure 2: The Bring-Your-Own-Key configuration panel for activating live Gemini AI intelligence.*"
    real_art = "![BYOK Setup](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/byok-setup-v2.png)\n*Figure 2: The Bring-Your-Own-Key configuration panel for activating live Gemini AI intelligence.*"

    if path == ws_path:
        content = content.replace(placeholder, real)
    else:
        # Check both relative and absolute paths in artifact just in case
        content = content.replace(placeholder, real_art)
        content = content.replace(placeholder_art, real_art)

    with open(path, 'w') as f:
        f.write(content)

print("Injected final BYOK image.")
