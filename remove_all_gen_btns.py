import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# Remove Generate button next to Project ID
pattern_proj = r'(<input type="text" id="project-id-input"[^>]*>)\s*<button type="button" onclick="document\.getElementById\(\'project-id-input\'\)\.value = [^"]+" class="[^"]*">Generate</button>'
content = re.sub(pattern_proj, r'\1', content)

# Remove Gen button next to OAuth Client ID
pattern_oauth = r'(<input type="text" id="oauth-id-input"[^>]*>)\s*<button type="button" onclick="document\.getElementById\(\'oauth-id-input\'\)\.value = [^"]+" class="[^"]*">Gen</button>'
content = re.sub(pattern_oauth, r'\1', content)

# Remove Gen button next to Client Secret
pattern_secret = r'(<input type="password" id="client-secret-input"[^>]*>)\s*<button type="button" onclick="document\.getElementById\(\'client-secret-input\'\)\.value = [^"]+" class="[^"]*">Gen</button>'
content = re.sub(pattern_secret, r'\1', content)

with open(html_path, 'w') as f:
    f.write(content)

print("Removed all Generate/Gen buttons in the BYOK panel.")
