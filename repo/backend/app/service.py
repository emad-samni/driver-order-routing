from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, time
from typing import Any

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
    Route,
    RouteStop,
    assert_status_transition,
    date,
    haversine_meters,
    estimate_travel_seconds,
    route_summary,
)
from .planner import GreedyRoutePlanner


class StatusEvent:
    def __init__(
        self,
        order_id: str,
        to_status: OrderStatus,
        actor_user_id: str,
        driver_id: str | None = None,
        from_status: OrderStatus | None = None,
        note: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.order_id = order_id
        self.to_status = to_status
        self.actor_user_id = actor_user_id
        self.driver_id = driver_id
        self.from_status = from_status
        self.note = note
        self.lat = lat
        self.lng = lng
        self.created_at = created_at or datetime.now(UTC)


class RoutingService:
    def __init__(self, planner: GreedyRoutePlanner | None = None, *, persist: bool = False, repository: Any | None = None) -> None:
        self.orders: dict[str, Order] = {}
        self.drivers: dict[str, Driver] = {}
        self.import_batches: dict[str, ImportBatch] = {}
        self.planning_runs: dict[str, PlanningRun] = {}
        self.status_events: list[StatusEvent] = []
        self.planner = planner or GreedyRoutePlanner()
        self.persist = False
        self.repository = None
        if persist:
            try:
                from .persistence import SqliteRepository
                self.repository = repository or SqliteRepository()
                self.persist = True
            except Exception:  # noqa: BLE001
                self.persist = False

    def _persist_order(self, order: Order) -> None:
        if self.persist and self.repository:
            self.repository.upsert_order(order)

    def _persist_driver(self, driver: Driver) -> None:
        if self.persist and self.repository:
            self.repository.upsert_driver(driver)

    def create_order(self, order: Order) -> tuple[Order, list[str]]:
        errors = order.mark_ready_if_valid()
        self.orders[order.id] = order
        self._persist_order(order)
        return order, errors

    def create_driver(self, driver: Driver) -> tuple[Driver, list[str]]:
        errors = driver.validate_for_planning()
        self.drivers[driver.id] = driver
        self._persist_driver(driver)
        return driver, errors

    def excel_template_schema(self) -> list[dict[str, str | bool]]:
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

    def import_orders_from_rows(self, rows: list[dict[str, object]], *, filename: str, planning_date: Any | None = None) -> ImportBatch:
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
        if self.persist and self.repository:
            self.repository.insert_import_batch(batch)
            for err in batch.row_errors:
                self.repository.insert_import_row_error(batch.id, err)
        return batch

    def run_planning(self, delivery_date: Any) -> PlanningRun:
        run = self.planner.plan(list(self.orders.values()), list(self.drivers.values()), delivery_date)
        self.planning_runs[run.id] = run
        if self.persist and self.repository:
            self.repository.insert_planning_run(run)
            for route in run.routes:
                self.repository.insert_route(route, run.id)
            for item in run.unassigned_orders:
                self.repository.insert_unassigned_order(run.id, item)
        return run

    def publish_plan(self, planning_run_id: str) -> PlanningRun:
        run = self.planning_runs[planning_run_id]
        for route in run.routes:
            for stop in route.stops:
                assert_status_transition(stop.order.status, OrderStatus.PUBLISHED)
                stop.order.status = OrderStatus.PUBLISHED
                stop.status = OrderStatus.PUBLISHED
                if self.persist and self.repository:
                    self.repository.update_order_status(stop.order.id, OrderStatus.PUBLISHED.value)
        run.status = PlanningStatus.PUBLISHED
        run.published_at = datetime.now(UTC)
        if self.persist and self.repository:
            self.repository.update_planning_run(run)
        return run

    def route_for_driver_today(self, driver_id: str, today: Any) -> list[dict]:
        visible: list[dict] = []
        for run in self.planning_runs.values():
            if run.delivery_date != today or run.status != PlanningStatus.PUBLISHED:
                continue
            for route in run.routes:
                if route.driver.id != driver_id:
                    continue
                for stop in sorted(route.stops, key=lambda s: s.sequence):
                    visible.append({
                        "order_id": stop.order.id,
                        "sequence": stop.sequence,
                        "recipient_name": stop.order.recipient_name,
                        "address": stop.order.address,
                        "planned_arrival": stop.planned_arrival.isoformat(),
                        "status": stop.order.status.value,
                        "navigation_url": self.navigation_url(stop.order),
                    })
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
        if self.persist and self.repository:
            self.repository.update_order_status(order_id, to_status.value)
            self.repository.insert_status_event(event)
        self.status_events.append(event)
        return event

    def move_order_between_drivers(self, order_id: str, target_driver_id: str, actor_user_id: str, note: str | None = None) -> tuple[Route, list[str], StatusEvent]:
        if not note or not str(note).strip():
            raise ValueError("audit note is required for manual driver change")
        source_route = self._find_route_with_order(order_id)
        if source_route is None:
            raise ValueError("order is not currently planned")
        source_driver = source_route.driver
        target_driver = self.drivers.get(target_driver_id)
        if target_driver is None:
            raise ValueError("target driver not found")
        if source_driver.id == target_driver.id:
            raise ValueError("order is already on that driver")
        warnings = self._feasibility_warnings_for_move(source_route, source_driver, target_driver, order_id)
        removed = self._remove_order_from_route(order_id, source_route)
        if removed is None:
            raise ValueError("order stop not found in source route")
        target_route = self._route_for_driver(target_driver.id)
        target_route.stops.append(removed)
        target_route.stops.sort(key=lambda stop: stop.planned_arrival)
        self._recompute_route_metrics(target_route)
        event = StatusEvent(
            order_id=order_id,
            to_status=OrderStatus.PLANNED,
            actor_user_id=actor_user_id,
            driver_id=target_driver.id,
            from_status=OrderStatus.PLANNED,
            note=str(note).strip() or None,
        )
        if self.persist and self.repository:
            self.repository.insert_status_event(event)
            self.repository.insert_audit_event(actor_user_id, "route_override", order_id, "move_order_between_drivers", None, str(note).strip() or None)
        self.status_events.append(event)
        return target_route, warnings, event

    def reorder_route_stops(self, driver_id: str, ordered_stop_order_ids: list[str], actor_user_id: str, note: str | None = None) -> tuple[Route, list[str], StatusEvent]:
        if not note or not str(note).strip():
            raise ValueError("audit note is required for manual route reorder")
        route = self._route_for_driver(driver_id)
        existing_ids = {stop.order.id for stop in route.stops}
        if set(ordered_stop_order_ids) != existing_ids:
            raise ValueError("reordered list must contain exactly the current route stops")
        stop_map = {stop.order.id: stop for stop in route.stops}
        new_stops: list[RouteStop] = []
        for idx, order_id in enumerate(ordered_stop_order_ids, start=1):
            stop = stop_map[order_id]
            stop.sequence = idx
            new_stops.append(stop)
        route.stops = new_stops
        self._recompute_route_metrics(route)
        warnings = self._shift_conflict_warnings(route)
        event = StatusEvent(
            order_id=route.stops[0].order.id if route.stops else "",
            to_status=OrderStatus.PLANNED,
            actor_user_id=actor_user_id,
            driver_id=driver_id,
            from_status=OrderStatus.PLANNED,
            note=str(note).strip() or None,
        )
        self.status_events.append(event)
        if self.persist and self.repository:
            self.repository.insert_status_event(event)
            self.repository.insert_audit_event(actor_user_id, "route_override", driver_id, "reorder_route_stops", None, str(note).strip() or None)
        return route, warnings, event

    def _find_route_with_order(self, order_id: str) -> Route | None:
        for run in self.planning_runs.values():
            for route in run.routes:
                if any(stop.order.id == order_id for stop in route.stops):
                    return route
        return None

    def _route_for_driver(self, driver_id: str) -> Route:
        latest_run = max(self.planning_runs.values(), key=lambda run: run.created_at, default=None)
        if latest_run is None:
            raise ValueError("no planning run exists yet")
        for route in latest_run.routes:
            if route.driver.id == driver_id:
                return route
        raise ValueError("driver has no route in the latest planning run")

    def _remove_order_from_route(self, order_id: str, route: Route) -> RouteStop | None:
        for idx, stop in enumerate(route.stops):
            if stop.order.id == order_id:
                return route.stops.pop(idx)
        return None

    def _recompute_route_metrics(self, route: Route) -> None:
        distance = 0
        duration = 0
        waypoints = [route.driver.start_location] + [stop.order.location for stop in route.stops if stop.order.location]
        for a, b in zip(waypoints, waypoints[1:]):
            distance += haversine_meters(a, b)
        for stop in route.stops:
            duration += stop.order.service_duration_minutes * 60
        duration += estimate_travel_seconds(distance)
        route.planned_distance_meters = distance
        route.planned_duration_seconds = duration

    def _feasibility_warnings_for_move(self, source_route: Route, source_driver: Driver, target_driver: Driver, order_id: str) -> list[str]:
        warnings: list[str] = []
        target_route = None
        for run in self.planning_runs.values():
            for route in run.routes:
                if route.driver.id == target_driver.id:
                    target_route = route
        if target_route is not None:
            stop_count = len(target_route.stops) + 1
            if stop_count > target_driver.max_stops:
                warnings.append(f"target driver will exceed max stops: {stop_count}/{target_driver.max_stops}")
        if target_driver.capacity_units <= 0:
            warnings.append("target driver capacity is non-positive")
        return warnings

    def _shift_conflict_warnings(self, route: Route) -> list[str]:
        warnings: list[str] = []
        for stop in route.stops:
            if stop.planned_arrival.time() < route.driver.shift_start or stop.planned_arrival.time() > route.driver.shift_end:
                warnings.append(f"stop {stop.sequence} falls outside driver shift window")
        return warnings

    def dispatch_dashboard(self) -> dict:
        by_status: dict[str, int] = {}
        for order in self.orders.values():
            by_status[order.status.value] = by_status.get(order.status.value, 0) + 1
        latest_run = max(self.planning_runs.values(), key=lambda r: r.created_at, default=None)
        return {
            "orders_by_status": by_status,
            "total_orders": len(self.orders),
            "total_drivers": len(self.drivers),
            "latest_plan_summary": route_summary(latest_run) if latest_run else None,
            "status_event_count": len(self.status_events),
        }

    def daily_summary(self, *, tenant_id: str | None = None) -> dict:
        orders = list(self.orders.values())
        drivers = list(self.drivers.values())
        if tenant_id:
            orders = [order for order in orders if order.tenant_id == tenant_id]
            drivers = [driver for driver in drivers if getattr(driver, "tenant_id", None) == tenant_id]
        by_status: dict[str, int] = {}
        for order in orders:
            by_status[order.status.value] = by_status.get(order.status.value, 0) + 1
        latest_run = max(self.planning_runs.values(), key=lambda run: run.created_at, default=None)
        summary = route_summary(latest_run) if latest_run else {}
        return {
            "tenant_id": tenant_id,
            "total_orders": len(orders),
            "orders_by_status": by_status,
            "total_drivers": len(drivers),
            "plan_summary": summary,
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
