# Research — Driver Order Routing App

_Last updated: 2026-07-30T13:01:33Z by Evening Stage 1 — Innovation & Research Lead_

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
Small and mid-sized delivery/logistics operators often coordinate deliveries through Excel, WhatsApp/phone calls, paper manifests, and manual Google Maps planning. This creates recurring operational waste:
- Dispatchers spend time manually grouping retailer orders by area, time window, vehicle, and driver.
- Drivers receive unclear stop order, causing avoidable distance, fuel use, missed slots, and late deliveries.
- Admins lack real-time visibility and must call drivers for status.
- Failed deliveries rise when recipient availability, building access, bulky-item service time, and driver working hours are not captured or respected.
- Proof of delivery is often manual or inconsistent, making disputes with customers or retailer clients harder to resolve.

### Market direction
The last-mile delivery software market is large and growing. Future Market Insights estimates the global market at USD 15.2B in 2025, expanding to USD 41.5B by 2035 at 10.6% CAGR, with cloud-based deployment leading and e-commerce as a major vertical. Western Europe-specific research also points to sustained growth, with Future Market Insights estimating a 10.3% CAGR from 2025 to 2035 and Germany as a leading Western European market. Persistence Market Research describes route optimization/planning as a top application, with Europe representing a significant share of global last-mile software demand and Germany expected to be a major national market.

For this project's clarified pilot geography, Germany and the Netherlands are attractive because both markets have dense e-commerce and retail delivery activity, mature logistics ecosystems, urban congestion/emission pressure, and high customer expectations around delivery slots. This supports a practical B2B wedge for small logistics subcontractors that serve large retailers but still plan routes through Excel, phone calls, and manual maps.

### Why now
- Retailers increasingly expect delivery partners to provide predictable time windows, status visibility, and cleaner handoffs.
- Fuel, driver labor, urban congestion, and emissions pressure make distance/time reductions commercially visible.
- Mobile-first workflows are now acceptable for small teams; dispatch can run from a phone, tablet, or lightweight web dashboard.
- Open-source and pay-as-you-go routing/geocoding tools make practical route optimization feasible without building a full mapping stack.
- Excel remains a common operational bridge for small subcontractors, creating a low-friction MVP entry point.

## 3. Target Customer Segments

| Segment | Pain intensity | Willingness to pay | MVP fit | Notes |
|---|---:|---:|---:|---|
| Small delivery/logistics companies serving large retailers, furniture, electronics, appliances, and bulky-goods stores | High | Medium-High | Very High | Matches Emad's clarified pilot: Germany/Netherlands, English UI, Excel intake, one warehouse, all drivers starting at warehouse, about 200 orders/day. Strong need for time windows, capacity/vehicle constraints, route sequencing, and admin visibility. |
| Small delivery businesses serving multiple local retailers | High | Medium | High | Adjacent expansion after one-retailer/one-warehouse pilot; needs multi-client reporting and flexible import formats. |
| Local shops delivering bulky or scheduled goods | Medium-High | Medium | High | Strong scheduled-delivery fit but may have lower daily route density than logistics subcontractors. |
| Grocery / specialty food / prepared meals with planned batches | High | Medium | Medium-High | Good later niche, but less aligned with the clarified bulky/retailer pilot and may need freshness/delivery-speed constraints. |
| Pharmacies / medical supply delivery | High | Medium-High | Deprioritized | Operationally attractive but explicitly not the first pilot focus; could introduce privacy/compliance complexity. |
| Restaurants/cloud kitchens with own drivers | High | Low-Medium | Low-Medium | Fast dynamic dispatch need, but lower margins and marketplace competition make this a weaker first wedge. |

## 4. Recommended Initial Niche

### Most promising target niche
**Small delivery/logistics companies in Germany and the Netherlands that deliver scheduled retailer orders for large retailers such as IKEA, MediaMarkt, furniture/electronics stores, appliance sellers, and similar bulky-goods or planned-delivery merchants.**

