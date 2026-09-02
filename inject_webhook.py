import re

html_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/static/index.html'
with open(html_path, 'r') as f:
    content = f.read()

# I will craft the HTML snippet that the user wants to see in the Webhook tab.
# The user wants: Project ID, OAuth Client ID, Client Secret, the BYOK Warning, and a Connect Button.
# Let's recreate it exactly as it looked in the BYOK panel.

html_to_inject = """
                <div class="mb-6 bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
                    <h4 class="text-xs font-bold text-slate-800 mb-3 border-b border-slate-100 pb-2">Global Data Integration Credentials</h4>
                    <div class="grid grid-cols-2 gap-3 mb-4">
                        <div class="col-span-2">
                            <label class="block text-[10px] font-bold text-slate-700 uppercase mb-1 flex justify-between"><span>Project ID</span> <span class="text-amber-500">Simulated (Demo)</span></label>
                            <div class="flex items-center space-x-2">
                                <input type="text" id="project-id-input" placeholder="workplacepulse-prod" class="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs focus:outline-none">
                            </div>
                        </div>
                        <div class="col-span-1">
                            <label class="block text-[10px] font-bold text-slate-700 uppercase mb-1 flex justify-between"><span>OAuth Client ID</span> <span class="text-amber-500">Simulated</span></label>
                            <div class="flex items-center space-x-1">
                                <input type="text" id="oauth-id-input" placeholder="Client ID" class="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-2 py-2 text-xs focus:outline-none">
                                <button type="button" onclick="document.getElementById('oauth-id-input').value = 'cid-' + Math.random().toString(36).substring(2,10)" class="text-[9px] bg-slate-100 border border-slate-200 text-slate-600 px-1.5 py-2 rounded-lg hover:bg-slate-200 transition font-bold">Gen</button>
                            </div>
                        </div>
                        <div class="col-span-1">
                            <label class="block text-[10px] font-bold text-slate-700 uppercase mb-1 flex justify-between"><span>Client Secret</span> <span class="text-amber-500">Simulated</span></label>
                            <div class="flex items-center space-x-1">
                                <input type="password" id="oauth-secret-input" placeholder="Secret" class="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-2 py-2 text-xs focus:outline-none">
                                <button type="button" onclick="document.getElementById('oauth-secret-input').value = 'sec-' + Math.random().toString(36).substring(2,10)" class="text-[9px] bg-slate-100 border border-slate-200 text-slate-600 px-1.5 py-2 rounded-lg hover:bg-slate-200 transition font-bold">Gen</button>
                            </div>
                        </div>
                    </div>
                    <div>
                        <p class="text-[10px] text-slate-800 font-medium mt-2 bg-yellow-50 border border-yellow-200 p-2 rounded leading-tight">
                            <strong>Bring Your Own Key (BYOK) Mode:</strong> Your API key is stored securely in temporary browser session memory for testing purposes and is never permanently saved to our servers.
                        </p>
                    </div>
                    <button type="button" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 rounded-lg text-xs transition shadow-sm flex items-center justify-center space-x-2 mt-4">
                        <span>Connect</span>
                    </button>
                </div>
"""

# Insert it at the top of the tab-register
pattern = r'(<div id="tab-register" class="p-6 overflow-y-auto flex-1 hidden">)'
new_content = re.sub(pattern, r'\1' + html_to_inject, content)

if content != new_content:
    with open(html_path, 'w') as f:
        f.write(new_content)
    print("Injected into Webhook tab.")
else:
    print("Could not find insertion point.")
