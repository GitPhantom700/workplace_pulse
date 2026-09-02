import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# 1. Fix the quotes in the JS template literals (rec.title)
content = content.replace(".replace(/'/g, \"'\")", r".replace(/'/g, \"\\'\")")

# 2. Fix the regex in replace for chart image
content = content.replace(".*?</canvas>/is,", r".*?<\/canvas>/is,")

# 3. Fix the webhook innerText replacement
content = content.replace(".replace(/n/g, 'n- ')", r".replace(/\n/g, '\n- ')")

# 4. Fix recsMarkdown \n replacements (looks like .n- [ ])
content = content.replace(".n- [ ]", ".\\n- [ ]")
content = content.replace("mo).n- [ ]", "mo).\\n- [ ]")
content = content.replace("risk.n- [ ]", "risk.\\n- [ ]")
content = content.replace("units.n- [ ]", "units.\\n- [ ]")
content = content.replace("+3.n- [ ]", "+3.\\n- [ ]")
content = content.replace("minutes.n- [ ]", "minutes.\\n- [ ]")

# 5. Fix the MacBook Pro unescaped quotes in device fields
content = content.replace('MacBook Pro 16" (M3 Max)"', r'MacBook Pro 16\" (M3 Max)"')
content = content.replace('MacBook Air 15" (M2)"', r'MacBook Air 15\" (M2)"')
content = content.replace('MacBook Pro 14" (M1 Pro)"', r'MacBook Pro 14\" (M1 Pro)"')
content = content.replace('MacBook Air 13" (M1)"', r'MacBook Air 13\" (M1)"')
content = content.replace('MacBook Pro 16" (M2 Max)"', r'MacBook Pro 16\" (M2 Max)"')
content = content.replace('MacBook Air 13" (M2)"', r'MacBook Air 13\" (M2)"')
content = content.replace('MacBook Pro 14" (M3 Pro)"', r'MacBook Pro 14\" (M3 Pro)"')
content = content.replace('MacBook Pro 16" (M1 Max)"', r'MacBook Pro 16\" (M1 Max)"')
content = content.replace('MacBook Air 15" (M3)"', r'MacBook Air 15\" (M3)"')
content = content.replace('MacBook Pro 13" (M1, 2020)"', r'MacBook Pro 13\" (M1, 2020)"')
content = content.replace('MacBook Pro 14" (M1 Pro, 2021)"', r'MacBook Pro 14\" (M1 Pro, 2021)"')
content = content.replace('MacBook Pro 16" (M2 Pro, 2023)"', r'MacBook Pro 16\" (M2 Pro, 2023)"')


with open(html_path, 'w') as f:
    f.write(content)
print("Applied syntax fixes.")
