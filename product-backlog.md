# Driver Routing Product Backlog

_Last updated: 2026-07-30T14:52:35Z by Evening Stage 2 — Product Owner_

## MVP Product Definition

### MVP Goal
Deliver a mobile-first dispatch and driver execution MVP for small delivery/logistics companies in Germany and the Netherlands that contract with larger retailers such as IKEA, MediaMarkt, furniture/electronics retailers, or similar high-volume local delivery clients. The MVP should let an admin import up to roughly 200 orders/day from Excel, validate constraints, generate configurable driver assignments and stop sequences, monitor progress, and let drivers execute routes from mobile with note + timestamp proof/status updates. The product should be suitable for a real pilot business, not just a demo.

### Target Users / Roles

| Role | Description | MVP Permissions |
|---|---|---|
| Admin / Owner | Business owner or operations lead responsible for delivery outcomes. | Manage users, orders, drivers, optimization runs, assignments, exceptions, and reports. |
| Dispatcher | Day-to-day delivery planner; may be the same person as Admin in small teams. | Import/create orders, create drivers, run optimization, override assignments, monitor status. |
| Driver | Field user executing assigned deliveries on a phone. | View only assigned published stops, open navigation, update statuses, capture delivery proof/notes. |
| Order Owner / Customer Service | Internal or retailer-facing staff who owns customer communication. | View order status and exception notes; create/update orders if permitted. Post-MVP or limited MVP role. |

### Personas

#### Admin / Owner: Small Fleet Operator
- Runs a 5–25 driver subcontracted delivery operation for one or more large retailers.
- Measures success by fewer planning hours, fewer failed/late deliveries, lower distance/fuel proxy, and cleaner proof when retailer clients challenge delivery performance.
- Needs fast Excel intake, simple route publishing, practical override control, and daily summary reporting.

#### Dispatcher: Daily Route Planner
- Starts the day with a retailer spreadsheet, available drivers, warehouse pickup rules, and customer time windows.
- Needs row-level import errors, feasibility warnings, selectable optimization strategies, and the ability to manually move or reorder stops before publishing.
- Uses a phone/tablet/laptop and wants list-first screens that work without advanced logistics training.

#### Driver: Mobile Route Executor
- Uses a phone during the delivery route.
- Needs a clear ordered stop list, next-stop highlight, external map navigation, customer/access notes, one-tap statuses, and simple delivered/failed proof capture.
- Should only see assigned published stops to minimize customer-data exposure.

#### Retailer / Order Owner: Visibility Consumer
- Wants confidence that outsourced deliveries are planned, attempted, completed, failed for known reasons, and reportable.
- MVP can support this through admin exports/status views; separate retailer portal and customer notifications are later enhancements.

### MVP Workflow
1. Admin/Dispatcher uploads an Excel file containing the daily delivery batch.
2. System validates required fields, routeability, time windows, service duration defaults, duplicates, and optional coordinates/capacity data.
3. Admin/Dispatcher configures one pickup warehouse/location for the batch.
4. Admin/Dispatcher creates/updates available drivers; for the first pilot, all drivers start from the same warehouse location, plus their shift hours, capacity/max stops, and availability.
5. Admin selects optimization configuration/options and triggers route planning.
6. System assigns feasible orders to drivers and sequences each route while respecting selected strategy, driver shifts, order time windows, capacity/max stops, and service time.
7. System surfaces unassigned/at-risk orders with reason codes.
8. Admin reviews the plan in list-first mobile-friendly format and manually overrides if needed.
9. Admin publishes routes to drivers.
10. Driver views today's route on mobile, opens external navigation, and updates stop status.
11. Admin monitors progress, late/failed orders, and route completion.
12. Admin exports/reviews daily delivery summary.

## Data Requirements

### Excel Import Schema — MVP Default
The first pilot should support a default `.xlsx` worksheet named `orders` or the first worksheet in the file. A field-mapping layer can come later, but MVP should start with a clear template.

