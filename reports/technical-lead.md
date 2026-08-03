# Technical Lead Report — Driver Routing

**Run Date:** 2026-08-03  
**Stage:** 3 — Technical Lead  
**Job:** Evening Stage 3 Technical Lead  

## 1. Validation Summary

- **Stage 2 Product Owner (current run):** `d6e15941a390` / `b3c3e45d21a7` executed on 2026-08-03 and produced `reports/product-owner.md`.
- **Existing Stage 1 Artifacts:** `reports/innovation-lead.md` and `research.md` are finalized and non-blocked; Stage 1 for the current run returned `[SILENT]`, but the deliverables already exist.
- **Decision:** Stage 3 can proceed because the current-run Stage 2 deliverables are present and finalized. No blocker exists. This report refreshes the Technical Lead handoff for the 2026-08-03 run.

## 2. Technical Architecture

The recommended MVP architecture remains as defined in `architecture.md`:

- **Frontend:** React + TypeScript + Vite PWA/responsive web app
- **Backend:** FastAPI with Pydantic request/response schemas
- **Database:** PostgreSQL with PostGIS-ready schema and Alembic migrations
- **Auth:** Simple JWT/session-based role model for Admin, Dispatcher, Driver, optional Order Owner
- **Real-time:** Polling first, compatible with SSE/WebSocket later
- **Maps/Navigation:** External navigation links to Google Maps/Apple Maps-compatible URLs
- **Geocoding:** Coordinates-first/manual fallback; pluggable provider later
- **Optimization:** No-spend deterministic heuristic first; OR-Tools VRP/VRPTW behind same interface once API/database/import workflow is stable
- **Distance matrix:** `DistanceMatrixProvider` abstraction; default prototype uses supplied coordinates + haversine/manhattan estimate

## 3. Route Optimization Approach Comparison

| Approach | Strengths | Weaknesses | Technical Recommendation |
|---|---|---|---|
| Simple heuristic: cluster/nearest-feasible/nearest-neighbor | Fast, explainable, no paid dependency, deterministic for tests | Not globally optimal; may struggle with dense time windows/capacity at 200 orders/day | Keep as fallback/prototype implementation and for QA fixtures |
| OR-Tools VRP/VRPTW | Supports vehicle routing, time windows, capacities, service times, dropped-order penalties | Needs reliable matrix/geocoding; solver tuning and runtime limits must be tested | Recommended MVP planning core once API/database/import workflow is stable |
| OSRM self-hosted | Fast OSM-based travel times/distances, no per-request billing | Needs map extracts and operations; no geocoding or live traffic | Good later local/self-hosted matrix provider if no paid APIs are approved |
| GraphHopper self-hosted/cloud | Flexible vehicle profiles, routing/matrix support | Licensing/ops/cost must be checked; cloud use may cost | Evaluate after core pilot workflow is proven |
| Google/Mapbox/HERE/TomTom/NextBillion APIs | High-quality geocoding/routing/ETA; potentially traffic-aware | Paid, vendor-dependent, billing/secrets needed | Do not use without Emad's explicit approval; design adapter interface only |

## 4. Data Model Boundaries

| Entity | Required Additions / Clarifications |
|---|---|
| `tenants` / `companies` | `id`, `name`, `default_country`, `default_service_minutes`, warehouse defaults, timestamps |
| `users` | `tenant_id`, role, status, login identifier; driver users map to driver records |
| `import_batches` | `tenant_id`, filename, worksheet, uploaded_by, planning_date, total_rows, valid_rows, invalid_rows, duplicate_rows, status, created_at |
| `import_row_errors` | `batch_id`, row_number, field, error_code, message, suggested_fix, row_snapshot_json |
| `orders` | `tenant_id`, `import_batch_id`, imported row number, explicit address fields, coordinates, geocode status, validation status (`draft`/`ready_to_plan`) |
| `drivers` | `tenant_id`, inherited warehouse start or driver-specific coordinates, shift window, availability, max stops, capacity units, vehicle type |
| `planning_runs` | `tenant_id`, `import_batch_id`, selected strategy, strict/relaxed mode, selected driver IDs, input counts, unassigned reason counts, created_by, timestamps, status |
| `route_stops` | `tenant_id`, planned arrival/departure, warning flags, override metadata |
| `status_events` | `tenant_id`, actor role/user, timestamp, note/proof/failure reason, optional coordinate |
| `audit_events` | `tenant_id`, object type/id, action, before/after JSON, required audit note for manual overrides |

## 5. API Boundaries

| Method | Path | Purpose | Related Stories |
|---|---|---|---|
| `GET` | `/health` | API health check | foundation |
| `POST/GET` | `/orders` | Create/list orders | DRV-US-001/002 |
| `GET/PATCH/DELETE` | `/orders/{id}` | Manage order details and draft/ready state | DRV-US-001/003 |
| `POST` | `/orders/import/excel` | Batch import orders from Excel `.xlsx` with row-level validation | DRV-US-002 |
| `GET` | `/excel-template` | Download or display default Excel template/schema metadata | DRV-US-002A |
| `GET` | `/import-batches/{id}` | Retrieve valid/invalid row counts and row errors | DRV-US-002B |
| `POST/GET` | `/drivers` | Create/list drivers | DRV-US-004/005 |
| `GET/PATCH/DELETE` | `/drivers/{id}` | Manage driver details/availability | DRV-US-004/005 |
| `POST` | `/planning-runs` | Create planning run with strategy/config/selected drivers | DRV-US-006/006A/006B |
| `GET` | `/planning-runs/{id}` | Review generated plan, routes, exceptions | DRV-US-007/008 |
| `PATCH` | `/planning-runs/{id}/routes` | Manual move/reorder with feasibility warnings and required audit note | DRV-US-009 |
| `POST` | `/planning-runs/{id}/publish` | Publish planned routes to drivers | DRV-US-010 |
| `GET` | `/driver/me/routes/today` | Auth-bound driver route view; must not accept arbitrary driver ID from client | DRV-US-011/012 |
| `POST` | `/orders/{id}/status-events` | Status/proof/failure updates with lifecycle validation and persistence | DRV-US-013/014 |
| `GET` | `/dashboard/dispatch` | Polling dashboard for admin progress and exceptions | DRV-US-015/016 |
| `GET` | `/reports/daily` | Daily summary for completed/failed/late/unassigned and driver route metrics | DRV-US-017 |
| `GET` | `/audit-events` | Dispatch/status audit trail | DRV-US-019 |

