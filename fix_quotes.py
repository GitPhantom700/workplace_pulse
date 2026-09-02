html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# Replace the broken replace function
content = content.replace(r'''replace(/'/g, \"\\'\")''', r'''replace(/'/g, "\\'")''')

with open(html_path, 'w') as f:
    f.write(content)
