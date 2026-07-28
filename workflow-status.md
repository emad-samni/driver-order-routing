# Evening Driver Routing Workflow Status

## Execution Rules
- Agents run strictly in sequence with 30-minute schedule gaps.
- Each stage validates the previous stage completed for the current daily run.
- Stale previous-day outputs are not valid for the current run.
- If validation fails, the agent must skip productive work and write a blocker report.

## Daily Stage Status

| Stage | Agent | Required Input | Required Output | Status | Last Updated | Validation Notes |
|---|---|---|---|---|---|---|
| 1 | Innovation & Research Lead | Project brief/workspace | `reports/innovation-lead.md`, `research.md` | pending | - | Validate project workspace |
| 2 | Product Owner | Stage 1 completed | `reports/product-owner.md`, `product-backlog.md` | pending | - | Validate research/problem/business assumptions |
| 3 | Technical Lead | Stage 2 completed | `reports/technical-lead.md`, `architecture.md`, `sprint-board.md` | pending | - | Validate backlog and route-optimization scope |
| 4 | Backend Developer | Stage 3 completed | `reports/backend-developer.md`, optional `repo/` files | pending | - | Validate backend tasks/API/data model |
| 5 | Frontend Developer | Stage 4 completed | `reports/frontend-developer.md`, optional `repo/` files | pending | - | Validate frontend/API assumptions |
| 6 | QA Engineer | Stage 5 completed | `reports/qa-engineer.md` | pending | - | Validate requirements, tests, UX/API quality |
| 7 | DevOps Engineer | Stage 6 completed | `reports/devops-engineer.md` | pending | - | Validate deployment/ops readiness |
| 8 | Scrum Master | Stage 7 completed | `reports/daily-scrum.md` | pending | - | Consolidate all reports |
| 9 | CEO / Project Director | Stage 8 completed | `reports/ceo-project-director.md`, Telegram final report | pending | - | Final quality review |
