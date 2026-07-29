# Project Brief — Driver Order Routing & Delivery Assignment App

## Vision
Create a mobile-first product for businesses that deliver orders to people. The system imports or receives a list of orders and available drivers, then assigns orders to drivers with an optimized order sequence to reduce distance, time, and petrol consumption.

## Target Users
Primary pilot target:
- Small delivery/logistics companies that contract with larger retailers such as IKEA, MediaMarkt, furniture/electronics retailers, or similar high-volume local delivery clients.

Secondary users to validate later:
- Small delivery businesses serving multiple local retailers.
- Local shops delivering bulky or scheduled goods.
- Small logistics teams that cannot afford enterprise route optimization tools.

Deprioritized for first pilot:
- Pharmacy/medical-specific delivery. The product should not be pharmacy-specific.
- Restaurants/cloud kitchens unless later research shows a strong fit.

## Inputs
### Orders
Each order may include:
- Order ID.
- Customer/person name.
- Delivery address.
- Contact phone/email, if available.
- Availability/time window of recipient.
- Delivery priority.
- Package size/weight, optional.
- Required delivery duration/service time.
- Special preferences/instructions.
- Order status.

### Drivers
Each driver may include:
- Driver ID and account.
- Name/contact.
- Initial/current location.
- Working hours/shift start/end.
- Capacity/vehicle constraints.
- Availability status.
- Assigned orders.

## Outputs
- Driver-order assignments.
- Optimized order sequence per driver.
- Estimated route distance/time.
- Admin overview of all drivers/orders/status.
- Driver mobile view of assigned stops and status updates.

## Preferred Product Shape
- Mobile-first app for drivers.
- Mobile-first admin app/dashboard for admin/dispatcher.
- Main product language: English.
- Pilot geography: Germany and the Netherlands/Holland, with Germany-first assumptions when conflict exists.
- Backend API for optimization, assignments, accounts, and real-time updates.
- Output objective: a real pilot business, not only a demo prototype.

## Confirmed MVP Constraints From Emad
- First pilot should target small delivery companies serving big retailers such as IKEA or MediaMarkt; not pharmacy-specific.
- Country focus: Germany and Netherlands/Holland.
- Main app language: English.
- Proof of delivery MVP: note + timestamp is enough.
- Customer phone number/contact number should be optional, not mandatory.
- Initial target scale: about 200 orders per day.
- Output should be a real pilot business with practical operational value.

## Key Open Questions for Team
- Is the MVP one mobile app with role-based views, or separate driver/admin apps?
- Which route optimization approach is best for MVP: Google/Mapbox/OSRM/GraphHopper/custom heuristic?
- How will addresses be geocoded?
- Should optimization be manual trigger by admin or automatic on import?
- What businesses are most likely to pay?
- What monetization model fits: subscription, per-driver, per-order, or one-time setup?
