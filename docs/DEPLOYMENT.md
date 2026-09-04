# WorkplacePulse Deployment Guide

This document outlines the end-to-end deployment process for **WorkplacePulse Sentinel Core**. The platform is deployed as a serverless container on **Google Cloud Run**, utilizing **Cloud Firestore** for state management and **Google Cloud Secret Manager** for secure credentials.

---

## 🏗️ Architecture Overview

*   **Compute:** Google Cloud Run (Fully managed, autoscaling container)
*   **Database:** Cloud Firestore (Native mode, document-based NoSQL in Locked Mode)
*   **Identity:** Firebase Authentication (Google Sign-In / Anonymous Auth JWTs)
*   **Security:** Google Cloud Secret Manager & Firestore Locked Perimeter Posture
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
3.  **Docker** (optional, for local container testing).
4.  **Python 3.9+** (for local development and testing; Python 3.11 matches the production container).

> **💡 Execution Tip (Terminal vs. Cloud Shell):** 
> All `gcloud` commands listed below can be run directly from your local terminal (macOS/Linux) if you have the SDK installed, or inside the [Google Cloud Shell](https://shell.cloud.google.com/) where `gcloud` is pre-installed and pre-authenticated. (Note: Firebase Authentication is configured in the Firebase Web Console, and Cloud Firestore operates in Native Locked Mode, so no Firebase CLI installation is required.)

---

## 🚀 Phase 1: Firebase & IAM Setup

### 1. Initialize the Project
Create a new project in the [Firebase Console](https://console.firebase.google.com/) (which automatically provisions a linked GCP project).

1. Enter your project name and click **Continue**.
2. Review the AI assistance screen and leave "Enable Gemini" checked.
3. Accept the Google Analytics terms and click **Create project**.
4. Once created, you will land on the Firebase Dashboard.

```bash
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID
```

### 2. Configure Firebase Authentication
1. Navigate to **Authentication** in the Firebase Console (via the Build menu).
2. Click **Get Started** -> **Sign-in method**.
3. Enable **Google** from the provider list, select your project support email, and click **Save**.
4. Enable **Anonymous** sign-in from the provider list to support guest evaluation.
5. Verify that both **Google** and **Anonymous** are listed as **Enabled** in your Sign-in providers list.

### 3. Register the Web App and Configure the SDK
1. Click the **`</>` (Web)** icon on the Project Overview dashboard to register your app.
2. Enter an App nickname (e.g., "WorkplacePulse Web") and click **Register app**.
3. Note your Firebase config object to place inside `static/index.html`.

**Expected Client Config Format:**
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyYourApiKeyHere...",
  authDomain: "your-firebase-project-id.firebaseapp.com",
  projectId: "your-firebase-project-id"
};
firebase.initializeApp(firebaseConfig);
```

### 4. Provision Cloud Firestore
1. Navigate to **Firestore Database** in the Firebase or Google Cloud Console.
2. Click **Create Database** (Start in **Production mode / Native mode**).
3. **Perimeter Security Posture:**
   When created in Production mode, Cloud Firestore defaults to Locked Mode (rejecting direct client-side Web/Mobile SDK connections). All application reads and writes are mediated exclusively through the containerized Cloud Run backend via Service Account Application Default Credentials (ADC) with IAM role `roles/datastore.user`. Multi-tenant scoping (`/users/{uid}/*`) and audit logging are strictly enforced at the application tier upon validating the Firebase Bearer JWT. The [`firestore.rules`](../firestore.rules) file in this repository documents this zero-trust default-deny perimeter posture.

---

## 🔐 Phase 2: Google Cloud Services & Secret Manager

### 1. Enable Required APIs
You can execute these commands in your local terminal or in Google Cloud Shell:

```bash
gcloud services enable \
    run.googleapis.com \
    secretmanager.googleapis.com \
    firestore.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com
```

**Expected Output:**
```text
Operation "operations/acf.p2-123456789-0000-0000-0000-000000000000" finished successfully.
```

### 2. Configure Secret Manager (Server-Side Gemini Fallback)
While the frontend supports a BYOK (Bring Your Own Key) model, the backend resolves a server-side Gemini API key for smart simulations and system-level forecasting:

```bash
# Create the secret
gcloud secrets create GEMINI_API_KEY --replication-policy="automatic"

# Add the secret value
echo -n "YOUR_GOOGLE_AI_STUDIO_API_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
```

### 3. Configure Runtime IAM Permissions
Grant the Cloud Run Compute Service Account access to Secret Manager and Cloud Firestore:

```bash
PROJECT_NUM=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Grant Secret Manager Secret Accessor
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Grant Datastore / Cloud Firestore User Access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
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
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --max-instances 10 \
    --set-env-vars ENV=production,DEMO_MODE=false,GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
    --labels dev-tutorial=cloud-run-ai-challenge
```

**Expected Output:**
```text
Deploying container to Cloud Run service [workplace-pulse-app] in project [workplacepulse] region [us-central1]
✓ Deploying... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
Done.
Service [workplace-pulse-app] revision [workplace-pulse-app-XXXXX-XXX] has been deployed and is serving 100 percent of traffic.
Service URL: https://workplace-pulse-app-996129350542.us-central1.run.app
```

### Deployment Flags Explained:
*   `--source .`: Utilizes Google Cloud Build / Dockerfile (`python:3.11-slim`) to containerize the app.
*   `--set-env-vars ENV=production,DEMO_MODE=false,GOOGLE_CLOUD_PROJECT=$PROJECT_ID`: Enables production runtime mode with ADC resolution for Secret Manager and Firestore.
*   `--labels dev-tutorial=cloud-run-ai-challenge`: Labels revision for GenAI Academy challenge compliance.
*   `--allow-unauthenticated`: Exposes the frontend to the public web (Security is handled at the application layer via Firebase JWTs).
*   **Runtime Secret Resolution vs. Static Env Injection:** We intentionally omit `--set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest`. Rather than injecting the secret statically into process environment memory, `security.py` resolves credentials dynamically at runtime via ADC using `SecretManagerServiceClient().access_secret_version()`. This generates immutable `AccessSecretVersion` audit records in Cloud Audit Logs on every resolution, validating Attestation #4 (Enterprise Secret Hygiene).

---

## 🧪 Phase 5: Post-Deployment Verification

1.  **Access the URL:** Navigate to the Service URL provided in the terminal output.
2.  **Health Check:** Append `/api/health` to the URL. You should receive a healthy JSON response:
    ```json
    {
      "status": "healthy",
      "service": "WorkplacePulse",
      "timestamp": "2026-09-04T05:42:00.000000+00:00",
      "environment": "production"
    }
    ```
3.  **Authentication Test:** Click **Sign in with Google** (or **Continue as Guest**) in the top header to verify Firebase OAuth / Anonymous JWT token issuance.
4.  **AI Copilot Test:** Verify the Gemini Copilot header displays active status badges (e.g., **Synthetic data** • **Server key** • **gemini-3.5-flash-lite**), click a prompt pill or submit a query to verify live AI inference, and optionally expand the BYOK drawer to test with a personal Google AI Studio key.

---

## 🛠️ Troubleshooting

| Issue | Root Cause | Remediation |
| :--- | :--- | :--- |
| **HTTP 401 Unauthorized** | Invalid Firebase JWT Token | Ensure `firebase-admin` is initialized correctly and the client is passing `Authorization: Bearer <token>`. |
| **HTTP 403 Forbidden** | Service Account missing IAM role | Run the `add-iam-policy-binding` command for `roles/datastore.user`. |
| **HTTP 500 on Chatbot** | Missing Gemini API Key | Verify the secret is created in Secret Manager (`GEMINI_API_KEY`) or a BYOK key is provided. |
| **Logs missing in Terminal UI** | Streaming / Network Timeout | Cloud Run enforces a 60-minute request timeout. Ensure streaming responses yield regularly. |

