"""In-memory service layer used by the backend prototype and tests.

FastAPI endpoints can wrap these methods directly. Persistence is deliberately
in-memory for this evening prototype; table names/fields are documented in
`docs/api-and-schema.md` for later PostgreSQL implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time

from .domain import (
    Driver,
    ImportBatch,
    ImportErrorCode,
    ImportRowError,
    Location,
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
        self.import_batches: dict[str, ImportBatch] = {}
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

    def excel_template_schema(self) -> list[dict[str, str | bool]]:
        """Return the MVP Excel template columns for UI/API documentation.

        The future FastAPI `.xlsx` upload parser should convert worksheet rows
        into dictionaries and call `import_orders_from_rows`; this keeps the
        validation behavior deterministic and unit-testable without adding a
        spreadsheet dependency during this no-spend prototype stage.
        """
        return [
            {"column": "order_id", "required": True, "example": "RET-100231"},
            {"column": "customer_name", "required": True, "example": "A. Müller"},
            {"column": "street_address", "required": True, "example": "Alexanderplatz 1"},
            {"column": "postal_code", "required": True, "example": "10178"},
            {"column": "city", "required": True, "example": "Berlin"},
            {"column": "country", "required": False, "example": "DE"},
            {"column": "latitude", "required": False, "example": "52.5219"},
            {"column": "longitude", "required": False, "example": "13.4132"},
            {"column": "delivery_date", "required": True, "example": "2026-08-03"},
            {"column": "time_window_start", "required": True, "example": "09:00"},
            {"column": "time_window_end", "required": True, "example": "13:00"},
            {"column": "service_minutes", "required": False, "example": "10"},
            {"column": "priority", "required": False, "example": "normal"},
            {"column": "phone", "required": False, "example": "+49..."},
            {"column": "package_units", "required": False, "example": "2"},
            {"column": "instructions", "required": False, "example": "Call before arrival"},
        ]

    def import_orders_from_rows(self, rows: list[dict[str, object]], *, filename: str, planning_date: date | None = None) -> ImportBatch:
        """Import Excel-normalized order rows with row-level validation.

        Valid coordinate-backed rows become `ready_to_plan`. Rows that are
        otherwise valid but missing coordinates are imported as `draft` with a
        `geocoding_required` row error so dispatchers can fix them manually.
        Hard-invalid rows are rejected and not inserted.
        """
        batch = ImportBatch(filename=filename, planning_date=planning_date, total_rows=len(rows))
        seen_external_ids: set[str] = set()

        for row_number, row in enumerate(rows, start=2):
            row_errors: list[ImportRowError] = []
            external_order_id = self._text(row.get("order_id"))
            customer_name = self._text(row.get("customer_name"))
            street_address = self._text(row.get("street_address") or row.get("address"))
            postal_code = self._text(row.get("postal_code"))
            city = self._text(row.get("city"))
            country = self._text(row.get("country")) or "DE"

            required_values = {
                "order_id": external_order_id,
                "customer_name": customer_name,
                "street_address": street_address,
                "postal_code": postal_code,
                "city": city,
                "delivery_date": self._text(row.get("delivery_date")),
                "time_window_start": self._text(row.get("time_window_start")),
                "time_window_end": self._text(row.get("time_window_end")),
            }
            for field_name, value in required_values.items():
                if not value:
                    row_errors.append(self._row_error(row_number, field_name, ImportErrorCode.MISSING_REQUIRED_FIELD, f"{field_name} is required", "Fill this column in the Excel row."))

            if external_order_id and external_order_id in seen_external_ids:
                row_errors.append(self._row_error(row_number, "order_id", ImportErrorCode.DUPLICATE_ORDER_ID, "order_id is duplicated within this import", "Use a unique retailer order ID for each row."))
                batch.duplicate_rows += 1
            if external_order_id:
                seen_external_ids.add(external_order_id)

            delivery_date = self._parse_date(row.get("delivery_date"), row_number, row_errors)
            window_start = self._parse_time(row.get("time_window_start"), row_number, "time_window_start", row_errors)
            window_end = self._parse_time(row.get("time_window_end"), row_number, "time_window_end", row_errors)
            if window_start and window_end and window_end <= window_start:
                row_errors.append(self._row_error(row_number, "time_window_end", ImportErrorCode.INVALID_TIME_WINDOW, "time_window_end must be after time_window_start", "Correct the delivery time window."))

            lat = self._parse_optional_float(row.get("latitude"), row_number, "latitude", row_errors)
            lng = self._parse_optional_float(row.get("longitude"), row_number, "longitude", row_errors)
            location = None
            if lat is None or lng is None:
                row_errors.append(self._row_error(row_number, "latitude/longitude", ImportErrorCode.GEOCODING_REQUIRED, "coordinates are missing; row can be saved but is not routeable in the no-spend prototype", "Add latitude and longitude or geocode manually before planning."))
            else:
                location = Location(lat, lng)
                try:
                    location.validate()
                except ValueError as exc:
                    row_errors.append(self._row_error(row_number, "latitude/longitude", ImportErrorCode.INVALID_COORDINATE, str(exc), "Use valid WGS84 latitude and longitude."))
                    location = None

            priority = self._text(row.get("priority")) or "normal"
            if priority not in {"low", "normal", "high"}:
                row_errors.append(self._row_error(row_number, "priority", ImportErrorCode.INVALID_PRIORITY, "priority must be low, normal, or high", "Use one of: low, normal, high."))

            service_minutes = self._parse_optional_int(row.get("service_minutes"), row_number, "service_minutes", row_errors) or 10
            package_units = self._parse_optional_int(row.get("package_units"), row_number, "package_units", row_errors) or 1
            address = ", ".join(part for part in [street_address, postal_code, city, country] if part)

            hard_errors = [error for error in row_errors if error.error_code != ImportErrorCode.GEOCODING_REQUIRED]
            if hard_errors or delivery_date is None or window_start is None or window_end is None:
                batch.invalid_rows += 1
                batch.row_errors.extend(row_errors)
                continue

            order = Order(
                external_order_id=external_order_id,
                recipient_name=customer_name,
                address=address,
                delivery_date=delivery_date,
                time_window_start=window_start,
                time_window_end=window_end,
                location=location,
                phone=self._text(row.get("phone")) or None,
                priority=priority,
                service_duration_minutes=service_minutes,
                package_units=package_units,
                special_instructions=self._text(row.get("instructions")) or None,
                import_batch_id=batch.id,
                import_row_number=row_number,
                geocode_status="coordinates_supplied" if location else "geocoding_required",
            )
            if location:
                order.status = OrderStatus.READY_TO_PLAN
                batch.valid_rows += 1
                batch.routeable_rows += 1
            else:
                order.status = OrderStatus.DRAFT
                batch.invalid_rows += 1
                batch.row_errors.extend(row_errors)
            self.orders[order.id] = order
            batch.imported_order_ids.append(order.id)

        self.import_batches[batch.id] = batch
        return batch

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

    @staticmethod
    def _text(value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def _row_error(row_number: int, field: str, code: ImportErrorCode, message: str, suggested_fix: str) -> ImportRowError:
        return ImportRowError(row_number=row_number, field=field, error_code=code, message=message, suggested_fix=suggested_fix)

    def _parse_date(self, value: object, row_number: int, errors: list[ImportRowError]) -> date | None:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        text = self._text(value)
        if not text:
            return None
        try:
            return date.fromisoformat(text)
        except ValueError:
            errors.append(self._row_error(row_number, "delivery_date", ImportErrorCode.INVALID_DATE, "delivery_date must use YYYY-MM-DD", "Use an ISO date such as 2026-08-03."))
            return None

    def _parse_time(self, value: object, row_number: int, field_name: str, errors: list[ImportRowError]) -> time | None:
        if isinstance(value, time):
            return value
        text = self._text(value)
        if not text:
            return None
        try:
            return time.fromisoformat(text)
        except ValueError:
            errors.append(self._row_error(row_number, field_name, ImportErrorCode.INVALID_TIME_WINDOW, f"{field_name} must use HH:MM", "Use a 24-hour time such as 09:00."))
            return None

    def _parse_optional_float(self, value: object, row_number: int, field_name: str, errors: list[ImportRowError]) -> float | None:
        text = self._text(value)
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            errors.append(self._row_error(row_number, field_name, ImportErrorCode.INVALID_COORDINATE, f"{field_name} must be numeric", "Use a decimal coordinate."))
            return None

    def _parse_optional_int(self, value: object, row_number: int, field_name: str, errors: list[ImportRowError]) -> int | None:
        text = self._text(value)
        if not text:
            return None
        try:
            parsed = int(text)
        except ValueError:
            errors.append(self._row_error(row_number, field_name, ImportErrorCode.INVALID_NUMBER, f"{field_name} must be an integer", "Use a whole number."))
            return None
        if parsed <= 0:
            errors.append(self._row_error(row_number, field_name, ImportErrorCode.INVALID_NUMBER, f"{field_name} must be positive", "Use a value greater than zero."))
            return None
        return parsed
