# DevOps Engineer Report — Driver Routing

_Last updated: 2026-07-30T19:00:56Z_

## Validation

Stage 7 prerequisite validation **passed** for the current evening run.

Validated:
- `workflow-status.md` marks Stage 6 QA Engineer as `completed` for the current run at `2026-07-30T18:30:40Z`.
- `reports/qa-engineer.md` exists, is current, and contains finalized QA output.
- QA explicitly reports **no blocker for Stage 7**.
- QA confirms the current artifact is a local workflow proof only and is **not pilot-ready**. Critical release blockers remain around API-level auth/RBAC/tenant isolation, durable persistence, real `.xlsx` upload parsing, manual override/audit implementation, API-backed frontend integration, live dashboard/reporting, and mobile browser verification.

## DevOps Work Completed

Updated project artifacts for the current run:

- `reports/devops-engineer.md` — refreshed Stage 7 report for 2026-07-30.
- `repo/ops/devops-runbook.md` — refreshed local-first runbook wording around Excel `.xlsx`, current verification commands, and release gates.
- `architecture.md` — refreshed DevOps/environment notes to match the current QA state and Excel-first MVP.
- `sprint-board.md` — updated DevOps task state and added operational follow-up tasks for local Compose, CI/secret scanning, and pilot readiness.
- `decisions/decision-log.md` — recorded the current local-only DevOps decision.
- `workflow-status.md` — marked Stage 7 completed for `2026-07-30T19:00:56Z`.

No deployment, GitHub push, cloud resource creation, image registry action, paid API configuration, public endpoint exposure, or production release was performed.

## Verification Performed

Executed from `repo/frontend/`:

```bash
node tests/frontend.test.js && python3 -m py_compile ../backend/app/*.py && PYTHONPATH=../backend python3 -m unittest discover -s ../backend/tests -v
```

Actual result:

```text
Frontend prototype tests passed
test_capacity_and_max_stops_constraints (test_routing_service.RoutingServiceTests.test_capacity_and_max_stops_constraints) ... ok
test_excel_template_schema_exposes_required_columns (test_routing_service.RoutingServiceTests.test_excel_template_schema_exposes_required_columns) ... ok
test_failed_requires_note (test_routing_service.RoutingServiceTests.test_failed_requires_note) ... ok
test_import_orders_from_rows_creates_ready_and_draft_rows_with_row_errors (test_routing_service.RoutingServiceTests.test_import_orders_from_rows_creates_ready_and_draft_rows_with_row_errors) ... ok
test_impossible_time_window_is_unassigned (test_routing_service.RoutingServiceTests.test_impossible_time_window_is_unassigned) ... ok
test_missing_coordinates_are_unassigned (test_routing_service.RoutingServiceTests.test_missing_coordinates_are_unassigned) ... ok
test_no_available_driver_reason (test_routing_service.RoutingServiceTests.test_no_available_driver_reason) ... ok
test_plans_and_publishes_driver_visible_route (test_routing_service.RoutingServiceTests.test_plans_and_publishes_driver_visible_route) ... ok
test_status_lifecycle_and_failure_note_validation (test_routing_service.RoutingServiceTests.test_status_lifecycle_and_failure_note_validation) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.002s

OK
```

Verification outcome: **pass for local prototype-level checks**.

## Current Local Development Strategy

The repository still contains dependency-light local prototypes, not a deployable application:

- Backend: Python in-memory domain/service/planner under `repo/backend/`.
- Frontend: static dependency-free mobile-first prototype under `repo/frontend/`.
- No FastAPI server, PostgreSQL database, migrations, React/Vite app, Docker runtime, production build, or hosted endpoint exists yet.

Recommended local commands remain:

Backend:

```bash
cd repo/backend
PYTHONPATH=. python3 -m unittest discover -s tests -v
python3 -m py_compile app/*.py
```

Frontend:

```bash
cd repo/frontend
node tests/frontend.test.js
python3 -m http.server 4173
# open http://localhost:4173 locally
```

## Docker / Dev Environment Plan

Do **not** add or run production-like deployment artifacts until the real runtime components exist. A Compose file is useful only after the project has a FastAPI entrypoint, React/Vite app, PostgreSQL schema/migrations, and health checks.

Recommended future local-only Compose services:

| Service | Purpose | MVP Notes |
|---|---|---|
| `api` | FastAPI application + route-planning service | Bind to `127.0.0.1`; expose `/health` and later `/ready`; run migrations before app start only in local/dev. |
| `web` | React/TypeScript/Vite PWA | Local dev server or static preview; no public exposure. |
| `postgres` | PostgreSQL 16/PostGIS-ready persistence | Required before pilot data; include backup/restore runbook before real use. |
| optional `osrm`/`graphhopper` | Self-hosted distance matrix/routing | Defer until resource and map-data impact are reviewed. |

No-spend defaults should remain:

```text
DISTANCE_PROVIDER=haversine
GEOCODER_PROVIDER=manual
MAPS_API_KEY=
ROUTING_API_KEY=
POLL_INTERVAL_SECONDS=15
```

## CI/CD Recommendation

CI should be added as **validation only**, not deployment, once repository workflow scope is approved for this project. Recommended checks:

1. Backend job:
   - use `uv`/isolated Python environment;
   - run unit tests;
   - run syntax/import checks.
2. Frontend job:
   - run existing static frontend test now;
   - after React/Vite scaffold, install from lockfile, run tests, and run production build.
