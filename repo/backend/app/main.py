"""FastAPI runtime wrapper around the existing in-memory routing service.

This module exposes the domain/service logic over HTTP and includes a real
`.xlsx` upload parser for `POST /orders/import/excel`. It uses `openpyxl`,
which is already available in the backend venv for this prototype.
"""

from __future__ import annotations

import os
from datetime import date, time
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from .domain import (
    Driver,
    DriverAvailability,
    ImportErrorCode,
    ImportRowError,
    Location,
    Order,
    OrderStatus,
    PlanningStatus,
    PlanningRun,
    Route,
    RouteStop,
    UnassignedOrder,
    route_summary,
)
from .import_parser import parse_xlsx_rows
from .planner import GreedyRoutePlanner
from .service import RoutingService

try:
    from .service_persisted import PersistedRoutingService
except ImportError:  # pragma: no cover
    PersistedRoutingService = None  # type: ignore[misc, assignment]

app = FastAPI(title="Driver Order Routing API", version="0.1.0")

_use_persisted = os.getenv("USE_PERSISTED_SERVICE", "").lower() in {"1", "true", "yes"}
if PersistedRoutingService and _use_persisted:
    service = PersistedRoutingService()
else:
    service = RoutingService(planner=GreedyRoutePlanner())


def _optional_auth_dependency(required_role: str):
    middleware_enabled = os.getenv("REQUIRE_API_KEY", "").lower() in {"1", "true", "yes"}
    if not middleware_enabled:
        return lambda: None
    try:
        from .auth import require_role
        return require_role(required_role)
    except ImportError:
        return lambda: None


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/excel-template")
def excel_template() -> JSONResponse:
    return JSONResponse({"columns": service.excel_template_schema()})


@app.post("/orders/import/excel")
async def import_excel_batch(request: Request) -> JSONResponse:
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()
        upload = form.get("upload")
        if upload is None:
            raise HTTPException(status_code=400, detail="Missing upload field")
        content = await upload.read()
        filename = getattr(upload, "filename", None) or "uploaded.xlsx"
    else:
        content = await request.body()
        filename = "uploaded.xlsx"
    try:
        rows = parse_xlsx_rows(content)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid Excel file: {exc}") from exc
    batch = service.import_orders_from_rows(rows, filename=filename)
    return JSONResponse(
        {
            "id": batch.id,
            "filename": batch.filename,
            "planning_date": batch.planning_date.isoformat() if batch.planning_date else None,
            "total_rows": batch.total_rows,
            "valid_rows": batch.valid_rows,
            "invalid_rows": batch.invalid_rows,
            "duplicate_rows": batch.duplicate_rows,
            "routeable_rows": batch.routeable_rows,
            "status": batch.status,
            "row_errors": [
                {
                    "row_number": err.row_number,
                    "field": err.field,
                    "error_code": err.error_code.value,
                    "message": err.message,
                    "suggested_fix": err.suggested_fix,
                }
                for err in batch.row_errors
            ],
            "imported_order_ids": batch.imported_order_ids,
        },
        status_code=201,
    )


