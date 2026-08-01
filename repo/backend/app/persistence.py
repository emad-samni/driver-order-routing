"""SQLite persistence layer for the driver order routing prototype.

This module provides real disk-backed storage using only Python stdlib
`sqlite3`, so it works without adding third-party dependencies.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from datetime import date, datetime, time
from typing import Any, Iterator

DB_PATH = "driver_routing.sqlite3"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS drivers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    start_address TEXT,
    start_lat REAL NOT NULL,
    start_lng REAL NOT NULL,
    shift_start TEXT NOT NULL,
    shift_end TEXT NOT NULL,
    availability_status TEXT NOT NULL DEFAULT 'available',
    max_stops INTEGER NOT NULL DEFAULT 25,
    capacity_units INTEGER NOT NULL DEFAULT 999,
    vehicle_type TEXT,
    user_id TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    external_order_id TEXT,
    recipient_name TEXT NOT NULL,
    address TEXT NOT NULL,
    lat REAL,
    lng REAL,
    geocode_status TEXT NOT NULL DEFAULT 'manual_or_pending',
    phone TEXT,
    delivery_date TEXT NOT NULL,
    time_window_start TEXT NOT NULL,
    time_window_end TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'normal',
    service_duration_minutes INTEGER NOT NULL DEFAULT 10,
    package_units INTEGER NOT NULL DEFAULT 1,
    special_instructions TEXT,
    status TEXT NOT NULL,
    proof_note TEXT,
    failure_reason TEXT,
    import_batch_id TEXT,
    import_row_number INTEGER,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS import_batches (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    planning_date TEXT,
    total_rows INTEGER NOT NULL DEFAULT 0,
    valid_rows INTEGER NOT NULL DEFAULT 0,
    invalid_rows INTEGER NOT NULL DEFAULT 0,
    duplicate_rows INTEGER NOT NULL DEFAULT 0,
    routeable_rows INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS import_row_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    import_batch_id TEXT NOT NULL,
    row_number INTEGER NOT NULL,
    field TEXT NOT NULL,
    error_code TEXT NOT NULL,
    message TEXT NOT NULL,
    suggested_fix TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS planning_runs (
    id TEXT PRIMARY KEY,
    delivery_date TEXT NOT NULL,
    status TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    matrix_provider TEXT NOT NULL,
    started_by TEXT,
    created_at TEXT NOT NULL,
    published_at TEXT
);
CREATE TABLE IF NOT EXISTS routes (
    id TEXT PRIMARY KEY,
    planning_run_id TEXT NOT NULL,
    driver_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'review',
    planned_distance_meters INTEGER NOT NULL DEFAULT 0,
    planned_duration_seconds INTEGER NOT NULL DEFAULT 0,
    starts_at TEXT,
    ends_at TEXT
);
CREATE TABLE IF NOT EXISTS route_stops (
    id TEXT PRIMARY KEY,
    route_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    planned_arrival TEXT NOT NULL,
    planned_departure TEXT NOT NULL,
    eta_status TEXT,
    status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS unassigned_orders (
    id TEXT PRIMARY KEY,
    planning_run_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    details TEXT
);
CREATE TABLE IF NOT EXISTS status_events (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    driver_id TEXT,
    actor_user_id TEXT NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    note TEXT,
    lat REAL,
    lng REAL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    actor_user_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    action TEXT NOT NULL,
    before_json TEXT,
    after_json TEXT,
    created_at TEXT NOT NULL
);
"""


class PersistenceError(Exception):
    pass


