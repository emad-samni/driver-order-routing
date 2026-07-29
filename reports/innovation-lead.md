# Innovation Lead Report — Driver Routing

_Last updated: 2026-07-29T15:49:54Z_

## Validation

Stage 1 prerequisite validation passed. Required project workspace files were present:
- `project-brief.md`
- `workflow-status.md`
- `research.md`
- `decisions/decision-log.md`
- `reports/innovation-lead.md`

## Market Need Summary

There is a clear market need for small delivery teams that currently coordinate with spreadsheets, calls, WhatsApp, and manual route planning. The operational pain is strongest where delivery failure is costly, customer availability matters, and proof/status visibility is required.

External research supports a growing last-mile delivery software market, with demand shifting from simple dispatch to cloud-based delivery orchestration, real-time tracking, route optimization, customer-facing updates, and proof-of-delivery workflows.

## Competitor Findings

The category is crowded, so the product should avoid generic "route planner" positioning. Key competitor patterns:
- Onfleet: strong high-volume/on-demand delivery UX, tracking, ETAs, branded experience.
- Routific: simple planned-route optimization for small/mid-sized local delivery.
- OptimoRoute: richer route constraints and fleet planning.
- Track-POD: proof of delivery, real-time tracking, route planning, offline mobile workflows.
- Shipday and similar tools: local delivery tracking, notifications, driver assignment.

The competitive opening is a simpler vertical-focused MVP for small operators with availability/time-window needs and low operational sophistication.

## Recommended Target Niche

Recommended initial niche: **small pharmacies, medical supply providers, and recurring-care delivery teams with 2–25 drivers/orders batches per day.**

Reasoning:
- Stronger willingness to pay than restaurants or NGOs.
- Customer availability/time windows and proof/status workflows are central.
- Failed deliveries and admin-driver phone coordination have real cost.
- A healthcare-adjacent wedge can later expand to groceries, prepared meals, florists, and local retail.

Recommended positioning:
> A mobile-first delivery command center for small healthcare and local delivery teams: import orders, respect customer availability, assign drivers, optimize stop sequence, and track every delivery in real time — without enterprise logistics complexity.

## MVP Opportunity

Build a lightweight mobile-first dispatch and driver execution MVP:
1. Admin imports or manually creates orders and drivers.
2. System validates address/time-window/driver-shift feasibility.
3. Admin triggers assignment and sequence optimization.
4. Admin reviews route plan and manually overrides if needed.
5. Driver sees assigned route on mobile, opens navigation externally, and updates stop status.
6. Admin monitors progress and exceptions.
7. Basic reporting shows planned distance/time, completed/failed orders, late/at-risk stops, and exception reasons.

## Optimization Recommendation

Recommended route optimization path:
- Prototype: simple explainable heuristic for clustering/sequencing and feasibility flags.
- MVP: OR-Tools VRP with time windows, capacity, service time, driver shifts, and a pluggable distance/time matrix provider.
- Later commercial version: production geocoding, traffic-aware ETA, customer notifications, live GPS tracking, re-optimization, and advanced analytics.

## Extra Requirements Identified

Important requirements beyond the brief:
- CSV/XLS import and copy-paste order entry.
- Address validation/geocoding confidence and ambiguous-address resolution.
- Manual assignment/drag-and-drop override.
- Unassigned/at-risk order queue with reason codes.
- Driver service time, breaks, max stops/distance, vehicle/capacity constraints.
- Proof of delivery: photo, signature/note, geotag, timestamp.
- Offline-capable driver route/status queue.
- Role-based access, tenant separation, audit log, and privacy-minded data retention.
- Admin exception dashboard for late, failed, unassigned, or high-priority orders.

## Monetization Recommendation

Primary pricing hypothesis:
- Starter flat plan for very small teams.
- Growth plan priced per driver/month.
- Optional per-stop usage tier for higher volume.
- Premium modules later for customer notifications, live GPS, compliance/privacy controls, integrations, and analytics.

## Decisions Recommended / Recorded

Recorded Stage 1 decisions in `decisions/decision-log.md`:
- Focus initial niche on small healthcare/local recurring delivery teams.
- Build a role-based mobile-first PWA/responsive app before separate native apps.
- Use OR-Tools/pluggable routing path for MVP, with simple heuristic acceptable for prototype.
- Prioritize admin override, proof/status, and exception handling as differentiators.

## Yesterday / Completed

- Validated required workspace files exist.
- Completed market, competitor, optimization, workflow, monetization, and target-niche research.
- Updated `research.md` with detailed findings and MVP assumptions.
- Prepared this Stage 1 report.

## Current Progress

Stage 1 is complete and ready for Stage 2 Product Owner to convert research into backlog, MVP scope, user stories, acceptance criteria, and product priorities.

## Next Actions

- Product Owner should define the MVP user personas, core journeys, and backlog.
- Confirm the first vertical assumption: small pharmacy/medical-supply/local recurring delivery teams.
- Convert extra requirements into phased MVP vs post-MVP scope.
- Define measurable MVP success metrics: planning time saved, distance reduction, on-time rate, failed delivery rate, and driver/admin call reduction.

## Risks / Blockers

- No blocker for Stage 1.
- Main risk: market is crowded; product must focus on a niche and workflow simplicity rather than generic route optimization.
- Technical risk: real geocoding/traffic-aware travel times may require paid APIs later; no spending should occur without explicit approval.
- Healthcare-adjacent niche may introduce privacy/compliance needs; MVP should avoid regulated claims until requirements are reviewed.
