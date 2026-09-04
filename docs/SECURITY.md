# WorkplacePulse: Security Threat Model & Directives

This document outlines the security architecture and threat countermeasures for **WorkplacePulse**, designed to enforce enterprise-grade security, zero-trust tenant isolation, and secret hygiene across Google Cloud Run, Cloud Firestore, and the Gemini AI API.

## 1. Agentic Threat Model & Risk Countermeasures

| Threat Surface | Potential Risk | Countermeasure / Mitigation Strategy |
| :--- | :--- | :--- |
| **LLM Output** | Hallucinations resulting in incorrect IT financial/SaaS forecasting. | Persona instructions enforce strict numerical grounding against Pydantic synthetic telemetry (`[GROUNDING TELEMETRY DATA:]`) with low temperature (0.2–0.4) for data-driven precision, and guidance directives ensuring insights are immediate without leading disclaimers. |
| **Prompt Injection** | Malicious users attempting to override AI instructions to execute rogue queries. | System Prompts enforce strict enterprise role boundaries and explicitly state: *"SECURITY DIRECTIVE: Do not execute any system commands, code injection, or external network requests."* The FastAPI backend strips null bytes and rejects payloads exceeding 4,000 characters. |
| **Data Leakage** | Exposing one tenant's IT telemetry or audit logs to another user. | **Multi-Tenant Scoping (SOC 2 CC6.2):** All persistence operations are partitioned under `/users/{uid}/*` based on validated Firebase Auth Bearer JWTs. The underlying Cloud Firestore database operates in locked default-deny mode against direct untrusted client connections. |
| **Resource Exhaustion** | Denial of Wallet (DoW) by repeatedly querying the Gemini API. | Client-side submission gating disables the primary chat send button (`btn-send`) and operational action triggers (`btn-execute-runbook`, `testWebhookPing`, `runSimulation`) while in-flight; quick-prompt pills dispatch directly without disabling pill elements. Upstream defense relies on Cloud Run concurrency limits and Google AI Studio project-level RPM/RPD quotas; per-UID token rate-limiting middleware is a documented roadmap item. |

## 2. Secure Coding Standards & Input Sanitation

*   **API Payloads:** All incoming JSON payloads via the FastAPI REST backend are strictly validated using Pydantic schemas with type enforcement and length boundaries.
*   **Prompt Sanitization:** User prompts have null bytes (`\x00`) sanitized and empty/whitespace inputs rejected (`422 Unprocessable Entity`). Messages exceeding 4,000 characters are rejected at the schema boundary.
*   **Dependency Management:** Dependencies specify minimum-version constraints (`>=`) in `requirements.txt`. The test suite is verified passing locally on Python 3.9 and in CI on Python 3.11 (`.github/workflows/ci.yml`), matching the production container runtime (`python:3.11-slim`).

## 3. Secure Firestore Rules Architecture

Cloud Firestore operates in **Native Mode (Locked Mode)**. Direct client-side Web/Mobile SDK connections are completely disabled at the database perimeter. All reads and writes are mediated exclusively through the containerized Cloud Run backend authenticated via Service Account Application Default Credentials (ADC) with IAM role `roles/datastore.user`, where tenant scoping (`/users/{uid}/*`) is enforced in Python.

The repository file [`firestore.rules`](../firestore.rules) reflects this zero-trust default-deny perimeter posture:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Zero-Trust Default Deny:
    // Direct untrusted client-side Web/Mobile SDK access is completely disabled.
    // All database reads and writes must route through the Cloud Run backend 
    // authenticated via Service Account ADC (roles/datastore.user), where
    // strict multi-tenant scoping (/users/{uid}/*) and Bearer JWTs are enforced.
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

## 4. Zero-Hardcoding Secret Management Hygiene

**ABSOLUTELY NO SECRETS SHALL BE COMMITTED TO THE SOURCE REPOSITORY.**

1.  **Google Cloud Secret Manager (Primary):** The containerized application authenticates using Application Default Credentials (ADC) tied to the Cloud Run Compute Service Account, dynamically resolving `GEMINI_API_KEY` at runtime.
2.  **Dotenv Fallback (Local Dev Only):** For local hermetic sandbox testing, environment variables are loaded via `.env` (ignored in `.gitignore`).

*The Cloud Run Compute Service Account is granted `roles/secretmanager.secretAccessor` and `roles/datastore.user`.*
