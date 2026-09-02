import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# Find the DOMContentLoaded where it checks sessionStorage
search_str = """        document.addEventListener('DOMContentLoaded', () => {
            if(sessionStorage.getItem('gemini_api_key')) {"""
            
replacement = """        document.addEventListener('DOMContentLoaded', () => {
            const savedKey = sessionStorage.getItem('byok_gemini_key') || sessionStorage.getItem('gemini_api_key');
            if(savedKey && (savedKey.startsWith('AIzaSy') || savedKey.startsWith('AQ.'))) {"""

content = content.replace(search_str, replacement)

# Another DOMContentLoaded section checks byok_gemini_key
search_str2 = """        // Check BYOK session storage
        document.addEventListener('DOMContentLoaded', () => {
            const savedKey = sessionStorage.getItem('byok_gemini_key');
            if (savedKey) {"""

replacement2 = """        // Check BYOK session storage
        document.addEventListener('DOMContentLoaded', () => {
            const savedKey = sessionStorage.getItem('byok_gemini_key');
            if (savedKey && (savedKey.startsWith('AIzaSy') || savedKey.startsWith('AQ.'))) {"""

content = content.replace(search_str2, replacement2)

with open(html_path, 'w') as f:
    f.write(content)
print("Added validation to sessionStorage loader.")
