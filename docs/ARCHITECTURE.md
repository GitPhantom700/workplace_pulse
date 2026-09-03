# 🏛️ WorkplacePulse Architecture & System Design

WorkplacePulse is an autonomous Enterprise IT Operations & Predictive FinOps Command Center deployed on Google Cloud Run.

## Multi-Project Cloud Topology

The enterprise deployment spans three specialized Google Cloud / Firebase projects to enforce principle of least privilege and strict boundary segregation:

1. **Google Cloud Project `workplacepulse` (Project #`996129350542`):**
   * **Cloud Run:** Hosts the containerized FastAPI backend service (`workplace-pulse-app`) in `us-central1`.
   * **Cloud Firestore (Native Mode):** Stores tenant-isolated audit logs, runbook execution histories, and webhook registries at `projects/workplacepulse/databases/(default)`.
   * **Cloud Secret Manager:** Securely stores production secrets (`GEMINI_API_KEY`) accessed via runtime Application Default Credentials (ADC) by `996129350542-compute@developer.gserviceaccount.com`.

2. **Firebase Project `workplacepulse-dev` (Project #`872061791801`):**
   * **Firebase Authentication:** Handles enterprise Google OAuth 2.0 and Anonymous Guest identity verification, issuing signed Firebase ID tokens (JWTs).

3. **Generative Language API Key (Project #`912878440808`):**
   * Dedicated Google AI Studio key provisioned in Secret Manager for high-throughput production inference across the Gemini ladder.

---

## System Components & Model Ladder

```
                                        +----------------------------+
                                        |       CLIENT BROWSER       |
                                        | (Tailwind UI + Chart.js)   |
                                        +--------------+-------------+
                                                       |
                          +----------------------------+----------------------------+
                          | (1. Firebase Google Auth / Anonymous JWT)               | (2. REST APIs & WebSockets)
                          v                                                         v
             +---------------------------+                             +---------------------------+
             |   Firebase Auth Service   |                             |   Cloud Run Container     |
             | (workplacepulse-dev)      |                             | (workplacepulse)          |
             +-------------+-------------+                             +-------------+-------------+
                           | Bearer JWT                                              |
                           +---------------------------------------------------------+
                                                       |
        +----------------------------------------------+----------------------------------------------+
        |                                              |                                              |
        v                                              v                                              v
+-------------------------------+             +-------------------------------+             +-------------------------------+
|    Security & Auth Gate       |             |   Gemini AI Copilot Engine    |             |  Tenant Isolation & Database  |
| - Firebase Admin SDK Token    |             | - Gemini 3.6 Flash Primary    |             | - Scoped /users/{userId}/...  |
|   Verification Middleware     |             | - Flash Lite / Pro Fallbacks  |             | - Immutable Cloud Firestore   |
| - Cloud Secret Manager ADC    |             | - Vertex AI Enterprise Rung   |             | - Audit Logs & SIEM Scopes    |
|   Dynamic Secret Fetching     |             | - Multi-Turn Role Prompts     |             | - Runbook Execution Logs      |
+-------------------------------+             +-------------------------------+             +-------------------------------+
```

---

## Production Model Fallback Ladder

1. **Rung 1 (Primary GA):** `gemini-3.6-flash` (via Google AI Studio key in Secret Manager).
2. **Rung 2 (Fast Fallback):** `gemini-flash-lite-latest` (Sub-second low-latency failover).
3. **Rung 3 (Secondary Fallback):** `gemini-flash-latest`.
4. **Rung 4 (Enterprise Fallback):** `gemini-2.5-flash` (Vertex AI SDK via ADC in `us-central1`).

---

## Security, Tenancy & Compliance Attestation

* **Backend ADC Tenant Scoping (SOC 2 CC6.2):** All Firestore reads/writes are strictly scoped to `/users/{uid}/*` based on validated Firebase Bearer JWTs, creating immutable per-tenant execution ledgers.
* **HMAC-SHA256 Signatures:** Outgoing webhook payloads are cryptographically signed with tenant secrets.
* **Zero Hardcoding Guarantee (SOC 2 CC6.3):** Verified by continuous automated compliance testing. All secrets are dynamically fetched at runtime from Cloud Secret Manager.
* **BYOK Privacy:** User-supplied Gemini keys reside strictly in browser `sessionStorage` and are never persisted to disk or databases.
