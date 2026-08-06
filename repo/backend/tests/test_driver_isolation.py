"""Auth-bound driver route access.

Proves that a driver credential can only read its own published route and can
never see another driver's stops/customer addresses, even when it supplies a
different driver_id in the request. This is the acceptance gate for the
2026-08-06 auth-binding hardening item.
"""

import os
import unittest

# Use the in-memory service so the test is self-contained; auth is toggled per
# test at request time (auth_enabled() reads the env on every call).
os.environ.setdefault("USE_PERSISTED_SERVICE", "0")

from fastapi.testclient import TestClient

from app import auth
from app.domain import OrderStatus
from app.main import app, service

client = TestClient(app)

DELIVERY_DATE = "2026-08-03"

DRIVER_A_KEY = "key-driver-a"
DRIVER_B_KEY = "key-driver-b"


def _clear_service_state() -> None:
    service.orders.clear()
    service.drivers.clear()
    service.import_batches.clear()
    service.planning_runs.clear()
    service.status_events.clear()
    auth._DRIVER_KEY_MAP.clear()


class DriverRouteIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        # Auth off while we set up fixtures through the admin-style endpoints.
        os.environ["REQUIRE_API_KEY"] = "0"
        _clear_service_state()

        driver_a = client.post(
            "/drivers",
            json={
                "name": "Driver A (Amsterdam)",
                "start_location": {"lat": 52.3676, "lng": 4.9041},
                "shift_start": "08:00",
                "shift_end": "18:00",
                "max_stops": 5,
                "capacity_units": 20,
            },
        ).json()
        driver_b = client.post(
            "/drivers",
            json={
                "name": "Driver B (Berlin)",
                "start_location": {"lat": 52.5200, "lng": 13.4050},
                "shift_start": "08:00",
                "shift_end": "18:00",
                "max_stops": 5,
                "capacity_units": 20,
            },
        ).json()
        self.driver_a_id = driver_a["id"]
        self.driver_b_id = driver_b["id"]

        # One order near each driver so the greedy planner assigns them apart.
        client.post(
            "/orders",
            json={
                "order_id": "RET-AMS-1",
                "recipient_name": "Amsterdam Customer",
                "address": "Damrak 1, 1012 Amsterdam",
                "delivery_date": DELIVERY_DATE,
                "time_window_start": "10:00",
                "time_window_end": "13:00",
                "latitude": 52.3738,
                "longitude": 4.8909,
            },
        )
        client.post(
            "/orders",
            json={
                "order_id": "RET-BER-1",
                "recipient_name": "Berlin Customer",
                "address": "Alexanderplatz 1, 10178 Berlin",
                "delivery_date": DELIVERY_DATE,
                "time_window_start": "10:00",
                "time_window_end": "13:00",
                "latitude": 52.5219,
                "longitude": 13.4132,
            },
        )

        run = client.post("/planning-runs", json={"delivery_date": DELIVERY_DATE}).json()
        client.post(f"/planning-runs/{run['id']}/publish")

        # Bind a per-driver credential to each driver identity.
        auth.register_driver_key(DRIVER_A_KEY, self.driver_a_id)
        auth.register_driver_key(DRIVER_B_KEY, self.driver_b_id)

        # Enforce auth for the assertions below.
        os.environ["REQUIRE_API_KEY"] = "1"

    def tearDown(self) -> None:
        os.environ["REQUIRE_API_KEY"] = "0"
        _clear_service_state()

    def _stops_for(self, resp) -> list[dict]:
        self.assertEqual(resp.status_code, 200, resp.text)
        return resp.json()

    def test_driver_sees_only_own_route(self):
        a_stops = self._stops_for(
            client.get(
                "/driver/me/routes/today",
                params={"today": DELIVERY_DATE},
                headers={"x-api-key": DRIVER_A_KEY},
            )
        )
        b_stops = self._stops_for(
            client.get(
                "/driver/me/routes/today",
                params={"today": DELIVERY_DATE},
                headers={"x-api-key": DRIVER_B_KEY},
            )
        )
        a_recipients = {s["recipient_name"] for s in a_stops}
        b_recipients = {s["recipient_name"] for s in b_stops}

        self.assertIn("Amsterdam Customer", a_recipients)
        self.assertNotIn("Berlin Customer", a_recipients)
        self.assertIn("Berlin Customer", b_recipients)
        self.assertNotIn("Amsterdam Customer", b_recipients)

    def test_driver_cannot_spoof_another_driver_via_query_param(self):
        # Driver A supplies driver B's id in the request. It must be ignored:
        # the route is resolved from the authenticated principal, not input.
        resp = client.get(
            "/driver/me/routes/today",
            params={"driver_id": self.driver_b_id, "today": DELIVERY_DATE},
            headers={"x-api-key": DRIVER_A_KEY},
        )
        stops = self._stops_for(resp)
        recipients = {s["recipient_name"] for s in stops}
        self.assertNotIn("Berlin Customer", recipients)
        self.assertIn("Amsterdam Customer", recipients)

    def test_missing_api_key_is_rejected(self):
        resp = client.get(
            "/driver/me/routes/today",
            params={"driver_id": self.driver_a_id, "today": DELIVERY_DATE},
        )
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
