# Backend API and Schema Draft

_Last updated: 2026-07-30T15:37:00Z by Evening Stage 4 — Backend Developer_

## Prototype Scope Implemented

The current code under `repo/backend/app/` implements a dependency-light backend domain and service prototype:

- Order and driver domain models with validation rules.
- Deterministic coordinate-based greedy planner.
- Planning run, route, route stop, and unassigned-order outputs.
- Publish flow that hides planned routes from drivers until admin approval.
- Driver-visible route projection with external navigation links.
- Status lifecycle validation with proof/failure notes.
- Simple dispatch dashboard summary.
- Excel-template schema metadata and dependency-light row import validation for Excel-normalized rows.
- Import batch summaries with row-level errors, duplicate counts, ready/draft/rejected behavior, and coordinate/routeability flags.

This prototype uses in-memory storage so it can run without PostgreSQL, FastAPI, paid map APIs, or deployment.

## API Endpoint Contract for FastAPI Wrapper

| Method | Path | Request | Response | Notes |
|---|---|---|---|---|
| `GET` | `/health` | none | `{ "status": "ok" }` | Basic health check. |
| `GET` | `/excel-template` | none | MVP template columns + examples | Implemented as service metadata; HTTP wrapper pending. |
| `POST` | `/orders/import/excel` | `.xlsx` upload | Import batch summary + row errors | Parser should normalize worksheet rows and call implemented row importer. |
| `GET` | `/import-batches/{id}` | none | Batch counts + row-level validation errors | In-memory batch store exists; HTTP wrapper pending. |
| `POST` | `/orders` | Order payload | Created order + validation errors | Valid orders become `ready_to_plan`; invalid stay `draft`. |
| `GET` | `/orders` | filters: date/status | List orders | Admin/dispatcher only. |
| `PATCH` | `/orders/{id}` | Partial order fields | Updated order + validation errors | Revalidates route-readiness. |
| `POST` | `/orders/import` | CSV/import rows | Created orders + row errors | Implement next around `Order` validation. |
| `POST` | `/drivers` | Driver payload | Created driver + validation errors | Requires shift and start coordinates for planning. |
| `GET` | `/drivers` | filters: availability | List drivers | Admin/dispatcher only. |
| `PATCH` | `/drivers/{id}` | Partial driver fields | Updated driver + validation errors | Availability changes affect next planning run. |
| `POST` | `/planning-runs` | `{ delivery_date }` | Planning run with routes/unassigned | Uses greedy planner for prototype. |
| `GET` | `/planning-runs/{id}` | none | Planning run detail | Review state until published. |
| `POST` | `/planning-runs/{id}/publish` | none | Published planning run | Changes planned orders to `published`. |
| `GET` | `/driver/me/routes/today` | auth context | Driver route cards | Only published stops assigned to current driver. |
| `POST` | `/orders/{id}/status-events` | `{ to_status, note? }` | Status event | Enforces lifecycle; failed requires reason. |
| `GET` | `/dashboard/dispatch` | filters: date | Status counts + latest plan summary | Suitable for 10–30s polling. |
| `GET` | `/reports/daily` | date | Daily summary | Can reuse dashboard + planning summary initially. |
| `GET` | `/audit-events` | filters | Audit event list | Add durable audit table in DB implementation. |

## PostgreSQL/PostGIS-Ready Tables

### `users`
- `id uuid primary key`
- `name text not null`
- `email text unique`
- `phone text`
- `role text not null check role in ('admin','dispatcher','driver','order_owner')`
- `status text not null default 'active'`
- `created_at timestamptz not null default now()`

### `drivers`
- `id uuid primary key`
- `user_id uuid references users(id)`
- `name text not null`
- `phone text`
- `start_address text`
- `start_lat double precision not null`
- `start_lng double precision not null`
- `shift_start time not null`
- `shift_end time not null`
- `availability_status text not null`
- `max_stops integer not null default 25`
- `capacity_units integer not null default 999`
- `vehicle_type text`
- Future: `start_geom geography(Point, 4326)` with geospatial index.

### `import_batches`
- `id uuid primary key`
- `filename text not null`
- `planning_date date`
- `total_rows integer not null default 0`
- `valid_rows integer not null default 0`
- `invalid_rows integer not null default 0`
- `duplicate_rows integer not null default 0`
- `routeable_rows integer not null default 0`
- `status text not null`
- `created_at timestamptz not null default now()`

