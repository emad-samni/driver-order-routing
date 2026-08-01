# Product Owner Report — Driver Order Routing

_Last updated: 2026-08-01 by Evening Stage 2 — Product Owner_

## Validation

Stage 2 prerequisite validation:
- Reviewed prior stage output: `reports/innovation-lead.md` dated 2026-08-01.
- Reviewed supporting artifacts: `reports/ceo-project-director.md`, `research.md`, `product-backlog.md`, `sprint-board.md`, `architecture.md`, `decisions/decision-log.md`.
- Stage 2 prerequisite validation passed. No blocker detected.

## Yesterday / Completed

- Stage 1 Innovation Lead completed research, competitor analysis, niche definition, optimization path, and monetization hypothesis.
- CEO final gate approved work as a local MVP foundation with corrections.
- Existing repo now contains backend runtime surface (`repo/backend/app/main.py`), domain logic, 15 integration tests, static frontend prototype, and supporting planning artifacts.

## Current Progress

- Synthesized Stage 1 findings into product ownership artifacts.
- Defined personas, epics, user stories, acceptance criteria, sprint goal, updated backlog priority, roadmap, and Definition of Done.

## Next Actions

- Hand off finalized product owner artifacts to Technical Lead / backend/frontend developers.
- Use stories and acceptance criteria to plan first backend increment: FastAPI app, Pydantic schemas, Excel template/import contract, orders/drivers/planning-runs endpoints, auth/tenant placeholders, and tests.
- Frontend Developer to start React/TypeScript/Vite PWA scaffold using static prototype flows as reference.
- QA Engineer to expand tests to API integration coverage and mobile viewport checks in next sprint.
- Update `product-backlog.md` and `sprint-board.md` with these refined stories after team review.

## Risks / Blockers

- No direct blocker for Stage 2.
- Risk: if backend or frontend do not pick up stories quickly, handoff will drift and duplicate/contradict planning.
- Risk: Excel upload and validation are central to the niche; if parser/validation slip, the core value proposition weakens.
- Risk: security/privacy is still a hard requirement before real data; no auth/RBAC/tenant implementation means current work is unsafe for customer order data.

---

## Personas

### Admin / Dispatcher (Primary)
- Name: Anna
- Context: Operations manager at a small retailer-delivery subcontractor in Germany/Netherlands. Handles 100–250 daily orders from large retailers, assigns drivers, and resolves exceptions.
- Needs:
  - Upload daily Excel orders fast.
  - See validated imports with row-level errors.
  - Choose optimization mode and review routes before publishing.
  - Monitor progress and exceptions on mobile and desktop.
- Success criteria: planning time reduced, fewer failed deliveries, visibility without phone calls.

### Driver (Primary)
- Name: Karim
- Context: Warehouse-start driver, mobile-only during route execution.
- Needs:
  - Clear assigned stop list with time windows and addresses.
  - One-tap navigation handoff.
  - Fast stop status update with note and timestamp.
  - Offline-friendly route and queue for status updates.
- Success criteria: fewer wrong stops, easier daily start, reliable proof capture.

### Retailer/Client Ops Contact (Secondary / Future)
- Name: Lena
- Context: Large retailer client who audits subcontractor performance.
- Needs:
  - Daily summary and exception visibility.
  - Confidence that proofs and timestamps exist.
- Success criteria: audit readiness and reduced exception escalations.

---

## Epics

### E1: Excel-First Order Intake
- Owner: Backend + Frontend
- Goal: Admin uploads daily `.xlsx`, receives validated normalized orders with row-level errors.
- MVP constraint: one warehouse origin; 200 orders/day scale.

### E2: Warehouse-Start Driver Assignment & Route Sequencing
- Owner: Backend + Technical Lead
- Goal: Assign orders to drivers, sequence stops from warehouse, and publish runnable routes.
- MVP constraint: one warehouse, warehouse-start drivers only.

### E3: Configurable Optimization
- Owner: Technical Lead + Backend
- Goal: Admin selects optimization profile; system computes feasible plan with reason-coded flags for at-risk/unassigned orders.
- MVP modes: shortest distance/fuel proxy, on-time priority, balanced workload, strict constraints, relaxed/manual-review.

### E4: Mobile Driver Execution & Proof
- Owner: Frontend
- Goal: Driver views route, navigates, captures note + timestamp proof, and admin sees progress.

### E5: Admin Exception Dashboard & Reporting
- Owner: Frontend + Backend
- Goal: Admin monitors late, failed, unassigned, and at-risk orders with summary metrics.

### E6: Platform Foundation
- Owner: Technical Lead + DevOps + QA
- Goal: Auth, RBAC, tenant scoping, persistence, tests, and mobile viewport readiness.

