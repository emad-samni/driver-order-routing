# Frontend Prototype — Driver Routing MVP

Dependency-free mobile-first frontend prototype for Stage 5.

## Files
- `index.html` — shell with mobile viewport and app mount.
- `styles.css` — responsive PWA-style UI for admin/dispatcher and driver screens.
- `app.js` — sample-state renderer, backend endpoint mapping, Excel import/template UI state, route/status helpers, and interactive role/status switching.
- `tests/frontend.test.js` — dependency-free Node unit checks for helper logic and rendered UI landmarks.

## Run locally

From this directory:

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173` in a browser or mobile emulator.

## Test

```bash
node tests/frontend.test.js
```

## Scope

The prototype is intentionally static until the FastAPI wrapper exists. It is structured around the backend API contract:
- `GET /excel-template`
- `POST /orders/import/excel`
- `GET /import-batches/{id}`
- `POST /orders`
- `GET /orders`
- `POST /drivers`
- `POST /planning-runs`
- `POST /planning-runs/{id}/publish`
- `GET /driver/me/routes/today`
- `POST /orders/{id}/status-events`
- `GET /dashboard/dispatch`

## Implemented UX coverage

- Mobile-first admin/dispatcher shell.
- Excel template visibility and .xlsx upload action placeholder.
- Import batch summary cards for total, ready, draft, and error rows.
- Row-level validation result cards with row number, field, error code, draft/rejected status, and suggested fix.
- Configurable planning controls for balanced, distance/fuel proxy, on-time, and workload strategies plus strict/relaxed constraint mode.
- Route review, exception queue, publish, manual override audit-note placeholder, driver route cards, external navigation links, and proof/failure note UX.

## Recommended implementation path

Keep the MVP as a React + TypeScript + Vite PWA when moving from prototype to production-grade UI. This static prototype proves the UX structure without adding package dependencies during the current scheduled run.