| Column | Required | Example | Validation / Notes |
|---|---:|---|---|
| `order_id` | Yes | `RET-100231` | Unique within upload/day; duplicate rows get row-level errors. |
| `customer_name` | Yes | `A. Müller` | Recipient/customer display name. |
| `street_address` | Yes | `Alexanderplatz 1` | Can also accept combined `address` if supplied. |
| `postal_code` | Yes | `10178` | Required for Germany/Netherlands address matching. |
| `city` | Yes | `Berlin` | Required for routeable address. |
| `country` | Preferred | `DE` | Default can be company/pilot country if omitted. |
| `latitude` | Optional | `52.5219` | If present with longitude, can bypass geocoding confidence risk for prototype. |
| `longitude` | Optional | `13.4132` | Must be valid coordinate if supplied. |
| `delivery_date` | Yes | `2026-08-03` | MVP plans one operating day/batch at a time. |
| `time_window_start` | Yes | `09:00` | Business default allowed only if explicitly configured. |
| `time_window_end` | Yes | `13:00` | Must be after start and within planning day. |
| `service_minutes` | Preferred | `10` | If absent, use configurable default. |
| `priority` | Preferred | `normal` | Allowed: low, normal, high. |
| `phone` | Optional | `+49...` | Optional by Emad decision; driver call action only appears if present. |
| `package_units` | Optional | `2` | Used if capacity constraints enabled. |
| `weight_kg` | Optional | `45` | Later/pilot-specific capacity rule. |
| `vehicle_requirement` | Optional | `van` | Future constraint; MVP can show as warning/metadata. |
| `instructions` | Optional | `Call before arrival` | Access notes, preferences, proof notes. |

#### Import Validation Error Model
- Import result must show total rows, valid rows, draft/error rows, duplicate rows, and routeable rows.
- Row errors should include row number, field, error code, human-readable message, and suggested fix.
- MVP error codes: `missing_required_field`, `duplicate_order_id`, `invalid_date`, `invalid_time_window`, `invalid_coordinate`, `invalid_priority`, `missing_routeable_address`, `unsupported_file`, `geocoding_required`, `geocoding_failed`, `outside_planning_day`.
- Valid rows become `ready_to_plan`; rows with fixable issues remain `draft` or are rejected with row-level detail depending on implementation simplicity.

### Order Fields
| Field | Required for MVP | Notes |
|---|---:|---|
| Order ID | Yes | Generated or imported unique identifier. |
| Customer / recipient name | Yes | Person receiving delivery. |
| Delivery address | Yes | Text address; geocoding confidence handled by Technical Lead. |
| Latitude / longitude | Preferred | Required for optimization once geocoded; can be manually supplied in prototype. |
| Contact phone | Optional | Customer number is not mandatory. Routing and delivery execution must work without it. |
| Delivery date | Yes | MVP routes one operating day at a time. |
| Time window start/end | Yes | Default business-wide window allowed if configured. |
| Priority | Yes | Low/normal/high; high influences exception visibility and tie-breaking. |
| Package size/weight/units | Optional | Required only if capacity constraints enabled for pilot. |
| Service duration | Yes | Default configurable, e.g. 5–10 minutes. |
| Special instructions | Optional | Gate code, parking/access notes, proof requirements. |
| Status | Yes | Lifecycle defined below. |
| Assigned driver / sequence | System | Filled by optimization or manual assignment. |
| Failure reason / proof fields | Conditional | For MVP, delivered/failed proof is note + timestamp. |

### Driver Fields
| Field | Required for MVP | Notes |
|---|---:|---|
| Driver ID/account | Yes | Login identity and assignment key. |
| Name/contact | Yes | For admin coordination. |
| Start/current location | Yes | First pilot: inherited warehouse start location. Future: driver-specific current/home locations. |
| Shift start/end | Yes | Hard feasibility constraint. |
| Availability status | Yes | Available, unavailable, on route. |
| Capacity/max stops | Yes | At least max stops; size/weight later if needed. |
| Vehicle type | Optional | Useful for future constraints. |
| Assigned route | System | Ordered stop list. |

### Warehouse / Batch Fields
| Field | Required for MVP | Notes |
|---|---:|---|
| Planning date | Yes | One daily batch at a time. |
| Warehouse name | Yes | Shared pickup/depot label. |
| Warehouse address | Yes | Used as common start location. |
| Warehouse latitude/longitude | Preferred | Required by optimizer after geocoding/manual coordinate entry. |
| Default service minutes | Yes | Used when import row omits `service_minutes`. |
| Default country | Yes | Germany or Netherlands for address defaults. |

## Status Lifecycle

### Order Statuses
- `draft`: created but missing required data.
- `ready_to_plan`: valid for route planning.
- `planned`: assigned to a driver and sequence, not yet published.
- `published`: visible to driver.
- `accepted`: driver acknowledged route/stop.
- `en_route`: driver is traveling to stop.
- `arrived`: driver arrived at customer location.
- `delivered`: delivery completed; proof captured if required.
- `failed`: delivery attempt failed; failure reason required.
- `returned`: item returned to depot/store.
- `cancelled`: removed from active planning.

### Driver Statuses
- `offline`
- `available`
- `assigned`
- `on_route`
- `paused`
- `completed_shift`

