import datetime
import unittest

from fastapi.testclient import TestClient

from app.domain import (
    DriverAvailability,
    ImportErrorCode,
    Location,
    OrderStatus,
    PlanningStatus,
    UnassignedReason,
)
from app.main import app, service


client = TestClient(app)


def _clear_service_state() -> None:
    service.orders.clear()
    service.drivers.clear()
    service.import_batches.clear()
    service.planning_runs.clear()
    service.status_events.clear()


class FastApiHealthTests(unittest.TestCase):
    def test_health_endpoint_returns_ok(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_excel_template_endpoint_lists_columns(self):
        response = client.get("/excel-template")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        columns = [column["column"] for column in body["columns"]]
        self.assertIn("order_id", columns)
        self.assertIn("latitude", columns)
        self.assertIn("longitude", columns)


class FastApiOrderTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_service_state()

    def test_create_order_and_list_orders(self):
        payload = {
            "order_id": "RET-INT-1",
            "recipient_name": "Integration Customer",
            "address": "Alexanderplatz 1, 10178 Berlin",
            "delivery_date": datetime.date(2026, 8, 3).isoformat(),
            "time_window_start": "09:00",
            "time_window_end": "12:00",
            "latitude": 52.5219,
            "longitude": 13.4132,
        }
        response = client.post("/orders", json=payload)
        self.assertEqual(response.status_code, 201)
        order = response.json()
        self.assertEqual(order["status"], OrderStatus.READY_TO_PLAN.value)

        response = client.get("/orders")
        self.assertEqual(response.status_code, 200)
        orders = response.json()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["external_order_id"], "RET-INT-1")

    def test_create_order_rejects_missing_required_fields(self):
        response = client.post("/orders", json={"order_id": "BAD"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("time_window_start", response.json()["detail"])


class FastApiDriverAndPlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_service_state()

    def test_create_driver_run_plan_and_publish(self):
        driver_payload = {
            "name": "Integration Driver",
            "start_location": {"lat": 52.3676, "lng": 4.9041},
            "shift_start": "08:00",
            "shift_end": "18:00",
            "max_stops": 5,
            "capacity_units": 20,
        }
        driver_response = client.post("/drivers", json=driver_payload)
        self.assertEqual(driver_response.status_code, 200, driver_response.text)
        self.assertEqual(driver_response.json()["availability_status"], DriverAvailability.AVAILABLE.value)

        order_payload = {
            "order_id": "RET-INT-2",
            "recipient_name": "Planning Customer",
            "address": "Damrak 1, 1012 Amsterdam",
            "delivery_date": datetime.date(2026, 8, 3).isoformat(),
            "time_window_start": "10:00",
            "time_window_end": "13:00",
            "latitude": 52.3738,
            "longitude": 4.8909,
        }
        order_response = client.post("/orders", json=order_payload)
        self.assertEqual(order_response.status_code, 201)

        plan_response = client.post("/planning-runs", json={"delivery_date": "2026-08-03"})
        self.assertEqual(plan_response.status_code, 201)
        run = plan_response.json()
        self.assertEqual(run["status"], PlanningStatus.REVIEW.value)
        self.assertEqual(run["summary"]["assigned_orders"], 1)
        run_id = run["id"]

        publish_response = client.post(f"/planning-runs/{run_id}/publish")
        self.assertEqual(publish_response.status_code, 200)
        self.assertEqual(publish_response.json()["status"], PlanningStatus.PUBLISHED.value)

        route_response = client.get("/driver/me/routes/today", params={"driver_id": run["routes"][0]["driver_id"], "today": "2026-08-03"})
        self.assertEqual(route_response.status_code, 200)
        visible_stops = route_response.json()
        self.assertEqual(len(visible_stops), 1)
        self.assertEqual(visible_stops[0]["status"], OrderStatus.PUBLISHED.value)

    def test_far_order_is_unassigned_due_to_shift_conflict(self):
        _clear_service_state()
        driver_payload = {
            "name": "Local Driver",
            "start_location": {"lat": 52.3676, "lng": 4.9041},
            "shift_start": "08:00",
            "shift_end": "18:00",
            "max_stops": 5,
            "capacity_units": 20,
        }
        self.assertEqual(client.post("/drivers", json=driver_payload).status_code, 200)

        far_order = {
            "order_id": "RET-FAR-1",
            "recipient_name": "Far Customer",
            "address": "Alexanderplatz 1, 10178 Berlin",
            "delivery_date": datetime.date(2026, 8, 3).isoformat(),
            "time_window_start": "10:00",
            "time_window_end": "13:00",
            "latitude": 52.5219,
            "longitude": 13.4132,
        }
        self.assertEqual(client.post("/orders", json=far_order).status_code, 201)

        run = client.post("/planning-runs", json={"delivery_date": "2026-08-03"}).json()
        self.assertEqual(run["summary"]["unassigned_orders"], 1)
        self.assertEqual(
            run["unassigned_orders"][0]["reason_code"],
            UnassignedReason.TIME_WINDOW_INFEASIBLE.value,
        )
