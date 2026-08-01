Project name: Driver Order Routing

The achievements for the round:
- Implemented real `.xlsx` parser in `repo/backend/app/import_parser.py` using `openpyxl`
- Replaced `/orders/import/excel` 501 stub with a working FastAPI endpoint
- Added backend API tests for Excel import and parser unit tests
- Added `openpyxl` to backend dependencies
- Verified backend test suite: 19 tests OK

Blockers if exist:
- None

What will be next:
- PostgreSQL/Alembic persistence
- Auth/RBAC/tenant isolation
- API-backed React/Vite PWA frontend
- Mobile viewport testing and expanded QA coverage
