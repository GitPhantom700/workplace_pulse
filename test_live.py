import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://workplace-pulse-app-996129350542.us-central1.run.app/api/scenarios/seed", 
    data=b'{"scenario_id": "saas_finops"}', 
    headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        data = json.loads(response.read())
        for m in data.get('saas_metrics', []):
            if 'Figma' in m['app_name']:
                print("Figma seats:", m['total_licenses'])
except Exception as e:
    print(e)
