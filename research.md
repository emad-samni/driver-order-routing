# Research — Driver Order Routing App

_Last updated: 2026-07-29T15:49:54Z by Evening Stage 1 — Innovation & Research Lead_

## 1. Workspace Validation

Validated required workspace files exist before productive work:
- `project-brief.md`
- `workflow-status.md`
- `research.md`
- `decisions/decision-log.md`
- `reports/innovation-lead.md`

No blocker found for Stage 1.

## 2. Market Need

### Core problem
Small and mid-sized delivery operators often coordinate deliveries through spreadsheets, WhatsApp/phone calls, paper manifests, and manual Google Maps planning. This creates recurring operational waste:
- Dispatchers spend time manually grouping orders by area and driver.
- Drivers receive unclear stop order, causing avoidable distance, fuel use, and late deliveries.
- Admins lack real-time visibility and must call drivers for status.
- Failed deliveries rise when customer availability/time windows are not captured or respected.
- Proof of delivery is often manual or inconsistent, making disputes hard to resolve.

### Market direction
The last-mile delivery software market is large and growing. Future Market Insights estimates the market at USD 15.2B in 2025, expanding to USD 41.5B by 2035 at 10.6% CAGR, with cloud-based deployment leading and e-commerce as a major vertical. The same report notes demand moving from basic dispatch support toward real-time delivery control, route optimization, proof-of-delivery workflows, and customer-facing tracking.

### Why now
- Local retailers and service businesses increasingly need same-day/next-day delivery expectations without enterprise logistics budgets.
- Fuel and driver labor remain meaningful cost drivers, making even simple distance/time reductions commercially valuable.
- Mobile-first workflows are now acceptable for small teams; dispatch can run from a phone or tablet.
- Open-source and pay-as-you-go routing/geocoding tools make MVP route optimization feasible without building a full mapping stack.

## 3. Target Customer Segments

| Segment | Pain intensity | Willingness to pay | MVP fit | Notes |
|---|---:|---:|---:|---|
| Pharmacies / medical supply delivery | High | High | High | Time windows, recipient availability, proof of delivery, privacy/security matter. Strong operational pain; may need compliance later. |
| Local grocery / specialty food / prepared meals | High | Medium | High | Planned routes, recurring customers, freshness windows, failed delivery costs. Good MVP niche. |
| Florists / gift delivery | Medium | Medium | High | Date/time commitments and route batching; seasonal peaks. |
| Small courier/document delivery | Medium-High | Medium | Medium | May need dynamic dispatch, proof of delivery, customer notifications. Competitive market. |
| Restaurants/cloud kitchens with own drivers | High | Low-Medium | Medium | Need speed/live dispatch but may already use marketplace apps; margins tight. |
| NGOs/community meal delivery | High | Low | Medium | Strong mission fit but weaker monetization; useful pilot/reference segment. |

## 4. Recommended Initial Niche

### Most promising target niche
**Small pharmacies, medical supply providers, and recurring-care delivery teams with 2–25 drivers/orders batches per day.**

### Reasoning
- They have stronger willingness to pay than restaurants because failed delivery, missed recipient availability, and proof disputes are costly.
- Customer availability/time windows are central, matching Emad's stated requirements.
- Real-time admin visibility and proof of delivery can differentiate beyond simple route planning.
- The niche can start with simple non-regulated delivery operations, then evolve toward stronger privacy/compliance features if traction appears.
- Adjacent expansion is natural: groceries, prepared meals, subscription food, florists, and local retail.

### Positioning statement
"A mobile-first delivery command center for small healthcare and local delivery teams: import orders, respect customer availability, assign drivers, optimize stop sequence, and track every delivery in real time — without enterprise logistics complexity."

## 5. Competitor / Pattern Notes

