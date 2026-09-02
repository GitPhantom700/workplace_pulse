import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# Restore Project ID button
pattern_proj = r'(<input type="text" id="project-id-input"[^>]*>)'
replace_proj = r'\1\n                                            <button type="button" onclick="document.getElementById(\'project-id-input\').value = \'prj-\' + Math.random().toString(36).substring(2,8)" class="text-[10px] bg-slate-100 border border-slate-200 text-slate-600 px-2 py-2 rounded-lg hover:bg-slate-200 transition font-bold">Generate</button>'
# Only restore if it's missing the button (which it is)
if 'onclick="document.getElementById(\'project-id-input\').value' not in content:
    content = re.sub(pattern_proj, replace_proj, content)

# Restore OAuth Client ID button
pattern_oauth = r'(<input type="text" id="oauth-id-input"[^>]*>)'
replace_oauth = r'\1\n                                            <button type="button" onclick="document.getElementById(\'oauth-id-input\').value = \'cid-\' + Math.random().toString(36).substring(2,10)" class="text-[9px] bg-slate-100 border border-slate-200 text-slate-600 px-1.5 py-2 rounded-lg hover:bg-slate-200 transition font-bold">Gen</button>'
if 'onclick="document.getElementById(\'oauth-id-input\').value' not in content:
    content = re.sub(pattern_oauth, replace_oauth, content)

with open(html_path, 'w') as f:
    f.write(content)

print("Restored buttons.")
