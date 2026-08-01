# QA Engineer Report — Driver Routing

_Last updated: 2026-08-01T22:10:00Z_

## Validation

Stage 6 prerequisite validation passed for the current evening run.

Validated:
- `workflow-status.md` marks Stage 5 Frontend Developer as `completed` for the current run at `2026-08-01T21:50:00Z`.
- `reports/frontend-developer.md` exists, is current, and reports no Stage 5 blocker.
- `reports/backend-developer.md` exists, is current, and reports no Stage 4 blocker.
- Frontend and backend reports are consistent: the current artifact is still a local prototype, with a dependency-light in-memory backend service and a static responsive frontend prototype. Both now align around Excel-first `.xlsx` import/template flows, row-level validation, planning strategy controls, driver route execution, and near-real-time dashboard polling as a future API-backed requirement.

## QA Verification Performed

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

Verification outcome: **pass for prototype-level checks**. No syntax/test regression was found in the current backend/frontend artifacts.

## Acceptance Criteria Coverage Review

| Area | Current QA Result | Notes |
|---|---|---|
| Excel import/template | Partial pass | Backend service exposes template metadata and validates Excel-normalized rows. Frontend displays template, import metrics, and row-level errors. Real `.xlsx` upload parsing, unsupported-file behavior, FastAPI endpoint, and persistent import batches are not implemented. |
| Row-level validation | Partial pass | Unit tests cover ready vs draft rows, duplicate order IDs, invalid time windows, missing coordinates/geocoding-required fallback, and row-error details. Need broader tests for missing required address parts, invalid dates, invalid priorities, invalid numeric fields, and malformed workbooks once real parser exists. |
| Order routeability | Partial pass | Coordinate-backed rows can become `ready_to_plan`; rows missing coordinates become `draft`/`geocoding_required`. Real geocoding, manual correction flow, and retry behavior are pending. |
| Driver constraints | Partial pass | Backend tests cover capacity/max-stops in combination and no available driver. Separate shift-end conflict, unavailable-driver reassignment confirmation, capacity-only, max-stops-only, and multi-driver balancing tests remain. |
| Route optimization assumptions | Partial pass | Deterministic greedy/haversine prototype remains acceptable for no-spend workflow proof. Configurable strategy controls are static UI only; selected strategy/config is not persisted or exercised by planner tests yet. |
| Admin review/publish | Partial pass | Backend publish gating and driver-visible route after publish are tested. Manual move/reorder, feasibility warnings, strict vs relaxed review behavior, and required audit note are not implemented. |
| Driver mobile workflow | Partial pass | Frontend prototype shows route list, next-stop highlight, external navigation, status actions, and proof/failure note placeholder. It is not auth-bound, API-backed, or tested at real mobile viewport/browser level. |
| Status/proof lifecycle | Partial pass | Backend tests enforce failed-note requirement and status lifecycle constraints. Delivered proof note is still weakly specified in UI/API; proof metadata persistence with actor/timestamp requires durable status events. |
| Dashboard / near-real-time visibility | Not implemented | Frontend copy documents 10–30 second polling target for `/dashboard/dispatch`, but no live polling/API integration exists. Late/at-risk detection and daily summary remain pending. |
| Security/privacy/RBAC | Not implemented for pilot readiness | No API-level auth, role checks, or tenant isolation exist. The service can filter by driver ID when called correctly, but that is not sufficient because a real API must derive driver identity from auth context. |
| Offline mode | Deferred | Product backlog marks offline route access and queued sync as P2/post-MVP. No current MVP blocker, but it remains a driver reliability risk for later. |

## QA Findings

### P0 Findings

1. **Real Excel upload path is not testable yet.**
   - Current state: validation works on normalized row dictionaries; no actual `.xlsx` parser/upload endpoint exists.
   - Risk: malformed files, worksheet selection, cell type conversion, date/time parsing, unsupported file errors, and large 200-order imports can still fail outside the service-level tests.
   - Corrective task: keep `DRV-BE-12` partial and add/maintain QA coverage under `DRV-QA-10` plus new parser/API cases.

2. **No API-level RBAC, tenant isolation, or auth-bound driver route isolation exists.**
   - Current state: prototype methods are caller-supplied and in-memory.
   - Risk: a future API could expose another tenant's orders or another driver's published route if not designed/tested from auth context.
   - Corrective task: `DRV-QA-12` remains partial and must become a release/pilot gate with negative access tests.

3. **Manual override and audit acceptance criteria remain untestable.**
   - Current state: frontend has a static manual override/audit-note label; backend has no persisted override/move/reorder API.
   - Risk: dispatcher trust workflow is incomplete because local-knowledge corrections cannot be validated, warned, or audited.
   - Corrective task: `DRV-QA-11` remains partial; backend/frontend must implement feasibility warnings and required audit note.

4. **Optimization configuration controls are UI-only.**
   - Current state: strategy/strict-relaxed controls exist in prototype copy/UI, but selected config is not persisted with planning runs and not used by tests.
   - Risk: product promises configurable optimization options, but prototype behavior does not yet prove strategy differences.
   - Corrective task: add planner tests for shortest-distance, on-time priority, balanced workload, strict constraints, and relaxed/manual-review outputs once planner supports them.

5. **Mobile UX is not browser-verified.**
   - Current state: static CSS/JS tests pass, but no real viewport/browser test was executed.
   - Risk: 360px phone usability, touch target sizes, sticky actions, and status/proof flows can regress without browser-level checks.
   - Corrective task: add a lightweight browser/DOM viewport test once React/Vite or a browser test harness is introduced.

### P1 Findings

