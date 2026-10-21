# 🏛️ WorkplacePulse Architecture & System Design

WorkplacePulse is an autonomous Enterprise IT Operations & Predictive FinOps Command Center deployed on Google Cloud Run.

## Cloud Topology

The deployment runs in a single Google Cloud project, `workplace-pulse-ch2026` (Project #`269979669794`), with Firebase attached to the same project so that ID tokens and the backend share one audience:

1. **Cloud Run:** Hosts the containerized FastAPI backend service (`workplace-pulse-app`) in `us-central1`.
2. **Cloud Firestore (Native Mode):** Stores tenant-isolated audit logs, runbook execution histories, and webhook registries at `projects/workplace-pulse-ch2026/databases/(default)`.
3. **Cloud Secret Manager:** Stores production secrets (`GEMINI_API_KEY`), read at runtime via Application Default Credentials (ADC) by `269979669794-compute@developer.gserviceaccount.com`.
4. **Firebase Authentication:** Handles Google OAuth 2.0 and Anonymous Guest identity verification, issuing signed Firebase ID tokens (JWTs).

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
             | (workplace-pulse-ch2026)  |                             | (workplace-pulse-ch2026)  |
             +-------------+-------------+                             +-------------+-------------+
                           | Bearer JWT                                              |
                           +---------------------------------------------------------+
                                                       |
        +----------------------------------------------+----------------------------------------------+
        |                                              |                                              |
        v                                              v                                              v
+-------------------------------+             +-------------------------------+             +-------------------------------+
|    Security & Auth Gate       |             |   Gemini AI Copilot Engine    |             |  Tenant Isolation & Database  |
| - Firebase Admin SDK Token    |             | - Gemini 3.5 Flash Lite (1st) |             | - Scoped /users/{userId}/...  |
|   Verification Middleware     |             | - 3.6 Flash / Flash Fallbacks |             | - Append-only Cloud Firestore |
| - Cloud Secret Manager ADC    |             | - Vertex AI Enterprise Rung   |             | - Audit Logs & SIEM Scopes    |
|   Dynamic Secret Fetching     |             | - Multi-Turn Role Prompts     |             | - Runbook Execution Logs      |
+-------------------------------+             +-------------------------------+             +-------------------------------+
```

---

## Production Model Fallback Ladder

Rungs are ordered by free-tier daily request headroom (RPD), not by model capability.

1. **Rung 1 (Primary):** `gemini-3.5-flash-lite` (via Google AI Studio key in Secret Manager) — highest free-tier headroom at 500 RPD.
2. **Rung 2 (Fast Fallback):** `gemini-flash-lite-latest` (same model family via moving alias).
3. **Rung 3 (Secondary Fallback):** `gemini-flash-latest`.
4. **Rung 4 (Capability Rung):** `gemini-3.6-flash` — placed last because its free-tier quota is 20 RPD; resets at midnight Pacific.
5. **Rung 5 (Enterprise Fallback):** `gemini-2.5-flash` (Vertex AI SDK via ADC in `us-central1`) — no free-tier request cap.

If every live rung is exhausted, the service returns a deterministic simulation response grounded in `data_engine.py` rather than failing.

---

## Security, Tenancy & Compliance Attestation

* **Backend ADC Tenant Scoping (SOC 2 CC6.2):** All Firestore reads/writes are strictly scoped to `/users/{uid}/*` based on validated Firebase Bearer JWTs, creating append-only per-tenant execution ledgers.
* **HMAC-SHA256 Signatures:** Outgoing webhook payloads are cryptographically signed with tenant secrets.
* **Zero Hardcoding Guarantee (SOC 2 CC6.3):** Verified by continuous automated compliance testing. All secrets are dynamically fetched at runtime from Cloud Secret Manager.
* **BYOK Privacy:** User-supplied Gemini keys reside strictly in browser `sessionStorage` and are never persisted to disk or databases.
