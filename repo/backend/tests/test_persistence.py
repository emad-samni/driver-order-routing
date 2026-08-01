from __future__ import annotations

import os
import unittest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.persistence import SqliteRepository
from app.domain import Driver, Location, Order, OrderStatus
from datetime import date, time


def _order(order_id="order-1"):
    return Order(
        id=order_id,
        external_order_id=order_id,
        recipient_name="A",
        address="Berlin",
        delivery_date=date.today(),
        time_window_start=time(9, 0),
        time_window_end=time(12, 0),
        location=Location(52.52, 13.405),
        status=OrderStatus.DRAFT,
    )


def _driver(driver_id="driver-1"):
    return Driver(
        id=driver_id,
        name="Lina",
        start_location=Location(52.52, 13.405),
        shift_start=time(8, 0),
        shift_end=time(17, 0),
    )


class SqliteRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = SqliteRepository(db_path=":memory:")

    def test_upsert_and_list_orders(self):
        self.repo.upsert_order(_order())
        orders = self.repo.list_orders()
        assert len(orders) == 1
        assert orders[0]["id"] == "order-1"

    def test_upsert_and_list_drivers(self):
        self.repo.upsert_driver(_driver())
        drivers = self.repo.list_drivers()
        assert len(drivers) == 1
        assert drivers[0]["id"] == "driver-1"

    def test_update_order_status(self):
        self.repo.upsert_order(_order())
        self.repo.update_order_status("order-1", OrderStatus.PUBLISHED.value)
        assert self.repo.list_orders()[0]["status"] == OrderStatus.PUBLISHED.value

    def test_list_import_batches_returns_empty_when_none(self):
        assert self.repo.list_import_batches() == []

    def test_audit_events_persist(self):
        self.repo.insert_audit_event("admin", "route_override", "order-1", "move", None, "note")
        audits = self.repo.list_audit_events()
        assert len(audits) == 1
        assert audits[0]["action"] == "move"
