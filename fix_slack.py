html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# Fix Slack fields
content = content.replace("`*Severity:*n`${eventDetails.severity}``", r"`*Severity:*\n\`${eventDetails.severity}\``")
content = content.replace("`*Target System:*n${eventDetails.target}`", r"`*Target System:*\n${eventDetails.target}`")
content = content.replace("`*Financial Impact:*n${eventDetails.impact}`", r"`*Financial Impact:*\n${eventDetails.impact}`")
content = content.replace("`*Status:*n🟢 Autonomous Remediation Complete`", r"`*Status:*\n🟢 Autonomous Remediation Complete`")

with open(html_path, 'w') as f:
    f.write(content)
