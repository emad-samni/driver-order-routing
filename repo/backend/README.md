# Driver Routing Backend Prototype

Dependency-light Python prototype for Stage 4 Backend Developer work.

## What is included

- `app/domain.py` — order, driver, planning, route, status, and validation models.
- `app/planner.py` — deterministic no-spend greedy route planner using coordinate distance estimates.
- `app/service.py` — in-memory service layer matching the planned FastAPI endpoints.
- `docs/api-and-schema.md` — API contract, PostgreSQL/PostGIS-ready schema, validation rules, and unit-test plan.
- `tests/test_routing_service.py` — executable unit tests for core MVP backend behavior.

## Run tests

From this directory:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

No external APIs, deployment, database, or paid services are used.

## Next implementation step

Wrap `RoutingService` in FastAPI endpoints and replace in-memory dictionaries with PostgreSQL persistence once the team is ready to add dependencies and database runtime.
