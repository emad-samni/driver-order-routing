from __future__ import annotations

import os
import unittest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.service import RoutingService
from app.planner import GreedyRoutePlanner
from app.domain import Order, Driver, Location
from datetime import date, time


def _service() -> RoutingService:
    return RoutingService(planner=GreedyRoutePlanner())


class OverrideServiceTests(unittest.TestCase):
    def test_move_order_between_drivers_requires_note(self):
        service = _service()
        try:
            service.move_order_between_drivers("o1", "d2", "admin", note=None)
        except ValueError as exc:
            assert "audit note is required" in str(exc)
        else:
            raise AssertionError("expected ValueError for missing note")

    def test_reorder_route_stops_requires_note(self):
        service = _service()
        try:
            service.reorder_route_stops("d1", [], "admin", note=None)
        except ValueError as exc:
            assert "audit note is required" in str(exc)
        else:
            raise AssertionError("expected ValueError for missing note")

    def test_move_order_between_drivers_reassigns_and_emits_audit_event(self):
        service = _service()
        order1 = Order(
            recipient_name="A",
            address="Berlin",
            delivery_date=date.today(),
            time_window_start=time(9, 0),
            time_window_end=time(12, 0),
            location=Location(52.52, 13.405),
        )
        order2 = Order(
            recipient_name="B",
            address="Berlin",
            delivery_date=date.today(),
            time_window_start=time(9, 0),
            time_window_end=time(12, 0),
            location=Location(52.53, 13.415),
        )
        driver1 = Driver(name="Lina", start_location=Location(52.52, 13.405), shift_start=time(8, 0), shift_end=time(17, 0))
        driver2 = Driver(name="Samir", start_location=Location(52.53, 13.41), shift_start=time(8, 0), shift_end=time(17, 0))
        service.create_order(order1)
        service.create_order(order2)
        service.create_driver(driver1)
        service.create_driver(driver2)
        run = service.run_planning(date.today())
        service.publish_plan(run.id)
        route, warnings, event = service.move_order_between_drivers(
            order1.id, driver2.id, "admin", note="Reassign for customer pickup"
        )
        assert route.driver.id == driver2.id
        assert any(stop.order.id == order1.id for stop in route.stops)
        assert event.note == "Reassign for customer pickup"
        assert event.actor_user_id == "admin"
        assert len(warnings) == 0

    def test_reorder_route_stops_reverses_sequence_and_emits_audit_event(self):
        service = _service()
        order = Order(
            recipient_name="A",
            address="Berlin",
            delivery_date=date.today(),
            time_window_start=time(9, 0),
            time_window_end=time(12, 0),
            location=Location(52.52, 13.405),
        )
        driver1 = Driver(name="Lina", start_location=Location(52.52, 13.405), shift_start=time(8, 0), shift_end=time(17, 0))
        service.create_order(order)
        service.create_driver(driver1)
        run = service.run_planning(date.today())
        service.publish_plan(run.id)
        stop_ids = [stop.order.id for stop in list(run.routes)[0].stops]
        route, warnings, event = service.reorder_route_stops(
            driver1.id, list(reversed(stop_ids)), "admin", note="Reverse route"
        )
        returned_ids = [stop.order.id for stop in route.stops]
        assert returned_ids == list(reversed(stop_ids))
        assert event.note == "Reverse route"
        assert event.actor_user_id == "admin"
