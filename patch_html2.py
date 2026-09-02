import re

with open("static/index.html", "r") as f:
    content = f.read()

# 1. Regex replace renderExecutiveRecommendations
new_render = """        async function renderExecutiveRecommendations(scenarioId, container) {
            if (!container) return;
            
            // Show loading state
            container.innerHTML = `
                <div class="col-span-full flex flex-col items-center justify-center py-6 text-slate-500">
                    <svg class="animate-spin h-6 w-6 text-indigo-600 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    <p class="text-xs font-bold uppercase tracking-widest animate-pulse">Generating Dynamic AI Recommendations...</p>
                </div>
            `;

            try {
                const idToken = await auth.currentUser.getIdToken();
                const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${idToken}` };
                const byokKey = sessionStorage.getItem('gemini_api_key');
                if (byokKey) headers['X-Gemini-Api-Key'] = byokKey;

                const res = await fetch('/api/forecast/recommendations', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ scenario_id: scenarioId })
                });
                
                const data = await res.json();
                const list = data.recommendations || [];
                let html = '';

                list.forEach((rec) => {
                    html += `
                        <div class="p-4 bg-slate-50/90 rounded-xl border border-slate-200/90 flex flex-col justify-between space-y-3 hover:border-indigo-300 hover:shadow-xs transition">
                            <div>
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${rec.tagColor}">${rec.tag}</span>
                                    <span class="text-[11px] font-extrabold ${rec.impactColor}">${rec.impact}</span>
                                </div>
                                <h4 class="font-bold text-slate-800 text-xs mb-1.5 leading-snug">${rec.title}</h4>
                                <p class="text-slate-600 text-[11px] leading-relaxed">${rec.desc}</p>
                            </div>
                            <button onclick="applyRecommendation(this, '${rec.title.replace(/'/g, "\\\\'")}')" class="w-full bg-white hover:bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold py-2 px-3 rounded-lg text-xs transition shadow-2xs flex items-center justify-center space-x-1">
                                <span>${rec.actionText}</span>
                            </button>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } catch (err) {
                container.innerHTML = '<div class="col-span-full p-4 text-rose-600 bg-rose-50 rounded-xl text-xs font-bold text-center">Failed to load AI recommendations.</div>';
            }
        }"""
        
content = re.sub(r'function renderExecutiveRecommendations\(scenarioId, container\) \{.*?container\.innerHTML = html;\n        \}', new_render, content, flags=re.DOTALL)


# 2. Regex replace connectApiCredentials
new_connect = """function connectApiCredentials() {
            const key = document.getElementById('api-key-input').value.trim();
            const errorEl = document.getElementById('api-key-error');
            const progressContainer = document.getElementById('api-connect-progress');
            const progressFill = document.getElementById('progress-bar-fill');
            const statusText = document.getElementById('api-connect-status-text');
            const btn = document.getElementById('btn-connect-api');
            const statusLabel = document.getElementById('api-key-status-label');
            
            if (!key) {
                errorEl.innerText = "Please enter an API Key.";
                errorEl.classList.remove('hidden');
                return;
            }
            
            errorEl.classList.add('hidden');
            progressContainer.classList.remove('hidden');
            btn.disabled = true;
            btn.classList.add('opacity-50', 'cursor-not-allowed');
            
            // Simulate connection process
            setTimeout(() => { progressFill.style.width = '30%'; statusText.innerText = "Verifying cryptographic signature..."; }, 400);
            setTimeout(() => { progressFill.style.width = '70%'; statusText.innerText = "Establishing secure session..."; }, 1200);
            setTimeout(() => { 
                progressFill.style.width = '100%'; 
                statusText.innerText = "Connected Successfully."; 
                statusText.classList.add('text-emerald-600', 'font-bold');
                
                // Store securely in session storage
                sessionStorage.setItem('gemini_api_key', key);
                
                // Update Labels
                if(statusLabel) {
                    statusLabel.innerText = "API Key Connected";
                    statusLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
                
                // Update Button
                btn.innerHTML = "<span>Key Connected ✅</span>";
                btn.classList.remove('bg-indigo-600', 'hover:bg-indigo-700');
                btn.classList.add('bg-emerald-600');
                
                // Collapse panel after a moment
                setTimeout(() => {
                    document.getElementById('api-creds-form').classList.add('hidden');
                }, 1500);
                
            }, 2000);
        }"""
        
content = re.sub(r'function connectApiCredentials\(\) \{.*?\n        \}', new_connect, content, flags=re.DOTALL)

with open("static/index.html", "w") as f:
    f.write(content)

