import re

with open("static/index.html", "r") as f:
    content = f.read()

# Replace renderExecutiveRecommendations
old_render = """        function renderExecutiveRecommendations(scenarioId, container) {
            if (!container) return;

            const recommendations = {
                'saas_finops': [
                    {
                        tag: 'FinOps Policy',
                        tagColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
                        title: 'Automate Okta SCIM Role Reclassification',
                        desc: 'Reclassify 130 Figma Enterprise seats with >60d inactivity to Viewer-Restricted without disrupting file access.',
                        impact: '+$56,400 / yr Recovered',
                        impactColor: 'text-emerald-600',
                        actionText: '⚡ Apply SCIM Policy'
                    },
                    {
                        tag: 'Workflow Automation',
                        tagColor: 'bg-indigo-50 text-indigo-700 border-indigo-200',
                        title: 'Enforce 45-Day Inactivity Auto-Reclaim Rule',
                        desc: 'Deploy an automated Sentinel lifecycle policy to prevent seat bloat by reclaiming licenses before upcoming Q3 renewals.',
                        impact: 'Zero License Bloat',
                        impactColor: 'text-indigo-600',
                        actionText: '⚡ Deploy Auto-Rule'
                    },
                    {
                        tag: 'Procurement Strategy',
                        tagColor: 'bg-purple-50 text-purple-700 border-purple-200',
                        title: 'Pre-Negotiate Enterprise Tier True-Down',
                        desc: 'Export verified usage telemetry to Figma procurement to lock in tier volume discounts ahead of contract renewal.',
                        impact: '15% Extra Savings',
                        impactColor: 'text-purple-600',
                        actionText: '⚡ Generate Audit Deck'
                    }
                ],
                'hardware_lifecycle': [
                    {
                        tag: 'Safety & Risk',
                        tagColor: 'bg-rose-50 text-rose-700 border-rose-200',
                        title: 'Quarantine 18 Swollen Battery Units',
                        desc: 'Lock and recall MacBook Pro 16" units exhibiting >800 cycle counts and thermal inflation patterns via Jamf MDM.',
                        impact: 'Critical Safety Mitigation',
                        impactColor: 'text-rose-600',
                        actionText: '⚡ Initiate Quarantine'
                    },
                    {
                        tag: 'Depot Logistics',
                        tagColor: 'bg-amber-50 text-amber-700 border-amber-200',
                        title: 'Batch Dispatch AppleCare+ Replacements',
                        desc: 'Auto-create vendor depot exchange tickets in Jira Service Management for fast 48-hour hardware turnaround.',
                        impact: 'Save $40,500 CapEx',
                        impactColor: 'text-amber-600',
                        actionText: '⚡ Batch Dispatch RMA'
                    },
                    {
                        tag: 'CapEx Planning',
                        tagColor: 'bg-indigo-50 text-indigo-700 border-indigo-200',
                        title: 'Align Q3 CapEx Refresh Forecast Model',
                        desc: 'Project replacement timelines for 32 aging laptops approaching warranty expiration in the next 90 days.',
                        impact: '100% Fleet Compliance',
                        impactColor: 'text-indigo-600',
                        actionText: '⚡ Export CapEx Model'
                    }
                ],
                'itsm_surge': [
                    {
                        tag: 'Staffing Optimization',
                        tagColor: 'bg-indigo-50 text-indigo-700 border-indigo-200',
                        title: 'Pre-Stage Tier-2 Identity Engineers',
                        desc: 'Shift 2 specialized IAM engineers to the 08:00–14:00 window to absorb the 42% Month-End close ticket surge.',
                        impact: 'Zero SLA Breaches',
                        impactColor: 'text-indigo-600',
                        actionText: '⚡ Shift Scheduling'
                    },
                    {
                        tag: 'SOX Self-Service',
                        tagColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
                        title: 'Deploy Fast-Track Slack Dual-Approval',
                        desc: 'Enable automated manager approval via Slack Block Kit for time-critical General Ledger access resets.',
                        impact: '-65% Resolution Time',
                        impactColor: 'text-emerald-600',
                        actionText: '⚡ Enable Fast-Track'
                    },
                    {
                        tag: 'Root Cause Mitigation',
                        tagColor: 'bg-purple-50 text-purple-700 border-purple-200',
                        title: 'Extend ERP SSO Session Expiry Thresholds',
                        desc: 'Temporarily lengthen session tokens during Month-End Close to prevent mass concurrent session disconnects.',
                        impact: '300+ Tickets Prevented',
                        impactColor: 'text-purple-600',
                        actionText: '⚡ Update SSO Policy'
                    }
                ]
            };

            const list = recommendations[scenarioId] || recommendations['saas_finops'];
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
                        <button onclick="applyRecommendation(this, '${rec.title.replace(/'/g, "\\'")}')" class="w-full bg-white hover:bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold py-2 px-3 rounded-lg text-xs transition shadow-2xs flex items-center justify-center space-x-1">
                            <span>${rec.actionText}</span>
                        </button>
                    </div>
                `;
            });

            container.innerHTML = html;
        }"""

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

if old_render in content:
    content = content.replace(old_render, new_render)
    print("Replaced renderExecutiveRecommendations")
else:
    print("Could not find old_render snippet")

# Now let's fix connectApiCredentials and add label updating logic
# Looking for `function connectApiCredentials()`
old_connect = """        function connectApiCredentials() {
            const key = document.getElementById('api-key-input').value.trim();
            const errorEl = document.getElementById('api-key-error');
            const progressContainer = document.getElementById('api-connect-progress');
            const progressFill = document.getElementById('progress-bar-fill');
            const statusText = document.getElementById('api-connect-status-text');
            const btn = document.getElementById('btn-connect-api');
            
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
        
new_connect = """        function connectApiCredentials() {
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
        }
        
        // On Load, check if key is already connected and update label
        document.addEventListener('DOMContentLoaded', () => {
            if(sessionStorage.getItem('gemini_api_key')) {
                const statusLabel = document.getElementById('api-key-status-label');
                if(statusLabel) {
                    statusLabel.innerText = "API Key Connected";
                    statusLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
            }
        });"""

if old_connect in content:
    content = content.replace(old_connect, new_connect)
    print("Replaced connectApiCredentials")
else:
    print("Could not find old_connect snippet")

with open("static/index.html", "w") as f:
    f.write(content)

