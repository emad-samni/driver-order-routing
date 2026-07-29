# Architecture — Driver Order Routing App

_Last updated: 2026-07-29T19:01:12Z by Evening Stage 7 — DevOps Engineer_

## Architecture Summary

Build the MVP as a **single mobile-first role-based PWA/responsive web app** backed by an API and a route-planning service. The system should prove the full delivery loop: order/driver setup, validation, optimization, admin review/publish, driver mobile execution, status updates, and admin exception visibility.

Recommended MVP architecture:

```text
Admin / Driver mobile browser
        ↓ HTTPS/JSON + SSE/WebSocket or polling
React + TypeScript PWA / responsive web app
        ↓
FastAPI backend API
        ↓
PostgreSQL + PostGIS-ready schema
        ↓
Optimization service module
        ↓
Distance/time matrix provider abstraction
   ├─ Prototype: coordinates + haversine/manhattan heuristic
   ├─ MVP/local: optional OSRM/GraphHopper self-hosted or precomputed matrix
   └─ Later approved paid APIs: Google/Mapbox/etc.
```

## Recommended Stack

| Layer | Recommendation | Reasoning |
|---|---|---|
| Frontend | React + TypeScript + Vite PWA/responsive app | Fastest route to mobile-first admin and driver views without separate native apps. |
| Mobile UX | PWA with installable shell, responsive cards, large touch actions | Meets phone-first requirement and keeps native-app complexity out of MVP. |
| Backend | Python FastAPI | Strong API ergonomics, validation with Pydantic, suitable for optimization service integration. |
| Database | PostgreSQL, PostGIS-ready | Reliable relational model; can later add geospatial indexes and distance queries. |
| Auth | MVP local/session/JWT role model | Required to ensure drivers see only assigned routes; can start simple. |
| Real-time updates | Start with short polling; design endpoint contract for SSE/WebSocket later | Polling is simplest and reliable for MVP; SSE/WebSocket can improve freshness without changing domain model. |
| Maps/navigation | External navigation links to Google Maps/Apple Maps-compatible URLs | Avoids in-app turn-by-turn complexity and paid map SDK dependency. |
| Geocoding | Coordinates-first prototype; manual coordinate entry/import fallback; pluggable geocoder later | Avoids paid API spend and uncertainty while preserving future integrations. |
| Optimization | Deterministic heuristic first; OR-Tools VRP module next | Heuristic enables quick demo; OR-Tools supports time windows, shifts, capacity, and max stops for MVP maturity. |
| Dev environment | Docker Compose-ready local stack when implementation begins | Keeps work self-contained and avoids deployment without approval. |

## DevOps / Environment Plan

Current implementation is a local prototype only: Python in-memory backend logic and a static frontend prototype. No deployment, public service exposure, cloud resource creation, paid API use, or repository push was performed by Stage 7.

Local-first MVP environment strategy:

- Keep dependency-light prototype commands available for quick validation.
- Add FastAPI + React/Vite + PostgreSQL/PostGIS Docker Compose only when those runtime components exist.
- Bind local development services to localhost by default.
- Keep map/routing providers pluggable and default to no-spend `haversine` distance and manual coordinates.
- Store secrets in local environment files or approved secret stores only; never commit real API keys.
- Use PWA-first mobile delivery; defer native app packaging and push-notification credentials until explicitly approved.

Recommended future local services:

| Service | Purpose | MVP Notes |
|---|---|---|
| `api` | FastAPI application and route planning service | Uvicorn locally; expose `/health` and later `/ready`. |
| `web` | React/TypeScript/Vite PWA | Local dev server or static preview; polls dispatch endpoints. |
| `postgres` | Durable relational persistence | Enable PostGIS-ready schema/migrations. |
| optional `osrm`/`graphhopper` | Self-hosted distance matrix/routing | Defer until data size/resource needs are reviewed. |

Operational guardrails before any pilot:

- API role-based auth and driver route isolation tests must pass.
- Durable audit trail, migrations, backup/restore plan, and secret management must be in place.
- Logs must avoid leaking unnecessary customer/healthcare-adjacent data.
- Paid geocoding/routing APIs require Emad's approval before configuration or use.
- External deployment and public exposure require separate approval.

