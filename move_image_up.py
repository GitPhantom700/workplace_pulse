import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

for path in [ws_path, art_path]:
    with open(path, 'r') as f:
        content = f.read()
    
    # We want to move the image block above the numbered list in Section 1.
    
    if path == ws_path:
        img_block = "![Executive Dashboard (Pre-Login)](./assets/screenshots/executive-dashboard-pre.png)\n*Figure 1: The pre-login landing page. The highlighted buttons in the top right control authentication and Demo Mode.*\n"
    else:
        img_block = "![Executive Dashboard (Pre-Login)](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre-v4.png)\n*Figure 1: The pre-login landing page. The highlighted buttons in the top right control authentication and Demo Mode.*\n"

    # Remove the img_block from its current position
    content = content.replace(img_block, "")
    
    # Insert it right after the intro text
    insert_target = "When you first navigate to the platform, you will be presented with the **Pre-Login Landing Page**. By default, the system operates in a simulated sandbox.\n\n"
    
    content = content.replace(insert_target, insert_target + img_block + "\n")
    
    with open(path, 'w') as f:
        f.write(content)

print("Moved image up.")
