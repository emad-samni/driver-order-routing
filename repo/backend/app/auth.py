"""Simple header-based API key auth for the prototype.

Roles:
- admin: full access.
- driver: restricted to driver and status endpoints; may be bound to a single
  driver identity so a driver credential can only read its own route.

Configuration via environment variables (read at request time so tests and the
runtime can toggle behaviour without re-importing the app):
- API_KEY_ADMIN
- API_KEY_DRIVER
- REQUIRE_API_KEY  (truthy enables enforcement)
- DRIVER_API_KEYS  ("key=driver_id;key2=driver_id2") binds keys to drivers
"""

from __future__ import annotations

import os
from typing import Callable

from fastapi import HTTPException, Request

ADMIN_ROLE = "admin"
DRIVER_ROLE = "driver"

# Programmatically registered driver key -> driver_id bindings. The runtime (or
# a test) can register a per-driver credential here; env DRIVER_API_KEYS is
# merged on top at resolution time.
_DRIVER_KEY_MAP: dict[str, str] = {}


class AuthError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Missing or invalid API key")


class Principal:
    """The authenticated caller: a role and, for drivers, a bound driver_id."""

    def __init__(self, role: str, driver_id: str | None = None) -> None:
        self.role = role
        self.driver_id = driver_id


def auth_enabled() -> bool:
    return os.getenv("REQUIRE_API_KEY", "1").lower() in {"1", "true", "yes"}


def _admin_key() -> str:
    return os.getenv("API_KEY_ADMIN", "admin-key")


def _driver_key() -> str:
    return os.getenv("API_KEY_DRIVER", "driver-key")


def register_driver_key(api_key: str, driver_id: str) -> None:
    _DRIVER_KEY_MAP[api_key] = driver_id


def _driver_key_map() -> dict[str, str]:
    mapping = dict(_DRIVER_KEY_MAP)
    raw = os.getenv("DRIVER_API_KEYS", "")
    for pair in raw.split(";"):
        pair = pair.strip()
        if "=" in pair:
            key, driver_id = pair.split("=", 1)
            mapping[key.strip()] = driver_id.strip()
    return mapping


def _extract_api_key(request: Request) -> str | None:
    return request.headers.get("x-api-key") or request.headers.get("X-API-Key")


def resolve_principal(request: Request) -> Principal | None:
    """Return the authenticated principal, or None if the key is unknown."""
    api_key = _extract_api_key(request)
    if api_key is None:
        return None
    mapping = _driver_key_map()
    if api_key in mapping:
        return Principal(DRIVER_ROLE, driver_id=mapping[api_key])
    if api_key == _admin_key():
        return Principal(ADMIN_ROLE)
    if api_key == _driver_key():
        return Principal(DRIVER_ROLE)
    return None


def _role_for_key(request: Request) -> str | None:
    principal = resolve_principal(request)
    return principal.role if principal else None


def require_role(required_role: str) -> Callable[[Request], None]:
    def dependency(request: Request) -> None:
        role = _role_for_key(request)
        if role is None:
            raise AuthError()
        if role != required_role and role != ADMIN_ROLE:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    return dependency
