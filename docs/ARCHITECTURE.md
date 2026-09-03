# 🏛️ WorkplacePulse Architecture & System Design

WorkplacePulse is an autonomous Enterprise IT Operations & Predictive FinOps Command Center deployed on Google Cloud Run.

## System Components

```
                                        +----------------------------+
                                        |       CLIENT BROWSER       |
                                        | (Tailwind UI + Chart.js)   |
                                        +--------------+-------------+
                                                       |
                          +----------------------------+----------------------------+
                          | (1. Firebase Google Auth)                               | (2. REST APIs & WebSockets)
                          v                                                         v
             +---------------------------+                             +---------------------------+
             |   Firebase Auth Service   |                             |   Cloud Run Container     |
             | (ID Token Issuance / SDK) |                             | (FastAPI Application)     |
             +-------------+-------------+                             +-------------+-------------+
                           | Bearer JWT                                              |
                           +---------------------------------------------------------+
                                                       |
        +----------------------------------------------+----------------------------------------------+
        |                                              |                                              |
        v                                              v                                              v
+-------------------------------+             +-------------------------------+             +-------------------------------+
|    Security & Auth Gate       |             |   Gemini AI Copilot Engine    |             |  Tenant Isolation & Database  |
| - Firebase Admin SDK Token    |             | - Gemini 2.5 Flash Primary    |             | - Scoped /users/{userId}/...  |
|   Verification Middleware     |             | - Gemini 2.0 Flash Fallback   |             | - Default-Deny Security Rules |
| - Cloud Secret Manager ADC    |             | - Multi-Turn Role Prompts     |             | - Immutable AI Audit Logs     |
|   Dynamic Secret Fetching     |             | - Prompt Injection Guard      |             | - Runbook Execution Logs      |
+-------------------------------+             +-------------------------------+             +-------------------------------+
```

## Security & Isolation

* **Firestore Security Rules:** Zero-trust tenant scoping under `/users/{userId}/`.
* **HMAC-SHA256 Signatures:** Webhook payloads cryptographically signed with tenant secrets.
* **BYOK Privacy:** User-supplied Gemini keys reside strictly in browser `sessionStorage`.
