# Sprint Board — Driver Order Routing App

_Last updated: 2026-07-30T19:30:00Z by Evening Stage 8 — Scrum Master_

## Sprint Goal
Define and prepare the MVP for a mobile-first driver/order assignment and route optimization product, then build a thin prototype that proves the core planning-to-driver-execution workflow.

## Priority Legend
- P0: Required for MVP workflow validation.
- P1: Important for pilot readiness.
- P2: Post-MVP / later enhancement.

| ID | Task | Owner | Status | Priority | Notes |
|---|---|---|---|---|---|
| DRV-INIT-1 | Research target market, competitors, optimization options, and MVP opportunity | Innovation Lead | done | P0 | Completed Stage 1; outputs in `research.md` and `reports/innovation-lead.md`. |
| DRV-PO-1 | Validate Stage 1 completion and convert research into MVP scope | Product Owner | done | P0 | Stage 1 completed for 2026-07-30; backlog/report refreshed around retailer-delivery subcontractor pilot. |
| DRV-PO-2 | Define MVP roles and permissions | Product Owner | done | P0 | Admin/Dispatcher, Driver, optional Order Owner/Customer Service. |
| DRV-PO-3 | Define order and driver input fields | Product Owner | done | P0 | Captured in `product-backlog.md`. |
| DRV-PO-4 | Define status lifecycle and core workflow | Product Owner | done | P0 | Draft through delivered/failed/returned; driver/admin lifecycle documented. |
| DRV-PO-5 | Define Excel import schema and row-level validation error model | Product Owner | done | P0 | Added default `.xlsx` order schema, required/optional columns, and import error codes to `product-backlog.md`. |
| DRV-PO-6 | Define personas and mobile UX requirements | Product Owner | done | P0 | Added Admin/Owner, Dispatcher, Driver, and Retailer/Order Owner personas plus mobile-first UX constraints. |
| DRV-PO-7 | Define MVP optimization configuration choices | Product Owner | done | P0 | Added shortest-distance, on-time, balanced-workload, strict-constraints, and relaxed/manual-review options. |
| DRV-TL-1 | Choose MVP technical architecture and prototype stack | Technical Lead | done | P0 | Completed 2026-07-29; single React/TypeScript PWA + FastAPI + PostgreSQL/PostGIS-ready architecture documented in `architecture.md`. |
| DRV-TL-2 | Define route optimization technical approach | Technical Lead | done | P0 | Completed 2026-07-29; greedy heuristic first, OR-Tools VRP behind planner interface next; distance/time matrix provider abstraction defined. |
| DRV-TL-3 | Define data model and API contracts | Technical Lead | done | P0 | Completed 2026-07-29; orders, drivers, planning runs, routes, route stops, unassigned orders, status events, and audit events defined. |
| DRV-TL-4 | Define geocoding/address handling strategy for prototype | Technical Lead | done | P0 | Completed 2026-07-29; coordinates-first/manual fallback and no-spend provider abstraction recommended. |
| DRV-TL-5 | Refresh architecture after current Product Owner handoff | Technical Lead | done | P0 | Completed 2026-07-30; validated Stage 2, superseded earlier blocked Stage 3, added Excel import/API/data-model/tenant-scope technical handoff and downstream tasks. |
| DRV-BE-1 | Implement order CRUD and validation | Backend Developer | in progress | P0 | Prototype service supports create/list-ready in memory with validation and draft/ready states in `repo/backend/app/service.py`; FastAPI wrapper and durable DB still needed. |
| DRV-BE-2 | Implement driver CRUD, availability, shifts, capacity/max stops | Backend Developer | in progress | P0 | Prototype service supports driver create/validation/availability constraints in memory; FastAPI wrapper and durable DB still needed. |
| DRV-BE-3 | Implement optimization endpoint and assignment persistence | Backend Developer | in progress | P0 | Greedy planner and in-memory planning run/route/stop/unassigned persistence implemented; API wrapper and PostgreSQL persistence remain. |
| DRV-BE-4 | Implement status lifecycle events and audit trail | Backend Developer | in progress | P0 | Status lifecycle events implemented in memory with proof/failure note validation; durable audit trail remains. |
| DRV-FE-1 | Build admin mobile-first order/driver management views | Frontend Developer | in progress | P0 | Static responsive prototype implemented in `repo/frontend/`; API integration pending. |
| DRV-FE-2 | Build admin route review, exception queue, and publish flow | Frontend Developer | in progress | P0 | Prototype includes plan review cards, unassigned reason queue, run/publish/manual override controls; real API/manual override persistence pending. |
| DRV-FE-3 | Build driver mobile route list and stop detail views | Frontend Developer | in progress | P0 | Prototype includes phone-frame route list, next-stop highlight, navigation handoff, and status action buttons; backend API integration pending. |
| DRV-FE-4 | Build proof/failure capture UI | Frontend Developer | in progress | P1 | Prototype includes proof/failure note field placeholder; photo/signature deferred. |
| DRV-QA-1 | Create acceptance test plan from MVP user stories | QA Engineer | backlog | P0 | Cover role access, validation, optimization, status lifecycle, and mobile UX. |
| DRV-QA-2 | Test route feasibility edge cases | QA Engineer | backlog | P0 | Missing address, impossible time window, unavailable driver, over capacity, shift conflict. |
| DRV-DEVOPS-1 | Define local/dev run instructions and environment boundaries | DevOps Engineer | done | P1 | Completed Stage 7; runbook added in `repo/ops/devops-runbook.md`; no deployment/production release without Emad approval. |
| DRV-SM-1 | Consolidate daily outputs and blockers | Scrum Master | done | P1 | Completed current Stage 8 on 2026-07-30; consolidated evening sequence, sprint health, blockers, decisions, and next priorities in `reports/daily-scrum.md`. |