## Route Optimization Approach Comparison

| Approach | Pros | Cons | Recommended Use |
|---|---|---|---|
| Simple greedy/nearest-neighbor heuristic | Very fast to implement; no paid APIs; explainable; good for smoke prototype. | May produce suboptimal routes; harder to satisfy complex time windows/capacity perfectly. | First backend prototype and deterministic demos. |
| OR-Tools VRP with time windows/capacity | Mature solver; supports driver shifts, service times, max stops/capacity, unassigned penalties. | More implementation complexity; requires distance/time matrix; solver tuning needed. | MVP route planner once CRUD/data model is stable. |
| OSRM self-hosted | Fast route durations/distances from OpenStreetMap; no per-request paid API. | Requires regional map data and ops setup; no geocoding; traffic not included. | Later local/self-hosted distance matrix option. |
| GraphHopper self-hosted/cloud | Routing and matrix capabilities; OSM-based; flexible vehicle profiles. | Self-hosting/limits/licensing must be checked; cloud may cost. | Later if OSRM is insufficient. |
| Google Maps / Mapbox APIs | Best developer experience, geocoding, ETA, traffic options. | Paid/usage-limited; cannot be used without Emad approval; vendor dependency. | Post-MVP or approved pilot only. |

## MVP Optimization Design

Use a **pluggable planning pipeline**:

1. Validate Excel-imported orders, the configured warehouse/pickup location, and available drivers.
2. Geocode/coordinate-check all customer stops and the shared warehouse start location.
3. Build a distance/time matrix through `DistanceMatrixProvider`.
4. Load selected `OptimizationConfig` from the admin planning form:
   - Strategy presets: balanced, shortest distance, petrol/fuel proxy, on-time/time-window priority, workload balance.
   - Constraints/toggles: respect time windows, driver working hours, max stops/capacity, priority orders, avoid late orders, allow unassigned orders with reason codes.
   - First-pilot defaults: one warehouse pickup, all drivers start from warehouse, no required return-to-warehouse unless configured later.
5. Run `RoutePlanner`:
   - Prototype: greedy assignment by nearest feasible driver/stop while checking selected configuration, shift, time window, service time, max stops.
   - MVP: OR-Tools VRP with time-window constraints, shared warehouse driver start nodes, service durations, max stops/capacity, selectable objective weights, and optional penalties for dropping orders.
6. Persist a `planning_run`, selected optimization configuration, `routes`, `route_stops`, and `unassigned_orders` with reason codes.
7. Return plan in review state; require admin publish before driver visibility.

Core unassigned/at-risk reason codes:
- `missing_coordinates`
- `invalid_address`
- `no_available_driver`
- `outside_driver_shift`
- `time_window_infeasible`
- `capacity_exceeded`
- `max_stops_exceeded`
- `optimization_failed`
- `manual_review_required`

## Core Data Model

| Entity | Key Fields |
|---|---|
| `users` | `id`, `name`, `email/phone`, `role`, `status`, `created_at` |
| `drivers` | `id`, `user_id`, `name`, `phone`, `start_address`, `start_lat`, `start_lng`, `shift_start`, `shift_end`, `availability_status`, `max_stops`, `capacity_units`, `vehicle_type` |
| `orders` | `id`, `external_order_id`, `recipient_name`, `address`, `lat`, `lng`, `geocode_status`, `phone`, `delivery_date`, `time_window_start`, `time_window_end`, `priority`, `service_duration_minutes`, `package_units`, `special_instructions`, `status`, `proof_note`, `failure_reason` |
| `planning_runs` | `id`, `delivery_date`, `status`, `started_by`, `algorithm`, `matrix_provider`, `optimization_strategy`, `optimization_config_json`, `warehouse_address`, `warehouse_lat`, `warehouse_lng`, `created_at`, `published_at`, `summary_json` |
| `routes` | `id`, `planning_run_id`, `driver_id`, `status`, `planned_distance_meters`, `planned_duration_seconds`, `starts_at`, `ends_at` |
| `route_stops` | `id`, `route_id`, `order_id`, `sequence`, `planned_arrival`, `planned_departure`, `eta_status`, `status` |
| `unassigned_orders` | `id`, `planning_run_id`, `order_id`, `reason_code`, `details` |
| `status_events` | `id`, `order_id`, `driver_id`, `actor_user_id`, `from_status`, `to_status`, `note`, `lat`, `lng`, `created_at` |
| `audit_events` | `id`, `actor_user_id`, `object_type`, `object_id`, `action`, `before_json`, `after_json`, `created_at` |

