import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/USER_GUIDE.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/USER_GUIDE.md'

for path in [ws_path, art_path]:
    with open(path, 'r') as f:
        content = f.read()
    
    # Rename for cache bust
    content = content.replace('executive-dashboard-pre.png', 'executive-dashboard-pre-v2.png')
    content = content.replace('executive-dashboard-post.png', 'executive-dashboard-post-v2.png')
    
    with open(path, 'w') as f:
        f.write(content)

import shutil
shutil.copy('/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-pre.png', 
            '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-pre-v2.png')
shutil.copy('/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post.png', 
            '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post-v2.png')
shutil.copy('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre.png', 
            '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre-v2.png')
shutil.copy('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post.png', 
            '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post-v2.png')

print("Busted cache.")
