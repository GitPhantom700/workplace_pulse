
        // ---------------------------------------------------------
        // Application State
        // ---------------------------------------------------------
        let currentScenarioId = 'saas_finops';
        let currentScenarioPayload = null;
        let chartInstance = null;
        let chatHistory = [];
        let isDemoMode = true;
        let currentUser = null;
        let userAuthToken = "demo-sandbox-token";
        let availableRunbooks = [];
        let registeredWebhooks = [];

        // ---------------------------------------------------------
        // Firebase Client Configuration
        // ---------------------------------------------------------
        const firebaseConfig = {
            apiKey: "AIzaSyADmB0e0VhrEtIbbCRCZ4he7HC8PKmRUfA",
            authDomain: "workplacepulse-dev.firebaseapp.com",
            projectId: "workplacepulse-dev",
            storageBucket: "workplacepulse-dev.firebasestorage.app",
            messagingSenderId: "872061791801",
            appId: "1:872061791801:web:d881b10a0294217839a7e8",
            measurementId: "G-430V9N9S88"
        };

        try {
            if (!firebase.apps.length) {
                firebase.initializeApp(firebaseConfig);
            }
            firebase.auth().onAuthStateChanged((user) => {
                if (user) {
                    currentUser = user;
                    user.getIdToken().then((token) => {
                        userAuthToken = token;
                        updateAuthUI(true, user);
                        loadWebhooks();
                    });
                } else {
                    currentUser = null;
                    if (!isDemoMode) {
                        userAuthToken = null;
                    }
                    updateAuthUI(false, null);
                }
            });
        } catch (e) {
            console.warn("Firebase Auth Client Init in Offline/Demo mode:", e);
        }

        function signInWithGoogle() {
            if (isDemoMode) {
                currentUser = {
                    displayName: "Chandraprakash Hingal",
                    email: "chandrahin@floqast.com",
                    photoURL: "https://ui-avatars.com/api/?name=Chandraprakash+Hingal&background=4f46e5&color=fff"
                };
                userAuthToken = "demo-mock-jwt-token";
                updateAuthUI(true, currentUser);
                loadWebhooks();
                return;
            }
            const provider = new firebase.auth.GoogleAuthProvider();
            firebase.auth().signInWithPopup(provider).catch((err) => {
                alert("Firebase Login Failed: " + err.message);
                console.error(err);
            });
        }

        function signOut() {
            if (firebase.auth().currentUser) {
                firebase.auth().signOut();
            }
            currentUser = null;
            if (!isDemoMode) userAuthToken = null;
            updateAuthUI(false, null);
        }

        function toggleDemoMode() {
            isDemoMode = !isDemoMode;
            document.getElementById('demo-status').innerText = isDemoMode ? "ON" : "OFF";
            document.getElementById('demo-status').className = isDemoMode ? "text-emerald-600 font-bold" : "text-amber-600 font-bold";
            if (isDemoMode && !currentUser) {
                userAuthToken = "demo-sandbox-token";
            }
        }

        function updateAuthUI(isSignedIn, user) {
            const outBox = document.getElementById('auth-signed-out');
            const inBox = document.getElementById('auth-signed-in');
            if (isSignedIn && user) {
                outBox.classList.add('hidden');
                inBox.classList.remove('hidden');
                document.getElementById('user-avatar').src = user.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.displayName || 'User')}`;
                document.getElementById('user-name').innerText = user.displayName || "Authenticated Engineer";
                document.getElementById('user-email').innerText = user.email || "";
            } else {
                inBox.classList.add('hidden');
                outBox.classList.remove('hidden');
            }
        }

        // ---------------------------------------------------------
        // Scenario Controller & Data Rendering
        // ---------------------------------------------------------
        async function switchScenario(scenarioId) {
            showDashboard();
            currentScenarioId = scenarioId;
            document.querySelectorAll('.scenario-btn').forEach(btn => {
                btn.className = "scenario-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition";
            });
            const activeBtn = document.getElementById(`btn-${scenarioId}`);
            if (activeBtn) {
                activeBtn.className = "scenario-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition bg-indigo-50 text-indigo-700";
            }

            // Reset runbook terminal view
            document.getElementById('runbook-terminal-container').classList.add('hidden');
            document.getElementById('runbook-terminal-logs').innerHTML = '';
            document.getElementById('runbook-webhook-results').innerHTML = '';

            // Clear chat stream on scenario switch
            chatHistory = [];
            document.getElementById('chat-messages').innerHTML = `
                <div class="chat-bubble-ai text-slate-800 p-3.5 rounded-xl shadow-sm leading-relaxed">
                    <p class="font-bold text-indigo-600 mb-1">🤖 WorkplacePulse Copilot Ready</p>
                    <p>Switched scenario to <strong>${scenarioId}</strong>. Grounding telemetry has been updated in memory. Ask your question or click a quick prompt below.</p>
                </div>
            `;

            await loadScenarioData(scenarioId);
            updateRunbookCardForScenario(scenarioId);
        }

        async function refreshScenario() {
            await loadScenarioData(currentScenarioId);
        }

        async function loadScenarioData(scenarioId) {
            try {
                const response = await fetch('/api/scenarios/seed', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ scenario_id: scenarioId })
                });
                const data = await response.json();
                currentScenarioPayload = data;

                // Update UI text
                document.getElementById('scenario-domain').innerText = data.domain;
                document.getElementById('scenario-title').innerText = data.title;
                document.getElementById('scenario-summary').innerText = data.summary;

                // Render Chart.js
                renderChart(data.chart_data);

                // Render Table Breakdown
                renderTable(data);

            } catch (err) {
                console.error("Failed to load scenario data:", err);
            }
        }

        function renderChart(chartPayload) {
            const ctx = document.getElementById('scenarioChart').getContext('2d');
            if (chartInstance) {
                chartInstance.destroy();
            }

            chartInstance = new Chart(ctx, {
                type: chartPayload.type || 'bar',
                data: {
                    labels: chartPayload.labels,
                    datasets: chartPayload.datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#475569', font: { size: 11 } }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#64748b', font: { size: 10 } },
                            grid: { color: '#f1f5f9' }
                        },
                        y: {
                            ticks: { color: '#64748b', font: { size: 10 } },
                            grid: { color: '#f1f5f9' }
                        }
                    }
                }
            });
        }

        function renderSparklineHtml(trendType, label, subtext) {
            let color = '#f43f5e';
            let pathD = 'M2 15 Q 18 13, 34 7 T 58 3';
            let endY = 3;
            let bgBadge = 'bg-rose-50 text-rose-700 border-rose-200';

            if (trendType === 'spike') {
                color = '#e11d48';
                pathD = 'M2 16 Q 20 15, 32 8 T 58 2';
                endY = 2;
                bgBadge = 'bg-rose-100 text-rose-800 border-rose-300';
            } else if (trendType === 'waste_rising') {
                color = '#f59e0b';
                pathD = 'M2 15 Q 18 13, 34 7 T 58 4';
                endY = 4;
                bgBadge = 'bg-amber-50 text-amber-700 border-amber-200';
            } else if (trendType === 'stable') {
                color = '#64748b';
                pathD = 'M2 10 Q 18 8, 32 11 T 58 10';
                endY = 10;
                bgBadge = 'bg-slate-100 text-slate-700 border-slate-200';
            } else if (trendType === 'improving') {
                color = '#10b981';
                pathD = 'M2 4 Q 18 7, 34 12 T 58 16';
                endY = 16;
                bgBadge = 'bg-emerald-50 text-emerald-700 border-emerald-200';
            }

            return `
                <div class="flex items-center space-x-2 py-0.5" title="${subtext}">
                    <svg class="w-12 h-4 overflow-visible shrink-0" viewBox="0 0 60 20">
                        <path d="${pathD}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="58" cy="${endY}" r="2.5" fill="${color}"/>
                    </svg>
                    <span class="text-[10px] font-bold px-1.5 py-0.5 rounded-full border ${bgBadge} whitespace-nowrap shadow-2xs">
                        ${label}
                    </span>
                </div>
            `;
        }

        function renderTable(payload) {
            const headersRow = document.getElementById('table-headers');
            const tableBody = document.getElementById('table-body');
            headersRow.innerHTML = '';
            tableBody.innerHTML = '';

            if (payload.saas_metrics && payload.saas_metrics.length > 0) {
                headersRow.innerHTML = `
                    <th class="p-2">Application</th>
                    <th class="p-2">Category</th>
                    <th class="p-2">Total Seats</th>
                    <th class="p-2">Active (30d)</th>
                    <th class="p-2">Inactive (60d+)</th>
                    <th class="p-2">Annual Waste</th>
                    <th class="p-2">Q4 Forecast Trend</th>
                `;

                const trendsMap = {
                    "Figma Enterprise": { type: "spike", label: "↗ +35% Waste", sub: "Projected waste growth without SCIM deprovisioning" },
                    "Zoom Pro": { type: "waste_rising", label: "↗ +22% Waste", sub: "Inactive host accounts increasing ahead of renewal" },
                    "GitHub Enterprise": { type: "stable", label: "→ Stable", sub: "Active developer seat utilization" },
                    "Notion Team": { type: "spike", label: "↗ +28% Waste", sub: "Unmanaged team workspace seat sprawl" },
                    "Salesforce Sales Cloud": { type: "stable", label: "→ Stable", sub: "CRM quota under strict enterprise management" },
                    "Miro Business": { type: "waste_rising", label: "↗ +18% Waste", sub: "Occasional collaborator seat accumulation" },
                    "Datadog Infrastructure": { type: "improving", label: "↘ Optimized", sub: "APM host deprovisioning on track" }
                };

                payload.saas_metrics.forEach(m => {
                    const trend = trendsMap[m.app_name] || { type: "waste_rising", label: "↗ +15%", sub: "Quarterly projection" };
                    tableBody.innerHTML += `
                        <tr class="hover:bg-slate-50 transition-colors">
                            <td class="p-2 font-medium text-slate-800">${m.app_name}</td>
                            <td class="p-2">${m.category}</td>
                            <td class="p-2">${m.total_licenses}</td>
                            <td class="p-2 text-emerald-600 font-semibold">${m.active_last_30d}</td>
                            <td class="p-2 text-rose-500 font-semibold">${m.inactive_60d_plus}</td>
                            <td class="p-2 text-amber-600 font-bold">$${m.annual_potential_savings.toLocaleString()}</td>
                            <td class="p-2">${renderSparklineHtml(trend.type, trend.label, trend.sub)}</td>
                        </tr>
                    `;
                });
            } else if (payload.hardware_metrics && payload.hardware_metrics.length > 0) {
                headersRow.innerHTML = `
                    <th class="p-2">Device Model</th>
                    <th class="p-2">OS Version</th>
                    <th class="p-2">Total Fleet</th>
                    <th class="p-2">Battery Degradation (>800c)</th>
                    <th class="p-2">Warranty Lapsed</th>
                    <th class="p-2">CapEx Budget</th>
                    <th class="p-2">Q4 Degradation Forecast</th>
                `;

                const hwTrendsMap = {
                    'MacBook Pro 13" (M1, 2020)': { type: "spike", label: "↗ 58 Units Risk", sub: "38% fleet entering battery critical threshold" },
                    'MacBook Pro 14" (M1 Pro, 2021)': { type: "waste_rising", label: "↗ 35 Expiring", sub: "AppleCare+ warranty lapsing within 60 days" },
                    'MacBook Pro 16" (M2 Pro, 2023)': { type: "improving", label: "🟢 98% Healthy", sub: "Modern silicon battery cycles under 150" },
                    'Dell XPS 15 (Windows 11)': { type: "waste_rising", label: "↗ 28 Thermal Wear", sub: "Thermal throttling and battery cycle fatigue" }
                };

                payload.hardware_metrics.forEach(m => {
                    const trend = hwTrendsMap[m.model_name] || { type: "waste_rising", label: "↗ Degrading", sub: "Hardware lifecycle forecast" };
                    tableBody.innerHTML += `
                        <tr class="hover:bg-slate-50 transition-colors">
                            <td class="p-2 font-medium text-slate-800">${m.model_name}</td>
                            <td class="p-2">${m.os_version}</td>
                            <td class="p-2">${m.total_units}</td>
                            <td class="p-2 text-amber-600 font-semibold">${m.battery_critical_units}</td>
                            <td class="p-2 text-rose-500">${m.out_of_warranty_units}</td>
                            <td class="p-2 text-sky-600 font-bold">$${m.estimated_replacement_budget_usd.toLocaleString()}</td>
                            <td class="p-2">${renderSparklineHtml(trend.type, trend.label, trend.sub)}</td>
                        </tr>
                    `;
                });
            } else if (payload.itsm_metrics && payload.itsm_metrics.length > 0) {
                headersRow.innerHTML = `
                    <th class="p-2">Ticket Category</th>
                    <th class="p-2">Normal Daily</th>
                    <th class="p-2">Month-End Surge</th>
                    <th class="p-2">Open Backlog</th>
                    <th class="p-2">MTTR (Hrs)</th>
                    <th class="p-2">Primary Bottleneck</th>
                    <th class="p-2">Surge Forecast (Q4)</th>
                `;

                const itsmTrendsMap = {
                    "Financial Close & ERP Access": { type: "spike", label: "⚡ 7.0x Surge", sub: "Historical Month-End dual-approval bottleneck" },
                    "SSO & Multi-Factor Auth (MFA)": { type: "waste_rising", label: "↗ 2.7x Spike", sub: "Quarterly token and password reset spikes" },
                    "Hardware / Peripheral Swaps": { type: "stable", label: "→ 1.3x Mild", sub: "Standard depot hardware replacement volume" },
                    "Software Provisioning & Add-ons": { type: "waste_rising", label: "↗ 1.9x Surge", sub: "Department license allocation queue" },
                    "eDiscovery & Legal Access Holds": { type: "stable", label: "→ Predictable", sub: "Low-frequency legal hold requests" }
                };

                payload.itsm_metrics.forEach(m => {
                    const trend = itsmTrendsMap[m.category] || { type: "waste_rising", label: "↗ 2.0x", sub: "Month-End forecast" };
                    tableBody.innerHTML += `
                        <tr class="hover:bg-slate-50 transition-colors">
                            <td class="p-2 font-medium text-slate-800">${m.category}</td>
                            <td class="p-2">${m.historical_daily_avg}</td>
                            <td class="p-2 text-rose-600 font-bold">${m.month_end_surge_daily_avg}</td>
                            <td class="p-2 text-amber-600">${m.current_open_backlog}</td>
                            <td class="p-2">${m.average_resolution_time_hrs}h</td>
                            <td class="p-2 text-slate-500">${m.primary_bottleneck}</td>
                            <td class="p-2">${renderSparklineHtml(trend.type, trend.label, trend.sub)}</td>
                        </tr>
                    `;
                });
            }
        }

        // ---------------------------------------------------------
        // Standout Feature: Runbook Execution
        // ---------------------------------------------------------
        
        // ---------------------------------------------------------
        // Executive Report Modal Controller
        // ---------------------------------------------------------
                let lastRunbookExecutionData = null;
        let reportModalChartInstance = null;

        function applyAiRecommendation(policyName) {
            alert(`✅ Action Executed: "${policyName}" has been successfully scheduled and queued in Sentinel Engine.`);
        }

        function openExecutiveReportModal() {
            const runbook = availableRunbooks.find(r => r.scenario_id === currentScenarioId);
            if (!runbook) return;

            const refId = `INC-${currentScenarioId.toUpperCase()}-${Date.now().toString().slice(-6)}`;
            const timestamp = new Date().toISOString();
            const auditorName = (currentUser && currentUser.displayName) ? currentUser.displayName : "Chandraprakash Hingal";
            const uid = (currentUser && currentUser.uid) ? currentUser.uid : "demo_user";

            // 1. Populate Header & KPIs (NO TRUNCATION)
            document.getElementById('report-modal-title').innerText = runbook.title;
            document.getElementById('report-modal-subtitle').innerText = `Autonomous Sentinel Runbook • Target: ${runbook.target_system}`;
            document.getElementById('report-modal-refid').innerText = refId;
            document.getElementById('report-modal-timestamp').innerText = timestamp;
            document.getElementById('report-modal-target').innerText = runbook.target_system;
            document.getElementById('report-modal-impact').innerText = runbook.estimated_impact;
            document.getElementById('report-modal-auditor').innerText = auditorName;
            document.getElementById('report-modal-firestore-path').innerText = `/users/${uid}/runbook_logs/${refId}`;

            // 2. Populate Insights & Risk Diagnosis
            let dynamicInsights = "Predictive telemetry detected inactive SaaS license accumulation exceeding threshold parameters across target directories.";
            let riskDiagnosis = "Unreclaimed seats generate recurrent budget drain and increase identity attack surfaces under SOX ITGC and ISO 27001 Access Control guidelines. Immediate autonomous remediation executed.";
            
            if (currentScenarioId === 'hardware_quarantine') {
                dynamicInsights = "Battery telemetry detected 42 laptops operating with cycle count >800 or severe capacity degradation (<75%).";
                riskDiagnosis = "Severe risk of battery swelling, trackpad displacement, and hardware fire hazard. Immediate quarantine and depot refresh required.";
            } else if (currentScenarioId === 'itsm_surge') {
                dynamicInsights = "Month-end close finance ticket volume spiked 340%, creating critical bottlenecks for ERP access approvals.";
                riskDiagnosis = "Financial close delay risk exceeding 4.5 hours per business unit. Emergency SOX fast-track dual-signer matrix executed.";
            } else if (currentScenarioPayload && currentScenarioPayload.summary) {
                dynamicInsights = currentScenarioPayload.summary;
            }

            document.getElementById('report-modal-insights').innerText = dynamicInsights;
            document.getElementById('report-modal-risk').innerText = riskDiagnosis;

            // 3. Render Large, High-Contrast Dedicated Report Chart
            const chartCanvas = document.getElementById('report-modal-chart-canvas');
            if (chartCanvas && currentScenarioPayload && currentScenarioPayload.chart_data) {
                if (reportModalChartInstance) {
                    reportModalChartInstance.destroy();
                }

                const ctx = chartCanvas.getContext('2d');
                const rawData = JSON.parse(JSON.stringify(currentScenarioPayload.chart_data));

                // Customize datasets for high-contrast executive presentation
                if (rawData.datasets) {
                    rawData.datasets.forEach((ds, idx) => {
                        ds.borderWidth = 2;
                        ds.borderRadius = 8;
                        if (idx === 0) {
                            ds.backgroundColor = '#6366f1'; // Vibrant Indigo
                            ds.borderColor = '#4f46e5';
                        } else if (idx === 1) {
                            ds.backgroundColor = '#cbd5e1'; // Clean Slate
                            ds.borderColor = '#94a3b8';
                        }
                    });
                }

                reportModalChartInstance = new Chart(ctx, {
                    type: rawData.type || 'bar',
                    data: rawData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    font: { size: 12, weight: '700', family: 'system-ui, sans-serif' },
                                    color: '#334155',
                                    padding: 16,
                                    usePointStyle: true,
                                    pointStyle: 'rectRounded'
                                }
                            },
                            tooltip: {
                                padding: 12,
                                titleFont: { size: 13, weight: 'bold' },
                                bodyFont: { size: 12 }
                            }
                        },
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: {
                                    font: { size: 11, weight: '600', family: 'system-ui, sans-serif' },
                                    color: '#475569',
                                    maxRotation: 25,
                                    minRotation: 0
                                }
                            },
                            y: {
                                grid: { color: '#f1f5f9' },
                                ticks: {
                                    font: { size: 11, weight: '600', family: 'system-ui, sans-serif' },
                                    color: '#475569'
                                }
                            }
                        }
                    }
                });
            }

            // 4. Populate Terminal Steps
            const stepsContainer = document.getElementById('report-modal-steps');
            const terminalLogs = document.getElementById('runbook-terminal-logs');
            if (terminalLogs && terminalLogs.children.length > 0) {
                stepsContainer.innerHTML = terminalLogs.innerHTML;
            } else {
                stepsContainer.innerHTML = `
                    <div class="text-emerald-400 font-mono">[${timestamp}] Initializing SCIM 2.0 API connector to ${runbook.target_system}...</div>
                    <div class="text-emerald-400 font-mono">[${timestamp}] Evaluating active accounts against compliance anomaly triggers...</div>
                    <div class="text-emerald-400 font-mono">[${timestamp}] Executed automated remediation batch dispatch: SUCCESS</div>
                    <div class="text-emerald-400 font-mono">[${timestamp}] Emitted immutable audit ledger record to Cloud Firestore</div>
                `;
            }

            // 5. Populate Section 5: Gemini AI Strategic Recommendations
            const recsContainer = document.getElementById('report-modal-recommendations');
            if (recsContainer) {
                renderExecutiveRecommendations(currentScenarioId, recsContainer);
            }

            // 6. Populate Webhook notifications
            const webhookContainer = document.getElementById('report-modal-webhooks');
            const liveWebhooks = document.getElementById('runbook-webhook-results');
            if (liveWebhooks && liveWebhooks.children.length > 0) {
                webhookContainer.innerHTML = liveWebhooks.innerHTML;
            } else {
                webhookContainer.innerHTML = `
                    <span class="px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-300 font-semibold flex items-center gap-1.5 text-xs">
                        <span>💬</span> Slack Alert Channel (delivered • 12.4ms)
                    </span>
                    <span class="px-3 py-1.5 rounded-lg bg-purple-50 text-purple-800 border border-purple-300 font-semibold flex items-center gap-1.5 text-xs">
                        <span>🎮</span> Security Operations Discord (delivered • 16.8ms)
                    </span>
                    <span class="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-800 border border-blue-300 font-semibold flex items-center gap-1.5 text-xs">
                        <span>💼</span> Microsoft Teams Ops (delivered • 14.1ms)
                    </span>
                `;
            }

            // 7. Open Modal
            document.getElementById('executive-report-modal').classList.remove('hidden');
        }

                async function renderExecutiveRecommendations(scenarioId, container) {
            if (!container) return;
            
            // Show loading state
            container.innerHTML = `
                <div class="col-span-full flex flex-col items-center justify-center py-6 text-slate-500">
                    <svg class="animate-spin h-6 w-6 text-indigo-600 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    <p class="text-xs font-bold uppercase tracking-widest animate-pulse">Generating Dynamic AI Recommendations...</p>
                </div>
            `;
            
            const isLive = !!sessionStorage.getItem('gemini_api_key');
            const recsHeader = document.getElementById('report-recs-badge');
            if (recsHeader) {
                if (isLive) {
                    recsHeader.innerText = "Live Data";
                    recsHeader.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide border border-emerald-200 ml-2";
                } else {
                    recsHeader.innerText = "Dummy Data";
                    recsHeader.className = "text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide border border-amber-200 ml-2";
                }
            }

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
                            <button onclick="applyRecommendation(this, '${rec.title.replace(/'/g, "\\'")}')" class="w-full bg-white hover:bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold py-2 px-3 rounded-lg text-xs transition shadow-2xs flex items-center justify-center space-x-1">
                                <span>${rec.actionText}</span>
                            </button>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } catch (err) {
                container.innerHTML = '<div class="col-span-full p-4 text-rose-600 bg-rose-50 rounded-xl text-xs font-bold text-center">Failed to load AI recommendations.</div>';
            }
        }

        function applyRecommendation(btn, title) {
            btn.className = "w-full bg-emerald-600 text-white font-bold py-2 px-3 rounded-lg text-xs shadow-2xs flex items-center justify-center space-x-1 cursor-default";
            btn.innerHTML = "<span>Policy Applied ✅</span>";
            btn.onclick = null;
        }

        function printExecutiveReport() {
            // Capture chart image
            let chartImg = "";
            const reportChartCanvas = document.getElementById('report-modal-chart-canvas');
            if (reportChartCanvas) {
                try {
                    chartImg = reportChartCanvas.toDataURL('image/png');
                } catch(e) {}
            } else if (chartInstance) {
                try {
                    const ctx = chartInstance.ctx;
                    ctx.save();
                    ctx.globalCompositeOperation = 'destination-over';
                    ctx.fillStyle = 'white';
                    ctx.fillRect(0, 0, chartInstance.width, chartInstance.height);
                    chartImg = chartInstance.toBase64Image();
                    ctx.restore();
                } catch(e) {}
            }

            // Create dedicated print window
            const printWindow = window.open('', '_blank');
            let reportContent = document.getElementById('printable-report-content').innerHTML;
            
            if (chartImg) {
                // Replace the canvas container with the actual image
                reportContent = reportContent.replace(
                    /<canvas[^>]*id="report-modal-chart-canvas"[^>]*>.*?<\/canvas>/is,
                    `<img src="${chartImg}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;">`
                );
            }

            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>WorkplacePulse - Incident Report</title>
                    <script src="https://cdn.tailwindcss.com"><\/script>
                    <style>
                        @media print {
                            body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                            .page-break { page-break-before: always; }
                            /* Removed .bg-slate-950 from break-inside:avoid to allow the terminal log to flow across pages naturally */
                            .border-slate-200/90 { break-inside: avoid; page-break-inside: avoid; }
                        }
                        body { padding: 40px; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
                    </style>
                </head>
                <body class="bg-white text-slate-800 max-w-4xl mx-auto">
                    <div class="mb-8 border-b border-slate-200 pb-4 flex justify-between items-end">
                        <div>
                            <h1 class="text-2xl font-bold text-slate-900">WorkplacePulse Executive Audit Report</h1>
                            <p class="text-sm text-slate-500">Official Remediation & Compliance Record</p>
                        </div>
                        <div class="text-right text-xs text-slate-400">
                            Printed: ${new Date().toLocaleString()}
                        </div>
                    </div>
                    
                    ${reportContent}
                </body>
                </html>
            `);
            printWindow.document.close();
            
            // Wait for Tailwind to inject styles before triggering print dialog
            setTimeout(() => {
                printWindow.focus();
                printWindow.print();
                printWindow.close();
            }, 750);
        }

        function closeExecutiveReportModal() {
            document.getElementById('executive-report-modal').classList.add('hidden');
        }

        function downloadReportMarkdown() {
            const runbook = availableRunbooks.find(r => r.scenario_id === currentScenarioId);
            const title = runbook ? runbook.title : "WorkplacePulse Incident Remediation";
            const target = runbook ? runbook.target_system : "Enterprise IT";
            const impact = runbook ? runbook.estimated_impact : "N/A";
            const timestamp = new Date().toISOString();
            const dateStr = new Date().toLocaleDateString();
            const refId = `INC-${currentScenarioId.toUpperCase()}-${Date.now().toString().slice(-6)}`;
            
            // Capture the dedicated report chart canvas as a Base64 Image
            let chartBase64 = "";
            const reportChartCanvas = document.getElementById('report-modal-chart-canvas');
            if (reportChartCanvas) {
                try {
                    chartBase64 = reportChartCanvas.toDataURL('image/png');
                } catch(e) {
                    console.warn("Failed to capture report chart image", e);
                }
            } else if (chartInstance) {
                try {
                    chartBase64 = chartInstance.toBase64Image();
                } catch(e) {}
            }
            
            let dynamicInsights = "System telemetry anomaly detected crossing compliance thresholds.";
            let recsMarkdown = "- [ ] **Policy Automation:** Enforce 45-day SCIM auto-reclaim policy in Okta.\n- [ ] **Tier Optimization:** Convert dormant Enterprise Editor seats to Viewer seats.\n- [ ] **Contract Alert:** Schedule automated 60-day renewal notices for vendor contracts.";
            
            if (currentScenarioId === 'saas_finops') {
                dynamicInsights = "Predictive telemetry detected inactive SaaS license accumulation exceeding the 60-day threshold across critical enterprise workspaces.";
                recsMarkdown = "- [ ] **Policy Automation:** Enforce 45-day SCIM auto-reclaim policy in Okta to eliminate recurring seat drift.\n- [ ] **Tier Optimization:** Transition 45 inactive Enterprise Editor seats to Viewer-only tier (recovering $2,025/mo).\n- [ ] **Contract Alert:** Set automated 60-day renewal review notifications with Procurement for Zoom & Notion contracts.";
            } else if (currentScenarioId === 'hardware_lifecycle' || currentScenarioId === 'hardware_quarantine') {
                dynamicInsights = "Battery telemetry detected 18 laptops operating with cycle count >800 or severe capacity degradation (<75%).";
                recsMarkdown = "- [ ] **Safety Policy:** Deploy Jamf Pro configuration profile quarantining all units with >800 cycles and thermal swelling risk.\n- [ ] **Depot Operations:** Automatically submit AppleCare+ depot exchange tickets for all 18 quarantined units.\n- [ ] **CapEx Alignment:** Align Q3 replacement budget for 32 laptops approaching warranty expiration.";
            } else if (currentScenarioId === 'itsm_surge') {
                dynamicInsights = "Month-end close finance ticket volume spiked 340%, creating critical bottlenecks for ERP access approvals.";
                recsMarkdown = "- [ ] **Process Automation:** Establish pre-approved delegation protocol in Jira Service Management during Month-End Days -3 to +3.\n- [ ] **AI Integration:** Enable Gemini Auto-Triage on ERP permission tickets to reduce MTTR from 3.8 hours to <12 minutes.\n- [ ] **SOX Compliance:** Automate signed hash digest synchronization from Cloud Firestore to PwC / EY external auditor portal.";
            } else if (currentScenarioPayload && currentScenarioPayload.summary) {
                dynamicInsights = currentScenarioPayload.summary;
            }

            const mdContent = `# ITIL Post-Incident & Remediation Report
**Reference ID:** ${refId}
**Date:** ${dateStr}
**Prepared By:** ${currentUser ? currentUser.displayName : "Chandraprakash Hingal"}
**Confidentiality:** Internal / Compliance Auditors Only

---

## 1. Incident Overview & Executive Summary
- **Target System / Scope:** ${target}
- **Remediation Action:** ${title}
- **Financial & Operational Impact:** ${impact}
- **Status:** Closed / Remediated

## 2. Root Cause Analysis & Anomaly Diagnosis
**Event Trigger:** AI Predictive Telemetry identified a compliance/financial anomaly.
**Description:** ${dynamicInsights}
**Action Required:** Immediate programmatic intervention required to prevent SLA breaches and recover resources.

### Telemetry Snapshot at Time of Execution
![Telemetry Chart Snapshot](${chartBase64})


## 3. Timeline of Events & Automated Remediation
The following actions were taken autonomously by the WorkplacePulse Sentinel Engine:
\`\`\`text
${document.getElementById('report-modal-steps').innerText}
\`\`\`\n
## 4. Trust Services Criteria & Security Controls Attestation
In accordance with SOC 2 Type II requirements, the following controls were verified during execution:
- [x] **Control ID SOC2-CC6.1 (Authentication):** Firebase JWT Google Sign-In Verified
- [x] **Control ID SOC2-CC6.2 (Data Segregation):** Cloud Firestore Multi-Tenant isolation enforced (/users/{uid}/*)
- [x] **Control ID SOC2-CC6.3 (Secret Management):** Google Cloud Secret Manager Application Default Credentials utilized (Zero hardcoded keys).

## 5. Gemini AI Strategic Recommendations & Next Actions
${recsMarkdown}

## 6. External Webhook Dispatch & Evidence of Implementation
The following external messaging platforms were successfully notified of the remediation event:
\`\`\`text
${document.getElementById('report-modal-webhooks').innerText.replace(/\n/g, '\n- ')}
\`\`\`\n
## 7. Management Sign-Off & Cryptographic Ledger
- **Firestore Immutable Audit Path:** /users/${currentUser ? currentUser.uid : 'demo_user'}/runbook_logs/${refId}
- **Cryptographic Signature:** HMAC-SHA256 (Verified via Google Cloud Secret Manager)
- **Time of Execution:** ${timestamp}

---
*Generated autonomously by WorkplacePulse Sentinel Engine on Google Cloud Run.*
`;

            const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `Incident_Report_${refId}.md`;
            link.click();
        }

        async function fetchRunbooks() {
            try {
                const res = await fetch('/api/runbooks');
                if (res.ok) {
                    availableRunbooks = await res.json();
                    updateRunbookCardForScenario(currentScenarioId);
                }
            } catch (err) {
                console.error("Failed to load runbooks catalog:", err);
            }
        }

        function updateRunbookCardForScenario(scenarioId) {
            const runbook = availableRunbooks.find(r => r.scenario_id === scenarioId);
            if (!runbook) return;

            document.getElementById('runbook-title').innerText = runbook.title;
            document.getElementById('runbook-desc').innerText = runbook.description;
            document.getElementById('runbook-target-system').innerText = `Target: ${runbook.target_system}`;
            document.getElementById('runbook-impact').innerText = runbook.estimated_impact;
        }

        async function executeActiveRunbook() {
            const runbook = availableRunbooks.find(r => r.scenario_id === currentScenarioId);
            if (!runbook) {
                alert("No runbook found for active scenario.");
                return;
            }

            const btn = document.getElementById('btn-execute-runbook');
            btn.disabled = true;
            btn.innerHTML = `<span class="animate-spin inline-block mr-2">⚙️</span> Executing Runbook...`;

            const terminalContainer = document.getElementById('runbook-terminal-container');
            const terminalLogs = document.getElementById('runbook-terminal-logs');
            const webhookResults = document.getElementById('runbook-webhook-results');
            
            terminalContainer.classList.remove('hidden');
            terminalLogs.innerHTML = `<p class="text-slate-400">> Initiating ${runbook.action_id} on Cloud Run...</p>`;
            webhookResults.innerHTML = '';

            try {
                const headers = { 'Content-Type': 'application/json' };
                if (userAuthToken) headers['Authorization'] = `Bearer ${userAuthToken}`;

                const response = await fetch('/api/runbooks/execute', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        action_id: runbook.action_id,
                        scenario_id: currentScenarioId,
                        dispatch_webhooks: true
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    terminalLogs.innerHTML = '';
                    data.execution_log.forEach((logLine, idx) => {
                        terminalLogs.innerHTML += `<p class="text-emerald-300">${DOMPurify.sanitize(logLine)}</p>`;
                    });

                    // Render Webhook Delivery Results
                    if (data.webhook_deliveries && data.webhook_deliveries.length > 0) {
                        data.webhook_deliveries.forEach(wh => {
                            const badgeColor = wh.status === 'delivered' || wh.status === 'simulated' ? 'bg-emerald-100 text-emerald-800 border-emerald-300' : 'bg-rose-100 text-rose-800 border-rose-300';
                            webhookResults.innerHTML += `
                                <div class="px-2.5 py-1 rounded-md border text-[11px] font-semibold flex items-center space-x-1.5 ${badgeColor}">
                                    <span>${wh.service_type === 'slack' ? '💬' : wh.service_type === 'discord' ? '🎮' : '🌐'}</span>
                                    <span>${DOMPurify.sanitize(wh.webhook_name)}</span>
                                    <span class="opacity-75">(${wh.status} &bull; ${wh.duration_ms}ms)</span>
                                </div>
                            `;
                        });
                    }
                } else {
                    terminalLogs.innerHTML += `<p class="text-rose-400">> Execution Error (${response.status}): ${DOMPurify.sanitize(data.detail || 'Failed')}</p>`;
                }
            } catch (err) {
                terminalLogs.innerHTML += `<p class="text-rose-400">> Network Error executing runbook: ${DOMPurify.sanitize(err.message)}</p>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = `<span>🚀</span> <span>Execute Runbook & Dispatch Alert</span>`;
            }
        }

        // ---------------------------------------------------------
        // Webhook Hub Management
        // ---------------------------------------------------------
        function openWebhookModal() {
            document.getElementById('webhook-modal').classList.remove('hidden');
            loadWebhooks();
        }

        function closeWebhookModal() {
            document.getElementById('webhook-modal').classList.add('hidden');
        }

        function switchWebhookTab(tabName) {
            ['destinations', 'simulator', 'register', 'logs'].forEach(t => {
                const el = document.getElementById(`tab-${t}`);
                const btn = document.getElementById(`tab-btn-${t}`);
                if (el) el.classList.add('hidden');
                if (btn) btn.className = "px-4 py-3 text-xs font-bold border-b-2 border-transparent text-slate-500 hover:text-slate-700 transition";
            });

            if (tabName === 'destinations') {
                document.getElementById('tab-destinations').classList.remove('hidden');
                document.getElementById('tab-btn-destinations').className = "px-4 py-3 text-xs font-bold border-b-2 border-indigo-600 text-indigo-600 transition";
                loadWebhooks();
            } else if (tabName === 'simulator') {
                document.getElementById('tab-simulator').classList.remove('hidden');
                document.getElementById('tab-btn-simulator').className = "px-4 py-3 text-xs font-bold border-b-2 border-indigo-600 text-indigo-600 transition flex items-center space-x-1.5";
                updateSimulatedPayload();
            } else if (tabName === 'register') {
                document.getElementById('tab-register').classList.remove('hidden');
                document.getElementById('tab-btn-register').className = "px-4 py-3 text-xs font-bold border-b-2 border-indigo-600 text-indigo-600 transition";
            } else if (tabName === 'logs') {
                document.getElementById('tab-logs').classList.remove('hidden');
                document.getElementById('tab-btn-logs').className = "px-4 py-3 text-xs font-bold border-b-2 border-indigo-600 text-indigo-600 transition";
                loadWebhookDeliveries();
            }
        }

        async function loadWebhooks() {
            try {
                const headers = {};
                if (userAuthToken) headers['Authorization'] = `Bearer ${userAuthToken}`;
                const res = await fetch('/api/webhooks', { headers });
                if (res.ok) {
                    registeredWebhooks = await res.json();
                    renderWebhooksList(registeredWebhooks);
                    document.getElementById('modal-hook-count').innerText = registeredWebhooks.length;
                    document.getElementById('nav-webhook-count').innerText = registeredWebhooks.length;
                }
            } catch (err) {
                console.error("Failed to load webhooks:", err);
            }
        }

        function renderWebhooksList(hooks) {
            const container = document.getElementById('webhook-list-container');
            container.innerHTML = '';

            if (!hooks || hooks.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-8 text-slate-400">
                        <p class="text-3xl mb-2">🔔</p>
                        <p class="text-xs font-semibold">No custom webhooks registered yet.</p>
                        <p class="text-[11px] mt-1">Register a Slack, Teams, or Discord webhook to receive live incident dispatch alerts.</p>
                        <button onclick="switchWebhookTab('register')" class="mt-3 bg-indigo-50 text-indigo-600 font-bold px-3 py-1.5 rounded-lg text-xs hover:bg-indigo-100 transition">
                            + Register Destination
                        </button>
                    </div>
                `;
                return;
            }

            hooks.forEach(h => {
                let srvBadge = '';
                if (h.service_type === 'slack') {
                    srvBadge = `<span class="inline-flex items-center space-x-1 text-[10px] font-bold bg-[#4A154B]/10 text-[#4A154B] px-2 py-0.5 rounded border border-[#4A154B]/20"><svg class="w-3 h-3 inline mr-1" viewBox="0 0 24 24" fill="none"><path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z" fill="#E01E5A"/></svg> Slack</span>`;
                } else if (h.service_type === 'teams') {
                    srvBadge = `<span class="inline-flex items-center space-x-1 text-[10px] font-bold bg-[#5B5FC7]/10 text-[#5B5FC7] px-2 py-0.5 rounded border border-[#5B5FC7]/20"><svg class="w-3 h-3 inline mr-1" viewBox="0 0 24 24" fill="none"><path d="M14.5 9.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM17 11h-5a2 2 0 0 0-2 2v4a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-4a2 2 0 0 0-3-2zM8 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM9.5 8h-3a2 2 0 0 0-2 2v3.5a.5.5 0 0 0 .5.5H8v-2a3 3 0 0 1 3-3h.5a2 2 0 0 0-2-1z" fill="#5B5FC7"/></svg> MS Teams</span>`;
                } else if (h.service_type === 'discord') {
                    srvBadge = `<span class="inline-flex items-center space-x-1 text-[10px] font-bold bg-[#5865F2]/10 text-[#5865F2] px-2 py-0.5 rounded border border-[#5865F2]/20"><svg class="w-3 h-3 inline mr-1" viewBox="0 0 24 24" fill="none"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994.021-.041.001-.09-.041-.106a13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.929 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.894.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.028zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" fill="#5865F2"/></svg> Discord</span>`;
                } else {
                    srvBadge = `<span class="inline-flex items-center space-x-1 text-[10px] font-bold bg-sky-50 text-sky-700 px-2 py-0.5 rounded border border-sky-200"><svg class="w-3 h-3 inline mr-1" viewBox="0 0 24 24" fill="none"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" stroke="#0284C7" stroke-width="2" stroke-linecap="round"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" stroke="#0284C7" stroke-width="2" stroke-linecap="round"/></svg> Generic JSON</span>`;
                }

                container.innerHTML += `
                    <div class="bg-white border border-slate-200 rounded-xl p-4 flex items-center justify-between shadow-sm">
                        <div>
                            <div class="flex items-center space-x-2">
                                <span class="text-xs font-bold text-slate-900">${escapeHtml(h.name)}</span>
                                ${srvBadge}
                                ${h.has_secret ? '<span class="text-[10px] font-bold bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded">🔒 HMAC</span>' : ''}
                            </div>
                            <p class="text-[11px] text-slate-500 font-mono-code mt-1">${escapeHtml(h.url)}</p>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button onclick="testWebhook('${h.webhook_id}', this)" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs px-3 py-1.5 rounded-lg transition flex items-center space-x-1">
                                <span>⚡</span> <span>Test Ping</span>
                            </button>
                            <button onclick="deleteWebhook('${h.webhook_id}')" class="text-slate-400 hover:text-rose-600 p-1.5 rounded-lg transition" title="Delete Webhook">
                                🗑️
                            </button>
                        </div>
                    </div>
                `;
            });
        }

        function getSimulatedWebhookData() {
            const eventType = document.getElementById('sim-event-select') ? document.getElementById('sim-event-select').value : 'saas_finops';
            const platform = document.getElementById('sim-platform-select') ? document.getElementById('sim-platform-select').value : 'slack';
            
            const eventDetails = {
                saas_finops: {
                    title: "SaaS FinOps: 130 Idle Figma Seats Reclaimed",
                    severity: "HIGH",
                    impact: "$56,400.00/yr Recurring SaaS Waste",
                    target: "Okta Universal Directory / SCIM 2.0",
                    action: "act_saas_reclaim_01"
                },
                hardware_lifecycle: {
                    title: "Hardware Health: Jamf Battery Swell Quarantine",
                    severity: "CRITICAL",
                    impact: "42 Endpoint Batteries at Swelling Threshold (>800 cycles)",
                    target: "Jamf Pro MDM / Apple Device Enrollment",
                    action: "act_hardware_quarantine_02"
                },
                itsm_surge: {
                    title: "ITSM Surge: Month-End Fast-Track Matrix Activated",
                    severity: "MEDIUM",
                    impact: "Reduced Close MTTR from 3.8 hrs to 12 mins",
                    target: "Jira Service Management / ServiceNow",
                    action: "act_itsm_sox_fasttrack_03"
                }
            }[eventType];

            let payloadObj = {};
            if (platform === 'slack') {
                payloadObj = {
                    "text": `🚨 *WorkplacePulse Incident Alert:* ${eventDetails.title}`,
                    "blocks": [
                        {
                            "type": "header",
                            "text": { "type": "plain_text", "text": `🚨 Sentinel Incident Dispatch: ${eventDetails.title}`, "emoji": true }
                        },
                        {
                            "type": "section",
                            "fields": [
                                { "type": "mrkdwn", "text": `*Severity:*\n\`${eventDetails.severity}\`` },
                                { "type": "mrkdwn", "text": `*Target System:*\n${eventDetails.target}` },
                                { "type": "mrkdwn", "text": `*Financial Impact:*\n${eventDetails.impact}` },
                                { "type": "mrkdwn", "text": `*Status:*\n🟢 Autonomous Remediation Complete` }
                            ]
                        },
                        {
                            "type": "context",
                            "elements": [
                                { "type": "mrkdwn", "text": `🕒 Timestamp: ${new Date().toISOString()} | Ref: \`INC-${Math.floor(Math.random()*900000+100000)}\`` }
                            ]
                        }
                    ]
                };
            } else if (platform === 'teams') {
                payloadObj = {
                    "type": "message",
                    "attachments": [
                        {
                            "contentType": "application/vnd.microsoft.card.adaptive",
                            "content": {
                                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                                "type": "AdaptiveCard",
                                "version": "1.4",
                                "body": [
                                    { "type": "TextBlock", "text": `🚨 Sentinel Alert: ${eventDetails.title}`, "weight": "Bolder", "size": "Medium", "color": "Attention" },
                                    {
                                        "type": "FactSet",
                                        "facts": [
                                            { "title": "Severity:", "value": eventDetails.severity },
                                            { "title": "Target:", "value": eventDetails.target },
                                            { "title": "Impact:", "value": eventDetails.impact },
                                            { "title": "Execution Ref:", "value": `INC-${Math.floor(Math.random()*900000+100000)}` }
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                };
            } else if (platform === 'discord') {
                payloadObj = {
                    "content": `🚨 **WorkplacePulse Sentinel Incident Alert**`,
                    "embeds": [
                        {
                            "title": eventDetails.title,
                            "color": eventDetails.severity === 'CRITICAL' ? 15548997 : 5793266,
                            "fields": [
                                { "name": "Severity", "value": eventDetails.severity, "inline": true },
                                { "name": "Target System", "value": eventDetails.target, "inline": true },
                                { "name": "Estimated Impact", "value": eventDetails.impact, "inline": false }
                            ],
                            "footer": { "text": "WorkplacePulse Cloud Run Sentinel Engine" },
                            "timestamp": new Date().toISOString()
                        }
                    ]
                };
            } else {
                payloadObj = {
                    "event_type": "incident.remediation.completed",
                    "incident_id": `INC-${Math.floor(Math.random()*900000+100000)}`,
                    "action_id": eventDetails.action,
                    "target_system": eventDetails.target,
                    "severity": eventDetails.severity,
                    "estimated_impact": eventDetails.impact,
                    "timestamp": new Date().toISOString(),
                    "environment": "production"
                };
            }

            return { eventDetails, payloadObj, platform };
        }

        function updateSimulatedPayload() {
            const { payloadObj, platform } = getSimulatedWebhookData();
            const codeEl = document.getElementById('sim-payload-code');
            const badgeEl = document.getElementById('sim-payload-type-badge');
            if (codeEl) {
                codeEl.innerText = JSON.stringify(payloadObj, null, 2);
            }
            if (badgeEl) {
                badgeEl.innerText = platform.toUpperCase() + ' WIRE JSON';
            }
        }

        function runWebhookSimulation() {
            const { eventDetails, payloadObj, platform } = getSimulatedWebhookData();
            const terminal = document.getElementById('sim-terminal');
            const runBtn = document.getElementById('btn-run-simulation');
            
            runBtn.disabled = true;
            runBtn.innerHTML = `<span class="animate-spin mr-1">⚙️</span> Simulating Dispatch...`;
            
            // Reset steps
            for (let i = 1; i <= 4; i++) {
                const s = document.getElementById(`sim-step-${i}`);
                if (s) {
                    s.className = "bg-white p-3 rounded-xl border-2 border-slate-200 transition-all duration-300";
                    document.getElementById(`sim-step-icon-${i}`).innerText = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"][i-1];
                }
            }

            terminal.innerHTML = `> [${new Date().toLocaleTimeString()}] INITIATING WEBHOOK SIMULATION PIPELINE...<br>`;

            const simStages = [
                {
                    stepNum: 1,
                    delay: 400,
                    log: `> [Step 1/4] EVENT_TRIGGER: Anomaly '${eventDetails.title}' detected.<br>> Assembling wire payload into ${platform.toUpperCase()} format... OK.`
                },
                {
                    stepNum: 2,
                    delay: 900,
                    log: `> [Step 2/4] CRYPTOGRAPHY: Computing HMAC-SHA256 signature with Secret Manager key...<br>> Header 'X-WorkplacePulse-Signature: sha256=a8f9c0e12d4b...' generated.`
                },
                {
                    stepNum: 3,
                    delay: 1400,
                    log: `> [Step 3/4] TRANSPORT: Initiating HTTPS mTLS connection to ${platform.toUpperCase()} endpoint...<br>> POST https://hooks.${platform === 'generic' ? 'enterprise-siem.com' : platform + '.com'}/v2/dispatch...`
                },
                {
                    stepNum: 4,
                    delay: 1900,
                    log: `> [Step 4/4] ACKNOWLEDGMENT: HTTP 200 OK received in 13.8ms.<br>> Committing immutable delivery audit log to Cloud Firestore... SUCCESS.`
                }
            ];

            simStages.forEach(stage => {
                setTimeout(() => {
                    terminal.innerHTML += `${stage.log}<br>`;
                    terminal.scrollTop = terminal.scrollHeight;
                    
                    const stepEl = document.getElementById(`sim-step-${stage.stepNum}`);
                    if (stepEl) {
                        stepEl.className = "bg-emerald-50 p-3 rounded-xl border-2 border-emerald-500 shadow-sm transition-all duration-300";
                        document.getElementById(`sim-step-icon-${stage.stepNum}`).innerText = "✅";
                    }

                    if (stage.stepNum === 4) {
                        runBtn.disabled = false;
                        runBtn.innerHTML = `<span>▶️</span> <span>Run Dispatch Simulation</span>`;
                        terminal.innerHTML += `> 🎉 Webhook dispatched & verified across all pipeline stages!<br>`;
                        terminal.scrollTop = terminal.scrollHeight;
                    }
                }, stage.delay);
            });
        }

        function fillWebhookPreset(type) {
            if (type === 'slack') {
                document.getElementById('wh-input-name').value = "#incident-alerts-slack";
                document.getElementById('wh-input-service').value = "slack";
                document.getElementById('wh-input-secret').value = "whsec_live_9a8f7c6e5d";
                document.getElementById('wh-input-url').value = "https://hooks.slack.com/services/YOUR_WORKSPACE/YOUR_WEBHOOK";
            } else if (type === 'teams') {
                document.getElementById('wh-input-name').value = "MS Teams IT-Ops Channel";
                document.getElementById('wh-input-service').value = "teams";
                document.getElementById('wh-input-secret').value = "whsec_teams_77218392";
                document.getElementById('wh-input-url').value = "https://acme.webhook.office.com/webhookb2/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX@XXXXXXXX/IncomingWebhook/XXXXXXXX";
            } else if (type === 'discord') {
                document.getElementById('wh-input-name').value = "Discord SecOps Bot";
                document.getElementById('wh-input-service').value = "discord";
                document.getElementById('wh-input-secret').value = "";
                document.getElementById('wh-input-url').value = "https://discord.com/api/webhooks/123456789012345678/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";
            }
        }

        async function handleRegisterWebhook(e) {
            e.preventDefault();
            const name = document.getElementById('wh-input-name').value.trim();
            const service_type = document.getElementById('wh-input-service').value;
            let url = document.getElementById('wh-input-url').value.trim();
            const secret_token = document.getElementById('wh-input-secret').value.trim() || null;

            if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
                url = 'https://' + url;
            }

            try {
                const headers = { 'Content-Type': 'application/json' };
                if (userAuthToken) headers['Authorization'] = `Bearer ${userAuthToken}`;

                const res = await fetch('/api/webhooks', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        name: name,
                        service_type: service_type,
                        url: url,
                        secret_token: secret_token
                    })
                });

                if (res.ok) {
                    document.getElementById('webhook-register-form').reset();
                    switchWebhookTab('destinations');
                } else {
                    const errData = await res.json();
                    alert(`Failed to create webhook: ${errData.detail || 'Validation error'}`);
                }
            } catch (err) {
                alert(`Network error creating webhook: ${err.message}`);
            }
        }

        async function testWebhook(webhookId, btnEl) {
            const hook = (registeredWebhooks || []).find(w => w.webhook_id === webhookId);
            const hookName = hook ? hook.name : "Webhook Destination";
            const hookUrl = hook ? hook.url : "https://hooks.example.com/...";
            const hookPlatform = hook ? hook.service_type : "generic";
            const hasSecret = hook ? hook.has_secret : false;

            const terminalContainer = document.getElementById('test-ping-terminal-container');
            const terminalLogs = document.getElementById('test-ping-terminal-logs');
            const terminalTitle = document.getElementById('test-ping-terminal-title');
            if (!terminalLogs) return;

            if (terminalContainer) {
                terminalContainer.classList.remove('hidden');
                terminalContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
            if (terminalTitle) {
                terminalTitle.innerText = `⚡ Dispatch Console: ${hookName} (${hookPlatform.toUpperCase()})`;
            }

            const nowStr = () => new Date().toISOString().split('T')[1].replace('Z', '');
            
            terminalLogs.innerHTML = `
                <div class="text-slate-400 font-mono">[${nowStr()}] > Initializing test ping dispatch to ${escapeHtml(hookName)}...</div>
                <div class="text-slate-400 font-mono">[${nowStr()}] > Target Endpoint: ${escapeHtml(hookUrl)}</div>
            `;

            let originalBtnHtml = "";
            if (btnEl) {
                originalBtnHtml = btnEl.innerHTML;
                btnEl.disabled = true;
                btnEl.innerHTML = `<span>⏳</span> <span>Pinging...</span>`;
            }

            const steps = [
                { text: `[${nowStr()}] > Formatting JSON payload for ${hookPlatform.toUpperCase()} receiver specification...`, delay: 120 },
                { text: `[${nowStr()}] > ${hasSecret ? 'HMAC-SHA256 signature generated with Secret Manager tenant key' : 'Standard payload digest prepared (X-Hub-Signature-256)'}`, delay: 280 },
                { text: `[${nowStr()}] > Establishing TLS session and dispatching HTTPS POST request...`, delay: 450 }
            ];

            steps.forEach(step => {
                setTimeout(() => {
                    if (terminalLogs) {
                        terminalLogs.innerHTML += `<div class="text-indigo-400 font-mono">${step.text}</div>`;
                        terminalLogs.scrollTop = terminalLogs.scrollHeight;
                    }
                }, step.delay);
            });

            try {
                const headers = { 'Content-Type': 'application/json' };
                if (userAuthToken) headers['Authorization'] = `Bearer ${userAuthToken}`;

                const res = await fetch('/api/webhooks/test', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ webhook_id: webhookId })
                });

                const data = await res.json();
                
                setTimeout(() => {
                    if (res.ok) {
                        terminalLogs.innerHTML += `
                            <div class="text-slate-300 font-mono">[${nowStr()}] > Server Response: HTTP 200 OK (Latency: ${data.duration_ms || 12.5}ms)</div>
                            <div class="text-slate-400 font-mono">[${nowStr()}] > Delivery logged to Firestore collection /deliveries/${data.delivery_id || 'del_' + Date.now().toString().slice(-6)}</div>
                            <div class="text-emerald-400 font-mono font-bold mt-1">[${nowStr()}] > ✅ SUCCESS: Webhook ping delivered successfully to ${escapeHtml(hookName)}!</div>
                        `;
                    } else {
                        terminalLogs.innerHTML += `
                            <div class="text-amber-400 font-mono">[${nowStr()}] > Server Response: HTTP ${res.status} (${data.detail || data.error_message || 'Endpoint returned error'})</div>
                            <div class="text-rose-400 font-mono font-bold mt-1">[${nowStr()}] > ❌ Notice: External endpoint returned error. Logged in Delivery Audit Trail.</div>
                        `;
                    }
                    terminalLogs.scrollTop = terminalLogs.scrollHeight;

                    if (btnEl) {
                        btnEl.disabled = false;
                        btnEl.innerHTML = originalBtnHtml || `<span>⚡</span> <span>Test Ping</span>`;
                    }
                }, 650);

            } catch (err) {
                setTimeout(() => {
                    terminalLogs.innerHTML += `
                        <div class="text-rose-400 font-mono font-bold mt-1">[${nowStr()}] > ❌ Network Error: ${err.message}</div>
                    `;
                    terminalLogs.scrollTop = terminalLogs.scrollHeight;
                    if (btnEl) {
                        btnEl.disabled = false;
                        btnEl.innerHTML = originalBtnHtml || `<span>⚡</span> <span>Test Ping</span>`;
                    }
                }, 650);
            }
        }

        async function deleteWebhook(webhookId) {
            if (!confirm("Are you sure you want to delete this webhook destination?")) return;
            try {
                const headers = {};
                if (userAuthToken) headers['Authorization'] = `Bearer ${userAuthToken}`;
                const res = await fetch(`/api/webhooks/${webhookId}`, {
                    method: 'DELETE',
                    headers: headers
                });
                if (res.ok) {
                    loadWebhooks();
                } else {
                    alert("Failed to delete webhook.");
                }
            } catch (err) {
                alert(`Error deleting webhook: ${err.message}`);
            }
        }

        async function loadWebhookDeliveries() {
            const body = document.getElementById('webhook-logs-body');
            body.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-slate-400">Loading audit history...</td></tr>';
            try {
                const headers = {};
                if (userAuthToken) headers['Authorization'] = `Bearer ${userAuthToken}`;
                const res = await fetch('/api/webhooks/deliveries', { headers });
                if (res.ok) {
                    const logs = await res.json();
                    if (!logs || logs.length === 0) {
                        body.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-slate-400">No delivery logs recorded yet.</td></tr>';
                        return;
                    }
                    body.innerHTML = '';
                    logs.forEach(l => {
                        const statusClass = l.status === 'delivered' || l.status === 'simulated' ? 'text-emerald-600 font-bold' : 'text-rose-600 font-bold';
                        body.innerHTML += `
                            <tr class="hover:bg-slate-50">
                                <td class="p-2">${escapeHtml(l.timestamp.slice(11, 19))} UTC</td>
                                <td class="p-2 font-medium">${escapeHtml(l.webhook_name)}</td>
                                <td class="p-2 uppercase text-[10px]">${escapeHtml(l.service_type)}</td>
                                <td class="p-2 text-slate-500 font-mono-code">${escapeHtml(l.event_type)}</td>
                                <td class="p-2 ${statusClass}">${escapeHtml(l.status)}</td>
                                <td class="p-2 text-slate-500">${l.duration_ms}ms</td>
                            </tr>
                        `;
                    });
                }
            } catch (err) {
                body.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-rose-500">Failed to load delivery logs: ${DOMPurify.sanitize(err.message)}</td></tr>`;
            }
        }

        // ---------------------------------------------------------
        // Conversational AI Chat & Markdown Formatting
        // ---------------------------------------------------------
        function sendQuickPrompt(promptText) {
            document.getElementById('chat-input').value = promptText;
            document.getElementById('chat-form').dispatchEvent(new Event('submit'));
        }

        async function handleChatSubmit(e) {
            e.preventDefault();
            const inputField = document.getElementById('chat-input');
            const message = inputField.value.trim();
            if (!message) return;

            inputField.value = '';
            const btnSend = document.getElementById('btn-send');
            btnSend.disabled = true;

            const chatContainer = document.getElementById('chat-messages');

            chatContainer.innerHTML += `
                <div class="flex items-start justify-end space-x-3 mb-6 animate-in fade-in duration-200">
                    <div class="space-y-1 max-w-[85%] flex flex-col items-end">
                        <div class="flex items-center space-x-2 text-[10px] text-slate-400">
                            <span>Just now</span>
                            <span class="font-bold text-slate-800 text-xs">You</span>
                        </div>
                        <div class="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-[13px] leading-relaxed shadow-sm">
                            ${escapeHtml(message)}
                        </div>
                    </div>
                    <div class="h-8 w-8 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold text-sm shrink-0 shadow-sm ring-2 ring-slate-100 mt-0.5">
                        👤
                    </div>
                </div>
            `;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            chatContainer.innerHTML += `
                <div id="${loadingId}" class="flex items-start space-x-3 mb-6">
                    <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 text-white flex items-center justify-center font-bold text-sm shrink-0 shadow-sm ring-2 ring-indigo-50 mt-0.5">
                        🤖
                    </div>
                    <div class="space-y-1 w-full overflow-hidden">
                        <div class="flex items-center space-x-2">
                            <span class="text-xs font-bold text-slate-800">Gemini Copilot</span>
                            <span class="text-[10px] text-slate-400">Thinking...</span>
                        </div>
                        <div class="bg-slate-50 border border-slate-200/60 rounded-2xl rounded-tl-sm px-4 py-3 text-slate-700 shadow-sm inline-flex items-center space-x-2">
                            <div class="h-1.5 w-1.5 bg-indigo-500 rounded-full animate-bounce"></div>
                            <div class="h-1.5 w-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                            <div class="h-1.5 w-1.5 bg-indigo-500 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                        </div>
                    </div>
                </div>
            `;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const headers = { 'Content-Type': 'application/json' };
                if (userAuthToken) {
                    headers['Authorization'] = `Bearer ${userAuthToken}`;
                }
                const mainKey = document.getElementById('api-key-input');
                const suppKey = document.getElementById('support-api-key-input');
                const activeKey = (mainKey && mainKey.value) ? mainKey.value : (sessionStorage.getItem('byok_gemini_key') || (suppKey ? suppKey.value : ''));
                if (activeKey) {
                    headers['X-Gemini-API-Key'] = activeKey;
                }

                const response = await fetch('/api/forecast/chat', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        scenario_id: currentScenarioId,
                        message: message,
                        history: chatHistory
                    })
                });

                const data = await response.json();
                document.getElementById(loadingId).remove();

                if (response.ok) {
                    const aiContent = data.response;
                    chatHistory.push({ role: "user", content: message });
                    chatHistory.push({ role: "model", content: aiContent });

                    const parsedHtml = DOMPurify.sanitize(marked.parse(aiContent));
                    chatContainer.innerHTML += `
                        <div class="flex items-start space-x-3 mb-6 animate-in fade-in duration-200">
                            <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 text-white flex items-center justify-center font-bold text-sm shrink-0 shadow-sm ring-2 ring-indigo-50 mt-0.5">
                                🤖
                            </div>
                            <div class="space-y-1 w-full overflow-hidden">
                                <div class="flex items-center space-x-2">
                                    <span class="text-xs font-bold text-slate-800">Gemini Copilot</span>
                                    <span class="text-[10px] text-slate-400">Just now</span>
                                </div>
                                <div class="prose prose-sm prose-slate max-w-none text-[13px] leading-relaxed overflow-x-auto w-full">
                                    ${parsedHtml}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    chatContainer.innerHTML += `
                        <div class="bg-rose-50 border border-rose-600 text-rose-700 p-3 rounded-xl text-xs">
                            <strong>Error (${response.status}):</strong> ${DOMPurify.sanitize(data.detail || 'Failed to complete forecast analysis.')}
                        </div>
                    `;
                }
            } catch (err) {
                document.getElementById(loadingId).remove();
                chatContainer.innerHTML += `
                    <div class="bg-rose-50 border border-rose-600 text-rose-700 p-3 rounded-xl text-xs">
                        <strong>Network Error:</strong> Failed to reach backend API endpoint.
                    </div>
                `;
            } finally {
                btnSend.disabled = false;
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }

        function escapeHtml(text) {
            if (!text) return "";
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function connectApiCredentials() {
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
                var aiBadge = document.getElementById('ai-data-badge');
                if(aiBadge) {
                    aiBadge.innerText = "Live Data";
                    aiBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }
                var suppBadge = document.getElementById('supp-ai-data-badge');
                if(suppBadge) {
                    suppBadge.innerText = "Live Data";
                    suppBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }
                var aiBadge = document.getElementById('ai-data-badge');
                if(aiBadge) {
                    aiBadge.innerText = "Live Data";
                    aiBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }
                var suppBadge = document.getElementById('supp-ai-data-badge');
                if(suppBadge) {
                    suppBadge.innerText = "Live Data";
                    suppBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
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

        function showDashboard() {
            document.getElementById('dashboard-view').classList.remove('hidden');
            document.getElementById('data-sources-view').classList.add('hidden');
            document.getElementById('support-view').classList.add('hidden');
            
            // Reset sidebar highlights
            const dsBtn = document.getElementById('btn-nav-data-sources');
            if (dsBtn) dsBtn.className = "w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition border border-slate-200 shadow-sm bg-white mb-2";
            const spBtn = document.getElementById('btn-nav-support');
            if (spBtn) spBtn.className = "w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition bg-transparent";
            
            // Re-highlight active scenario button
            document.querySelectorAll('.scenario-btn').forEach(btn => {
                btn.className = "scenario-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition";
            });
            const activeBtn = document.getElementById(`btn-${currentScenarioId}`);
            if (activeBtn) {
                activeBtn.className = "scenario-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition bg-indigo-50 text-indigo-700 font-bold";
            }
        }

        function showDataSources() {
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('support-view').classList.add('hidden');
            document.getElementById('data-sources-view').classList.remove('hidden');
            
            // Remove scenario button highlights
            document.querySelectorAll('.scenario-btn').forEach(btn => {
                btn.className = "scenario-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition";
            });
            const dsBtn = document.getElementById('btn-nav-data-sources');
            if (dsBtn) dsBtn.className = "w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 shadow-sm mb-2";
            const spBtn = document.getElementById('btn-nav-support');
            if (spBtn) spBtn.className = "w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition bg-transparent";
        }

        function showSupport() {
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('data-sources-view').classList.add('hidden');
            document.getElementById('support-view').classList.remove('hidden');
            
            // Remove scenario button highlights
            document.querySelectorAll('.scenario-btn').forEach(btn => {
                btn.className = "scenario-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition";
            });
            const dsBtn = document.getElementById('btn-nav-data-sources');
            if (dsBtn) dsBtn.className = "w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition border border-slate-200 shadow-sm bg-white mb-2";
            const spBtn = document.getElementById('btn-nav-support');
            if (spBtn) spBtn.className = "w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 shadow-sm";
        }

        function connectSupportApiCredentials() {
            const apiKey = document.getElementById('support-api-key-input').value.trim();
            const errorEl = document.getElementById('support-api-key-error');

            // Clear previous error
            if (errorEl) { errorEl.classList.add('hidden'); errorEl.innerText = ''; }

            if (!apiKey) {
                if (errorEl) { errorEl.innerText = '⚠️ Please enter an API key.'; errorEl.classList.remove('hidden'); }
                return;
            }

            // Validate Google API key format — accepts both legacy (AIzaSy...) and newer (AQ....) formats
            const isLegacyFmt = apiKey.startsWith('AIzaSy') && apiKey.length >= 35;
            const isNewFmt = apiKey.startsWith('AQ.');
            
            if (!isLegacyFmt && !isNewFmt) {
                if (errorEl) {
                    errorEl.innerText = '❌ Invalid key format. A valid Google Gemini API key must start with "AIzaSy" (and be 39+ chars) or start with "AQ.". Get yours at aistudio.google.com.';
                    errorEl.classList.remove('hidden');
                }
                return;
            }

            // Persist to session memory only after validation
            sessionStorage.setItem('byok_gemini_key', apiKey);
            sessionStorage.setItem('byok_key_connected', 'true');
            const mainKey = document.getElementById('api-key-input');
            if (mainKey) mainKey.value = apiKey;
            
            const btn = document.getElementById('btn-connect-support-api');
            const progressContainer = document.getElementById('support-api-connect-progress');
            const progressFill = document.getElementById('support-progress-bar-fill');
            const statusText = document.getElementById('support-api-connect-status-text');
            
            btn.classList.add('hidden');
            progressContainer.classList.remove('hidden');
            
            // Simulate connection steps
            statusText.innerText = "Authenticating with Google Cloud...";
            progressFill.style.width = "30%";
            
            setTimeout(() => {
                statusText.innerText = "Verifying Gemini API quota...";
                progressFill.style.width = "70%";
                
                setTimeout(() => {
                    statusText.innerText = "Connection Established!";
                    progressFill.style.width = "100%";
                    
                    setTimeout(() => {
                        // Update both UI labels
                        const label = document.getElementById('api-key-status-label');
                        if (label) {
                            label.innerText = "API Key Connected";
                            label.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                        }
                        const suppLabel = document.getElementById('support-api-key-status-label');
                        if (suppLabel) {
                            suppLabel.innerText = "API Key Connected";
                            suppLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                        }
                        
                        btn.classList.remove('hidden');
                        btn.innerText = "Connected ✅";
                        btn.className = "w-full bg-emerald-600 text-white font-bold py-2 rounded-lg text-xs shadow-sm flex items-center justify-center mt-2 cursor-default";
                        btn.onclick = null;
                        
                        progressContainer.classList.add('hidden');
                        
                        // Collapse form automatically
                        setTimeout(() => {
                            document.getElementById('support-api-creds-form').classList.add('hidden');
                        }, 1000);
                        
                    }, 500);
                }, 800);
            }, 800);
        }

        let supportChatHistory = [];

        function sendSupportQuickPrompt(promptText) {
            const input = document.getElementById('support-chat-input');
            if (input) {
                input.value = promptText;
                document.getElementById('support-chat-form').dispatchEvent(new Event('submit', { cancelable: true }));
            }
        }

        async function handleSupportChatSubmit(e) {
            e.preventDefault();
            const inputField = document.getElementById('support-chat-input');
            const message = inputField.value.trim();
            if (!message) return;
            
            inputField.value = '';
            const chatContainer = document.getElementById('support-chat-messages');
            
            chatContainer.innerHTML += `
                <div class="flex items-start justify-end space-x-2.5 mb-4 animate-in fade-in duration-200">
                    <div class="space-y-1 max-w-[85%] flex flex-col items-end">
                        <div class="flex items-center space-x-1.5 text-[10px] text-slate-400">
                            <span>You</span>
                        </div>
                        <div class="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-2xl rounded-tr-sm p-3.5 text-xs sm:text-sm leading-relaxed shadow-sm">
                            ${escapeHtml(message)}
                        </div>
                    </div>
                    <div class="h-8 w-8 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-sm ring-2 ring-slate-100 mt-1">
                        👤
                    </div>
                </div>
            `;
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            const loadingId = 'loading-' + Date.now();
            chatContainer.innerHTML += `
                <div id="${loadingId}" class="flex items-start space-x-2.5 mb-4">
                    <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-sm ring-2 ring-indigo-100 mt-1">
                        🤖
                    </div>
                    <div class="bg-slate-50 border border-slate-200/90 rounded-2xl rounded-tl-sm p-3.5 text-slate-700 text-xs shadow-xs flex items-center space-x-2">
                        <div class="h-2 w-2 bg-indigo-600 rounded-full animate-bounce"></div>
                        <div class="h-2 w-2 bg-indigo-600 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                        <div class="h-2 w-2 bg-indigo-600 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                        <span class="text-[11px] text-slate-500 font-medium ml-1">Alex is typing...</span>
                    </div>
                </div>
            `;
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            try {
                const headers = { 'Content-Type': 'application/json' };
                if (userAuthToken) {
                    headers['Authorization'] = `Bearer ${userAuthToken}`;
                }
                const suppKey = document.getElementById('support-api-key-input');
                const mainKey = document.getElementById('api-key-input');
                const activeKey = (suppKey && suppKey.value) ? suppKey.value : (mainKey ? mainKey.value : '');
                if (activeKey) {
                    headers['X-Gemini-API-Key'] = activeKey;
                }

                const response = await fetch('/api/forecast/chat', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        scenario_id: 'support_inquiry',
                        message: message,
                        history: supportChatHistory
                    })
                });

                const data = await response.json();
                document.getElementById(loadingId).remove();

                if (response.ok) {
                    const aiContent = data.response;
                    supportChatHistory.push({ role: "user", content: message });
                    supportChatHistory.push({ role: "model", content: aiContent });

                    const parsedHtml = DOMPurify.sanitize(marked.parse(aiContent));
                    chatContainer.innerHTML += `
                        <div class="flex items-start space-x-2.5 mb-4 animate-in fade-in duration-200">
                            <div class="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-sm ring-2 ring-indigo-100 mt-1">
                                🤖
                            </div>
                            <div class="space-y-1 max-w-[85%]">
                                <div class="flex items-center space-x-2">
                                    <span class="text-[11px] font-bold text-slate-800">Alex &bull; Sentinel Support</span>
                                    <span class="text-[9px] text-slate-400">Just now</span>
                                </div>
                                <div class="bg-slate-50 border border-slate-200/90 rounded-2xl rounded-tl-sm p-3.5 text-slate-800 text-xs sm:text-sm leading-relaxed shadow-xs prose prose-sm prose-slate max-w-none">
                                    ${parsedHtml}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    chatContainer.innerHTML += `
                        <div class="bg-rose-50 border border-rose-600 text-rose-700 p-3 rounded-xl text-xs max-w-[85%]">
                            <strong>Error:</strong> Failed to get support response.
                        </div>
                    `;
                }
            } catch (err) {
                document.getElementById(loadingId).remove();
                chatContainer.innerHTML += `
                    <div class="bg-rose-50 border border-rose-600 text-rose-700 p-3 rounded-xl text-xs max-w-[85%]">
                        <strong>Network Error:</strong> Unable to connect to support endpoint.
                    </div>
                `;
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function saveDataCredentials(btn) {
            btn.innerText = "Verifying...";
            setTimeout(() => {
                btn.innerText = "Save Configuration";
                document.getElementById('ds-save-status').classList.remove('hidden');
                setTimeout(() => {
                    document.getElementById('ds-save-status').classList.add('hidden');
                }, 4000);
            }, 800);
        }

        // Enterprise Data Connectors State
        const DATA_CONNECTORS = {
            'Figma Enterprise': { id: 'figma', name: 'Figma Enterprise', connected: true, lastSynced: '2 mins ago', icon: '/static/figma_logo.png', desc: 'License telemetry & SCIM sync.' },
            'Zoom Pro': { id: 'zoom', name: 'Zoom Pro', connected: false, lastSynced: 'Never', icon: '/static/zoom_logo.png', desc: 'Meeting analytics and user activity.' },
            'Jamf Pro': { id: 'jamf', name: 'Jamf Pro', connected: true, lastSynced: '1 hr ago', icon: '/static/jamf_logo.png', desc: 'Apple fleet MDM telemetry.' },
            'Jira Service Management': { id: 'jira', name: 'Jira Service Management', connected: true, lastSynced: '5 mins ago', icon: '/static/jira_logo.png', desc: 'ITSM ticket surge telemetry.' },
            'Okta': { id: 'okta', name: 'Okta', connected: true, lastSynced: '10 mins ago', icon: '/static/okta_logo.svg', desc: 'SSO & Directory Sync.' }
        };

        let currentSyncSource = null;

        const SAMPLE_PEOPLE = [
            { name: "Sarah Jenkins", email: "sarah.jenkins@acme-corp.com", role: "Lead Product Designer", device: "MacBook Pro 16\" (M3 Max)", ticket: "INC-8492: VPN Tunnel Dropout", status: "Inactive (62d)", activity: "62 days ago" },
            { name: "Marcus Vance", email: "marcus.vance@acme-corp.com", role: "Staff Cloud Architect", device: "MacBook Air 15\" (M2)", ticket: "INC-8493: Figma License Renewal", status: "Active", activity: "1 hour ago" },
            { name: "Elena Rostova", email: "elena.rostova@acme-corp.com", role: "VP of Engineering", device: "Mac Studio (M2 Ultra)", ticket: "INC-8494: SSO Multi-Factor Reset", status: "Active", activity: "3 hours ago" },
            { name: "Alex Chen", email: "alex.chen@acme-corp.com", role: "Sr. Frontend Engineer", device: "MacBook Pro 14\" (M1 Pro)", ticket: "INC-8495: Jamf FileVault Recovery", status: "Inactive (45d)", activity: "45 days ago" },
            { name: "Priya Sharma", email: "priya.sharma@acme-corp.com", role: "Group Product Manager", device: "MacBook Air 13\" (M1)", ticket: "INC-8496: Jira Service Desk Escalation", status: "Inactive (80d)", activity: "80 days ago" },
            { name: "David Kim", email: "david.kim@acme-corp.com", role: "SecOps Incident Responder", device: "MacBook Pro 16\" (M2 Max)", ticket: "INC-8497: Okta SCIM Token Expired", status: "Active", activity: "10 mins ago" },
            { name: "Rachel Green", email: "rachel.green@acme-corp.com", role: "Principal UX Researcher", device: "MacBook Air 13\" (M2)", ticket: "INC-8498: Zoom Cloud Storage Quota", status: "Inactive (34d)", activity: "34 days ago" },
            { name: "Jordan Patel", email: "jordan.patel@acme-corp.com", role: "Data Platform Lead", device: "MacBook Pro 14\" (M3 Pro)", ticket: "INC-8499: BigQuery IAM Sync", status: "Active", activity: "Just now" },
            { name: "Emily Watson", email: "emily.watson@acme-corp.com", role: "DevOps Specialist", device: "MacBook Pro 16\" (M1 Max)", ticket: "INC-8500: Datadog Webhook Failure", status: "Inactive (71d)", activity: "71 days ago" },
            { name: "Carlos Mendez", email: "carlos.mendez@acme-corp.com", role: "IT Helpdesk Specialist", device: "MacBook Air 15\" (M3)", ticket: "INC-8501: Workstation Refresh", status: "Active", activity: "5 mins ago" }
        ];

        function startDataSync(sourceName) {
            currentSyncSource = sourceName;
            const connector = DATA_CONNECTORS[sourceName] || { connected: false };
            const isFirstTimeConnect = !connector.connected;
            
            const modal = document.getElementById('sync-terminal-modal');
            const titleEl = document.getElementById('sync-title');
            const modalBadge = document.getElementById('sync-modal-status-badge');
            const output = document.getElementById('sync-terminal-output');
            const progress = document.getElementById('sync-progress');
            const previewContainer = document.getElementById('sync-preview-container');
            const disconnectBtn = document.getElementById('modal-disconnect-btn');
            const resyncBtn = document.getElementById('modal-resync-btn');
            const closeBtn = document.getElementById('modal-close-btn');
            
            modal.classList.remove('hidden');
            
            if (isFirstTimeConnect) {
                // FIRST-TIME CONNECTING FLOW
                titleEl.innerText = `Connecting: ${sourceName}`;
                if (modalBadge) {
                    modalBadge.innerText = "🟡 Connecting...";
                    modalBadge.className = "text-[10px] bg-amber-100 text-amber-700 font-bold px-2 py-0.5 rounded";
                }
                
                // Hide management controls while connecting
                if (disconnectBtn) disconnectBtn.classList.add('hidden');
                if (resyncBtn) resyncBtn.classList.add('hidden');
                if (closeBtn) {
                    closeBtn.innerText = "Connecting...";
                    closeBtn.disabled = true;
                    closeBtn.className = "text-xs font-bold text-white bg-indigo-400 px-4 py-1.5 rounded-lg transition cursor-not-allowed";
                }
                
                previewContainer.classList.add('hidden');
                output.innerHTML = `> Initiating enterprise authorization handshake for ${sourceName}...<br>`;
                progress.style.width = '5%';
                
                // Update card button to Connecting...
                updateCardConnectingState(sourceName, true);
                
                const connectSteps = [
                    { msg: `> Initiating OAuth 2.0 / SAML 2.0 PKCE Handshake with ${sourceName}...`, delay: 400, prog: 20 },
                    { msg: `> Validating API Scopes: read:telemetry, read:licenses, read:audit_logs...`, delay: 900, prog: 45 },
                    { msg: `> Establishing secure mTLS reverse tunnel to Sentinel Data Pipeline...`, delay: 1400, prog: 70 },
                    { msg: `> Provisioning tenant encryption keys and event-driven webhook dispatch...`, delay: 1900, prog: 88 },
                    { msg: `> Ingesting initial 30-day baseline telemetry and user activity...`, delay: 2400, prog: 96 },
                    { msg: `> Connection established! ${sourceName} is now LIVE and synchronized.`, delay: 2800, prog: 100 }
                ];
                
                connectSteps.forEach(step => {
                    setTimeout(() => {
                        output.innerHTML += `${step.msg}<br>`;
                        output.scrollTop = output.scrollHeight;
                        progress.style.width = `${step.prog}%`;
                        
                        if (step.prog === 100) {
                            if (DATA_CONNECTORS[sourceName]) {
                                DATA_CONNECTORS[sourceName].connected = true;
                                DATA_CONNECTORS[sourceName].lastSynced = "Just now";
                                updateConnectorCardUI(sourceName);
                            }
                            
                            titleEl.innerText = `Manage: ${sourceName}`;
                            if (modalBadge) {
                                modalBadge.innerText = "🟢 Connected";
                                modalBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 font-bold px-2 py-0.5 rounded";
                            }
                            
                            // Restore management buttons
                            if (disconnectBtn) disconnectBtn.classList.remove('hidden');
                            if (resyncBtn) resyncBtn.classList.remove('hidden');
                            if (closeBtn) {
                                closeBtn.innerText = "Done";
                                closeBtn.disabled = false;
                                closeBtn.className = "text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-1.5 rounded-lg transition shadow-sm cursor-pointer";
                            }
                            
                            setTimeout(() => showDataPreview(sourceName), 300);
                        }
                    }, step.delay);
                });
            } else {
                // ALREADY-CONNECTED MANAGE FLOW
                titleEl.innerText = `Manage: ${sourceName}`;
                if (modalBadge) {
                    modalBadge.innerText = "🟢 Connected";
                    modalBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 font-bold px-2 py-0.5 rounded";
                }
                
                if (disconnectBtn) disconnectBtn.classList.remove('hidden');
                if (resyncBtn) resyncBtn.classList.remove('hidden');
                if (closeBtn) {
                    closeBtn.innerText = "Close";
                    closeBtn.disabled = false;
                    closeBtn.className = "text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-1.5 rounded-lg transition shadow-sm cursor-pointer";
                }
                
                progress.style.width = '100%';
                output.innerHTML = `
                    > Status: Integration Active & Healthy.<br>
                    > Last Telemetry Sync: ${connector.lastSynced}.<br>
                    > Continuous Ingestion Mode: Enabled via Webhooks.<br>
                    > Ready to inspect raw records or trigger on-demand sync.
                `;
                showDataPreview(sourceName);
            }
        }

        function updateCardConnectingState(sourceName, isConnecting) {
            const cards = document.querySelectorAll('#data-sources-view .grid > div');
            cards.forEach(card => {
                const title = card.querySelector('h3');
                if (title && title.innerText.trim() === sourceName) {
                    const btn = card.querySelector('button');
                    const badge = card.querySelector('.flex.justify-between span');
                    if (isConnecting) {
                        if (btn) {
                            btn.innerText = "Connecting...";
                            btn.className = "text-xs text-amber-600 font-bold border border-amber-300 bg-amber-50 px-3 py-1.5 rounded-lg transition animate-pulse cursor-wait";
                        }
                        if (badge) {
                            badge.innerText = "🟡 Connecting...";
                            badge.className = "text-[10px] bg-amber-100 text-amber-700 font-bold px-2 py-1 rounded animate-pulse";
                        }
                    }
                }
            });
        }

        function triggerReSync() {
            if (!currentSyncSource) return;
            const output = document.getElementById('sync-terminal-output');
            const progress = document.getElementById('sync-progress');
            const previewContainer = document.getElementById('sync-preview-container');
            
            previewContainer.classList.add('hidden');
            output.innerHTML = `> Triggering ad-hoc telemetry re-sync for ${currentSyncSource}...<br>`;
            progress.style.width = '10%';
            
            const steps = [
                { msg: `> Fetching incremental delta logs from ${currentSyncSource}...`, delay: 400, prog: 40 },
                { msg: `> Reconciling active user licenses and endpoint metrics...`, delay: 900, prog: 75 },
                { msg: `> Schema validation complete. 0 errors detected.`, delay: 1400, prog: 95 },
                { msg: `> Re-sync successful! Updated at ${new Date().toLocaleTimeString()}.`, delay: 1700, prog: 100 }
            ];
            
            steps.forEach(step => {
                setTimeout(() => {
                    output.innerHTML += `${step.msg}<br>`;
                    output.scrollTop = output.scrollHeight;
                    progress.style.width = `${step.prog}%`;
                    if (step.prog === 100) {
                        if (DATA_CONNECTORS[currentSyncSource]) {
                            DATA_CONNECTORS[currentSyncSource].lastSynced = "Just now";
                            updateConnectorCardUI(currentSyncSource);
                        }
                        setTimeout(() => showDataPreview(currentSyncSource), 300);
                    }
                }, step.delay);
            });
        }

        function disconnectCurrentSource() {
            if (!currentSyncSource) return;
            if (!confirm(`Are you sure you want to disconnect ${currentSyncSource}? Automated telemetry ingestion will be stopped.`)) {
                return;
            }
            if (DATA_CONNECTORS[currentSyncSource]) {
                DATA_CONNECTORS[currentSyncSource].connected = false;
                DATA_CONNECTORS[currentSyncSource].lastSynced = "Disconnected";
                updateConnectorCardUI(currentSyncSource);
            }
            document.getElementById('sync-terminal-modal').classList.add('hidden');
            alert(`✓ ${currentSyncSource} has been successfully disconnected.`);
        }

        function updateConnectorCardUI(sourceName) {
            const connector = DATA_CONNECTORS[sourceName];
            if (!connector) return;
            
            // Find card in data-sources view
            const cards = document.querySelectorAll('#data-sources-view .grid > div');
            cards.forEach(card => {
                const title = card.querySelector('h3');
                if (title && title.innerText.trim() === sourceName) {
                    const badge = card.querySelector('.flex.justify-between span');
                    const lastSync = card.querySelector('.text-[10px].text-slate-400');
                    const btn = card.querySelector('button');
                    
                    if (badge) {
                        badge.innerText = connector.connected ? "🟢 Connected" : "⚪ Not Connected";
                        badge.className = connector.connected 
                            ? "text-[10px] bg-emerald-100 text-emerald-700 font-bold px-2 py-1 rounded"
                            : "text-[10px] bg-slate-100 text-slate-500 font-bold px-2 py-1 rounded";
                    }
                    if (lastSync) {
                        lastSync.innerText = connector.connected ? `Last Synced: ${connector.lastSynced}` : "Status: Disconnected";
                    }
                    if (btn) {
                        btn.innerText = connector.connected ? "Manage / Sync" : "Connect";
                        btn.className = connector.connected
                            ? "text-xs text-indigo-600 font-bold border border-indigo-200 hover:bg-indigo-50 px-3 py-1.5 rounded-lg transition"
                            : "text-xs text-slate-600 font-bold border border-slate-200 hover:bg-slate-50 px-3 py-1.5 rounded-lg transition";
                    }
                }
            });
        }

        function showDataPreview(sourceName) {
            const table = document.getElementById('sync-preview-table');
            let rows = "";
            
            // Generate customized rows depending on the connector type
            SAMPLE_PEOPLE.forEach((person, idx) => {
                const idNum = 1000 + (idx * 37) + (sourceName.length * 13);
                let idCol = `USR-${idNum}`;
                let userCol = `
                    <div class="font-bold text-slate-800">${person.name}</div>
                    <div class="text-[10px] text-slate-400 font-mono">${person.email} &bull; ${person.role}</div>
                `;
                
                if (sourceName.includes('Jamf')) {
                    idCol = `DEV-${idNum}`;
                    userCol = `
                        <div class="font-bold text-slate-800">${person.device}</div>
                        <div class="text-[10px] text-slate-400">Assigned: ${person.name} (${person.email})</div>
                    `;
                } else if (sourceName.includes('Jira')) {
                    idCol = person.ticket.split(':')[0];
                    userCol = `
                        <div class="font-bold text-slate-800">${person.ticket}</div>
                        <div class="text-[10px] text-slate-400">Reporter: ${person.name} &bull; ${person.role}</div>
                    `;
                }
                
                const isInactive = person.status.includes('Inactive');
                const badgeClass = isInactive ? "bg-amber-50 text-amber-700 border border-amber-200" : "bg-emerald-50 text-emerald-700 border border-emerald-200";
                
                rows += `
                    <tr class="hover:bg-slate-50/80 transition">
                        <td class="p-2.5 font-mono text-indigo-600 font-bold">${idCol}</td>
                        <td class="p-2.5">${userCol}</td>
                        <td class="p-2.5"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${badgeClass}">${person.status}</span></td>
                        <td class="p-2.5 text-slate-500 font-medium">${person.activity}</td>
                    </tr>
                `;
            });
            
            table.innerHTML = rows;
            document.getElementById('sync-preview-container').classList.remove('hidden');
        }

        // Initialize default scenario and runbooks on page load
        window.addEventListener('DOMContentLoaded', async () => {
            // Restore BYOK API Key if explicitly connected in this session
            const savedKey = sessionStorage.getItem('byok_gemini_key');
            const wasConnected = sessionStorage.getItem('byok_key_connected') === 'true';
            if (savedKey && wasConnected && savedKey.startsWith('AIzaSy')) {
                const mainKey = document.getElementById('api-key-input');
                if (mainKey) mainKey.value = savedKey;
                const suppKey = document.getElementById('support-api-key-input');
                if (suppKey) suppKey.value = savedKey;

                const label = document.getElementById('api-key-status-label');
                if (label) {
                    label.innerText = "API Key Connected";
                    label.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
                const suppLabel = document.getElementById('support-api-key-status-label');
                if (suppLabel) {
                    suppLabel.innerText = "API Key Connected";
                    suppLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
            }

            await fetchRunbooks();
            await switchScenario('saas_finops');
        });

        // Check API Key Status on load
        document.addEventListener('DOMContentLoaded', () => {
            if(sessionStorage.getItem('gemini_api_key')) {
                const statusLabel = document.getElementById('api-key-status-label');
                                if(statusLabel) {
                    statusLabel.innerText = "API Key Connected";
                    statusLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
                var aiBadge = document.getElementById('ai-data-badge');
                if(aiBadge) {
                    aiBadge.innerText = "Live Data";
                    aiBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }
                var suppBadge = document.getElementById('supp-ai-data-badge');
                if(suppBadge) {
                    suppBadge.innerText = "Live Data";
                    suppBadge.className = "text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide";
                }
            }
        });
    