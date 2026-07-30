# Innovation Lead Report — Driver Routing

_Last updated: 2026-07-30T13:01:33Z_

## Validation

Stage 1 prerequisite validation passed. Required project workspace files were present:
- `project-brief.md`
- `workflow-status.md`
- `research.md`
- `decisions/decision-log.md`
- `reports/innovation-lead.md`

## Market Need Summary

There is a clear market need for small delivery/logistics teams that currently coordinate retailer delivery work through Excel sheets, calls, WhatsApp, and manual route planning. The operational pain is strongest where daily order volume is high enough to make manual planning expensive, customer availability/time windows matter, vehicle/capacity constraints matter, and dispatchers need proof/status visibility without enterprise logistics complexity.

External research supports a growing last-mile delivery software market, with demand shifting from simple dispatch to cloud-based delivery orchestration, real-time tracking, route optimization, customer-facing updates, exception handling, and proof-of-delivery workflows. Germany and the Netherlands/Benelux remain attractive pilot markets because of dense e-commerce/retail logistics, high delivery-slot expectations, urban congestion, and pressure to reduce vehicle kilometres/fuel/emissions.

## Competitor Findings

The category is crowded, so the product should avoid generic "route planner" positioning. Key competitor patterns:
- Onfleet: strong high-volume/on-demand delivery UX, tracking, ETAs, branded experience.
- Routific: simple planned-route optimization for small/mid-sized local delivery.
- OptimoRoute: richer route constraints and fleet planning.
- Route4Me / Circuit / Zeo / MyRouteOnline: practical multi-stop routing, Excel/import patterns, and mobile driver workflows.
- Track-POD: proof of delivery, real-time tracking, route planning, offline mobile workflows.
- Bringg / FarEye / LogiNext / Locus / DispatchTrack / eLogii: mature orchestration, analytics, integrations, and enterprise/SMB delivery operations.

The competitive opening is a simpler vertical-focused MVP for retailer-delivery subcontractors: Excel upload, one-warehouse route planning, configurable optimization, mobile driver execution, note/timestamp proof, and admin exception control.

## Recommended Target Niche

Recommended initial niche: **small delivery/logistics companies in Germany and the Netherlands that deliver scheduled orders for large retailers such as IKEA, MediaMarkt, furniture/electronics stores, appliance sellers, and similar bulky-goods or planned-delivery merchants.**

Reasoning:
- This matches Emad's clarified direction and explicitly avoids pharmacy-specific positioning.
- These operators commonly need to transform retailer order spreadsheets into practical driver routes.
- Customer availability/time windows, bulky-item service duration, vehicle/capacity constraints, and working hours are central.
- At about 200 orders/day, route distance/fuel reduction and dispatcher time savings can create visible ROI.
- A one-warehouse/all-drivers-start-at-warehouse MVP is realistic for the first pilot and keeps optimization tractable.

Recommended positioning:
> A mobile-first routing command center for small retailer-delivery fleets: upload Excel orders, choose the optimization strategy, assign warehouse-start routes to drivers, respect customer availability, and monitor every delivery from dispatch to proof — without enterprise logistics complexity.

## MVP Opportunity

Build a lightweight mobile-first dispatch and driver execution MVP:
1. Admin uploads a daily Excel file from the retailer/client.
2. System validates required order fields, addresses/geocoding confidence, time windows, service duration, vehicle/capacity fields, and one-warehouse assumptions.
3. Admin chooses optimization configuration: shortest distance/fuel proxy, on-time priority, balanced workload, strict constraints, or relaxed/manual-review mode.
4. System assigns orders and sequences stops from the warehouse, flagging unassigned/at-risk orders with reason codes.
5. Admin reviews list-first route plans and manually overrides before publishing.
6. Driver sees assigned route on mobile, opens external navigation, and updates stop status.
7. Driver proof is note + timestamp for MVP; photos/signatures/geotags remain later options.
8. Admin monitors progress and exceptions; basic reporting shows planned distance/time, completed/failed orders, late/at-risk stops, and exception reasons.