6. **Near-real-time dispatch dashboard is not implemented.**
   - Requirement: admin dashboard refreshes or receives updates every 10–30 seconds.
   - Current state: only static dashboard copy and in-memory summary support exist.

7. **Late/at-risk detection is pending.**
   - Requirement: exception queue should highlight late or at-risk stops using planned ETA/status/time windows.
   - Current state: unassigned reasons exist; live ETA/time-window risk queue does not.

8. **Daily report/export is pending.**
   - Requirement: admin daily delivery summary for completed/failed/late/unassigned and driver route metrics.
   - Current state: no `/reports/daily` endpoint or UI implementation.

## Additional QA Cases Recommended

### Excel import and data quality
- Upload unsupported file type and malformed workbook.
- Missing worksheet or wrong worksheet name.
- Missing required columns: `order_id`, `customer_name`, street/address, `postal_code`, `city`, `delivery_date`, `time_window_start`, `time_window_end`.
- Duplicate `order_id` within file and duplicate against existing orders for the same tenant/day.
- Invalid dates, Excel serial dates, locale-formatted dates, invalid times, and `time_window_end <= time_window_start`.
- Invalid latitude/longitude bounds and invalid numeric package/service fields.
- 200-order import runtime and row-error readability.

### Optimization and dispatch
- Separate tests for shift conflict, capacity exceeded, and max stops exceeded.
- Multiple drivers with uneven capacity and shift windows.
- Priority tie-breaking when capacity is scarce.
- Strict constraints should exclude infeasible orders; relaxed/manual-review mode should surface warnings without hiding risk.
- Re-running a planning run should define whether earlier plans are superseded or preserved.
- Manual move between drivers and reorder within route should produce warnings and require audit note.

### Driver/status/security
- Driver route endpoint must not accept arbitrary driver IDs from client.
- Driver cannot view draft, unpublished, unassigned, other-driver, or other-tenant stops.
- Driver cannot update unrelated/unpublished order status.
- Failed delivery requires a trimmed non-empty reason/note.
- Delivered proof note behavior should be explicit: optional vs required by tenant/pilot configuration.
- Status/proof events must include actor, role, timestamp, previous status, new status, and tenant.

### Frontend/mobile
- Validate 360px, 390px, tablet, and desktop responsive layouts.
- Ensure import row-error cards are readable and actionable on phone width.
- Ensure driver status actions remain large enough for touch operation.
- Ensure external navigation link supports coordinates and address fallback.
- Ensure dashboard polling interval is visible/configured and does not create excessive requests.

## Sprint Board Updates

Updated `sprint-board.md` for the current QA pass:
- Marked `DRV-QA-10` **partial** because service-level Excel template/import row validation tests pass, but real `.xlsx` parser/API coverage is still pending.
- Marked `DRV-QA-11` **partial** because publish gating and core unassigned reason tests pass, but strategy persistence, strict/relaxed behavior, manual override warnings, and audit metadata remain pending.
- Marked `DRV-QA-12` **partial** because status lifecycle behavior is tested, but RBAC, tenant isolation, API authorization, and driver route isolation remain unimplemented.
- Updated old CSV wording to Excel/import wording where needed.
- Added new corrective QA task `DRV-QA-13` for real `.xlsx` parser/upload/API tests.
- Added new corrective QA task `DRV-QA-14` for mobile viewport/browser-level UX checks.

Updated `workflow-status.md`: Stage 6 completed for `2026-08-01T22:10:00Z`.

### Yesterday / Completed

- Previous QA pass validated the earlier in-memory backend and static frontend prototype, then identified blockers around auth, manual override, import validation, proof UX, polling, and reporting.
- Today, validated current-run Stage 5 completion and confirmed frontend/backend handoffs are consistent and unblocked.
- Ran real verification across frontend tests, backend syntax checks, and backend unit tests: all passed on 2026-08-01.
- Re-reviewed MVP acceptance coverage against the updated Excel-first import workflow, configurable planning controls, mobile UX, admin/driver workflows, and security/privacy expectations.
- Updated QA report, sprint board QA task statuses, and workflow status.

### Current Progress

Stage 6 QA Engineer work is **completed** for the current run.

The current artifact is acceptable as a local workflow proof. It demonstrates the intended flow shape:

Excel template/import review → row-level validation and draft/ready routeability → planning review/publish → driver mobile route execution/status/proof placeholder → admin dashboard direction.

It is **not pilot-ready**. The largest release blockers are still API/auth/tenant isolation, durable persistence, real `.xlsx` upload parsing, manual override/audit implementation, API-backed frontend integration, and live dashboard/reporting.

### Next Actions

- Stage 7 DevOps Engineer should proceed and keep all work local-only: no deployment, paid APIs, public exposure, or production pilot action.
- Backend next pass should prioritize FastAPI endpoint wrappers, real `.xlsx` parser tests, PostgreSQL/Alembic persistence, tenant/RBAC enforcement, auth-bound driver route isolation, and manual override/audit APIs.
- Frontend next pass should scaffold/port to React + TypeScript + Vite PWA and wire Excel import, planning, publish, status/proof, and dashboard polling to real API contracts once available.
- QA next pass should expand from service/static tests into API integration tests and browser/mobile viewport tests.

### Risks / Blockers

- No blocker for Stage 7.
- Security/privacy remains the top pilot blocker until tenant scoping, role checks, and driver route isolation are implemented and tested.
- Route optimization remains heuristic/haversine only and cannot support production-grade ETA/fuel claims yet.
- Real retailer Excel data may expose parser/date/address edge cases not covered by normalized-row service tests.
- Mobile usability cannot be fully certified until the app is browser-tested at phone viewports and connected to real state/API behavior.