---

## User Stories and Acceptance Criteria

### Epic E1: Excel-First Order Intake

**E1.1 — Excel template download**
- As an admin, I can download a standard Excel template so that I know the required fields and structure.
- AC:
  - `/excel-template` returns a downloadable `.xlsx`.
  - Template contains required headers and one example row.
  - Mobile and desktop download works.

**E1.2 — Excel upload and row validation**
- As an admin, I can upload a daily `.xlsx` file and see row-level validation errors.
- AC:
  - `/orders/import/excel` accepts `.xlsx`.
  - Required fields: customer name, address, time window start/end, service duration, bulky-item flag, contact phone.
  - Invalid rows are returned with row number, field, and human-readable error.
  - Valid rows are normalized into internal order schema.
  - Import batch record is persisted with counts and error summary.

**E1.3 — Import preview and correction flow**
- As an admin, I can review validation results and decide whether to proceed with valid rows or fix file.
- AC:
  - UI shows valid row count, invalid row count, and first few errors.
  - Proceeding with valid rows creates draft orders in tenant scope.
  - Canceling discards the batch.

### Epic E2: Warehouse-Start Driver Assignment & Route Sequencing

**E2.1 — Driver creation and management**
- As an admin, I can create/update driver accounts with start location, working hours, vehicle/capacity constraints.
- AC:
  - Admin CRUD for drivers.
  - Fields: name, phone, vehicle type, capacity units, max stops, working start/end, optional access notes.
  - Validation prevents unworkable configurations.

**E2.2 — Planning run creation**
- As an admin, I can create a planning run from draft orders and select optimization mode.
- AC:
  - `/planning-runs` accepts draft order batch id, driver ids, warehouse id, optimization mode, strict/relaxed flag.
  - Run is persisted with status `draft` and configuration snapshot.
  - Invalid config returns structured validation errors.

**E2.3 — Route assignment and sequence generation**
- As an system, I can assign orders to drivers and sequence stops from warehouse.
- AC:
  - Planner returns per-driver ordered stop list.
  - Feasibility checked against working hours, service durations, travel estimates, capacity.
  - Unassigned/at-risk orders have reason codes.
  - Results are stored under planning run id.

**E2.4 — Manual override**
- As an admin, I can reorder stops, move orders between drivers, or mark unassigned with required audit note.
- AC:
  - PATCH `/planning-runs/{id}` accepts reorder/reassign payload.
  - Feasibility warnings emitted when override risks violation.
  - Override requires mandatory note and is persisted as audit event.

**E2.5 — Publish driver routes**
- As an admin, I can publish the planning run so drivers see assigned routes.
- AC:
  - POST `/planning-runs/{id}/publish` transitions run to `published`.
  - Driver route endpoints return only published runs scoped to driver identity.
  - Republish replaces prior published state for same date/driver.

### Epic E3: Configurable Optimization

**E3.1 — Optimization mode selection**
- As an admin, I can choose optimization strategy per planning run.
- AC:
  - Supported modes: shortest_distance_fuel_proxy, ontime_priority, balanced_workload, strict_constraints, relaxed_manual_review.
  - Mode stored with planning run and shown in admin review.

**E3.2 — Feasibility and risk flags**
- As an admin, I see which orders are at risk and why before publishing.
- AC:
  - Risk reasons: time-window conflict, capacity exceeded, working-hours breach, missing address/geocoding confidence.
  - At-risk queue shows order, driver, and reason.

### Epic E4: Mobile Driver Execution & Proof

**E4.1 — Driver route view**
- As a driver, I can see today's published route in ordered stops.
- AC:
  - `/driver/me/routes/today` returns current route with stop sequence.
  - Mobile layout usable at 360px/390px width.
  - Offline-cached route shown when network unavailable.

**E4.2 — Stop status updates**
- As a driver, I can update stop status with note and timestamp.
- AC:
  - Statuses: en_route, arrived, completed, failed, skipped.
  - POST `/orders/{order_id}/status-events` stores status, note, timestamp, driver id.
  - Failed/skipped require note.
  - Events queue offline and sync when connection returns.

**E4.3 — External navigation handoff**
- As a driver, I can open external navigation from a stop.
- AC:
  - Stop row includes open-navigation action using device map app.
  - Uses geo URI or app-intent link; no paid map SDK required.

### Epic E5: Admin Exception Dashboard & Reporting

**E5.1 — Dispatch dashboard**
- As an admin, I can monitor today's runs with at-risk and late indicators.
- AC:
  - `/dashboard/dispatch` returns today's runs, completion %, late count, failed count, unassigned count.
  - Dashboard updates without full page reload via polling.

