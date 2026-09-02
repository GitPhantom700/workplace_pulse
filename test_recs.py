import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Create a mock JWT token or hit the endpoint if it allows without token (it requires verify_firebase_token)
# Wait, it requires a Firebase token.
