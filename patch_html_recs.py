import re

with open("static/index.html", "r") as f:
    content = f.read()

# Update the executive report recommendations header in JS
search = """                    <svg class="animate-spin h-6 w-6 text-indigo-600 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                    <p class="text-xs font-bold uppercase tracking-widest animate-pulse">Generating Dynamic AI Recommendations...</p>
                </div>
            `;

            try {"""

replace = """                    <svg class="animate-spin h-6 w-6 text-indigo-600 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
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

            try {"""

if search in content:
    content = content.replace(search, replace)
    
# Add the report-recs-badge to the HTML
header_search = """                            <span class="w-2.5 h-2.5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600"></span> 5. Gemini AI Strategic Recommendations & Next Actions
                        </h3>"""
header_replace = """                            <span class="w-2.5 h-2.5 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600"></span> 5. Gemini AI Strategic Recommendations & Next Actions
                            <span id="report-recs-badge" class="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded font-bold uppercase tracking-wide border border-amber-200 ml-2">Dummy Data</span>
                        </h3>"""

if header_search in content:
    content = content.replace(header_search, header_replace)

with open("static/index.html", "w") as f:
    f.write(content)
