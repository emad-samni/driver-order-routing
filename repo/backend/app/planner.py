"""Deterministic no-spend route planner for backend prototype.

The planner uses a nearest-feasible greedy heuristic. It is intentionally not a
claim of global optimality; it proves the data flow and keeps the solver behind a
replaceable interface for a future OR-Tools implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .domain import (
    Driver,
    DriverAvailability,
    Location,
    Order,
    OrderStatus,
    PlanningRun,
    Route,
    RouteStop,
    UnassignedOrder,
    UnassignedReason,
    combine,
    estimate_travel_seconds,
    haversine_meters,
)


@dataclass
class DriverRouteState:
    route: Route
    current_location: Location
    current_time: datetime
    used_capacity: int = 0


class GreedyRoutePlanner:
    """Assign each ready order to the nearest currently feasible driver route."""

    def __init__(self, average_kph: float = 30.0):
        self.average_kph = average_kph

    def plan(self, orders: list[Order], drivers: list[Driver], delivery_date) -> PlanningRun:
        routes: list[Route] = []
        unassigned: list[UnassignedOrder] = []

        available_drivers = [d for d in drivers if d.is_available_for_planning and not d.validate_for_planning()]
        invalid_or_unready_orders: list[Order] = []
        ready_orders: list[Order] = []

        for order in orders:
            errors = order.mark_ready_if_valid()
            if order.delivery_date != delivery_date:
                errors.append("order delivery_date does not match planning date")
            if errors:
                reason = UnassignedReason.MISSING_COORDINATES if order.location is None else UnassignedReason.MANUAL_REVIEW_REQUIRED
                unassigned.append(UnassignedOrder(order=order, reason_code=reason, details="; ".join(errors)))
                invalid_or_unready_orders.append(order)
            else:
                ready_orders.append(order)

        if not available_drivers:
            for order in ready_orders:
                unassigned.append(
                    UnassignedOrder(order=order, reason_code=UnassignedReason.NO_AVAILABLE_DRIVER, details="no available valid drivers")
                )
            return PlanningRun(delivery_date=delivery_date, routes=[], unassigned_orders=unassigned)

        states: list[DriverRouteState] = []
        for driver in available_drivers:
            route = Route(driver=driver)
            routes.append(route)
            states.append(
                DriverRouteState(
                    route=route,
                    current_location=driver.start_location,
                    current_time=combine(delivery_date, driver.shift_start),
                )
            )

        # High-priority and earlier-window orders get first chance at scarce capacity.
        sorted_orders = sorted(ready_orders, key=lambda o: (self._priority_rank(o.priority), o.time_window_end, o.time_window_start))

        for order in sorted_orders:
            best_state: DriverRouteState | None = None
            best_arrival: datetime | None = None
            best_departure: datetime | None = None
            best_distance: int | None = None
            rejection_reasons: set[UnassignedReason] = set()

            for state in states:
                feasible, reason, arrival, departure, distance = self._evaluate_append(state, order, delivery_date)
                if not feasible:
                    rejection_reasons.add(reason or UnassignedReason.MANUAL_REVIEW_REQUIRED)
                    continue
                if best_distance is None or distance < best_distance:
                    best_state = state
                    best_arrival = arrival
                    best_departure = departure
                    best_distance = distance

            if best_state is None or best_arrival is None or best_departure is None or best_distance is None:
                unassigned.append(
                    UnassignedOrder(
                        order=order,
                        reason_code=self._dominant_reason(rejection_reasons),
                        details="; ".join(sorted(r.value for r in rejection_reasons)) or "no feasible append found",
                    )
                )
                continue

            sequence = len(best_state.route.stops) + 1
            stop = RouteStop(order=order, sequence=sequence, planned_arrival=best_arrival, planned_departure=best_departure)
            best_state.route.stops.append(stop)
            best_state.route.planned_distance_meters += best_distance
            best_state.route.planned_duration_seconds += estimate_travel_seconds(best_distance, self.average_kph)
            best_state.route.planned_duration_seconds += order.service_duration_minutes * 60
            best_state.current_location = order.location  # type: ignore[assignment]
            best_state.current_time = best_departure
            best_state.used_capacity += order.package_units
            order.status = OrderStatus.PLANNED

        # Hide empty routes from review to reduce frontend noise.
        routes = [route for route in routes if route.stops]
        return PlanningRun(delivery_date=delivery_date, routes=routes, unassigned_orders=unassigned)

    def _evaluate_append(self, state: DriverRouteState, order: Order, delivery_date) -> tuple[bool, UnassignedReason | None, datetime, datetime, int]:
        assert order.location is not None
        driver = state.route.driver
        distance = haversine_meters(state.current_location, order.location)
        travel_seconds = estimate_travel_seconds(distance, self.average_kph)
        raw_arrival = state.current_time + timedelta(seconds=travel_seconds)
        window_start = combine(delivery_date, order.time_window_start)
        window_end = combine(delivery_date, order.time_window_end)
        shift_end = combine(delivery_date, driver.shift_end)
        arrival = max(raw_arrival, window_start)
        departure = arrival + timedelta(minutes=order.service_duration_minutes)

        if len(state.route.stops) >= driver.max_stops:
            return False, UnassignedReason.MAX_STOPS_EXCEEDED, arrival, departure, distance
        if state.used_capacity + order.package_units > driver.capacity_units:
            return False, UnassignedReason.CAPACITY_EXCEEDED, arrival, departure, distance
        if arrival > window_end:
            return False, UnassignedReason.TIME_WINDOW_INFEASIBLE, arrival, departure, distance
        if departure > shift_end:
            return False, UnassignedReason.OUTSIDE_DRIVER_SHIFT, arrival, departure, distance
        return True, None, arrival, departure, distance

    @staticmethod
    def _priority_rank(priority: str) -> int:
        return {"high": 0, "normal": 1, "low": 2}.get(priority, 1)

    @staticmethod
    def _dominant_reason(reasons: set[UnassignedReason]) -> UnassignedReason:
        priority = [
            UnassignedReason.MISSING_COORDINATES,
            UnassignedReason.NO_AVAILABLE_DRIVER,
            UnassignedReason.TIME_WINDOW_INFEASIBLE,
            UnassignedReason.OUTSIDE_DRIVER_SHIFT,
            UnassignedReason.CAPACITY_EXCEEDED,
            UnassignedReason.MAX_STOPS_EXCEEDED,
            UnassignedReason.MANUAL_REVIEW_REQUIRED,
        ]
        for reason in priority:
            if reason in reasons:
                return reason
        return UnassignedReason.OPTIMIZATION_FAILED