## 6. Security / Privacy Requirements

- Every API query must be tenant-scoped; never rely on client-supplied tenant IDs without auth context.
- Drivers may read only their own assigned, published route stops.
- Draft, unassigned, unpublished, and other-driver orders must be hidden from driver endpoints.
- Store proof note + timestamp for MVP; do not add photos/signatures/geotags unless approved.
- Do not configure paid geocoding, routing, SMS/WhatsApp, push notifications, deployment, or public exposure without explicit approval.

## 7. Implementation Sequence

1. Scaffold backend/frontend local prototype and database models.
2. Implement order CRUD/import and validation states.
3. Implement driver CRUD, availability, shifts, and max stops.
4. Implement prototype distance matrix and greedy planner with reason codes.
5. Persist planning runs/routes/stops/unassigned orders.
6. Build admin planning review and publish flow.
7. Build driver mobile route list, external navigation link, and status events.
8. Build admin dashboard polling, exception queues, and daily summary.
9. Add OR-Tools planner behind the same interface when data flow is stable.
10. Add security/audit hardening and QA edge-case tests.

## 8. Downstream Task Split

**Backend:**
- `DRV-BE-12`: FastAPI order and Excel import API with `.xlsx` parser, import batches, row-level errors, template metadata, draft/ready states, and routeability/geocode flags.
- `DRV-BE-13`: PostgreSQL/Alembic tenant-scoped user/driver/role models and RBAC/tenant query boundaries.
- `DRV-BE-14`: persisted planning runs, optimization config, route metrics, unassigned counts, routes/stops, strict/relaxed strategy metadata.
- `DRV-BE-15`: manual move/reorder API, feasibility warnings, publish gate, status/proof lifecycle, and audit events/notes.

**Frontend:**
- `DRV-FE-9`: API-backed Excel import/template UI with row-level validation result screen.
- `DRV-FE-10`: API-backed planning configuration, route review, exception queue, manual override warning, and publish flow.
- `DRV-FE-11`: auth-bound driver PWA route execution screens with external navigation, one-tap statuses, proof/failure note, and hidden unpublished/other-driver stops.
- `DRV-FE-12`: polling admin dispatch dashboard and daily summary UI.

**QA:**
- `DRV-QA-10`: Excel schema/import validation tests.
- `DRV-QA-11`: optimization/manual override/publish-gating tests.
- `DRV-QA-12`: RBAC, tenant isolation, driver route isolation, status/proof lifecycle, and audit tests.

**DevOps:**
- `DRV-DEVOPS-6`: local-only Docker Compose plan for FastAPI, web, and PostgreSQL/PostGIS once runtime services exist.

## 9. Claude Code Execution

This Stage 3 run was executed directly from existing project artifacts because the Claude Code execution helper path was not available/usable in the current runtime. The synthesis below is based on the current workspace state.

**Files read and used:**
- `reports/product-owner.md`
- `project-brief.md`
- `product-backlog.md`
- `architecture.md`
- `workflow-status.md`

**Artifacts produced:**
- `reports/technical-lead.md` (this report)

## 10. Yesterday / Completed

- Validated current-run Stage 2 Product Owner deliverables for 2026-08-03.
- Confirmed architecture, stack decisions, optimization approach, data model, API boundaries, security requirements, implementation sequence, and downstream task split remain coherent.
- Superseded earlier stale prior-day Stage 3 artifacts with this current-run handoff.

## 11. Current Progress

Stage 3 validation is complete for this run. The technical architecture is coherent for the clarified pilot: Excel upload → row-level validation → tenant-scoped persistence → configurable planning run → route review/manual override → publish to driver mobile PWA → status/proof updates → admin polling dashboard and daily summary.

## 12. Next Actions

- Backend Developer should start with `DRV-BE-12` through `DRV-BE-15`, prioritizing FastAPI + PostgreSQL/Alembic foundation, Excel import validation, planning-run persistence, and role/tenant boundaries.
- Frontend Developer should implement API-backed PWA flows from `DRV-FE-9` through `DRV-FE-12`, preserving list-first mobile UX.
- QA should prepare acceptance coverage for import errors, optimization strategies, manual override warnings, publish gating, tenant isolation, driver route isolation, and proof/status lifecycle.
- DevOps should keep local-only/no-spend boundaries and prepare Compose only for implemented runtime services.

## 13. Risks / Blockers

- No Stage 3 blocker remains for this run.
- Biggest technical risks: geocoding quality, solver complexity at ~200 orders/day, row-level Excel data variability, tenant/RBAC mistakes, and mobile driver usability.
- Paid geocoding/routing, external deployment, customer outreach, public release, spending, and production pilot launch remain blocked without explicit approval.
- Open Product Owner questions remain for Emad: likely real Excel columns, return-to-warehouse requirement, default optimization strategy, bulky-goods capacity rules, and whether daily summary export is required in MVP.
