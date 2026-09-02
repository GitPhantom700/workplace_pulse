# Project: WorkplacePulse Dynamic Audit, Compliance & Auto-Remediation

## Architecture
- **Framework**: FastAPI backend with async endpoints, Pydantic schemas, Uvicorn ASGI server.
- **AI Integration**: Google GenAI SDK (Gemini API) with dynamic fallback ladder, system prompt injection protection, and structured JSON output.
- **Authentication**: Firebase Admin Bearer token verification with environment-gated demo sandbox mode (`DEMO_MODE`).
- **Database & Security**: Cloud Firestore with strict multi-tenant user isolation (`/users/{userId}/forecast_logs/{logId}`) and default-deny `firestore.rules`.
- **Secret Management**: Google Cloud Secret Manager with ADC and `.env` fallback.
- **Deployment**: Google Cloud Run serverless container with dynamic `$PORT` binding and `/api/health` probe.
- **Frontend**: Single-page dashboard (`static/index.html`) with Firebase JS Auth, Chart.js, and DOMPurify sanitized markdown rendering.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Health Check API | `GET /api/health` container liveness/readiness probe | M1 | survey |
| 2 | Scenario Catalog API | `GET /api/scenarios` listing available IT/FinOps simulation presets | M1 | survey |
| 3 | Scenario Seeding API | `POST /api/scenarios/seed` generating metric time-series and incidents | M1 | survey |
| 4 | Multi-Turn AI Forecast | `POST /api/forecast/chat` authenticated Gemini forecast & runbook generation | M1 | survey |
| 5 | Firebase Token Auth | `verify_firebase_token` Bearer auth with `DEMO_MODE` environment gate | M1 | survey |
| 6 | Secret Manager Integration | Zero-hardcoding Secret Manager loader with ADC and `.env` fallback | M1 | survey |
| 7 | Firestore Multi-Tenant Storage | Write/read isolation to `/users/{userId}/forecast_logs/` | M1 | survey |
| 8 | Firestore Security Rules | Zero-trust default deny and strict `request.auth.uid == userId` | M1 | survey |
| 9 | Cloud Run Containerization | `Dockerfile` with dynamic `$PORT` binding and `.dockerignore` | M1 | survey |
| 10 | Frontend Markdown Sanitization | DOMPurify sanitization of AI responses in `static/index.html` | M1 | survey |
| 11 | CORS & Headers Hardening | Spec-compliant CORS and security headers in FastAPI | M1 | survey |
| 12 | 4-Tier Test Suite | Comprehensive unit, dynamic REST API, security, and resilience tests (118 tests) | M2 | survey |
| 13 | Forensic Integrity Audit | Systematic checks against hardcoding, dummy mocks, or bypasses | M3 | survey |
| 14 | Final QA Testing Report | Comprehensive `testing_report.md` fulfilling all acceptance criteria | M3 | survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Auto-Remediation & Hardening | Fix auth bypass, lazy secret init, CORS, DOM XSS, Dockerfile, gitignore | Survey | DONE |
| M2 | Dynamic E2E Testing Suite | Build and pass 100% of Tier 1-4 tests (dynamic HTTP status codes, security, isolation) | M1 | DONE |
| M3 | Hardening, Audit & QA Report | Adversarial verification, Forensic Audit, and `testing_report.md` generation | M2 | DONE |

## Code Layout
- `main.py` — FastAPI application entry point, routing, middleware, and lifecycle.
- `security.py` — Firebase Auth token validation, Secret Manager loader.
- `ai_service.py` — Gemini client initialization, fallback ladder, prompt schemas.
- `database.py` — Firestore client, audit logging helper.
- `data_engine.py` — IT/FinOps simulation data generator and scenario registry.
- `firestore.rules` — Declarative Firestore security and access rules.
- `Dockerfile` — Container build configuration.
- `.gitignore` & `.dockerignore` — Repository and build boundary protection.
- `static/` — Frontend assets (`index.html`).
- `tests/` — Automated test suite (Tiers 1–4 and Adversarial suites, 118 tests).
- `testing_report.md` — Final QA and compliance report.
