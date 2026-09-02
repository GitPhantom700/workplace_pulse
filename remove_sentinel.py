import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

for path in [ws_path, art_path]:
    with open(path, 'r') as f:
        content = f.read()
    
    # Remove Sentinel word
    content = content.replace('**WorkplacePulse Sentinel** command center', '**WorkplacePulse** command center')
    content = content.replace('**Sentinel Executive Dashboard**', '**WorkplacePulse Executive Dashboard**')
    
    with open(path, 'w') as f:
        f.write(content)

print("Removed Sentinel from user guide.")