**E5.2 — Exception review**
- As an admin, I can open failed, skipped, or at-risk orders and see context.
- AC:
  - Order detail shows status events, assigned driver, stop sequence, time window, and last note.
  - Admin can trigger manual override or re-plan flow.

**E5.3 — Daily summary export**
- As an admin, I can export a daily summary of planned vs completed metrics.
- AC:
  - Export includes planned stops, completed, failed, late count, distance/time estimate, driver summary.

### Epic E6: Platform Foundation

**E6.1 — Authentication and RBAC**
- As a system, I ensure only authorized users access tenant-scoped data.
- AC:
  - Admin, driver, and future client roles.
  - Token-based auth with tenant claims.
  - Driver route endpoints enforce driver identity match.
  - Negative tests for cross-tenant and unauthorized access.

**E6.2 — Persistence and migrations**
- As a system, I persist core entities durably.
- AC:
  - PostgreSQL models for tenants, users, drivers, orders, import batches, planning runs, routes, stops, status events, audit events.
  - Alembic migrations apply cleanly on fresh database.

**E6.3 — Mobile viewport readiness**
- As a user, I can use admin and driver flows on mobile.
- AC:
  - Critical paths verified at 360px/390px viewport.
  - Touch targets and readability meet mobile-first guidelines.

---

## Sprint Goal

**Sprint 1: Verified backend planning API with admin import and review flow**
- Deliver FastAPI app with typed endpoints for Excel template, Excel import with row validation, orders, drivers, planning runs, publish, driver routes, status events, and dashboard.
- Deliver at least 15 passing API integration tests covering import, planning run, publish, driver route isolation, status events, and dashboard.
- Deliver tenant/auth placeholders and negative access tests.
- Deliver frontend scaffold with Excel import preview, row errors, and planning review UI connected to backend.

## Updated Backlog Priority

### P0
1. Excel template and `.xlsx` upload parser with row validation.
2. Order/driver CRUD and tenant scoping.
3. Planning run creation, optimization mode config, feasibility flags.
4. Manual override/reorder with audit notes.
5. Publish driver routes and driver route endpoint isolation.
6. Driver status events and offline queue.
7. Auth/RBAC and negative isolation tests.
8. PostgreSQL persistence and migrations for core entities.
9. Admin dashboard polling and daily summary export.

### P1
10. React/TypeScript/Vite PWA scaffold and API wiring.
11. Mobile viewport testing for critical paths.
12. Analytics/reporting views and CSV export.
13. Local Docker Compose for backend + database + frontend.

### P2 / Later
14. Real geocoding and distance matrix provider abstraction.
15. Customer notification module.
16. Multi-depot routing and advanced constraints.
17. Live GPS tracking and re-optimization.
18. Signature/photo/barcode proof.
19. Retailer client portal.

## Roadmap

### MVP Internal Version
- Excel-first intake, one warehouse, warehouse-start drivers, configurable optimization, admin review/publish, mobile driver route with status/proof, admin dashboard, no external paid APIs.
- Target: local workflow proof ready for first pilot operator evaluation.

### V1
- PostgreSQL-backed persistence.
- Auth/RBAC/tenant enforcement.
- Real `.xlsx` parsing and import batch history.
- React/Vite PWA with API-backed import, planning, publish, driver route, status, dashboard, daily summary.
- Mobile viewport tests and basic operational runbook.
- Basic monitoring/logging and local backup/restore runbook.

### V2+
- Distance matrix provider abstraction and optional external routing integration if approved.
- Customer notifications and client portal.
- Multi-depot and advanced constraints.
- Analytics, KPIs, and audit/reporting extensions.

## Definition of Done

- Story implemented with tests passing in CI or local equivalent.
- Acceptance criteria verified and documented in QA notes.
- No new lint/type errors introduced.
- API contract documented if endpoint changed.
- Frontend wired to real API or clearly marked mock.
- Mobile viewport check completed for user-facing story.
- Security/privacy review completed for data-handling story.
- No paid/external API keys or cloud resources used without approval.

---

## Claude Code Execution

- The requested Claude Code helper path in the prompt (`/opt_data/home/.local/bin/claude`) is not available in this environment.
- Proceeding without delegating to Claude Code, using existing workspace artifacts and direct synthesis.
- Inputs reviewed:
  - `reports/innovation-lead.md`
  - `reports/ceo-project-director.md`
  - `project-brief.md`
  - `product-backlog.md`
  - `sprint-board.md`
  - `architecture.md`
  - `research.md`
- Output produced:
  - `reports/product-owner.md`
