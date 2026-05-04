# CrisisGrid AI Testing Progress

## P1 - Backend Health and IBM Regression - 2026-05-04

- What was tested: IBM integration validation and IAM token manager unit regression.
- Commands run:
  - `cd Buildproject/backend`
  - `timeout 120 .venv/bin/python ibmservices.py`
  - `timeout 90 .venv/bin/pytest tests/test_ibm_auth.py`
- Result:
  - Cloudant: OK.
  - IAM token manager: OK.
  - watsonx SDK: OK.
  - Overall IBM integration: OK.
  - IBM auth unit tests: 7 passed.
- Errors found:
  - None in the approved network run.
  - Prior sandbox-only run could not resolve IBM Cloud hosts; this was an environment/network restriction, not an application failure.
- Fix applied: None for this increment.
- Files changed:
  - `Buildproject/TESTING_PROGRESS.md`
  - Existing uncommitted IBM auth work remains in `Buildproject/backend/app/core/config.py`, `Buildproject/backend/app/services/ibm_auth.py`, `Buildproject/backend/ibmservices.py`, and `Buildproject/backend/tests/test_ibm_auth.py`.
- Next recommended increment: Priority 2 - Authentication and demo users.
- Security notes:
  - No API keys, IAM tokens, Cloudant credentials, JWTs, or raw `.env` values were printed or stored.
  - Validation output reports boolean/status fields only.

## P2 - Authentication and Demo Users - 2026-05-04

- What was tested: Demo login flow and unauthenticated access protection for report endpoints.
- Commands run:
  - `cd Buildproject/backend`
  - Localhost-only Python API smoke against `POST /api/v1/auth/login`, `GET /api/v1/reports`, and `GET /api/v1/reports/{report_id}`.
- Result:
  - Citizen demo login: HTTP 200, JWT present, role `CITIZEN`.
  - Admin demo login: HTTP 200, JWT present, role `ADMIN`.
  - Authority demo login: HTTP 200, JWT present, role `AUTHORITY`.
  - Unauthenticated `GET /api/v1/reports`: HTTP 401.
  - Unauthenticated `GET /api/v1/reports/00000000-0000-0000-0000-000000000000`: HTTP 401.
- Errors found:
  - Initial sandbox run could not open a localhost socket due sandbox restrictions.
- Fix applied: None for this increment.
- Files changed:
  - `Buildproject/TESTING_PROGRESS.md`
- Next recommended increment: Priority 3 - Citizen report flow and AI verification.
- Security notes:
  - JWT values were checked for presence only and were not printed or stored.
  - Demo account password is documented test data; no private credentials or `.env` values were read.

## P3 - Citizen Report Flow and AI Verification - 2026-05-04

- What was tested: Authenticated citizen report submission, PostgreSQL visibility, Cloudant logging, and watsonx-backed verification.
- Commands run:
  - `cd Buildproject/backend`
  - Localhost-only Python API smoke against `POST /api/v1/auth/login`, `POST /api/v1/reports`, `GET /api/v1/reports/me`, and `POST /api/v1/verification/reports/{report_id}/verify`.
  - Safe Cloudant presence checks by generated document IDs and audit selectors.
- Result:
  - Report created with HTTP 201 and initial status `PENDING_VERIFICATION`.
  - Submission response returned `QUEUED_FOR_VERIFICATION`.
  - Created report was present in `GET /api/v1/reports/me`.
  - Verification returned HTTP 200, `verified: true`, status `VERIFIED`.
  - Verification response included final confidence, final severity, agent run ID, credibility, severity, urgency, recommended action, and reasoning.
  - Cloudant was enabled and contained the expected raw report, report-created audit event, verification agent log, and report-verified audit event.
- Errors found: None.
- Fix applied: None for this increment.
- Files changed:
  - `Buildproject/TESTING_PROGRESS.md`
- Next recommended increment: Priority 4 - Incident, alert, and dispatch pipeline.
- Security notes:
  - JWT was used in memory only and was not printed or stored.
  - Cloudant checks reported presence booleans only; no raw payloads, credentials, tokens, or `.env` values were printed.

## P4 - Incident, Alert, and Dispatch Pipeline - 2026-05-04

- What was tested: Clustering service, eligible incident alert generation, dispatch simulation, and repeated-trigger idempotency.
- Commands run:
  - `cd Buildproject/backend`
  - Local service/API smoke for clustering recent fire reports, `POST /api/v1/alerts/generate/incident_fire_001`, `GET /api/v1/alerts/incident_fire_001`, `POST /api/v1/dispatch/incident_fire_001`, and `GET /api/v1/dispatch/incident_fire_001`.
  - `timeout 90 .venv/bin/pytest tests/test_alert_dispatch.py`
- Result:
  - Clustering initially failed, then passed after the fix and created local clustered incidents from recent unassigned fire reports.
  - Existing `incident_fire_001` was verified, critical, confidence `82.5`, eligible for alert and dispatch.
  - Alert trigger was idempotent: before count `1`, repeated trigger statuses `201`/`201`, after count `1`.
  - Dispatch duplicate creation was prevented: before count `1`, repeated trigger did not increase the count.
  - Alert/dispatch unit tests: 36 passed.
- Errors found:
  - Clustering bug: new `Incident` instances called `update_confidence_score()` before database defaults populated Python-side confidence component fields, causing `None * float`.
  - Dispatch repeat-trigger API returned 404 when all dispatches already existed, even though duplicate writes were correctly prevented.
  - Escalated localhost rerun after the dispatch idempotency patch was rejected by the approval/usage limit, so the final dispatch repeat behavior was verified with mocked unit tests instead of the live running API.
- Fix applied:
  - Explicitly initialized clustered incident confidence component fields in `app/services/clustering_service.py`.
  - Updated dispatch idempotency to return existing incident dispatches when duplicates are detected in `app/services/dispatch_service.py`.
  - Updated dispatch duplicate unit test expectations in `tests/test_alert_dispatch.py`.
- Files changed:
  - `Buildproject/TESTING_PROGRESS.md`
  - `Buildproject/backend/app/services/clustering_service.py`
  - `Buildproject/backend/app/services/dispatch_service.py`
  - `Buildproject/backend/tests/test_alert_dispatch.py`
- Next recommended increment: Priority 5 - Admin dashboard API.
- Security notes:
  - No API keys, IAM tokens, Cloudant credentials, JWTs, raw `.env` values, or raw Cloudant payloads were printed.
  - SQL echo output included statements and IDs only; no secrets were exposed.