3. Security/config job:
   - scan for committed secrets;
   - fail on non-placeholder `MAPS_API_KEY`, `ROUTING_API_KEY`, JWT secrets, database passwords, or provider tokens;
   - run dependency audit where available.
4. Container job after Dockerfiles exist:
   - build API/web images locally in CI;
   - do not push images or deploy without explicit approval.

## Hosting Recommendation — For Later Approval Only

Low-cost MVP hosting options when Emad separately approves pilot deployment:

| Option | Recommendation | Tradeoff |
|---|---|---|
| Single VPS + Docker Compose | Best low-cost controlled pilot option | Requires manual TLS, backups, monitoring, patching, and rollback discipline. |
| PaaS + managed PostgreSQL | Fastest operational setup | Likely monthly cost and vendor limits; requires approval. |
| Supabase Postgres + lightweight API host | Fast DB/admin path | Privacy/security and row-level access posture must be reviewed. |
| Cloud Run/App Runner + managed DB | More production-grade path | More setup complexity and likely higher cost. |

## Secrets, Maps/Routing API Keys, and Data Protection

- `repo/.env.example` contains placeholders only and no real secrets.
- Real secrets must never be committed.
- Paid geocoding/routing/map APIs must remain unset until Emad approves spend and provider choice.
- Keep the prototype on manual coordinates + haversine distance for no-spend validation.
- Future pilot secrets should be stored in approved hosting secret stores, not in repository files.
- Logs must avoid leaking full customer/order details, phone numbers, notes, or precise addresses unless operationally necessary.

## Logging, Monitoring, and Release Gates

Before any external pilot, implement:

- `/health` and `/ready` endpoints;
- structured API logs with request/correlation IDs;
- planning-run duration, failure, assigned/unassigned, and route-count metrics;
- dashboard polling latency/error metrics;
- status-event and publish/manual-override audit logs;
- auth failure logs without exposing customer PII;
- PostgreSQL backup/restore process and migration rollback notes;
- PII-scrubbed error reporting.

Required release gates before pilot/public exposure:

- API-level auth, RBAC, tenant scoping, and auth-bound driver route isolation implemented and tested.
- Durable PostgreSQL/PostGIS-ready persistence and Alembic migrations implemented.
- Real `.xlsx` upload parser/API, import batch persistence, and row-level validation errors implemented and tested.
- Manual assignment/reorder override, feasibility warnings, required audit note, and durable audit events implemented.
- API-backed React/Vite PWA implemented for admin and driver flows.
- Dashboard polling and daily report endpoints implemented.
- Mobile viewport/browser-level tests pass.
- No real secrets or paid API keys in source control.
- TLS, backups, logs, monitoring, and rollback steps documented for the approved environment.
- QA signs off on P0 workflow/security/privacy tests.
- Emad explicitly approves deployment/release.

## Mobile Release Constraints

- Keep MVP as a PWA first.
- Defer native iOS/Android packaging until the role-based PWA workflow is validated.
- Defer APNs/FCM push notifications until notification scope, credentials, costs, and privacy implications are approved.
- Offline route access is useful later but should not precede the API-backed PWA, auth foundation, and durable sync/status model.

### Yesterday / Completed

- Previous DevOps run created a local-first runbook and `.env.example`, and kept all work local-only.
- Today, validated current-run Stage 6 QA completion and confirmed QA reported no blocker for Stage 7.
- Re-ran real verification: frontend static test passed, backend syntax check passed, and 9 backend unit tests passed.
- Refreshed DevOps report, runbook, architecture DevOps notes, sprint-board DevOps tasks, decision log, and workflow status.
- No deployment, cloud resources, paid APIs, public exposure, native packaging, or GitHub push were performed.

### Current Progress

Stage 7 DevOps Engineer work is **completed** for the current run.

The project has a safe local-first operations plan and clear release gates. The current artifact is verified as a local workflow proof, but it remains **not deployable/pilot-ready** because the runtime is still in-memory/static and lacks API auth, persistence, real Excel upload parsing, API-backed frontend integration, monitoring, and release infrastructure.

### Next Actions

- Stage 8 Scrum Master should consolidate the evening sequence and note that Stage 7 completed without release/deployment activity.
- Backend next pass should prioritize FastAPI runtime, PostgreSQL/Alembic persistence, tenant/RBAC enforcement, auth-bound driver route isolation, real `.xlsx` parser/upload endpoint, and manual override/audit APIs.
- Frontend next pass should scaffold React/TypeScript/Vite PWA and wire import, planning, publish, status/proof, and dashboard polling to real API contracts.
- DevOps next pass should add local-only Compose only after FastAPI/React/PostgreSQL scaffolds exist, then add health checks, migration commands, secret scanning, and CI validation.
- QA next pass should expand into API integration tests, real workbook/parser tests, tenant/driver isolation tests, and browser-level mobile viewport tests.

### Risks / Blockers

- No blocker for Stage 8.
- Current artifact is not production-deployable: backend is in-memory and frontend is static.
- Critical release blockers remain: API auth/RBAC/tenant isolation, durable persistence/migrations, real Excel upload parsing, manual override auditability, API integration, mobile browser verification, dashboard/reporting, secrets management, logging/monitoring, and backups.
- Paid map/geocoding/routing APIs, public deployment, image publishing, native mobile release, and production pilot activity must not be configured or executed without Emad's explicit approval.
