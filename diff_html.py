import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with urllib.request.urlopen("https://workplace-pulse-app-996129350542.us-central1.run.app/", context=ctx) as response:
        live_html = response.read().decode('utf-8')
    with open('static/index.html', 'r') as f:
        local_html = f.read()
    if live_html == local_html:
        print("HTML IS IDENTICAL")
    else:
        print("HTML IS DIFFERENT")
except Exception as e:
    print(e)