### Reasoning
- This directly matches Emad's clarified pilot direction and avoids pharmacy-specific positioning.
- These operators often receive orders from retailer systems/spreadsheets but need to transform them into executable driver routes quickly.
- Bulky/scheduled deliveries make capacity, vehicle type, delivery duration, customer availability, parking/access notes, and working-hour constraints more important than in simple parcel routes.
- At about 200 orders/day, even modest distance/fuel and dispatcher-time savings can justify subscription pricing.
- A one-warehouse/all-drivers-start-at-warehouse assumption is realistic for the first MVP while preserving a later path to multi-depot operations.
- Adjacent expansion is natural: other retailer subcontractors, local courier companies, specialty shops, grocery/subscription deliveries, and field-service routing.

### Positioning statement
"A mobile-first routing command center for small retailer-delivery fleets: upload Excel orders, choose the optimization strategy, assign warehouse-start routes to drivers, respect customer availability, and monitor every delivery from dispatch to proof — without enterprise logistics complexity."

## 5. Competitor / Pattern Notes

### Route and delivery management competitors
- **Onfleet**: Strong high-volume/on-demand delivery platform, driver/customer experience, predictive ETAs, branded tracking. Useful benchmark for real-time admin visibility and driver UX.
- **Routific**: Known for planned next-day route optimization, small/mid-sized local delivery, simple routing. Useful benchmark for batch route planning and small-business friendliness.
- **OptimoRoute**: Handles richer constraints such as time windows, capacity, pickup/delivery, multi-day routes; benchmark for optimization depth.
- **Route4Me / Circuit / Spoke / Zeo / MyRouteOnline**: Popular route planning/driver tools; emphasize multi-stop planning, Excel/import workflows, driver mobile usage, and simple route execution.
- **Track-POD**: Delivery management with route planning, real-time tracking, proof of delivery, signatures/photos, barcode scanning, notifications, and offline driver app. Strong benchmark for proof/status requirements.
- **Shipday**: Local delivery management with live driver tracking, automated driver assignment, customer notifications, and proof of delivery. Good benchmark for local shops/restaurants.
- **DispatchTrack / OnTime 360 / eLogii / Locus / WorkWave / Bringg / FarEye / LogiNext**: Mature delivery orchestration / enterprise or SMB offerings with advanced dispatch, analytics, proof of delivery, integrations, customer communication, and exception management.

### Competitive gap for this project
The market is crowded, so the MVP should not be a generic route planner. The opportunity is a focused product for small retailer-delivery subcontractors:
- Excel upload as a first-class intake path.
- One-warehouse, scheduled-delivery planning before complex multi-depot/dynamic dispatch.
- Configurable optimization options that are understandable to dispatchers.
- Mobile-first admin and driver experience.
- Driver route execution, status updates, note/timestamp proof, and exception reporting.
- Designed for non-technical small teams in Germany/Netherlands with low setup friction.
- Simple pricing and practical ROI story around dispatcher time, distance/fuel proxy, and fewer failed deliveries.

## 6. Route Optimization Options

### MVP optimization requirement
The MVP needs practical, explainable optimization, not perfect mathematical optimality. It should handle:
- Daily Excel import around 200 orders/day.
- One warehouse/pickup location and all drivers starting there.
- Multiple drivers.
- Driver working hours.
- Order time windows / recipient availability.
- Optional capacity/vehicle limit, package size/weight, service time, and access notes.
- Manual admin overrides.
- Configurable optimization objectives: distance/fuel proxy, on-time priority, balanced workload, strict constraints, and relaxed/manual-review mode.

### Options

1. **OR-Tools + distance/time matrix**
   - Pros: Open-source, supports vehicle routing, time windows, capacity constraints, vehicle limits, and extensibility.
   - Cons: Requires distance matrix source; implementation complexity; route quality depends on travel-time data.
   - Fit: Best MVP optimization core once the data model and import workflow are stable.

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
   - Examples: Excel import, normalize addresses, geocode or use provided coordinates, cluster by area/capacity/vehicle type, sort by nearest-neighbor while respecting time windows and driver shifts, flag unassignable stops.
   - Pros: Fast to build, explainable, usable for pilots.
   - Cons: Not globally optimal; may fail complex constraints.
   - Fit: Best first prototype if no paid APIs and limited implementation time.

