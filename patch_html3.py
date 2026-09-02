import re
with open("static/index.html", "r") as f:
    content = f.read()
    
onload_logic = """
        // Check API Key Status on load
        document.addEventListener('DOMContentLoaded', () => {
            if(sessionStorage.getItem('gemini_api_key')) {
                const statusLabel = document.getElementById('api-key-status-label');
                if(statusLabel) {
                    statusLabel.innerText = "API Key Connected";
                    statusLabel.className = "text-[10px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-bold tracking-wide";
                }
            }
        });
"""

if "Check API Key Status on load" not in content:
    content = content.replace('    </script>\n</body>', onload_logic + '    </script>\n</body>')
    with open("static/index.html", "w") as f:
        f.write(content)
