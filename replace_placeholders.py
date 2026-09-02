import re

with open("/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/DEPLOYMENT.md", "r") as f:
    content = f.read()

# 1. Firebase Auth - replace image with config example
auth_search = """4. Note your Firebase config object to place inside `static/index.html`.

![Firebase Auth Setup Screenshot](./assets/screenshots/firebase-auth-setup.png)
*(Screenshot: Firebase Console showing Google Sign-In enabled)*"""

auth_replace = """4. Note your Firebase config object to place inside `static/index.html`.

**Expected Client Config Format:**
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyYourApiKeyHere...",
  authDomain: "your-gcp-project-id.firebaseapp.com",
  projectId: "your-gcp-project-id"
};
firebase.initializeApp(firebaseConfig);
```"""
content = content.replace(auth_search, auth_replace)


# 2. Firestore Rules - replace image with terminal output
rules_search = """    *(See [`firestore.rules`](./firestore.rules) for the exact match criteria: `match /users/{userId}/{document=**} { allow read, write: if request.auth != null && request.auth.uid == userId; }`)*

![Firestore Rules Screenshot](./assets/screenshots/firestore-rules.png)
*(Screenshot: Cloud Firestore Data and Rules dashboard)*"""

rules_replace = """    *(See [`firestore.rules`](./firestore.rules) for the exact match criteria: `match /users/{userId}/{document=**} { allow read, write: if request.auth != null && request.auth.uid == userId; }`)*

    **Expected Output:**
    ```text
    === Deploying to 'your-gcp-project-id'...

    i  deploying firestore
    i  firestore: checking firestore.rules for compilation errors...
    ✔  firestore: rules file firestore.rules compiled successfully
    i  firestore: uploading rules firestore.rules...
    ✔  firestore: released rules firestore.rules to cloud.firestore

    ✔  Deploy complete!
    ```"""
content = content.replace(rules_search, rules_replace)


# 3. API Enablement - replace image with terminal output
api_search = """You can execute these commands in your local terminal or by clicking the `>_` (Activate Cloud Shell) icon in the top right of the Google Cloud Console.

![Cloud Shell Execution Screenshot](./assets/screenshots/cloud-shell-execution.png)
*(Screenshot: Executing the gcloud API enablement command in Cloud Shell)*

```bash
gcloud services enable \\
    run.googleapis.com \\
    secretmanager.googleapis.com \\
    firestore.googleapis.com \\
    cloudbuild.googleapis.com
```"""

api_replace = """You can execute these commands in your local terminal or by clicking the `>_` (Activate Cloud Shell) icon in the top right of the Google Cloud Console.

```bash
gcloud services enable \\
    run.googleapis.com \\
    secretmanager.googleapis.com \\
    firestore.googleapis.com \\
    cloudbuild.googleapis.com
```

**Expected Output:**
```text
Operation "operations/acf.p2-123456789-0000-0000-0000-000000000000" finished successfully.
```"""
content = content.replace(api_search, api_replace)


# 4. Cloud Run - replace image with terminal output
run_search = """    --max-instances 10
```

![Cloud Run Deployment Success Screenshot](./assets/screenshots/cloud-run-success.png)
*(Screenshot: Google Cloud Run dashboard showing the healthy deployed service and active URL)*"""

run_replace = """    --max-instances 10
```

**Expected Output:**
```text
Deploying container to Cloud Run service [workplacepulse-core] in project [your-gcp-project-id] region [us-central1]
✓ Deploying... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
Service [workplacepulse-core] revision [workplacepulse-core-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://workplacepulse-core-xyz-uc.a.run.app
```"""
content = content.replace(run_search, run_replace)

with open("/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/DEPLOYMENT.md", "w") as f:
    f.write(content)

