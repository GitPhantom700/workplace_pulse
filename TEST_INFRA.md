# E2E Test Infra: WorkplacePulse

## Test Philosophy
- Opaque-box, requirement-driven. Direct dynamic simulation of API requests against running FastAPI application.
- Verification of HTTP status codes (200 OK for valid interactions, 401 Unauthorized for missing/invalid tokens, 403 Forbidden for cross-tenant violations, 422 Unprocessable Entity for invalid schemas).
- Hermetic test runners supporting local execution and CI/CD without external cloud dependencies.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|---------------------|:------:|:------:|:------:|:------:|
| 1 | Health Check API (`GET /api/health`) | R1 (Container probe) | ✓ | ✓ | ✓ | ✓ |
| 2 | Scenario Catalog (`GET /api/scenarios`) | R1 (Catalog API) | ✓ | ✓ | ✓ | ✓ |
| 3 | Scenario Seeding (`POST /api/scenarios/seed`) | R1 (Seed API) | ✓ | ✓ | ✓ | ✓ |
| 4 | Multi-Turn Forecast (`POST /api/forecast/chat`) | R1 (Gemini & Auth) | ✓ | ✓ | ✓ | ✓ |
| 5 | Firebase Token Verification | R1, R2 (Security/Auth) | ✓ | ✓ | ✓ | ✓ |
| 6 | Secret Manager Integration | R1, R2 (Secret hygiene) | ✓ | ✓ | ✓ | ✓ |
| 7 | Firestore Multi-Tenant Isolation | R1, R2 (Data isolation) | ✓ | ✓ | ✓ | ✓ |
| 8 | Firestore Security Rules | R1, R2 (Rule enforcement) | ✓ | ✓ | ✓ | ✓ |
| 9 | Cloud Run Containerization & Port Binding | R1 (Cloud Run specs) | ✓ | ✓ | ✓ | ✓ |
| 10 | Frontend DOM Sanitization | R2 (XSS protection) | ✓ | ✓ | ✓ | ✓ |

## Test Architecture & Tier Taxonomy
- **Tier 1 (Unit & Schema Tests)**: `tests/test_data_engine.py`, `tests/test_models.py`, `tests/test_ai_service.py`, `tests/test_security_unit.py`.
- **Tier 2 (Dynamic REST API & Contract Tests)**: `tests/test_api_endpoints.py` (executing live TestClient requests checking 200, 401, 403, 404, 422).
- **Tier 3 (Security & Multi-Tenant Isolation)**: `tests/test_security_compliance.py` (verifying zero hardcoded secrets, `request.auth.uid == userId` rules, auth bypass constraints, DOM sanitization).
- **Tier 4 (Cloud Run Deployment & Resilience)**: `tests/test_cloud_run_resilience.py` (verifying Dockerfile `$PORT` handling, Gemini fallback ladder under simulated 429/503 errors, graceful startup).

## Test Runner
- Invocation: `python3 -m pytest tests/ -v` or `pytest -v`
- Pass Condition: 100% tests passing, zero warnings/errors.
