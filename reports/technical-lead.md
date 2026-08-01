# Technical Lead Report — Driver Routing

_Last updated: 2026-08-01T21:20:00Z_

## Validation

Stage 3 prerequisite validation passed for the current evening run.

Validated:
- `workflow-status.md` marks Stage 2 Product Owner as `completed` for the current run at `2026-08-01T21:10:00Z`.
- `reports/product-owner.md` exists, is finalized for Driver Routing, and reports no Stage 2 blocker.
- `product-backlog.md` exists and contains finalized MVP/user stories for the retailer-delivery routing product.
- Product Owner output covers the required scope: roles/personas, Excel `.xlsx` import schema, row-level validation error model, order/driver fields, status lifecycles, mobile UX requirements, optimization options, success metrics, and open questions.

The earlier Stage 3 blocked report from prior runs is superseded because Stage 2 has been completed for the current run.

## Technical Architecture Completed

Updated `architecture.md` to keep the existing architecture direction and harden it around the new Stage 2 requirements.

Recommended MVP architecture remains:
- **Mobile-first PWA/responsive web app** for admin/dispatcher and driver views.
- **React + TypeScript + Vite** frontend.
- **FastAPI** backend with Pydantic request/response schemas.
- **PostgreSQL with PostGIS-ready schema** and Alembic migrations.
- **Simple JWT/session role model** for Admin, Dispatcher, Driver, and optional limited Order Owner visibility.
- **Polling first** for near-real-time status/dashboard updates, with event model compatible with SSE/WebSocket later.
- **External navigation links** for Google Maps/Apple Maps-compatible handoff, not in-app turn-by-turn navigation.
- **Coordinates-first/manual fallback geocoding** until a free/local or paid provider is explicitly approved.
- **Route planner abstraction** with no-spend deterministic heuristic first and OR-Tools VRP/VRPTW as the recommended MVP solver once persistence/API/data quality are stable.

## Route Optimization Comparison

Updated the architecture with a clear comparison:
- **Simple heuristic**: fastest, no paid dependency, explainable, deterministic for tests; good first prototype/fallback but not globally optimal.
- **OR-Tools VRP/VRPTW**: best open-source MVP solver path for time windows, shifts, capacity, service time, and dropped-order penalties; needs a reliable distance/time matrix.
- **OSRM/GraphHopper**: useful later as no/low marginal-cost matrix providers, but add operational complexity and do not solve geocoding alone.
- **Google/Mapbox/HERE/TomTom/NextBillion-style APIs**: strong production geocoding/routing/ETA quality, but paid/vendor-dependent and not allowed without explicit approval.

## API and Data Model Boundaries

Added/clarified technical boundaries for:
- `tenants` / `companies`.
- `users` and role mapping.
- `import_batches` and `import_row_errors`.
- explicit Excel/address fields on `orders`.
- tenant-scoped `drivers`, `planning_runs`, `routes`, `route_stops`, `status_events`, and `audit_events`.
- import template endpoint.
- Excel upload endpoint with row-level validation result.
- persisted planning-run endpoint with selected optimization config.
- manual move/reorder endpoint with feasibility warnings and required audit note.
- auth-bound driver route endpoint: `/driver/me/routes/today`.
- status/proof/failure event endpoint.
- polling dispatch dashboard and daily summary endpoints.

## Sprint Board Updates

Updated `sprint-board.md` with current Stage 3 task split:

Backend ready tasks:
- `DRV-BE-12`: FastAPI order and Excel import API with `.xlsx` parser, import batches, row-level errors, template metadata, draft/ready states, and routeability/geocode flags.
- `DRV-BE-13`: PostgreSQL/Alembic tenant-scoped user/driver/role models and RBAC/tenant query boundaries.
- `DRV-BE-14`: persisted planning runs, optimization config, route metrics, unassigned counts, routes/stops, strict/relaxed strategy metadata.
- `DRV-BE-15`: manual move/reorder API, feasibility warnings, publish gate, status/proof lifecycle, and audit events/notes.

Frontend ready tasks:
- `DRV-FE-9`: API-backed Excel import/template UI with row-level validation result screen.
- `DRV-FE-10`: API-backed planning configuration, route review, exception queue, manual override warning, and publish flow.
- `DRV-FE-11`: auth-bound driver PWA route execution screens with external navigation, one-tap statuses, proof/failure note, and hidden unpublished/other-driver stops.
- `DRV-FE-12`: polling admin dispatch dashboard and daily summary UI.

QA ready tasks:
- `DRV-QA-10`: Excel schema/import validation tests.
- `DRV-QA-11`: optimization/manual override/publish-gating tests.
- `DRV-QA-12`: RBAC, tenant isolation, driver route isolation, status/proof lifecycle, and audit tests.

DevOps ready task:
- `DRV-DEVOPS-6`: local-only Docker Compose plan for FastAPI, web, and PostgreSQL/PostGIS once runtime services exist.

## Decisions Recorded

Recorded Technical Lead decisions in `decisions/decision-log.md`:
1. Supersede the earlier blocked Stage 3 handoff because current-run Product Owner artifacts are now valid and non-blocked.
2. Keep the mobile-first PWA + FastAPI + PostgreSQL/PostGIS-ready architecture and harden it around Excel import, row-level validation, tenant/RBAC boundaries, and persisted planning runs.
3. Use a no-spend deterministic heuristic first while preserving OR-Tools VRP and pluggable distance-matrix provider boundaries for MVP maturity.

### Yesterday / Completed

- Validated current-run Stage 2 completion and finalized Product Owner artifacts.
- Recovered Stage 3 from the earlier blocked state.
- Updated `architecture.md` with refined technical architecture, stack decisions, optimization approach comparison, API boundaries, data model additions, security/privacy boundaries, and downstream task split.
- Updated `sprint-board.md` with Stage 3 completion plus backend, frontend, QA, and DevOps ready tasks.
- Updated `workflow-status.md` Stage 3 to `completed` for the current run.
- Recorded Technical Lead decisions in `decisions/decision-log.md`.

### Current Progress

Stage 3 is now **completed** for the current evening run.

The architecture is technically coherent for the clarified pilot: Excel upload → row-level validation → tenant-scoped persistence → configurable planning run → route review/manual override → publish to driver mobile PWA → status/proof updates → admin polling dashboard and daily summary.

### Next Actions

- Backend Developer should start with `DRV-BE-12` through `DRV-BE-15`, prioritizing FastAPI + PostgreSQL/Alembic foundation, Excel import validation, planning-run persistence, and role/tenant boundaries.
- Frontend Developer should implement API-backed PWA flows from `DRV-FE-9` through `DRV-FE-12`, preserving list-first mobile UX.
- QA should prepare acceptance coverage for import errors, optimization strategies, manual override warnings, publish gating, tenant isolation, driver route isolation, and proof/status lifecycle.
- DevOps should keep local-only/no-spend boundaries and prepare Compose only for implemented runtime services.

### Risks / Blockers

- No Stage 3 blocker remains.
- Biggest technical risks: geocoding quality, solver complexity at ~200 orders/day, row-level Excel data variability, tenant/RBAC mistakes, and mobile driver usability.
- Paid geocoding/routing, external deployment, customer outreach, public release, spending, and production pilot launch remain blocked without explicit approval.
- Open Product Owner questions remain for Emad: likely real Excel columns, return-to-warehouse requirement, default optimization strategy, bulky-goods capacity rules, and whether daily summary export is required in MVP.
