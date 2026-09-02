import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/DEPLOYMENT.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/DEPLOYMENT.md'

with open(ws_path, 'r') as f:
    content = f.read()

# Replace the old image reference with the redacted one
new_content_ws = content.replace(
    './assets/screenshots/firebase-auth-save.png', 
    './assets/screenshots/firebase-auth-save-redacted.png'
)

with open(ws_path, 'w') as f:
    f.write(new_content_ws)

# Do the same for the artifact view (absolute paths)
with open(art_path, 'r') as f:
    art_content = f.read()

new_content_art = art_content.replace(
    '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/firebase-auth-save.png',
    '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/firebase-auth-save-redacted.png'
)

with open(art_path, 'w') as f:
    f.write(new_content_art)

print("Updated markdown references.")