### Route and delivery management competitors
- **Onfleet**: Strong high-volume/on-demand delivery platform, driver/customer experience, predictive ETAs, branded tracking. Likely more expensive/complex for very small teams; good benchmark for driver UX and admin visibility.
- **Routific**: Known for planned next-day route optimization, small/mid-sized local delivery, simple routing. Useful benchmark for batch planning and small-business friendliness.
- **OptimoRoute**: Handles richer constraints such as time windows, capacity, pickup/delivery, multi-day routes; benchmark for optimization depth.
- **Route4Me / Circuit / Spoke / Zeo**: Popular route planning/driver tools; emphasize multi-stop planning, driver mobile usage, and simple route execution.
- **Track-POD**: Delivery management with route planning, real-time tracking, proof of delivery, signatures/photos, barcode scanning, notifications, and offline driver app. Strong benchmark for MVP-adjacent requirements.
- **Shipday**: Local delivery management with live driver tracking, automated driver assignment, customer notifications, and proof of delivery. Good benchmark for local shops/restaurants.
- **DispatchTrack / OnTime 360 / eLogii / Locus / WorkWave**: More mature delivery orchestration / enterprise or SMB offerings with advanced dispatch, analytics, proof of delivery, and integrations.

### Competitive gap for this project
The market is crowded, so the MVP should not be a generic route planner. The opportunity is a simpler, vertical-focused product:
- Mobile-first admin and driver experience.
- Designed for non-technical small teams.
- Availability/time-window-first delivery planning.
- Fast CSV/manual import and WhatsApp-friendly operations.
- Simple pricing and low setup friction.
- Local-language/local-market customization can become an advantage later.

## 6. Route Optimization Options

### MVP optimization requirement
The MVP needs practical, explainable optimization, not perfect mathematical optimality. It should handle:
- Multiple drivers.
- Driver start/current location.
- Driver working hours.
- Order time windows / recipient availability.
- Optional capacity/vehicle limit.
- Service time per stop.
- Manual admin overrides.

### Options

1. **OR-Tools + distance/time matrix**
   - Pros: Open-source, supports vehicle routing, time windows, capacity constraints, extensible.
   - Cons: Requires distance matrix source; implementation complexity; route quality depends on travel-time data.
   - Fit: Best long-term optimization core if technical team can implement a constrained VRP MVP.

2. **Google Maps Platform / Route Optimization / Distance Matrix**
   - Pros: High-quality geocoding, traffic-aware travel times, familiar maps UX.
   - Cons: Usage-based cost; vendor dependency; billing complexity.
   - Fit: Good for production-quality routing/geocoding if budget is approved later. Avoid hard dependency in no-spend prototype.

3. **Mapbox / HERE / TomTom / NextBillion.ai / GraphHopper API**
   - Pros: Logistics-oriented APIs; some lower-cost/flexible options; GraphHopper has open-source path.
   - Cons: Pricing and capability tradeoffs; vendor-specific integration.
   - Fit: Evaluate after MVP assumptions are validated.

4. **OSRM / GraphHopper self-hosted/open-source routing**
   - Pros: Lower marginal cost and avoids per-request billing.
   - Cons: Operations complexity, map data management, less live traffic accuracy.
   - Fit: Good later if volume/cost justifies operational ownership.

5. **Simple heuristic MVP**
   - Examples: geocode orders, cluster by driver capacity/area, sort by nearest-neighbor while respecting time windows, flag unassignable stops.
   - Pros: Fast to build, explainable, usable for pilots.
   - Cons: Not globally optimal; may fail complex constraints.
   - Fit: Best first prototype if no paid APIs and limited implementation time.

### Recommended optimization path
- Prototype: simple heuristic with mocked/geocoded coordinates and manual matrix or free/local routing where available.
- MVP: OR-Tools VRP with time windows and capacity, backed by a configurable distance/time provider.
- Commercial version: add production geocoding, traffic-aware ETA, re-optimization, and customer notifications.

## 7. Extra Requirements Emad Did Not Explicitly List

### Operational requirements
- CSV/XLS import and copy-paste order entry for small teams.
- Address validation and geocoding confidence; flag ambiguous addresses before routing.
- Manual assignment/drag-and-drop override by admin.
- Unassigned/at-risk order queue with reasons: outside time window, over capacity, missing address, driver shift conflict.
- Driver break time and maximum stops/distance per shift.
- Service duration per stop.
- Delivery priority and promised-by time.
- Re-optimization when orders are added/cancelled or a driver falls behind.
- Delivery zones/territories and driver skills/permissions.

### Driver mobile workflow
- Login/account for drivers.
- Today route list with next stop highlighted.
- One-tap status updates: accepted, en route, arrived, delivered, failed, returned.
- Navigation handoff to Google Maps/Apple Maps/Waze.
- Call/message customer from stop card.
- Capture proof of delivery: photo, signature, note, timestamp, geotag.
- Offline mode for route list and status queue with later sync.
- Driver cannot easily skip required proof fields where policy requires them.