## Technical Implementation Tasks — Added by Stage 3

| ID | Source Story | Task | Owner | Priority | Status | Dependencies / Notes |
|---|---|---|---|---|---|---|
| DRV-BE-5 | DRV-US-001/002/003 | Create backend domain models and validation services for orders, geocode status, draft/ready states, and row-level import errors | Backend Developer | P0 | partial | Domain model and validation implemented in `repo/backend/app/domain.py`; row-level CSV import still pending. |
| DRV-BE-6 | DRV-US-004/005 | Create driver model/API with shift windows, availability, max stops/capacity, and start/current coordinates | Backend Developer | P0 | partial | Driver domain validation and planning exclusion implemented; FastAPI API wrapper pending. |
| DRV-BE-7 | DRV-US-006/007 | Implement `DistanceMatrixProvider` interface and no-spend coordinate-based prototype matrix | Backend Developer | P0 | done | Haversine distance and travel-time estimate implemented with no paid API dependency. |
| DRV-BE-8 | DRV-US-006/007 | Implement deterministic greedy route planner with feasibility checks and unassigned reason codes | Backend Developer | P0 | done | Implemented in `repo/backend/app/planner.py` and covered by unit tests. |
| DRV-BE-9 | DRV-US-008/009/010 | Persist planning runs, routes, route stops, manual overrides, validation warnings, and publish state | Backend Developer | P0 | partial | In-memory planning persistence and publish gating implemented; manual overrides and database persistence pending. |
| DRV-BE-10 | DRV-US-013/014/019 | Implement status event lifecycle, proof/failure note fields, and audit trail | Backend Developer | P0 | partial | In-memory status lifecycle/proof/failure events implemented; durable audit table pending. |
| DRV-BE-11 | DRV-US-015/016/017 | Implement admin dispatch dashboard and daily summary endpoints | Backend Developer | P1 | partial | In-memory dispatch dashboard summary implemented; daily report/export endpoint pending. |
| DRV-FE-5 | DRV-US-001/004/005 | Build mobile-first admin forms/lists for orders and drivers | Frontend Developer | P0 | partial | Static admin order/driver forms and mobile responsive layout implemented in `repo/frontend/`; Stage 5 added Excel import-first intake path. Backend submission/validation wiring pending. |
| DRV-FE-6 | DRV-US-006/007/008/009/010 | Build route planning, plan review, exception reason, manual override, and publish screens | Frontend Developer | P0 | partial | Static route review, metrics, exception queue, planning strategy controls, strict/relaxed mode, publish controls, and manual override audit-note placeholder implemented; API integration and persisted override warnings pending. |
| DRV-FE-7 | DRV-US-011/012/013/014 | Build driver mobile route list, stop cards, external navigation handoff, one-tap statuses, and proof/failure capture | Frontend Developer | P0 | partial | Static driver mobile route UI implemented with external navigation links, transition buttons, and proof/failure note placeholder; auth/API integration pending. |
| DRV-FE-8 | DRV-US-015/016/017 | Build admin progress dashboard, exception queues, and daily summary UI | Frontend Developer | P1 | partial | Static dashboard metrics and exception queue implemented; Stage 5 copy now documents 10–30s `/dashboard/dispatch` polling target. Live polling and daily report view pending. |
| DRV-QA-3 | DRV-US-006/007 | Test optimization edge cases: missing coordinates, impossible time window, no drivers, capacity/max stops, shift conflicts | QA Engineer | P0 | done | Existing backend tests cover missing coordinates, impossible time window, no available driver, and combined capacity/max-stops. Add separate shift conflict/capacity/max-stops cases next. |
| DRV-QA-4 | DRV-US-011/013/018 | Test mobile driver authorization and status lifecycle | QA Engineer | P0 | partial | Status lifecycle tests pass and unpublished routes are hidden before publish; full authorization cannot be validated until auth/API wrapper exists. |
| DRV-QA-5 | DRV-US-011/018 | Add auth-bound driver route isolation tests | Backend/QA | P0 | backlog | Verify driver identity comes from auth context, drivers cannot fetch another driver's route, and unpublished/unassigned stops are never exposed. Added by Stage 6 QA. |
| DRV-QA-6 | DRV-US-009/019 | Add manual override/reorder feasibility and audit acceptance tests | Backend/Frontend/QA | P0 | backlog | Cover move between drivers, reorder within route, warnings for time-window/shift/capacity violations, and required audit note. Added by Stage 6 QA. |
|| DRV-QA-7 | DRV-US-002/003 | Add Excel/import row-level validation tests | Backend/QA | P0 | done | Service-level and real `.xlsx` parser/upload API tests added; parser/API coverage now in place for 2026-08-01 increment. |
| DRV-QA-8 | DRV-US-014 | Add delivered proof and failed reason UX/API tests | Frontend/Backend/QA | P1 | backlog | Failed must require a non-empty reason; delivered proof note should be action-specific and persisted with timestamp/driver metadata. Added by Stage 6 QA. |
| DRV-QA-9 | DRV-US-015/016/017 | Add dashboard polling, late/at-risk exception, and daily summary QA tests | Frontend/Backend/QA | P1 | backlog | Validate 10–30s polling behavior, late/at-risk reason display, and `/reports/daily` summary once implemented. Added by Stage 6 QA. |
| DRV-DEVOPS-2 | Foundation | Document local development run mode, environment variables, and no-paid-API/no-deployment constraints | DevOps Engineer | P1 | done | Current Stage 7 refreshed `repo/ops/devops-runbook.md` and `repo/.env.example`; no deployment, paid APIs, or public exposure. |
| DRV-DEVOPS-3 | Foundation | Add `.env.example` with no-spend defaults and future FastAPI/PostgreSQL variables | DevOps Engineer | P1 | done | Added `repo/.env.example`; contains local placeholders only and no real secrets. |
| DRV-DEVOPS-4 | Foundation | Prepare Docker Compose plan for API/web/PostgreSQL once real services exist | DevOps Engineer | P1 | backlog | Plan refreshed in Stage 7; do not add Compose until FastAPI/React/PostgreSQL runtime scaffolds, health checks, and migrations exist. |
| DRV-DEVOPS-5 | Foundation/Security | Add CI checks for backend tests, frontend tests, secret scan, and later container build | DevOps Engineer | P1 | backlog | Stage 7 recommends validation-only CI: tests, compile checks, secret scan, audits, and image build checks only; do not push images or deploy without approval. |
| DRV-CEO-1 | CEO Review | Implement FastAPI wrapper with typed request/response schemas around the existing routing service | Backend Developer | P0 | backlog | Corrective action from Stage 9; required before live frontend integration or pilot use. |
| DRV-CEO-2 | CEO Review | Add PostgreSQL/PostGIS-ready persistence and migrations for core delivery, routing, status, and audit entities | Backend Developer | P0 | backlog | Corrective action from Stage 9; in-memory state is not acceptable for pilot use. |
| DRV-CEO-3 | CEO Review | Complete auth-bound role access, tenant isolation, and driver route isolation tests | Backend Developer/QA | P0 | backlog | Corrective action from Stage 9; top security/privacy release blocker. |
| DRV-CEO-4 | CEO Review | Implement manual assignment/reorder override with feasibility warnings and required audit note | Backend/Frontend | P0 | backlog | Corrective action from Stage 9; currently only a UI placeholder and product requirement is not testable. |
| DRV-CEO-5 | CEO Review | Implement Excel/import row-level validation with draft/ready states and actionable row errors | Backend/QA | P0 | partial | Corrective action from Stage 9; service-level Excel-normalized import validation exists, but real `.xlsx` upload parser/API and persistence remain required for realistic small-team batch planning. |
| DRV-CEO-6 | CEO Review | Scaffold React/TypeScript/Vite PWA and wire API-backed admin/driver flows | Frontend Developer | P0 | backlog | Corrective action from Stage 9; static frontend is useful but not pilot-ready. |
| DRV-PO-8 | DRV-US-002A | Add downloadable/import-visible Excel template and schema docs in UI | Frontend/Product | P0 | backlog | New Stage 2 refinement; should be addressed before realistic pilot import testing. |
| DRV-PO-9 | DRV-US-002B | Implement row-level import validation result UI and API contract | Backend/Frontend/QA | P0 | backlog | New Stage 2 refinement; show row number, field, error code/message, and accepted/draft/rejected state. |
| DRV-PO-10 | DRV-US-019A | Add tenant/company scoping to data model and access tests | Backend/QA | P1 | backlog | New Stage 2 refinement; required before any real multi-company pilot data. |
| DRV-BE-12 | DRV-US-001/002/002A/002B/003 | Implement FastAPI order and Excel import API with `.xlsx` parser, import batch persistence, row-level validation errors, template metadata, draft/ready states, and routeability/geocode flags | Backend Developer | P0 | partial | Stage 4 implemented dependency-light template metadata, Excel-normalized row importer, import batch summaries, row-level validation errors, duplicate detection, ready/draft routeability states, and tests in the in-memory service. FastAPI upload wrapper, true `.xlsx` parsing dependency, and durable PostgreSQL persistence remain. |
| DRV-BE-13 | DRV-US-004/005/018/019A | Add PostgreSQL/Alembic tenant-scoped driver/user/role models and enforce tenant/RBAC query boundaries | Backend Developer | P0 | ready | Current Stage 3 task; drivers must not see other drivers' or tenants' data. Tenant model is P1 product hardening but backend foundation should not omit `tenant_id`. |
| DRV-BE-14 | DRV-US-006/006A/006B/007 | Persist planning runs with selected optimization config, route metrics, unassigned reason counts, routes, stops, and strict/relaxed strategy metadata | Backend Developer | P0 | ready | Current Stage 3 task; preserve greedy planner first while keeping OR-Tools/provider abstraction ready. |
| DRV-BE-15 | DRV-US-009/010/013/014/019 | Implement manual move/reorder API, feasibility warnings, publish gate, status/proof lifecycle, and required audit events/notes | Backend Developer | P0 | ready | Current Stage 3 task; manual override and auditability are core trust features. |
| DRV-FE-9 | DRV-US-002/002A/002B/003 | Build API-backed Excel import/template UI with row-level validation result screen | Frontend Developer | P0 | partial | Stage 5 added static UI for template columns, `.xlsx` upload/download actions, import batch counts, and row-level validation cards with suggested fixes in `repo/frontend/`. API-backed upload remains pending until FastAPI endpoints exist. |
| DRV-FE-10 | DRV-US-006/006A/007/008/009/010 | Build API-backed planning configuration, route review, exception queue, manual override warning, and publish flow | Frontend Developer | P0 | partial | Stage 5 added static planning strategy/constraint controls and manual override audit-note labeling; API-backed config persistence, feasibility warnings, and publish integration remain pending. |
| DRV-FE-11 | DRV-US-011/012/013/014/018 | Build auth-bound driver PWA route execution screens with external navigation, one-tap statuses, proof/failure note, and hidden unpublished/other-driver stops | Frontend Developer | P0 | ready | Current Stage 3 task; must consume `/driver/me/routes/today`, not arbitrary driver IDs. |
| DRV-FE-12 | DRV-US-015/016/017 | Build polling admin dispatch dashboard and daily summary UI | Frontend Developer | P1 | ready | Current Stage 3 task; initial polling interval 10–30 seconds. |
| DRV-QA-10 | DRV-US-002/002B/003 | Validate Excel import schema, row-level errors, duplicate IDs, invalid windows/coordinates, and routeability fallback behavior | QA Engineer | P0 | partial | Current QA pass verified service-level template/import tests pass. Still needs real `.xlsx` parser/upload API, malformed/unsupported workbook coverage, persistence checks, and 200-row import behavior. |
| DRV-QA-11 | DRV-US-006/006A/007/009/010 | Validate optimization strategies, unassigned reason codes, manual override warnings, publish gating, and planning-run audit metadata | QA Engineer | P0 | partial | Current QA pass verified existing unassigned reason and publish-gating tests pass. Still needs strategy persistence, strict vs relaxed behavior, manual override warnings, and audit metadata once implemented. |
| DRV-QA-12 | DRV-US-018/019/019A | Validate RBAC, tenant isolation, driver route isolation, status/proof lifecycle, and audit trail | QA Engineer | P0 | partial | Current QA pass verified status lifecycle tests pass. RBAC, tenant isolation, API authorization, driver route isolation, and durable audit trail remain release/pilot blockers. |
| DRV-QA-13 | DRV-US-002/002A/002B/003 | Add real `.xlsx` parser/upload API QA coverage | Backend/QA | P0 | backlog | Cover unsupported file type, malformed workbook, worksheet selection, Excel serial dates, locale date/time values, missing columns, duplicate IDs, invalid coordinates/numerics, geocoding-required drafts, persistence of import batches/row errors, and ~200-row runtime. Added by Stage 6 QA. |
| DRV-QA-14 | DRV-US-011/012/013/014/015 | Add browser-level mobile viewport UX tests | Frontend/QA | P1 | backlog | Validate 360px/390px phone layouts, touch targets, import row-error readability, driver next-stop/status/proof flow, external navigation fallback, and dashboard polling behavior once a browser/PWA test harness exists. Added by Stage 6 QA. |
| DRV-DEVOPS-6 | Foundation | Prepare local-only Docker Compose plan for FastAPI, web, and PostgreSQL/PostGIS once runtime services are implemented | DevOps Engineer | P1 | done | Current Stage 7 completed local-only Compose plan in report/runbook/architecture; actual Compose file intentionally deferred until runtime services exist. No public exposure, deployment, paid APIs, or secret commits. |
| DRV-DEVOPS-7 | Foundation/Security | Add a repository secret-scanning check and placeholder-key guard once CI is introduced | DevOps Engineer | P1 | backlog | Fail on real maps/routing keys, JWT secrets, database passwords, provider tokens, or non-placeholder `.env` values. Added by Stage 7. |
| DRV-DEVOPS-8 | Foundation/Operations | Add health/readiness endpoint checks, migration command, and backup/restore notes after FastAPI/PostgreSQL scaffold exists | DevOps Engineer/Backend | P1 | backlog | Required before any pilot deployment approval; depends on FastAPI runtime and PostgreSQL/Alembic persistence. Added by Stage 7. |

