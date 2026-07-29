# DevOps Runbook — Driver Routing MVP

_Last updated: 2026-07-29T19:01:12Z by Evening Stage 7 — DevOps Engineer_

## Current Artifact State

The repository currently contains dependency-light prototypes only:

- Backend: Python in-memory domain/service/planner under `repo/backend/`.
- Frontend: static dependency-free mobile-first prototype under `repo/frontend/`.
- No FastAPI server, database container, production build, cloud deployment, or external API integration exists yet.

## Local Verification Commands

Backend:

```bash
cd repo/backend
PYTHONPATH=. python3 -m unittest discover -s tests -v
python3 -m py_compile app/*.py
```

Frontend:

```bash
cd repo/frontend
node tests/frontend.test.js
python3 -m http.server 4173
# open http://localhost:4173 locally
```

## Environment Strategy

Use local-first configuration and keep all paid/external integrations disabled by default.

Recommended future environment variables:

```text
APP_ENV=local
APP_HOST=127.0.0.1
APP_PORT=8000
FRONTEND_PORT=5173
DATABASE_URL=postgresql://driver_routing:driver_routing@postgres:5432/driver_routing
JWT_SECRET=replace-for-local-dev-only
JWT_ISSUER=driver-routing-local
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173
DISTANCE_PROVIDER=haversine
GEOCODER_PROVIDER=manual
MAPS_API_KEY=
ROUTING_API_KEY=
LOG_LEVEL=INFO
POLL_INTERVAL_SECONDS=15
```

Rules:

- Do not commit real secrets.
- Do not configure paid map/geocoding/routing keys without Emad's explicit approval.
- Use `DISTANCE_PROVIDER=haversine` and `GEOCODER_PROVIDER=manual` for no-spend MVP development.
- Rotate `JWT_SECRET` per environment when auth is implemented.

## Docker / Compose Plan

When FastAPI/PostgreSQL implementation begins, use Docker Compose for local development only:

- `api`: FastAPI + Uvicorn service.
- `web`: React/TypeScript/Vite PWA dev server or static build preview.
- `postgres`: PostgreSQL 16 with PostGIS extension enabled.
- Optional later local routing stack: OSRM or GraphHopper only after map data size and host resource impact are reviewed.

Local Compose should expose only localhost ports and should not be treated as a production deployment.

## CI Plan

Recommended GitHub Actions or equivalent CI after repository push approval/use:

1. Backend lint/type/test job:
   - install via `uv` in isolated environment
   - run unit tests
   - run compile/import checks
2. Frontend lint/test/build job once React/Vite is introduced:
   - install locked dependencies
   - run unit tests
   - run production build
3. Security/config checks:
   - secret scan
   - dependency audit where available
   - verify no real API keys in repository
4. Container build check after Dockerfiles exist:
   - build API/web images
   - do not push images unless explicitly approved

## Deployment Options — Not Executed

No deployment was performed. Options for a later approved pilot:

| Option | Fit | Notes |
|---|---|---|
| Single VPS with Docker Compose | Lowest-cost pilot | Good for one small pilot; requires backups, TLS, monitoring setup. |
| Render/Fly.io/Railway-style PaaS + managed Postgres | Fastest ops setup | May cost money; use only after approval. |
| Supabase Postgres + lightweight API hosting | Fast database setup | Good for admin dashboards, but privacy/security review needed. |
| Cloud Run/App Runner + managed Postgres | More production-grade | Higher setup complexity and likely costs. |

## Logging and Monitoring Plan

MVP local/pilot readiness should include:

- Structured JSON logs for API requests, planning runs, status events, publish actions, and auth failures.
- Correlation/request IDs.
- Health endpoints: `/health` and later `/ready`.
- Basic metrics: planning run duration, orders planned/unassigned, status-event count, API error rate, dashboard poll latency.
- Error tracking later, with PII scrubbing.

## Backup / Data Protection Plan

Before any real pilot data:

- Use PostgreSQL automated backups or daily dumps.
- Define retention period.
- Encrypt backups where hosted provider supports it.
- Minimize recipient/customer data exposed to drivers and logs.
- Avoid regulated healthcare claims/workflows until privacy/compliance review is complete.

## Mobile Release Constraints

- MVP should remain a PWA first.
- Native iOS/Android packaging is deferred until product workflow is validated.
- If push notifications are added later, plan APNs/FCM credentials, opt-in UX, and privacy review.
- Offline support should be designed after the API-backed PWA exists.

## Release Gates Before Any Pilot

Do not release externally until all are complete and Emad approves:

- API auth/role isolation implemented and tested.
- Durable PostgreSQL persistence and migrations implemented.
- Manual override audit trail implemented.
- CSV/import row validation implemented.
- No paid/external API keys required by default.
- Secrets are out of source control.
- TLS, backups, logging, and basic monitoring are configured.
- QA signs off on P0 security/privacy and workflow tests.
