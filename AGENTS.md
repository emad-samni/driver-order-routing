# Driver Order Routing Project — Evening Work Track

This workspace is the evening project track for Emad's Virtual AI Product Development Team.

## Project Goal
Design and build a mobile-first system to organize delivery drivers and assign customer orders optimally, reducing driving distance, petrol consumption, and operational effort.

## Important Operating Rule
- The morning AI Product Team workflow continues unchanged for autonomous product discovery.
- This project is an additional evening assignment for the same team.
- Agents must use this project workspace for evening work only.
- Emad has approved pushing this project repository to GitHub.
- No deployment, external contact, spending, or production release without separate explicit approval from Emad.

## Product Summary
Inputs:
- Orders: customer name, address, delivery preferences, availability/time windows, order owner/customer constraints, special requirements discovered by team.
- Drivers: driver account, initial/current location, working hours, capacity/limits, optional vehicle info.

Outputs:
- Orders assigned to drivers.
- Optimal delivery sequence per driver to reduce travel distance/petrol consumption.
- Driver mobile app/account to view and manage assigned orders.
- Admin mobile app/dashboard to monitor all orders, drivers, updates, progress, exceptions.

## Core Constraints
- Mobile-first for both drivers and admins.
- Real-time status updates from driver to admin.
- Route/order optimization must respect availability/time windows and driver working hours.
- Prefer MVP simplicity first; advanced optimization can evolve later.

## Sequential Execution
- Evening agents run strictly in sequence with 30-minute gaps.
- Every agent validates previous stage completion in `workflow-status.md` before productive work.
- If validation fails, write a blocker report and stop.

## Shared Files
- `project-brief.md`
- `workflow-status.md`
- `research.md`
- `product-backlog.md`
- `architecture.md`
- `sprint-board.md`
- `decisions/decision-log.md`
- `reports/*.md`
- `repo/` optional prototype area

## Daily Report Sections
Each role report must include:

### Yesterday / Completed
### Current Progress
### Next Actions
### Risks / Blockers
