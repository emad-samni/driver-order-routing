"""Backend domain model for the Driver Order Routing MVP prototype.

This module is intentionally dependency-light so it can be exercised in the
current workspace without paid APIs or external services. It mirrors the
architecture/backlog data model and can later be mapped to FastAPI/Pydantic and
PostgreSQL tables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from enum import StrEnum
from math import asin, cos, radians, sin, sqrt
from typing import Iterable
from uuid import uuid4


class OrderStatus(StrEnum):
    DRAFT = "draft"
    READY_TO_PLAN = "ready_to_plan"
    PLANNED = "planned"
    PUBLISHED = "published"
    ACCEPTED = "accepted"
    EN_ROUTE = "en_route"
    ARRIVED = "arrived"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class DriverAvailability(StrEnum):
    OFFLINE = "offline"
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    ON_ROUTE = "on_route"
    PAUSED = "paused"
    COMPLETED_SHIFT = "completed_shift"


class PlanningStatus(StrEnum):
    REVIEW = "review"
    PUBLISHED = "published"
    FAILED = "failed"


class UnassignedReason(StrEnum):
    MISSING_COORDINATES = "missing_coordinates"
    INVALID_ADDRESS = "invalid_address"
    NO_AVAILABLE_DRIVER = "no_available_driver"
    OUTSIDE_DRIVER_SHIFT = "outside_driver_shift"
    TIME_WINDOW_INFEASIBLE = "time_window_infeasible"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    MAX_STOPS_EXCEEDED = "max_stops_exceeded"
    OPTIMIZATION_FAILED = "optimization_failed"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"


class ImportRowStatus(StrEnum):
    READY_TO_PLAN = "ready_to_plan"
    DRAFT = "draft"
    REJECTED = "rejected"


class ImportErrorCode(StrEnum):
    MISSING_REQUIRED_FIELD = "missing_required_field"
    DUPLICATE_ORDER_ID = "duplicate_order_id"
    INVALID_DATE = "invalid_date"
    INVALID_TIME_WINDOW = "invalid_time_window"
    INVALID_COORDINATE = "invalid_coordinate"
    INVALID_PRIORITY = "invalid_priority"
    MISSING_ROUTEABLE_ADDRESS = "missing_routeable_address"
    GEOCODING_REQUIRED = "geocoding_required"
    INVALID_NUMBER = "invalid_number"


@dataclass(frozen=True)
class Location:
    lat: float
    lng: float

    def validate(self) -> None:
        if not (-90 <= self.lat <= 90 and -180 <= self.lng <= 180):
            raise ValueError("location coordinates must be valid WGS84 lat/lng")


@dataclass
class Order:
    recipient_name: str
    address: str
    delivery_date: date
    time_window_start: time
    time_window_end: time
    location: Location | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    external_order_id: str | None = None
    phone: str | None = None
    priority: str = "normal"
    service_duration_minutes: int = 10
    package_units: int = 1
    special_instructions: str | None = None
    status: OrderStatus = OrderStatus.DRAFT
    proof_note: str | None = None
    failure_reason: str | None = None
    import_batch_id: str | None = None
    import_row_number: int | None = None
    geocode_status: str = "manual_or_pending"

    def validate_for_planning(self) -> list[str]:
        errors: list[str] = []
        if not self.recipient_name.strip():
            errors.append("recipient_name is required")
        if not self.address.strip():
            errors.append("address is required")
        if self.location is None:
            errors.append("coordinates are required for prototype planning")
        else:
            try:
                self.location.validate()
            except ValueError as exc:
                errors.append(str(exc))
        if self.time_window_end <= self.time_window_start:
            errors.append("time_window_end must be after time_window_start")
        if self.service_duration_minutes <= 0:
            errors.append("service_duration_minutes must be positive")
        if self.package_units <= 0:
            errors.append("package_units must be positive")
        return errors

    def mark_ready_if_valid(self) -> list[str]:
        errors = self.validate_for_planning()
        self.status = OrderStatus.READY_TO_PLAN if not errors else OrderStatus.DRAFT
        return errors


@dataclass
class Driver:
    name: str
    start_location: Location
    shift_start: time
    shift_end: time
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str | None = None
    phone: str | None = None
    start_address: str | None = None
    availability_status: DriverAvailability = DriverAvailability.AVAILABLE
    max_stops: int = 25
    capacity_units: int = 999
    vehicle_type: str | None = None

    def validate_for_planning(self) -> list[str]:
        errors: list[str] = []
        if not self.name.strip():
            errors.append("driver name is required")
        try:
            self.start_location.validate()
        except ValueError as exc:
            errors.append(str(exc))
        if self.shift_end <= self.shift_start:
            errors.append("shift_end must be after shift_start")
        if self.max_stops <= 0:
            errors.append("max_stops must be positive")
        if self.capacity_units <= 0:
            errors.append("capacity_units must be positive")
        return errors

    @property
    def is_available_for_planning(self) -> bool:
        return self.availability_status == DriverAvailability.AVAILABLE


@dataclass
class RouteStop:
    order: Order
    sequence: int
    planned_arrival: datetime
    planned_departure: datetime
    status: OrderStatus = OrderStatus.PLANNED


@dataclass
class Route:
    driver: Driver
    stops: list[RouteStop] = field(default_factory=list)
    planned_distance_meters: int = 0
    planned_duration_seconds: int = 0


@dataclass
class UnassignedOrder:
    order: Order
    reason_code: UnassignedReason
    details: str


@dataclass(frozen=True)
class ImportRowError:
    row_number: int
    field: str
    error_code: ImportErrorCode
    message: str
    suggested_fix: str


@dataclass
class ImportBatch:
    filename: str
    planning_date: date | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    total_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    duplicate_rows: int = 0
    routeable_rows: int = 0
    row_errors: list[ImportRowError] = field(default_factory=list)
    imported_order_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def status(self) -> str:
        if self.total_rows == 0:
            return "empty"
        if self.invalid_rows:
            return "completed_with_errors"
        return "completed"


@dataclass
class PlanningRun:
    delivery_date: date
    routes: list[Route]
    unassigned_orders: list[UnassignedOrder]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: PlanningStatus = PlanningStatus.REVIEW
    algorithm: str = "greedy_nearest_feasible_v1"
    matrix_provider: str = "haversine_estimate_v1"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    published_at: datetime | None = None


def haversine_meters(a: Location, b: Location) -> int:
    """Approximate straight-line distance between two WGS84 points."""
    earth_radius_m = 6_371_000
    d_lat = radians(b.lat - a.lat)
    d_lng = radians(b.lng - a.lng)
    lat1 = radians(a.lat)
    lat2 = radians(b.lat)
    h = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lng / 2) ** 2
    return int(2 * earth_radius_m * asin(sqrt(h)))


def estimate_travel_seconds(distance_meters: int, average_kph: float = 30.0) -> int:
    if average_kph <= 0:
        raise ValueError("average_kph must be positive")
    return int((distance_meters / 1000) / average_kph * 3600)


def combine(day: date, clock: time) -> datetime:
    return datetime.combine(day, clock)


ALLOWED_STATUS_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {OrderStatus.READY_TO_PLAN, OrderStatus.CANCELLED},
    OrderStatus.READY_TO_PLAN: {OrderStatus.PLANNED, OrderStatus.CANCELLED},
    OrderStatus.PLANNED: {OrderStatus.PUBLISHED, OrderStatus.READY_TO_PLAN, OrderStatus.CANCELLED},
    OrderStatus.PUBLISHED: {OrderStatus.ACCEPTED, OrderStatus.EN_ROUTE, OrderStatus.FAILED, OrderStatus.CANCELLED},
    OrderStatus.ACCEPTED: {OrderStatus.EN_ROUTE, OrderStatus.FAILED, OrderStatus.RETURNED},
    OrderStatus.EN_ROUTE: {OrderStatus.ARRIVED, OrderStatus.FAILED, OrderStatus.RETURNED},
    OrderStatus.ARRIVED: {OrderStatus.DELIVERED, OrderStatus.FAILED, OrderStatus.RETURNED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.FAILED: {OrderStatus.RETURNED},
    OrderStatus.RETURNED: set(),
    OrderStatus.CANCELLED: set(),
}


def assert_status_transition(from_status: OrderStatus, to_status: OrderStatus) -> None:
    if to_status not in ALLOWED_STATUS_TRANSITIONS[from_status]:
        raise ValueError(f"invalid order status transition: {from_status} -> {to_status}")


def route_summary(run: PlanningRun) -> dict[str, int]:
    assigned = sum(len(route.stops) for route in run.routes)
    return {
        "routes": len(run.routes),
        "assigned_orders": assigned,
        "unassigned_orders": len(run.unassigned_orders),
        "planned_distance_meters": sum(route.planned_distance_meters for route in run.routes),
        "planned_duration_seconds": sum(route.planned_duration_seconds for route in run.routes),
    }


def ready_orders(orders: Iterable[Order]) -> list[Order]:
    valid: list[Order] = []
    for order in orders:
        if not order.mark_ready_if_valid():
            valid.append(order)
    return valid
