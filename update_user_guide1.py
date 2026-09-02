import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

# Update the workspace version
with open(ws_path, 'r') as f:
    ws_content = f.read()

ws_content = ws_content.replace(
    '![Login Screen](./assets/screenshots/login-screen.png)\n*(Screenshot Placeholder: The landing page with the Google Sign-In button)*',
    '![Login Screen](./assets/screenshots/login-popup.png)'
)
with open(ws_path, 'w') as f:
    f.write(ws_content)

# Update the artifact version (needs absolute path for the image)
with open(art_path, 'r') as f:
    art_content = f.read()

art_content = art_content.replace(
    '![Login Screen](./assets/screenshots/login-screen.png)\n*(Screenshot Placeholder: The landing page with the Google Sign-In button)*',
    '![Login Screen](/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/login-popup.png)'
)
with open(art_path, 'w') as f:
    f.write(art_content)

print("Updated User Guide with the login popup screenshot.")