## Optimization Recommendation

Recommended route optimization path:
- Prototype: simple explainable heuristic for clustering/sequencing and feasibility flags.
- MVP: OR-Tools VRP with one depot/warehouse, time windows, capacity/vehicle constraints, service time, driver shifts, and a pluggable distance/time matrix provider.
- Later commercial version: production geocoding, traffic-aware ETA, customer notifications, live GPS tracking, re-optimization, multi-depot, and advanced analytics.

## Extra Requirements Identified

Important requirements beyond the original brief:
- Excel import as the first pilot intake, with CSV/copy-paste/manual entry later.
- Import field mapping and validation preview.
- Address validation/geocoding confidence and ambiguous-address resolution.
- Manual assignment/drag-and-drop override.
- Unassigned/at-risk order queue with reason codes.
- Driver service time, breaks, max stops/distance, vehicle/capacity constraints, bulky-item handling needs, and access/parking notes.
- Proof of delivery: MVP note + timestamp; later photo/signature/geotag/barcode if needed.
- Offline-capable driver route/status queue.
- Role-based access, tenant separation, audit log, and GDPR/privacy-minded data retention.
- Admin exception dashboard for late, failed, unassigned, high-priority, or vehicle-mismatch orders.

## Monetization Recommendation

Primary pricing hypothesis:
- Starter flat plan for very small teams.
- Growth plan priced per driver/month.
- Optional per-stop/order volume tier for high-volume operators.
- Optional onboarding/import-template setup fee for Excel-heavy pilots.
- Premium modules later for customer notifications, live GPS, advanced proof, analytics, integrations, and multi-depot routing.

## Decisions Recommended / Recorded

Recorded Stage 1 decisions in `decisions/decision-log.md`:
- Retarget the first niche to small retailer-delivery/logistics subcontractors in Germany/Netherlands, consistent with Emad's clarification.
- Position the product as Excel-to-optimized warehouse-start routes for retailer-delivery fleets, not a generic route planner.
- Use Excel upload, one warehouse, warehouse-start drivers, and configurable optimization as first-pilot assumptions.
- Build a role-based mobile-first PWA/responsive app before separate native apps.
- Use OR-Tools/pluggable routing path for MVP, with simple heuristic acceptable for prototype.
- Prioritize admin override, proof/status, and exception handling as differentiators.

## Yesterday / Completed

- Validated required workspace files exist for the current run.
- Reconciled Stage 1 research with Emad's clarified pilot: small delivery/logistics companies serving large retailers in Germany/Netherlands; not pharmacy-specific.
- Refreshed market, competitor, optimization, monetization, MVP assumption, and extra-requirement notes.
- Updated `research.md`, `reports/innovation-lead.md`, `workflow-status.md`, and `decisions/decision-log.md`.

## Current Progress

Stage 1 is complete for the current evening run and ready for Stage 2 Product Owner to convert the clarified niche into backlog, MVP scope, user stories, acceptance criteria, and product priorities.

## Next Actions

- Product Owner should define personas for logistics owner/admin dispatcher, driver, and retailer/client operations contact.
- Convert Excel upload, one warehouse, 200 orders/day, configurable optimization, mobile route execution, and proof note/timestamp into prioritized MVP stories.
- Define the Excel import schema and validation error model.
- Define measurable MVP success metrics: planning time saved, distance/fuel proxy reduction, on-time rate, failed delivery rate, driver/admin call reduction, and manual override rate.

## Risks / Blockers

- No blocker for Stage 1.
- Main risk: market is crowded; product must focus on retailer-delivery subcontractor workflows and not compete as a generic route planner.
- Technical risk: real geocoding/traffic-aware travel times may require paid APIs later; no spending should occur without explicit approval.
- Data quality risk: retailer Excel files may contain inconsistent address/time-window fields, so import validation and exception handling are essential.