@app.get("/import-batches/{batch_id}")
def get_import_batch(batch_id: str) -> JSONResponse:
    batch = service.import_batches.get(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")
    return JSONResponse(
        {
            "id": batch.id,
            "filename": batch.filename,
            "planning_date": batch.planning_date.isoformat() if batch.planning_date else None,
            "total_rows": batch.total_rows,
            "valid_rows": batch.valid_rows,
            "invalid_rows": batch.invalid_rows,
            "duplicate_rows": batch.duplicate_rows,
            "routeable_rows": batch.routeable_rows,
            "status": batch.status,
            "row_errors": [
                {
                    "row_number": err.row_number,
                    "field": err.field,
                    "error_code": err.error_code.value,
                    "message": err.message,
                    "suggested_fix": err.suggested_fix,
                }
                for err in batch.row_errors
            ],
            "imported_order_ids": batch.imported_order_ids,
        }
    )


@app.post("/orders")
def create_order(payload: dict[str, Any]) -> JSONResponse:
    try:
        order = _order_from_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    created, errors = service.create_order(order)
    return JSONResponse(_order_payload(created), status_code=201 if not errors else 200)


@app.get("/orders")
def list_orders() -> JSONResponse:
    return JSONResponse([_order_payload(o) for o in service.orders.values()])


@app.post("/drivers")
def create_driver(payload: dict[str, Any]) -> JSONResponse:
    try:
        driver = _driver_from_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    created, errors = service.create_driver(driver)
    response = _driver_payload(created)
    response["errors"] = errors
    return JSONResponse(response)


@app.get("/drivers")
def list_drivers() -> JSONResponse:
    return JSONResponse([_driver_payload(d) for d in service.drivers.values()])


@app.post("/planning-runs")
def run_planning(payload: dict[str, Any]) -> JSONResponse:
    delivery_date_raw = payload.get("delivery_date")
    if delivery_date_raw is None:
        raise HTTPException(status_code=400, detail="delivery_date is required")
    try:
        delivery_date = date.fromisoformat(str(delivery_date_raw))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="delivery_date must be YYYY-MM-DD") from exc
    run = service.run_planning(delivery_date)
    return JSONResponse(_planning_run_payload(run), status_code=201)


@app.post("/planning-runs/{run_id}/publish")
def publish_plan(run_id: str) -> JSONResponse:
    run = service.planning_runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Planning run not found")
    published = service.publish_plan(run_id)
    return JSONResponse(_planning_run_payload(published))


@app.get("/driver/me/routes/today")
def driver_routes_today(
    driver_id: str = Query(..., description="Current driver identity"),
    today: str | None = Query(None, description="ISO delivery date, defaults to current date"),
) -> JSONResponse:
    target_date = date.fromisoformat(today) if today else date.today()
    visible = service.route_for_driver_today(driver_id, target_date)
    return JSONResponse(visible)


@app.post("/orders/{order_id}/status-events")
def order_status_event(order_id: str, payload: dict[str, Any]) -> JSONResponse:
    if order_id not in service.orders:
        raise HTTPException(status_code=404, detail="Order not found")
    to_status_raw = payload.get("to_status")
    if not to_status_raw:
        raise HTTPException(status_code=400, detail="to_status is required")
    try:
        to_status = OrderStatus(str(to_status_raw))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid to_status") from exc
    actor_user_id = str(payload.get("actor_user_id") or "anonymous")
    driver_id = payload.get("driver_id")
    note = payload.get("note")
    event = service.update_order_status(
        order_id,
        to_status,
        actor_user_id,
        driver_id=str(driver_id) if driver_id else None,
        note=str(note) if note else None,
    )
    return JSONResponse(
        {
            "order_id": event.order_id,
            "from_status": event.from_status.value if event.from_status else None,
            "to_status": event.to_status.value,
            "actor_user_id": event.actor_user_id,
            "driver_id": event.driver_id,
            "note": event.note,
            "created_at": event.created_at.isoformat(),
        }
    )


@app.get("/dashboard/dispatch")
def dispatch_dashboard() -> JSONResponse:
    return JSONResponse(service.dispatch_dashboard())


@app.post("/planning-runs/{run_id}/override/move")
def override_move_order(run_id: str, payload: dict[str, Any]) -> JSONResponse:
    order_id = str(payload.get("order_id") or "")
    target_driver_id = str(payload.get("target_driver_id") or "")
    actor_user_id = str(payload.get("actor_user_id") or "anonymous")
    note = payload.get("note")
    if not order_id or not target_driver_id:
        raise HTTPException(status_code=400, detail="order_id and target_driver_id are required")
    if run_id not in service.planning_runs:
        raise HTTPException(status_code=404, detail="Planning run not found")
    route, warnings, event = service.move_order_between_drivers(order_id, target_driver_id, actor_user_id, note=note)
    if route is None:
        raise HTTPException(status_code=404, detail="order is not currently planned")
    return JSONResponse(
        {
            "run_id": run_id,
            "route": {
                "driver_id": route.driver.id,
                "driver_name": route.driver.name,
                "planned_distance_meters": route.planned_distance_meters,
                "planned_duration_seconds": route.planned_duration_seconds,
                "stops": [
                    {
                        "sequence": stop.sequence,
                        "order_id": stop.order.id,
                        "recipient_name": stop.order.recipient_name,
                        "planned_arrival": stop.planned_arrival.isoformat(),
                        "status": stop.status.value,
                    }
                    for stop in route.stops
                ],
            },
            "warnings": warnings,
            "audit_event": {
                "order_id": event.order_id,
                "actor_user_id": event.actor_user_id,
                "driver_id": event.driver_id,
                "note": event.note,
                "created_at": event.created_at.isoformat(),
            },
        }
    )


