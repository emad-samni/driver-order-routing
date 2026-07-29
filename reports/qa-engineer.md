# QA Engineer Report — Driver Routing

_Last updated: 2026-07-29T18:31:27Z_

## Validation

Stage 6 prerequisite validation passed.

Validated that Stage 5 for the current daily run is marked **completed** in `workflow-status.md` with timestamp `2026-07-29T18:04:14Z` and no blocker noted.

Validated frontend/backend reports exist and are consistent:
- `reports/backend-developer.md` documents a completed in-memory backend prototype, API/schema draft, unit tests, and no blocker for Stage 5/6.
- `reports/frontend-developer.md` documents a completed mobile-first static frontend prototype, API contract alignment, frontend tests, and no blocker for Stage 6.
- Both reports agree that current implementation is prototype-only: backend is not yet FastAPI/PostgreSQL-backed, frontend is not yet connected to live API/auth/polling.

## QA Verification Performed

Executed backend unit tests from `repo/backend/`:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Actual result:

```text
test_capacity_and_max_stops_constraints ... ok
test_failed_requires_note ... ok
test_impossible_time_window_is_unassigned ... ok
test_missing_coordinates_are_unassigned ... ok
test_no_available_driver_reason ... ok
test_plans_and_publishes_driver_visible_route ... ok
test_status_lifecycle_and_failure_note_validation ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.001s

OK
```

Executed frontend prototype tests from `repo/frontend/`:

```bash
node tests/frontend.test.js
```

Actual result:

```text
Frontend prototype tests passed
```

Executed backend syntax check:

```bash
python3 -m py_compile backend/app/*.py
```

Actual result: command exited successfully with no syntax errors.

## Acceptance Criteria Coverage Review

| Area | Current QA Result | Notes |
|---|---|---|
| Order intake validation | Partial pass | Backend validates recipient, address, coordinates, time window, service duration, package units. CSV/import row-level validation is not implemented. Frontend form is visual-only. |
| Driver validation | Partial pass | Backend validates driver name, start coordinates, shift, max stops, and capacity. Frontend driver form is visual-only. |
| Route optimization constraints | Partial pass | Unit tests cover missing coordinates, impossible time window, no available drivers, capacity/max stops, publish visibility, and status lifecycle. Additional shift-end conflict, priority ordering, mixed-driver, and same-day filtering tests should be added. |
| Admin review/publish | Partial pass | Backend publish gate works in unit tests. Frontend shows static route review/publish controls. Manual override/reorder is not implemented. |
| Driver mobile workflow | Partial pass | Frontend renders mobile route cards, external navigation links, next-stop highlight, and status buttons. Backend provides driver route projection after publish. No auth enforcement yet. |
| Status lifecycle | Partial pass | Backend enforces lifecycle and failed-note requirement. Delivered proof note is optional; if pilot requires proof for every delivered order, acceptance criteria must be tightened. Frontend note field appears only when `failed` is an available action, so delivered proof UX is under-specified. |
| Real-time / near-real-time updates | Not implemented | Architecture says 10–30s polling first; frontend/backend only provide static dashboard/prototype summary, no polling loop or API wrapper. |
| Security/privacy | Not implemented | Backend service method filters by driver ID when called correctly, but there is no authentication, role model, tenant/org isolation, or API-level authorization yet. |
| Offline mode | Deferred | Backlog marks offline route access as P2/post-MVP. No blocker for MVP prototype, but important for later driver reliability. |
| Reporting | Partial/not implemented | Dashboard summary exists in-memory; daily report/export endpoint and UI are not implemented. |

## QA Findings

### P0 Findings

1. **No API-level role-based authorization exists yet.**
   - Requirement: drivers can see only assigned published stops.
   - Current state: `route_for_driver_today(driver_id, today)` returns only a matching driver route, but the caller supplies `driver_id`; without auth/session binding, this is not sufficient for a real API.
   - Corrective task added: `DRV-QA-5` / implementation should add auth-bound driver route tests.

2. **Manual override acceptance criteria are not testable yet.**
   - Requirement: admin can move/reorder stops with feasibility warnings and audit note.
   - Current state: UI has placeholder button; backend has no override method/API.
   - Corrective task added: `DRV-QA-6`.

3. **CSV/import row-level validation is not implemented.**
   - Requirement: batch import should identify invalid rows and keep invalid orders draft/rejected.
   - Current state: backend validates individual `Order` objects only.
   - Corrective task added: `DRV-QA-7`.

4. **Frontend delivered proof capture is incomplete.**
   - Requirement: delivery proof/failure capture design.
   - Current state: a shared textarea appears only when `failed` is an available action; once a stop is `arrived`, actions are `delivered`/`failed`, so note exists, but the UI copy is not action-specific and click handler does not persist note to state/API.
   - Corrective task added: `DRV-QA-8`.

