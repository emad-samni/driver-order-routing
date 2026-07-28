# Project Brief — Driver Order Routing & Delivery Assignment App

## Vision
Create a mobile-first product for businesses that deliver orders to people. The system imports or receives a list of orders and available drivers, then assigns orders to drivers with an optimized order sequence to reduce distance, time, and petrol consumption.

## Target Users
Potential target users to validate:
- Small delivery businesses.
- Restaurants or cloud kitchens with own drivers.
- Local shops delivering groceries, pharmacy items, parcels, or documents.
- Small logistics teams that cannot afford enterprise route optimization tools.
- NGOs/community services delivering meals or supplies.

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
- Mobile app for drivers.
- Mobile app or responsive admin app for admin.
- Backend API for optimization, assignments, accounts, and real-time updates.

## Key Open Questions for Team
- Is the MVP one mobile app with role-based views, or separate driver/admin apps?
- Which route optimization approach is best for MVP: Google/Mapbox/OSRM/GraphHopper/custom heuristic?
- How will addresses be geocoded?
- Should optimization be manual trigger by admin or automatic on import?
- What businesses are most likely to pay?
- What monetization model fits: subscription, per-driver, per-order, or one-time setup?
