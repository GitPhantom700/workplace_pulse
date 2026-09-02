import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# I need to escape the backticks inside the template literals.
# Instead of guessing all places, let's just escape the markdown code blocks in mdContent.
content = content.replace("```text", r"\`\`\`text")
content = content.replace("```\n", r"\`\`\`\n")

# Wait, there might be other places where backticks were used inside template literals.
# Let's check for any other triple backticks.
content = content.replace("```", r"\`\`\`")

# Actually, the above replace will replace the ones we just did again if we're not careful.
# Let's do it cleanly:
content = content.replace(r"\`\`\`", "```") # revert just in case
content = content.replace("```", r"\`\`\`")

with open(html_path, 'w') as f:
    f.write(content)
