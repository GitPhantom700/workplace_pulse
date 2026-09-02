import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# I want to add UI reset logic when validation fails
# Let's find the validation logic I inserted earlier
search_str = """            if (!isLegacyFmt && !isNewFmt) {
                errorEl.innerText = '❌ Invalid key format. A valid Google Gemini API key must start with "AIzaSy" (and be 39+ chars) or start with "AQ.". Get yours at aistudio.google.com.';
                errorEl.classList.remove('hidden');
                return;
            }"""

replacement = """            if (!isLegacyFmt && !isNewFmt) {
                errorEl.innerText = '❌ Invalid key format. A valid Google Gemini API key must start with "AIzaSy" (and be 39+ chars) or start with "AQ.". Get yours at aistudio.google.com.';
                errorEl.classList.remove('hidden');
                
                // Reset the UI to "Not Connected" since they provided an invalid key
                sessionStorage.removeItem('byok_gemini_key');
                sessionStorage.removeItem('gemini_api_key');
                sessionStorage.removeItem('byok_key_connected');
                if (statusLabel) {
                    statusLabel.innerText = "Not Connected";
                    statusLabel.className = "text-[10px] bg-slate-100 text-slate-500 border border-slate-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
                const aiBadge = document.getElementById('ai-data-badge');
                if (aiBadge) {
                    aiBadge.innerText = "Dummy Data";
                    aiBadge.className = "text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }
                return;
            }"""

content = content.replace(search_str, replacement)

with open(html_path, 'w') as f:
    f.write(content)
print("Updated validation to reset UI.")
