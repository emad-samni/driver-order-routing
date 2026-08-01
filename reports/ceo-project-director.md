Project name: Driver Order Routing

The achievements for the round:
- Added real `.xlsx` upload parser and `/orders/import/excel` FastAPI endpoint, replacing the previous 501 stub
- Added `openpyxl` dependency and parser unit tests
- Added Excel import API tests covering valid upload, malformed workbook, and row error behavior
- Added frontend `apiClient` wrapper for `/excel-template`, `/orders/import/excel`, and `/import-batches/{id}`
- Backend QA passes: 19 tests OK

Blockers if exist:
- Frontend export/test alignment still needs a small follow-up patch to ensure `api`/`apiClient` exposure and test assertions are clean
- No deployment, external contact, spending, or public hosting approved

What will be next:
- PostgreSQL/Alembic persistence and tenant-scoped data models
- Authentication/RBAC and driver route isolation
- React/Vite PWA frontend wired to live APIs
- Mobile viewport testing and expanded API integration tests
