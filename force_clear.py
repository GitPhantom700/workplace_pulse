import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# Add a check to clear invalid or dummy keys on page load
clear_script = """
        // Force clear any dummy keys that might be stuck in session storage
        if (sessionStorage.getItem('byok_gemini_key') === 'AIzaSyDummyKeyForDemo123' || 
            sessionStorage.getItem('gemini_api_key') === 'AIzaSyDummyKeyForDemo123') {
            sessionStorage.removeItem('byok_gemini_key');
            sessionStorage.removeItem('gemini_api_key');
            sessionStorage.removeItem('byok_key_connected');
        }
"""

content = content.replace("        // Check API Key Status on load", clear_script + "\n        // Check API Key Status on load")

with open(html_path, 'w') as f:
    f.write(content)
print("Added script to clear dummy keys on load.")