### P1 Findings

5. **Near-real-time dashboard polling is not implemented.**
   - Requirement: admin progress dashboard refreshes every 10–30 seconds or equivalent.
   - Current state: static sample dashboard only.

6. **Late/at-risk detection is not implemented.**
   - Requirement: compare ETA/status against time windows and surface late/at-risk stops.
   - Current state: unassigned exceptions exist; late risk queue is not implemented.

7. **Daily summary/export endpoint and UI are pending.**
   - Requirement: daily route summary/reporting.
   - Current state: backend dashboard summary can be reused later; no `/reports/daily` implementation.

## Additional QA Cases Recommended

### Backend route planning
- Invalid coordinate bounds should keep order/driver out of planning with actionable error.
- Order date mismatch should not be silently planned into the wrong daily run.
- Driver shift-end conflict should return `outside_driver_shift` distinctly from `time_window_infeasible`.
- Capacity exceeded and max-stops exceeded should be tested separately.
- Priority ordering should be deterministic when capacity is scarce.
- Multiple drivers should receive feasible assignments without exceeding individual constraints.
- Re-running a plan should clarify whether previous planned orders are replanned, ignored, or superseded.

### Status lifecycle
- Reject status updates before publish.
- Reject delivered without arrival if strict lifecycle is required; current lifecycle allows published → en_route but not en_route → delivered.
- Verify returned flow from failed/en_route/arrived.
- Verify failed delivery note is non-empty after trimming whitespace.
- Verify proof/failure metadata includes driver, actor, timestamp, and optional location.

### Frontend/mobile UX
- Touch targets should remain usable on small phone widths.
- Driver route should keep next-stop highlight after status changes.
- Failed delivery should require a reason before submission.
- Navigation links should support coordinate and address fallback.
- Admin exception queue should include missing coordinates, invalid address, time window, capacity, max stops, shift conflict, and no driver reason labels.

### Security/privacy
- Driver cannot fetch another driver's route by changing an ID.
- Driver cannot see unpublished planned orders.
- Driver cannot update unassigned/unpublished/unrelated orders.
- Customer phone/instructions are exposed only when needed for delivery.
- Audit events capture assignment overrides and status transitions.

## Sprint Board Updates

Added QA corrective tasks to `sprint-board.md`:
- `DRV-QA-5` — add auth/role/driver-route isolation tests.
- `DRV-QA-6` — add manual override and feasibility warning acceptance tests.
- `DRV-QA-7` — add CSV/import row-level validation tests.
- `DRV-QA-8` — add delivered proof/failure note UX tests.
- `DRV-QA-9` — add dashboard polling/late-exception QA tests.

Updated workflow status: Stage 6 completed for `2026-07-29T18:31:27Z`.

### Yesterday / Completed

- Validated Stage 5 Frontend Developer completion for the current daily Driver Routing run.
- Verified frontend and backend reports are present and consistent.
- Reviewed MVP acceptance criteria in `product-backlog.md`, technical boundaries in `architecture.md`, implementation status in `sprint-board.md`, and prototype files under `repo/`.
- Ran backend unit tests: 7 tests passed.
- Ran frontend prototype tests: passed.
- Ran backend syntax check: passed.
- Updated QA report, sprint board corrective QA tasks, and workflow status.

### Current Progress

Stage 6 QA Engineer work is complete for today.

The prototype is QA-acceptable as a workflow proof: it demonstrates order/driver validation, deterministic route planning, unassigned reason codes, publish gating, driver mobile route display, navigation handoff, and status lifecycle behavior. It is not yet pilot-ready because API integration, durable persistence, auth, manual override, import validation, polling, and stronger proof/exception handling remain incomplete.

### Next Actions

- Stage 7 DevOps Engineer should define local run instructions and environment boundaries without deployment.
- Backend next pass should add FastAPI wrapper, auth-bound route access tests, CSV import validation, manual override validation warnings, and durable audit/persistence.
- Frontend next pass should scaffold the React/TypeScript PWA and wire forms/actions to API contracts once backend endpoints exist.
- QA next pass should convert the recommended edge cases into executable tests after the API wrapper and real frontend app exist.

### Risks / Blockers

- No blocker for Stage 7.
- Main QA risk: security/privacy acceptance criteria cannot be fully validated until authentication and API authorization exist.
- Route optimization is heuristic/haversine only; accepted for no-spend prototype, but not sufficient for production ETA/fuel claims.
- Mobile UX is static and not API-integrated; usability and validation behavior need re-testing once implemented in the real PWA.