@app.post("/planning-runs/{run_id}/override/reorder")
def override_reorder_stops(run_id: str, payload: dict[str, Any]) -> JSONResponse:
    driver_id = str(payload.get("driver_id") or "")
    ordered_stop_order_ids = [str(item) for item in (payload.get("ordered_stop_order_ids") or [])]
    actor_user_id = str(payload.get("actor_user_id") or "anonymous")
    note = payload.get("note")
    if not driver_id or not ordered_stop_order_ids:
        raise HTTPException(status_code=400, detail="driver_id and ordered_stop_order_ids are required")
    if run_id not in service.planning_runs:
        raise HTTPException(status_code=404, detail="Planning run not found")
    route, warnings, event = service.reorder_route_stops(driver_id, ordered_stop_order_ids, actor_user_id, note=note)
    return JSONResponse(
        {
            "run_id": run_id,
            "route": {
                "driver_id": route.driver.id,
                "driver_name": route.driver.name,
                "planned_distance_meters": route.planned_distance_meters,
                "planned_duration_seconds": route.planned_duration_seconds,
                "stops": [
                    {
                        "sequence": stop.sequence,
                        "order_id": stop.order.id,
                        "recipient_name": stop.order.recipient_name,
                        "planned_arrival": stop.planned_arrival.isoformat(),
                        "status": stop.status.value,
                    }
                    for stop in route.stops
                ],
            },
            "warnings": warnings,
            "audit_event": {
                "order_id": event.order_id,
                "actor_user_id": event.actor_user_id,
                "driver_id": event.driver_id,
                "note": event.note,
                "created_at": event.created_at.isoformat(),
            },
        }
    )


def _order_payload(order: Order) -> dict[str, Any]:
    return {
        "id": order.id,
        "external_order_id": order.external_order_id,
        "recipient_name": order.recipient_name,
        "address": order.address,
        "delivery_date": order.delivery_date.isoformat(),
        "time_window_start": order.time_window_start.isoformat(),
        "time_window_end": order.time_window_end.isoformat(),
        "status": order.status.value,
        "priority": order.priority,
        "phone": order.phone,
        "service_duration_minutes": order.service_duration_minutes,
        "package_units": order.package_units,
        "special_instructions": order.special_instructions,
        "location": (
            {"lat": order.location.lat, "lng": order.location.lng} if order.location else None
        ),
        "geocode_status": order.geocode_status,
    }


def _driver_payload(driver: Driver) -> dict[str, Any]:
    return {
        "id": driver.id,
        "name": driver.name,
        "phone": driver.phone,
        "start_address": driver.start_address,
        "start_location": (
            {"lat": driver.start_location.lat, "lng": driver.start_location.lng}
        ),
        "shift_start": driver.shift_start.isoformat(),
        "shift_end": driver.shift_end.isoformat(),
        "availability_status": driver.availability_status.value,
        "max_stops": driver.max_stops,
        "capacity_units": driver.capacity_units,
        "vehicle_type": driver.vehicle_type,
    }


def _route_stop_payload(stop: RouteStop) -> dict[str, Any]:
    return {
        "sequence": stop.sequence,
        "order_id": stop.order.id,
        "recipient_name": stop.order.recipient_name,
        "address": stop.order.address,
        "planned_arrival": stop.planned_arrival.isoformat(),
        "planned_departure": stop.planned_departure.isoformat(),
        "status": stop.status.value,
        "navigation_url": service.navigation_url(stop.order),
    }


