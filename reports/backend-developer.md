# Stage 4 — Backend Developer Report

_Last updated: 2026-08-06_

## Stage 3 Validation
- `reports/technical-lead.md` exists, dated 2026-08-06, no blocker.
- `workflow-status.md` shows Stage 3 `completed`, Last Updated 2026-08-06.
- `architecture.md` carries the 2026-08-06 addendum.
- Input is fresh and valid. Stage 4 proceeds.

## Backend State (inspected, not assumed)
- 16 routes in `app/main.py`; service layer split across `service.py` (in-memory) and `service_persisted.py` (SQLite), selected at import time by `USE_PERSISTED_SERVICE` (`main.py:43`).
- Excel intake: `import_parser.py` + multipart upload handler; row-level errors with draft/ready classification.
- Planner: greedy sequencing with capacity, max-stops, and time-window constraints; haversine distances.
- Auth: `auth.py` API-key middleware, enabled only when `REQUIRE_API_KEY` is truthy (`main.py:51`).
- Tests: 30 passing across import parser, API, override API, persistence, routing service.

## Implementation Tasks (scoped, not executed this stage)
1. **Default persistence on.** Invert the `USE_PERSISTED_SERVICE` default in `main.py:43`; keep an explicit `USE_PERSISTED_SERVICE=0` escape hatch for the in-memory test path. ~0.5 day including test-fixture updates.
2. **Bind driver route to principal.** Resolve the driver from the authenticated API key / principal in `/driver/me/routes/today` instead of request-supplied identity; return 403 for a mismatch. Default `REQUIRE_API_KEY` on. ~1 day including a key→driver mapping.
3. **Response models.** Add explicit Pydantic response models to `/planning-runs`, `/planning-runs/{id}/publish`, and `/driver/me/routes/today`. ~0.5 day.
4. **Demote in-memory service.** After (1), move `service.py` out of the runtime selection path and keep it as a test double. ~0.5 day.

**Scope estimate: ~2.5 developer-days.** No new dependencies, no framework changes, no schema migration.

## Test Plan
- Extend `test_persistence.py` with a restart-survival case: write orders + a published plan, re-open the repository from the same SQLite file, assert both are readable.
- Add `test_driver_isolation` to `test_api.py`: driver A's credential requesting today's route must not return driver B's stops. This test is expected to **fail against current code** and pass after task 2 — that is its purpose.
- Re-run the full suite via `.venv/bin/python -m unittest discover -s tests -v`; the 30 existing tests must stay green.
- Manual: import `repo/samples/test-orders.xlsx` against a persisted backend, plan, publish, post a status event, restart the process, confirm state survives.

## Work Performed This Stage
Analysis and scoping only. No repository code was modified — the report defines the sprint, and per the brief, code scope is not expanded beyond it.

## Verification
- Backend suite re-run this round: 30 tests, all passing (see Stage 6).

## Decision Log Entry
- 2026-08-06: Scoped the hardening sprint at ~2.5 days: persistence default, driver-identity binding, response models, in-memory demotion. No new dependencies.

### Yesterday / Completed
- 2026-08-05 round closed; no backend code changed since commit `a1ac7f0`.

### Current Progress
- Backend API surface is complete against MVP contracts; remaining work is hardening.
- Hardening sprint scoped and estimated.

### Next Actions
- Frontend Developer to verify SPA behavior against a persisted backend and plan for enforced auth.
- QA to run the current regression suite and add the two new tests above.

### Risks / Blockers
- Driver-isolation gap is real and currently exploitable; it is the reason task 2 outranks everything else.
- GitHub push remains credential-blocked.