## Mobile UX Requirements
- Screens must be responsive from a 360px-wide phone viewport upward.
- Admin critical path must be usable from mobile: import/review summary, driver availability, run optimization, review exceptions, publish routes, monitor progress.
- Driver critical path must require minimal typing: route list, next stop, open navigation, one-tap status, proof/failure note only when needed.
- List-first UI is required for MVP; map visualization is helpful but not blocking.
- Status/error copy should be plain English for non-technical dispatchers.
- Drivers must never see draft/unpublished orders or orders assigned to other drivers.

## Optimization Configuration — MVP Options
- `shortest_distance`: minimize planned route distance / fuel proxy.
- `on_time_priority`: prioritize feasible arrival inside customer time windows.
- `balanced_workload`: distribute stops/work minutes more evenly across drivers.
- `strict_constraints`: exclude orders that violate time windows, shifts, capacity, or routeability.
- `relaxed_manual_review`: produce best-effort routes but surface warnings for dispatcher override.
- All planning runs should save chosen strategy, selected drivers, input counts, unassigned reason counts, and timestamp for audit/reproducibility.

## MVP Success Metrics
- Dispatcher planning time per route batch reduced by at least 50% versus manual process.
- Planned distance/fuel proxy reduced by at least 10–20% in pilot scenarios.
- On-time delivery rate visible and measurable per driver/day.
- Failed delivery reasons captured for 90%+ of failed stops.
- Driver/admin phone coordination reduced via status visibility.
- Manual override rate visible, so the team can see where optimization/configuration needs improvement.

## Epics

| Epic ID | Epic | MVP Scope | Priority |
|---|---|---|---|
| EPIC-1 | Order Intake & Validation | Excel upload for first pilot, import-ready structure, required-field validation, draft/ready states; manual/CSV can come later. | P0 |
| EPIC-2 | Driver & Shift Management | Driver accounts, shared warehouse start location for first pilot, shift hours, availability, capacity/max stops. | P0 |
| EPIC-3 | Route Planning & Optimization | Admin-triggered assignment/sequence, selectable optimization strategy/configuration, time windows, driver shifts, service time, capacity/max stops, reason-coded unassigned orders. | P0 |
| EPIC-4 | Admin Dispatch Control | Review plan, publish routes, override assignments/sequences, monitor order/driver progress. | P0 |
| EPIC-5 | Driver Mobile Execution | Mobile route list, stop details, external navigation handoff, status updates, proof/failure capture. | P0 |
| EPIC-6 | Real-Time / Near-Real-Time Visibility | Admin progress updates, exception queues, late/failed/unassigned filters. | P1 |
| EPIC-7 | Reporting & Analytics | Daily route summary, planned distance/time, completed/failed/late metrics, exportable report. | P1 |
| EPIC-8 | Security, Roles & Auditability | Role-based access, tenant/company scoping, drivers see assigned stops only, assignment/status audit trail. | P1 |
| EPIC-9 | Post-MVP Enhancements | Live GPS, customer notifications, offline sync, signatures/barcodes, advanced analytics, native apps. | P2 |

## User Stories

