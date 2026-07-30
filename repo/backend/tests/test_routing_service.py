from datetime import date, time
import unittest

from app.domain import Driver, DriverAvailability, ImportErrorCode, Location, Order, OrderStatus, UnassignedReason
from app.service import RoutingService


DAY = date(2026, 7, 30)


def order(name: str, lat: float | None, lng: float | None, *, start=time(9, 0), end=time(17, 0), units=1) -> Order:
    return Order(
        recipient_name=name,
        address=f"{name} address",
        delivery_date=DAY,
        time_window_start=start,
        time_window_end=end,
        location=Location(lat, lng) if lat is not None and lng is not None else None,
        package_units=units,
    )


def driver(name: str = "Driver A", *, max_stops=25, capacity=999, availability=DriverAvailability.AVAILABLE) -> Driver:
    return Driver(
        name=name,
        start_location=Location(25.2048, 55.2708),
        shift_start=time(8, 0),
        shift_end=time(18, 0),
        max_stops=max_stops,
        capacity_units=capacity,
        availability_status=availability,
    )


class RoutingServiceTests(unittest.TestCase):
    def test_plans_and_publishes_driver_visible_route(self):
        service = RoutingService()
        created_driver, driver_errors = service.create_driver(driver())
        self.assertEqual(driver_errors, [])
        service.create_order(order("Stop 1", 25.21, 55.28))
        service.create_order(order("Stop 2", 25.22, 55.29))

        run = service.run_planning(DAY)
        self.assertEqual(len(run.routes), 1)
        self.assertEqual(len(run.routes[0].stops), 2)
        self.assertEqual(service.route_for_driver_today(created_driver.id, DAY), [])

        service.publish_plan(run.id)
        visible = service.route_for_driver_today(created_driver.id, DAY)
        self.assertEqual(len(visible), 2)
        self.assertIn("navigation_url", visible[0])
        self.assertEqual(visible[0]["status"], OrderStatus.PUBLISHED.value)

    def test_missing_coordinates_are_unassigned(self):
        service = RoutingService()
        service.create_driver(driver())
        service.create_order(order("No Coordinates", None, None))

        run = service.run_planning(DAY)
        self.assertEqual(len(run.routes), 0)
        self.assertEqual(run.unassigned_orders[0].reason_code, UnassignedReason.MISSING_COORDINATES)

    def test_no_available_driver_reason(self):
        service = RoutingService()
        service.create_driver(driver(availability=DriverAvailability.OFFLINE))
        service.create_order(order("Stop", 25.21, 55.28))

        run = service.run_planning(DAY)
        self.assertEqual(run.unassigned_orders[0].reason_code, UnassignedReason.NO_AVAILABLE_DRIVER)

    def test_impossible_time_window_is_unassigned(self):
        service = RoutingService()
        service.create_driver(driver())
        # Very short early window far enough from depot that arrival after 08:01 is infeasible.
        service.create_order(order("Too Early", 25.40, 55.50, start=time(8, 0), end=time(8, 1)))

        run = service.run_planning(DAY)
        self.assertEqual(run.unassigned_orders[0].reason_code, UnassignedReason.TIME_WINDOW_INFEASIBLE)

    def test_capacity_and_max_stops_constraints(self):
        service = RoutingService()
        service.create_driver(driver(max_stops=1, capacity=1))
        service.create_order(order("First", 25.21, 55.28, units=1))
        service.create_order(order("Second", 25.22, 55.29, units=1))

        run = service.run_planning(DAY)
        self.assertEqual(len(run.routes[0].stops), 1)
        self.assertEqual(run.unassigned_orders[0].reason_code, UnassignedReason.MAX_STOPS_EXCEEDED)

    def test_status_lifecycle_and_failure_note_validation(self):
        service = RoutingService()
        created_driver, _ = service.create_driver(driver())
        created_order, _ = service.create_order(order("Stop", 25.21, 55.28))
        run = service.run_planning(DAY)
        service.publish_plan(run.id)

        service.update_order_status(created_order.id, OrderStatus.ACCEPTED, "driver-user", driver_id=created_driver.id)
        service.update_order_status(created_order.id, OrderStatus.EN_ROUTE, "driver-user", driver_id=created_driver.id)
        service.update_order_status(created_order.id, OrderStatus.ARRIVED, "driver-user", driver_id=created_driver.id)
        service.update_order_status(created_order.id, OrderStatus.DELIVERED, "driver-user", driver_id=created_driver.id, note="Left with recipient")
        self.assertEqual(created_order.status, OrderStatus.DELIVERED)
        self.assertEqual(created_order.proof_note, "Left with recipient")

        with self.assertRaises(ValueError):
            service.update_order_status(created_order.id, OrderStatus.FAILED, "driver-user")

    def test_failed_requires_note(self):
        service = RoutingService()
        created_driver, _ = service.create_driver(driver())
        created_order, _ = service.create_order(order("Stop", 25.21, 55.28))
        run = service.run_planning(DAY)
        service.publish_plan(run.id)
        service.update_order_status(created_order.id, OrderStatus.ACCEPTED, "driver-user", driver_id=created_driver.id)
        with self.assertRaises(ValueError):
            service.update_order_status(created_order.id, OrderStatus.FAILED, "driver-user", driver_id=created_driver.id)
        event = service.update_order_status(created_order.id, OrderStatus.FAILED, "driver-user", driver_id=created_driver.id, note="Customer unavailable")
        self.assertEqual(event.from_status, OrderStatus.ACCEPTED)
        self.assertEqual(created_order.failure_reason, "Customer unavailable")
    def test_excel_template_schema_exposes_required_columns(self):
        service = RoutingService()
        schema = service.excel_template_schema()
        columns = {field["column"]: field for field in schema}

        self.assertTrue(columns["order_id"]["required"])
        self.assertTrue(columns["customer_name"]["required"])
        self.assertTrue(columns["delivery_date"]["required"])
        self.assertIn("latitude", columns)
        self.assertIn("longitude", columns)

    def test_import_orders_from_rows_creates_ready_and_draft_rows_with_row_errors(self):
        service = RoutingService()
        batch = service.import_orders_from_rows(
            [
                {
                    "order_id": "RET-1",
                    "customer_name": "Customer One",
                    "street_address": "Alexanderplatz 1",
                    "postal_code": "10178",
                    "city": "Berlin",
                    "country": "DE",
                    "latitude": "52.5219",
                    "longitude": "13.4132",
                    "delivery_date": "2026-07-30",
                    "time_window_start": "09:00",
                    "time_window_end": "13:00",
                    "service_minutes": "12",
                    "priority": "high",
                    "package_units": "2",
                },
                {
                    "order_id": "RET-2",
                    "customer_name": "Customer Two",
                    "street_address": "Damrak 1",
                    "postal_code": "1012",
                    "city": "Amsterdam",
                    "country": "NL",
                    "delivery_date": "2026-07-30",
                    "time_window_start": "10:00",
                    "time_window_end": "14:00",
                },
                {
                    "order_id": "RET-1",
                    "customer_name": "Duplicate",
                    "street_address": "Bad Row 1",
                    "postal_code": "10178",
                    "city": "Berlin",
                    "delivery_date": "bad-date",
                    "time_window_start": "12:00",
                    "time_window_end": "11:00",
                    "priority": "urgent",
                },
            ],
            filename="orders.xlsx",
            planning_date=DAY,
        )

        self.assertEqual(batch.total_rows, 3)
        self.assertEqual(batch.valid_rows, 1)
        self.assertEqual(batch.routeable_rows, 1)
        self.assertEqual(batch.invalid_rows, 2)
        self.assertEqual(batch.duplicate_rows, 1)
        self.assertEqual(len(batch.imported_order_ids), 2)
        imported = [service.orders[order_id] for order_id in batch.imported_order_ids]
        self.assertEqual(imported[0].status, OrderStatus.READY_TO_PLAN)
        self.assertEqual(imported[0].geocode_status, "coordinates_supplied")
        self.assertEqual(imported[1].status, OrderStatus.DRAFT)
        self.assertEqual(imported[1].geocode_status, "geocoding_required")
        codes = {error.error_code for error in batch.row_errors}
        self.assertIn(ImportErrorCode.GEOCODING_REQUIRED, codes)
        self.assertIn(ImportErrorCode.DUPLICATE_ORDER_ID, codes)
        self.assertIn(ImportErrorCode.INVALID_DATE, codes)
        self.assertIn(ImportErrorCode.INVALID_TIME_WINDOW, codes)
        self.assertIn(ImportErrorCode.INVALID_PRIORITY, codes)


if __name__ == "__main__":
    unittest.main()
