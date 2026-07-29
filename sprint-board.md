# Sprint Board — Driver Order Routing App

_Last updated: 2026-07-29T20:00:00Z by Evening Stage 9 — CEO / Project Director_

## Sprint Goal
Define and prepare the MVP for a mobile-first driver/order assignment and route optimization product, then build a thin prototype that proves the core planning-to-driver-execution workflow.

## Priority Legend
- P0: Required for MVP workflow validation.
- P1: Important for pilot readiness.
- P2: Post-MVP / later enhancement.

| ID | Task | Owner | Status | Priority | Notes |
|---|---|---|---|---|---|
| DRV-INIT-1 | Research target market, competitors, optimization options, and MVP opportunity | Innovation Lead | done | P0 | Completed Stage 1; outputs in `research.md` and `reports/innovation-lead.md`. |
| DRV-PO-1 | Validate Stage 1 completion and convert research into MVP scope | Product Owner | done | P0 | Stage 1 completed for 2026-07-29; backlog/report updated. |
| DRV-PO-2 | Define MVP roles and permissions | Product Owner | done | P0 | Admin/Dispatcher, Driver, optional Order Owner/Customer Service. |
| DRV-PO-3 | Define order and driver input fields | Product Owner | done | P0 | Captured in `product-backlog.md`. |
| DRV-PO-4 | Define status lifecycle and core workflow | Product Owner | done | P0 | Draft through delivered/failed/returned; driver/admin lifecycle documented. |
| DRV-TL-1 | Choose MVP technical architecture and prototype stack | Technical Lead | done | P0 | Completed 2026-07-29; single React/TypeScript PWA + FastAPI + PostgreSQL/PostGIS-ready architecture documented in `architecture.md`. |
| DRV-TL-2 | Define route optimization technical approach | Technical Lead | done | P0 | Completed 2026-07-29; greedy heuristic first, OR-Tools VRP behind planner interface next; distance/time matrix provider abstraction defined. |
| DRV-TL-3 | Define data model and API contracts | Technical Lead | done | P0 | Completed 2026-07-29; orders, drivers, planning runs, routes, route stops, unassigned orders, status events, and audit events defined. |
| DRV-TL-4 | Define geocoding/address handling strategy for prototype | Technical Lead | done | P0 | Completed 2026-07-29; coordinates-first/manual fallback and no-spend provider abstraction recommended. |
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
| DRV-SM-1 | Consolidate daily outputs and blockers | Scrum Master | done | P1 | Completed Stage 8; consolidated evening sequence in `reports/daily-scrum.md`. |

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
| DRV-FE-5 | DRV-US-001/004/005 | Build mobile-first admin forms/lists for orders and drivers | Frontend Developer | P0 | partial | Static admin order/driver forms and mobile responsive layout implemented in `repo/frontend/`; backend submission/validation wiring pending. |
| DRV-FE-6 | DRV-US-006/007/008/009/010 | Build route planning, plan review, exception reason, manual override, and publish screens | Frontend Developer | P0 | partial | Static route review, metrics, exception queue, and publish controls implemented; API integration and override warnings pending. |
| DRV-FE-7 | DRV-US-011/012/013/014 | Build driver mobile route list, stop cards, external navigation handoff, one-tap statuses, and proof/failure capture | Frontend Developer | P0 | partial | Static driver mobile route UI implemented with external navigation links, transition buttons, and proof/failure note placeholder; auth/API integration pending. |
| DRV-FE-8 | DRV-US-015/016/017 | Build admin progress dashboard, exception queues, and daily summary UI | Frontend Developer | P1 | partial | Static dashboard metrics and exception queue implemented; polling `/dashboard/dispatch` and daily report view pending. |
| DRV-QA-3 | DRV-US-006/007 | Test optimization edge cases: missing coordinates, impossible time window, no drivers, capacity/max stops, shift conflicts | QA Engineer | P0 | done | Existing backend tests cover missing coordinates, impossible time window, no available driver, and combined capacity/max-stops. Add separate shift conflict/capacity/max-stops cases next. |
| DRV-QA-4 | DRV-US-011/013/018 | Test mobile driver authorization and status lifecycle | QA Engineer | P0 | partial | Status lifecycle tests pass and unpublished routes are hidden before publish; full authorization cannot be validated until auth/API wrapper exists. |
| DRV-QA-5 | DRV-US-011/018 | Add auth-bound driver route isolation tests | Backend/QA | P0 | backlog | Verify driver identity comes from auth context, drivers cannot fetch another driver's route, and unpublished/unassigned stops are never exposed. Added by Stage 6 QA. |
| DRV-QA-6 | DRV-US-009/019 | Add manual override/reorder feasibility and audit acceptance tests | Backend/Frontend/QA | P0 | backlog | Cover move between drivers, reorder within route, warnings for time-window/shift/capacity violations, and required audit note. Added by Stage 6 QA. |
| DRV-QA-7 | DRV-US-002/003 | Add CSV/import row-level validation tests | Backend/QA | P0 | backlog | Cover valid rows, missing address/name/date/window, invalid coordinates, draft vs ready states, and actionable row errors. Added by Stage 6 QA. |
| DRV-QA-8 | DRV-US-014 | Add delivered proof and failed reason UX/API tests | Frontend/Backend/QA | P1 | backlog | Failed must require a non-empty reason; delivered proof note should be action-specific and persisted with timestamp/driver metadata. Added by Stage 6 QA. |
| DRV-QA-9 | DRV-US-015/016/017 | Add dashboard polling, late/at-risk exception, and daily summary QA tests | Frontend/Backend/QA | P1 | backlog | Validate 10–30s polling behavior, late/at-risk reason display, and `/reports/daily` summary once implemented. Added by Stage 6 QA. |
| DRV-DEVOPS-2 | Foundation | Document local development run mode, environment variables, and no-paid-API/no-deployment constraints | DevOps Engineer | P1 | ready | Docker Compose-ready is fine, but do not deploy externally without approval. |
| DRV-DEVOPS-3 | Foundation | Add `.env.example` with no-spend defaults and future FastAPI/PostgreSQL variables | DevOps Engineer | P1 | done | Added `repo/.env.example`; contains local placeholders only and no real secrets. |
| DRV-DEVOPS-4 | Foundation | Prepare Docker Compose plan for API/web/PostgreSQL once real services exist | DevOps Engineer | P1 | backlog | Do not add production deployment or public exposure; local-only Compose should wait for FastAPI/React runtime scaffolds. |
| DRV-DEVOPS-5 | Foundation/Security | Add CI checks for backend tests, frontend tests, secret scan, and later container build | DevOps Engineer | P1 | backlog | CI can be added after repo workflow scope is approved; build images only, do not push/deploy without approval. |
| DRV-CEO-1 | CEO Review | Implement FastAPI wrapper with typed request/response schemas around the existing routing service | Backend Developer | P0 | backlog | Corrective action from Stage 9; required before live frontend integration or pilot use. |
| DRV-CEO-2 | CEO Review | Add PostgreSQL/PostGIS-ready persistence and migrations for core delivery, routing, status, and audit entities | Backend Developer | P0 | backlog | Corrective action from Stage 9; in-memory state is not acceptable for pilot use. |
| DRV-CEO-3 | CEO Review | Complete auth-bound role access, tenant isolation, and driver route isolation tests | Backend Developer/QA | P0 | backlog | Corrective action from Stage 9; top security/privacy release blocker. |
| DRV-CEO-4 | CEO Review | Implement manual assignment/reorder override with feasibility warnings and required audit note | Backend/Frontend | P0 | backlog | Corrective action from Stage 9; currently only a UI placeholder and product requirement is not testable. |
| DRV-CEO-5 | CEO Review | Implement CSV/import row-level validation with draft/ready states and actionable row errors | Backend/QA | P0 | backlog | Corrective action from Stage 9; required for realistic small-team batch planning. |
| DRV-CEO-6 | CEO Review | Scaffold React/TypeScript/Vite PWA and wire API-backed admin/driver flows | Frontend Developer | P0 | backlog | Corrective action from Stage 9; static frontend is useful but not pilot-ready. |

## Current MVP Build Order Recommendation
1. Data model/API contracts.
2. Order and driver CRUD with validation.
3. Optimization service with simple deterministic sample data support.
4. Admin planning/review/publish flow.
5. Driver mobile route execution/status flow.
6. Exception dashboard and daily summary.
7. Proof capture, audit hardening, and pilot-readiness improvements.