### Admin workflow
- Mobile-responsive dashboard with map/list views.
- Real-time driver location/status and route progress.
- Filter by late, failed, unassigned, high-priority, driver, zone.
- Manual dispatch updates and reassignment.
- Customer notification templates via SMS/WhatsApp/email later.
- Export delivery reports and daily route summaries.
- Basic analytics: distance planned vs actual, stops/driver, failed attempts, on-time rate, fuel-distance proxy.

### Data/security requirements
- Role-based access: admin, dispatcher, driver.
- Tenant separation for each business.
- Audit log of assignment/status changes.
- Minimal customer personal data exposure to drivers: only assigned stops.
- Data retention controls for delivery proof photos/signatures.
- Privacy/compliance review before handling sensitive medical deliveries.

## 8. MVP Assumptions

- Start with one responsive web app/PWA with role-based admin and driver views, not separate native apps.
- Admin imports or manually creates orders and drivers.
- Orders require address and time window; phone and notes optional.
- Drivers have start location, shift start/end, capacity/max stops, and status.
- Optimization is admin-triggered initially, with clear warnings for unassigned/problem orders.
- Driver route execution is mobile-first with status updates and optional proof photo/note in MVP.
- Real-time can be approximated initially with frequent refresh/WebSocket later; full GPS live tracking can be phase 2.
- Navigation is handed off to external map apps instead of building in-app turn-by-turn navigation.
- Customer notifications are phase 2 unless quick email/SMS/WhatsApp integration is explicitly approved.

## 9. Monetization Options

| Model | Pros | Cons | Recommendation |
|---|---|---|---|
| Per-driver monthly subscription | Easy to understand; aligns with fleet size | Small teams may churn if seasonal | Primary model |
| Per-order/stop pricing | Aligns with usage and value | Harder to predict bill; may discourage usage | Add-on or high-volume tier |
| Flat small-business plan | Simple buying decision | Can underprice heavy users | Starter tier |
| Setup/import/onboarding fee | Helps service-heavy deployments | Friction for MVP | Optional for managed onboarding |
| Vertical premium modules | Compliance, proof retention, advanced analytics | Requires mature product | Later expansion |

### Suggested early pricing hypothesis
- Starter: low monthly fee for 1–3 drivers and limited stops/day.
- Growth: per-driver/month for 4–25 drivers with optimization and proof of delivery.
- Premium: advanced notifications, live GPS, analytics, API integrations, compliance/privacy controls.

## 10. Commercial Potential

Commercial potential is credible if the product focuses on a painful, narrow workflow instead of competing broadly with mature delivery suites. The most monetizable wedge is "availability-aware route planning + mobile proof/status for small healthcare/local delivery teams." The product can expand horizontally after proving measurable savings:
- Reduced dispatcher planning time.
- Reduced route distance/fuel proxy.
- Improved on-time rate.
- Fewer failed delivery attempts.
- Less driver/admin phone coordination.

## 11. Recommended MVP Opportunity

Build a lightweight, mobile-first dispatch and driver execution MVP:
1. Admin creates/imports orders and drivers.
2. System validates addresses/time windows and flags incomplete orders.
3. Admin triggers route assignment/sequence optimization.
4. Admin reviews map/list result and manually adjusts if needed.
5. Driver sees assigned stops on mobile and updates statuses.
6. Admin monitors route progress and exceptions.
7. Reports show planned distance/time, completed deliveries, failed deliveries, and exception reasons.

## 12. Key Sources Consulted

- Future Market Insights, "Last Mile Delivery Software Market" — market size, growth, cloud deployment, real-time delivery control trends: https://www.futuremarketinsights.com/reports/last-mile-delivery-software-market
- Google OR-Tools documentation, "Vehicle Routing Problem" — VRP and time-window capable optimization approach: https://developers.google.com/optimization/routing/vrp
- Track-POD product site — delivery management patterns: proof of delivery, real-time tracking, notifications, offline driver app: https://www.track-pod.com/
- Onfleet route optimization software comparison — competitor positioning for high-volume/on-demand delivery and driver/customer experience: https://onfleet.com/blog/best-route-optimization-software/
- Routific route-planning materials — small/mid-sized planned local delivery positioning and route planning patterns: https://www.routific.com/blog/best-route-planning-software-for-deliveries