| ID | Epic | User Story | Acceptance Criteria | Priority | Owner | Status |
|---|---|---|---|---|---|---|
| DRV-US-001 | EPIC-1 | As a dispatcher, I want to create an order manually so that urgent orders can be added without a spreadsheet. | Required fields include recipient name, address, delivery date, time window, service duration/default, and priority; missing required fields keep the order in `draft`; valid orders can become `ready_to_plan`. | P0 | Product/Backend/Frontend | ready for refinement |
| DRV-US-002 | EPIC-1 | As a dispatcher, I want to import a batch of orders from an Excel file so that daily planning is fast and matches common business workflows. | System accepts an `.xlsx` Excel upload using the documented MVP schema; rows with missing required fields are rejected or marked draft with row-level errors; valid rows are created as ready to plan. CSV/manual entry can be added later. | P0 | Product/Backend | ready for refinement |
| DRV-US-002A | EPIC-1 | As a dispatcher, I want a downloadable/import-visible Excel template so that retailer files can be prepared correctly. | Template or schema documentation lists required/optional columns, examples, accepted time/date formats, optional coordinate fields, and import screen links to it. | P0 | Product/Frontend | ready for refinement |
| DRV-US-002B | EPIC-1 | As a dispatcher, I want row-level import validation results so that I can fix bad retailer data quickly. | Import result displays row number, field, error code/message, valid row count, invalid row count, and whether each row was imported as ready/draft/rejected. | P0 | Backend/Frontend/QA | ready for refinement |
| DRV-US-003 | EPIC-1 | As a dispatcher, I want ambiguous or incomplete addresses flagged before routing so that bad data does not produce poor routes. | Order shows address validation/geocoding status; unrouteable orders are excluded from optimization with a reason; admin can edit and retry. | P0 | Technical Lead/Backend | ready for refinement |
| DRV-US-004 | EPIC-2 | As an admin, I want to create driver accounts with shift hours while all drivers start from the warehouse for the first pilot so that the optimizer can plan feasible routes from one shared origin. | Driver has name/contact, login/account key, warehouse start location inherited from batch/company settings, shift start/end, availability, and max stops/capacity; unavailable drivers are excluded from planning. | P0 | Backend/Frontend | ready for refinement |
| DRV-US-005 | EPIC-2 | As a dispatcher, I want to mark drivers available/unavailable so that the plan uses only real capacity. | Driver availability can be changed before planning; unavailable drivers receive no new route; existing assignments require admin confirmation before removal. | P0 | Frontend/Backend | ready for refinement |
| DRV-US-006 | EPIC-3 | As a dispatcher, I want to run route optimization for a delivery day so that orders are assigned and sequenced efficiently. | Admin can select date/batch and drivers; optimization returns route per driver with ordered stops; respects selected optimization configuration, time windows, shift hours, service time, and max stops/capacity where data exists. | P0 | Technical Lead/Backend | ready for refinement |
| DRV-US-006A | EPIC-3 | As an admin, I want to choose optimization options before planning so that the system can match different business priorities. | Optimization configuration supports shortest distance/fuel proxy, on-time priority, balanced workload, strict constraints, relaxed/manual-review mode, max stops, and driver working hours; selected configuration is saved with the planning run. | P0 | Product/Technical Lead/Backend/Frontend | ready for refinement |
| DRV-US-006B | EPIC-3 | As a dispatcher, I want each planning run to preserve its input summary and selected strategy so that route decisions can be explained later. | Planning run stores date, warehouse, selected drivers, order count, strategy, strict/relaxed mode, created_by, timestamp, route count, and unassigned reason counts. | P1 | Backend | ready for refinement |
| DRV-US-007 | EPIC-3 | As a dispatcher, I want the system to explain unassigned or at-risk orders so that I know what to fix. | Each unassigned/at-risk order has a reason code such as missing address, outside driver shifts, capacity exceeded, impossible time window, no available driver, or optimization failed. | P0 | Backend/Frontend | ready for refinement |
| DRV-US-008 | EPIC-4 | As a dispatcher, I want to review assignments before publishing so that I retain control over dispatch decisions. | Planned routes remain internal until published; route list shows driver, sequence, ETA/time-window status, planned distance/time if available, and exceptions. | P0 | Frontend | ready for refinement |
| DRV-US-009 | EPIC-4 | As a dispatcher, I want to manually change a driver assignment or stop sequence so that local knowledge can override automation. | Admin can move an order between drivers or reorder stops; system warns if change violates time window/shift/capacity; override is saved with audit note. | P0 | Frontend/Backend | ready for refinement |
| DRV-US-010 | EPIC-4 | As a dispatcher, I want to publish routes to drivers so that drivers see only finalized work. | Publish action changes planned orders to `published`; driver mobile view updates; republishing after override is supported. | P0 | Backend/Frontend | ready for refinement |
| DRV-US-011 | EPIC-5 | As a driver, I want a mobile route list for today so that I know my assigned stops in order. | Driver sees only assigned published stops; next stop is highlighted; each stop shows recipient, address, time window, instructions, contact action if phone exists, and status. | P0 | Frontend | ready for refinement |
| DRV-US-012 | EPIC-5 | As a driver, I want to open the next stop in a map app so that I can navigate without in-app turn-by-turn routing. | Stop card provides external navigation link using coordinates/address; link works on mobile for Google Maps/Apple Maps-compatible URL. | P0 | Frontend | ready for refinement |
| DRV-US-013 | EPIC-5 | As a driver, I want one-tap status updates so that admin can monitor progress without calling me. | Driver can set accepted, en route, arrived, delivered, failed, returned where allowed; status updates record timestamp and user; invalid transitions are blocked or confirmed. | P0 | Backend/Frontend | ready for refinement |
| DRV-US-014 | EPIC-5 | As a driver, I want to capture delivery proof or failure reason so that completed/failed stops are documented. | Delivered/failed stop supports note + timestamp as MVP proof; failed stop requires reason and optional note; proof metadata includes timestamp and driver. Photo/signature are post-MVP unless Emad approves earlier. | P1 | Backend/Frontend | ready for refinement |
| DRV-US-015 | EPIC-6 | As an admin, I want a live or near-real-time dashboard so that I can see route progress and exceptions. | Dashboard refreshes or receives updates; filters show unassigned, late/at-risk, failed, in progress, completed; route progress count shown per driver. | P1 | Backend/Frontend | ready for refinement |
| DRV-US-016 | EPIC-6 | As a dispatcher, I want late and at-risk stops highlighted so that I can intervene early. | System compares planned/actual status against time windows/ETA if available; late/at-risk stops appear in exception queue. | P1 | Backend/Frontend | ready for refinement |
| DRV-US-017 | EPIC-7 | As an admin, I want a daily delivery summary so that I can measure performance. | Report includes total orders, assigned/unassigned, completed, failed, late, stops per driver, planned distance/time if available, and exception reasons. | P1 | Backend/Frontend | ready for refinement |
| DRV-US-018 | EPIC-8 | As an admin, I want role-based access so that drivers cannot view unrelated customer data. | Admin/dispatcher can manage batches; drivers can access only their assigned published route; protected routes/API enforce role checks. | P1 | Backend | ready for refinement |
| DRV-US-019 | EPIC-8 | As an admin, I want an audit trail for dispatch and status changes so that disputes can be reviewed. | Assignment changes, status updates, proof submissions, and overrides include user, timestamp, previous value, and new value. | P1 | Backend | ready for refinement |
| DRV-US-019A | EPIC-8 | As an admin, I want tenant-safe data access so that one delivery company cannot see another company's orders, drivers, or route history. | Every business object belongs to a tenant/company; APIs enforce tenant scope; tests cover cross-tenant denial. | P1 | Backend/QA | ready for refinement |
| DRV-US-020 | EPIC-9 | As a customer service user, I want optional customer notifications so that recipients know when delivery is coming. | Deferred post-MVP unless approved; notification events and templates documented for later SMS/WhatsApp/email integration. | P2 | Product | deferred |
| DRV-US-021 | EPIC-9 | As a driver, I want offline route access and queued status sync so that poor network does not stop delivery work. | Deferred post-MVP; PWA should be designed so offline cache/sync can be added later. | P2 | Product/Technical Lead | deferred |

