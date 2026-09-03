# WorkplacePulse Deployment Guide

This document outlines the end-to-end deployment process for **WorkplacePulse Sentinel Core**. The platform is designed to be deployed as a serverless container on **Google Cloud Run**, utilizing **Cloud Firestore** for state management and **Google Cloud Secret Manager** for secure credentials.

---

## 🏗️ Architecture Overview

*   **Compute:** Google Cloud Run (Fully managed, autoscaling container)
*   **Database:** Cloud Firestore (Native mode, document-based NoSQL)
*   **Identity:** Firebase Authentication (Google Sign-In / OAuth 2.0)
*   **Security:** Google Cloud Secret Manager & Firestore Security Rules
*   **Framework:** FastAPI (Python 3.11) + Vanilla HTML/TailwindCSS (Frontend)

---

## 📋 Prerequisites

Before beginning, ensure you have the following tools and permissions:

1.  **Google Cloud Platform (GCP) Account** with Billing Enabled.
2.  **Google Cloud SDK (`gcloud`)** installed and authenticated:
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
3.  **Firebase CLI** installed:
    ```bash
    npm install -g firebase-tools
    firebase login
    ```
4.  **Docker** installed (for local container testing).

> **💡 Execution Tip (Terminal vs. Cloud Shell):** 
> All `gcloud` and `firebase` commands listed below can be run directly from your local terminal (macOS/Linux) if you have the SDKs installed. Alternatively, you can run them directly in the browser using the [Google Cloud Shell](https://shell.cloud.google.com/), which has all required CLIs pre-installed and automatically authenticated.

---

## 🚀 Phase 1: Firebase & IAM Setup

### 1. Initialize the Project
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
![Save Google Auth](./assets/screenshots/firebase-auth-save-redacted-v4.png)
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
```

### 3. Provision Cloud Firestore
1. Navigate to **Firestore Database** in the Firebase Console.
2. Click **Create Database** (Start in **Production mode**).
3. Deploy the Multi-Tenant Security Rules to prevent cross-tenant data leakage:
    ```bash
    firebase deploy --only firestore:rules
    ```
    *(See [`firestore.rules`](./firestore.rules) for the exact match criteria: `match /users/{userId}/{document=**} { allow read, write: if request.auth != null && request.auth.uid == userId; }`)*

    **Expected Output:**
    ```text
    === Deploying to 'your-gcp-project-id'...

    i  deploying firestore
    i  firestore: checking firestore.rules for compilation errors...
    ✔  firestore: rules file firestore.rules compiled successfully
    i  firestore: uploading rules firestore.rules...
    ✔  firestore: released rules firestore.rules to cloud.firestore

    ✔  Deploy complete!
    ```

---

## 🔐 Phase 2: Google Cloud Services & Secret Manager

### 1. Enable Required APIs
You can execute these commands in your local terminal or by clicking the `>_` (Activate Cloud Shell) icon in the top right of the Google Cloud Console.

```bash
gcloud services enable \
    run.googleapis.com \
    secretmanager.googleapis.com \
    firestore.googleapis.com \
    cloudbuild.googleapis.com
```

**Expected Output:**
```text
Operation "operations/acf.p2-123456789-0000-0000-0000-000000000000" finished successfully.
```

### 2. Configure Secret Manager (Server-Side Gemini Fallback)
While the frontend supports a BYOK (Bring Your Own Key) model, the backend requires a fallback Gemini API key for smart simulations and system-level batch processing.

```bash
# Create the secret
gcloud secrets create GEMINI_API_KEY --replication-policy="automatic"

# Add the secret value
echo -n "your-gemini-1.5-pro-key" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
```

### 3. Configure the Runtime Service Account
Create a dedicated Service Account for Cloud Run to enforce Principle of Least Privilege (PoLP).

```bash
# Create Service Account
gcloud iam service-accounts create workplacepulse-sa \
    --display-name="WorkplacePulse Runtime SA"

# Grant Secret Manager Access
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
    --member="serviceAccount:workplacepulse-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Grant Datastore/Firestore Access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:workplacepulse-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/datastore.user"
```

---

## 💻 Phase 3: Local Development (Optional)

To test the application locally before deploying to Cloud Run:

```bash
# 1. Create Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Set Local Environment Variables
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
export GEMINI_API_KEY="your-local-key" # Only if not using Application Default Credentials

# 4. Run the Uvicorn Server
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
Navigate to `http://localhost:8080` to verify the frontend loads.

---

## ☁️ Phase 4: Cloud Run Deployment

Deploy the application as an autoscaling serverless container. Cloud Build will automatically containerize the FastAPI app using the provided `Dockerfile`.

```bash
gcloud run deploy workplace-pulse-app \
    --source . \
    --region us-central1 \
    --project workplacepulse \
    --set-env-vars ENV=production \
    --update-labels dev-tutorial=cloud-run-ai-challenge \
    --allow-unauthenticated
```

> **Note on Service Account:** In production, the default Compute Service Account (`996129350542-compute@developer.gserviceaccount.com`) is granted `roles/secretmanager.secretAccessor` and `roles/datastore.user` to automatically resolve secrets and write to Cloud Firestore via ADC.

**Expected Output:**
```text
Deploying container to Cloud Run service [workplace-pulse-app] in project [workplacepulse] region [us-central1]
✓ Deploying... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
Done.
Service [workplace-pulse-app] revision [workplace-pulse-app-00024-lm4] has been deployed and is serving 100 percent of traffic.
Service URL: https://workplace-pulse-app-996129350542.us-central1.run.app
```

### Deployment Flags Explained:
*   `--source .`: Utilizes Google Cloud Buildpacks/Dockerfile to containerize the app.
*   `--set-env-vars ENV=production`: Enables runtime ADC resolution for Secret Manager and Firestore.
*   `--update-labels dev-tutorial=cloud-run-ai-challenge`: Labels revision for GenAI Academy challenge compliance.
*   `--allow-unauthenticated`: Exposes the frontend to the public web (Security is handled at the application layer via Firebase JWTs).

---

## 🧪 Phase 5: Post-Deployment Verification

1.  **Access the URL:** Navigate to the Service URL provided in the terminal output.
2.  **Health Check:** Append `/api/health` to the URL. You should receive a `{"status":"ok","version":"1.0.0"}` response.
3.  **Authentication Test:** Click the "Sign In" button on the web interface to verify Firebase OAuth flow.
4.  **AI Connectivity Test:** Navigate to **Data Sources**, open the **Gemini Copilot** settings, input an API Key (BYOK), and verify the "Live Data" badge appears and the chatbot responds contextually.

---

## 🛠️ Troubleshooting

| Issue | Root Cause | Remediation |
| :--- | :--- | :--- |
| **HTTP 401 Unauthorized** | Invalid Firebase JWT Token | Ensure `firebase-admin` is initialized correctly and the client is passing `Authorization: Bearer <token>`. |
| **HTTP 403 Forbidden** | Service Account missing IAM role | Run the `add-iam-policy-binding` command for `roles/datastore.user`. |
| **HTTP 500 on Chatbot** | Missing Gemini API Key | Verify the secret is correctly mounted in Cloud Run (`--set-secrets`) or a BYOK key is provided. |
| **Logs missing in Terminal UI** | Websocket/SSE Timeout | Cloud Run enforces a 60-minute request timeout. Ensure streaming responses yield regularly. |
