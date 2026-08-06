# Stage 3 — Technical Lead Report

_Last updated: 2026-08-06_

## Stage 2 Validation
- `reports/product-owner.md` exists, dated 2026-08-06, no blocker.
- `workflow-status.md` shows Stage 2 `completed`, Last Updated 2026-08-06.
- `product-backlog.md` carries the 2026-08-06 re-ranking note.
- Input is fresh and valid. Stage 3 proceeds.

## Architecture Position
Stack stays as built: FastAPI + dependency-light domain/service layer + SQLite repository + vanilla-JS SPA served same-origin. Three decisions confirmed this run:

1. **No React/Vite rewrite.** `architecture.md` still lists "React/Vite PWA scaffold or conversion from static prototype" as frontend work. That description is stale — `repo/frontend/app.js` already performs typed API calls against every backend route. Rewriting it would consume a sprint and produce no new capability.
2. **SQLite stays; PostgreSQL/PostGIS deferred.** `service_persisted.py` (696 LOC) and `persistence.py` (481 LOC) already implement the repository against SQLite and are covered by tests. A single-tenant pilot does not need PostgreSQL. Defer until concurrent multi-tenant load or PostGIS distance work is real.
3. **Auth model moves from optional to enforced.** The current shape — `REQUIRE_API_KEY` off by default, driver identity taken from request input — is acceptable for a local prototype and not acceptable for pilot data.

## Technical Risks
- **Dual service implementations.** `service.py` (in-memory, 496 LOC) and `service_persisted.py` (696 LOC) are parallel implementations selected by env var. They will drift. Once persistence is default, the in-memory path should be reduced to a test fixture rather than a maintained runtime.
- **Distance model.** Haversine straight-line distance underestimates real road distance, typically by 20–40% in urban delivery. Route sequencing stays roughly sane, but ETAs and any fuel-saving figure are not defensible to a customer. Keep the provider boundary pluggable; do not quote savings numbers from current output.
- **No response-model hardening.** Several endpoints return loosely typed dicts, so contract breakage would surface at the client rather than at the API boundary.

## Recommended Fixes (in order)
1. Default `USE_PERSISTED_SERVICE=1`; keep an explicit opt-out for tests.
2. Resolve driver identity from the authenticated principal in `/driver/me/routes/today`; default `REQUIRE_API_KEY=1`.
3. Add explicit Pydantic response models to the planning, publish, and driver-route endpoints.
4. Demote `service.py` to a test double once (1) lands.

## Architecture Update
`architecture.md` updated with a dated 2026-08-06 addendum recording the three decisions above and correcting the stale frontend task description in the downstream split.

## Downstream Task Split
- **Backend:** persistence default, driver-identity binding, response models. No new frameworks.
- **Frontend:** no rewrite. Verify behavior against a persisted backend and surface auth state in the UI.
- **QA:** add a driver-isolation test that fails today and passes after fix (2); add a restart-persistence test.
- **DevOps:** produce a reproducible local start path for backend + frontend.

## Decision Log Entry
- 2026-08-06: Confirmed no React rewrite, SQLite retained, auth moves from optional to enforced. Flagged dual service implementations as a drift risk.

### Yesterday / Completed
- 2026-08-05 round closed all stages; no code changed since commit `a1ac7f0`.

### Current Progress
- Architecture is stable and matches the code; the stale frontend description is corrected.
- Next sprint is hardening, not new structure.

### Next Actions
- Backend Developer to scope persistence default and identity binding.
- QA to prepare the isolation and restart tests.

### Risks / Blockers
- Cross-driver route visibility is an open security gap.
- Service-layer duplication will cost maintenance if left past the persistence switch.
- GitHub push remains credential-blocked.
