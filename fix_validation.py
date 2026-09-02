import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# We want to insert the validation logic right after checking `if (!key) { ... }` in connectApiCredentials.
validation_logic = """
            if (!key) {
                errorEl.innerText = "Please enter an API Key.";
                errorEl.classList.remove('hidden');
                return;
            }

            const isLegacyFmt = key.startsWith('AIzaSy') && key.length >= 35;
            const isNewFmt = key.startsWith('AQ.');
            
            if (!isLegacyFmt && !isNewFmt) {
                errorEl.innerText = '❌ Invalid key format. A valid Google Gemini API key must start with "AIzaSy" (and be 39+ chars) or start with "AQ.". Get yours at aistudio.google.com.';
                errorEl.classList.remove('hidden');
                return;
            }
"""

# Replace the existing `if (!key) { ... }` with the new one containing validation
# Search for:
search_str = """            if (!key) {
                errorEl.innerText = "Please enter an API Key.";
                errorEl.classList.remove('hidden');
                return;
            }"""

content = content.replace(search_str, validation_logic.strip('\n'))

with open(html_path, 'w') as f:
    f.write(content)
print("Added validation to connectApiCredentials.")