### Recommended optimization path
- Prototype: simple heuristic with mocked/geocoded coordinates and manual matrix or free/local routing where available.
- MVP: OR-Tools VRP with time windows, capacity/vehicle constraints, service time, one depot/warehouse, and a configurable distance/time provider.
- Commercial version: add production geocoding, traffic-aware ETA, re-optimization, multi-depot, customer notifications, and advanced analytics.

## 7. Extra Requirements Emad Did Not Explicitly List

### Operational requirements
- Excel import as the primary MVP intake, with CSV/copy-paste/manual entry as later convenience paths.
- Import field mapping and validation preview before route optimization.
- Address validation and geocoding confidence; flag ambiguous addresses before routing.
- Manual assignment/drag-and-drop override by admin.
- Unassigned/at-risk order queue with reasons: outside time window, over capacity, missing address, driver shift conflict, vehicle mismatch, access/service-time issue.
- Driver break time, helper/crew needs for bulky goods, vehicle category, capacity, and maximum stops/distance per shift.
- Service duration per stop.
- Delivery priority and promised-by time.
- Re-optimization when orders are added/cancelled or a driver falls behind.
- Delivery zones/territories, vehicle/service skills, lift-gate/large-item handling, parking/access notes, and driver permissions.
- Return-to-warehouse / failed-delivery disposition for undelivered goods.

### Driver mobile workflow
- Login/account for drivers.
- Today route list with next stop highlighted.
- One-tap status updates: accepted, en route, arrived, delivered, failed, returned.
- Navigation handoff to Google Maps/Apple Maps/Waze.
- Call/message customer from stop card if customer phone is provided; phone remains optional.
- Capture proof of delivery: MVP note + timestamp; later photo, signature, geotag, barcode/QR scan, and customer confirmation if approved.
- Offline mode for route list and status queue with later sync.
- Driver cannot easily skip required proof fields where policy requires them.

### Admin workflow
- Mobile-responsive dashboard with map/list views; list-first route review is enough for early MVP.
- Real-time or near-real-time driver status and route progress.
- Filter by late, failed, unassigned, high-priority, driver, route, zone, or retailer client.
- Manual dispatch updates and reassignment.
- Customer/retailer notification templates via SMS/WhatsApp/email later.
- Export delivery reports and daily route summaries.
- Basic analytics: distance planned vs actual, stops/driver, failed attempts, on-time rate, fuel-distance proxy, manual override rate.

### Data/security requirements
- Role-based access: admin, dispatcher, driver.
- Tenant separation for each business.
- Audit log of assignment/status changes.
- Minimal customer personal data exposure to drivers: only assigned stops.
- Data retention controls for delivery proof notes/photos/signatures if added later.
- GDPR/privacy review for Germany/Netherlands before real pilot data is stored.

## 8. MVP Assumptions

- Start with one responsive web app/PWA with role-based admin and driver views, not separate native apps.
- Main product language is English.
- Admin imports orders from Excel for the first pilot; manual entry/editing is useful but secondary.
- First pilot uses one warehouse/pickup location and assumes all drivers start from that warehouse.
- Initial planning scale is about 200 orders/day.
- Orders require order ID, customer name, address, availability/time window, service duration/default, and optional phone/notes/preferences.
- Drivers have shift start/end, capacity/max stops, vehicle constraints, and status; current-location routing can be phase 2 after warehouse-start planning works.
- Optimization is admin-triggered initially and exposes strategy options such as shortest distance/fuel proxy, on-time priority, balanced workload, max stops, or strict/relaxed time-window handling.
- Driver route execution is mobile-first with status updates and proof note + timestamp in MVP.
- Real-time can be approximated initially with frequent refresh/WebSocket later; full GPS live tracking can be phase 2.
- Navigation is handed off to external map apps instead of building in-app turn-by-turn navigation.
- Customer notifications are phase 2 unless quick email/SMS/WhatsApp integration is explicitly approved.

## 9. Monetization Options

