import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# Replace <span>Connect Key</span> with <span>Connect</span>
new_content = content.replace('<span>Connect Key</span>', '<span>Connect</span>')

if content != new_content:
    with open(html_path, 'w') as f:
        f.write(new_content)
    print("Renamed 'Connect Key' to 'Connect'.")
else:
    print("Could not find 'Connect Key'.")
