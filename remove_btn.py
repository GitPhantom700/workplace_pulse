import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# The specific button code:
# <button type="button" onclick="document.getElementById('api-key-input').value = 'AIzaSyDemo' + Math.random().toString(36).substring(2,10)" class="text-[10px] bg-slate-100 border border-slate-200 text-slate-600 px-2 py-2 rounded-lg hover:bg-slate-200 transition font-bold">Generate</button>
pattern = r'(<input type="password" id="api-key-input"[^>]*>)\s*<button type="button" onclick="document\.getElementById\(\'api-key-input\'\)\.value = [^"]+" class="[^"]*">Generate</button>'

new_content = re.sub(pattern, r'\1', content)

if content != new_content:
    with open(html_path, 'w') as f:
        f.write(new_content)
    print("Generate button removed from index.html")
else:
    print("Could not find the exact pattern.")