## API Boundary Draft

| Method | Path | Purpose | Related Stories |
|---|---|---|---|
| `GET` | `/health` | API health check | foundation |
| `POST/GET` | `/orders` | Create/list orders | DRV-US-001/002 |
| `GET/PATCH/DELETE` | `/orders/{id}` | Manage order details and draft/ready state | DRV-US-001/003 |
| `POST` | `/orders/import/excel` | Batch import orders from Excel `.xlsx` with row-level validation | DRV-US-002 |
| `POST/GET` | `/drivers` | Create/list drivers | DRV-US-004/005 |
| `GET/PATCH/DELETE` | `/drivers/{id}` | Manage driver details/availability | DRV-US-004/005 |
| `POST` | `/planning-runs` | Run optimization for a delivery date/batch | DRV-US-006/007 |
| `GET` | `/planning-runs/{id}` | Review generated plan, routes, exceptions | DRV-US-007/008 |
| `PATCH` | `/routes/{id}/stops` | Reorder/move stops with validation warnings | DRV-US-009 |
| `POST` | `/planning-runs/{id}/publish` | Publish planned routes to drivers | DRV-US-010 |
| `GET` | `/driver/me/routes/today` | Driver mobile route list | DRV-US-011 |
| `POST` | `/orders/{id}/status-events` | Driver/admin status update with lifecycle validation | DRV-US-013/014 |
| `GET` | `/dashboard/dispatch` | Admin progress/exception dashboard | DRV-US-015/016 |
| `GET` | `/reports/daily` | Daily delivery summary | DRV-US-017 |
| `GET` | `/audit-events` | Dispatch/status audit trail | DRV-US-019 |

## Real-Time / Near-Real-Time Strategy

MVP should start with **near-real-time polling**:
- Driver route view posts status events immediately.
- Admin dashboard polls `/dashboard/dispatch` every 10–30 seconds.
- Driver route list refreshes after publish/status changes.

Keep status/event data model compatible with later:
- Server-Sent Events for admin dashboard updates.
- WebSocket channel per organization/route.
- Push notifications only after explicit approval and scope definition.

## Security and Privacy Boundaries

- Enforce role-based access at API level: drivers can only read assigned published stops.
- Minimize sensitive data exposed to drivers: only delivery-relevant recipient info.
- Keep customer phone optional; support external contact links only if data exists and policy allows.
- Store status/proof events with actor and timestamp.
- Avoid regulated healthcare claims; phrase the product as delivery operations support.
- No external deployment, paid APIs, customer outreach, or production release without Emad's explicit approval. GitHub push for this repository has already been approved by Emad.

## Scalability / Performance Notes

- Target first scale: approximately 200 orders per day for a real pilot business; measure solver/runtime performance with representative data before production use.
- Add indexes on `delivery_date`, `status`, `driver_id`, `planning_run_id`, and future geospatial coordinates.
- Optimization should run asynchronously for larger batches later; MVP can start synchronous with clear timeout/error handling.
- Persist planning results to avoid recomputing routes on each page load.
- Distance matrix provider must be cacheable by coordinate pair and date/batch.

## Implementation Sequence

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

## Technical Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Geocoding/address ambiguity | Bad routes or unroutable orders | Coordinates-first prototype, geocode status field, manual correction, unassigned reason codes. |
| Paid map/routing dependency | Cost/compliance blocker | Use no-spend heuristic first; keep provider abstraction; only use paid APIs with approval. |
| Solver complexity | Delayed MVP | Start greedy; introduce OR-Tools after basic workflow works. |
| Real-time expectations | Operational trust risk | Start polling; upgrade to SSE/WebSocket when needed. |
| Privacy in healthcare-adjacent niche | Legal/reputation risk | Minimize data exposure, role-based access, conservative product wording. |
| Mobile UX complexity | Driver adoption risk | Prioritize phone-first route cards, one-tap actions, and external navigation rather than complex maps. |
