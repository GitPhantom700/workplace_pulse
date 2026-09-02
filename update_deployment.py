import re

ws_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/DEPLOYMENT.md'
art_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/DEPLOYMENT.md'

with open(ws_path, 'r') as f:
    content = f.read()

# The new Phase 1 content for workspace
new_phase1_ws = """### 1. Initialize the Project
Create a new project in the [Firebase Console](https://console.firebase.google.com/) (which automatically provisions a GCP project).

1. Enter your project name and click Continue.
2. Review the AI assistance screen and leave "Enable Gemini" checked.
![Enable Gemini in Firebase](./assets/screenshots/firebase-enable-gemini.png)
3. Accept the Google Analytics terms and click **Create project**.
![Configure Analytics](./assets/screenshots/firebase-analytics.png)
4. Once created, you will land on the Firebase Dashboard.
![Firebase Dashboard Overview](./assets/screenshots/firebase-dashboard-redacted.png)

```bash
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID
```

### 2. Configure Firebase Authentication
1. Navigate to **Authentication** in the Firebase Console (via the Build menu).
2. Click **Get Started** -> **Sign-in method**.
![Sign-in Methods](./assets/screenshots/firebase-auth-methods.png)
3. Select **Google** from the Additional Providers list.
![Enable Google Auth](./assets/screenshots/firebase-auth-google.png)
4. Toggle it to **Enable**, select your project support email, and click **Save**.
![Save Google Auth](./assets/screenshots/firebase-auth-save.png)
5. Verify that Google is now listed as **Enabled** in your Sign-in providers list.
![Google Auth Enabled](./assets/screenshots/firebase-auth-enabled.png)

### 3. Register the Web App and Configure the SDK
1. Click the **`</>` (Web)** icon on the Project Overview dashboard to register your app.
![Register Web App](./assets/screenshots/firebase-register.png)
2. Enter an App nickname (e.g., "My web app") and click **Register app**.
3. Note your Firebase config object to place inside `static/index.html`.
![Firebase Configuration SDK](./assets/screenshots/firebase-config.png)

**Expected Client Config Format:**
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyYourApiKeyHere...",
  authDomain: "your-gcp-project-id.firebaseapp.com",
  projectId: "your-gcp-project-id"
};
firebase.initializeApp(firebaseConfig);
```"""

# Replace in content
pattern = r"### 1\. Initialize the Project.*?```javascript.*?firebase\.initializeApp\(firebaseConfig\);\n```"
new_content_ws = re.sub(pattern, new_phase1_ws, content, flags=re.DOTALL)

with open(ws_path, 'w') as f:
    f.write(new_content_ws)

# Now for the Artifact version (needs absolute paths)
new_phase1_art = new_phase1_ws.replace('./assets/screenshots/', '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/')

with open(art_path, 'r') as f:
    art_content = f.read()

new_content_art = re.sub(pattern, new_phase1_art, art_content, flags=re.DOTALL)
with open(art_path, 'w') as f:
    f.write(new_content_art)

print("Updated DEPLOYMENT.md in both locations.")
