"""In-memory service layer used by the backend prototype and tests.

FastAPI endpoints can wrap these methods directly. Persistence is deliberately
in-memory for this evening prototype; table names/fields are documented in
`docs/api-and-schema.md` for later PostgreSQL implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from .domain import (
    Driver,
    Order,
    OrderStatus,
    PlanningRun,
    PlanningStatus,
    assert_status_transition,
    route_summary,
)
from .planner import GreedyRoutePlanner


@dataclass
class StatusEvent:
    order_id: str
    to_status: OrderStatus
    actor_user_id: str
    driver_id: str | None = None
    from_status: OrderStatus | None = None
    note: str | None = None
    lat: float | None = None
    lng: float | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class RoutingService:
    def __init__(self, planner: GreedyRoutePlanner | None = None):
        self.orders: dict[str, Order] = {}
        self.drivers: dict[str, Driver] = {}
        self.planning_runs: dict[str, PlanningRun] = {}
        self.status_events: list[StatusEvent] = []
        self.planner = planner or GreedyRoutePlanner()

    def create_order(self, order: Order) -> tuple[Order, list[str]]:
        errors = order.mark_ready_if_valid()
        self.orders[order.id] = order
        return order, errors

    def create_driver(self, driver: Driver) -> tuple[Driver, list[str]]:
        errors = driver.validate_for_planning()
        self.drivers[driver.id] = driver
        return driver, errors

    def run_planning(self, delivery_date) -> PlanningRun:
        run = self.planner.plan(list(self.orders.values()), list(self.drivers.values()), delivery_date)
        self.planning_runs[run.id] = run
        return run

    def publish_plan(self, planning_run_id: str) -> PlanningRun:
        run = self.planning_runs[planning_run_id]
        for route in run.routes:
            for stop in route.stops:
                assert_status_transition(stop.order.status, OrderStatus.PUBLISHED)
                stop.order.status = OrderStatus.PUBLISHED
                stop.status = OrderStatus.PUBLISHED
        run.status = PlanningStatus.PUBLISHED
        run.published_at = datetime.now(UTC)
        return run

    def route_for_driver_today(self, driver_id: str, today) -> list[dict]:
        visible: list[dict] = []
        for run in self.planning_runs.values():
            if run.delivery_date != today or run.status != PlanningStatus.PUBLISHED:
                continue
            for route in run.routes:
                if route.driver.id != driver_id:
                    continue
                for stop in sorted(route.stops, key=lambda s: s.sequence):
                    visible.append(
                        {
                            "order_id": stop.order.id,
                            "sequence": stop.sequence,
                            "recipient_name": stop.order.recipient_name,
                            "address": stop.order.address,
                            "planned_arrival": stop.planned_arrival.isoformat(),
                            "status": stop.order.status.value,
                            "navigation_url": self.navigation_url(stop.order),
                        }
                    )
        return visible

    def update_order_status(self, order_id: str, to_status: OrderStatus, actor_user_id: str, *, driver_id: str | None = None, note: str | None = None) -> StatusEvent:
        order = self.orders[order_id]
        assert_status_transition(order.status, to_status)
        if to_status == OrderStatus.FAILED and not note:
            raise ValueError("failed status requires a failure reason/note")
        if to_status == OrderStatus.DELIVERED and note:
            order.proof_note = note
        if to_status == OrderStatus.FAILED:
            order.failure_reason = note
        event = StatusEvent(
            order_id=order_id,
            from_status=order.status,
            to_status=to_status,
            actor_user_id=actor_user_id,
            driver_id=driver_id,
            note=note,
        )
        order.status = to_status
        self.status_events.append(event)
        return event

    def dispatch_dashboard(self) -> dict:
        orders = list(self.orders.values())
        by_status: dict[str, int] = {}
        for order in orders:
            by_status[order.status.value] = by_status.get(order.status.value, 0) + 1
        latest_run = max(self.planning_runs.values(), key=lambda r: r.created_at, default=None)
        return {
            "orders_by_status": by_status,
            "total_orders": len(orders),
            "total_drivers": len(self.drivers),
            "latest_plan_summary": route_summary(latest_run) if latest_run else None,
            "status_event_count": len(self.status_events),
        }

    @staticmethod
    def navigation_url(order: Order) -> str:
        if order.location:
            return f"https://www.google.com/maps/dir/?api=1&destination={order.location.lat},{order.location.lng}"
        return f"https://www.google.com/maps/search/?api=1&query={order.address.replace(' ', '+')}"
