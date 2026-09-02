import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    html = f.read()

scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
if scripts:
    main_script = scripts[-1]
    with open('extracted_script.js', 'w') as f:
        f.write(main_script)
    print("Script extracted. Running node -c...")
else:
    print("No scripts found")
