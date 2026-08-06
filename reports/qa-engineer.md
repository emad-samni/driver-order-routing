# Stage 6 — QA Engineer Report

_Last updated: 2026-08-06_

## Stage 5 Validation
- `reports/frontend-developer.md` exists, dated 2026-08-06, no blocker.
- `workflow-status.md` shows Stage 5 `completed`, Last Updated 2026-08-06.
- Input is fresh and valid. Stage 6 proceeds.

## Test Execution

**Primary command — `uv run python -m unittest discover -s tests -v`: FAILED to run.**
Not a test failure; a packaging failure. `uv` attempts to build the project wheel and hatchling errors:
`ValueError: Unable to determine which files to ship inside the wheel` — no directory matches the project
name `driver_routing_backend_prototype` and `[tool.hatch.build.targets.wheel]` is undefined in
`pyproject.toml`. This is the documented fallback trigger.

**Fallback — `.venv/bin/python -m unittest discover -s tests -v`: PASSED.**
`Ran 30 tests in 0.311s — OK`, covering `test_api`, `test_import_parser`, `test_override_api`,
`test_persistence`, `test_routing_service` (import validation and row errors, capacity/max-stops
constraints, time-window infeasibility, missing coordinates, no-available-driver reason codes,
plan/publish/driver-visible route, status lifecycle and failure-note validation, override move/reorder,
SQLite upsert/list).

**Frontend — `node tests/frontend.test.js` (Node v22.22.3): PASSED.** Prototype smoke test only.

## Pass / Fail Status
- Backend regression: **PASS** (30/30, via venv fallback).
- Frontend smoke: **PASS** (1 test file; not a browser test).
- Build/packaging: **FAIL** — `uv run` is unusable until `pyproject.toml` declares the wheel target.

## Release Readiness: NOT READY for pilot
Green tests confirm the logic that is covered; they do not cover the things that block a pilot.

1. **No driver-isolation test exists.** `/driver/me/routes/today` resolves the driver from request input and `REQUIRE_API_KEY` defaults off, so one driver can read another's route and customer addresses. No test asserts otherwise. Must-fix before real data.
2. **No restart-persistence test.** The default runtime is in-memory; nothing verifies that a published plan survives a process restart, because in the default configuration it does not.
3. **No browser or mobile-viewport test.** Frontend coverage is one Node smoke file; the 360/390px driver flow is unverified by automation.
4. **No degraded-mode test.** `fetchWithFallback` silently serves local data when the API is down, and nothing asserts that this state is visible to the user.

## QA Tasks (next sprint)
1. Add `test_driver_isolation` — expected to fail on current code; it is the acceptance gate for the auth fix.
2. Add a restart-survival persistence test against a file-backed SQLite database.
3. Fix `pyproject.toml` wheel configuration so the documented `uv run` path works.
4. Add browser-level mobile viewport tests for the driver flow.
5. Keep the backend suite at 30+ green.

## Decision Log Entry
- 2026-08-06: Backend regression green at 30 tests, but release readiness reported as NOT READY — coverage omits driver isolation, restart persistence, and mobile browser flows.

### Yesterday / Completed
- 2026-08-05 round reported the same 30 passing tests; no code has changed since.

### Current Progress
- Regression suite is stable and fast.
- Coverage gaps are concentrated exactly where pilot risk is highest.

### Next Actions
- DevOps to report runtime posture and the `uv`/hatchling packaging defect.
- Backend Developer to land auth binding so the isolation test can go green.

### Risks / Blockers
- Passing tests risk creating false confidence: the untested paths are the pilot blockers.
- `uv run` is broken by packaging configuration, so the documented developer entry point does not work.
- GitHub push remains credential-blocked.