def _planning_run_payload(run: PlanningRun) -> dict[str, Any]:
    return {
        "id": run.id,
        "delivery_date": run.delivery_date.isoformat(),
        "status": run.status.value,
        "algorithm": run.algorithm,
        "matrix_provider": run.matrix_provider,
        "created_at": run.created_at.isoformat(),
        "published_at": run.published_at.isoformat() if run.published_at else None,
        "summary": route_summary(run),
        "routes": [
            {
                "driver_id": route.driver.id,
                "driver_name": route.driver.name,
                "planned_distance_meters": route.planned_distance_meters,
                "planned_duration_seconds": route.planned_duration_seconds,
                "stops": [_route_stop_payload(stop) for stop in route.stops],
            }
            for route in run.routes
        ],
        "unassigned_orders": [
            {
                "order_id": item.order.id,
                "reason_code": item.reason_code.value,
                "details": item.details,
            }
            for item in run.unassigned_orders
        ],
    }


def _order_from_payload(payload: dict[str, Any]) -> Order:
    location = None
    lat = payload.get("latitude") if payload.get("latitude") is not None else payload.get("location", {}).get("lat")
    lng = payload.get("longitude") if payload.get("longitude") is not None else payload.get("location", {}).get("lng")
    if lat is not None and lng is not None:
        location = Location(float(lat), float(lng))
    window_start_raw = payload.get("time_window_start") or payload.get("time_window", {}).get("start")
    window_end_raw = payload.get("time_window_end") or payload.get("time_window", {}).get("end")
    if not window_start_raw or not window_end_raw:
        raise ValueError("time_window_start and time_window_end are required")
    return Order(
        external_order_id=payload.get("order_id"),
        recipient_name=str(payload.get("recipient_name") or payload.get("customer_name") or ""),
        address=str(payload.get("address") or payload.get("street_address") or ""),
        delivery_date=date.fromisoformat(str(payload.get("delivery_date"))),
        time_window_start=time.fromisoformat(str(window_start_raw)),
        time_window_end=time.fromisoformat(str(window_end_raw)),
        location=location,
        phone=payload.get("phone"),
        priority=str(payload.get("priority") or "normal"),
        service_duration_minutes=int(payload.get("service_minutes") or 10),
        package_units=int(payload.get("package_units") or 1),
        special_instructions=payload.get("instructions"),
    )


def _driver_from_payload(payload: dict[str, Any]) -> Driver:
    start = payload.get("start_location") or {}
    lat = start.get("lat") or start.get("latitude")
    lng = start.get("lng") or start.get("longitude")
    if lat is None or lng is None:
        raise ValueError("start_location lat/lng are required")
    start_raw = payload.get("shift") or {}
    shift_start = str(start_raw.get("start") or payload.get("shift_start") or "08:00")
    shift_end = str(start_raw.get("end") or payload.get("shift_end") or "18:00")
    return Driver(
        name=str(payload.get("name") or payload.get("driver_name") or ""),
        start_location=Location(float(lat), float(lng)),
        shift_start=time.fromisoformat(shift_start),
        shift_end=time.fromisoformat(shift_end),
        phone=payload.get("phone"),
        start_address=payload.get("start_address"),
        availability_status=DriverAvailability(payload.get("availability_status") or DriverAvailability.AVAILABLE),
        max_stops=int(payload.get("max_stops") or 25),
        capacity_units=int(payload.get("capacity_units") or 999),
        vehicle_type=payload.get("vehicle_type"),
    )

# Allow public localtunnel testing from any origin for the pilot.
try:
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=False,
        allow_methods=['*'],
        allow_headers=['*'],
    )
except Exception:  # noqa: BLE001
    pass

# Serve frontend files after API routes so same-origin testing works.
try:
    from fastapi.staticfiles import StaticFiles
    FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend'))
    if os.path.isdir(FRONTEND_DIR):
        app.mount('/', StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')
except Exception:  # noqa: BLE001
    pass
