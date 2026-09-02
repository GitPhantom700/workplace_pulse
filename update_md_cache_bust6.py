import re
import shutil

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

for path in [ws_path, art_path]:
    with open(path, 'r') as f:
        content = f.read()
    
    # Rename for cache bust
    content = content.replace('executive-dashboard-post-v5.png', 'executive-dashboard-post-v6.png')
    
    # Inject BYOK image
    byok_placeholder = "![BYOK Setup](./assets/screenshots/byok-setup.png)\n*(Screenshot Placeholder: The API Credentials form inside the Copilot panel)*"
    byok_placeholder_art = "![BYOK Setup](./assets/screenshots/byok-setup.png)\n*(Screenshot Placeholder: The API Credentials form inside the Copilot panel)*"
    
    byok_real = "![BYOK Setup](./assets/screenshots/byok-setup.png)\n*Figure 2: The Bring-Your-Own-Key configuration panel for activating live Gemini AI intelligence.*"
    byok_real_art = "![BYOK Setup](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/byok-setup.png)\n*Figure 2: The Bring-Your-Own-Key configuration panel for activating live Gemini AI intelligence.*"

    if path == ws_path:
        content = content.replace(byok_placeholder, byok_real)
    else:
        # It might still have the original placeholder in the artifact
        content = content.replace(byok_placeholder_art, byok_real_art)

    with open(path, 'w') as f:
        f.write(content)

# Copy the images
shutil.copy('/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post.png', 
            '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post-v6.png')
shutil.copy('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post.png', 
            '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post-v6.png')

# Save BYOK image
shutil.copy('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788323848099.png',
            '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/byok-setup.png')
shutil.copy('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788323848099.png',
            '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/byok-setup.png')

print("Busted cache v6 and injected BYOK image.")
