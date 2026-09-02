html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

content = content.replace(r"`🕒 Timestamp: ${new Date().toISOString()} | Ref: `INC-${Math.floor(Math.random()*900000+100000)}``", r"`🕒 Timestamp: ${new Date().toISOString()} | Ref: \`INC-${Math.floor(Math.random()*900000+100000)}\``")

with open(html_path, 'w') as f:
    f.write(content)
