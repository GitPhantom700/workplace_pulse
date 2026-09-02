import os

with open("ai_service.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'elif any(w in msg_low for w in ["report", "pdf"' in line:
        json_logic = """
        elif "strict json format matching this schema" in msg_low:
            if "saas" in scenario_id:
                return '''{
                    "recommendations": [
                        {
                            "tag": "FinOps Policy",
                            "tagColor": "bg-emerald-50 text-emerald-700 border-emerald-200",
                            "title": "Automate Okta SCIM Role Reclassification",
                            "desc": "Reclassify 130 Figma Enterprise seats with >60d inactivity to Viewer-Restricted without disrupting file access.",
                            "impact": "+$56,400 / yr Recovered",
                            "impactColor": "text-emerald-600",
                            "actionText": "⚡ Apply SCIM Policy"
                        },
                        {
                            "tag": "Workflow Automation",
                            "tagColor": "bg-indigo-50 text-indigo-700 border-indigo-200",
                            "title": "Enforce 45-Day Inactivity Auto-Reclaim Rule",
                            "desc": "Deploy an automated Sentinel lifecycle policy to prevent seat bloat by reclaiming licenses before upcoming Q3 renewals.",
                            "impact": "Zero License Bloat",
                            "impactColor": "text-indigo-600",
                            "actionText": "⚡ Deploy Auto-Rule"
                        }
                    ]
                }'''
            elif "hardware" in scenario_id:
                return '''{
                    "recommendations": [
                        {
                            "tag": "Safety & Risk",
                            "tagColor": "bg-rose-50 text-rose-700 border-rose-200",
                            "title": "Quarantine 18 Swollen Battery Units",
                            "desc": "Lock and recall MacBook Pro 16\\" units exhibiting >800 cycle counts and thermal inflation patterns via Jamf MDM.",
                            "impact": "Critical Safety Mitigation",
                            "impactColor": "text-rose-600",
                            "actionText": "⚡ Initiate Quarantine"
                        }
                    ]
                }'''
            else:
                return '''{
                    "recommendations": [
                        {
                            "tag": "Staffing Optimization",
                            "tagColor": "bg-indigo-50 text-indigo-700 border-indigo-200",
                            "title": "Pre-Stage Tier-2 Identity Engineers",
                            "desc": "Shift 2 specialized IAM engineers to the 08:00–14:00 window to absorb the 42% Month-End close ticket surge.",
                            "impact": "Zero SLA Breaches",
                            "impactColor": "text-indigo-600",
                            "actionText": "⚡ Shift Scheduling"
                        }
                    ]
                }'''
"""
        new_lines.append(json_logic)
    new_lines.append(line)

with open("ai_service.py", "w") as f:
    f.writelines(new_lines)
