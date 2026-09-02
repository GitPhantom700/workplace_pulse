import re

with open("static/index.html", "r") as f:
    content = f.read()

# Update Copilot Header
copilot_header = """                        <div class="p-6 border-b border-slate-50 flex items-center justify-between">
                            <div class="flex items-center space-x-2">
                                <h3 class="text-lg font-bold text-slate-800">Gemini Copilot</h3>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span id="api-key-status-label" class="text-[10px] bg-slate-100 text-slate-500 border border-slate-200 px-2.5 py-1 rounded-full font-bold tracking-wide">Not Connected</span>
                                <span class="text-[10px] bg-indigo-50 text-indigo-600 px-2.5 py-1 rounded-full font-bold tracking-wide">AI ACTIVE</span>
                            </div>
                        </div>"""
                        
new_copilot_header = """                        <div class="p-6 border-b border-slate-50 flex items-center justify-between">
                            <div class="flex items-center space-x-2">
                                <h3 class="text-lg font-bold text-slate-800">Gemini Copilot</h3>
                                <span id="ai-data-badge" class="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide">Dummy Data</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span id="api-key-status-label" class="text-[10px] bg-slate-100 text-slate-500 border border-slate-200 px-2.5 py-1 rounded-full font-bold tracking-wide">Not Connected</span>
                                <span class="text-[10px] bg-indigo-50 text-indigo-600 px-2.5 py-1 rounded-full font-bold tracking-wide">AI ACTIVE</span>
                            </div>
                        </div>"""

if copilot_header in content:
    content = content.replace(copilot_header, new_copilot_header)
    print("Patched Copilot header")
else:
    print("Copilot header not found")

# Update Support AI Chat Header
supp_header = """                            <div class="flex items-center space-x-2">
                                <span id="support-api-key-status-label" class="text-[10px] bg-slate-100 text-slate-500 border border-slate-200 px-2.5 py-1 rounded-full font-bold tracking-wide">Not Connected</span>
                                <span class="text-[10px] bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-full font-bold tracking-wide">ONLINE</span>
                            </div>"""

new_supp_header = """                            <div class="flex items-center space-x-2">
                                <span id="supp-ai-data-badge" class="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide">Dummy Data</span>
                                <span id="support-api-key-status-label" class="text-[10px] bg-slate-100 text-slate-500 border border-slate-200 px-2.5 py-1 rounded-full font-bold tracking-wide">Not Connected</span>
                                <span class="text-[10px] bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-full font-bold tracking-wide">ONLINE</span>
                            </div>"""

if supp_header in content:
    content = content.replace(supp_header, new_supp_header)
    print("Patched Support header")
else:
    print("Support header not found")


# Update JS logic to change Dummy Data -> Live Data
js_update_str = """                // Update Labels
                if(statusLabel) {
                    statusLabel.innerText = "API Key Connected";
                    statusLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }"""
                
js_update_new = """                // Update Labels
                if(statusLabel) {
                    statusLabel.innerText = "API Key Connected";
                    statusLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
                const aiBadge = document.getElementById('ai-data-badge');
                if(aiBadge) {
                    aiBadge.innerText = "Live Data";
                    aiBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }
                const suppBadge = document.getElementById('supp-ai-data-badge');
                if(suppBadge) {
                    suppBadge.innerText = "Live Data";
                    suppBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }"""

content = content.replace(js_update_str, js_update_new)

# Update DOMContentLoaded JS logic
js_onload_str = """                if(statusLabel) {
                    statusLabel.innerText = "API Key Connected";
                    statusLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }"""

js_onload_new = """                if(statusLabel) {
                    statusLabel.innerText = "API Key Connected";
                    statusLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
                const aiBadge = document.getElementById('ai-data-badge');
                if(aiBadge) {
                    aiBadge.innerText = "Live Data";
                    aiBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }
                const suppBadge = document.getElementById('supp-ai-data-badge');
                if(suppBadge) {
                    suppBadge.innerText = "Live Data";
                    suppBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }"""

# Using regex because JS is duplicated in 2 places (connect func and onload func)
content = re.sub(r'if\(statusLabel\) \{.*?\}', js_onload_new, content, flags=re.DOTALL)


with open("static/index.html", "w") as f:
    f.write(content)

