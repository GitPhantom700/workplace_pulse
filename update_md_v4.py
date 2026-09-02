import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/DEPLOYMENT.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/DEPLOYMENT.md'

with open(ws_path, 'r') as f:
    content = f.read()

new_content_ws = content.replace(
    'firebase-auth-save-redacted-v3.png', 
    'firebase-auth-save-redacted-v4.png'
)

with open(ws_path, 'w') as f:
    f.write(new_content_ws)

with open(art_path, 'r') as f:
    art_content = f.read()

new_content_art = art_content.replace(
    'firebase-auth-save-redacted-v3.png',
    'firebase-auth-save-redacted-v4.png'
)

with open(art_path, 'w') as f:
    f.write(new_content_art)

print("Markdown updated to v4")