## Current MVP Build Order Recommendation
1. FastAPI + PostgreSQL/Alembic tenant-scoped foundation.
2. Excel template/import API and row-level validation UI.
3. Order and driver CRUD with validation, shifts, availability, capacity/max-stops, and geocode status.
4. Planning-run persistence with configurable strategy and greedy planner behind solver/provider interfaces.
5. Admin planning review, manual override warnings/audit notes, and publish flow.
6. Auth-bound driver mobile route execution/status/proof flow.
7. Polling dispatch dashboard and daily summary.
8. QA/security hardening for tenant isolation, driver route isolation, import edge cases, and solver/runtime limits.

## Backend Developer Handoff — 2026-07-30

- Stage 4 validated the current-run Stage 3 Technical Lead handoff and made a focused backend prototype increment rather than attempting the full FastAPI/PostgreSQL rebuild in one cron slot.
- Implemented the testable core of `DRV-BE-12` in `repo/backend/app/`:
  - Excel template/schema metadata via `RoutingService.excel_template_schema()`.
  - Excel-normalized row import service via `RoutingService.import_orders_from_rows(...)`.
  - `ImportBatch` and `ImportRowError` domain objects with counts for total, valid, invalid, duplicate, routeable rows and row-level fix guidance.
  - Validation for missing required fields, duplicate `order_id`, invalid date, invalid time window, invalid coordinates, invalid priority, and missing coordinates / `geocoding_required` routeability fallback.
  - Imported coordinate-backed rows become `ready_to_plan`; rows missing coordinates but otherwise valid are stored as `draft` with actionable row errors; hard-invalid rows are rejected.
- Updated `repo/backend/docs/api-and-schema.md` with import/template endpoint contracts and import persistence schema draft.
- Verification passed in `repo/backend`: `uv run python -m unittest discover -s tests -v` ran 9 tests successfully.
- Remaining Backend gaps: real FastAPI upload endpoints, actual `.xlsx` file parsing wrapper, PostgreSQL/Alembic persistence, tenant/RBAC models, planning-run durable persistence, manual override API/audit notes, and daily report endpoint.
