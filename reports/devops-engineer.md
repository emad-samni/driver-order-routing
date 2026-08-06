# Stage 7 — DevOps Engineer Report

_Last updated: 2026-08-06_

## Stage 6 Validation
- `reports/qa-engineer.md` exists, dated 2026-08-06, no blocker preventing Stage 7.
- `workflow-status.md` shows Stage 6 `completed`, Last Updated 2026-08-06.
- Input is fresh and valid. Stage 7 proceeds.

## Runtime Status
- **Backend:** local uvicorn only. Virtualenv at `repo/backend/.venv` (36 MB, Python 3.13.5) is healthy; all backend modules import cleanly and the suite runs in 0.31s.
- **Frontend:** static assets served same-origin by FastAPI. No separate build step, no bundler, no node_modules — deployment surface is three files.
- **Database:** `repo/backend/driver_routing.sqlite3` exists (4 KB, plus `-shm`/`-wal`), last written 2026-08-02. It is essentially empty because the default runtime is in-memory (`USE_PERSISTED_SERVICE` unset), so nothing has been persisting to it.
- **Config:** `repo/.env.example` is present and no-spend by default (`DISTANCE_PROVIDER=haversine`, `GEOCODER_PROVIDER=manual`, empty `MAPS_API_KEY`/`ROUTING_API_KEY`). It also carries a `DATABASE_URL` pointing at a PostgreSQL service that does not exist and a placeholder `JWT_SECRET` — both are forward-looking and currently unused.
- **Ops docs:** `repo/ops/devops-runbook.md` only. No Dockerfile, no Compose file, no CI configuration anywhere in the repo.

## Infra Blockers
1. **No deployment path.** There is no container, no CI, no hosted environment. A pilot rehearsal currently requires a developer at a terminal. This is the DevOps item on the Product Owner's top three.
2. **Packaging defect breaks the documented entry point.** `uv run` fails at wheel build — `pyproject.toml` names the project `driver-routing-backend-prototype` with no matching package directory and no `[tool.hatch.build.targets.wheel]` table. Every developer and every CI job hits this. One-line fix: declare `packages = ["app"]`.
3. **Persistence not wired in the default runtime.** The SQLite file exists but is unused by default; the stale 2026-08-02 timestamp is direct evidence.
4. **No GitHub credential** configured (HTTPS helper or SSH key) in this environment.
5. **`.env.example` drift.** It advertises PostgreSQL and JWT settings the code does not read, while omitting the two variables that actually control runtime behavior: `USE_PERSISTED_SERVICE` and `REQUIRE_API_KEY`.

## Validation Steps Completed
- Backend suite executed: 30 tests, all passing, via the venv fallback.
- Backend module imports verified under Python 3.13.5.
- Environment template and runtime artifacts inspected on disk.
- No deployment, no public exposure, no cloud resource creation, no paid API use, no repository push performed at this stage.

## Recommended DevOps Tasks
1. Add `[tool.hatch.build.targets.wheel] packages = ["app"]` to `repo/backend/pyproject.toml` — unblocks `uv run` (minutes).
2. Add `USE_PERSISTED_SERVICE` and `REQUIRE_API_KEY` to `.env.example` with pilot-correct defaults; mark the PostgreSQL/JWT block as unused-until-Phase-2.
3. Add a single `make dev` / shell script that starts the backend with persistence on and serves the frontend — the minimum viable "show a dispatcher" path.
4. Defer Docker Compose and PostgreSQL until after the hardening sprint; they add surface without removing a current blocker.

## Decision Log Entry
- 2026-08-06: Kept the local-only runtime posture. Flagged the hatchling packaging defect and `.env.example` drift as concrete, cheap fixes; Compose/PostgreSQL stay deferred.

### Yesterday / Completed
- 2026-08-05 round verified the same local runtime; no infrastructure has changed since.

### Current Progress
- Local runtime is healthy and reproducible for a developer.
- It is not reproducible for anyone else — that is the gap.

### Next Actions
- Scrum Master to consolidate blockers across stages.
- Fix packaging and env template alongside the backend hardening sprint.

### Risks / Blockers
- No deployment path blocks pilot rehearsal with a real dispatcher.
- Broken `uv run` will block CI the moment CI is introduced.
- GitHub push remains credential-blocked.