### `import_row_errors`
- `id uuid primary key`
- `import_batch_id uuid not null references import_batches(id)`
- `row_number integer not null`
- `field text not null`
- `error_code text not null`
- `message text not null`
- `suggested_fix text not null`

### `orders`
- `id uuid primary key`
- `import_batch_id uuid references import_batches(id)`
- `import_row_number integer`
- `external_order_id text`
- `recipient_name text not null`
- `address text not null`
- `lat double precision`
- `lng double precision`
- `geocode_status text not null default 'manual_or_pending'`
- `phone text`
- `delivery_date date not null`
- `time_window_start time not null`
- `time_window_end time not null`
- `priority text not null default 'normal'`
- `service_duration_minutes integer not null default 10`
- `package_units integer not null default 1`
- `special_instructions text`
- `status text not null`
- `proof_note text`
- `failure_reason text`
- Future: `delivery_geom geography(Point, 4326)` with geospatial index.

### `planning_runs`
- `id uuid primary key`
- `delivery_date date not null`
- `status text not null`
- `started_by uuid references users(id)`
- `algorithm text not null`
- `matrix_provider text not null`
- `created_at timestamptz not null default now()`
- `published_at timestamptz`
- `summary_json jsonb not null default '{}'::jsonb`

### `routes`
- `id uuid primary key`
- `planning_run_id uuid not null references planning_runs(id)`
- `driver_id uuid not null references drivers(id)`
- `status text not null default 'review'`
- `planned_distance_meters integer not null default 0`
- `planned_duration_seconds integer not null default 0`
- `starts_at timestamptz`
- `ends_at timestamptz`

### `route_stops`
- `id uuid primary key`
- `route_id uuid not null references routes(id)`
- `order_id uuid not null references orders(id)`
- `sequence integer not null`
- `planned_arrival timestamptz not null`
- `planned_departure timestamptz not null`
- `eta_status text`
- `status text not null`
- Unique constraint: `(route_id, sequence)`.

### `unassigned_orders`
- `id uuid primary key`
- `planning_run_id uuid not null references planning_runs(id)`
- `order_id uuid not null references orders(id)`
- `reason_code text not null`
- `details text`

### `status_events`
- `id uuid primary key`
- `order_id uuid not null references orders(id)`
- `driver_id uuid references drivers(id)`
- `actor_user_id uuid references users(id)`
- `from_status text not null`
- `to_status text not null`
- `note text`
- `lat double precision`
- `lng double precision`
- `created_at timestamptz not null default now()`

### `audit_events`
- `id uuid primary key`
- `actor_user_id uuid references users(id)`
- `object_type text not null`
- `object_id uuid not null`
- `action text not null`
- `before_json jsonb`
- `after_json jsonb`
- `created_at timestamptz not null default now()`

## Validation Rules Implemented / Required

- Orders require recipient name, address, valid coordinates for prototype planning, valid delivery date, positive service duration, positive package units, and `time_window_end > time_window_start`.
- Drivers require name, valid start coordinates, `shift_end > shift_start`, positive `max_stops`, positive `capacity_units`, and `availability_status=available` to be used by planning.
- Planning excludes invalid orders with reason-coded unassigned entries.
- Planning excludes unavailable/invalid drivers.
- Greedy route append checks max stops, capacity, order time window, service duration, and driver shift end.
- Publish must happen before driver route visibility.
- Status transitions follow the MVP lifecycle. Invalid transitions raise errors.
- Failed status requires a note/failure reason.

## Unit Test Plan

Implemented tests cover:

1. Valid order/driver creation and route planning.
2. Driver route hidden before publish and visible after publish.
3. Missing coordinates become `missing_coordinates` unassigned reason.
4. Impossible time window becomes `time_window_infeasible`.
5. Capacity/max stop constraints produce reason-coded unassigned orders.
6. Status lifecycle supports published → accepted → en_route → arrived → delivered.
7. Invalid status transitions are rejected.
8. Failed delivery requires a note.

Next backend tests should add row-level CSV import errors, manual route override warnings, role authorization checks, and database persistence integration tests.
