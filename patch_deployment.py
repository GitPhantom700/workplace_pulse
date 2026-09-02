import re

with open("/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/DEPLOYMENT.md", "r") as f:
    content = f.read()

# Add Cloud Shell clarification
prereq_search = """4.  **Docker** installed (for local container testing).

---"""

prereq_replace = """4.  **Docker** installed (for local container testing).

> **💡 Execution Tip (Terminal vs. Cloud Shell):** 
> All `gcloud` and `firebase` commands listed below can be run directly from your local terminal (macOS/Linux) if you have the SDKs installed. Alternatively, you can run them directly in the browser using the [Google Cloud Shell](https://shell.cloud.google.com/), which has all required CLIs pre-installed and automatically authenticated.

---"""

content = content.replace(prereq_search, prereq_replace)

# Add screenshots for Firebase Auth
auth_search = """4. Note your Firebase config object to place inside `static/index.html`."""
auth_replace = """4. Note your Firebase config object to place inside `static/index.html`.

![Firebase Auth Setup Screenshot](./assets/screenshots/firebase-auth-setup.png)
*(Screenshot: Firebase Console showing Google Sign-In enabled)*"""
content = content.replace(auth_search, auth_replace)

# Add screenshots for Firestore
firestore_search = """    *(See [`firestore.rules`](./firestore.rules) for the exact match criteria: `match /users/{userId}/{document=**} { allow read, write: if request.auth != null && request.auth.uid == userId; }`)*"""
firestore_replace = """    *(See [`firestore.rules`](./firestore.rules) for the exact match criteria: `match /users/{userId}/{document=**} { allow read, write: if request.auth != null && request.auth.uid == userId; }`)*

![Firestore Rules Screenshot](./assets/screenshots/firestore-rules.png)
*(Screenshot: Cloud Firestore Data and Rules dashboard)*"""
content = content.replace(firestore_search, firestore_replace)

# Add screenshots for API
api_search = """### 1. Enable Required APIs
```bash
gcloud services enable \\
    run.googleapis.com \\
    secretmanager.googleapis.com \\
    firestore.googleapis.com \\
    cloudbuild.googleapis.com
```"""
api_replace = """### 1. Enable Required APIs
You can execute these commands in your local terminal or by clicking the `>_` (Activate Cloud Shell) icon in the top right of the Google Cloud Console.

![Cloud Shell Execution Screenshot](./assets/screenshots/cloud-shell-execution.png)
*(Screenshot: Executing the gcloud API enablement command in Cloud Shell)*

```bash
gcloud services enable \\
    run.googleapis.com \\
    secretmanager.googleapis.com \\
    firestore.googleapis.com \\
    cloudbuild.googleapis.com
```"""
content = content.replace(api_search, api_replace)

# Add screenshots for Cloud Run
cloudrun_search = """    --min-instances 0 \\
    --max-instances 10
```"""
cloudrun_replace = """    --min-instances 0 \\
    --max-instances 10
```

![Cloud Run Deployment Success Screenshot](./assets/screenshots/cloud-run-success.png)
*(Screenshot: Google Cloud Run dashboard showing the healthy deployed service and active URL)*"""
content = content.replace(cloudrun_search, cloudrun_replace)

with open("/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/DEPLOYMENT.md", "w") as f:
    f.write(content)