## Resolved Questions From Emad
1. First pilot target: not pharmacy-specific; focus on small delivery/logistics companies contracting with big retailers such as IKEA, MediaMarkt, furniture/electronics retail, or similar.
2. Geography/language: Germany and Netherlands/Holland; main product language should be English.
3. Proof of delivery MVP: note + timestamp is enough.
4. Customer phone/contact number: optional, not mandatory.
5. Expected scale: approximately 200 orders per day.
6. Intended output: real pilot business, not just demo prototype.
7. First pilot order input: upload an Excel file (`.xlsx`); this can change later.
8. First pilot pickup model: one pickup location / warehouse.
9. First pilot driver start model: all drivers start from the warehouse/shared pickup location.
10. Optimization must expose multiple configurable options so the user/admin can choose the planning strategy.

## Remaining Open Questions for Emad
1. For Excel upload, what columns will the first real customer/company likely provide?
2. Should every route return to the warehouse at the end of the shift, or can drivers finish at the last delivery?
3. Which optimization option should be the default: balanced, shortest distance, petrol/fuel proxy, or on-time delivery?
4. Are bulky-goods capacity constraints needed in the first pilot, and if yes should they be based on max stops, units, weight, volume, vehicle type, or helper/crew requirement?
5. Should the admin be able to send delivery summaries to retailer clients as Excel/PDF in MVP, or is on-screen reporting enough for the first build?

---

## 2026-08-06 Re-Ranking Note (Product Owner, Stage 2)

Direct repo inspection this run showed the frontend SPA is already API-backed against all 13 backend
endpoints, so the long-standing "build the API-backed frontend" priority is substantially satisfied.
Priorities are re-ranked accordingly. No items added or removed; no scope change.

**Top 3 for the next sprint**
1. Persist by default — flip `USE_PERSISTED_SERVICE` to default-on (`repo/backend/app/main.py:43`).
   Today an in-memory restart discards every order, plan, and status event.
2. Auth-bound driver route access — bind `/driver/me/routes/today` to an authenticated principal and
   default `REQUIRE_API_KEY` on (`repo/backend/app/main.py:51`). Cross-driver route visibility is a
   GDPR exposure once real customer addresses are loaded.
3. Runnable deployment for pilot rehearsal — one reproducible way to start backend + frontend together
   so a dispatcher can be walked through the workflow without a developer present.

**Demoted:** React/Vite rewrite moves to conditional Phase 2. It re-implements working software and does
not advance pilot readiness. Revisit only if the vanilla SPA hits a concrete limit.