class SqliteRepository:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._local = threading.local()
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        if hasattr(self._local, "connection"):
            return self._local.connection
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        self._local.connection = conn
        return conn

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def _ensure_schema(self) -> None:
        conn = self._connect()
        conn.executescript(SCHEMA_SQL)
        conn.commit()

    # --- Drivers ---
    def upsert_driver(self, driver: Any) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO drivers (id, name, phone, start_address, start_lat, start_lng, shift_start, shift_end, availability_status, max_stops, capacity_units, vehicle_type, user_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  name=excluded.name,
                  phone=excluded.phone,
                  start_address=excluded.start_address,
                  start_lat=excluded.start_lat,
                  start_lng=excluded.start_lng,
                  shift_start=excluded.shift_start,
                  shift_end=excluded.shift_end,
                  availability_status=excluded.availability_status,
                  max_stops=excluded.max_stops,
                  capacity_units=excluded.capacity_units,
                  vehicle_type=excluded.vehicle_type
                """,
                (
                    driver.id,
                    driver.name,
                    driver.phone,
                    driver.start_address,
                    driver.start_location.lat if driver.start_location else None,
                    driver.start_location.lng if driver.start_location else None,
                    driver.shift_start.isoformat(),
                    driver.shift_end.isoformat(),
                    driver.availability_status.value,
                    driver.max_stops,
                    driver.capacity_units,
                    driver.vehicle_type,
                    getattr(driver, "user_id", None),
                    datetime.now(__import__("datetime").UTC).isoformat(),
                ),
            )

    def list_drivers(self) -> list[dict[str, Any]]:
        with self.session() as conn:
            rows = conn.execute("SELECT * FROM drivers").fetchall()
            return [dict(row) for row in rows]

    # --- Orders ---
    def upsert_order(self, order: Any) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO orders (id, external_order_id, recipient_name, address, lat, lng, geocode_status, phone, delivery_date, time_window_start, time_window_end, priority, service_duration_minutes, package_units, special_instructions, status, proof_note, failure_reason, import_batch_id, import_row_number, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  external_order_id=excluded.external_order_id,
                  recipient_name=excluded.recipient_name,
                  address=excluded.address,
                  lat=excluded.lat,
                  lng=excluded.lng,
                  geocode_status=excluded.geocode_status,
                  phone=excluded.phone,
                  delivery_date=excluded.delivery_date,
                  time_window_start=excluded.time_window_start,
                  time_window_end=excluded.time_window_end,
                  priority=excluded.priority,
                  service_duration_minutes=excluded.service_duration_minutes,
                  package_units=excluded.package_units,
                  special_instructions=excluded.special_instructions,
                  status=excluded.status,
                  proof_note=excluded.proof_note,
                  failure_reason=excluded.failure_reason,
                  import_batch_id=excluded.import_batch_id,
                  import_row_number=excluded.import_row_number
                """,
                (
                    order.id,
                    order.external_order_id,
                    order.recipient_name,
                    order.address,
                    order.location.lat if order.location else None,
                    order.location.lng if order.location else None,
                    getattr(order, "geocode_status", "manual_or_pending"),
                    order.phone,
                    order.delivery_date.isoformat(),
                    order.time_window_start.isoformat(),
                    order.time_window_end.isoformat(),
                    order.priority,
                    order.service_duration_minutes,
                    order.package_units,
                    order.special_instructions,
                    order.status.value,
                    getattr(order, "proof_note", None),
                    getattr(order, "failure_reason", None),
                    getattr(order, "import_batch_id", None),
                    getattr(order, "import_row_number", None),
                    datetime.now(__import__("datetime").UTC).isoformat(),
                ),
            )

    def list_orders(self) -> list[dict[str, Any]]:
        with self.session() as conn:
            rows = conn.execute("SELECT * FROM orders").fetchall()
            return [dict(row) for row in rows]

    def update_order_status(self, order_id: str, status: str) -> None:
        with self.session() as conn:
            conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))

    # --- Import batches ---
    def insert_import_batch(self, batch: Any) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO import_batches (id, filename, planning_date, total_rows, valid_rows, invalid_rows, duplicate_rows, routeable_rows, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch.id,
                    batch.filename,
                    batch.planning_date.isoformat() if batch.planning_date else None,
                    batch.total_rows,
                    batch.valid_rows,
                    batch.invalid_rows,
                    batch.duplicate_rows,
                    batch.routeable_rows,
                    batch.status,
                    batch.created_at.isoformat(),
                ),
            )

    def insert_import_row_error(self, batch_id: str, err: Any) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO import_row_errors (import_batch_id, row_number, field, error_code, message, suggested_fix)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    err.row_number,
                    err.field,
                    err.error_code.value,
                    err.message,
                    err.suggested_fix,
                ),
            )

    def list_import_batches(self) -> list[dict[str, Any]]:
        with self.session() as conn:
            rows = conn.execute("SELECT * FROM import_batches ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def get_import_batch(self, batch_id: str) -> dict[str, Any] | None:
        with self.session() as conn:
            row = conn.execute("SELECT * FROM import_batches WHERE id = ?", (batch_id,)).fetchone()
            return dict(row) if row else None

    # --- Planning runs ---
    def insert_planning_run(self, run: Any) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO planning_runs (id, delivery_date, status, algorithm, matrix_provider, started_by, created_at, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.delivery_date.isoformat(),
                    run.status.value,
                    run.algorithm,
                    run.matrix_provider,
                    None,
                    run.created_at.isoformat(),
                    run.published_at.isoformat() if run.published_at else None,
                ),
            )

    def update_planning_run(self, run: Any) -> None:
        with self.session() as conn:
            conn.execute(
                """
                UPDATE planning_runs SET status = ?, published_at = ? WHERE id = ?
                """,
                (run.status.value, run.published_at.isoformat() if run.published_at else None, run.id),
            )

    def list_planning_runs(self) -> list[dict[str, Any]]:
        with self.session() as conn:
            rows = conn.execute("SELECT * FROM planning_runs ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def get_planning_run(self, run_id: str) -> dict[str, Any] | None:
        with self.session() as conn:
            row = conn.execute("SELECT * FROM planning_runs WHERE id = ?", (run_id,)).fetchone()
            return dict(row) if row else None

    # --- Routes / stops ---
    def insert_route(self, route: Any, run_id: str) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO routes (id, planning_run_id, driver_id, status, planned_distance_meters, planned_duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{run_id}::{route.driver.id}",
                    run_id,
                    route.driver.id,
                    "review",
                    route.planned_distance_meters,
                    route.planned_duration_seconds,
                ),
            )
            for stop in route.stops:
                conn.execute(
                    """
                    INSERT INTO route_stops (id, route_id, order_id, sequence, planned_arrival, planned_departure, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"{run_id}::{route.driver.id}::{stop.sequence}",
                        f"{run_id}::{route.driver.id}",
                        stop.order.id,
                        stop.sequence,
                        stop.planned_arrival.isoformat(),
                        stop.planned_departure.isoformat(),
                        stop.status.value,
                    ),
                )

    def list_routes_for_run(self, run_id: str) -> list[dict[str, Any]]:
        with self.session() as conn:
            routes = conn.execute("SELECT * FROM routes WHERE planning_run_id = ?", (run_id,)).fetchall()
            result = []
            for route in routes:
                stops = conn.execute("SELECT * FROM route_stops WHERE route_id = ? ORDER BY sequence", (route["id"],)).fetchall()
                result.append({"route": dict(route), "stops": [dict(s) for s in stops]})
            return result

    # --- Unassigned orders ---
    def insert_unassigned_order(self, run_id: str, item: Any) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO unassigned_orders (id, planning_run_id, order_id, reason_code, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (f"{run_id}::{item.order.id}", run_id, item.order.id, item.reason_code.value, item.details),
            )

    # --- Status events ---
    def insert_status_event(self, event: Any) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO status_events (id, order_id, driver_id, actor_user_id, from_status, to_status, note, lat, lng, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id if hasattr(event, "id") else event.order_id + "::" + event.created_at.isoformat(),
                    event.order_id,
                    event.driver_id,
                    event.actor_user_id,
                    event.from_status.value if event.from_status else None,
                    event.to_status.value,
                    event.note,
                    event.lat,
                    event.lng,
                    event.created_at.isoformat(),
                ),
            )

    def list_status_events(self, order_id: str | None = None) -> list[dict[str, Any]]:
        with self.session() as conn:
            if order_id:
                rows = conn.execute("SELECT * FROM status_events WHERE order_id = ? ORDER BY created_at", (order_id,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM status_events ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    # --- Audit events ---
    def insert_audit_event(self, actor_user_id: str, object_type: str, object_id: str, action: str, before_json: str | None, after_json: str | None) -> None:
        with self.session() as conn:
            conn.execute(
                """
                INSERT INTO audit_events (id, actor_user_id, object_type, object_id, action, before_json, after_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{object_type}::{object_id}::{action}::{datetime.now(__import__('datetime').UTC).isoformat()}",
                    actor_user_id,
                    object_type,
                    object_id,
                    action,
                    before_json,
                    after_json,
                    datetime.now(__import__("datetime").UTC).isoformat(),
                ),
            )

    def list_audit_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.session() as conn:
            rows = conn.execute("SELECT * FROM audit_events ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]


repository = SqliteRepository()