| Model | Pros | Cons | Recommendation |
|---|---|---|---|
| Per-driver monthly subscription | Easy to understand; aligns with fleet size | Small teams may churn if seasonal | Primary model |
| Per-order/stop pricing | Aligns with usage and value | Harder to predict bill; may discourage usage | Add-on or high-volume tier |
| Flat small-business plan | Simple buying decision | Can underprice heavy users | Starter tier |
| Setup/import/onboarding fee | Helps service-heavy Excel/client deployments | Friction for MVP | Optional for managed onboarding |
| Vertical premium modules | Notifications, live GPS, analytics, integrations, advanced proof | Requires mature product | Later expansion |

### Suggested early pricing hypothesis
- Starter: low monthly fee for 1–3 drivers and limited stops/day.
- Growth: per-driver/month for 4–25 drivers with optimization and proof/status workflows.
- Operations tier: higher daily order volume, Excel templates, reporting exports, route history, and priority support.
- Premium: advanced notifications, live GPS, analytics, API integrations, multi-depot, and advanced proof-of-delivery.

## 10. Commercial Potential

Commercial potential is credible if the product focuses on a painful, narrow workflow instead of competing broadly with mature delivery suites. The most monetizable wedge is "Excel-to-optimized-routes + mobile driver execution for small retailer-delivery subcontractors in Germany/Netherlands." The product can expand horizontally after proving measurable savings:
- Reduced dispatcher planning time.
- Reduced route distance/fuel proxy.
- Improved on-time rate.
- Fewer failed delivery attempts.
- Less driver/admin phone coordination.
- Cleaner reporting back to retailer clients.

## 11. Recommended MVP Opportunity

Build a lightweight, mobile-first dispatch and driver execution MVP:
1. Admin uploads the daily Excel file from the retailer/client.
2. System validates required fields, address/geocoding confidence, time windows, service duration, vehicle/capacity fields, and warehouse-start assumptions.
3. Admin chooses optimization configuration: minimize distance/fuel proxy, prioritize on-time delivery, balance workload, or respect strict constraints.
4. System assigns orders to drivers and sequences stops from the warehouse, flagging unassigned/at-risk orders with reasons.
5. Admin reviews list-first route plans, adjusts assignments manually, then publishes to drivers.
6. Driver sees assigned stops on mobile, opens external navigation, and updates statuses.
7. Admin monitors route progress, exceptions, failed deliveries, and proof notes/timestamps.
8. Reports show planned distance/time, completed/failed orders, late/at-risk stops, and exception reasons.

## 12. Key Sources Consulted

- Future Market Insights, "Last Mile Delivery Software Market" — market size, growth, cloud deployment, real-time delivery control trends: https://www.futuremarketinsights.com/reports/last-mile-delivery-software-market
- Future Market Insights, "Western Europe Last-mile Delivery Software Market" — Western Europe 2025–2035 CAGR, Germany/Benelux relevance, cloud/e-commerce trends: https://www.futuremarketinsights.com/reports/industry-analysis-of-last-mile-delivery-software-in-western-europe
- Persistence Market Research, "Last-Mile Delivery Software Market Size & Forecast, 2033" — route optimization/planning share, Europe and Germany demand notes: https://www.persistencemarketresearch.com/market-research/last-mile-delivery-software-market.asp
- Google OR-Tools documentation, "Vehicle Routing Problem" — VRP and time-window capable optimization approach: https://developers.google.com/optimization/routing/vrp
- Google OR-Tools documentation, "Vehicle Routing Problem with Time Windows" — time-window constraints and feasible route timing patterns: https://developers.google.com/optimization/routing/vrptw
- Track-POD product site — delivery management patterns: proof of delivery, real-time tracking, notifications, offline driver app: https://www.track-pod.com/
- Onfleet route optimization software comparison — competitor positioning for high-volume/on-demand delivery and driver/customer experience: https://onfleet.com/blog/best-route-optimization-software/
- Routific route-planning materials — small/mid-sized planned local delivery positioning and route planning patterns: https://www.routific.com/blog/best-route-planning-software-for-deliveries
- IKEA Germany delivery service page — supports relevance of furniture/retail delivery workflows and business delivery context: https://www.ikea.com/de/en/customer-service/services/delivery/
